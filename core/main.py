import os
import typer
from openai import OpenAI
from dotenv import load_dotenv

from core.agent_loader import load_agent

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
        print(f"✅ Agent '{agent.name}' loaded successfully. Model: {agent.model}")
    except (FileNotFoundError, AttributeError, KeyError) as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()
        
    print("Type your message below. Press Ctrl+C to exit.")

    last_response_id = None

    while True:
        try:
            user_input = input("\n> ")

            # --- ADDED UX MESSAGE ---
            print(f"\nSending request to {agent.name}...", flush=True)

            request_payload = {
                "model": agent.model,
                "input": user_input,
                "instructions": agent.system_prompt
            }

            if last_response_id:
                request_payload["previous_response_id"] = last_response_id

            response = client.responses.create(**request_payload)

            last_response_id = response.id

            if response.output_text:
                print(f"\nAssistant: {response.output_text}")
            else:
                print("\nAssistant: (No text output was generated)")

        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            last_response_id = None

if __name__ == "__main__":
    app()
