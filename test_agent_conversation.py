#!/usr/bin/env python3
"""
Test script to validate TodoistAgent behavior and pattern learning.

This script simulates a conversation to test:
1. Weekly review workflow
2. Pattern learning (e.g., "5 d" means complete task 5)
3. Batch processing
4. Knowledge retrieval
"""

import os
from dotenv import load_dotenv
from core.agent_loader import load_agent
from core.providers import get_provider
import json

load_dotenv()

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def send_message(provider, client, messages, system_prompt, model, tools, user_text):
    """Send a message and handle tool calls."""
    print(f"USER: {user_text}")
    messages.append({"role": "user", "content": user_text})

    # Get response
    response = provider.send_message(
        client=client,
        messages=messages,
        system_prompt=system_prompt,
        model=model,
        tools=tools
    )

    # Handle tool calls
    while response.tool_calls:
        print(f"\n🛠️  Executing {len(response.tool_calls)} tool(s):")

        # Add assistant message
        messages.append(provider.get_assistant_message(response))

        # Execute tools
        tool_results = []
        for tool_call in response.tool_calls:
            print(f"  → {tool_call.name}({tool_call.arguments})")

            try:
                tool_method = getattr(agent, tool_call.name)
                result = tool_method(**tool_call.arguments)

                # Parse and display result
                try:
                    data = json.loads(result)
                    if data.get("status") == "success":
                        print(f"    ✓ {data.get('message', 'Success')}")
                    else:
                        print(f"    ✗ {data.get('error', 'Error')}")
                except:
                    print(f"    Result: {result[:100]}")

                tool_results.append(
                    provider.format_tool_results(tool_call.id, str(result))
                )
            except Exception as e:
                error_msg = f'{{"status": "error", "error": "{str(e)}"}}'
                print(f"    ✗ Error: {e}")
                tool_results.append(
                    provider.format_tool_results(tool_call.id, error_msg)
                )

        # Add tool results
        if agent.provider == "anthropic":
            messages.append({"role": "user", "content": tool_results})
        else:
            messages.extend(tool_results)

        # Get next response
        response = provider.send_message(
            client=client,
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            tools=tools
        )

    # Display text response
    if response.text:
        print(f"\nASSISTANT: {response.text}\n")
        messages.append({"role": "assistant", "content": response.text})

    # Show token usage
    if response.usage:
        print(f"[Tokens: {response.usage.input_tokens} in + {response.usage.output_tokens} out = {response.usage.total_tokens} total]")

    return messages


# Main test
if __name__ == "__main__":
    print_section("TODOIST AGENT CONVERSATION TEST")

    # Load agent
    print("Loading agent...")
    agent = load_agent(agent_name="todoist_openai")
    print(f"✓ Agent: {agent.name} ({agent.provider}/{agent.model})")

    # Get provider
    provider = get_provider(agent.provider)
    client = provider.create_client()
    tools = provider.format_tool_schemas(agent)

    tool_names = [
        t.get("name") or t.get("function", {}).get("name")
        for t in tools
    ]
    print(f"✓ Tools: {', '.join(tool_names)}\n")

    # Initialize conversation
    messages = []

    # Test 1: Initialization
    print_section("TEST 1: Initialization")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools,
        "hello"
    )

    # Test 2: List inbox tasks
    print_section("TEST 2: List Inbox Tasks")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools,
        "list all tasks in inbox"
    )

    # Test 3: Teach pattern - "d" means done
    print_section("TEST 3: Teach Pattern Recognition")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools,
        "From now on, when I say a task number followed by 'd', it means that task is completed. For example, '5 d' means complete task 5. Can you remember this pattern?"
    )

    # Test 4: Check if it learned
    print_section("TEST 4: Verify Pattern Learning")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools,
        "Did you save that pattern to your knowledge? Where did you save it?"
    )

    # Test 5: Test weekly review start
    print_section("TEST 5: Weekly Review - Inbox Processing")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools,
        "Let's start a weekly review. Process the inbox."
    )

    print_section("TEST COMPLETE")
    print("\nKey things to verify:")
    print("1. ✓ Did agent call get_current_time() on startup?")
    print("2. ✓ Did agent call query_knowledge('learned_rules') for weekly review?")
    print("3. ✓ Did agent present tasks in batches of 5 or less?")
    print("4. ✓ Did agent ask to save the 'd' pattern to learned_rules?")
    print("5. ✓ Did agent present suggestions without preamble?")
    print("\nCheck the knowledge file:")
    print("  cat knowledge/todoistagent/learned_rules.md")
