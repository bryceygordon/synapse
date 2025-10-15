"""
Tests for knowledge store abstraction layer.

Verifies that:
1. BaseKnowledgeStore enforces abstract interface
2. Knowledge store factory works correctly
3. LocalVectorStore can be instantiated
"""

import pytest
from core.knowledge.base_store import BaseKnowledgeStore
from core.knowledge import get_knowledge_store


class TestAbstractBaseEnforcement:
    """Test that BaseKnowledgeStore enforces abstract methods."""

    def test_cannot_instantiate_base_store(self):
        """Test that BaseKnowledgeStore cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseKnowledgeStore()

    def test_subclass_must_implement_all_methods(self):
        """Test that incomplete subclasses cannot be instantiated."""

        class IncompleteStore(BaseKnowledgeStore):
            """Missing required methods."""
            pass

        with pytest.raises(TypeError):
            IncompleteStore()


class TestKnowledgeStoreFactory:
    """Test the knowledge store factory function."""

    def test_factory_creates_local_vector_store(self):
        """Test that factory creates LocalVectorStore."""
        config = {
            "path": "./test_knowledge_db",
            "collection_name": "test_collection"
        }

        store = get_knowledge_store("local_vector_store", config)

        assert store is not None
        assert store.__class__.__name__ == "LocalVectorStore"

    def test_factory_case_insensitive(self):
        """Test that factory handles case-insensitive store types."""
        config = {"path": "./test_db"}

        store1 = get_knowledge_store("local_vector_store", config)
        store2 = get_knowledge_store("LOCAL_VECTOR_STORE", config)
        store3 = get_knowledge_store("Local_Vector_Store", config)

        assert all(s.__class__.__name__ == "LocalVectorStore" for s in [store1, store2, store3])

    def test_factory_raises_for_email_store(self):
        """Test that factory raises NotImplementedError for email_store."""
        with pytest.raises(NotImplementedError) as exc_info:
            get_knowledge_store("email_store", {})

        assert "EmailStore is not yet implemented" in str(exc_info.value)
        assert "local_vector_store" in str(exc_info.value)

    def test_factory_raises_for_task_store(self):
        """Test that factory raises NotImplementedError for task_store."""
        with pytest.raises(NotImplementedError) as exc_info:
            get_knowledge_store("task_store", {})

        assert "TaskStore is not yet implemented" in str(exc_info.value)

    def test_factory_raises_for_unknown_type(self):
        """Test that factory raises ValueError for unknown store types."""
        with pytest.raises(ValueError) as exc_info:
            get_knowledge_store("unknown_store", {})

        assert "Unknown knowledge store type: 'unknown_store'" in str(exc_info.value)


class TestLocalVectorStoreInterface:
    """Test that LocalVectorStore implements the full interface."""

    def test_local_vector_store_has_all_methods(self):
        """Test that LocalVectorStore implements all required methods."""
        from core.knowledge.local_vector_store import LocalVectorStore

        config = {"path": "./test_db"}
        store = LocalVectorStore(config)

        # Check all required methods exist and are callable
        assert hasattr(store, "initialize") and callable(store.initialize)
        assert hasattr(store, "query") and callable(store.query)
        assert hasattr(store, "sync") and callable(store.sync)
        assert hasattr(store, "clear") and callable(store.clear)
        assert hasattr(store, "get_stats") and callable(store.get_stats)

    def test_local_vector_store_config_storage(self):
        """Test that LocalVectorStore stores configuration correctly."""
        from core.knowledge.local_vector_store import LocalVectorStore

        config = {
            "path": "./custom_path",
            "collection_name": "custom_collection",
            "chunk_size": 2000
        }

        store = LocalVectorStore(config)

        assert store.path == "./custom_path"
        assert store.collection_name == "custom_collection"
        assert store.chunk_size == 2000

    def test_local_vector_store_default_values(self):
        """Test that LocalVectorStore uses sensible defaults."""
        from core.knowledge.local_vector_store import LocalVectorStore

        config = {}
        store = LocalVectorStore(config)

        assert store.path == "./knowledge_db"
        assert store.collection_name == "default"
        assert store.chunk_size == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
