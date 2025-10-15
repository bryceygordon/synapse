import json
import os
from pathlib import Path
from core.agents.base import BaseAgent
from core.secure_executor import execute_sandboxed_command

class CoderAgent(BaseAgent):
    """
    A specialized agent for software development tasks.
    All methods return structured JSON for better machine reasoning.
    """

    def _success(self, content: str) -> str:
        """Helper to return structured success response."""
        return json.dumps({"status": "success", "content": content})

    def _error(self, error_type: str, message: str) -> str:
        """Helper to return structured error response."""
        return json.dumps({"status": "error", "error_type": error_type, "message": message})

    def _validate_path(self, file_path: str) -> Path:
        """Validates that a path is within the workspace."""
        try:
            workspace = Path.cwd().resolve()
            target = (workspace / file_path).resolve()

            # Ensure the path is within workspace
            target.relative_to(workspace)
            return target
        except ValueError:
            raise PermissionError(f"Access denied: {file_path} is outside workspace")

    def read_file(self, file_path: str) -> str:
        """
        Reads the content of a file at the specified path.

        Args:
            file_path: The relative or absolute path to the file.
        """
        try:
            path = self._validate_path(file_path)
            if not path.exists():
                return self._error("FileNotFoundError", f"File not found at {file_path}")
            if not path.is_file():
                return self._error("ValueError", f"Path {file_path} is not a file")

            with open(path, "r") as f:
                content = f.read()
            return self._success(content)
        except PermissionError as e:
            return self._error("PermissionError", str(e))
        except Exception as e:
            return self._error("IOError", f"Error reading file: {e}")

    def write_file(self, file_path: str, content: str) -> str:
        """
        Writes or overwrites content to a file at the specified path.

        Args:
            file_path: The path where the file will be written.
            content: The string content to write to the file.
        """
        try:
            path = self._validate_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                f.write(content)
            return self._success(f"Successfully wrote to {file_path}")
        except PermissionError as e:
            return self._error("PermissionError", str(e))
        except Exception as e:
            return self._error("IOError", f"Error writing file: {e}")

    def list_files(self, directory_path: str = ".") -> str:
        """
        Lists all files and directories in a specified directory.

        Args:
            directory_path: The path to the directory to list. Defaults to the current directory.
        """
        try:
            path = self._validate_path(directory_path)
            if not path.exists():
                return self._error("FileNotFoundError", f"Directory not found at {directory_path}")
            if not path.is_dir():
                return self._error("ValueError", f"Path {directory_path} is not a directory")

            command = ["ls", "-la", str(path)]
            result = execute_sandboxed_command(command)
            return self._success(result)
        except PermissionError as e:
            return self._error("PermissionError", str(e))
        except Exception as e:
            return self._error("IOError", f"Error listing files: {e}")

    def run_tests(self, path: str = ".") -> str:
        """
        Runs the pytest test suite on a given path.

        Args:
            path: The specific file or directory to run tests on. Defaults to the whole project.
        """
        try:
            validated_path = self._validate_path(path)
            command = ["python", "-m", "pytest", str(validated_path), "-v"]
            result = execute_sandboxed_command(command)

            # Check if tests passed
            if "failed" in result.lower() or "error" in result.lower():
                return self._error("TestFailure", result)
            return self._success(result)
        except PermissionError as e:
            return self._error("PermissionError", str(e))
        except Exception as e:
            return self._error("ExecutionError", f"Error running tests: {e}")

    def git_commit(self, message: str) -> str:
        """
        Stages all changes and creates a git commit with the provided message.

        Args:
            message: The commit message.
        """
        try:
            # First, stage all changes
            add_command = ["git", "add", "."]
            add_result = execute_sandboxed_command(add_command)

            # Then commit
            commit_command = ["git", "commit", "-m", message]
            commit_result = execute_sandboxed_command(commit_command)

            if "nothing to commit" in commit_result.lower():
                return self._error("NoChanges", "No changes to commit")

            return self._success(commit_result)
        except Exception as e:
            return self._error("GitError", f"Error creating commit: {e}")
