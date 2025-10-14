from unittest.mock import patch

# We need to test the methods on the CoderAgent class
from core.agents.coder import CoderAgent

dummy_config = {"name": "TestCoder"}
agent = CoderAgent(config=dummy_config)

@patch('core.agents.coder.execute_sandboxed_command')
def test_run_tests_calls_executor(mock_executor):
    """Tests that run_tests() calls the secure executor with the correct command."""
    agent.run_tests(path="tests/")
    mock_executor.assert_called_once_with(["python", "-m", "pytest", "tests/"])

@patch('core.agents.coder.execute_sandboxed_command')
def test_git_commit_calls_executor(mock_executor):
    """Tests that git_commit() calls the secure executor for both 'add' and 'commit'."""
    agent.git_commit(message="Test commit")

    assert mock_executor.call_count == 2
    # Check the 'git add' call
    mock_executor.call_args_list[0].assert_called_with(["git", "add", "."])
    # Check the 'git commit' call
    mock_executor.call_args_list[1].assert_called_with(["git", "commit", "-m", "Test commit"])

