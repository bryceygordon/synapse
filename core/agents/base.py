import json
from pathlib import Path


class BaseAgent:
    """
    A base class for all agents, handling the initialization of common attributes
    from a configuration dictionary.

    Implements Just-In-Time (JIT) knowledge loading pattern for efficient token usage.
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

        # Just-In-Time knowledge system
        self.knowledge_dir = Path("knowledge") / self.name.lower().replace(" ", "_")
        self._knowledge_index = None

    def _load_knowledge_index(self) -> dict:
        """Load the knowledge index for this agent."""
        if self._knowledge_index is not None:
            return self._knowledge_index

        index_path = self.knowledge_dir / "index.json"
        if index_path.exists():
            with open(index_path, 'r') as f:
                self._knowledge_index = json.load(f)
        else:
            # Default index if none exists
            self._knowledge_index = {
                "topics": {},
                "description": f"Knowledge base for {self.name}"
            }

        return self._knowledge_index

    def query_knowledge(self, topic: str) -> str:
        """
        Retrieve specific knowledge on-demand (Just-In-Time loading).

        This is a tool exposed to AI agents to query their knowledge base
        only when needed, dramatically reducing token usage.

        Args:
            topic: The knowledge topic to retrieve (e.g., "context_labels", "processing_rules")

        Returns:
            JSON string with knowledge content or error message

        Example:
            >>> agent.query_knowledge("context_labels")
            {"status": "success", "topic": "context_labels", "content": "..."}
        """
        try:
            index = self._load_knowledge_index()

            # Check if topic exists
            if topic not in index.get("topics", {}):
                available = list(index.get("topics", {}).keys())
                return json.dumps({
                    "status": "error",
                    "error": f"Topic '{topic}' not found",
                    "available_topics": available,
                    "hint": f"Available topics: {', '.join(available)}"
                })

            # Load the topic file
            topic_info = index["topics"][topic]
            topic_file = self.knowledge_dir / topic_info["file"]

            if not topic_file.exists():
                return json.dumps({
                    "status": "error",
                    "error": f"Knowledge file not found: {topic_file}"
                })

            content = topic_file.read_text()

            return json.dumps({
                "status": "success",
                "topic": topic,
                "description": topic_info.get("description", ""),
                "content": content
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"Failed to load knowledge: {str(e)}"
            })

