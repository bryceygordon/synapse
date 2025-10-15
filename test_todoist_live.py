"""
Live integration test for TodoistAgent.
Tests real API interactions with comprehensive scenarios.
"""

import os
import time
import json
from dotenv import load_dotenv
from core.agent_loader import load_agent

# Load environment
load_dotenv()

def print_result(test_name, result):
    """Pretty print test results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

    try:
        data = json.loads(result)
        print(f"Status: {data.get('status', 'unknown')}")
        if data.get('status') == 'success':
            print(f"✅ {data.get('message', 'Success')}")
            if data.get('data'):
                print(f"\nData:")
                for key, value in data['data'].items():
                    if key not in ['content']:  # Skip redundant content
                        print(f"  {key}: {value}")
        else:
            print(f"❌ Error: {data.get('message', 'Unknown error')}")
            print(f"   Type: {data.get('error_type', 'Unknown')}")
    except json.JSONDecodeError:
        print(f"Raw result: {result[:500]}")

    print(f"{'='*60}\n")
    return result

def wait_for_api(seconds=2):
    """Wait for Todoist API to sync."""
    print(f"⏳ Waiting {seconds}s for API sync...")
    time.sleep(seconds)

def main():
    print("🚀 Starting TodoistAgent Live Integration Tests")
    print("📝 All tasks will be labeled with @test for easy cleanup\n")

    # Load agent
    agent = load_agent(agent_name="todoist")
    print(f"✅ Loaded agent: {agent.name}")
    print(f"   Provider: {agent.provider}")
    print(f"   Model: {agent.model}\n")

    # Store task IDs for later tests
    task_ids = {}

    # TEST 1: Get current time
    result = print_result(
        "1. Get Current Time",
        agent.get_current_time()
    )
    data = json.loads(result)
    current_date = data['data']['date']
    print(f"📅 Current date for testing: {current_date}\n")

    # TEST 2: List projects
    print_result(
        "2. List Available Projects",
        agent.list_projects()
    )

    # TEST 3: List labels
    print_result(
        "3. List Available Labels",
        agent.list_labels()
    )

    # TEST 4: Create basic task
    result = print_result(
        "4. Create Basic Task",
        agent.create_task(
            content="[TEST] Basic task - please ignore",
            project_name="Inbox",
            labels=["test"],
            description="This is a test task created by automated testing"
        )
    )
    data = json.loads(result)
    if data['status'] == 'success':
        task_ids['basic'] = data['data']['task_id']

    wait_for_api()

    # TEST 5: Create task with natural language due date
    result = print_result(
        "5. Create Task with Natural Language Due Date",
        agent.create_task(
            content="[TEST] Task due tomorrow afternoon",
            project_name="Inbox",
            labels=["test"],
            due_string="tomorrow at 2pm"
        )
    )
    data = json.loads(result)
    if data['status'] == 'success':
        task_ids['due_date'] = data['data']['task_id']

    wait_for_api()

    # TEST 6: Create recurring task
    result = print_result(
        "6. Create Recurring Task",
        agent.create_task(
            content="[TEST] Recurring task - every monday",
            project_name="Inbox",
            labels=["test"],
            due_string="every monday at 9am"
        )
    )
    data = json.loads(result)
    if data['status'] == 'success':
        task_ids['recurring'] = data['data']['task_id']

    wait_for_api()

    # TEST 7: Create task with duration
    result = print_result(
        "7. Create Task with Duration",
        agent.create_task(
            content="[TEST] Task with 30 minute duration",
            project_name="Inbox",
            labels=["test"],
            due_string="tomorrow at 10am",
            duration=30,
            duration_unit="minute"
        )
    )
    data = json.loads(result)
    if data['status'] == 'success':
        task_ids['duration'] = data['data']['task_id']

    wait_for_api()

    # TEST 8: Create parent task for subtask test
    result = print_result(
        "8. Create Parent Task",
        agent.create_task(
            content="[TEST] Parent task for subtasks",
            project_name="Inbox",
            labels=["test"],
            priority=2
        )
    )
    data = json.loads(result)
    if data['status'] == 'success':
        task_ids['parent'] = data['data']['task_id']

    wait_for_api()

    # TEST 9: Create subtask
    if 'parent' in task_ids:
        result = print_result(
            "9. Create Subtask",
            agent.create_task(
                content="[TEST] Subtask of parent",
                project_name="Inbox",
                labels=["test"],
                parent_id=task_ids['parent']
            )
        )
        data = json.loads(result)
        if data['status'] == 'success':
            task_ids['subtask'] = data['data']['task_id']

    wait_for_api()

    # TEST 10: List all test tasks
    result = print_result(
        "10. List All Tasks with @test Label",
        agent.list_tasks(label="test")
    )

    # TEST 10b: Verify created_at is included and test sorting
    data = json.loads(result)
    if data['status'] == 'success' and len(data['data']['tasks']) > 0:
        print(f"✅ Verifying created_at field is present...")
        first_task = data['data']['tasks'][0]
        if 'created_at' in first_task:
            print(f"   ✓ created_at found: {first_task['created_at']}")
        else:
            print(f"   ❌ created_at NOT found in task data!")

    # TEST 10c: Test sorting by created_desc (newest first)
    result = print_result(
        "10c. List Test Tasks Sorted by Created Date (Newest First)",
        agent.list_tasks(label="test", sort_by="created_desc")
    )
    data = json.loads(result)
    if data['status'] == 'success':
        tasks = data['data']['tasks']
        if len(tasks) >= 2:
            print(f"✅ Sorting verification:")
            print(f"   First task: {tasks[0]['content'][:50]}... (created: {tasks[0]['created_at']})")
            print(f"   Last task: {tasks[-1]['content'][:50]}... (created: {tasks[-1]['created_at']})")

            # Verify sorting
            first_created = tasks[0]['created_at']
            last_created = tasks[-1]['created_at']
            if first_created >= last_created:
                print(f"   ✓ Tasks correctly sorted newest first")
            else:
                print(f"   ⚠️  Warning: Tasks may not be correctly sorted")

    # TEST 11: Get specific task details
    if 'basic' in task_ids:
        print_result(
            "11. Get Task Details",
            agent.get_task(task_ids['basic'])
        )

    # TEST 12: Update task (change priority and due date)
    if 'basic' in task_ids:
        result = print_result(
            "12. Update Task (Priority + Due Date)",
            agent.update_task(
                task_id=task_ids['basic'],
                priority=4,
                due_string="today at 5pm"
            )
        )

    wait_for_api()

    # TEST 13: Verify update
    if 'basic' in task_ids:
        print_result(
            "13. Verify Update",
            agent.get_task(task_ids['basic'])
        )

    # TEST 14: Add comment
    if 'basic' in task_ids:
        print_result(
            "14. Add Comment to Task",
            agent.add_comment(
                task_id=task_ids['basic'],
                comment="This is a test comment added by automation"
            )
        )

    wait_for_api()

    # TEST 15: Get comments
    if 'basic' in task_ids:
        print_result(
            "15. Get Task Comments",
            agent.get_comments(task_ids['basic'])
        )

    # TEST 16: Complete task
    if 'duration' in task_ids:
        print_result(
            "16. Complete Task",
            agent.complete_task(task_ids['duration'])
        )

    wait_for_api()

    # TEST 17: Reopen task
    if 'duration' in task_ids:
        print_result(
            "17. Reopen Completed Task",
            agent.reopen_task(task_ids['duration'])
        )

    wait_for_api()

    # TEST 18: Move task to Processed project
    if 'basic' in task_ids:
        print_result(
            "18. Move Task to Processed Project",
            agent.move_task(
                task_id=task_ids['basic'],
                project_name="Processed"
            )
        )

    wait_for_api()

    # TEST 19: Verify move
    if 'basic' in task_ids:
        print_result(
            "19. Verify Task Was Moved",
            agent.get_task(task_ids['basic'])
        )

    # TEST 20: List all test tasks in Processed
    print_result(
        "20. List Test Tasks in Processed",
        agent.list_tasks(
            project_name="Processed",
            label="test"
        )
    )

    # CLEANUP: Delete all test tasks
    print("\n" + "="*60)
    print("CLEANUP: Deleting All Test Tasks")
    print("="*60)

    for task_name, task_id in task_ids.items():
        print(f"🗑️  Deleting {task_name} task...")
        result = agent.delete_task(task_id)
        data = json.loads(result)
        if data['status'] == 'success':
            print(f"   ✅ Deleted: {data['data']['content']}")
        else:
            print(f"   ❌ Failed: {data.get('message')}")
        time.sleep(0.5)  # Small delay between deletions

    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE!")
    print("="*60)
    print(f"\nTotal tasks created: {len(task_ids)}")
    print("All test tasks have been cleaned up.")

if __name__ == "__main__":
    main()
