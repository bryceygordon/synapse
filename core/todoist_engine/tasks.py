# core/todoist_engine/tasks.py

import os
import json
from typing import Optional, List
from todoist_api_python.api import TodoistAPI, Task, Project, Section, Label

# --- API Initialization ---

def get_api_client() -> TodoistAPI:
    """Initializes and returns the Todoist API client."""
    api_token = os.getenv("TODOIST_TOKEN") or os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise ValueError("TODOIST_TOKEN or TODOIST_API_TOKEN environment variable not set.")
    return TodoistAPI(api_token)

# --- Response Helpers ---

def _success(content: str, data: dict = None) -> str:
    """Formats a standardized success JSON response."""
    response = {"status": "success", "content": content}
    if data:
        response["data"] = data
    return json.dumps(response, indent=2)

def _error(error_type: str, message: str) -> str:
    """Formats a standardized error JSON response."""
    response = {"status": "error", "error_type": error_type, "message": message}
    return json.dumps(response, indent=2)

# --- Data Fetching & Lookup Helpers ---

def get_projects(api: TodoistAPI) -> list[Project]:
    """Retrieves all projects."""
    projects_paginator = api.get_projects()
    all_projects = []
    for page in projects_paginator:
        all_projects.extend(page)
    return all_projects

def find_project_by_name(api: TodoistAPI, project_name: str) -> Optional[Project]:
    """Finds a project by its name (case-insensitive)."""
    projects = get_projects(api)
    return next((p for p in projects if p.name.lower() == project_name.lower()), None)

def find_section_by_name(api: TodoistAPI, section_name: str, project_id: str) -> Optional[Section]:
    """Finds a section by its name within a project."""
    sections = api.get_sections(project_id=project_id)
    return next((s for s in sections if s.name.lower() == section_name.lower()), None)

# --- Core Task Functions ---

def get_tasks_list(api: TodoistAPI, **kwargs) -> list[Task]:
    """Get ALL tasks as a list (handles pagination)."""
    tasks_paginator = api.get_tasks(**kwargs)
    all_tasks = []
    for page in tasks_paginator:
        all_tasks.extend(page)
    return all_tasks

def get_task(api: TodoistAPI, task_id: str) -> str:
    """Get task details."""
    try:
        task = api.get_task(task_id)
        task_info = {
            "id": task.id, "content": task.content, "description": task.description,
            "project_id": task.project_id, "labels": task.labels, "priority": task.priority,
            "due": task.due.string if task.due else None, "url": task.url,
            "created_at": str(task.created_at) if task.created_at else None
        }
        labels_str = f"\\nLabels: {', '.join('@' + l for l in task.labels)}" if task.labels else ""
        due_str = f"\\nDue: {task.due.string}" if task.due else ""
        priority_str = f"\\nPriority: P{task.priority}" if task.priority > 1 else ""
        desc_str = f"\\nDescription: {task.description}" if task.description else ""
        summary = f"{task.content}{labels_str}{due_str}{priority_str}{desc_str}"
        return _success(summary, data=task_info)
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to get task: {str(e)}")

def create_task(api: TodoistAPI, content: str, project_name: str = "Inbox", labels: list[str] = None, priority: int = 1, due_string: str = None, description: str = None, section_name: str = None, parent_id: str = None, duration: int = None, duration_unit: str = "minute") -> Task:
    """
    Create task. Returns the created Task object.
    Raises ValueError for not found project/section, and re-raises API errors.
    """
    try:
        task_data = {"content": content, "priority": priority}
        if parent_id:
            task_data["parent_id"] = parent_id
        else:
            project = find_project_by_name(api, project_name)
            if not project:
                raise ValueError(f"Project '{project_name}' not found.")
            task_data["project_id"] = project.id
        if section_name and not parent_id:
            section = find_section_by_name(api, section_name, project_id=task_data["project_id"])
            if not section:
                raise ValueError(f"Section '{section_name}' not found in project '{project_name}'")
            task_data["section_id"] = section.id
        if parent_id:
            task_data["parent_id"] = parent_id
        if labels:
            if isinstance(labels, str):
                labels = [label.strip().lstrip('@') for label in labels.split(',')] if ',' in labels else [labels]
            clean_labels = [label.lstrip('@').strip() for label in labels]
            task_data["labels"] = clean_labels
        if due_string:
            task_data["due_string"] = due_string
        if description:
            task_data["description"] = description
        if duration is not None:
            task_data["duration"] = duration
            task_data["duration_unit"] = duration_unit

        task = api.add_task(**task_data)
        return task
    except Exception as e:
        # Re-raise exceptions to be handled by the caller.
        raise e

def update_task(api: TodoistAPI, task_id: str, content: str = None, labels: list[str] = None, priority: int = None, due_string: str = None, description: str = None, duration: int = None, duration_unit: str = "minute") -> str:
    """Update task."""
    try:
        update_data = {}
        if content is not None: update_data["content"] = content
        if labels is not None:
            if isinstance(labels, str):
                labels = [label.strip().lstrip('@') for label in labels.split(',')] if ',' in labels else [labels]
            clean_labels = [label.lstrip('@').strip() for label in labels]
            update_data["labels"] = clean_labels
        if priority is not None: update_data["priority"] = priority
        if due_string is not None: update_data["due_string"] = due_string
        if description is not None: update_data["description"] = description
        if duration is not None:
            update_data["duration"] = duration
            update_data["duration_unit"] = duration_unit

        if not update_data:
            return _error("InvalidInput", "No updates provided")

        is_success = api.update_task(task_id, **update_data)
        if is_success:
            task = api.get_task(task_id)
            return _success(f"Updated task: {task.content}", data={"task_id": task.id, "content": task.content})
        else:
            return _error("TodoistAPIError", "Failed to update task, API returned unsuccessful.")
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to update task: {str(e)}")

def complete_task(api: TodoistAPI, task_id: str) -> str:
    """Complete task."""
    try:
        api.complete_task(task_id)
        return _success("✓ Task completed", data={"task_id": task_id})
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to complete task: {str(e)}")

def reopen_task(api: TodoistAPI, task_id: str) -> str:
    """Reopen task."""
    try:
        task = api.get_task(task_id)
        api.uncomplete_task(task_id)
        return _success(f"Reopened task: {task.content}", data={"task_id": task_id, "content": task.content})
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to reopen task: {str(e)}")

def delete_task(api: TodoistAPI, task_id: str) -> str:
    """Delete task."""
    try:
        task = api.get_task(task_id)
        content = task.content
        api.delete_task(task_id)
        return _success(f"Deleted task: {content}", data={"task_id": task_id, "content": content})
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to delete task: {str(e)}")

def move_task(api: TodoistAPI, task_id: str, project_id: str) -> str:
    """Move task to a different project."""
    try:
        is_success = api.move_task(task_id=task_id, project_id=project_id)
        if is_success:
            return _success(f"Moved task to new project.", data={"task_id": task_id, "project_id": project_id})
        else:
            return _error("TodoistAPIError", "Failed to move task, API returned unsuccessful.")
    except Exception as e:
        return _error("TodoistAPIError", f"Failed to move task: {str(e)}")
