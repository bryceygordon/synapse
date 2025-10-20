# tests/test_inbox_wizard.py

import pytest
from unittest.mock import MagicMock, patch, call
import unittest
from rich.console import Console

# Mock the modules that are not available in the test environment or need to be controlled.
# This is important for isolating the script's logic from its dependencies.
import sys
import os

# Ensure the script's directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now, we can import the script we want to test
from scripts import process_inbox

@patch('scripts.process_inbox.tasks.get_api_client')
@patch('scripts.process_inbox.tasks.find_project_by_name')
@patch('scripts.process_inbox.tasks.get_tasks_list')
@patch('rich.prompt.Prompt.ask')
@patch('rich.prompt.Confirm.ask')
@patch('rich.console.Console.print')
def test_run_inbox_wizard_happy_path(
    mock_console_print, mock_confirm_ask, mock_prompt_ask,
    mock_get_tasks, mock_find_project, mock_get_api
):
    """
    Tests the happy path of the inbox wizard where the user processes one task and exits.
    """
    # Arrange: Mock the API calls and user inputs
    mock_api = MagicMock()
    mock_get_api.return_value = mock_api

    mock_project = MagicMock()
    mock_project.id = 'inbox-project-id'
    mock_find_project.return_value = mock_project

    mock_task = MagicMock()
    mock_task.id = 'task-123'
    mock_task.content = 'My test task'
    mock_get_tasks.return_value = [mock_task]

    # Simulate user walking through the wizard for one task
    mock_prompt_ask.side_effect = [
        "process",      # Choose to process the task
        "simple",       # Mark as a simple task
        "Test task details @home #today p1",  # Add details
        "exit"          # Exit after the first task
    ]
    mock_confirm_ask.return_value = False  # Don't rename the task

    # Mock the agent response part to avoid running the actual agent
    mock_agent_config = {'provider': 'mock_provider', 'model': 'mock_model', 'system_prompt': 'mock_prompt'}
    with patch('builtins.open', unittest.mock.mock_open(read_data='')), \
         patch('yaml.safe_load', return_value=mock_agent_config), \
         patch('scripts.process_inbox.get_provider') as mock_get_provider:

        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        # Act
        process_inbox.run_inbox_wizard()

    # Assert: Verify that the key functions were called as expected
    mock_get_api.assert_called_once()
    mock_find_project.assert_called_with(mock_api, "Inbox")
    mock_get_tasks.assert_called_with(mock_api, project_id='inbox-project-id')

    # Verify user prompts
    assert mock_prompt_ask.call_count > 0

    # Verify that the success message is printed
    mock_console_print.assert_any_call("\n[bold green]Inbox processing complete. Handing off to the agent for refinement...[/bold green]")
