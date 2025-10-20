# tests/test_todoist_engine.py

import pytest
from unittest.mock import MagicMock, patch
from core.todoist_engine import tasks

def test_get_api_client_success():
    """
    Tests that get_api_client returns a TodoistAPI instance when the token is set.
    """
    with patch.dict('os.environ', {'TODOIST_API_TOKEN': 'fake_token'}):
        api_client = tasks.get_api_client()
        assert api_client is not None
        # Further assertions can be made here about the type of the returned object
        # For example, if TodoistAPI is the expected class:
        # from todoist_api_python.api import TodoistAPI
        # assert isinstance(api_client, TodoistAPI)

def test_get_api_client_failure():
    """
    Tests that get_api_client raises a ValueError when the token is not set.
    """
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="TODOIST_API_TOKEN environment variable not set."):
            tasks.get_api_client()

class TestTaskFunctions:
    """Test suite for core task functions in the todoist engine."""

    def setup_method(self):
        """Set up a mock API client for each test."""
        self.mock_api = MagicMock()

    def test_find_project_by_name_found(self):
        """Test finding an existing project."""
        mock_project = MagicMock()
        mock_project.name = "Inbox"
        self.mock_api.get_projects.return_value = [mock_project]

        project = tasks.find_project_by_name(self.mock_api, "Inbox")

        assert project is not None
        assert project.name == "Inbox"
        self.mock_api.get_projects.assert_called_once()

    def test_find_project_by_name_not_found(self):
        """Test finding a non-existent project."""
        mock_project = MagicMock()
        mock_project.name = "Work"
        self.mock_api.get_projects.return_value = [mock_project]

        project = tasks.find_project_by_name(self.mock_api, "Inbox")

        assert project is None
        self.mock_api.get_projects.assert_called_once()

    def test_get_tasks_list(self):
        """Test retrieving a list of tasks."""
        mock_task1 = MagicMock()
        mock_task2 = MagicMock()
        # Simulate paginated response
        self.mock_api.get_tasks.return_value = [[mock_task1], [mock_task2]]

        task_list = tasks.get_tasks_list(self.mock_api, project_id="123")

        assert len(task_list) == 2
        self.mock_api.get_tasks.assert_called_once_with(project_id="123")

    def test_update_task_success(self):
        """Test successfully updating a task."""
        self.mock_api.update_task.return_value = True
        self.mock_api.get_task.return_value = MagicMock(id="123", content="Updated content")

        result_json = tasks.update_task(self.mock_api, task_id="123", content="Updated content")

        import json
        result = json.loads(result_json)

        assert result["status"] == "success"
        assert result["content"] == "Updated task: Updated content"
        self.mock_api.update_task.assert_called_once_with("123", content="Updated content")
        self.mock_api.get_task.assert_called_once_with("123")

    def test_create_task_success(self):
        """Test successfully creating a task."""
        # Mock find_project_by_name to return a mock project
        with patch('core.todoist_engine.tasks.find_project_by_name') as mock_find:
            mock_project = MagicMock()
            mock_project.id = "project-id-123"
            mock_find.return_value = mock_project

            mock_added_task = MagicMock()
            mock_added_task.id = "task-id-456"
            mock_added_task.content = "New Task"
            mock_added_task.url = "http://todoist.com/task/456"
            self.mock_api.add_task.return_value = mock_added_task

            result_json = tasks.create_task(self.mock_api, content="New Task", project_name="Inbox")

            import json
            result = json.loads(result_json)

            assert result["status"] == "success"
            assert "Created task in #Inbox" in result["content"]
            self.mock_api.add_task.assert_called_once()
