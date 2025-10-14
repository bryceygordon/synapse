import os
import json
import typer
from openai import OpenAI
from dotenv import load_dotenv

from core.agent_loader import load_agent
from core.schema_generator import generate_tool_schemas

app = typer.Typer()

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
        tools_for_api = generate_tool_schemas(agent)
        print(f"✅ Agent '{agent.name}' loaded successfully. Model: {agent.model}. Tools: {[t['function']['name'] for t in tools_for_api]}")
    except (FileNotFoundError, AttributeError, KeyError) as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()
        
    print("Type your message below. Press Ctrl+C to exit.")

    last_response_id = None
    next_input = None

    while True:
        try:
            # --- REVISED LOGIC: Decide what the input for this turn is ---
            if next_input:
                # If there's pending tool output, that's our input
                current_input = next_input
                next_input = None # Clear it for the next iteration
            else:
                # Otherwise, get input from the user
                user_text = input("\n> ")
                current_input = [{"type": "text", "text": user_text}]

            print(f"\nSending request to {agent.name}...", flush=True)

            request_payload = {
                "model": agent.model,
                "input": current_input,
                "instructions": agent.system_prompt,
                "tools": tools_for_api
            }
            
            if last_response_id:
                request_payload["previous_response_id"] = last_response_id
            
            response = client.responses.create(**request_payload)
            last_response_id = response.id

            tool_call = next((item for item in response.output if item.type == "function_call"), None)

            if tool_call:
                # If a tool is called, invoke it and set up the next input
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🛠️  Invoking tool: {function_name}(**{arguments})")
                
                method_to_call = getattr(agent, function_name)
                tool_output = method_to_call(**arguments)
                
                # Prepare the input for the *next* iteration of the loop
                next_input = [{
                    "type": "function_call_output",
                    "call_id": tool_call.id,
                    "output": tool_output
                }]
                # Continue to the next loop iteration immediately
                continue
            
            # If no tool call, print the text response
            if response.output_text:
                print(f"\nAssistant: {response.output_text}")

        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            last_response_id = None
            next_input = None # Reset state on error

if __name__ == "__main__":
    app()
