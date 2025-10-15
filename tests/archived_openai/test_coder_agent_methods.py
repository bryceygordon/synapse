# tests/test_coder_agent_methods.py

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.agents.coder import CoderAgent

# Keep the agent instantiation if it exists, or add it.
agent = CoderAgent(config={
    "name": "TestCoder",
    "tools": ["run_tests", "git_commit"]
})

@patch('core.agents.coder.execute_sandboxed_command')
def test_run_tests_calls_executor(mock_executor):
    """Tests that run_tests() calls the secure executor with the correct command."""
    # This is the fix: construct the expected absolute path.
    expected_path = str(Path("tests/").resolve())
    expected_command = ["python", "-m", "pytest", expected_path, "-v"]
    
    agent.run_tests(path="tests/")
    
    # Assert the new, correct command.
    mock_executor.assert_called_once_with(expected_command)

@patch('core.agents.coder.execute_sandboxed_command')
def test_git_commit_calls_executor(mock_executor):
    """Tests that git_commit() calls the executor for both add and commit."""
    agent.git_commit(message="feat: new feature")
    assert mock_executor.call_count == 2
    mock_executor.assert_any_call(["git", "add", "."])
    mock_executor.assert_called_with(["git", "commit", "-m", "feat: new feature"])
