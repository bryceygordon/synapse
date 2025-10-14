import yaml
import importlib
from pathlib import Path
from core.agents.base import BaseAgent

def load_agent(agent_name: str, config_path: str = "agents") -> BaseAgent:
    """
    Loads an agent's configuration, dynamically imports its class,
    and returns an initialized agent instance.

    Args:
        agent_name: The name of the agent to load (e.g., "coder").
        config_path: The directory containing agent YAML files.

    Returns:
        An initialized instance of the specified agent class (e.g., CoderAgent).

    Raises:
        FileNotFoundError: If the agent's YAML file does not exist.
        AttributeError: If the class specified in the YAML does not exist.
        KeyError: If essential keys are missing from the YAML file.
    """
    # 1. Construct the file path and check for existence.
    file_path = Path(config_path) / f"{agent_name}.yaml"
    if not file_path.exists():
        raise FileNotFoundError(f"Agent configuration file not found at: {file_path}")

    # 2. Load the YAML configuration.
    with open(file_path, "r") as f:
        config_data = yaml.safe_load(f)

    if not config_data:
        raise ValueError(f"Configuration file is empty or invalid: {file_path}")

    # 3. Get the required class name from the config.
    class_name = config_data.get("class_name")
    if not class_name:
        raise KeyError(f"'class_name' not specified in {file_path}")

    # 4. Dynamically import the agent's module and get the class.
    # This is the clever part: it turns a string into a real Python class.
    try:
        agent_module = importlib.import_module(f"core.agents.{agent_name}")
        AgentClass = getattr(agent_module, class_name)
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"Could not find class '{class_name}' in module 'core.agents.{agent_name}'. Please check your configuration. Original error: {e}")

    # 5. Instantiate the class with its configuration and return it.
    return AgentClass(config=config_data)

