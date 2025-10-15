"""
Knowledge management system for Synapse agents.

This module provides a pluggable knowledge store system that allows different
agent types to use appropriate knowledge backends:
- File-based agents (CoderAgent) use LocalVectorStore with ChromaDB
- Email agents (EmailAgent) use EmailStore with IMAP
- Task agents (TaskAgent) use TaskStore with Todoist API
- etc.
"""

from core.knowledge.base_store import BaseKnowledgeStore


def get_knowledge_store(store_type: str, config: dict) -> BaseKnowledgeStore:
    """
    Factory function to create a knowledge store instance.

    Args:
        store_type: Type of knowledge store ('local_vector_store', 'email_store', etc.)
        config: Configuration dictionary for the store

    Returns:
        Instance of the requested knowledge store

    Raises:
        ValueError: If store_type is not supported

    Example:
        >>> config = {"path": "./knowledge", "collection_name": "codebase"}
        >>> store = get_knowledge_store("local_vector_store", config)
    """
    store_type = store_type.lower()

    if store_type == "local_vector_store":
        from core.knowledge.local_vector_store import LocalVectorStore
        return LocalVectorStore(config)
    elif store_type == "email_store":
        raise NotImplementedError(
            "EmailStore is not yet implemented. "
            "It will be added in a future phase for EmailAgent. "
            "Currently supported stores: local_vector_store"
        )
    elif store_type == "task_store":
        raise NotImplementedError(
            "TaskStore is not yet implemented. "
            "It will be added in a future phase for TaskAgent. "
            "Currently supported stores: local_vector_store"
        )
    else:
        raise ValueError(
            f"Unknown knowledge store type: '{store_type}'. "
            f"Supported types: local_vector_store"
        )


__all__ = [
    'BaseKnowledgeStore',
    'get_knowledge_store',
]
