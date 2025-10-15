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
        self.provider: str = config.get("provider", "anthropic")  # Which AI provider to use
        self.model: str = config.get("model", "claude-sonnet-4.5")  # Provider-specific model
        self.system_prompt: str = config.get("system_prompt", "You are a helpful assistant.")
        self.tools: list[str] = config.get("tools", [])

        # Legacy OpenAI field - kept for backward compatibility, deprecated
        self.vector_store_id: str | None = config.get("vector_store_id")

        # Knowledge store configuration (Phase 4)
        self.knowledge_store_config: dict | None = config.get("knowledge_store")
        self.knowledge_store = None  # Will be initialized in Phase 4

