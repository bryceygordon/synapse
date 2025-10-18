"""
Interactive wizard for reviewing tasks without next actions.

This wizard provides Phase 1 of a two-phase workflow for fixing tasks
in the processed project that lack next actions.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class TaskAction:
    """Action to take on a task."""
    task_id: str
    action: str  # "add_next", "complete", "delete", "skip"
    next_action_text: str = None  # For "add_next" action


class NoNextActionWizard:
    """
    Interactive wizard for reviewing tasks without next actions.

    Phase 1 workflow:
    1. Present each task one at a time
    2. User chooses: add next action, complete, delete, skip, pause, quit
    3. For "add next action": Just type the text, move to next task
    4. Wizard collects all actions
    5. Returns structured instructions for batch execution

    Phase 2 happens in the caller using SubtaskTagWizard (reused from inbox wizard).
    """

    def __init__(self, tasks: List[Dict]):
        """
        Initialize wizard with tasks.

        Args:
            tasks: List of task dicts from find_tasks_without_next_actions()
                   Each has: id, content, labels, has_subtasks, subtask_count
        """
        self.tasks = tasks
        self.actions: List[TaskAction] = []
        self.current_index = 0

    def run(self) -> str:
        """
        Run the wizard interactively.

        Returns:
            Structured instructions for AI to execute, or special strings:
            - "CANCELLED" if user quits
            - "NO_ACTIONS" if no actions taken
        """
        print("\n" + "="*60)
        print("  REVIEW TASKS WITHOUT NEXT ACTIONS - PHASE 1")
        print("="*60)
        print(f"\nReviewing {len(self.tasks)} task(s)")
        print("Quick review: declare actions, then AI will suggest tags\n")

        for i, task in enumerate(self.tasks):
            self.current_index = i
            task_id = task['id']

            print(f"\n[{i+1}/{len(self.tasks)}] " + "-"*50)
            print(f"Task: {task['content']}")
            if task.get('labels'):
                labels_str = ', '.join('@' + l for l in task['labels'])
                print(f"Labels: {labels_str}")
            if task.get('has_subtasks'):
                print(f"Subtasks: {task['subtask_count']} (none have @next)")

            # Prompt for action
            print(f"\n  (a)dd next action | (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: ", end="")
            action = input().strip().lower()

            if action == 'a':
                # Prompt for next action text
                print(f"  What's the next action? ", end="")
                next_action_text = input().strip()
                if next_action_text:
                    print(f"  ✓ Will add next action: {next_action_text}")
                    self.actions.append(TaskAction(
                        task_id=task_id,
                        action="add_next",
                        next_action_text=next_action_text
                    ))
                else:
                    print("  ⊘ Skipped (no action text provided)")
            elif action == 'c':
                print("  ✓ Marked for completion")
                self.actions.append(TaskAction(task_id=task_id, action="complete"))
            elif action == 'd':
                print("  ✓ Marked for deletion")
                self.actions.append(TaskAction(task_id=task_id, action="delete"))
            elif action == 's':
                print("  ⊘ Skipped")
            elif action == 'p' or action == 'pause':
                print("\n⏸️  Pausing wizard...")
                return self._generate_instructions()
            elif action == 'q' or action == 'quit':
                print("\n❌ Wizard cancelled.")
                return "CANCELLED"
            else:
                print("  ⊘ Invalid option, skipping")

        print(f"\n{'='*60}")
        print("  PHASE 1 COMPLETE")
        print(f"{'='*60}\n")

        return self._generate_instructions()

    def _generate_instructions(self) -> str:
        """
        Generate structured instructions for AI to execute.

        Format:
        ```
        NO_NEXT_ACTION_REVIEW_OUTPUT

        TASKS_TO_ADD_NEXT_ACTION:
        task_id: 123
        - next_action: "Research options"

        task_id: 456
        - next_action: "Call to confirm"

        TASKS_TO_COMPLETE: ['789', '012']
        TASKS_TO_DELETE: ['345']
        ```

        Returns:
            Formatted instruction string, or "NO_ACTIONS" if nothing to do
        """
        if not self.actions:
            return "NO_ACTIONS"

        instructions = []
        instructions.append("NO_NEXT_ACTION_REVIEW_OUTPUT\n")

        # Group by action type
        add_next = [a for a in self.actions if a.action == "add_next"]
        complete = [a.task_id for a in self.actions if a.action == "complete"]
        delete = [a.task_id for a in self.actions if a.action == "delete"]

        # Add next actions section
        if add_next:
            instructions.append("TASKS_TO_ADD_NEXT_ACTION:")
            for action in add_next:
                instructions.append(f"task_id: {action.task_id}")
                instructions.append(f"- next_action: \"{action.next_action_text}\"")
                instructions.append("")

        # Complete section
        if complete:
            instructions.append(f"TASKS_TO_COMPLETE: {complete}\n")

        # Delete section
        if delete:
            instructions.append(f"TASKS_TO_DELETE: {delete}\n")

        instructions.append(f"Total actions: {len(self.actions)}")

        return "\n".join(instructions)


def run_no_next_action_wizard(tasks: List[Dict]) -> str:
    """
    Convenience function to run the no-next-action wizard.

    Args:
        tasks: List of tasks without next actions

    Returns:
        Structured instructions for AI to process, or special strings:
        - "CANCELLED" if user quits
        - "NO_ACTIONS" if no actions taken
    """
    wizard = NoNextActionWizard(tasks)
    return wizard.run()
