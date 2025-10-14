from core.agents.coder import CoderAgent

# We instantiate the agent once with a dummy config for all tests in this file.
dummy_config = {"name": "TestCoder"}
agent = CoderAgent(config=dummy_config)

def test_read_and_write_file(tmp_path):
    """Tests that the agent can write a file and then read it back."""
    file = tmp_path / "test.txt"
    content = "Hello, Synapse!"

    # Test write
    write_result = agent.write_file(str(file), content)
    assert "Successfully wrote" in write_result
    assert file.exists()

    # Test read
    read_result = agent.read_file(str(file))
    assert read_result == content

def test_read_file_not_found():
    """Tests that reading a non-existent file returns an error."""
    result = agent.read_file("non_existent_file.txt")
    assert "Error: File not found" in result

def test_list_files(tmp_path):
    """Tests that the agent can list files in a directory."""
    (tmp_path / "dir1").mkdir()
    (tmp_path / "file1.txt").touch()
    (tmp_path / "dir1" / "file2.txt").touch()

    result = agent.list_files(str(tmp_path))

    # Check if the known files and directories are in the output string
    assert "dir1" in result
    assert "file1.txt" in result
    assert "file2.txt" in result

def test_run_shell_command():
    """Tests that the agent can run a simple shell command."""
    # Using 'echo' is a safe, cross-platform command for testing
    result = agent.run_shell_command("echo 'hello world'")
    assert "hello world" in result
    assert "STDOUT" in result

def test_run_shell_command_error():
    """Tests that a failing shell command returns an error and stderr."""
    # 'ls' on a non-existent file will return a non-zero exit code
    result = agent.run_shell_command("ls non_existent_directory_12345")
    assert "failed with exit code" in result
    assert "STDERR" in result

