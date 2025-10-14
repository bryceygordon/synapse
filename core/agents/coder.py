import subprocess
from pathlib import Path
from core.agents.base import BaseAgent

class CoderAgent(BaseAgent):
    """
    A specialized agent for software development tasks.
    Its methods serve as the tools it can use to interact with the filesystem
    and development environment.
    """

    def read_file(self, file_path: str) -> str:
        """
        Reads the content of a file at the specified path.

        Args:
            file_path: The relative or absolute path to the file.

        Returns:
            The content of the file as a string, or an error message if the file
            is not found or cannot be read.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File not found at {file_path}"
            
            with open(path, "r") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        """
        Writes or overwrites content to a file at the specified path.
        It will create parent directories if they do not exist.

        Args:
            file_path: The path where the file will be written.
            content: The string content to write to the file.

        Returns:
            A success message or an error message.
        """
        try:
            path = Path(file_path)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_files(self, directory_path: str = ".") -> str:
        """
        Lists all files and directories in a specified directory, recursively.

        Args:
            directory_path: The path to the directory to list. Defaults to the current directory.

        Returns:
            A string representation of the directory tree, or an error message.
        """
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                return f"Error: Directory not found at {directory_path}"

            tree = []
            for item in sorted(path.rglob('*')):
                tree.append(str(item))
            
            return "\n".join(tree)
        except Exception as e:
            return f"Error listing files: {e}"

    def run_shell_command(self, command: str) -> str:
        """
        Executes a shell command and returns its output.
        SECURITY: This is a powerful tool. Be cautious about the commands executed.
        For this project, we assume a trusted user environment.

        Args:
            command: The shell command to execute.

        Returns:
            The combined stdout and stderr of the command, or an error message.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            output = f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}"
            return output
        except subprocess.CalledProcessError as e:
            # This catches errors where the command returns a non-zero exit code
            return f"Command '{command}' failed with exit code {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred while running command '{command}': {e}"

