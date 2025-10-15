"""
Integration tests for LocalVectorStore with ChromaDB.

Tests the full functionality with mocked ChromaDB to avoid
requiring actual database connections during testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestLocalVectorStoreInitialization:
    """Test LocalVectorStore initialization and client creation."""

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_initialize_creates_persistent_client(self, mock_persistent_client):
        """Test that initialize creates a ChromaDB persistent client."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Initialize store
        config = {"path": "./test_db", "collection_name": "test"}
        store = LocalVectorStore(config)
        store.initialize(config)

        # Verify client creation
        mock_persistent_client.assert_called_once_with(path="./test_db")
        mock_client.get_or_create_collection.assert_called_once_with(name="test")
        assert store.client is not None
        assert store.collection is not None

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_initialize_called_automatically_on_query(self, mock_persistent_client):
        """Test that query() initializes store if not already initialized."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {"documents": [["test result"]]}
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Create store without initializing
        config = {"path": "./test_db"}
        store = LocalVectorStore(config)

        # Query should auto-initialize
        results = store.query("test query")

        # Verify initialization happened
        mock_persistent_client.assert_called_once()
        assert results == ["test result"]


class TestLocalVectorStoreQuery:
    """Test semantic search functionality."""

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_query_returns_documents(self, mock_persistent_client):
        """Test that query returns relevant documents."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["doc1 content", "doc2 content", "doc3 content"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Query store
        config = {"path": "./test_db"}
        store = LocalVectorStore(config)
        results = store.query("test query", k=3)

        # Verify query was called correctly
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=3
        )
        assert len(results) == 3
        assert results[0] == "doc1 content"

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_query_handles_empty_results(self, mock_persistent_client):
        """Test that query handles empty results gracefully."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {"documents": None}
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Query store
        config = {"path": "./test_db"}
        store = LocalVectorStore(config)
        results = store.query("test query")

        assert results == []

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_query_default_k_value(self, mock_persistent_client):
        """Test that query uses default k=5."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {"documents": [[]]}
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Query without k parameter
        config = {"path": "./test_db"}
        store = LocalVectorStore(config)
        store.query("test query")

        # Verify default k=5 was used
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=5
        )


class TestLocalVectorStoreSync:
    """Test file indexing and synchronization."""

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    @patch("core.knowledge.local_vector_store.Path")
    def test_sync_indexes_files(self, mock_path_class, mock_persistent_client):
        """Test that sync indexes files from directory."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup ChromaDB mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Setup Path mock
        mock_source_path = Mock()
        mock_source_path.exists.return_value = True
        mock_path_class.return_value = mock_source_path

        # Mock file discovery
        mock_file1 = Mock()
        mock_file1.name = "test.py"
        mock_file1.__str__ = lambda self: "/test/test.py"

        mock_file2 = Mock()
        mock_file2.name = "readme.md"
        mock_file2.__str__ = lambda self: "/test/readme.md"

        mock_source_path.rglob.side_effect = lambda pattern: (
            [mock_file1] if pattern == "*.py" else
            [mock_file2] if pattern == "*.md" else
            []
        )

        # Mock file reading
        with patch("builtins.open", create=True) as mock_open:
            mock_file_handle = MagicMock()
            mock_file_handle.__enter__.return_value.read.side_effect = [
                "print('hello')",
                "# README"
            ]
            mock_open.return_value = mock_file_handle

            # Sync store
            config = {"path": "./test_db", "chunk_size": 1000}
            store = LocalVectorStore(config)
            store.sync("/test/source")

            # Verify files were indexed
            assert mock_collection.add.called
            call_args = mock_collection.add.call_args
            assert "documents" in call_args.kwargs
            assert "metadatas" in call_args.kwargs
            assert "ids" in call_args.kwargs

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    @patch("core.knowledge.local_vector_store.Path")
    def test_sync_raises_for_nonexistent_directory(self, mock_path_class, mock_persistent_client):
        """Test that sync raises ValueError for nonexistent directory."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mocks
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        mock_source_path = Mock()
        mock_source_path.exists.return_value = False
        mock_path_class.return_value = mock_source_path

        # Sync should raise
        config = {"path": "./test_db"}
        store = LocalVectorStore(config)

        with pytest.raises(ValueError) as exc_info:
            store.sync("/nonexistent")

        assert "Source directory does not exist" in str(exc_info.value)


class TestLocalVectorStoreClear:
    """Test clearing functionality."""

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_clear_deletes_and_recreates_collection(self, mock_persistent_client):
        """Test that clear() deletes and recreates collection."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client.create_collection.return_value = Mock()
        mock_persistent_client.return_value = mock_client

        # Clear store
        config = {"path": "./test_db", "collection_name": "test"}
        store = LocalVectorStore(config)
        store.clear()

        # Verify delete and recreate
        mock_client.delete_collection.assert_called_once_with(name="test")
        mock_client.create_collection.assert_called_once_with(name="test")


class TestLocalVectorStoreStats:
    """Test statistics functionality."""

    @patch("core.knowledge.local_vector_store.chromadb.PersistentClient")
    def test_get_stats_returns_collection_info(self, mock_persistent_client):
        """Test that get_stats() returns collection information."""
        from core.knowledge.local_vector_store import LocalVectorStore

        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_persistent_client.return_value = mock_client

        # Get stats
        config = {
            "path": "./custom_db",
            "collection_name": "my_collection"
        }
        store = LocalVectorStore(config)
        stats = store.get_stats()

        # Verify stats structure
        assert stats["collection_name"] == "my_collection"
        assert stats["document_count"] == 42
        assert stats["path"] == "./custom_db"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
