"""
TodoistAgent - GTD Personal Assistant

This agent manages a Todoist system following strict GTD methodology
and the user's specific workflow design.
"""

import os
import json
from pathlib import Path
from typing import Optional
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

        # Legacy knowledge file paths (for old update_rules/query_rules methods)
        # Note: JIT knowledge now uses BaseAgent.knowledge_dir = "knowledge/todoistagent"
        legacy_knowledge_dir = Path("knowledge")
        self.system_file = legacy_knowledge_dir / "todoist_system.md"
        self.rules_file = legacy_knowledge_dir / "todoist_rules.md"
        self.context_file = legacy_knowledge_dir / "todoist_context.md"

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
            project_name: Project
            labels: Labels (no @)
            priority: 1-4
            due_string: YYYY-MM-DD
            description: Notes
            section_name: Section
            parent_id: Parent ID
            duration: Amount
            duration_unit: Unit
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

            # Add section if provided
            if section_name:
                section = self._find_section_by_name(section_name, project_id=project.id)
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
            # Get task details first
            task = self.api.get_task(task_id)

            # Complete it
            self.api.complete_task(task_id)

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
        operation: str = "append"
    ) -> str:
        """
        Updates the learned rules knowledge file and commits to git.

        Use this tool to save new preferences, patterns, and rules as you learn them
        from conversations with the user. This ensures persistent memory across sessions.
        Changes are automatically backed up to git.

        Args:
            section: The section to update (e.g., "Processing Rules", "Weekly Review", "Task Patterns")
            rule_content: The rule or preference to add (markdown formatted)
            operation: How to update - "append" adds to section, "replace" replaces section content

        IMPORTANT: Always call this with a confirmation message after updating.
        """
        try:
            import subprocess

            # Ensure knowledge directory exists
            self.knowledge_dir.mkdir(parents=True, exist_ok=True)

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

            if section_header in content:
                # Section exists
                if operation == "replace":
                    # Replace entire section content
                    import re
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
