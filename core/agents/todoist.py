"""
TodoistAgent - GTD Personal Assistant

This agent manages a Todoist system following strict GTD methodology
and the user's specific workflow design.
"""

import os
import json
from pathlib import Path
from typing import Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task, Project
from core.agents.base import BaseAgent


class TodoistAgent(BaseAgent):
    """
    A specialized agent for managing Todoist tasks using GTD methodology.

    This agent understands the user's unique GTD system and learns preferences
    over time, storing them in markdown files.
    """

    def __init__(self, config: dict):
        """Initialize the TodoistAgent with API connection."""
        super().__init__(config)

        # Initialize Todoist API
        api_token = os.getenv("TODOIST_API_TOKEN")
        if not api_token:
            raise ValueError(
                "TODOIST_API_TOKEN not found in environment. "
                "Please set it in your .env file."
            )

        self.api = TodoistAPI(api_token)

        # Cache for projects (avoid repeated API calls)
        self._projects_cache: Optional[list[Project]] = None

        # Knowledge file paths
        self.knowledge_dir = Path("knowledge")
        self.system_file = self.knowledge_dir / "todoist_system.md"
        self.rules_file = self.knowledge_dir / "todoist_rules.md"
        self.context_file = self.knowledge_dir / "todoist_context.md"

    def _get_projects(self) -> list[Project]:
        """Get all projects, using cache if available."""
        if self._projects_cache is None:
            self._projects_cache = self.api.get_projects()
        return self._projects_cache

    def _find_project_by_name(self, project_name: str) -> Optional[Project]:
        """Find a project by name (case-insensitive)."""
        projects = self._get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                return project
        return None

    def _success(self, content: str, data: dict = None) -> str:
        """Helper to return structured success response."""
        response = {"status": "success", "message": content}
        if data:
            response["data"] = data
        return json.dumps(response, indent=2)

    def _error(self, error_type: str, message: str) -> str:
        """Helper to return structured error response."""
        return json.dumps({
            "status": "error",
            "error_type": error_type,
            "message": message
        }, indent=2)

    # =========================================================================
    # TOOL METHODS (Exposed to AI)
    # =========================================================================

    def create_task(
        self,
        content: str,
        project_name: str = "Inbox",
        labels: list[str] = None,
        priority: int = 1,
        due_string: str = None,
        description: str = None
    ) -> str:
        """
        Creates a new task in Todoist.

        Args:
            content: The task description/title
            project_name: Project name (e.g., "Processed", "Inbox", "Groceries")
            labels: List of context labels (e.g., ["home", "chore"])
            priority: Priority level 1-4 (1=lowest/none, 4=highest). Default 1.
            due_string: Natural language due date (e.g., "tomorrow", "next Monday")
            description: Additional notes/context for the task
        """
        try:
            # Find the project
            project = self._find_project_by_name(project_name)
            if not project:
                return self._error(
                    "ProjectNotFound",
                    f"Project '{project_name}' not found. Available projects: "
                    f"{', '.join(p.name for p in self._get_projects())}"
                )

            # Prepare task data
            task_data = {
                "content": content,
                "project_id": project.id,
                "priority": priority
            }

            # Add labels if provided (remove @ prefix if present)
            if labels:
                clean_labels = [label.lstrip('@') for label in labels]
                task_data["labels"] = clean_labels

            # Add due date if provided
            if due_string:
                task_data["due_string"] = due_string

            # Add description if provided
            if description:
                task_data["description"] = description

            # Create the task
            task = self.api.add_task(**task_data)

            # Format response
            labels_str = f" [{', '.join('@' + l for l in labels)}]" if labels else ""
            due_str = f" (due: {due_string})" if due_string else ""
            priority_str = f" [P{priority}]" if priority > 1 else ""

            return self._success(
                f"Created task in #{project_name}{labels_str}{due_str}{priority_str}",
                data={
                    "task_id": task.id,
                    "content": task.content,
                    "project": project_name,
                    "url": task.url
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to create task: {str(e)}")

    def list_tasks(
        self,
        project_name: str = None,
        label: str = None,
        filter_query: str = None
    ) -> str:
        """
        Lists tasks from Todoist.

        Args:
            project_name: Filter by project name (e.g., "Inbox", "Processed")
            label: Filter by label (e.g., "home", "urgent")
            filter_query: Advanced Todoist filter query (e.g., "today | overdue")
        """
        try:
            tasks = []

            if filter_query:
                # Use advanced filter
                tasks = self.api.get_tasks(filter=filter_query)
            elif project_name:
                # Filter by project
                project = self._find_project_by_name(project_name)
                if not project:
                    return self._error(
                        "ProjectNotFound",
                        f"Project '{project_name}' not found"
                    )
                tasks = self.api.get_tasks(project_id=project.id)
            elif label:
                # Filter by label (remove @ prefix if present)
                clean_label = label.lstrip('@')
                tasks = self.api.get_tasks(label=clean_label)
            else:
                # Get all tasks
                tasks = self.api.get_tasks()

            if not tasks:
                return self._success("No tasks found")

            # Format task list
            task_list = []
            for task in tasks:
                task_info = {
                    "id": task.id,
                    "content": task.content,
                    "project_id": task.project_id,
                    "labels": task.labels,
                    "priority": task.priority,
                    "due": task.due.string if task.due else None,
                    "url": task.url
                }
                task_list.append(task_info)

            # Create readable summary
            summary_lines = [f"Found {len(tasks)} task(s):\n"]
            for i, task in enumerate(tasks, 1):
                labels_str = f" [{', '.join('@' + l for l in task.labels)}]" if task.labels else ""
                due_str = f" (due: {task.due.string})" if task.due else ""
                priority_str = f" [P{task.priority}]" if task.priority > 1 else ""
                summary_lines.append(
                    f"{i}. {task.content}{labels_str}{due_str}{priority_str}"
                )

            return self._success(
                "\n".join(summary_lines),
                data={"tasks": task_list, "count": len(tasks)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list tasks: {str(e)}")

    def complete_task(self, task_id: str) -> str:
        """
        Marks a task as complete.

        Args:
            task_id: The ID of the task to complete
        """
        try:
            # Get task details first
            task = self.api.get_task(task_id)

            # Complete it
            self.api.close_task(task_id)

            return self._success(
                f"Completed task: {task.content}",
                data={"task_id": task_id, "content": task.content}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to complete task: {str(e)}")

    def update_task(
        self,
        task_id: str,
        content: str = None,
        labels: list[str] = None,
        priority: int = None,
        due_string: str = None,
        description: str = None
    ) -> str:
        """
        Updates an existing task.

        Args:
            task_id: The ID of the task to update
            content: New task description (optional)
            labels: New labels list (optional, replaces existing)
            priority: New priority 1-4 (optional)
            due_string: New due date (optional)
            description: New description (optional)
        """
        try:
            # Build update data
            update_data = {}

            if content is not None:
                update_data["content"] = content

            if labels is not None:
                clean_labels = [label.lstrip('@') for label in labels]
                update_data["labels"] = clean_labels

            if priority is not None:
                update_data["priority"] = priority

            if due_string is not None:
                update_data["due_string"] = due_string

            if description is not None:
                update_data["description"] = description

            if not update_data:
                return self._error("InvalidInput", "No updates provided")

            # Update the task
            task = self.api.update_task(task_id, **update_data)

            return self._success(
                f"Updated task: {task.content}",
                data={"task_id": task.id, "content": task.content}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to update task: {str(e)}")

    def get_task(self, task_id: str) -> str:
        """
        Gets details of a specific task.

        Args:
            task_id: The ID of the task to retrieve
        """
        try:
            task = self.api.get_task(task_id)

            task_info = {
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "project_id": task.project_id,
                "labels": task.labels,
                "priority": task.priority,
                "due": task.due.string if task.due else None,
                "url": task.url,
                "created_at": task.created_at
            }

            # Format readable output
            labels_str = f"\nLabels: {', '.join('@' + l for l in task.labels)}" if task.labels else ""
            due_str = f"\nDue: {task.due.string}" if task.due else ""
            priority_str = f"\nPriority: P{task.priority}" if task.priority > 1 else ""
            desc_str = f"\nDescription: {task.description}" if task.description else ""

            summary = f"{task.content}{labels_str}{due_str}{priority_str}{desc_str}"

            return self._success(summary, data=task_info)

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to get task: {str(e)}")

    def add_comment(self, task_id: str, comment: str) -> str:
        """
        Adds a comment to a task.

        Args:
            task_id: The ID of the task
            comment: The comment text to add
        """
        try:
            comment_obj = self.api.add_comment(
                task_id=task_id,
                content=comment
            )

            return self._success(
                f"Added comment to task",
                data={"comment_id": comment_obj.id, "content": comment}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to add comment: {str(e)}")

    def query_rules(self, search_term: str = None) -> str:
        """
        Reads learned rules from the knowledge files.

        Args:
            search_term: Optional search term to filter rules (case-insensitive)
        """
        try:
            content_parts = []

            # Read system file
            if self.system_file.exists():
                content_parts.append("=== SYSTEM DESIGN ===\n")
                content_parts.append(self.system_file.read_text())

            # Read rules file
            if self.rules_file.exists():
                content_parts.append("\n\n=== LEARNED RULES ===\n")
                content_parts.append(self.rules_file.read_text())

            # Read context file
            if self.context_file.exists():
                content_parts.append("\n\n=== CONTEXT ===\n")
                content_parts.append(self.context_file.read_text())

            full_content = "".join(content_parts)

            # Filter if search term provided
            if search_term:
                lines = full_content.split('\n')
                matching_lines = [
                    line for line in lines
                    if search_term.lower() in line.lower()
                ]
                if matching_lines:
                    filtered_content = "\n".join(matching_lines)
                    return self._success(
                        f"Found {len(matching_lines)} matching line(s)",
                        data={"content": filtered_content}
                    )
                else:
                    return self._success(f"No matches found for '{search_term}'")

            return self._success(
                "Knowledge files loaded",
                data={"content": full_content}
            )

        except Exception as e:
            return self._error("FileError", f"Failed to read rules: {str(e)}")
