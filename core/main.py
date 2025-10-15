"""
Main CLI application for Synapse AI Orchestration Engine.

This module provides the command-line interface for interacting with
AI agents through multiple providers (Claude, OpenAI, Gemini, etc.).
"""

import json
import typer
from dotenv import load_dotenv

from core.agent_loader import load_agent
from core.providers import get_provider
from core.logger import setup_logging

app = typer.Typer(help="A modular, command-line-first AI orchestration engine.")


@app.command("chat", help="Starts an interactive chat session with the agent.")
@app.command("", hidden=True)
def chat(agent_name: str = "coder"):
    """
    Starts an interactive chat session with the configured Synapse agent.

    Args:
        agent_name: Name of the agent to load (default: coder)
    """
    print(f"--- Synapse AI Chat ---")
    setup_logging()
    load_dotenv()

    try:
        # Load agent configuration
        agent = load_agent(agent_name=agent_name)
        print(f"✅ Agent '{agent.name}' loaded successfully")
        print(f"   Provider: {agent.provider}")
        print(f"   Model: {agent.model}")

        # Get the appropriate provider
        provider = get_provider(agent.provider)
        client = provider.create_client()

        # Generate tool schemas for this provider
        tools = provider.format_tool_schemas(agent)
        tool_names = [t.get("name") for t in tools]
        print(f"   Tools: {tool_names}\n")

    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        raise typer.Exit()

    print("Type your message below. Press Ctrl+C to exit.\n")

    # Conversation state
    messages = []

    while True:
        try:
            # Get user input
            user_text = input("> ")
            if not user_text.strip():
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_text})

            print("\n🤔 Thinking...", flush=True)

            # Send message to provider
            response = provider.send_message(
                client=client,
                messages=messages,
                system_prompt=agent.system_prompt,
                model=agent.model,
                tools=tools
            )

            # Handle tool calls
            if response.tool_calls:
                print(f"🛠️  Invoking {len(response.tool_calls)} tool(s)...\n")

                # Add assistant's tool use message to history
                messages.append({
                    "role": "assistant",
                    "content": response.tool_calls  # Provider-specific format
                })

                # Execute each tool
                tool_results = []
                for tool_call in response.tool_calls:
                    print(f"  → {tool_call.name}({tool_call.arguments})")

                    # Invoke the tool method on the agent
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)

                    print(f"    ✓ Result: {str(result)[:100]}...")

                    # Format result for provider
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )

                # Add tool results to message history
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Get next response after tool execution
                print("\n🤔 Processing results...", flush=True)
                response = provider.send_message(
                    client=client,
                    messages=messages,
                    system_prompt=agent.system_prompt,
                    model=agent.model,
                    tools=tools
                )

            # Display text response if present
            if response.text:
                print(f"\nAssistant: {response.text}\n")
                messages.append({"role": "assistant", "content": response.text})

        except KeyboardInterrupt:
            print("\n\nExiting chat. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Continuing conversation...\n")


@app.command("run", help="Executes a high-level goal autonomously.")
def run(goal: str, max_steps: int = 15, agent_name: str = "coder"):
    """
    Takes a goal and lets the agent work autonomously to achieve it.

    Args:
        goal: The goal for the agent to achieve
        max_steps: Maximum number of reasoning steps (default: 15)
        agent_name: Name of the agent to use (default: coder)
    """
    print(f"--- Synapse AI Run ---\n🎯 Goal: {goal}\n")
    setup_logging()
    load_dotenv()

    try:
        # Load agent and provider
        agent = load_agent(agent_name=agent_name)
        provider = get_provider(agent.provider)
        client = provider.create_client()
        tools = provider.format_tool_schemas(agent)

        print(f"✅ Agent: {agent.name} ({agent.provider}/{agent.model})")
        print(f"📋 Max steps: {max_steps}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit()

    # Initialize conversation with the goal
    messages = [{"role": "user", "content": goal}]

    for step in range(max_steps):
        print(f"--- Step {step + 1}/{max_steps} ---")

        try:
            print("🤔 Thinking...", flush=True)

            # Send message to provider
            response = provider.send_message(
                client=client,
                messages=messages,
                system_prompt=agent.system_prompt,
                model=agent.model,
                tools=tools
            )

            # If no tool calls, agent is done
            if not response.tool_calls:
                if response.text:
                    print(f"✅ Final response:\n{response.text}")
                print("\n--- Run Finished: Goal achieved or no further tools needed. ---")
                break

            # Execute tools
            print(f"🛠️  Invoking {len(response.tool_calls)} tool(s)...")

            tool_results = []
            commit_requested = False

            for tool_call in response.tool_calls:
                print(f"  → {tool_call.name}(**{tool_call.arguments})")

                if tool_call.name == "git_commit":
                    commit_requested = True

                # Execute tool
                tool_method = getattr(agent, tool_call.name)
                result = tool_method(**tool_call.arguments)

                print(f"    ✓ Output: {str(result)[:150]}...")

                tool_results.append(
                    provider.format_tool_results(tool_call.id, str(result))
                )

            # Update conversation with tool results
            messages.append({
                "role": "assistant",
                "content": response.tool_calls
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # If commit was requested, consider goal achieved
            if commit_requested:
                print("\n--- Run Finished: Commit task completed. ---")
                break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

    else:
        print("\n--- Run Finished: Maximum steps reached. ---")


if __name__ == "__main__":
    app()
