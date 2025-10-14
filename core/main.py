import os
import typer
from openai import OpenAI
from dotenv import load_dotenv

from core.agent_loader import load_agent

# Initialize the Typer app for our CLI
app = typer.Typer()

@app.command()
def chat():
    """
    Starts an interactive chat session with the configured Synapse agent.
    """
    print("--- Synapse AI Chat---")
    print("Agent: CoderAgent | Model: gpt-5")
    print("Type your message below. Press Ctrl+C to exit.")

    # Load environment variables (for the API key)
    load_dotenv()
    client = OpenAI()

    # --- Core Application Loop ---

    # 1. Load the agent object from its configuration file.
    try:
        agent = load_agent(agent_name="coder")
        print("✅ CoderAgent loaded successfully.")
    except (FileNotFoundError, AttributeError, KeyError) as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()

    # 2. Initialize conversation state.
    last_response_id = None

    while True:
        try:
            # 3. Get user input.
            user_input = input("\n> ")

            # 4. Construct the API request payload using the agent's attributes.
            request_payload = {
                "model": agent.model,
                "input": user_input,
                "instructions": agent.system_prompt
            }

            # 5. Add the previous response ID to maintain conversation context.
            if last_response_id:
                request_payload["previous_response_id"] = last_response_id

            # 6. Make the API call.
            response = client.responses.create(**request_payload)

            # 7. Store the ID of this response for the next turn.
            last_response_id = response.id

            # 8. Print the assistant's output text.
            if response.output_text:
                print(f"\nAssistant: {response.output_text}")
            else:
                print("\nAssistant: (No text output was generated)")

        except KeyboardInterrupt:
            # Handle Ctrl+C for a clean exit (fulfills the Ctrl+Q request).
            print("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            # Reset conversation on error to prevent broken chains.
            last_response_id = None

if __name__ == "__main__":
    app()

