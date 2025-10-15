"""
Abstract base class for knowledge store implementations.

This module defines the interface that all knowledge stores must implement
to work with Synapse's agent system. Different agent types can use different
knowledge backends (files, emails, tasks, databases, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseKnowledgeStore(ABC):
    """
    Abstract base class for knowledge store implementations.

    Knowledge stores provide context and memory for agents. Different domains
    need different knowledge sources:
    - CoderAgent: Local codebase files (ChromaDB)
    - EmailAgent: Email history (IMAP/Gmail API)
    - TaskAgent: Task context (Todoist API)
    - etc.
    """

    @abstractmethod
    def initialize(self, config: dict) -> None:
        """
        Initialize the knowledge store with domain-specific configuration.

        Args:
            config: Configuration dictionary from agent YAML

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def query(self, query: str, k: int = 5) -> list[str]:
        """
        Search for relevant context given a query.

        Args:
            query: The search query (user message, system prompt, etc.)
            k: Number of results to return

        Returns:
            List of relevant context strings
        """
        pass

    @abstractmethod
    def sync(self, source: Any) -> None:
        """
        Sync/index new data from a source.

        The source type varies by implementation:
        - LocalVectorStore: directory path (str)
        - EmailStore: IMAP config (dict)
        - TaskStore: API credentials (dict)

        Args:
            source: Data source to sync (type varies by implementation)
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored knowledge."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """
        Return statistics about the knowledge store.

        Returns:
            Dictionary with store-specific stats (e.g., document count, size)
        """
        pass
