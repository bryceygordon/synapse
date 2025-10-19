"""Vector database interface for code embeddings and semantic search."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, SearchRequest
from sentence_transformers import SentenceTransformer
from core.rag.chunking import CodeChunk

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Qdrant vector database interface with embedding capabilities.

    Handles:
    - Embedding generation using sentence-transformers
    - Storing code chunks in Qdrant for semantic search
    - Searching by semantic similarity
    """

    def __init__(self,
                 collection_name: str = "synapse_code",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 host: str = "localhost",
                 port: int = 6333):
        """Initialize vector store with Qdrant client and embedding model.

        Args:
            collection_name: Name of Qdrant collection
            embedding_model: SentenceTransformer model name
            host: Qdrant server host
            port: Qdrant server port
        """
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        # Initialize Qdrant client
        self.client = QdrantClient(host=host, port=port)

        # Initialize embedding model
        try:
            self.embedder = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.warning(f"Failed to load {embedding_model}: {e}")
            # Fallback to smaller model
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Fallback to all-MiniLM-L6-v2")

        # Ensure collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist with proper vector configuration."""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception:
            # Create collection
            vector_size = len(self.embedder.encode("test"))  # Get embedding dimension

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE  # Cosine similarity for semantic search
                )
            )
            logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedder.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return zero vectors as fallback (will be filtered out)
            return [[0.0] * self.embedder.get_sentence_embedding_dimension()] * len(texts)

    def index_chunks(self, chunks: List[CodeChunk]) -> int:
        """Index code chunks in the vector database.

        Args:
            chunks: List of CodeChunk objects to index

        Returns:
            Number of chunks successfully indexed
        """
        if not chunks:
            return 0

        # Extract texts for embedding
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts)

        # Create Qdrant points
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Skip failed embeddings (all zeros)
            if all(v == 0.0 for v in embedding):
                continue

            point = PointStruct(
                id=i,  # Simple incremental ID
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "metadata": chunk.metadata,
                    "searchable_text": chunk.content.lower()  # For BM25 hybrid search
                }
            )
            points.append(point)

        if points:
            # Upsert in batches of 100
            batch_size = 100
            total_indexed = 0
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                try:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=batch
                    )
                    total_indexed += len(batch)
                    logger.debug(f"Indexed batch of {len(batch)} chunks")
                except Exception as e:
                    logger.error(f"Failed to index batch {i//batch_size}: {e}")

            logger.info(f"Successfully indexed {total_indexed} chunks")
            return total_indexed
        else:
            logger.warning("No chunks to index (all embeddings failed)")
            return 0

    def search(self, query: str, top_k: int = 5, file_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for semantically similar code chunks.

        Args:
            query: Search query text
            top_k: Number of results to return
            file_filter: Optional file path filter (glob pattern)

        Returns:
            List of search results with scores and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode([query])[0].tolist()

            # Prepare search parameters
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_embedding,
                "limit": top_k,
                "with_payload": True,
                "with_vectors": False  # Don't return vectors
            }

            # Add file filter if specified
            if file_filter:
                # Convert glob to regex and filter
                import fnmatch
                # This is a simple implementation - could be enhanced
                search_params["payload_filter"] = lambda payload: fnmatch.fnmatch(payload.get("file_path", ""), file_filter)

            # Execute search
            search_results = self.client.search(**search_params)

            # Convert to our result format
            results = []
            for result in search_results:
                result_dict = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                results.append(result_dict)

            logger.debug(f"Semantic search returned {len(results)} results for query: '{query}'")
            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def get_chunk_count(self) -> int:
        """Get total number of chunks indexed."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception as e:
            logger.error(f"Failed to get chunk count: {e}")
            return 0

    def clear_collection(self):
        """Clear all chunks from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()  # Recreate empty
            logger.info(f"Cleared collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")