#!/usr/bin/env python3
"""Quick test of query_knowledge with OpenAI."""

import os
from dotenv import load_dotenv
from core.agent_loader import load_agent
from core.providers import get_provider

load_dotenv()

# Load agent
agent = load_agent(agent_name="todoist_openai")
print(f"Agent: {agent.name}")

# Test direct call
print("\n=== Direct Call Test ===")
result = agent.query_knowledge("learned_rules")
print(f"Result length: {len(result)}")
print(f"First 200 chars: {result[:200]}")

# Test via provider
print("\n=== Provider Call Test ===")
provider = get_provider(agent.provider)
client = provider.create_client()
tools = provider.format_tool_schemas(agent)

messages = [{"role": "user", "content": "Please query the learned_rules knowledge topic"}]

response = provider.send_message(
    client=client,
    messages=messages,
    system_prompt=agent.system_prompt,
    model=agent.model,
    tools=tools
)

print(f"Tool calls: {len(response.tool_calls) if response.tool_calls else 0}")
if response.tool_calls:
    for tc in response.tool_calls:
        print(f"  - {tc.name}({tc.arguments})")
        result = getattr(agent, tc.name)(**tc.arguments)
        print(f"  Result: {result[:200]}")
