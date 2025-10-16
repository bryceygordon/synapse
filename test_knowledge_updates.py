#!/usr/bin/env python3
"""
Test knowledge update system.

Tests:
1. Query existing knowledge
2. Add new rule
3. Verify existing rules preserved
4. Test rule affects behavior
5. Revert the change
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
                print(f"  → {tool_call.name}({args_str[:150]}...)" if len(args_str) > 150 else f"  → {tool_call.name}({args_str})")

                try:
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)

                    # Parse and display key info
                    try:
                        data = json.loads(result)
                        if data.get("status") == "success":
                            msg = data.get('message', 'Success')
                            if len(msg) > 100:
                                msg = msg[:100] + "..."
                            print(f"    ✓ {msg}")

                            # Show content preview if knowledge query
                            if tool_call.name == "query_knowledge" and data.get("content"):
                                content = data["content"][:300]
                                print(f"    📄 Content preview: {content}...")
                        else:
                            print(f"    ✗ {data.get('error', 'Error')}")
                    except:
                        if len(result) < 200:
                            print(f"    Result: {result}")

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
    print_divider("KNOWLEDGE UPDATE SYSTEM TEST")

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

    # Test 1: Query existing knowledge about chores
    print_divider("TEST 1: Query Current Chore Rules")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "What are the current rules for processing chore tasks? Query your learned_rules knowledge."
    )

    # Test 2: Teach a new pattern - "painting tasks"
    print_divider("TEST 2: Add New Rule - Painting Tasks")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "I want to teach you a new pattern: Any task that mentions 'painting' should automatically get @house, @medenergy, and @weather labels. The @weather is important because you can't paint when it's raining. Please save this rule."
    )

    # Test 3: Verify existing rules weren't destroyed
    print_divider("TEST 3: Verify Existing Rules Still Exist")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Query your learned_rules again and confirm that the original chore rules are still there, along with the new painting rule."
    )

    # Test 4: Test that the rule affects behavior
    print_divider("TEST 4: Test New Rule Application")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "I have a task 'Paint the bedroom walls'. What contexts, energy, and labels would you suggest for this based on your rules?"
    )

    # Test 5: Update the rule (modify it)
    print_divider("TEST 5: Modify Existing Rule")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Actually, painting tasks should be @highenergy not @medenergy, because they take a lot of effort. Please update the painting rule."
    )

    # Test 6: Verify the modification
    print_divider("TEST 6: Test Modified Rule")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Now suggest contexts for 'Paint the garden fence'. It should reflect the updated @highenergy rule."
    )

    # Test 7: Revert the rule completely
    print_divider("TEST 7: Remove Painting Rule")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Actually, I don't want a special rule for painting tasks. Please remove the painting rule from your knowledge and query learned_rules to confirm it's gone."
    )

    # Test 8: Verify removal
    print_divider("TEST 8: Verify Rule Removed")
    messages = send_message(
        provider, client, messages, agent.system_prompt, agent.model, tools, agent,
        "Suggest contexts for 'Paint the front door' now. Without the painting rule, what would you suggest?"
    )

    print_divider("TEST COMPLETE")

    print("\n📋 ANALYSIS CHECKLIST:\n")
    print("  1. ✓ Did agent query knowledge correctly?")
    print("  2. ✓ Did agent add new rule without destroying existing rules?")
    print("  3. ✓ Did agent explain what was being added/modified?")
    print("  4. ✓ Did new rule affect task suggestions?")
    print("  5. ✓ Did agent successfully modify existing rule?")
    print("  6. ✓ Did agent successfully remove rule?")
    print("  7. ✓ Did behavior revert after removal?")
    print("\nReview the conversation above to verify all aspects worked correctly.")
