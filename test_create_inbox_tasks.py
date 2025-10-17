#!/usr/bin/env python3
"""
Create test tasks in Todoist Inbox for testing the wizard workflow.
"""
import os
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

# Create test tasks
test_tasks = [
    {
        'content': 'buy groceries for dinner',
        'description': 'Need milk, eggs, bread, and vegetables'
    },
    {
        'content': 'plan vacation to japan',
        'description': 'Research flights, hotels, and create itinerary'
    },
    {
        'content': 'call dentist to schedule cleaning',
        'description': ''
    },
    {
        'content': 'organize home office',
        'description': 'File papers, clean desk, organize cables and equipment'
    }
]

print('Creating test tasks in Inbox...')
created_ids = []
for task_data in test_tasks:
    task = agent.api.add_task(
        content=task_data['content'],
        description=task_data['description'] if task_data['description'] else None
    )
    created_ids.append(task.id)
    print(f'✓ Created: {task.content} (ID: {task.id})')

print(f'\nCreated {len(test_tasks)} test tasks')
print(f'Task IDs: {", ".join(created_ids)}')
