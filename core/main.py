import os
import json
import typer
import openai # Import the base library to catch its specific errors
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from core.agent_loader import load_agent
from core.schema_generator import generate_tool_schemas

app = typer.Typer()

# --- NEW: Retry Logic Definition ---
def before_sleep_log(retry_state):
    """Log before sleeping on a retry."""
    print(f"Retrying API call... (Attempt {retry_state.attempt_number})")

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60), # Exponential backoff: 2s, 4s, 8s...
    stop=stop_after_attempt(3), # Stop after 3 attempts
    retry=retry_if_exception_type(openai.APIStatusError), # Only retry on server-side errors (5xx)
    before_sleep=before_sleep_log,
)
def make_api_call(client: OpenAI, payload: dict):
    """
    A hardened wrapper for the client.responses.create call that includes retry logic.
    """
    return client.responses.create(**payload)
# --- End of New Logic ---


@app.command()
def chat():
    """
    Starts an interactive chat session with the configured Synapse agent.
    """
    print("--- Synapse AI Chat---")

    load_dotenv()
    client = OpenAI()

    try:
        agent = load_agent(agent_name="coder")
        tools_for_api = []
        if agent.vector_store_id:
            tools_for_api.append({"type": "file_search", "vector_store_ids": [agent.vector_store_id]})
            print(f"🧠 Knowledge enabled with Vector Store: {agent.vector_store_id}")
        function_tool_schemas = generate_tool_schemas(agent)
        tools_for_api.extend(function_tool_schemas)
        tool_names = [t.get("name") for t in function_tool_schemas]
        print(f"✅ Agent '{agent.name}' loaded successfully. Model: {agent.model}. Tools: {tool_names}")
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()

    print("Type your message below. Press Ctrl+C to exit.")

    last_response_id = None
    next_input = None

    while True:
        try:
            if next_input:
                current_input = next_input
                next_input = None
            else:
                user_text = input("\n> ")
                current_input = [{"type": "message", "role": "user", "content": user_text}]

            print(f"\nSending request to {agent.name}...", flush=True)

            request_payload = {
                "model": agent.model,
                "input": current_input,
                "instructions": agent.system_prompt,
                "tools": tools_for_api,
            }

            if last_response_id:
                request_payload["previous_response_id"] = last_response_id

            # --- MODIFIED: Use the hardened API call wrapper ---
            response = make_api_call(client=client, payload=request_payload)
            last_response_id = response.id

            tool_call = next((item for item in response.output if item.type == "function_call"), None)

            if tool_call:
                function_name = tool_call.name
                arguments = json.loads(tool_call.arguments)

                print(f"🛠️  Invoking tool: {function_name}(**{arguments})")

                method_to_call = getattr(agent, function_name)
                tool_output = method_to_call(**arguments)

                next_input = [
                    tool_call.model_dump(),
                    {"type": "function_call_output", "call_id": tool_call.id, "output": tool_output}
                ]
                continue

            if response.output_text:
                print(f"\nAssistant: {response.output_text}")

        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            last_response_id = None
            next_input = None

if __name__ == "__main__":
    app()
