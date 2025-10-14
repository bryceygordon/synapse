import os
import json
import typer
import pprint
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
        
        tools_for_api = []
        if agent.vector_store_id:
            tools_for_api.append({"type": "file_search", "vector_store_ids": [agent.vector_store_id]})
            print(f"🧠 Knowledge enabled with Vector Store: {agent.vector_store_id}")
        
        function_tool_schemas = generate_tool_schemas(agent)
        tools_for_api.extend(function_tool_schemas)

        tool_names = [t.get("name") for t in function_tool_schemas]
        print(f"✅ Agent '{agent.name}' loaded successfully. Model: {agent.model}. Tools: {tool_names}")
    
    except (FileNotFoundError, AttributeError, KeyError) as e:
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
                "tools": tools_for_api
            }
            
            if last_response_id:
                request_payload["previous_response_id"] = last_response_id
            
            response = client.responses.create(**request_payload)
            last_response_id = response.id

            tool_call = next((item for item in response.output if item.type == "function_call"), None)

            if tool_call:
                function_name = tool_call.name
                arguments = json.loads(tool_call.arguments)
                
                print(f"🛠️  Invoking tool: {function_name}(**{arguments})")
                
                method_to_call = getattr(agent, function_name)
                tool_output = method_to_call(**arguments)
                
                # --- THE CRITICAL FIX IS HERE ---
                # We must send back a complete record of the tool call and its output.
                # The .model_dump() method converts the Pydantic object to a dictionary.
                next_input = [
                    tool_call.model_dump(),
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.id,
                        "output": tool_output
                    }
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
