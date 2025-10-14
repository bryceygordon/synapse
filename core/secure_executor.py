import docker
import os

def execute_sandboxed_command(command: list[str]) -> str:
    """
    Executes a command inside a new, ephemeral, and hardened Docker container.

    Args:
        command: A list of strings representing the command and its arguments.

    Returns:
        The combined stdout and stderr from the container.
    """
    try:
        client = docker.from_env()
        workspace_path = os.getcwd()

        container = client.containers.run(
            image="debian:bookworm-slim",  # A minimal, trusted base image
            command=command,
            working_dir="/workspace",
            volumes={workspace_path: {"bind": "/workspace", "mode": "rw"}},
            remove=True,  # Ephemeral: container is deleted after execution
            detach=False, # Run in the foreground and wait for completion
            security_opt=["no-new-privileges"], # Prevent privilege escalation
            user=f"{os.getuid()}:{os.getgid()}", # Run as the current host user
        )

        # The result is returned as bytes, so we decode it.
        output = container.decode('utf-8')
        return f"Command executed successfully:\n{output}"

    except docker.errors.ContainerError as e:
        # This error is raised for non-zero exit codes.
        return f"Command failed with exit code {e.exit_status}:\n{e.stderr.decode('utf-8')}"
    except docker.errors.ImageNotFound:
        return "Error: The 'debian:bookworm-slim' Docker image was not found. Please run 'docker pull debian:bookworm-slim'."
    except Exception as e:
        return f"An unexpected error occurred with Docker: {e}"

