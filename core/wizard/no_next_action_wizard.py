"""
Interactive wizard for processing tasks that have no next action.
"""

from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

class RichNoNextActionWizard:
    """
    A rich, interactive wizard for fixing tasks without a next action.
    """

    def __init__(self, tasks: List[Dict]):
        self.tasks = tasks
        self.actions = []

    def run(self) -> List[Dict]:
        console.print(Panel("[bold cyan]No Next Action Wizard[/bold cyan]", expand=False, border_style="cyan"))
        console.print(f"Processing {len(self.tasks)} task(s).")

        for i, task in enumerate(self.tasks):
            console.print(Panel(f"[bold]{task['content']}[/bold]", title=f"Task {i+1}/{len(self.tasks)}", border_style="green"))

            # Here we would add the logic to check for existing subtasks
            # and prompt the user to choose one or create a new next action.
            # For now, we will implement a simplified version.

            instruction = Prompt.ask("Enter processing instructions (e.g., 'add next action: Review document @computer')")
            self.actions.append({
                "task_id": task['id'],
                "action": "add_next_action",
                "instruction": instruction,
            })

        console.print(Panel("[bold cyan]Wizard Complete[/bold cyan]", expand=False, border_style="cyan"))
        return self.actions

def run_no_next_action_wizard(tasks: List[Dict]) -> List[Dict]:
    """
    Convenience function to run the new rich no-next-action wizard.
    """
    wizard = RichNoNextActionWizard(tasks)
    return wizard.run()