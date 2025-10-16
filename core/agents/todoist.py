"""
TodoistAgent - GTD Personal Assistant

This agent manages a Todoist system following strict GTD methodology
and the user's specific workflow design.
"""

import os
import json
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task, Project, Section, Label, Comment
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

        # Cache for projects, sections, and labels (avoid repeated API calls)
        self._projects_cache: Optional[list[Project]] = None
        self._sections_cache: Optional[list[Section]] = None
        self._labels_cache: Optional[list[Label]] = None

        # User timezone (default to system timezone)
        self.timezone = ZoneInfo(os.getenv("TIMEZONE", "UTC"))

        # Knowledge file paths - use JIT knowledge directory structure
        # JIT knowledge uses BaseAgent.knowledge_dir = "knowledge/todoistagent"
        self.system_file = self.knowledge_dir / "todoist_system.md"
        self.rules_file = self.knowledge_dir / "learned_rules.md"
        self.context_file = self.knowledge_dir / "todoist_context.md"

    def _get_projects(self) -> list[Project]:
        """Get all projects, using cache if available."""
        if self._projects_cache is None:
            # get_projects() returns a ResultsPaginator
            # First iteration yields the complete list of projects
            projects_paginator = self.api.get_projects()
            self._projects_cache = next(iter(projects_paginator))
        return self._projects_cache

    def _find_project_by_name(self, project_name: str) -> Optional[Project]:
        """Find a project by name (case-insensitive)."""
        projects = self._get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                return project
        return None

    def _get_sections(self, project_id: str = None) -> list[Section]:
        """Get all sections, optionally filtered by project, using cache if available."""
        if self._sections_cache is None:
            sections_paginator = self.api.get_sections()
            self._sections_cache = next(iter(sections_paginator))

        if project_id:
            return [s for s in self._sections_cache if s.project_id == project_id]
        return self._sections_cache

    def _find_section_by_name(self, section_name: str, project_id: str = None) -> Optional[Section]:
        """Find a section by name (case-insensitive), optionally within a specific project."""
        sections = self._get_sections(project_id=project_id)
        for section in sections:
            if section.name.lower() == section_name.lower():
                return section
        return None

    def _get_labels(self) -> list[Label]:
        """Get all labels, using cache if available."""
        if self._labels_cache is None:
            labels_paginator = self.api.get_labels()
            self._labels_cache = next(iter(labels_paginator))
        return self._labels_cache

    def _get_tasks_list(self, **kwargs) -> list[Task]:
        """
        Get ALL tasks as a list (handles pagination).

        The Todoist API returns paginated results (typically 50 items per page).
        This method iterates through ALL pages to return the complete task list.
        """
        tasks_paginator = self.api.get_tasks(**kwargs)
        all_tasks = []

        # Iterate through ALL pages of results
        for page in tasks_paginator:
            all_tasks.extend(page)

        return all_tasks

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

    def get_current_time(self) -> str:
        """
        Get the current date and time in the user's timezone.

        Returns current datetime information including:
        - Full datetime with timezone
        - Current date in YYYY-MM-DD format (for Todoist due_date)
        - Day of week
        - Time in 24-hour and 12-hour formats

        This is essential for determining due dates and understanding temporal context.
        """
        try:
            now = datetime.now(self.timezone)

            info = {
                "datetime": now.strftime("%A, %B %d, %Y at %I:%M %p %Z"),
                "date": now.strftime("%Y-%m-%d"),
                "day_of_week": now.strftime("%A"),
                "time_24h": now.strftime("%H:%M"),
                "time_12h": now.strftime("%I:%M %p"),
                "timezone": str(self.timezone),
                "iso8601": now.isoformat()
            }

            summary = (
                f"Current time: {info['datetime']}\n"
                f"Date (for Todoist): {info['date']}\n"
                f"Day: {info['day_of_week']}\n"
                f"Time: {info['time_12h']} ({info['time_24h']})"
            )

            return self._success(summary, data=info)

        except Exception as e:
            return self._error("TimeError", f"Failed to get current time: {str(e)}")

    def create_task(
        self,
        content: str,
        project_name: str = "Inbox",
        labels: list[str] = None,
        priority: int = 1,
        due_string: str = None,
        description: str = None,
        section_name: str = None,
        parent_id: str = None,
        duration: int = None,
        duration_unit: str = "minute"
    ) -> str:
        """
        Create task.

        Args:
            content: Task title
            project_name: Project (ignored if parent_id provided)
            labels: Labels (no @)
            priority: 1-4
            due_string: YYYY-MM-DD
            description: Notes
            section_name: Section
            parent_id: Parent ID (for subtasks - inherits parent's project)
            duration: Amount
            duration_unit: Unit
        """
        try:
            # Prepare task data
            task_data = {
                "content": content,
                "priority": priority
            }

            # Handle subtasks vs regular tasks
            if parent_id:
                # Subtask - inherits parent's project, don't set project_id
                task_data["parent_id"] = parent_id
            else:
                # Regular task - find and set project
                project = self._find_project_by_name(project_name)
                if not project:
                    return self._error(
                        "ProjectNotFound",
                        f"Project '{project_name}' not found. Available projects: "
                        f"{', '.join(p.name for p in self._get_projects())}"
                    )
                task_data["project_id"] = project.id

            # Add section if provided (only for regular tasks, not subtasks)
            if section_name and not parent_id:
                section = self._find_section_by_name(section_name, project_id=task_data["project_id"])
                if not section:
                    return self._error(
                        "SectionNotFound",
                        f"Section '{section_name}' not found in project '{project_name}'"
                    )
                task_data["section_id"] = section.id

            # Add parent_id for subtasks
            if parent_id:
                task_data["parent_id"] = parent_id

            # Add labels if provided (remove @ prefix if present)
            if labels:
                # Handle case where labels is accidentally passed as a string instead of list
                if isinstance(labels, str):
                    # Check if it's a comma-separated string
                    if ',' in labels:
                        labels = [label.strip().lstrip('@') for label in labels.split(',')]
                    else:
                        labels = [labels]
                clean_labels = [label.lstrip('@').strip() for label in labels]
                task_data["labels"] = clean_labels

            # Add due date if provided
            if due_string:
                task_data["due_string"] = due_string

            # Add description if provided
            if description:
                task_data["description"] = description

            # Add duration if provided
            if duration is not None:
                task_data["duration"] = duration
                task_data["duration_unit"] = duration_unit

            # Create the task
            task = self.api.add_task(**task_data)

            # Format response
            labels_str = f" [{', '.join('@' + l for l in labels)}]" if labels else ""
            due_str = f" (due: {due_string})" if due_string else ""
            priority_str = f" [P{priority}]" if priority > 1 else ""

            if parent_id:
                location = "as subtask"
            else:
                location = f"in #{project_name}"

            return self._success(
                f"Created task {location}{labels_str}{due_str}{priority_str}",
                data={
                    "task_id": task.id,
                    "content": task.content,
                    "project": project_name if not parent_id else None,
                    "parent_id": parent_id,
                    "url": task.url
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to create task: {str(e)}")

    def list_tasks(
        self,
        project_name: str = None,
        label: str = None,
        filter_query: str = None,
        sort_by: str = None
    ) -> str:
        """
        List tasks.

        Args:
            project_name: Project filter
            label: Label filter
            filter_query: Search term
            sort_by: Sort order
        """
        try:
            tasks = []

            if project_name:
                # Filter by project
                project = self._find_project_by_name(project_name)
                if not project:
                    return self._error(
                        "ProjectNotFound",
                        f"Project '{project_name}' not found"
                    )
                tasks = self._get_tasks_list(project_id=project.id)
            elif label:
                # Filter by label (remove @ prefix if present)
                clean_label = label.lstrip('@')
                tasks = self._get_tasks_list(label=clean_label)
            else:
                # Get all tasks
                tasks = self._get_tasks_list()

            # Apply local filtering if filter_query is provided
            if filter_query and tasks:
                tasks = [
                    task for task in tasks
                    if (filter_query.lower() in task.content.lower() or
                        any(filter_query.lower() in label.lower() for label in task.labels))
                ]

            if not tasks:
                return self._success("No tasks found")

            # Sort tasks if requested
            if sort_by:
                if sort_by == "created_asc":
                    tasks = sorted(tasks, key=lambda t: t.created_at if t.created_at else "")
                elif sort_by == "created_desc":
                    tasks = sorted(tasks, key=lambda t: t.created_at if t.created_at else "", reverse=True)
                elif sort_by == "priority_asc":
                    tasks = sorted(tasks, key=lambda t: t.priority)
                elif sort_by == "priority_desc":
                    tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

            # Create readable summary with only essential info
            summary_lines = [f"Found {len(tasks)} task(s):\n"]
            task_summaries = []
            for i, task in enumerate(tasks, 1):
                labels_str = f" [{', '.join('@' + l for l in task.labels)}]" if task.labels else ""
                due_str = f" (due: {task.due.string})" if task.due else ""
                priority_str = f" [P{task.priority}]" if task.priority > 1 else ""
                task_line = f"{i}. {task.content}{labels_str}{due_str}{priority_str}"
                summary_lines.append(task_line)

                # Include full task details in data payload for AI processing
                task_summaries.append({
                    "id": task.id,
                    "content": task.content,
                    "labels": task.labels,  # CRITICAL: Include labels array for AI to detect malformed tags
                    "priority": task.priority,
                    "due": task.due.string if task.due else None,
                    "project_id": task.project_id,
                    "created_at": str(task.created_at) if task.created_at else None
                })

            return self._success(
                "\n".join(summary_lines),
                data={"tasks": task_summaries, "task_ids": [t.id for t in tasks], "count": len(tasks)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list tasks: {str(e)}")

    def complete_task(self, task_id: str) -> str:
        """
        Complete task.

        Args:
            task_id: Task ID
        """
        try:
            # Complete the task directly (no need to fetch details first)
            self.api.complete_task(task_id)

            return self._success(
                "✓ Task completed",
                data={"task_id": task_id}
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
        description: str = None,
        duration: int = None,
        duration_unit: str = "minute"
    ) -> str:
        """
        Update task.

        Args:
            task_id: Task ID
            content: New title
            labels: New labels (no @)
            priority: 1-4
            due_string: New date
            description: New notes
            duration: Amount
            duration_unit: Unit
        """
        try:
            # Build update data
            update_data = {}

            if content is not None:
                update_data["content"] = content

            if labels is not None:
                # Handle case where labels is accidentally passed as a string instead of list
                if isinstance(labels, str):
                    # Check if it's a comma-separated string
                    if ',' in labels:
                        labels = [label.strip().lstrip('@') for label in labels.split(',')]
                    else:
                        labels = [labels]
                clean_labels = [label.lstrip('@').strip() for label in labels]
                update_data["labels"] = clean_labels

            if priority is not None:
                update_data["priority"] = priority

            if due_string is not None:
                update_data["due_string"] = due_string

            if description is not None:
                update_data["description"] = description

            if duration is not None:
                update_data["duration"] = duration
                update_data["duration_unit"] = duration_unit

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
        Get task details.

        Args:
            task_id: Task ID
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
                "created_at": str(task.created_at) if task.created_at else None
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
        Add comment.

        Args:
            task_id: Task ID
            comment: Comment text
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

    def delete_task(self, task_id: str) -> str:
        """
        Delete task.

        Args:
            task_id: Task ID
        """
        try:
            # Get task details first
            task = self.api.get_task(task_id)
            content = task.content

            # Delete it
            self.api.delete_task(task_id)

            return self._success(
                f"Deleted task: {content}",
                data={"task_id": task_id, "content": content}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to delete task: {str(e)}")

    def reopen_task(self, task_id: str) -> str:
        """
        Reopen task.

        Args:
            task_id: Task ID
        """
        try:
            # Get task details first
            task = self.api.get_task(task_id)

            # Reopen it
            self.api.uncomplete_task(task_id)

            return self._success(
                f"Reopened task: {task.content}",
                data={"task_id": task_id, "content": task.content}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to reopen task: {str(e)}")

    def move_task(self, task_id: str, project_name: str) -> str:
        """
        Move task.

        Args:
            task_id: Task ID
            project_name: Destination
        """
        try:
            # Find the destination project
            project = self._find_project_by_name(project_name)
            if not project:
                return self._error(
                    "ProjectNotFound",
                    f"Project '{project_name}' not found. Available projects: "
                    f"{', '.join(p.name for p in self._get_projects())}"
                )

            # Move the task
            result = self.api.move_task(task_id, project_id=project.id)

            # Get the task to confirm move
            task = self.api.get_task(task_id)

            return self._success(
                f"Moved task to #{project_name}: {task.content}",
                data={"task_id": task.id, "project": project_name, "content": task.content}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to move task: {str(e)}")

    def batch_move_tasks(self, task_ids: list[str], project_name: str) -> str:
        """
        Move multiple tasks to a project in batch (optimized for performance).

        This method moves multiple tasks sequentially but is optimized to minimize
        API calls by caching the destination project lookup and not fetching task
        details after each move.

        Args:
            task_ids: List of task IDs to move
            project_name: Destination project name

        Returns:
            JSON with success/failure counts and details

        Example:
            batch_move_tasks(
                task_ids=["123", "456", "789"],
                project_name="processed"
            )
        """
        try:
            if not task_ids:
                return self._error("InvalidInput", "No task IDs provided")

            # Find the destination project once (cached lookup)
            project = self._find_project_by_name(project_name)
            if not project:
                return self._error(
                    "ProjectNotFound",
                    f"Project '{project_name}' not found. Available projects: "
                    f"{', '.join(p.name for p in self._get_projects())}"
                )

            # Track results
            successful = []
            failed = []

            # Move all tasks
            for task_id in task_ids:
                try:
                    # Just move without fetching task details (saves API calls)
                    self.api.move_task(task_id, project_id=project.id)
                    successful.append(task_id)
                except Exception as e:
                    failed.append({"task_id": task_id, "error": str(e)})

            # Create summary message
            total = len(task_ids)
            success_count = len(successful)
            fail_count = len(failed)

            summary_parts = []
            if success_count > 0:
                summary_parts.append(f"✅ Moved {success_count} task(s) to #{project_name}")
            if fail_count > 0:
                summary_parts.append(f"❌ Failed to move {fail_count} task(s)")

            summary = " | ".join(summary_parts)

            return self._success(
                summary,
                data={
                    "total": total,
                    "successful": success_count,
                    "failed": fail_count,
                    "project": project_name,
                    "successful_ids": successful,
                    "failed_details": failed
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Batch move failed: {str(e)}")

    def list_projects(self) -> str:
        """List projects."""
        try:
            projects = self._get_projects()

            project_list = []
            for project in projects:
                project_info = {
                    "id": project.id,
                    "name": project.name,
                    "color": project.color,
                    "is_favorite": project.is_favorite
                }
                project_list.append(project_info)

            # Create readable summary
            summary_lines = [f"Found {len(projects)} project(s):\n"]
            for i, project in enumerate(projects, 1):
                fav_str = " ⭐" if project.is_favorite else ""
                summary_lines.append(f"{i}. #{project.name}{fav_str}")

            return self._success(
                "\n".join(summary_lines),
                data={"projects": project_list, "count": len(projects)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list projects: {str(e)}")

    def list_sections(self, project_name: str = None) -> str:
        """
        List sections.

        Args:
            project_name: Project filter
        """
        try:
            project_id = None
            if project_name:
                project = self._find_project_by_name(project_name)
                if not project:
                    return self._error("ProjectNotFound", f"Project '{project_name}' not found")
                project_id = project.id

            sections = self._get_sections(project_id=project_id)

            if not sections:
                return self._success("No sections found")

            section_list = []
            for section in sections:
                section_info = {
                    "id": section.id,
                    "name": section.name,
                    "project_id": section.project_id
                }
                section_list.append(section_info)

            # Create readable summary
            filter_msg = f" in project '{project_name}'" if project_name else ""
            summary_lines = [f"Found {len(sections)} section(s){filter_msg}:\n"]
            for i, section in enumerate(sections, 1):
                summary_lines.append(f"{i}. {section.name}")

            return self._success(
                "\n".join(summary_lines),
                data={"sections": section_list, "count": len(sections)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list sections: {str(e)}")

    def list_labels(self) -> str:
        """List labels."""
        try:
            labels = self._get_labels()

            if not labels:
                return self._success("No labels found")

            label_list = []
            for label in labels:
                label_info = {
                    "id": label.id,
                    "name": label.name,
                    "color": label.color,
                    "is_favorite": label.is_favorite
                }
                label_list.append(label_info)

            # Create readable summary
            summary_lines = [f"Found {len(labels)} label(s):\n"]
            for i, label in enumerate(labels, 1):
                fav_str = " ⭐" if label.is_favorite else ""
                summary_lines.append(f"{i}. @{label.name}{fav_str}")

            return self._success(
                "\n".join(summary_lines),
                data={"labels": label_list, "count": len(labels)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list labels: {str(e)}")

    def get_comments(self, task_id: str) -> str:
        """
        Get comments.

        Args:
            task_id: Task ID
        """
        try:
            comments_paginator = self.api.get_comments(task_id=task_id)
            comments = next(iter(comments_paginator))

            if not comments:
                return self._success("No comments found")

            comment_list = []
            for comment in comments:
                comment_info = {
                    "id": comment.id,
                    "content": comment.content,
                    "posted_at": str(comment.posted_at) if comment.posted_at else None
                }
                comment_list.append(comment_info)

            # Create readable summary
            summary_lines = [f"Found {len(comments)} comment(s):\n"]
            for i, comment in enumerate(comments, 1):
                summary_lines.append(f"{i}. {comment.content} (posted: {comment.posted_at})")

            return self._success(
                "\n".join(summary_lines),
                data={"comments": comment_list, "count": len(comments)}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to get comments: {str(e)}")

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

    def update_rules(
        self,
        section: str,
        rule_content: str,
        operation: str = "auto"
    ) -> str:
        """
        Updates the learned rules knowledge file and commits to git.

        Use this tool to save new preferences, patterns, and rules as you learn them
        from conversations with the user. This ensures persistent memory across sessions.
        Changes are automatically backed up to git.

        Args:
            section: The section to update (e.g., "Processing Rules", "Weekly Review", "Task Patterns")
            rule_content: The rule or preference to add/update/replace (markdown formatted)
            operation: How to update - "auto" (default), "append", or "replace"
                      "auto" intelligently detects: checks if similar rule exists
                      "append" adds new rule to section
                      "replace" replaces entire section content

        IMPORTANT: Always explain what you're changing and why before calling this.
        """
        try:
            import subprocess
            import re

            # Ensure knowledge directory exists
            legacy_knowledge_dir = Path("knowledge")
            legacy_knowledge_dir.mkdir(parents=True, exist_ok=True)

            # Read current rules file
            if self.rules_file.exists():
                content = self.rules_file.read_text()
            else:
                # Create initial structure if file doesn't exist
                content = """# Learned GTD Rules

**Purpose:** This file stores learned preferences and patterns discovered through conversations.
**Maintained by:** TodoistAgent (updated with user approval)
**Last updated:** {date}

---

"""

            # Update the last modified date
            now = datetime.now(self.timezone)
            date_str = now.strftime("%Y-%m-%d")
            content = content.replace("**Last updated:**", f"**Last updated:** {date_str}\n**Last updated:**").replace(f"**Last updated:** {date_str}\n**Last updated:**", f"**Last updated:** {date_str}")

            # Find or create the section
            section_header = f"## {section}"

            # Auto-detect operation if needed
            actual_operation = operation
            if operation == "auto" and section_header in content:
                # Extract current section content
                section_pos = content.find(section_header)
                next_section = content.find("\n##", section_pos + len(section_header))
                if next_section != -1:
                    current_section_content = content[section_pos:next_section]
                else:
                    current_section_content = content[section_pos:]

                # Check if this is an update/removal of existing content
                # Look for keywords that indicate replacement intent
                if any(keyword in rule_content.lower() for keyword in ["removing", "delete", "update", "change", "replace"]):
                    actual_operation = "replace"
                # Check if the rule pattern already exists (simple similarity check)
                elif any(line.strip() in current_section_content for line in rule_content.split('\n') if line.strip() and not line.strip().startswith('#')):
                    actual_operation = "replace"
                else:
                    actual_operation = "append"
            elif operation == "auto":
                actual_operation = "append"  # New section, always append

            if section_header in content:
                # Section exists
                if actual_operation == "replace":
                    # Replace entire section content
                    # Match from section header to next ## or end of file
                    pattern = f"({re.escape(section_header)}\n)(.*?)(\n##|$)"
                    replacement = f"\\1\n{rule_content}\n\\3"
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                else:
                    # Append to section
                    # Find the section and add content after the header
                    section_pos = content.find(section_header)
                    if section_pos != -1:
                        # Find the end of the section (next ## or end of file)
                        next_section = content.find("\n##", section_pos + len(section_header))
                        if next_section != -1:
                            # Insert before next section
                            content = content[:next_section] + f"\n{rule_content}\n" + content[next_section:]
                        else:
                            # Append at end
                            content += f"\n{rule_content}\n"
            else:
                # Section doesn't exist, create it
                content += f"\n{section_header}\n\n{rule_content}\n\n---\n"

            # Write updated content
            self.rules_file.write_text(content)

            # Git backup: commit and push the change
            git_success = False
            try:
                # Stage the file
                subprocess.run(
                    ["git", "add", str(self.rules_file)],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.knowledge_dir.parent)
                )

                # Commit with descriptive message
                commit_msg = f"chore(knowledge): Update {section} in todoist_rules.md\n\nAutomatically committed by TodoistAgent on {date_str}"
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.knowledge_dir.parent)
                )

                # Push to remote
                subprocess.run(
                    ["git", "push"],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.knowledge_dir.parent)
                )

                git_success = True
            except subprocess.CalledProcessError as git_error:
                # Git backup failed, but file was still saved locally
                # Log the error but don't fail the whole operation
                pass

            confirmation_msg = f"✅ MEMORY UPDATED: Added to '{section}' section"
            if git_success:
                confirmation_msg += " and backed up to git"

            return self._success(
                confirmation_msg,
                data={
                    "section": section,
                    "operation": operation,
                    "file": str(self.rules_file),
                    "git_backup": git_success,
                    "confirmation": f"Rules successfully saved to {section}. Memory persisted{' and backed up to git' if git_success else ''}."
                }
            )

        except Exception as e:
            return self._error("FileError", f"Failed to update rules: {str(e)}")

    # =========================================================================
    # GTD-NATIVE CONSTRAINED TOOLS (Workflow-Specific)
    # =========================================================================

    def capture(self, content: str) -> str:
        """
        Quick capture to Inbox - get it out of your head fast.

        Args:
            content: What needs capturing
        """
        try:
            inbox = self._find_project_by_name("Inbox")
            task = self.api.add_task(
                content=content,
                project_id=inbox.id,
                priority=1
            )
            return self._success(
                "→ Inbox",
                data={"task_id": task.id, "content": task.content}
            )
        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to capture: {str(e)}")

    def add_grocery(self, item: str) -> str:
        """
        Add item to shopping list (bypasses GTD).

        Args:
            item: Grocery item
        """
        try:
            groceries = self._find_project_by_name("groceries")
            task = self.api.add_task(
                content=item,
                project_id=groceries.id,
                priority=1
            )
            return self._success(
                "→ Groceries",
                data={"task_id": task.id, "content": task.content}
            )
        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to add grocery: {str(e)}")

    def make_actionable(
        self,
        task_id: str,
        location: Literal["home", "house", "yard", "errand", "bunnings", "parents"],
        activity: Literal["chore", "maintenance", "call", "email", "computer"],
        energy: Literal["lowenergy", "medenergy", "highenergy"],
        duration: Literal["short", "medium", "long"],
        next_action: str = None,
        additional_contexts: list[str] = None,
        description: str = None
    ) -> str:
        """
        Process task from Inbox → Processed with full GTD contexts.

        NOTE: Todoist API requires 2 separate calls (move + update) - this is unavoidable.

        Args:
            task_id: Task to process
            location: WHERE task happens
            activity: WHAT type of activity
            energy: Energy level required
            duration: Time estimate
            next_action: If multi-step, what's the immediate next physical action
            additional_contexts: Optional extra labels (weather, nokids, people)
            description: Optional notes/context
        """
        try:
            # Build labels
            labels = [location, activity, energy, duration]
            if additional_contexts:
                labels.extend([ctx.lstrip('@') for ctx in additional_contexts])

            # Handle next action logic BEFORE updating task
            if next_action:
                # Multi-step task - parent gets labels, subtask gets @next
                pass  # Don't add @next to parent
            else:
                # Simple task - IS the next action, so add @next to parent
                labels.append("next")

            # Find processed project
            processed = self._find_project_by_name("processed")

            # Move to processed with all subtasks (if any)
            move_result = self._move_task_with_subtasks(task_id, processed.id)

            # Update labels and description (API call 2 of 2 - unavoidable)
            update_data = {"labels": labels}
            if description:
                update_data["description"] = description
            self.api.update_task(task_id, **update_data)

            # Create next action subtask if needed
            if next_action:
                # Multi-step task - create subtask with @next
                self.api.add_task(
                    content=next_action,
                    parent_id=task_id,
                    labels=["next"]
                )
                next_info = f" + next: {next_action}"
            else:
                next_info = " [@next]"

            return self._success(
                f"✓ Processed{next_info}",
                data={"task_id": task_id, "labels": labels}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to make actionable: {str(e)}")

    def ask_question(
        self,
        task_id: str,
        person: Literal["bec", "william", "reece", "alex", "parents"],
        via_call: bool = False
    ) -> str:
        """
        Move task to Questions project with person context.

        NOTE: Todoist API requires 2 separate calls (move + update) - this is unavoidable.

        Args:
            task_id: Task to move
            person: Who to ask
            via_call: True if need to call them
        """
        try:
            # Build labels (questions are always low-energy & short)
            labels = [person, "lowenergy", "short"]
            if via_call:
                labels.append("call")

            # Find questions project
            questions = self._find_project_by_name("questions")

            # Move to questions (API call 1 of 2 - unavoidable)
            self.api.move_task(task_id, project_id=questions.id)

            # Update labels (API call 2 of 2 - unavoidable)
            self.api.update_task(task_id, labels=labels)

            return self._success(
                f"→ Questions (@{person})",
                data={"task_id": task_id, "person": person}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to create question: {str(e)}")

    def _calculate_reminder_time(self, due_date: str, due_time: str = None) -> datetime:
        """
        Calculate reminder time using 45-minute buffer rule.

        Rules:
        - If due_time >= 08:30 OR no due_time: reminder = 07:45
        - If due_time < 08:30: reminder = due_time - 45 minutes

        Args:
            due_date: Date in YYYY-MM-DD format
            due_time: Time in HH:MM format (24-hour), optional

        Returns:
            datetime object with timezone
        """
        from datetime import timedelta

        # Parse due date
        due_dt = datetime.strptime(due_date, "%Y-%m-%d")
        due_dt = due_dt.replace(tzinfo=self.timezone)

        if due_time:
            # Parse time
            hour, minute = map(int, due_time.split(":"))
            due_dt = due_dt.replace(hour=hour, minute=minute)

            # Check if before 8:30am
            cutoff = due_dt.replace(hour=8, minute=30)

            if due_dt < cutoff:
                # Maintain 45-minute buffer
                reminder_dt = due_dt - timedelta(minutes=45)
            else:
                # Use default 7:45am
                reminder_dt = due_dt.replace(hour=7, minute=45)
        else:
            # No time specified, default to 7:45am
            reminder_dt = due_dt.replace(hour=7, minute=45)

        return reminder_dt

    def _get_subtasks(self, parent_id: str) -> list[Task]:
        """
        Get all subtasks for a parent task.

        Args:
            parent_id: ID of parent task

        Returns:
            List of Task objects that are children of the parent
        """
        all_tasks = self._get_tasks_list()
        return [task for task in all_tasks if task.parent_id == parent_id]

    def _move_task_with_subtasks(self, task_id: str, project_id: str) -> dict:
        """
        Move a task and all its subtasks to a new project.

        Subtasks inherit parent's project, but we move them explicitly to be safe.

        Args:
            task_id: Parent task ID
            project_id: Destination project ID

        Returns:
            dict with counts of moved tasks
        """
        # Move parent first
        self.api.move_task(task_id, project_id=project_id)
        moved_count = 1

        # Get and move all subtasks
        subtasks = self._get_subtasks(task_id)
        for subtask in subtasks:
            try:
                self.api.move_task(subtask.id, project_id=project_id)
                moved_count += 1
            except Exception as e:
                # Log but don't fail - subtask might already be in correct project
                pass

        return {
            "moved_count": moved_count,
            "parent_id": task_id,
            "subtask_count": len(subtasks)
        }

    def _find_staggered_slot(self, target_datetime: datetime) -> datetime:
        """
        Find next available reminder slot, staggering by 1 minute if occupied.

        Checks all tasks in reminder project and increments time until free slot found.

        Args:
            target_datetime: Desired reminder time

        Returns:
            Available datetime (may be offset from target)
        """
        from datetime import timedelta

        # Get all tasks in reminder project
        reminder_project = self._find_project_by_name("reminder")
        tasks = self._get_tasks_list(project_id=reminder_project.id)

        # Extract all due datetimes
        occupied_slots = set()
        for task in tasks:
            if task.due and task.due.datetime:
                # Parse ISO datetime and normalize to minute precision
                dt = datetime.fromisoformat(task.due.datetime.replace('Z', '+00:00'))
                # Convert to user timezone and truncate seconds
                dt = dt.astimezone(self.timezone).replace(second=0, microsecond=0)
                occupied_slots.add(dt)

        # Find free slot
        candidate = target_datetime.replace(second=0, microsecond=0)
        while candidate in occupied_slots:
            candidate += timedelta(minutes=1)

        return candidate

    def set_reminder(
        self,
        task_id: str,
        due_date: str,
        due_time: str = None
    ) -> str:
        """
        Set reminder for a task (standard 45-minute buffer rule).

        Workflow:
        1. Set due date/time on original task (stays in current project)
        2. Calculate reminder time (7:45am default, or due_time - 45min if before 8:30am)
        3. Find staggered slot (increment by 1min if conflict)
        4. Create reminder task in "reminder" project with calculated time
        5. Prompt user to manually set Todoist reminder attribute via UI

        Args:
            task_id: Task to set reminder for
            due_date: Due date in YYYY-MM-DD format
            due_time: Due time in HH:MM format (24-hour), optional

        Example:
            set_reminder("123", "2025-10-22", "14:30")
            → Original task due 2025-10-22 14:30
            → Reminder task created for 2025-10-22 07:45 (or 07:46 if 07:45 occupied)
        """
        try:
            # Step 1: Get original task details
            task = self.api.get_task(task_id)

            # Step 2: Set due date/time on original task
            if due_time:
                due_string = f"{due_date} {due_time}"
            else:
                due_string = due_date
            self.api.update_task(task_id, due_string=due_string)

            # Step 3: Calculate reminder time
            reminder_datetime = self._calculate_reminder_time(due_date, due_time)

            # Step 4: Find staggered slot
            final_reminder_time = self._find_staggered_slot(reminder_datetime)

            # Step 5: Create reminder task in "reminder" project
            reminder_project = self._find_project_by_name("reminder")

            # Format datetime for Todoist API (ISO 8601 with timezone)
            reminder_due_string = final_reminder_time.isoformat()

            reminder_task = self.api.add_task(
                content=f"REMINDER: {task.content}",
                project_id=reminder_project.id,
                due_string=reminder_due_string
            )

            # Format time for display
            time_display = final_reminder_time.strftime("%I:%M %p")

            return self._success(
                f"✓ Reminder task created for {time_display}\n"
                f"⚠️  MANUAL ACTION REQUIRED: Open Todoist and set reminder attribute on task:\n"
                f"   {reminder_task.url}",
                data={
                    "original_task_id": task_id,
                    "original_task_due": due_string,
                    "reminder_task_id": reminder_task.id,
                    "reminder_task_url": reminder_task.url,
                    "reminder_time": final_reminder_time.isoformat(),
                    "reminder_time_display": time_display
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to set reminder: {str(e)}")

    def create_standalone_reminder(
        self,
        content: str,
        reminder_date: str,
        reminder_time: str = "07:45"
    ) -> str:
        """
        Create a standalone reminder (not linked to any existing task).

        Use this when user wants a simple reminder like "remind me about basketball at 9am tomorrow".
        Creates task directly in "reminder" project with staggered time if needed.

        Args:
            content: What to be reminded about
            reminder_date: Date in YYYY-MM-DD format
            reminder_time: Time in HH:MM format (24-hour), default 07:45

        Example:
            create_standalone_reminder("Basketball game", "2025-10-23", "09:00")
        """
        try:
            # Parse reminder datetime
            reminder_dt = datetime.strptime(f"{reminder_date} {reminder_time}", "%Y-%m-%d %H:%M")
            reminder_dt = reminder_dt.replace(tzinfo=self.timezone)

            # Find staggered slot
            final_reminder_time = self._find_staggered_slot(reminder_dt)

            # Create task in reminder project
            reminder_project = self._find_project_by_name("reminder")
            reminder_task = self.api.add_task(
                content=f"REMINDER: {content}",
                project_id=reminder_project.id,
                due_string=final_reminder_time.isoformat()
            )

            # Format time for display
            time_display = final_reminder_time.strftime("%I:%M %p on %A, %B %d")

            return self._success(
                f"✓ Standalone reminder created for {time_display}\n"
                f"⚠️  MANUAL ACTION REQUIRED: Open Todoist and set reminder attribute on task:\n"
                f"   {reminder_task.url}",
                data={
                    "reminder_task_id": reminder_task.id,
                    "reminder_task_url": reminder_task.url,
                    "reminder_time": final_reminder_time.isoformat(),
                    "reminder_time_display": time_display
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to create standalone reminder: {str(e)}")

    def set_routine_reminder(
        self,
        task_id: str,
        reminder_time: str,
        recurrence: str = "every day"
    ) -> str:
        """
        Set reminder for routine task (reminder time = due time, recurring).

        For routine tasks, the reminder time matches the due time exactly (no 45-minute buffer).
        Task is moved to "routine" project and made recurring.

        Workflow:
        1. Move task to "routine" project
        2. Set as recurring with due time
        3. Create matching recurring reminder task in "reminder" project
        4. Prompt user to manually set Todoist reminder attribute

        Args:
            task_id: Task to convert to routine
            reminder_time: Time in HH:MM format (24-hour) - serves as both due time and reminder time
            recurrence: Recurrence pattern (default: "every day")

        Example:
            set_routine_reminder("123", "09:00", "every day")
            → Task moved to routine, recurring daily at 9:00am
            → Reminder task created in reminder project, also recurring daily at 9:00am
        """
        try:
            # Step 1: Get task details
            task = self.api.get_task(task_id)

            # Step 2: Move to routine project
            routine_project = self._find_project_by_name("routine")
            self.api.move_task(task_id, project_id=routine_project.id)

            # Step 3: Set recurring due time
            due_string = f"{recurrence} at {reminder_time}"
            self.api.update_task(task_id, due_string=due_string)

            # Step 4: Create matching reminder task in "reminder" project (also recurring)
            reminder_project = self._find_project_by_name("reminder")

            reminder_task = self.api.add_task(
                content=f"REMINDER: {task.content}",
                project_id=reminder_project.id,
                due_string=due_string  # Same recurring pattern
            )

            # Parse time for display
            hour, minute = map(int, reminder_time.split(":"))
            time_obj = datetime.now(self.timezone).replace(hour=hour, minute=minute)
            time_display = time_obj.strftime("%I:%M %p")

            return self._success(
                f"✓ Routine reminder created: {recurrence} at {time_display}\n"
                f"⚠️  MANUAL ACTION REQUIRED: Open Todoist and set reminder attribute on task:\n"
                f"   {reminder_task.url}",
                data={
                    "routine_task_id": task_id,
                    "routine_task_due": due_string,
                    "reminder_task_id": reminder_task.id,
                    "reminder_task_url": reminder_task.url,
                    "reminder_time": reminder_time,
                    "reminder_time_display": time_display,
                    "recurrence": recurrence
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to set routine reminder: {str(e)}")

    def reset_overdue_routines(self) -> str:
        """
        Reset overdue DAILY routine tasks to today.

        Finds all tasks in "routine" project that are:
        - Daily recurring (due.is_recurring = True with "every day" pattern)
        - Overdue (due date is before today)

        Reschedules them to today, preserving the time component.
        Useful for daily routines that got skipped - brings them back to current day.

        Returns:
            JSON with count of reset tasks and their details
        """
        try:
            from datetime import date

            # Get current date
            today = date.today().strftime("%Y-%m-%d")

            # Get all tasks in routine project
            routine_project = self._find_project_by_name("routine")
            if not routine_project:
                return self._error(
                    "ProjectNotFound",
                    f"Project 'routine' not found. Available projects: "
                    f"{', '.join(p.name for p in self._get_projects())}"
                )
            tasks = self._get_tasks_list(project_id=routine_project.id)

            # Find overdue DAILY recurring tasks
            overdue_daily_tasks = []
            today_date = date.today()

            # Track statistics for reporting
            daily_recurring_count = 0
            non_daily_recurring_count = 0
            non_recurring_count = 0

            for task in tasks:
                if task.due and task.due.date:
                    try:
                        # Check if it's a recurring task
                        if not task.due.is_recurring:
                            non_recurring_count += 1
                            continue

                        # Check if it's a daily recurrence
                        # Todoist returns string like "every day" or "every 1 day"
                        if task.due.string and "every day" not in task.due.string.lower() and "every 1 day" not in task.due.string.lower():
                            non_daily_recurring_count += 1
                            continue

                        # It's a daily recurring task
                        daily_recurring_count += 1

                        # Parse due date
                        due_date = datetime.strptime(task.due.date, "%Y-%m-%d").date()

                        # Check if overdue (due date is before today)
                        if due_date < today_date:
                            overdue_daily_tasks.append(task)
                    except:
                        # Skip tasks with invalid dates
                        continue

            if not overdue_daily_tasks:
                summary = f"✓ Checked {len(tasks)} routine tasks: {daily_recurring_count} daily recurring, {non_daily_recurring_count} other recurring, {non_recurring_count} non-recurring. No overdue daily routines found."
                return self._success(
                    summary,
                    data={
                        "total_tasks": len(tasks),
                        "daily_recurring": daily_recurring_count,
                        "non_daily_recurring": non_daily_recurring_count,
                        "non_recurring": non_recurring_count,
                        "overdue_count": 0
                    }
                )

            # Reset each overdue daily task to today
            reset_count = 0
            reset_details = []

            for task in overdue_daily_tasks:
                try:
                    # Preserve time if it exists
                    if task.due.datetime:
                        # Has time component - preserve it
                        old_dt = datetime.fromisoformat(task.due.datetime.replace('Z', '+00:00'))
                        new_dt = datetime.combine(today_date, old_dt.time())
                        new_dt = new_dt.replace(tzinfo=self.timezone)
                        due_string = new_dt.isoformat()
                    else:
                        # Date only - just update date
                        due_string = today

                    # Update task
                    self.api.update_task(task.id, due_string=due_string)
                    reset_count += 1

                    reset_details.append({
                        "task_id": task.id,
                        "content": task.content,
                        "old_due": task.due.date,
                        "new_due": today
                    })
                except Exception as e:
                    # Skip tasks that fail to update
                    continue

            return self._success(
                f"✓ Reset {reset_count} overdue daily routine task(s) to today",
                data={
                    "reset_count": reset_count,
                    "reset_tasks": reset_details
                }
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to reset daily routines: {str(e)}")

    def list_next_actions(self) -> str:
        """
        Show all tasks marked @next - ready to work on.
        """
        try:
            tasks = self._get_tasks_list(label="next")

            if not tasks:
                return self._success("No next actions found")

            # Format task list
            summary_lines = [f"Found {len(tasks)} next action(s):\n"]
            for i, task in enumerate(tasks, 1):
                labels_str = f" [{', '.join('@' + l for l in task.labels if l != 'next')}]" if task.labels else ""
                summary_lines.append(f"{i}. {task.content}{labels_str}")

            return self._success(
                "\n".join(summary_lines),
                data={"count": len(tasks), "task_ids": [t.id for t in tasks]}
            )

        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to list next actions: {str(e)}")

    def schedule_task(self, task_id: str, date: str) -> str:
        """
        Schedule a processed task for a specific day (planning).

        Args:
            task_id: Task to schedule
            date: Date to schedule (YYYY-MM-DD)
        """
        try:
            self.api.update_task(task_id, due_string=date)
            return self._success(
                f"Scheduled → {date}",
                data={"task_id": task_id, "date": date}
            )
        except Exception as e:
            return self._error("TodoistAPIError", f"Failed to schedule task: {str(e)}")
