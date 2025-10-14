import os
import json
import typer
import openai # Import the base library to catch its specific errors
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from core.agent_loader import load_agent
from core.schema_generator import generate_tool_schemas
from core.logger import setup_logging

app = typer.Typer(help="A modular, command-line-first AI orchestration engine.")

# --- Retry Logic ---
def before_sleep_log(retry_state):
    """Log before sleeping on a retry."""
    print(f"Retrying API call... (Attempt {retry_state.attempt_number})")

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(openai.APIStatusError),
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
    setup_logging()
    load_dotenv()
    client = OpenAI()

    try:
        agent = load_agent(agent_name="coder")
        tools_for_api = generate_tool_schemas(agent)
        tool_names = [t.get("name") for t in tools_for_api]
        print(f"✅ Agent '{agent.name}' loaded. Tools: {tool_names}")
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()

    messages = [{"role": "system", "content": agent.system_prompt}]
    print("Type your message below. Press Ctrl+C to exit.")

    while True:
        try:
            user_text = input("\n> ")
            messages.append({"role": "user", "content": user_text})

            while True:
                print(f"\nThinking...", flush=True)
                response = make_api_call(client=client, payload={"model": agent.model, "messages": messages, "tools": tools_for_api, "tool_choice": "auto"})
                response_message = response.choices[0].message
                messages.append(response_message)

                if response_message.tool_calls:
                    print(f"🛠️  Invoking tool(s)...")
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        print(f"  - {function_name}(**{arguments})")
                        method_to_call = getattr(agent, function_name)
                        tool_output = method_to_call(**arguments)
                        messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": str(tool_output)})
                    continue

                if response_message.content:
                    print(f"\nAssistant: {response_message.content}")
                break
        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            messages = messages[:1]
            continue

@app.command("run", help="Executes a high-level goal autonomously.")
def run(goal: str, max_steps: int = 10):
    """Takes a goal and lets the agent work autonomously to achieve it."""
    print(f"--- Synapse AI Run ---")
    print(f"🎯 Goal: {goal}")

    setup_logging()
    load_dotenv()
    client = OpenAI()
    agent = load_agent(agent_name="coder")
    tools_for_api = generate_tool_schemas(agent)
    
    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": goal}
    ]

    for i in range(max_steps):
        print(f"\n--- Step {i+1}/{max_steps} ---")
        try:
            print("🤔 Thinking...", flush=True)
            response = make_api_call(client=client, payload={"model": agent.model, "messages": messages, "tools": tools_for_api, "tool_choice": "auto"})
            response_message = response.choices[0].message
            messages.append(response_message)

            if not response_message.tool_calls:
                print("✅ Assistant provided final response:")
                print(response_message.content)
                print("\n--- Run Finished: No tool call detected. ---")
                break

            print(f"🛠️  Invoking tool(s)...")
            final_tool_call_name = ""
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                final_tool_call_name = function_name # Keep track of the last tool
                arguments = json.loads(tool_call.function.arguments)
                print(f"  - {function_name}(**{arguments})")
                
                method_to_call = getattr(agent, function_name)
                tool_output = method_to_call(**arguments)
                print(f"  - Output:\n{tool_output}")
                
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": str(tool_output)})

            if final_tool_call_name == "git_commit":
                print("\n--- Run Finished: Commit task completed. ---")
                break

        except Exception as e:
            print(f"\nAn error occurred during the run: {e}")
            break
    else:
        print("\n--- Run Finished: Maximum steps reached. ---")

if __name__ == "__main__":
    app()
