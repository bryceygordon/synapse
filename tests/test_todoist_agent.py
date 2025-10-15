"""
Comprehensive tests for TodoistAgent functionality.

Tests all Todoist API integration methods including:
- Time awareness
- Task CRUD operations
- Task management (move, reopen, delete)
- Project/section/label listing
- Comments
- Advanced features (subtasks, durations, sections)
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from zoneinfo import ZoneInfo

from core.agents.todoist import TodoistAgent
from todoist_api_python.models import Task, Project, Section, Label, Comment


@pytest.fixture
def mock_todoist_api():
    """Create a mock TodoistAPI instance."""
    with patch('core.agents.todoist.TodoistAPI') as mock_api_class:
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
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "system_prompt": "Test prompt"
    }
    return TodoistAgent(config)


@pytest.fixture
def mock_project():
    """Create a mock Project."""
    project = Mock(spec=Project)
    project.id = "proj123"
    project.name = "Processed"
    project.color = "blue"
    project.is_favorite = False
    return project


@pytest.fixture
def mock_task():
    """Create a mock Task."""
    task = Mock(spec=Task)
    task.id = "task123"
    task.content = "Test task"
    task.description = "Test description"
    task.project_id = "proj123"
    task.labels = ["home", "chore"]
    task.priority = 1
    task.due = None
    task.url = "https://todoist.com/app/task/123"
    task.created_at = "2025-01-01T00:00:00Z"
    return task


@pytest.fixture
def mock_section():
    """Create a mock Section."""
    section = Mock(spec=Section)
    section.id = "sect123"
    section.name = "Today"
    section.project_id = "proj123"
    return section


@pytest.fixture
def mock_label():
    """Create a mock Label."""
    label = Mock(spec=Label)
    label.id = "label123"
    label.name = "home"
    label.color = "green"
    label.is_favorite = False
    return label


@pytest.fixture
def mock_comment():
    """Create a mock Comment."""
    comment = Mock(spec=Comment)
    comment.id = "comment123"
    comment.content = "Test comment"
    comment.posted_at = "2025-01-01T00:00:00Z"
    return comment


# =============================================================================
# TIME AWARENESS TESTS
# =============================================================================

def test_get_current_time(agent):
    """Test getting current time in user's timezone."""
    result = agent.get_current_time()
    data = json.loads(result)

    assert data["status"] == "success"
    assert "date" in data["data"]
    assert "datetime" in data["data"]
    assert "day_of_week" in data["data"]
    assert "timezone" in data["data"]
    assert data["data"]["timezone"] == "Australia/Sydney"


def test_get_current_time_includes_formats(agent):
    """Test that current time includes all required formats."""
    result = agent.get_current_time()
    data = json.loads(result)

    assert "date" in data["data"]  # YYYY-MM-DD
    assert "time_24h" in data["data"]  # HH:MM
    assert "time_12h" in data["data"]  # HH:MM AM/PM
    assert "iso8601" in data["data"]  # Full ISO format


# =============================================================================
# TASK CREATION TESTS
# =============================================================================

def test_create_task_basic(agent, mock_todoist_api, mock_project, mock_task):
    """Test basic task creation."""
    # Setup mocks
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = mock_task

    result = agent.create_task(
        content="Test task",
        project_name="Processed"
    )

    data = json.loads(result)
    assert data["status"] == "success"
    assert "task_id" in data["data"]
    mock_todoist_api.add_task.assert_called_once()


def test_create_task_with_all_parameters(agent, mock_todoist_api, mock_project, mock_task, mock_section):
    """Test task creation with all parameters."""
    # Setup mocks
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])
    mock_todoist_api.add_task.return_value = mock_task

    result = agent.create_task(
        content="Complex task",
        project_name="Processed",
        labels=["home", "urgent"],
        priority=4,
        due_string="tomorrow at 2pm",
        description="Detailed description",
        section_name="Today",
        parent_id="parent123",
        duration=30,
        duration_unit="minute"
    )

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify all parameters were passed
    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["content"] == "Complex task"
    assert call_args["project_id"] == "proj123"
    assert call_args["labels"] == ["home", "urgent"]
    assert call_args["priority"] == 4
    assert call_args["due_string"] == "tomorrow at 2pm"
    assert call_args["description"] == "Detailed description"
    assert call_args["section_id"] == "sect123"
    assert call_args["parent_id"] == "parent123"
    assert call_args["duration"] == 30
    assert call_args["duration_unit"] == "minute"


def test_create_task_strips_at_from_labels(agent, mock_todoist_api, mock_project, mock_task):
    """Test that @ prefix is stripped from labels."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.add_task.return_value = mock_task

    agent.create_task(
        content="Task",
        project_name="Processed",
        labels=["@home", "@chore"]
    )

    call_args = mock_todoist_api.add_task.call_args[1]
    assert call_args["labels"] == ["home", "chore"]


def test_create_task_project_not_found(agent, mock_todoist_api, mock_project):
    """Test error when project doesn't exist."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])

    result = agent.create_task(
        content="Task",
        project_name="NonexistentProject"
    )

    data = json.loads(result)
    assert data["status"] == "error"
    assert data["error_type"] == "ProjectNotFound"


def test_create_task_section_not_found(agent, mock_todoist_api, mock_project, mock_section):
    """Test error when section doesn't exist."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])

    result = agent.create_task(
        content="Task",
        project_name="Processed",
        section_name="NonexistentSection"
    )

    data = json.loads(result)
    assert data["status"] == "error"
    assert data["error_type"] == "SectionNotFound"


# =============================================================================
# TASK LISTING TESTS
# =============================================================================

def test_list_tasks_all(agent, mock_todoist_api, mock_task):
    """Test listing all tasks."""
    mock_todoist_api.get_tasks.return_value = iter([[mock_task]])

    result = agent.list_tasks()

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["count"] == 1
    assert len(data["data"]["tasks"]) == 1


def test_list_tasks_by_project(agent, mock_todoist_api, mock_project, mock_task):
    """Test listing tasks filtered by project."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.get_tasks.return_value = iter([[mock_task]])

    result = agent.list_tasks(project_name="Processed")

    data = json.loads(result)
    assert data["status"] == "success"
    mock_todoist_api.get_tasks.assert_called_with(project_id="proj123")


def test_list_tasks_by_label(agent, mock_todoist_api, mock_task):
    """Test listing tasks filtered by label."""
    mock_todoist_api.get_tasks.return_value = iter([[mock_task]])

    result = agent.list_tasks(label="@home")

    data = json.loads(result)
    assert data["status"] == "success"
    # Verify @ was stripped
    mock_todoist_api.get_tasks.assert_called_with(label="home")


def test_list_tasks_by_filter(agent, mock_todoist_api, mock_task):
    """Test listing tasks with local filter query."""
    mock_task.content = "test task"  # Ensure task has content for filtering
    mock_todoist_api.get_tasks.return_value = iter([[mock_task]])

    result = agent.list_tasks(filter_query="test")

    data = json.loads(result)
    assert data["status"] == "success"
    # filter_query is applied locally after fetching all tasks
    mock_todoist_api.get_tasks.assert_called_with()


def test_list_tasks_empty(agent, mock_todoist_api):
    """Test listing tasks when none exist."""
    mock_todoist_api.get_tasks.return_value = iter([[]])

    result = agent.list_tasks()

    data = json.loads(result)
    assert data["status"] == "success"
    assert "No tasks found" in data["message"]


def test_list_tasks_includes_created_at(agent, mock_todoist_api, mock_task):
    """Test that list_tasks includes created_at field."""
    mock_todoist_api.get_tasks.return_value = iter([[mock_task]])

    result = agent.list_tasks()

    data = json.loads(result)
    assert data["status"] == "success"
    assert "created_at" in data["data"]["tasks"][0]
    assert data["data"]["tasks"][0]["created_at"] == "2025-01-01T00:00:00Z"


def test_list_tasks_sort_by_created_desc(agent, mock_todoist_api):
    """Test sorting tasks by creation date (newest first)."""
    # Create multiple tasks with different created_at times
    task1 = Mock(spec=Task)
    task1.id = "task1"
    task1.content = "Oldest task"
    task1.project_id = "proj123"
    task1.labels = []
    task1.priority = 1
    task1.due = None
    task1.url = "https://todoist.com/app/task/1"
    task1.created_at = "2025-01-01T00:00:00Z"

    task2 = Mock(spec=Task)
    task2.id = "task2"
    task2.content = "Middle task"
    task2.project_id = "proj123"
    task2.labels = []
    task2.priority = 1
    task2.due = None
    task2.url = "https://todoist.com/app/task/2"
    task2.created_at = "2025-01-02T00:00:00Z"

    task3 = Mock(spec=Task)
    task3.id = "task3"
    task3.content = "Newest task"
    task3.project_id = "proj123"
    task3.labels = []
    task3.priority = 1
    task3.due = None
    task3.url = "https://todoist.com/app/task/3"
    task3.created_at = "2025-01-03T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task1, task2, task3]])

    result = agent.list_tasks(sort_by="created_desc")

    data = json.loads(result)
    assert data["status"] == "success"
    tasks = data["data"]["tasks"]

    # Should be sorted newest first
    assert tasks[0]["id"] == "task3"
    assert tasks[1]["id"] == "task2"
    assert tasks[2]["id"] == "task1"


def test_list_tasks_sort_by_created_asc(agent, mock_todoist_api):
    """Test sorting tasks by creation date (oldest first)."""
    # Create multiple tasks with different created_at times
    task1 = Mock(spec=Task)
    task1.id = "task1"
    task1.content = "Oldest task"
    task1.project_id = "proj123"
    task1.labels = []
    task1.priority = 1
    task1.due = None
    task1.url = "https://todoist.com/app/task/1"
    task1.created_at = "2025-01-01T00:00:00Z"

    task2 = Mock(spec=Task)
    task2.id = "task2"
    task2.content = "Newest task"
    task2.project_id = "proj123"
    task2.labels = []
    task2.priority = 1
    task2.due = None
    task2.url = "https://todoist.com/app/task/2"
    task2.created_at = "2025-01-02T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task2, task1]])  # Return in wrong order

    result = agent.list_tasks(sort_by="created_asc")

    data = json.loads(result)
    assert data["status"] == "success"
    tasks = data["data"]["tasks"]

    # Should be sorted oldest first
    assert tasks[0]["id"] == "task1"
    assert tasks[1]["id"] == "task2"


def test_list_tasks_sort_by_priority_desc(agent, mock_todoist_api):
    """Test sorting tasks by priority (highest first)."""
    task1 = Mock(spec=Task)
    task1.id = "task1"
    task1.content = "High priority"
    task1.project_id = "proj123"
    task1.labels = []
    task1.priority = 4
    task1.due = None
    task1.url = "https://todoist.com/app/task/1"
    task1.created_at = "2025-01-01T00:00:00Z"

    task2 = Mock(spec=Task)
    task2.id = "task2"
    task2.content = "Low priority"
    task2.project_id = "proj123"
    task2.labels = []
    task2.priority = 1
    task2.due = None
    task2.url = "https://todoist.com/app/task/2"
    task2.created_at = "2025-01-01T00:00:00Z"

    mock_todoist_api.get_tasks.return_value = iter([[task2, task1]])  # Return in wrong order

    result = agent.list_tasks(sort_by="priority_desc")

    data = json.loads(result)
    assert data["status"] == "success"
    tasks = data["data"]["tasks"]

    # Should be sorted by priority descending (4 before 1)
    assert tasks[0]["id"] == "task1"
    assert tasks[0]["priority"] == 4
    assert tasks[1]["id"] == "task2"
    assert tasks[1]["priority"] == 1


# =============================================================================
# TASK UPDATE TESTS
# =============================================================================

def test_update_task(agent, mock_todoist_api, mock_task):
    """Test updating a task."""
    mock_todoist_api.update_task.return_value = mock_task

    result = agent.update_task(
        task_id="task123",
        content="Updated content",
        priority=3,
        due_string="tomorrow"
    )

    data = json.loads(result)
    assert data["status"] == "success"
    mock_todoist_api.update_task.assert_called_once()


def test_update_task_with_duration(agent, mock_todoist_api, mock_task):
    """Test updating task with duration."""
    mock_todoist_api.update_task.return_value = mock_task

    result = agent.update_task(
        task_id="task123",
        duration=45,
        duration_unit="minute"
    )

    data = json.loads(result)
    assert data["status"] == "success"

    call_args = mock_todoist_api.update_task.call_args[1]
    assert call_args["duration"] == 45
    assert call_args["duration_unit"] == "minute"


def test_update_task_no_updates(agent):
    """Test error when no updates provided."""
    result = agent.update_task(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "error"
    assert data["error_type"] == "InvalidInput"


# =============================================================================
# TASK COMPLETION TESTS
# =============================================================================

def test_complete_task(agent, mock_todoist_api, mock_task):
    """Test completing a task."""
    mock_todoist_api.get_task.return_value = mock_task

    result = agent.complete_task(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "Completed task" in data["message"]
    mock_todoist_api.complete_task.assert_called_once_with("task123")


def test_reopen_task(agent, mock_todoist_api, mock_task):
    """Test reopening a completed task."""
    mock_todoist_api.get_task.return_value = mock_task

    result = agent.reopen_task(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "Reopened task" in data["message"]
    mock_todoist_api.uncomplete_task.assert_called_once_with("task123")


def test_delete_task(agent, mock_todoist_api, mock_task):
    """Test deleting a task."""
    mock_todoist_api.get_task.return_value = mock_task

    result = agent.delete_task(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "Deleted task" in data["message"]
    mock_todoist_api.delete_task.assert_called_once_with("task123")


# =============================================================================
# TASK MOVEMENT TESTS
# =============================================================================

def test_move_task(agent, mock_todoist_api, mock_project, mock_task):
    """Test moving a task to another project."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.move_task.return_value = mock_task
    mock_todoist_api.get_task.return_value = mock_task  # Need to mock get_task since move_task calls it

    result = agent.move_task(task_id="task123", project_name="Processed")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "Moved task" in data["message"]
    mock_todoist_api.move_task.assert_called_once_with("task123", project_id="proj123")


def test_move_task_project_not_found(agent, mock_todoist_api, mock_project):
    """Test error when moving to nonexistent project."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])

    result = agent.move_task(task_id="task123", project_name="NonexistentProject")

    data = json.loads(result)
    assert data["status"] == "error"
    assert data["error_type"] == "ProjectNotFound"


# =============================================================================
# PROJECT LISTING TESTS
# =============================================================================

def test_list_projects(agent, mock_todoist_api, mock_project):
    """Test listing all projects."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])

    result = agent.list_projects()

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["count"] == 1
    assert len(data["data"]["projects"]) == 1
    assert data["data"]["projects"][0]["name"] == "Processed"


# =============================================================================
# SECTION LISTING TESTS
# =============================================================================

def test_list_sections_all(agent, mock_todoist_api, mock_section):
    """Test listing all sections."""
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])

    result = agent.list_sections()

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["count"] == 1


def test_list_sections_by_project(agent, mock_todoist_api, mock_project, mock_section):
    """Test listing sections filtered by project."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])

    result = agent.list_sections(project_name="Processed")

    data = json.loads(result)
    assert data["status"] == "success"


def test_list_sections_empty(agent, mock_todoist_api):
    """Test listing sections when none exist."""
    mock_todoist_api.get_sections.return_value = iter([[]])

    result = agent.list_sections()

    data = json.loads(result)
    assert data["status"] == "success"
    assert "No sections found" in data["message"]


# =============================================================================
# LABEL LISTING TESTS
# =============================================================================

def test_list_labels(agent, mock_todoist_api, mock_label):
    """Test listing all labels."""
    mock_todoist_api.get_labels.return_value = iter([[mock_label]])

    result = agent.list_labels()

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["count"] == 1
    assert data["data"]["labels"][0]["name"] == "home"


def test_list_labels_empty(agent, mock_todoist_api):
    """Test listing labels when none exist."""
    mock_todoist_api.get_labels.return_value = iter([[]])

    result = agent.list_labels()

    data = json.loads(result)
    assert data["status"] == "success"
    assert "No labels found" in data["message"]


# =============================================================================
# COMMENT TESTS
# =============================================================================

def test_add_comment(agent, mock_todoist_api, mock_comment):
    """Test adding a comment to a task."""
    mock_todoist_api.add_comment.return_value = mock_comment

    result = agent.add_comment(task_id="task123", comment="Test comment")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "Added comment" in data["message"]
    mock_todoist_api.add_comment.assert_called_once_with(
        task_id="task123",
        content="Test comment"
    )


def test_get_comments(agent, mock_todoist_api, mock_comment):
    """Test getting comments for a task."""
    mock_todoist_api.get_comments.return_value = iter([[mock_comment]])

    result = agent.get_comments(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["count"] == 1
    assert len(data["data"]["comments"]) == 1


def test_get_comments_empty(agent, mock_todoist_api):
    """Test getting comments when none exist."""
    mock_todoist_api.get_comments.return_value = iter([[]])

    result = agent.get_comments(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "No comments found" in data["message"]


# =============================================================================
# GET TASK DETAILS TESTS
# =============================================================================

def test_get_task(agent, mock_todoist_api, mock_task):
    """Test getting task details."""
    mock_todoist_api.get_task.return_value = mock_task

    result = agent.get_task(task_id="task123")

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["data"]["id"] == "task123"
    assert data["data"]["content"] == "Test task"
    assert "url" in data["data"]


# =============================================================================
# CACHE TESTS
# =============================================================================

def test_project_cache(agent, mock_todoist_api, mock_project):
    """Test that projects are cached after first fetch."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])

    # First call
    agent._get_projects()
    # Second call should use cache
    projects = agent._get_projects()

    assert len(projects) == 1
    # API should only be called once
    assert mock_todoist_api.get_projects.call_count == 1


def test_section_cache(agent, mock_todoist_api, mock_section):
    """Test that sections are cached after first fetch."""
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])

    # First call
    agent._get_sections()
    # Second call should use cache
    sections = agent._get_sections()

    assert len(sections) == 1
    # API should only be called once
    assert mock_todoist_api.get_sections.call_count == 1


def test_label_cache(agent, mock_todoist_api, mock_label):
    """Test that labels are cached after first fetch."""
    mock_todoist_api.get_labels.return_value = iter([[mock_label]])

    # First call
    agent._get_labels()
    # Second call should use cache
    labels = agent._get_labels()

    assert len(labels) == 1
    # API should only be called once
    assert mock_todoist_api.get_labels.call_count == 1


# =============================================================================
# HELPER METHOD TESTS
# =============================================================================

def test_find_project_by_name_case_insensitive(agent, mock_todoist_api, mock_project):
    """Test that project search is case-insensitive."""
    mock_todoist_api.get_projects.return_value = iter([[mock_project]])

    project = agent._find_project_by_name("processed")
    assert project is not None
    assert project.name == "Processed"

    project = agent._find_project_by_name("PROCESSED")
    assert project is not None


def test_find_section_by_name_case_insensitive(agent, mock_todoist_api, mock_section):
    """Test that section search is case-insensitive."""
    mock_todoist_api.get_sections.return_value = iter([[mock_section]])

    section = agent._find_section_by_name("today")
    assert section is not None
    assert section.name == "Today"


def test_success_helper(agent):
    """Test _success helper formats response correctly."""
    result = agent._success("Test message", data={"key": "value"})
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["message"] == "Test message"
    assert data["data"]["key"] == "value"


def test_error_helper(agent):
    """Test _error helper formats response correctly."""
    result = agent._error("TestError", "Error message")
    data = json.loads(result)

    assert data["status"] == "error"
    assert data["error_type"] == "TestError"
    assert data["message"] == "Error message"
