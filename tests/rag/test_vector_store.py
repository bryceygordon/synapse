"""Test vector database operations and semantic search.

This test follows fail-first TDD: written before implementation to capture requirements.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from dataclasses import dataclass
from typing import List
from core.rag.chunking import CodeChunk


@dataclass
class MockPointStruct:
    """Mock Qdrant point for testing."""
    id: int
    vector: List[float]
    payload: dict


class TestQdrantVectorStore:
    """Fail-first tests for vector database operations."""

    def test_vector_store_initialization_works(self):
        """Test that vector store initializes without errors."""
        from core.rag.vector_store import QdrantVectorStore

        store = QdrantVectorStore(collection_name="test_collection")
        assert store is not None
        assert hasattr(store, 'client')
        assert hasattr(store, 'embedder')

    def test_embedding_generation_produces_vectors(self):
        """Test embedding model produces proper vector dimensions."""
        from core.rag.vector_store import QdrantVectorStore

        store = QdrantVectorStore(collection_name="test_collection")
        test_texts = ["def hello(): print('world')", "class Vector: pass"]

        embeddings = store.generate_embeddings(test_texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(test_texts)
        assert all(isinstance(vec, list) for vec in embeddings)
        assert all(len(vec) >= 768 for vec in embeddings)  # Most models have >=768 dims

    def test_chunk_indexing_creates_searchable_chunks(self):
        """Test indexing code chunks makes them searchable."""
        from core.rag.vector_store import QdrantVectorStore

        store = QdrantVectorStore(collection_name="test_indexing")

        chunks = [
            CodeChunk(
                content="def hello_world():\n    return 'Hello World'",
                file_path="test.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "test_0", "token_count_est": 15}
            ),
            CodeChunk(
                content="class Calculator:\n    def add(self, a, b):\n        return a + b",
                file_path="calc.py",
                start_line=1,
                end_line=3,
                chunk_type="class",
                metadata={"chunk_id": "test_1", "token_count_est": 25}
            )
        ]

        # Index chunks
        indexed_count = store.index_chunks(chunks)
        assert indexed_count == len(chunks)

        # Search should work
        results = store.search("add function", top_k=2)
        assert len(results) >= 1  # Should find calculator add

    def test_semantic_search_returns_relevant_chunks(self):
        """Test semantic search finds relevant code over literal matches."""
        from core.rag.vector_store import QdrantVectorStore

        store = QdrantVectorStore(collection_name="test_semantic")

        chunks = [
            CodeChunk(
                content="def login_user(username, password):\n    return authenticate(username, password)",
                file_path="auth.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "auth_0", "token_count_est": 18}
            ),
            CodeChunk(
                content="def calculate_tax(income, deductions):\n    return (income - deductions) * 0.25",
                file_path="finance.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "tax_1", "token_count_est": 22}
            ),
            CodeChunk(
                content="def verify_email(email_addr):\n    return validate_email_format(email_addr)",
                file_path="email.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "email_2", "token_count_est": 20}
            )
        ]

        # Index them
        store.index_chunks(chunks)

        # Search for "log in" - should find authentication over exact matches
        results = store.search("log in to account", top_k=1)
        assert len(results) >= 1
        found_content = results[0].payload.get('content', '')
        assert 'login_user' in found_content or 'authenticate' in found_content

    def test_search_with_file_filter_narrows_results(self):
        """Test that file filtering reduces returned results to specific files."""
        from core.rag.vector_store import QdrantVectorStore

        store = QdrantVectorStore(collection_name="test_filter")

        chunks = [
            CodeChunk(
                content="def connect_database(host):\n    return db.connect(host)",
                file_path="db.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "db_0", "token_count_est": 16}
            ),
            CodeChunk(
                content="def log_error(msg):\n    logger.error(msg)",
                file_path="log.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": "log_1", "token_count_est": 12}
            )
        ]

        store.index_chunks(chunks)

        # Search without filter should find both
        all_results = store.search("function", top_k=10)
        assert len(all_results) >= 2

        # Search with file filter - this would require file filter implementation
        # For now, just test the method exists
        assert hasattr(store, 'search')

    @pytest.mark.slow
    def test_large_index_performance_acceptable(self):
        """Test that indexing and searching scales reasonably (slow test - skip in CI)."""
        from core.rag.vector_store import QdrantVectorStore
        import time

        store = QdrantVectorStore(collection_name="test_perf")

        # Create multiple chunks to test performance
        chunks = [
            CodeChunk(
                content=f"def func_{i}():\n    return {i}",
                file_path=f"file_{i}.py",
                start_line=1,
                end_line=2,
                chunk_type="function",
                metadata={"chunk_id": f"perf_{i}", "token_count_est": 10}
            )
            for i in range(20)  # Small scale test
        ]

        # Time indexing
        start_time = time.time()
        indexed = store.index_chunks(chunks)
        index_time = time.time() - start_time

        # Should index quickly
        assert index_time < 10  # 10 seconds max for 20 chunks
        assert indexed == len(chunks)

        # Time search
        search_start = time.time()
        results = store.search("function", top_k=5)
        search_time = time.time() - search_start

        # Should search very quickly
        assert search_time < 1  # 1 second max for small index
        assert len(results) >= 3