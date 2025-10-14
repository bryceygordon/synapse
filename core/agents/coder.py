from pathlib import Path
from core.agents.base import BaseAgent
from core.secure_executor import execute_sandboxed_command # We will create this next

class CoderAgent(BaseAgent):
    """
    A specialized agent for software development tasks.
    Its methods are specific, secure tools that delegate execution to a sandboxed environment.
    """

    def read_file(self, file_path: str) -> str:
        """
        Reads the content of a file at the specified path.

        Args:
            file_path: The relative or absolute path to the file.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File not found at {file_path}"
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        """
        Writes or overwrites content to a file at the specified path.

        Args:
            file_path: The path where the file will be written.
            content: The string content to write to the file.
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_files(self, directory_path: str = ".") -> str:
        """
        Lists all files and directories in a specified directory.
        Args:
            directory_path: The path to the directory to list. Defaults to the current directory.
        """
        command = ["ls", "-la", directory_path]
        return execute_sandboxed_command(command)

    def run_tests(self, path: str = ".") -> str:
        """
        Runs the pytest test suite on a given path.
        Args:
            path: The specific file or directory to run tests on. Defaults to the whole project.
        """
        command = ["python", "-m", "pytest", path]
        return execute_sandboxed_command(command)

    def git_commit(self, message: str) -> str:
        """
        Stages all changes and creates a git commit with the provided message.
        Args:
            message: The commit message.
        """
        add_command = ["git", "add", "."]
        execute_sandboxed_command(add_command) # Run the 'add' first

        commit_command = ["git", "commit", "-m", message]
        return execute_sandboxed_command(commit_command)
