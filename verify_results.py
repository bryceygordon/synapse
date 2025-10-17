from dotenv import load_dotenv
from core.agents.todoist import TodoistAgent
import json

load_dotenv()

config = {
    'name': 'TodoistAgent',
    'provider': 'anthropic',
    'model': 'claude-sonnet-4-20250514',
    'system_prompt': 'Test prompt'
}

agent = TodoistAgent(config)

print("=" * 60)
print("VERIFICATION: Checking processed tasks")
print("=" * 60)

# Get tasks in processed project (sorted by creation date)
result = agent.list_tasks(project_name="processed", sort_by="created_desc")
result_data = json.loads(result)

if result_data["status"] == "success":
    tasks = result_data["data"]["tasks"]
    print(f"\nFound {len(tasks)} task(s) in #processed")

    # Show our 4 test tasks (newest)
    print("\nMost recent tasks:")
    for i, task in enumerate(tasks[:4], 1):
        labels_str = ', '.join('@' + l for l in task['labels'])
        print(f"\n{i}. {task['content']}")
        print(f"   Labels: {labels_str}")

# Check for next actions
print("\n" + "=" * 60)
print("VERIFICATION: Checking @next actions")
print("=" * 60)

result = agent.list_next_actions()
result_data = json.loads(result)

if result_data["status"] == "success":
    print(f"\nFound {result_data['data']['count']} @next action(s)")
    # Get full details
    for task_id in result_data['data']['task_ids'][:6]:  # Show first 6
        task = agent.api.get_task(task_id)
        labels_str = ', '.join('@' + l for l in task.labels if l != 'next')
        print(f"  • {task.content}")
        if labels_str:
            print(f"    Tags: {labels_str}")
