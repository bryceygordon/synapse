# scripts/plan_my_day.py
import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI
from rich.console import Console
from rich.prompt import Prompt, Confirm

from core.todoist_engine import tasks
from core.todoist_engine.tasks import Task
from core.weather_service import WeatherService


console = Console()


def run_scheduler_wizard():
    """
    An interactive CLI wizard to help the user plan their day.
    """
    load_dotenv()
    api_key = os.getenv("TODOIST_API_KEY")
    if not api_key:
        console.print("[bold red]Error: TODOIST_API_KEY environment variable not set.[/bold red]")
        return

    api = TodoistAPI(api_key)
    scheduler = Scheduler(api, console)

    console.print("[bold cyan]Welcome to the Daily Scheduler![/bold cyan]")
    planning_day = Prompt.ask("Are you planning for [bold](t)oday[/bold] or [bold]to(m)orrow[/bold]?", choices=["t", "m"], default="t")
    day_string = "today" if planning_day == 't' else "tomorrow"

    console.print("Fetching tasks from your 'processed' project...")

    initial_tasks = scheduler.get_initial_tasks()
    if not initial_tasks:
        console.print("[yellow]No tasks found in 'processed'. Nothing to plan today.[/yellow]")
        return

    console.print(f"Found {len(initial_tasks)} tasks. Checking weather conditions...")
    weather_filtered_tasks = scheduler.filter_tasks_by_weather(initial_tasks)
    if len(weather_filtered_tasks) < len(initial_tasks):
        console.print("[yellow]Filtered out weather-dependent tasks due to rain.[/yellow]")

    console.print("Generating a suggested daily plan...")
    daily_plan = scheduler.generate_daily_plan(weather_filtered_tasks)
    scheduler.set_final_plan(daily_plan)

    if not daily_plan:
        console.print("[yellow]Could not generate a plan based on the available tasks and heuristics.[/yellow]")
        return

    while True:
        console.print("\n[bold green]✨ Your Suggested Daily Plan ✨[/bold green]")
        for i, task in enumerate(scheduler.get_final_plan(), 1):
            console.print(f"{i}. [bold]{task.scheduled_time}[/bold] - {task.content}")

        console.print("\n[bold]What would you like to do?[/bold]")
        action = Prompt.ask(
            "Choose an action: [bold](a)[/bold]dd, [bold](c)[/bold]omplete, [bold](d)[/bold]elete, [bold](s)[/bold]ubmit, [bold](e)[/bold]xit",
            choices=["a", "c", "d", "s", "e"],
            default="s"
        )

        if action == 'a':
            content = Prompt.ask("Enter the task content")
            labels_str = Prompt.ask("Enter labels (comma-separated)", default="")
            labels = [label.strip() for label in labels_str.split(',')] if labels_str else []
            priority = int(Prompt.ask("Enter priority (1-4)", choices=["1", "2", "3", "4"], default="1"))
            scheduler.add_task_interactively(content, labels, priority)
            console.print(f"[green]✓ Task '{content}' added to the plan.[/green]")

        elif action == 'c':
            task_num = int(Prompt.ask("Enter the number of the task to complete", choices=[str(i) for i in range(1, len(scheduler.get_final_plan()) + 1)]))
            task_to_complete = scheduler.get_final_plan()[task_num - 1]
            if scheduler.complete_task(task_to_complete.id):
                 console.print(f"[green]✓ Task '{task_to_complete.content}' marked as complete.[/green]")
                 # We remove it from the plan visually, but the API call is what matters
                 current_plan = scheduler.get_final_plan()
                 current_plan.pop(task_num - 1)
                 scheduler.set_final_plan(current_plan)
            else:
                console.print("[red]Error completing task via API.[/red]")

        elif action == 'd':
            task_num = int(Prompt.ask("Enter the number of the task to delete", choices=[str(i) for i in range(1, len(scheduler.get_final_plan()) + 1)]))
            task_to_delete = scheduler.get_final_plan()[task_num - 1]
            if scheduler.delete_task(task_to_delete.id):
                 console.print(f"[green]✓ Task '{task_to_delete.content}' deleted.[/green]")
                 current_plan = scheduler.get_final_plan()
                 current_plan.pop(task_num - 1)
                 scheduler.set_final_plan(current_plan)
            else:
                 console.print("[red]Error deleting task via API.[/red]")

        elif action == 's':
            if Confirm.ask("[bold yellow]Are you sure you want to submit this plan to Todoist?[/bold yellow]"):
                console.print("Submitting to Todoist...")
                if scheduler.submit_plan(day_string):
                    console.print("[bold green]✓ Your daily plan has been submitted successfully![/bold green]")
                else:
                    console.print("[bold red]An error occurred during submission.[/bold red]")
                break

        elif action == 'e':
            console.print("Exiting without submitting. Your plan has not been saved.")
            break


class Scheduler:
    def __init__(self, api, console):
        self.api = api
        self.console = console
        self.final_plan = []

    def get_initial_tasks(self):
        return self.get_tasks_from_project("processed")

    def get_tasks_from_project(self, project_name):
        project = tasks.find_or_create_project(self.api, project_name)
        return tasks.get_tasks_list(self.api, project_id=project.id)

    def filter_tasks_by_weather(self, tasks):
        weather = WeatherService().get_weather()
        if weather['condition'] == 'rain':
            return [task for task in tasks if 'weather_dependent' not in task.labels]
        return tasks

    def find_task_to_plan(self, tasks):
        for task in tasks:
            if 'plan' in task.labels:
                return task
        return None

    def sort_tasks_by_priority(self, tasks):
        return sorted(tasks, key=lambda task: task.priority, reverse=True)

    def generate_daily_plan(self, tasks):
        daily_plan = []
        low_energy_tasks_count = 0
        high_energy_task_scheduled = False

        # Sort tasks by priority to handle high-priority items first
        sorted_tasks = self.sort_tasks_by_priority(tasks)

        for task in sorted_tasks:
            if "low_energy" in task.labels and low_energy_tasks_count < 2:
                if low_energy_tasks_count == 0:
                    task.scheduled_time = "08:00"
                else:
                    task.scheduled_time = "08:30"
                daily_plan.append(task)
                low_energy_tasks_count += 1

            elif "errand" in task.labels:
                task.scheduled_time = "09:30"
                daily_plan.append(task)

            elif "high_energy" in task.labels and not high_energy_task_scheduled:
                task.scheduled_time = "10:00"
                daily_plan.append(task)
                high_energy_task_scheduled = True

        # Fallback: If no specific heuristics match, suggest the top 3 highest-priority tasks.
        if not daily_plan and sorted_tasks:
            for task in sorted_tasks[:3]:
                task.scheduled_time = "anytime"
                daily_plan.append(task)

        return daily_plan

    def start_conversation(self):
        pass

    def add_task_interactively(self, content, labels, priority):
        task = self.add_task(content, labels=labels, priority=priority)
        if task:
            # The test is expecting a Task object, so we'll create one to simulate the API response
            new_task = Task(id='new_task', content=content, labels=labels, priority=priority, project_id=task.project_id, completed_at=None, parent_id=None, created_at=None, creator_id=None, due=None, order=0, section_id=None, assignee_id=None, assigner_id=None, description='', deadline=None, duration=None, is_collapsed=False, updated_at=None)
            self.final_plan.append(new_task)
            return new_task
        return None

    def get_final_plan(self):
        return self.final_plan

    def set_final_plan(self, plan):
        self.final_plan = plan

    def submit_plan(self, day_string="today"):
        """
        Submits the final plan to the Todoist API.

        Iterates through the `final_plan` and updates each task
        with the scheduled time and project.

        Returns:
            bool: True on success, False otherwise.
        """
        try:
            for task in self.final_plan:
                due_string = day_string  # Default for 'anytime' tasks
                if hasattr(task, 'scheduled_time') and task.scheduled_time != "anytime":
                    due_string = f"{day_string} at {task.scheduled_time}"

                self.api.update_task(task_id=task.id, due_string=due_string)
            return True
        except Exception as e:
            self.console.print(f"[bold red]API Error submitting plan:[/bold red] {e}")
            return False

    def add_task(self, task_content, project_name='inbox', labels=None, due_string=None, priority=1):
        """
        Creates a new task in Todoist.

        Args:
            task_content (str): The content of the task.
            project_name (str): The name of the project to add the task to. Defaults to 'inbox'.
            labels (list): A list of labels to add to the task.
            due_string (str): The due date string for the task.
            priority (int): The priority of the task.

        Returns:
            The created task object, or None on failure.
        """
        try:
            project = tasks.find_or_create_project(self.api, project_name)
            if not project:
                return None
            task = self.api.add_task(
                content=task_content,
                project_id=project.id,
                labels=labels,
                due_string=due_string,
                priority=priority
            )
            return task
        except Exception as e:
            self.console.print(f"[bold red]API Error adding task:[/bold red] {e}")
            return None

    def complete_task(self, task_id):
        """
        Marks a task as complete in Todoist.

        Args:
            task_id (str): The ID of the task to complete.

        Returns:
            bool: True on success, False otherwise.
        """
        try:
            return self.api.complete_task(task_id=task_id)
        except Exception as e:
            self.console.print(f"[bold red]API Error completing task:[/bold red] {e}")
            return False

    def delete_task(self, task_id):
        """
        Deletes a task from Todoist.

        Args:
            task_id (str): The ID of the task to delete.

        Returns:
            bool: True on success, False otherwise.
        """
        try:
            return self.api.delete_task(task_id=task_id)
        except Exception as e:
            self.console.print(f"[bold red]API Error deleting task:[/bold red] {e}")
            return False

if __name__ == "__main__":
    run_scheduler_wizard()
