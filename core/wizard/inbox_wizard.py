"""
Interactive wizard for processing Todoist inbox tasks.

This wizard provides a streamlined CLI interface for processing inbox tasks
with AI assistance. The wizard can be paused at any time to consult the AI,
at which point all changes are automatically pushed to Todoist.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class WizardTaskUpdate:
    """Represents updates to be made to a single task."""
    task_id: str
    content: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None  # Natural language: "add next, remove shed"
    due_date: Optional[str] = None  # Natural language: "tomorrow 8am", "every day 8am"
    energy: Optional[str] = None  # h/m/l
    duration: Optional[str] = None  # s/m/l
    is_multistep: Optional[bool] = None
    next_action: Optional[str] = None


class InboxWizard:
    """
    Interactive wizard for processing inbox tasks.

    Flow:
    1. AI provides batch suggestions for all inbox tasks
    2. Wizard steps through each task with simple prompts
    3. User can accept AI suggestions (ENTER) or provide overrides
    4. Wizard collects all updates in structured format
    5. On completion/pause, outputs instructions for AI to execute
    """

    def __init__(self, tasks: List[Dict], ai_suggestions: Dict[str, Dict]):
        """
        Initialize wizard with tasks and AI suggestions.

        Args:
            tasks: List of task dicts with id, content, description
            ai_suggestions: Dict mapping task_id to suggested updates
        """
        self.tasks = tasks
        self.ai_suggestions = ai_suggestions
        self.updates: List[WizardTaskUpdate] = []
        self.current_index = 0

    def run(self) -> str:
        """
        Run the wizard interactively.

        Returns:
            Structured instructions for AI to process
        """
        print("\n" + "="*60)
        print("  INBOX PROCESSING WIZARD")
        print("="*60)
        print(f"\nProcessing {len(self.tasks)} task(s)")
        print("Press ENTER to accept AI suggestions, or type your changes")
        print("Type 'pause' at any prompt to save and exit\n")

        for i, task in enumerate(self.tasks):
            self.current_index = i
            task_id = task['id']

            print(f"\n[{i+1}/{len(self.tasks)}] " + "-"*50)
            print(f"Task: {task['content']}")
            if task.get('description'):
                print(f"Description: {task['description']}")

            # Get AI suggestion for this task
            suggestion = self.ai_suggestions.get(task_id, {})

            # Initialize update object
            update = WizardTaskUpdate(task_id=task_id)

            # 1. Content formatting (if AI suggests reformatting)
            if suggestion.get('content') and suggestion['content'] != task['content']:
                response = self._prompt(
                    "Content",
                    suggestion['content'],
                    f"AI suggests reformatting to: {suggestion['content']}"
                )
                if response == "PAUSE":
                    return self._generate_instructions()
                if response:
                    update.content = response
                else:
                    update.content = suggestion['content']

            # 2. Description (if AI suggests one)
            if suggestion.get('description'):
                response = self._prompt(
                    "Description",
                    suggestion['description'],
                    f"AI suggests: {suggestion['description']}"
                )
                if response == "PAUSE":
                    return self._generate_instructions()
                if response:
                    update.description = response
                else:
                    update.description = suggestion['description']

            # 3. Simple vs Multi-step
            is_multistep_suggestion = suggestion.get('is_multistep', False)
            is_multistep_str = "yes" if is_multistep_suggestion else "no"
            response = self._prompt(
                "Multi-step task? (y/n)",
                is_multistep_str,
                f"AI suggests: {is_multistep_str}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.is_multistep = response.lower().startswith('y')
            else:
                update.is_multistep = is_multistep_suggestion

            # 4. Next action (if multi-step)
            if update.is_multistep:
                response = self._prompt(
                    "What's the next action?",
                    suggestion.get('next_action', ''),
                    f"AI suggests: {suggestion.get('next_action', '')}" if suggestion.get('next_action') else None
                )
                if response == "PAUSE":
                    return self._generate_instructions()

                if response:
                    update.next_action = response
                else:
                    update.next_action = suggestion.get('next_action', '')

            # 5. Energy level (h/m/l)
            energy_suggestion = suggestion.get('energy', 'm')
            response = self._prompt(
                "Energy (h/m/l)",
                energy_suggestion,
                f"AI suggests: {energy_suggestion}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.energy = response.lower()
            else:
                update.energy = energy_suggestion

            # 6. Duration (s/m/l)
            duration_suggestion = suggestion.get('duration', 'm')
            response = self._prompt(
                "Duration (s/m/l)",
                duration_suggestion,
                f"AI suggests: {duration_suggestion}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.duration = response.lower()
            else:
                update.duration = duration_suggestion

            # 7. Labels/contexts (natural language)
            labels_suggestion = suggestion.get('labels', '')
            response = self._prompt(
                "Labels (natural language: 'add home, remove shed')",
                labels_suggestion,
                f"AI suggests: {labels_suggestion}" if labels_suggestion else None
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.labels = response
            else:
                update.labels = labels_suggestion

            # 8. Due date/recurrence (natural language)
            due_suggestion = suggestion.get('due_date', '')
            response = self._prompt(
                "Due date/recurrence (natural language: 'tomorrow 8am', 'every day')",
                due_suggestion,
                f"AI suggests: {due_suggestion}" if due_suggestion else None
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.due_date = response
            else:
                update.due_date = due_suggestion

            # Store update
            self.updates.append(update)

        print(f"\n{'='*60}")
        print("  WIZARD COMPLETE")
        print(f"{'='*60}\n")

        return self._generate_instructions()

    def _prompt(self, field_name: str, default: str, hint: Optional[str] = None) -> str:
        """
        Prompt user for input with default value.

        Args:
            field_name: Name of field being prompted
            default: Default value (shown in brackets)
            hint: Optional hint to display

        Returns:
            User input, empty string for default, or "PAUSE" to pause
        """
        if hint:
            print(f"  {hint}")

        prompt_str = f"  {field_name}"
        if default:
            prompt_str += f" [{default}]"
        prompt_str += ": "

        user_input = input(prompt_str).strip()

        if user_input.lower() == 'pause':
            return "PAUSE"

        return user_input  # Empty string means accept default

    def _generate_instructions(self) -> str:
        """
        Generate structured instructions for AI to process.

        Format:
        ```
        task_id: 123456789
        - content: "New content"
        - description: "New description"
        - labels: "add home, add next, remove shed"
        - due_date: "tomorrow 8am"
        - energy: m
        - duration: l
        - is_multistep: true
        - next_action: "Call to confirm"
        ```

        Returns:
            Formatted instruction string
        """
        if not self.updates:
            return "No updates to process."

        instructions = []
        instructions.append("WIZARD OUTPUT - Process these task updates:\n")

        for update in self.updates:
            instructions.append(f"task_id: {update.task_id}")

            if update.content:
                instructions.append(f"- content: \"{update.content}\"")
            if update.description:
                instructions.append(f"- description: \"{update.description}\"")
            if update.labels:
                instructions.append(f"- labels: \"{update.labels}\"")
            if update.due_date:
                instructions.append(f"- due_date: \"{update.due_date}\"")
            if update.energy:
                instructions.append(f"- energy: {update.energy}")
            if update.duration:
                instructions.append(f"- duration: {update.duration}")
            if update.is_multistep is not None:
                instructions.append(f"- is_multistep: {str(update.is_multistep).lower()}")
            if update.next_action:
                instructions.append(f"- next_action: \"{update.next_action}\"")

            instructions.append("")  # Blank line between tasks

        instructions.append(f"\nTotal: {len(self.updates)} task(s) to process")

        return "\n".join(instructions)


def run_inbox_wizard(tasks: List[Dict], ai_suggestions: Dict[str, Dict]) -> str:
    """
    Convenience function to run the inbox wizard.

    Args:
        tasks: List of inbox tasks
        ai_suggestions: AI's batch suggestions for all tasks

    Returns:
        Structured instructions for AI to process
    """
    wizard = InboxWizard(tasks, ai_suggestions)
    return wizard.run()
