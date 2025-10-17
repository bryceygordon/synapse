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
    is_simple: Optional[bool] = None  # True = simple task (gets @next), False = multi-step
    next_action: Optional[str] = None  # For multi-step tasks


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
        self.destination_project = "processed"  # Default destination
        self.created_subtasks: List[str] = []  # Track created next action subtasks

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

        # Ask for destination project at start
        dest_response = self._prompt(
            "Destination project",
            "processed",
            "Where should these tasks be moved after processing?"
        )
        if dest_response == "PAUSE":
            return self._generate_instructions()

        self.destination_project = dest_response if dest_response else "processed"
        print(f"\n→ Tasks will be moved to: {self.destination_project}\n")

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

            # 3. Simple or Multi-step task
            is_simple_suggestion = suggestion.get('is_simple', True)
            task_type_str = "s" if is_simple_suggestion else "m"
            response = self._prompt(
                "Task type: (s)imple or (m)ulti-step",
                task_type_str,
                f"AI suggests: {'simple' if is_simple_suggestion else 'multi-step'}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            if response:
                update.is_simple = response.lower() == 's'
            else:
                update.is_simple = is_simple_suggestion

            # 4. Next action (if multi-step)
            if not update.is_simple:  # Multi-step task
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

            # For simple tasks, automatically add 'next' to labels
            if update.is_simple:
                if labels_suggestion:
                    labels_suggestion = f"{labels_suggestion}, add next"
                else:
                    labels_suggestion = "add next"

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
        DESTINATION_PROJECT: processed

        task_id: 123456789
        - content: "New content"
        - description: "New description"
        - labels: "add home, add next, remove shed"
        - due_date: "tomorrow 8am"
        - energy: m
        - duration: l
        - is_simple: true
        - next_action: "Call to confirm"
        ```

        Returns:
            Formatted instruction string
        """
        if not self.updates:
            return "No updates to process."

        instructions = []
        instructions.append("WIZARD OUTPUT - Process these task updates:\n")
        instructions.append(f"DESTINATION_PROJECT: {self.destination_project}\n")

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
            if update.is_simple is not None:
                instructions.append(f"- is_simple: {str(update.is_simple).lower()}")
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


class SubtaskTagWizard:
    """
    Interactive wizard for approving/editing tags on newly created next action subtasks.

    Flow:
    1. AI provides tag suggestions for all created subtasks
    2. Wizard steps through each subtask showing parent context
    3. User can accept AI suggestions (ENTER) or provide overrides
    4. Wizard collects all tag updates in structured format
    5. On completion, outputs instructions for AI to execute
    """

    def __init__(self, subtask_suggestions: List[Dict]):
        """
        Initialize wizard with subtask tag suggestions.

        Args:
            subtask_suggestions: List of dicts with keys:
                - subtask_id: ID of the subtask
                - subtask_content: Content of the subtask
                - parent_content: Content of the parent task
                - parent_labels: Labels from parent task
                - suggested_labels: AI suggested labels (natural language)
                - suggested_energy: AI suggested energy (h/m/l)
                - suggested_duration: AI suggested duration (s/m/l)
        """
        self.suggestions = subtask_suggestions
        self.updates: List[Dict] = []

    def run(self) -> str:
        """
        Run the subtask tag wizard interactively.

        Returns:
            Structured instructions for AI to process
        """
        if not self.suggestions:
            return "No subtasks to tag."

        print("\n" + "="*60)
        print("  NEXT ACTION TAG APPROVAL")
        print("="*60)
        print(f"\nReviewing tags for {len(self.suggestions)} next action(s)")
        print("Press ENTER to accept AI suggestions, or type your changes")
        print("Type 'pause' at any prompt to save and exit\n")

        for i, suggestion in enumerate(self.suggestions):
            subtask_id = suggestion['subtask_id']
            subtask_content = suggestion['subtask_content']
            parent_content = suggestion['parent_content']
            parent_labels = suggestion.get('parent_labels', [])

            print(f"\n[{i+1}/{len(self.suggestions)}] " + "-"*50)
            print(f"Parent: {parent_content}")
            if parent_labels:
                print(f"Parent labels: {', '.join('@' + l for l in parent_labels)}")
            print(f"Next action: {subtask_content}")

            # Prompt for labels
            suggested_labels = suggestion['suggested_labels']
            response = self._prompt(
                "Labels (natural language: 'add home, add call')",
                suggested_labels,
                f"AI suggests: {suggested_labels}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            labels = response if response else suggested_labels

            # Prompt for energy
            suggested_energy = suggestion['suggested_energy']
            response = self._prompt(
                "Energy (h/m/l)",
                suggested_energy,
                f"AI suggests: {suggested_energy}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            energy = response.lower() if response else suggested_energy

            # Prompt for duration
            suggested_duration = suggestion['suggested_duration']
            response = self._prompt(
                "Duration (s/m/l)",
                suggested_duration,
                f"AI suggests: {suggested_duration}"
            )
            if response == "PAUSE":
                return self._generate_instructions()

            duration = response.lower() if response else suggested_duration

            # Store update
            self.updates.append({
                'subtask_id': subtask_id,
                'labels': labels,
                'energy': energy,
                'duration': duration
            })

        print(f"\n{'='*60}")
        print("  TAG APPROVAL COMPLETE")
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
        Generate structured instructions for AI to process subtask tags.

        Format:
        ```
        SUBTASK_TAG_UPDATES

        subtask_id: 123456789
        - labels: "add call, add home"
        - energy: l
        - duration: s
        ```

        Returns:
            Formatted instruction string
        """
        if not self.updates:
            return "No updates to process."

        instructions = []
        instructions.append("SUBTASK_TAG_UPDATES - Apply these tag updates:\n")

        for update in self.updates:
            instructions.append(f"subtask_id: {update['subtask_id']}")
            instructions.append(f"- labels: \"{update['labels']}\"")
            instructions.append(f"- energy: {update['energy']}")
            instructions.append(f"- duration: {update['duration']}")
            instructions.append("")  # Blank line between subtasks

        instructions.append(f"\nTotal: {len(self.updates)} subtask(s) to update")

        return "\n".join(instructions)


def run_subtask_tag_wizard(subtask_suggestions: List[Dict]) -> str:
    """
    Convenience function to run the subtask tag wizard.

    Args:
        subtask_suggestions: AI's tag suggestions for all created subtasks

    Returns:
        Structured instructions for AI to process
    """
    wizard = SubtaskTagWizard(subtask_suggestions)
    return wizard.run()
