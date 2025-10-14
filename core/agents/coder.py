import os
from pathlib import Path
from core.agents.base import BaseAgent
from core.secure_executor import execute_sandboxed_command

class CoderAgent(BaseAgent):
    """
    A specialized agent for software development tasks.
    Its methods are specific, secure tools that delegate execution to a sandboxed environment.
    """
    def read_file(self, file_path: str) -> str:
        """Reads the content of a file at the specified path."""
        try:
            path = Path(file_path)
            if not path.is_file(): return f"Error: Path is not a file: {file_path}"
            return path.read_text()
        except Exception as e: return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        """Writes or overwrites content to a file at the specified path."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e: return f"Error writing file: {e}"

    def list_files(self, directory_path: str = ".", recursive: bool = False) -> str:
        """
        Lists files and directories in a specified path, optionally recursively.
        Args:
            directory_path: The path to the directory to list. Defaults to the current directory.
            recursive: Whether to list files in subdirectories. Defaults to False.
        """
        try:
            base_path = Path(directory_path)
            if not base_path.is_dir(): return f"Error: Not a valid directory: {directory_path}"
            
            ignore_dirs = {'.git', '.venv', '__pycache__', '.pytest_cache'}
            output_files = []

            if recursive:
                for root, dirs, files in os.walk(base_path):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for name in files:
                        full_path = Path(root) / name
                        display_path = full_path.relative_to(base_path)
                        output_files.append(str(display_path))
            else:
                for item in base_path.iterdir():
                    if item.name not in ignore_dirs:
                        output_files.append(item.name)
            
            return "\n".join(sorted(output_files))
        except Exception as e:
            return f"Error listing files: {e}"

    def run_tests(self, path: str = ".") -> str:
        """Runs the pytest test suite on a given path."""
        command = ["python", "-m", "pytest", path]
        return execute_sandboxed_command(command)

    def git_commit(self, message: str) -> str:
        """Stages all changes and creates a git commit with the provided message."""
        add_command = ["git", "add", "."]
        execute_sandboxed_command(add_command)
        commit_command = ["git", "commit", "-m", message]
        return execute_sandboxed_command(commit_command)
