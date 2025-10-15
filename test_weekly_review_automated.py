#!/usr/bin/env python3
"""
Automated weekly review test script.

This script will:
1. Create test tasks in inbox
2. Initiate weekly review with the agent
3. Interact with the agent through the workflow
4. Analyze the behavior and identify issues
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
            print(f"\n🛠️  Executing {len(response.tool_calls)} tool(s):")

            # Add assistant message
            messages.append(provider.get_assistant_message(response))

            # Execute tools
            tool_results = []
            for tool_call in response.tool_calls:
                args_str = json.dumps(tool_call.arguments) if tool_call.arguments else ""
                print(f"  → {tool_call.name}({args_str})")

                try:
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)

                    # Parse and display key info
                    try:
                        data = json.loads(result)
                        if data.get("status") == "success":
                            msg = data.get('message', '')
                            if len(msg) > 100:
                                msg = msg[:100] + "..."
                            print(f"    ✓ {msg}")
                        else:
                            print(f"    ✗ {data.get('error', 'Error')}")
                    except:
                        pass

                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )
                except Exception as e:
                    error_msg = f'{{"status": "error", "error": "{str(e)}"}}'
                    print(f"    ✗ Exception: {e}")
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

        # Show token usage
        if response.usage:
            print(f"\n📊 Tokens: {response.usage.input_tokens} in + {response.usage.output_tokens} out = {response.usage.total_tokens} total")

        # Break if no tool calls
        break

    return messages


# Main test
if __name__ == "__main__":
    print_divider("TODOIST AGENT - AUTOMATED WEEKLY REVIEW TEST")

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

    # Step 1: Create test tasks
    print_divider("STEP 1: Create Test Tasks in Inbox")

    test_tasks = [
        {"content": "Fix leaky kitchen tap", "description": "Kitchen sink tap has been dripping"},
        {"content": "Buy groceries for week", "description": "Need: milk, bread, eggs, vegetables"},
        {"content": "Mow the front lawn", "description": "Grass is getting too long"},
        {"content": "Call dentist for checkup appointment", "description": "Due for 6-month checkup"},
        {"content": "Research new laptop options", "description": "Current laptop is slow"},
        {"content": "Clean out garage", "description": "Garage is full of junk"},
    ]

    print("Creating test tasks in Inbox...")
    for task in test_tasks:
        messages = send_message(
            provider, client, messages, agent.system_prompt, agent.model, tools, agent,
            f"Create task: '{task['content']}' with description '{task['description']}' in Inbox project"
        )

    # Step 2: List inbox tasks
    print_divider("STEP 2: List Current Inbox Tasks")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "List all tasks in the Inbox"
    )

    # Step 3: Teach pattern
    print_divider("STEP 3: Teach Pattern Recognition")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "From now on, when I say a task number followed by 'd', it means complete that task. For example, '5 d' means complete task 5. Please remember this pattern."
    )

    # Step 4: Start weekly review
    print_divider("STEP 4: Initiate Weekly Review - Inbox Processing")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Let's do a weekly review. Start by processing the inbox. Present the first batch."
    )

    # Step 5: Approve first batch
    print_divider("STEP 5: Approve First Batch")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Yes, looks good. Process these and show me the next batch."
    )

    # Step 6: Modify second batch
    print_divider("STEP 6: Request Modification on Next Batch")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Change task 1 to @highenergy and @long. Otherwise looks good."
    )

    # Step 7: Test pattern
    print_divider("STEP 7: Test Pattern Learning - Use '1 d'")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "1 d"
    )

    print_divider("TEST COMPLETE")

    print("\n📋 BEHAVIOR ANALYSIS:\n")
    print("Review the output above and check:")
    print("  1. ✓ Did agent call query_knowledge('learned_rules') for weekly review?")
    print("  2. ✓ Did agent present tasks in batches of 5 or less?")
    print("  3. ✓ Did agent intuit contexts, energy, duration for tasks?")
    print("  4. ✓ Did agent present without preamble/summary?")
    print("  5. ✓ Did agent process entire batch before moving to next?")
    print("  6. ✓ Did agent save the 'd' pattern with update_rules?")
    print("  7. ✓ Did agent complete task when user said '1 d'?")
    print("\nReview conversation above to identify any issues.")
