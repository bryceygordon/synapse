#!/usr/bin/env python3
"""
Test the Learning Protocol - ensure agent shows before/after and asks for confirmation.

Expected behavior:
1. Agent queries current knowledge first
2. Shows BEFORE state
3. Shows AFTER state
4. Asks for confirmation
5. Only updates after user says yes
"""

import os
import json
from dotenv import load_dotenv
from core.agent_loader import load_agent
from core.providers import get_provider

load_dotenv()

def print_divider(title=""):
    print(f"\n{'='*70}")
    if title:
        print(f"  {title}")
        print(f"{'='*70}")
    print()

def send_message(provider, client, messages, system_prompt, model, tools, agent, user_text, max_iterations=5):
    """Send a message and handle all tool calls."""
    print(f"\n👤 USER: {user_text}")
    messages.append({"role": "user", "content": user_text})

    iteration = 0
    while iteration < max_iterations:
        iteration += 1

        # Get response
        response = provider.send_message(
            client=client,
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            tools=tools
        )

        # Handle tool calls
        if response.tool_calls:
            print(f"\n🛠️  Tool calls: {[tc.name for tc in response.tool_calls]}")

            # Add assistant message
            messages.append(provider.get_assistant_message(response))

            # Execute tools
            tool_results = []
            for tool_call in response.tool_calls:
                try:
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )
                except Exception as e:
                    error_msg = f'{{"status": "error", "error": "{str(e)}"}}'
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, error_msg)
                    )

            # Add tool results
            if agent.provider == "anthropic":
                messages.append({"role": "user", "content": tool_results})
            else:
                messages.extend(tool_results)

            # Continue loop to get next response
            continue

        # Display text response
        if response.text:
            print(f"\n🤖 ASSISTANT:\n{response.text}")
            messages.append({"role": "assistant", "content": response.text})

        # Break if no tool calls
        break

    return messages


# Main test
if __name__ == "__main__":
    print_divider("LEARNING PROTOCOL TEST")

    # Load agent
    print("Loading agent...")
    agent = load_agent(agent_name="todoist_openai")
    print(f"✓ Agent: {agent.name} ({agent.provider}/{agent.model})\n")

    # Get provider
    provider = get_provider(agent.provider)
    client = provider.create_client()
    tools = provider.format_tool_schemas(agent)

    # Initialize conversation
    messages = []

    # Test 1: Teach a NEW rule (no existing rule)
    print_divider("TEST 1: Teaching a NEW Rule")
    print("Expected: Should show BEFORE: 'No existing rule', AFTER: new rule, then ASK")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "I want to teach you a pattern: Tasks that mention 'gardening' should get @yard, @medenergy, and @weather labels."
    )

    # Check if agent asked for confirmation
    last_response = messages[-1]["content"]
    if "should i save" in last_response.lower() or "confirm" in last_response.lower():
        print("\n✅ PASS: Agent asked for confirmation")
    else:
        print("\n❌ FAIL: Agent did NOT ask for confirmation")
        print(f"Last response: {last_response[:200]}")

    # Confirm
    print_divider("User Confirms")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "yes, save it"
    )

    # Test 2: UPDATE an existing rule
    print_divider("TEST 2: Updating EXISTING Rule")
    print("Expected: Should show BEFORE: old rule, AFTER: updated rule, then ASK")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Actually, gardening tasks should be @highenergy, not @medenergy."
    )

    # Check if agent showed before/after
    last_response = messages[-1]["content"]
    has_before = "before" in last_response.lower()
    has_after = "after" in last_response.lower()
    asks_confirmation = "should i" in last_response.lower() or "confirm" in last_response.lower()

    if has_before and has_after and asks_confirmation:
        print("\n✅ PASS: Agent showed BEFORE/AFTER and asked for confirmation")
    else:
        print(f"\n❌ FAIL: Missing elements - before:{has_before}, after:{has_after}, asks:{asks_confirmation}")
        print(f"Last response: {last_response[:300]}")

    print_divider("TEST COMPLETE")
    print("\nReview the conversation above to verify the Learning Protocol was followed.")
