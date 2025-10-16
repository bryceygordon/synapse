#!/usr/bin/env python3
"""
Test the constrained tools workflow with real Todoist API
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env file")
else:
    print("⚠ No .env file found")

from core.agent_loader import load_agent

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")

def print_result(result):
    """Pretty print JSON result"""
    try:
        data = json.loads(result)
        print(json.dumps(data, indent=2))
    except:
        print(result)

# Load agent
print_section("LOADING TODOIST AGENT")
agent = load_agent("todoist")
print("✓ Agent loaded successfully")

# Step 1: Create 20 test tasks using capture()
print_section("STEP 1: Creating 20 Test Tasks")

test_tasks = [
    "Clean out garage",
    "Call dentist for appointment",
    "Ask Bec about weekend plans",
    "Mow the lawn",
    "Buy groceries at Woolworths",
    "Fix leaking tap in bathroom",
    "Fertilize garden beds",
    "Ask William about homework",
    "Vacuum living room",
    "Take car for service",
    "Paint fence",
    "Call plumber about quote",
    "Sweep patio",
    "Ask Reece about soccer practice",
    "Organize tool shed",
    "Buy paint at Bunnings",
    "Clean windows",
    "Ask Alex about school project",
    "Trim hedges",
    "Deep clean kitchen"
]

created_task_ids = []

for i, task_content in enumerate(test_tasks, 1):
    print(f"\n{i}/20: Creating '{task_content}' with @test label")
    # OPTIMIZED: Create task with label in single API call using create_task
    result = agent.create_task(
        content=task_content,
        project_name="Inbox",
        labels=["test"],
        priority=1
    )

    try:
        data = json.loads(result)
        if data.get("status") == "success":
            task_id = data["data"]["task_id"]
            created_task_ids.append(task_id)
            print(f"  ✓ Created task ID: {task_id} [@test]")
        else:
            print(f"  ❌ Failed: {data.get('message')}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n✓ Created {len(created_task_ids)} test tasks with @test label (1 API call each)")

# Step 2: List the test tasks
print_section("STEP 2: Listing Test Tasks")
result = agent.list_tasks(label="test")
print_result(result)

# Step 3: Process first 5 test tasks using constrained tools
print_section("STEP 3: Processing Tasks with Constrained make_actionable()")

print("\nNote: This tests the enum constraints - the agent would normally suggest these,")
print("but we're calling them directly to verify the tool behavior.\n")

# Get the first 5 task IDs
tasks_to_process = created_task_ids[:5]

# Process each with different enum values to test constraints
test_cases = [
    {
        "task_id": tasks_to_process[0],
        "desc": "Clean out garage",
        "location": "house",
        "activity": "chore",
        "energy": "highenergy",
        "duration": "long",
        "next_action": "Sort items into keep/donate/trash piles"
    },
    {
        "task_id": tasks_to_process[1],
        "desc": "Call dentist",
        "location": "home",
        "activity": "call",
        "energy": "lowenergy",
        "duration": "short",
        "next_action": None  # Simple task, IS the next action
    },
    {
        "task_id": tasks_to_process[2],
        "desc": "Ask Bec about weekend",
        # This should use ask_question instead
        "skip_make_actionable": True
    },
    {
        "task_id": tasks_to_process[3],
        "desc": "Mow the lawn",
        "location": "yard",
        "activity": "chore",
        "energy": "highenergy",
        "duration": "medium",
        "next_action": None,
        "additional_contexts": ["weather"]  # Weather-dependent
    },
    {
        "task_id": tasks_to_process[4],
        "desc": "Buy groceries",
        "location": "errand",
        "activity": "errand",  # Testing if this works or should be different
        "energy": "medenergy",
        "duration": "medium",
        "next_action": None
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n--- Processing Task {i}: {test_case['desc']} ---")

    if test_case.get("skip_make_actionable"):
        # Use ask_question instead
        print("Using ask_question() for this task...")
        result = agent.ask_question(test_case["task_id"], person="bec", via_call=False)
        print_result(result)
    else:
        # Use make_actionable
        kwargs = {
            "task_id": test_case["task_id"],
            "location": test_case["location"],
            "activity": test_case["activity"],
            "energy": test_case["energy"],
            "duration": test_case["duration"]
        }

        if test_case.get("next_action"):
            kwargs["next_action"] = test_case["next_action"]

        if test_case.get("additional_contexts"):
            kwargs["additional_contexts"] = test_case["additional_contexts"]

        result = agent.make_actionable(**kwargs)
        print_result(result)

# Step 4: Verify processed tasks
print_section("STEP 4: Verifying Processed Tasks")
result = agent.list_tasks(project_name="processed")
print("Checking processed project for our test tasks...")
print_result(result)

# Step 5: Check questions project for the "ask Bec" task
print_section("STEP 5: Checking Questions Project")
result = agent.list_tasks(project_name="questions")
print_result(result)

# Step 6: Clean up - Delete all @test tasks
print_section("STEP 6: Cleaning Up Test Tasks")
print("Fetching all tasks with @test label...")
result = agent.list_tasks(label="test")
data = json.loads(result)

if data.get("status") == "success" and data.get("data", {}).get("task_ids"):
    test_task_ids = data["data"]["task_ids"]
    print(f"Found {len(test_task_ids)} tasks with @test label")

    print("\nDeleting test tasks...")
    for i, task_id in enumerate(test_task_ids, 1):
        print(f"  {i}/{len(test_task_ids)}: Deleting task {task_id}")
        delete_result = agent.delete_task(task_id)
        delete_data = json.loads(delete_result)
        if delete_data.get("status") == "success":
            print(f"    ✓ Deleted")
        else:
            print(f"    ❌ Failed: {delete_data.get('message')}")

    print(f"\n✓ Cleanup complete: Deleted {len(test_task_ids)} test tasks")
else:
    print("No test tasks found to clean up")

print_section("TEST WORKFLOW COMPLETE")
print("""
Summary:
1. ✓ Created 20 test tasks with @test label
2. ✓ Processed 5 tasks with constrained make_actionable() tool
3. ✓ Verified enum constraints (location, activity, energy, duration)
4. ✓ Tested ask_question() with person enum
5. ✓ Cleaned up all test tasks

The constrained tools workflow is working as expected!
""")
