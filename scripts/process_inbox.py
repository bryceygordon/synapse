# scripts/process_inbox.py

import json
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.todoist_engine import tasks
import yaml
from core.providers import get_provider
from core.main import display_turn_usage

# Initialize Rich console
console = Console()

def prompt_with_shortcuts(question: str, choices: dict, default: str) -> str:
    """Creates a prompt with single-letter shortcuts."""
    prompt_text = f"{question} ("
    prompt_text += "/".join([f"[bold underline]{k}[/bold underline]{v[1:]}" for k, v in choices.items()])
    prompt_text += f") "

    valid_shortcuts = list(choices.keys())

    while True:
        user_input = Prompt.ask(prompt_text, default=default).lower()
        if user_input in choices.values(): # User typed the full word
            return user_input
        if user_input in valid_shortcuts: # User typed the shortcut
            return choices[user_input]
        console.print(f"[red]Invalid input. Please enter one of {', '.join(valid_shortcuts)} or a full option name.[/red]")

def run_inbox_wizard():
    """
    An interactive CLI wizard to process tasks from the Todoist Inbox.
    """
    try:
        api = tasks.get_api_client()
        console.print("[bold green]Fetching tasks from your Inbox...[/bold green]")

        # Find the Inbox project
        inbox_project = tasks.find_or_create_project(api, "Inbox")
        processed_project = tasks.find_or_create_project(api, "processed")
        reminder_project = tasks.find_or_create_project(api, "reminder")

        # Get all tasks in the Inbox
        inbox_tasks = tasks.get_tasks_list(api, project_id=inbox_project.id)

        # Sort tasks by creation date (oldest first)
        inbox_tasks.sort(key=lambda x: x.created_at)

        if not inbox_tasks:
            console.print("[bold yellow]Your Inbox is empty. Nothing to process![/bold yellow]")
            return

        console.print(f"[bold cyan]Found {len(inbox_tasks)} tasks to process.[/bold cyan]")

        processed_data = []

        for i, task in enumerate(inbox_tasks):
            console.print(Panel(f"[bold]{task.content}[/bold]", title=f"Processing Task {i+1} of {len(inbox_tasks)}", border_style="blue"))

            # --- Interactive Processing Logic ---
            action_choices = {
                "h": "happy",
                "p": "process",
                "s": "skip",
                "c": "complete",
                "d": "delete",
                "e": "exit"
            }
            action = prompt_with_shortcuts("Choose an action", action_choices, "h")

            if action == "exit":
                if processed_data:
                    console.print("[yellow]Exiting inbox wizard. Any processed tasks will now be sent to the agent.[/yellow]")
                else:
                    console.print("[yellow]Exiting inbox wizard. No tasks to process.[/yellow]")
                break
            if action == "skip":
                console.print(f"Skipping task: {task.content}")
                continue

            if action == "happy":
                # Task is good as is, send to agent with default values
                task_data = {
                    "original_task_id": task.id,
                    "original_content": task.content,
                    "is_multistep": False,
                    "should_rename": False,
                    "user_input": ""
                }
                processed_data.append(task_data)
                console.print(f"[green]✓ Task '{task.content}' captured for processing.[/green]")
                console.print("-" * 30)
                continue

            if action == "complete":
                try:
                    tasks.complete_task(api, task.id)
                    console.print(f"[green]✓ Task '{task.content}' completed.[/green]")
                except Exception as e:
                    console.print(f"[red]Error completing task: {e}[/red]")
                continue

            if action == "delete":
                if Confirm.ask(f"Are you sure you want to delete '{task.content}'?", default=False):
                    try:
                        tasks.delete_task(api, task.id)
                        console.print(f"[green]✓ Task '{task.content}' deleted.[/green]")
                    except Exception as e:
                        console.print(f"[red]Error deleting task: {e}[/red]")
                else:
                    console.print("Deletion cancelled.")
                continue

            # Ask if simple or multistep
            task_type_choices = {"s": "simple", "m": "multistep"}
            task_type = prompt_with_shortcuts("Is this a simple or multi-step task?", task_type_choices, "s")
            is_multistep = (task_type == "multistep")

            # Ask to rename
            should_rename = Confirm.ask(f"Do you want to rename this task?", default=False)

            user_input = ""
            if should_rename:
                user_input = Prompt.ask("[cyan]Enter new task name (with tags, dates, etc.)[/cyan]")
            else:
                user_input = Prompt.ask(f"[cyan]Add details for '{task.content}' (tags, dates, etc.)[/cyan]")

            # Store the collected data
            task_data = {
                "original_task_id": task.id,
                "original_content": task.content,
                "is_multistep": is_multistep,
                "should_rename": should_rename,
                "user_input": user_input
            }
            processed_data.append(task_data)

            console.print(f"[green]✓ Task '{task.content}' captured for processing.[/green]")
            console.print("-" * 30)

        if processed_data:
            console.print("\n[bold green]Inbox processing complete. Handing off to the agent for refinement...[/bold green]")

            # --- Agent Integration ---
            try:
                # 1. Load the agent config from YAML
                config_path = "agents/todoist_inbox_processor.yaml"
                with open(config_path, "r") as f:
                    agent_config = yaml.safe_load(f)
                provider = get_provider(agent_config["provider"])
                client = provider.create_client()

                # 2. Format the data and send to the agent
                input_json = json.dumps(processed_data, indent=2)

                with console.status("[bold yellow]Agent is processing...[/bold yellow]", spinner="dots"):
                    response = provider.send_message(
                        client=client,
                        system_prompt=agent_config["system_prompt"],
                        user_prompt=input_json,
                        model=agent_config["model"],
                        tools=[],
                        discussion=[]
                    )
                display_turn_usage(response)

                # 3. Display the refined output
                console.print(Panel("[bold green]Agent has returned the refined tasks:[/bold green]", border_style="green"))

                # The agent's response should be a JSON string in the first text block
                refined_json_str = response.text

                # Clean the JSON string if it's wrapped in markdown
                if refined_json_str.strip().startswith("```json"):
                    refined_json_str = refined_json_str.strip()[7:-3].strip()

                # --- Final Review and Execution ---
                try:
                    refined_tasks = json.loads(refined_json_str)

                    while True:
                        console.print("\n[bold yellow]--- Proposed Changes ---[/bold yellow]")
                        for i, task_op in enumerate(refined_tasks):
                            op = task_op['action'].upper()
                            content = task_op['api_params'].get('content', '')
                            labels = task_op['api_params'].get('labels', [])
                            due = task_op['api_params'].get('due_string', 'No due date')
                            priority = task_op['api_params'].get('priority', 1)
                            console.print(f"{i+1}. [cyan]({op})[/cyan] '{content}' | Labels: {labels} | Due: {due} | Priority: P{priority}")

                        # Ask for confirmation
                        proceed_choices = {"a": "apply", "e": "edit", "c": "cancel"}
                        proceed = prompt_with_shortcuts("\nApply these changes?", proceed_choices, "a")

                        if proceed == "cancel":
                            console.print("[red]Operation cancelled.[/red]")
                            return

                        if proceed == "apply":
                            reminder_tasks = []
                            with console.status("[bold yellow]Applying changes...[/bold yellow]", spinner="dots"):
                                for task_op in refined_tasks:
                                    # --- Add @next tag ---
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

                                    # --- Move to destination project ---
                                    destination = task_op.get('destination_project', 'processed')
                                    if destination == 'reminder':
                                        target_project_id = reminder_project.id
                                        reminder_tasks.append(api_params.get('content', ''))
                                    else:
                                        target_project_id = processed_project.id
                                    tasks.move_task(api, task_id=original_id, project_id=target_project_id)
                                console.print("[bold green]✓ All tasks processed successfully![/bold green]")
                            if reminder_tasks:
                                reminder_list = "\n".join([f"- {task}" for task in reminder_tasks])
                                console.print(Panel(
                                    f"[bold]The following tasks were moved to your 'reminder' project:[/bold]\n\n{reminder_list}\n\n[italic yellow]Don't forget to set a notification for them in Todoist![/italic yellow]",
                                    title="[bold magenta]🔔 Reminder Set 🔔[/bold magenta]",
                                    border_style="magenta",
                                    expand=False
                                ))
                            break

                        if proceed == "edit":
                            task_num = IntPrompt.ask("Enter the number of the task to edit") - 1
                            if 0 <= task_num < len(refined_tasks):
                                field_choices = {
                                    "t": "content",
                                    "l": "labels",
                                    "p": "priority",
                                    "d": "due_string"
                                }
                                field_to_edit = prompt_with_shortcuts("Which field to edit?", field_choices, "t")
                                new_value = Prompt.ask(f"Enter the new value for '{field_to_edit}'")

                                if field_to_edit == "priority":
                                    refined_tasks[task_num]['api_params'][field_to_edit] = int(new_value)
                                elif field_to_edit == "labels":
                                    refined_tasks[task_num]['api_params'][field_to_edit] = [l.strip() for l in new_value.split(',')]
                                else:
                                    refined_tasks[task_num]['api_params'][field_to_edit] = new_value
                                console.print("[green]Task updated. Here is the new plan:[/green]")
                            else:
                                console.print("[red]Invalid task number.[/red]")

                except json.JSONDecodeError:
                    console.print(Panel("[bold red]Error: Agent returned invalid JSON. Cannot proceed.[/bold red]", border_style="red"))
                except Exception as final_error:
                    console.print(Panel(f"[bold red]An error occurred during final submission:[/bold red] {final_error}", title="Error", border_style="red"))

            except Exception as agent_error:
                console.print(Panel(f"[bold red]Agent processing failed:[/bold red] {agent_error}", title="Error", border_style="red"))

            except Exception as agent_error:
                console.print(Panel(f"[bold red]Agent processing failed:[/bold red] {agent_error}", title="Error", border_style="red"))



    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred:[/bold red] {e}", title="Error", border_style="red"))

if __name__ == "__main__":
    run_inbox_wizard()
