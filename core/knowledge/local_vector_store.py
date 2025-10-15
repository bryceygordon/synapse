"""
Local vector store implementation using ChromaDB.

This knowledge store indexes local files and provides semantic search
for retrieving relevant context. Suitable for CoderAgent and DocumentAgent.
"""

import os
from pathlib import Path
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError(
        "ChromaDB is required for LocalVectorStore. "
        "Install it with: pip install chromadb"
    )

from core.knowledge.base_store import BaseKnowledgeStore


class LocalVectorStore(BaseKnowledgeStore):
    """
    Local vector store for file-based knowledge using ChromaDB.

    Stores document embeddings locally and provides semantic search.
    """

    def __init__(self, config: dict):
        """
        Initialize the local vector store.

        Args:
            config: Configuration dictionary with keys:
                - path: Directory to store ChromaDB data
                - collection_name: Name for the collection
                - chunk_size: (optional) Size of text chunks
        """
        self.config = config
        self.path = config.get("path", "./knowledge_db")
        self.collection_name = config.get("collection_name", "default")
        self.chunk_size = config.get("chunk_size", 1000)

        self.client: Optional[chromadb.Client] = None
        self.collection = None

    def initialize(self, config: dict) -> None:
        """
        Initialize ChromaDB client and collection.

        Args:
            config: Configuration dictionary (same as __init__)
        """
        # Create persistent client
        self.client = chromadb.PersistentClient(path=self.path)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def query(self, query: str, k: int = 5) -> list[str]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant document contents
        """
        if not self.collection:
            self.initialize(self.config)

        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )

        # Extract documents from results
        if results and results.get("documents"):
            return results["documents"][0]  # First query's results
        return []

    def sync(self, source: str) -> None:
        """
        Sync files from a directory into the vector store.

        Args:
            source: Directory path to index
        """
        if not self.collection:
            self.initialize(self.config)

        source_path = Path(source)
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source}")

        # Find all text files
        file_extensions = [".py", ".md", ".txt", ".yaml", ".yml", ".json"]
        files_to_index = []

        for ext in file_extensions:
            files_to_index.extend(source_path.rglob(f"*{ext}"))

        # Index each file
        documents = []
        metadatas = []
        ids = []

        for idx, file_path in enumerate(files_to_index):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append(content[:self.chunk_size])  # Simple chunking
                metadatas.append({
                    "file_path": str(file_path),
                    "file_name": file_path.name
                })
                ids.append(f"doc_{idx}")

            except Exception as e:
                # Skip files that can't be read
                continue

        # Add to collection if we have documents
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def clear(self) -> None:
        """Clear all documents from the collection."""
        if not self.collection:
            self.initialize(self.config)

        # Delete and recreate collection
        if self.client:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name
            )

    def get_stats(self) -> dict:
        """
        Get statistics about the knowledge store.

        Returns:
            Dictionary with collection stats
        """
        if not self.collection:
            self.initialize(self.config)

        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "path": self.path
        }
