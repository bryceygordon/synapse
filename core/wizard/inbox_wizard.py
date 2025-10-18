"""
Interactive wizard for processing Todoist inbox tasks using a user-first,
shorthand-based workflow.
"""

from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

class RichInboxWizard:
    """
    A rich, interactive wizard for processing inbox tasks.

    This wizard follows a user-first data entry model. The user provides
    quick shorthand instructions, which are then batched and sent to the AI
    for interpretation and execution.
    """

    def __init__(self, tasks: List[Dict]):
        self.tasks = tasks
        self.actions = []
        self.current_index = 0

    def run(self) -> List[Dict]:
        """
        Run the wizard interactively.

        Returns:
            A list of action dictionaries for the AI to process.
        """
        console.print(Panel("[bold cyan]Inbox Processing Wizard[/bold cyan]", expand=False, border_style="cyan"))
        console.print(f"Processing {len(self.tasks)} task(s).")

        for i, task in enumerate(self.tasks):
            self.current_index = i
            task_id = task['id']
            content = task['content']

            console.print(Panel(f"[bold]{content}[/bold]", title=f"Task {i+1}/{len(self.tasks)}", border_style="green"))

            action = Prompt.ask(
                Text("Action: (p)rocess, (r)ename, (c)omplete, (d)elete, (s)kip, (q)uit", style="bold blue"),
                choices=["p", "r", "c", "d", "s", "q"],
                default="p",
            )

            if action == 's':
                console.print("[yellow]Skipped.[/yellow]")
                continue
            elif action == 'q':
                console.print("[bold red]Quitting wizard.[/bold red]")
                break
            elif action == 'c':
                self.actions.append({"task_id": task_id, "action": "complete"})
                console.print("[green]✓ Marked for completion.[/green]")
                continue
            elif action == 'd':
                self.actions.append({"task_id": task_id, "action": "delete"})
                console.print("[green]✓ Marked for deletion.[/green]")
                continue
            elif action == 'r':
                new_content = Prompt.ask("Enter new task content")
                self.actions.append({"task_id": task_id, "action": "rename", "new_content": new_content})
                console.print(f"[green]✓ Will be renamed to: '{new_content}'[/green]")
                # After renaming, we should still process it
                self._process_task(task_id)

            elif action == 'p':
                self._process_task(task_id)

        console.print(Panel("[bold cyan]Wizard Complete[/bold cyan]", expand=False, border_style="cyan"))
        return self.actions

    def _process_task(self, task_id: str):
        """Handles the logic for processing a single task (simple or multi-step)."""
        is_simple = Confirm.ask("Is this a simple (single-step) task?", default=True)

        if is_simple:
            instruction = Prompt.ask("Enter processing instructions (e.g., 'high long computer p3 due tomorrow 10am')")
            self.actions.append({
                "task_id": task_id,
                "action": "process_simple",
                "instruction": instruction,
            })
        else:
            # Multi-step
            next_actions = []
            while True:
                next_action_instruction = Prompt.ask("Enter next action instructions (e.g., 'go to shed @yard @chore')")
                next_actions.append(next_action_instruction)
                if not Confirm.ask("Add another step?", default=False):
                    break
            self.actions.append({
                "task_id": task_id,
                "action": "process_multistep",
                "next_actions": next_actions,
            })

def run_inbox_wizard(tasks: List[Dict]) -> List[Dict]:
    """
    Convenience function to run the new rich inbox wizard.
    """
    wizard = RichInboxWizard(tasks)
    return wizard.run()