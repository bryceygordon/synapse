import os
import json
import typer
from openai import OpenAI, BadRequestError, APIStatusError
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt

from core.agent_loader import load_agent
from core.schema_generator import generate_tool_schemas
from core.logger import setup_logging

app = typer.Typer(help="A modular, command-line-first AI orchestration engine.")

# --- Refined Retry Logic ---
def before_sleep_log(retry_state):
    """Log before sleeping on a retry."""
    print(f"Retrying API call due to server error... (Attempt {retry_state.attempt_number})")

def is_server_error(exception):
    """Return True if the exception is a server-side error (5xx)."""
    return isinstance(exception, APIStatusError) and exception.status_code >= 500

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    retry=is_server_error,
    before_sleep=before_sleep_log
)
def make_api_call(client: OpenAI, payload: dict):
    """A hardened wrapper for the client.responses.create call."""
    return client.responses.create(**payload)

@app.command("chat", help="Starts an interactive chat session with the agent.")
@app.command("", hidden=True)
def chat():
    """Starts an interactive chat session with the configured Synapse agent."""
    print("--- Synapse AI Chat (Responses API) ---")
    setup_logging(); load_dotenv(); client = OpenAI()

    try:
        agent = load_agent(agent_name="coder")
        tools_for_api = generate_tool_schemas(agent)
        tool_names = [t.get("name") for t in tools_for_api]
        print(f"✅ Agent '{agent.name}' loaded. Tools: {tool_names}")
    except Exception as e:
        print(f"❌ Error loading agent: {e}"); raise typer.Exit()

    print("Type your message below. Press Ctrl+C to exit.")
    last_response_id, next_input = None, None

    while True:
        try:
            if next_input:
                current_input = next_input
                next_input = None
            else:
                user_text = input("\n> ")
                current_input = [{"type": "message", "role": "user", "content": user_text}]

            print(f"\nThinking...", flush=True)
            request_payload = {"model": agent.model, "input": current_input, "instructions": agent.system_prompt, "tools": tools_for_api}
            if last_response_id: request_payload["previous_response_id"] = last_response_id
            response = make_api_call(client=client, payload=request_payload)
            last_response_id = response.id

            tool_calls = [item for item in response.output if item.type == "function_call"]
            if tool_calls:
                print(f"🛠️  Invoking {len(tool_calls)} tool(s) in parallel...")
                original_tool_calls, tool_outputs = [], []
                for tool_call in tool_calls:
                    function_name, arguments = tool_call.name, json.loads(tool_call.arguments)
                    print(f"  - {function_name}(**{arguments})")
                    tool_output = getattr(agent, function_name)(**arguments)
                    original_tool_calls.append(tool_call.model_dump())
                    tool_outputs.append({"type": "function_call_output", "call_id": tool_call.id, "output": str(tool_output)})
                next_input = original_tool_calls + tool_outputs
                continue

            if response.output_text: print(f"\nAssistant: {response.output_text}")
        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!"); break
        except Exception as e:
            print(f"\nAn error occurred: {e}"); last_response_id, next_input = None, None

@app.command("run", help="Executes a high-level goal autonomously.")
def run(goal: str, max_steps: int = 15):
    """Takes a goal and lets the agent work autonomously to achieve it."""
    print(f"--- Synapse AI Run ---\n🎯 Goal: {goal}")
    setup_logging(); load_dotenv(); client = OpenAI()
    agent = load_agent(agent_name="coder")
    tools_for_api = generate_tool_schemas(agent)
    
    last_response_id = None
    current_input = [{"type": "message", "role": "user", "content": goal}]

    for i in range(max_steps):
        print(f"\n--- Step {i+1}/{max_steps} ---")
        try:
            print("🤔 Thinking...", flush=True)
            request_payload = {"model": agent.model, "input": current_input, "instructions": agent.system_prompt, "tools": tools_for_api}
            if last_response_id: request_payload["previous_response_id"] = last_response_id
            response = make_api_call(client=client, payload=request_payload)
            last_response_id = response.id

            tool_calls = [item for item in response.output if item.type == "function_call"]

            if not tool_calls:
                print(f"✅ Assistant provided final response:\n{response.output_text}")
                print("\n--- Run Finished: Goal achieved or no further tools needed. ---"); break

            print(f"🛠️  Invoking {len(tool_calls)} tool(s) in parallel...")
            original_tool_calls, tool_outputs = [], []
            commit_requested = False
            for tool_call in tool_calls:
                function_name, arguments = tool_call.name, json.loads(tool_call.arguments)
                if function_name == "git_commit": commit_requested = True
                print(f"  - {function_name}(**{arguments})")
                tool_output = getattr(agent, function_name)(**arguments)
                print(f"    - Output: {str(tool_output)[:200]}...") # Truncate long outputs
                original_tool_calls.append(tool_call.model_dump())
                tool_outputs.append({"type": "function_call_output", "call_id": tool_call.id, "output": str(tool_output)})
            
            current_input = original_tool_calls + tool_outputs
            if commit_requested: print("\n--- Run Finished: Commit task completed. ---"); break
        except BadRequestError as e:
            print(f"\n❌ Invalid Request Error: The request was malformed. This can be due to excessive context length. Aborting. Details: {e}"); break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}"); break
    else:
        print("\n--- Run Finished: Maximum steps reached. ---")

if __name__ == "__main__":
    app()
