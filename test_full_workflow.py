#!/usr/bin/env python3
"""
Complete end-to-end test of the inbox processing wizard workflow.
This simulates the full flow without interactive input.
"""
import json
from dotenv import load_dotenv
from core.agents.todoist import TodoistAgent

# Load environment variables
load_dotenv()

# Initialize agent
config = {
    'name': 'TodoistAgent',
    'provider': 'anthropic',
    'model': 'claude-sonnet-4-20250514',
    'system_prompt': 'Test prompt'
}

agent = TodoistAgent(config)

print("=" * 70)
print("  COMPLETE INBOX PROCESSING WORKFLOW - END-TO-END TEST")
print("=" * 70)

# Phase 1: Fetch and prepare tasks
print("\n[PHASE 1] Fetching inbox tasks (sorted by creation date)...")
result = agent.list_tasks(project_name="Inbox", sort_by="created_desc")
result_data = json.loads(result)

if result_data["status"] != "success":
    print(f"Error: {result_data['message']}")
    exit(1)

tasks_data = result_data["data"]["tasks"]
print(f"✓ Found {len(tasks_data)} inbox task(s)")

# Take our 4 test tasks
tasks = []
for task_data in tasks_data[:4]:
    task_full = agent.api.get_task(task_data["id"])
    tasks.append({
        'id': task_full.id,
        'content': task_full.content,
        'description': task_full.description or ''
    })
    print(f"  • {task_full.content}")

# Phase 2: Generate simulated wizard output (what would come from interactive wizard)
print("\n[PHASE 2] Generating wizard output (simulating user decisions)...")
wizard_instructions = ["WIZARD OUTPUT - Process these task updates:\n"]
wizard_instructions.append("DESTINATION_PROJECT: processed\n")

created_subtask_count = 0
for i, task in enumerate(tasks, 1):
    content_lower = task['content'].lower()

    # Determine task type
    multi_step_keywords = ['plan', 'organize', 'research']
    is_multi_step = any(keyword in content_lower for keyword in multi_step_keywords)

    wizard_instructions.append(f"task_id: {task['id']}")

    # Simple vs multi-step
    wizard_instructions.append(f"- is_simple: {str(not is_multi_step).lower()}")

    # Next action for multi-step tasks
    if is_multi_step:
        if 'plan' in content_lower or 'research' in content_lower:
            next_action = "Research and gather information"
        elif 'organize' in content_lower:
            next_action = "Identify what needs organizing"
        wizard_instructions.append(f'- next_action: "{next_action}"')
        created_subtask_count += 1

    # Energy
    if 'call' in content_lower:
        energy = 'l'
    elif 'organize' in content_lower or 'plan' in content_lower:
        energy = 'h'
    else:
        energy = 'm'
    wizard_instructions.append(f"- energy: {energy}")

    # Duration
    if 'call' in content_lower:
        duration = 's'
    elif 'organize' in content_lower or 'plan' in content_lower:
        duration = 'l'
    else:
        duration = 'm'
    wizard_instructions.append(f"- duration: {duration}")

    # Labels
    labels = []
    if 'call' in content_lower:
        labels.append('add call')
        labels.append('add home')
    elif 'buy' in content_lower or 'groceries' in content_lower:
        labels.append('add errand')
    elif 'organize' in content_lower:
        labels.append('add chore')
        labels.append('add home')
    else:
        labels.append('add home')

    # Simple tasks get @next automatically
    if not is_multi_step:
        labels.append('add next')

    wizard_instructions.append(f'- labels: "{", ".join(labels)}"')
    wizard_instructions.append("")  # Blank line

wizard_instructions.append(f"\nTotal: {len(tasks)} task(s) to process")
wizard_output = "\n".join(wizard_instructions)

print("✓ Wizard output generated")
print(f"  • {len(tasks)} tasks to process")
print(f"  • {created_subtask_count} next action subtasks will be created")

# Phase 3: Process wizard output
print("\n[PHASE 3] Processing wizard output...")
process_result = agent.process_wizard_output(wizard_output)
process_data = json.loads(process_result)

if process_data["status"] == "success":
    print(f"✅ {process_data['message']}")
    print(f"  • Processed: {process_data['data']['successful']} task(s)")
    print(f"  • Moved to: #{process_data['data']['destination_project']}")
    print(f"  • Created: {len(process_data['data']['created_subtasks'])} next action subtask(s)")

    created_subtasks = process_data['data']['created_subtasks']

    # Phase 4: Generate tag suggestions for subtasks
    if created_subtasks:
        print("\n[PHASE 4] Generating tag suggestions for next action subtasks...")
        suggest_result = agent.suggest_next_action_tags(created_subtasks)
        suggest_data = json.loads(suggest_result)

        if suggest_data["status"] == "success":
            suggestions = suggest_data['data']['suggestions']
            print(f"✓ Generated suggestions for {len(suggestions)} subtask(s)")

            # Phase 5: Simulate user approving suggestions (would be interactive wizard)
            print("\n[PHASE 5] Simulating user approval of tag suggestions...")
            tag_instructions = ["SUBTASK_TAG_UPDATES - Apply these tag updates:\n"]

            for suggestion in suggestions:
                tag_instructions.append(f"subtask_id: {suggestion['subtask_id']}")
                tag_instructions.append(f'- labels: "{suggestion["suggested_labels"]}"')
                tag_instructions.append(f"- energy: {suggestion['suggested_energy']}")
                tag_instructions.append(f"- duration: {suggestion['suggested_duration']}")
                tag_instructions.append("")

            tag_instructions.append(f"\nTotal: {len(suggestions)} subtask(s) to update")
            tag_output = "\n".join(tag_instructions)

            # Phase 6: Process subtask tags
            print("\n[PHASE 6] Applying tags to subtasks...")
            tag_result = agent.process_subtask_tags(tag_output)
            tag_data = json.loads(tag_result)

            if tag_data["status"] == "success":
                print(f"✅ {tag_data['message']}")
                print(f"  • Tagged: {tag_data['data']['successful']} subtask(s)")
            else:
                print(f"❌ Error: {tag_data['message']}")
        else:
            print(f"❌ Error: {suggest_data['message']}")
    else:
        print("\n[PHASE 4-6] Skipped - No multi-step tasks (no subtasks created)")

    # Summary
    print("\n" + "=" * 70)
    print("  WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\n✓ Processed {len(tasks)} inbox tasks")
    print(f"✓ Moved all tasks to #processed")
    if created_subtasks:
        print(f"✓ Created and tagged {len(created_subtasks)} next action subtask(s)")
    print("\nCheck Todoist to see the results!")

else:
    print(f"❌ Error: {process_data['message']}")
