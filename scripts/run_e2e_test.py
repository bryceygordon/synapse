# scripts/run_e2e_test.py

import json
import os
import sys
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.todoist_engine import tasks
import yaml
from core.providers import get_provider

# Initialize Rich console
console = Console()

def create_test_tasks(api, project_name):
    """Creates a set of unique tasks for the test run."""
    console.print(f"Creating test tasks in project '{project_name}'...")
    test_run_id = str(uuid.uuid4())[:8]
    task_definitions = [
        {
            "content": f"[E2E-Test-{test_run_id}] Simple task rename @home p1 tomorrow",
            "description": "This is a simple task that should be renamed and processed."
        },
        {
            "content": f"[E2E-Test-{test_run_id}] Multi-step task",
            "description": "This task should become a parent task with a subtask."
        },
        {
            "content": f"[E2E-Test-{test_run_id}] Task with contextual tags",
            "description": "This task about poisoning weeds should get 'yard' and 'weather' tags."
        },
        {
            "content": f"[E2E-Test-{test_run_id}] Task to complete",
            "description": "This task should be marked as complete directly by the wizard."
        },
        {
            "content": f"[E2E-Test-{test_run_id}] Task to delete",
            "description": "This task should be deleted directly by the wizard."
        },
        {
            "content": f"[E2E-Test-{test_run_id}] Task to leave in inbox",
            "description": "This task should be left in the inbox after a partial run."
        }
    ]
    created_tasks = []
    for definition in task_definitions:
        task = tasks.create_task(api, **definition, project_name=project_name)
        created_tasks.append(task)
        console.print(f"  - Created task: {task.content}")
    return created_tasks, test_run_id

def run_automated_test():
    """
    An automated, non-interactive script to perform an end-to-end test
    of the Todoist inbox processing workflow.
    """
    test_run_id = None
    tasks_to_process_ids = []
    tasks_to_complete_ids = []
    tasks_to_delete_ids = []
    tasks_left_in_inbox_ids = []
    try:
        # --- 1. Setup ---
        api = tasks.get_api_client()
        console.print("[bold green]Successfully connected to Todoist API.[/bold green]")

        inbox_project = tasks.find_project_by_name(api, "Inbox")
        processed_project = tasks.find_project_by_name(api, "processed")
        if not inbox_project or not processed_project:
            console.print("[bold red]Error: Could not find 'Inbox' or 'processed' project.[/bold red]")
            return None, [], [], [], []

        # --- 2. Create Test Data ---
        test_tasks, test_run_id = create_test_tasks(api, inbox_project.name)
        if not test_tasks:
            console.print("[bold red]Error: Failed to create test tasks.[/bold red]")
            return test_run_id, [], [], [], []

        # Assign tasks to their simulated outcomes
        tasks_to_process_ids = [test_tasks[0].id, test_tasks[1].id]
        tasks_to_complete_ids = [test_tasks[2].id]
        tasks_to_delete_ids = [test_tasks[3].id]
        tasks_left_in_inbox_ids = [test_tasks[4].id] # Task to be "exited" on

        # --- 3. Simulate Wizard Actions ---
        console.print("\n[bold blue]Simulating wizard actions (partial run)...[/bold blue]")
        agent_processing_list = [
            # Task 1: Rename
            {"original_task_id": test_tasks[0].id, "original_content": test_tasks[0].content, "is_multistep": False, "should_rename": True, "user_input": "Renamed simple task @home p1 tomorrow"},
            # Task 2: Multi-step
            {"original_task_id": test_tasks[1].id, "original_content": test_tasks[1].content, "is_multistep": True, "should_rename": False, "user_input": "First subtask for the multi-step item @computer"},
        ]
        console.print(f"  - Simulating 'process' for {len(agent_processing_list)} tasks.")

        # Task 3: Complete
        console.print(f"  - Simulating 'complete' for task: {test_tasks[2].content}")
        tasks.complete_task(api, tasks_to_complete_ids[0])

        # Task 4: Delete
        console.print(f"  - Simulating 'delete' for task: {test_tasks[3].content}")
        tasks.delete_task(api, tasks_to_delete_ids[0])

        # Task 5: Simulate exiting
        console.print(f"  - Simulating 'exit' on task: {test_tasks[4].content}")
        console.print("[green]✓ Partial wizard simulation complete.[/green]")


        # --- 4. Agent Processing ---
        if agent_processing_list:
            console.print("\n[bold blue]Handing off to the agent for refinement...[/bold blue]")
            config_path = "agents/todoist_inbox_processor.yaml"
            with open(config_path, "r") as f:
                agent_config = yaml.safe_load(f)

            provider = get_provider(agent_config["provider"])
            client = provider.create_client()

            input_json = json.dumps(agent_processing_list, indent=2)
            console.print(Panel(Syntax(input_json, "json", theme="monokai", line_numbers=True), title="[bold cyan]Data Sent to Agent[/bold cyan]"))

            with console.status("[bold yellow]Agent is processing...[/bold yellow]", spinner="dots"):
                response = provider.send_message(
                    client=client,
                    system_prompt=agent_config["system_prompt"],
                    user_prompt=input_json,
                    model=agent_config["model"],
                    tools=[],
                    discussion=[]
                )

            refined_json_str = response.text
            console.print(Panel(Syntax(refined_json_str, "json", theme="monokai", line_numbers=True), title="[bold green]Refined Data Received from Agent[/bold green]"))

            # --- 5. Apply Changes ---
            try:
                if refined_json_str.strip().startswith("```json"):
                    refined_json_str = refined_json_str.strip()[7:-3].strip()

                refined_tasks = json.loads(refined_json_str)
                with console.status("[bold yellow]Applying changes...[/bold yellow]", spinner="dots"):
                    for task_op in refined_tasks:
                        api_params = task_op['api_params']
                        if 'labels' not in api_params:
                            api_params['labels'] = []
                        if 'next' not in api_params['labels']:
                            api_params['labels'].append('next')

                        original_id = task_op['original_task_id']

                        if task_op['action'] == 'update':
                            tasks.update_task(api, task_id=original_id, **api_params)
                        elif task_op['action'] == 'create_subtask':
                            api_params['parent_id'] = original_id
                            tasks.create_task(api, **api_params)

                        tasks.move_task(api, task_id=original_id, project_id=processed_project.id)
                console.print("[bold green]✓ All changes applied successfully![/bold green]")

            except json.JSONDecodeError:
                console.print(Panel("[bold red]Error: Agent returned invalid JSON.[/bold red]", border_style="red"))
            except Exception as e:
                console.print(Panel(f"[bold red]An error occurred during final submission:[/bold red] {e}", border_style="red"))
        else:
            console.print("[yellow]No tasks were marked for agent processing.[/yellow]")

        return test_run_id, tasks_to_process_ids, tasks_to_complete_ids, tasks_to_delete_ids, tasks_left_in_inbox_ids

    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred:[/bold red] {e}", border_style="red"))
    return test_run_id, [], [], [], []

def verify_results(api, test_run_id, processed_ids, completed_ids, deleted_ids, left_in_inbox_ids):
    """Fetches and displays the processed tasks for verification."""
    console.print("\n[bold blue]--- Verifying Results ---[/bold blue]")
    if not test_run_id:
        console.print("[bold red]Verification skipped due to test failure.[/bold red]")
        return

    console.print(f"Searching for tasks with test run ID: [cyan]{test_run_id}[/cyan]")

    # --- 1. Verify Processed Tasks ---
    console.print("\n[bold]Verifying processed tasks...[/bold]")
    processed_project = tasks.find_project_by_name(api, "processed")
    processed_tasks_on_todoist = tasks.get_tasks_list(api, project_id=processed_project.id)
    parent_tasks_found = [t for t in processed_tasks_on_todoist if t.id in processed_ids]

    if len(parent_tasks_found) == len(processed_ids):
        console.print(f"[bold green]✓ Success:[/bold green] Found all {len(processed_ids)} processed parent tasks in the 'processed' project.")
        for task in parent_tasks_found:
            console.print(f"  - [cyan]Parent Task:[/cyan] {task.content}")
            subtasks = [st for st in processed_tasks_on_todoist if st.parent_id == task.id]
            if subtasks:
                for subtask in subtasks:
                    console.print(f"    - [yellow]Subtask:[/yellow] {subtask.content} | Labels: {subtask.labels}")
    else:
        console.print(f"[bold red]CRITICAL FAILURE:[/bold red] Expected {len(processed_ids)} processed tasks, but found {len(parent_tasks_found)}.")

    # --- 2. Verify Completed Tasks ---
    console.print("\n[bold]Verifying completed tasks...[/bold]")
    try:
        completed_task_id = completed_ids[0]
        # In the Todoist API, completed tasks are not directly queryable by default.
        # We will check if the task is still in the inbox; if not, we assume it was completed.
        inbox_project = tasks.find_project_by_name(api, "Inbox")
        inbox_tasks = tasks.get_tasks_list(api, project_id=inbox_project.id)
        task_still_in_inbox = any(t.id == completed_task_id for t in inbox_tasks)
        if not task_still_in_inbox:
             console.print(f"[bold green]✓ Success:[/bold green] Task with ID {completed_task_id} is no longer in the inbox, assumed completed.")
        else:
             console.print(f"[bold red]CRITICAL FAILURE:[/bold red] Task with ID {completed_task_id} was found in the inbox and was not completed.")

    except Exception as e:
        console.print(f"[bold red]An error occurred during completion verification:[/bold red] {e}")


    # --- 3. Verify Deleted Tasks ---
    console.print("\n[bold]Verifying deleted tasks...[/bold]")
    try:
        deleted_task_id = deleted_ids[0]
        api.get_task(deleted_task_id)
        console.print(f"[bold red]CRITICAL FAILURE:[/bold red] Deleted task with ID {deleted_task_id} still exists.")
    except Exception as e:
        # We expect an exception here, as the task should not be found.
        console.print(f"[bold green]✓ Success:[/bold green] Deleted task with ID {deleted_ids[0]} could not be found, as expected.")

    # --- 4. Verify Tasks Left in Inbox ---
    console.print("\n[bold]Verifying tasks left in inbox...[/bold]")
    inbox_project = tasks.find_project_by_name(api, "Inbox")
    inbox_tasks = tasks.get_tasks_list(api, project_id=inbox_project.id)
    tasks_found_in_inbox = [t for t in inbox_tasks if t.id in left_in_inbox_ids]

    if len(tasks_found_in_inbox) == len(left_in_inbox_ids):
        console.print(f"[bold green]✓ Success:[/bold green] Found all {len(left_in_inbox_ids)} unprocessed tasks in the 'Inbox' project, as expected.")
    else:
        console.print(f"[bold red]CRITICAL FAILURE:[/bold red] Expected {len(left_in_inbox_ids)} tasks to be left in the inbox, but found {len(tasks_found_in_inbox)}.")


    console.print("\n[bold]Verification complete. Please manually check the Todoist 'processed' project for correctness.[/bold]")


if __name__ == "__main__":
    test_run_id, processed_ids, completed_ids, deleted_ids, left_in_inbox_ids = run_automated_test()
    if test_run_id:
        api = tasks.get_api_client()
        verify_results(api, test_run_id, processed_ids, completed_ids, deleted_ids, left_in_inbox_ids)
