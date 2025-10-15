"""
Tests for new Todoist features added in recent updates.

Tests include:
- Label data in list_tasks response
- Label fixing (splitting comma-separated labels)
- Date format handling (YYYY-MM-DD)
"""

import pytest
import json
from unittest.mock import Mock, patch
from core.agents.todoist_openai import TodoistAgent
from todoist_api_python.models import Task, Project


@pytest.fixture
def mock_todoist_api():
    """Create a mock TodoistAPI instance."""
    with patch('core.agents.todoist_openai.TodoistAPI') as mock_api_class:
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        yield mock_api


@pytest.fixture
def mock_env(monkeypatch):
    """Set up environment variables."""
    monkeypatch.setenv("TODOIST_API_TOKEN", "test_token_123")
    monkeypatch.setenv("TIMEZONE", "Australia/Sydney")


@pytest.fixture
def agent(mock_env, mock_todoist_api):
    """Create a TodoistAgent instance with mocked API."""
    config = {
        "name": "TodoistAgent",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "system_prompt": "Test prompt"
    }
    return TodoistAgent(config)


@pytest.fixture
def mock_project():
    """Create a mock Project."""
    project = Mock(spec=Project)
    project.id = "proj123"
    project.name = "Inbox"
    project.color = "blue"
    project.is_favorite = False
    return project


# =============================================================================
# LIST_TASKS RETURNS LABELS IN DATA PAYLOAD
# =============================================================================

def test_list_tasks_includes_labels_in_data(agent, mock_todoist_api):
    """Test that list_tasks returns labels array in data payload."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Test task"
    task.labels = ["home", "chore"]
    task.priority = 1
    task.due = None
    task.project_id = "proj123"
    task.created_at = "2025-01-01T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task]])

    result = agent.list_tasks()
    data = json.loads(result)

    assert data["status"] == "success"
    assert "tasks" in data["data"]
    assert len(data["data"]["tasks"]) == 1

    # CRITICAL: labels must be in the data payload
    task_data = data["data"]["tasks"][0]
    assert "labels" in task_data
    assert task_data["labels"] == ["home", "chore"]


def test_list_tasks_includes_priority_in_data(agent, mock_todoist_api):
    """Test that list_tasks returns priority in data payload."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "High priority task"
    task.labels = []
    task.priority = 4
    task.due = None
    task.project_id = "proj123"
    task.created_at = "2025-01-01T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task]])

    result = agent.list_tasks()
    data = json.loads(result)

    task_data = data["data"]["tasks"][0]
    assert "priority" in task_data
    assert task_data["priority"] == 4


def test_list_tasks_includes_due_in_data(agent, mock_todoist_api):
    """Test that list_tasks returns due date in data payload."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Task with due date"
    task.labels = []
    task.priority = 1
    task.due = Mock()
    task.due.string = "tomorrow"
    task.project_id = "proj123"
    task.created_at = "2025-01-01T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task]])

    result = agent.list_tasks()
    data = json.loads(result)

    task_data = data["data"]["tasks"][0]
    assert "due" in task_data
    assert task_data["due"] == "tomorrow"


# =============================================================================
# LABEL FIXING TESTS
# =============================================================================

def test_create_task_splits_comma_separated_labels(agent, mock_todoist_api, mock_project):
    """Test that create_task handles comma-separated labels passed as string."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Test task"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    # Simulate AI accidentally passing comma-separated string
    result = agent.create_task(
        content="Test task",
        project_name="Inbox",
        labels="home,chore,yard"  # This is wrong, but should be handled
    )

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify labels were split correctly
    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["labels"] == ["home", "chore", "yard"]


def test_create_task_strips_at_symbols_from_labels(agent, mock_todoist_api, mock_project):
    """Test that @ symbols are stripped from labels."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Test task"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    result = agent.create_task(
        content="Test task",
        project_name="Inbox",
        labels=["@home", "@chore", "@yard"]
    )

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify @ symbols were stripped
    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["labels"] == ["home", "chore", "yard"]


def test_update_task_fixes_malformed_labels(agent, mock_todoist_api):
    """Test that update_task can fix malformed labels."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Updated task"

    mock_todoist_api.update_task.return_value = task

    # Simulate fixing a malformed label like "yard,@maintenance,@weather"
    result = agent.update_task(
        task_id="task123",
        labels=["yard", "maintenance", "weather", "medenergy", "medium"]
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.update_task.call_args[1]
    assert call_args["labels"] == ["yard", "maintenance", "weather", "medenergy", "medium"]


def test_update_task_handles_comma_and_at_symbols(agent, mock_todoist_api):
    """Test that update_task strips both commas and @ symbols."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Updated task"

    mock_todoist_api.update_task.return_value = task

    # Simulate label with both commas and @ symbols: "@next,@plan"
    result = agent.update_task(
        task_id="task123",
        labels="@next,@plan,@yard"  # Should split on comma and strip @
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.update_task.call_args[1]
    assert call_args["labels"] == ["next", "plan", "yard"]


# =============================================================================
# DATE HANDLING TESTS
# =============================================================================

def test_create_task_accepts_yyyy_mm_dd_format(agent, mock_todoist_api, mock_project):
    """Test that create_task accepts YYYY-MM-DD date format."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Task with explicit date"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    result = agent.create_task(
        content="Task due specific date",
        project_name="Inbox",
        due_string="2025-11-03"
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["due_string"] == "2025-11-03"


def test_create_task_accepts_yyyy_mm_dd_with_time(agent, mock_todoist_api, mock_project):
    """Test that create_task accepts YYYY-MM-DD HH:MM format."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Task with time"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    result = agent.create_task(
        content="Task due at specific time",
        project_name="Inbox",
        due_string="2025-11-03 10:00"
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["due_string"] == "2025-11-03 10:00"


def test_create_task_accepts_recurring_natural_language(agent, mock_todoist_api, mock_project):
    """Test that create_task still accepts natural language for recurring tasks."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Recurring task"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    result = agent.create_task(
        content="Weekly task",
        project_name="Inbox",
        due_string="every monday at 9am"
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["due_string"] == "every monday at 9am"


# =============================================================================
# PROJECT NAMING TESTS (# symbol handling)
# =============================================================================

def test_create_task_defaults_to_inbox(agent, mock_todoist_api, mock_project):
    """Test that create_task defaults to Inbox project."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Default project task"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = task

    # Don't specify project_name, should default to Inbox
    result = agent.create_task(content="Test task")

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify it used Inbox project
    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["project_id"] == "proj123"  # Inbox project ID


def test_create_task_finds_inbox_case_insensitive(agent, mock_todoist_api):
    """Test that project lookup is case-insensitive."""
    inbox_project = Mock(spec=Project)
    inbox_project.id = "inbox123"
    inbox_project.name = "Inbox"  # Capital I
    inbox_project.color = "blue"
    inbox_project.is_favorite = False

    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Task"
    task.url = "https://todoist.com/app/task/123"

    mock_todoist_api.get_projects.return_value = iter([[inbox_project]])
    mock_todoist_api.add_task.return_value = task

    # Try with lowercase "inbox"
    result = agent.create_task(
        content="Test task",
        project_name="inbox"  # lowercase
    )

    data = json.loads(result)
    assert data["status"] == "success"


# =============================================================================
# PAGINATION TESTS
# =============================================================================

def test_get_tasks_list_handles_pagination(agent, mock_todoist_api):
    """Test that _get_tasks_list properly handles pagination."""
    # Create multiple pages of tasks
    page1_tasks = [Mock(spec=Task) for _ in range(50)]
    page2_tasks = [Mock(spec=Task) for _ in range(35)]

    for i, task in enumerate(page1_tasks):
        task.id = f"task{i}"
        task.content = f"Task {i}"
        task.labels = []
        task.priority = 1
        task.due = None
        task.project_id = "proj123"
        task.created_at = "2025-01-01T00:00:00Z"

    for i, task in enumerate(page2_tasks):
        task.id = f"task{i+50}"
        task.content = f"Task {i+50}"
        task.labels = []
        task.priority = 1
        task.due = None
        task.project_id = "proj123"
        task.created_at = "2025-01-01T00:00:00Z"

    # Mock paginator returns two pages
    mock_todoist_api.get_tasks.return_value = iter([page1_tasks, page2_tasks])

    result = agent.list_tasks()
    data = json.loads(result)

    assert data["status"] == "success"
    # Should return ALL 85 tasks, not just first 50
    assert data["data"]["count"] == 85
    assert len(data["data"]["tasks"]) == 85
