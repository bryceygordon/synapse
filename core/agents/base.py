class BaseAgent:
    """
    A base class for all agents, handling the initialization of common attributes
    from a configuration dictionary.
    """
    def __init__(self, config: dict):
        """
        Initializes the agent with attributes from the provided config.

        Args:
            config: A dictionary loaded from the agent's YAML configuration file.
        """
        self.name: str = config.get("name", "Unnamed Agent")
        self.class_name: str = config.get("class_name", "BaseAgent")
        self.model: str = config.get("model", "gpt-4o") # A sensible default
        self.system_prompt: str = config.get("system_prompt", "You are a helpful assistant.")
        self.vector_store_id: str | None = config.get("vector_store_id")
        self.tools: list[str] = config.get("tools", [])

