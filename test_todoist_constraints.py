#!/usr/bin/env python3
"""
Test script for TodoistAgent constrained tools
"""
import os
import sys
from core.agent_loader import load_agent

# Load the agent
agent = load_agent("todoist")

print("=" * 80)
print("TODOIST AGENT - CONSTRAINED TOOLS TEST")
print("=" * 80)

# Test 1: Create test tasks in Inbox using the new `capture` tool
print("\n📝 TEST 1: Creating test tasks using capture() tool...")
print("-" * 80)

test_tasks = [
    "Clean out the garage",
    "Call Bec about dinner plans",
    "Buy milk and bread",
    "Fertilize the front lawn",
    "Fix leaking tap in bathroom",
]

task_ids = []
for task_content in test_tasks:
    print(f"\nCapturing: '{task_content}'")
    result = agent.capture(task_content)
    print(f"Result: {result}")
    # Extract task_id from result if successful
    import json
    try:
        result_data = json.loads(result)
        if result_data.get("status") == "success":
            task_id = result_data.get("data", {}).get("task_id")
            if task_id:
                task_ids.append((task_id, task_content))
                print(f"✓ Created task ID: {task_id}")
    except:
        pass

print(f"\n✓ Created {len(task_ids)} test tasks")

# Test 2: List tasks in Inbox to verify
print("\n\n📋 TEST 2: Listing Inbox tasks...")
print("-" * 80)
inbox_result = agent.list_tasks(project_name="Inbox")
print(inbox_result)

# Test 3: Inspect tool schemas to verify enum constraints
print("\n\n🔍 TEST 3: Inspecting make_actionable tool schema for enum constraints...")
print("-" * 80)

from core.schema_generator import generate_tool_schemas
schemas = generate_tool_schemas(agent)

# Find make_actionable schema
make_actionable_schema = None
for schema in schemas:
    if schema.get("name") == "make_actionable":
        make_actionable_schema = schema
        break

if make_actionable_schema:
    print("✓ Found make_actionable tool schema")
    print(f"\nTool: {make_actionable_schema['name']}")
    print(f"Description: {make_actionable_schema['description']}")
    print("\nParameters with enum constraints:")

    params = make_actionable_schema.get("parameters", {}).get("properties", {})
    for param_name, param_def in params.items():
        if "enum" in param_def:
            print(f"\n  {param_name}:")
            print(f"    type: {param_def.get('type')}")
            print(f"    enum: {param_def.get('enum')}")
            print(f"    description: {param_def.get('description')}")
else:
    print("❌ make_actionable tool not found in schemas!")

# Test 4: Also check ask_question schema
print("\n\n🔍 TEST 4: Inspecting ask_question tool schema for person enum...")
print("-" * 80)

ask_question_schema = None
for schema in schemas:
    if schema.get("name") == "ask_question":
        ask_question_schema = schema
        break

if ask_question_schema:
    print("✓ Found ask_question tool schema")
    params = ask_question_schema.get("parameters", {}).get("properties", {})
    person_param = params.get("person", {})
    if "enum" in person_param:
        print(f"\n  person parameter:")
        print(f"    enum: {person_param.get('enum')}")
        print("    ✓ Enum constraint working!")
    else:
        print("    ❌ No enum constraint found!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Summary
print("\n📊 SUMMARY:")
print(f"  - Test tasks created: {len(task_ids)}")
print(f"  - Enum constraints in make_actionable: {bool(make_actionable_schema and any('enum' in p for p in make_actionable_schema.get('parameters', {}).get('properties', {}).values()))}")
print(f"  - Enum constraints in ask_question: {bool(ask_question_schema and any('enum' in p for p in ask_question_schema.get('parameters', {}).get('properties', {}).values()))}")

# List all created task IDs for next test
print("\n🔑 Created Task IDs for next test:")
for task_id, content in task_ids:
    print(f"  {task_id}: {content}")
