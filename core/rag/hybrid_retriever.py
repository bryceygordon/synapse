"""Hybrid retrieval combining BM25 keyword search and vector semantic search."""

import logging
from typing import List, Dict, Any
from core.rag.chunking import CodeChunk
from core.rag.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class BM25Retriever:
    """Keyword-based retriever using BM25 scoring for exact identifier matching."""

    def __init__(self, vector_store: QdrantVectorStore):
        """Initialize BM25 retriever.

        Args:
            vector_store: QdrantVectorStore instance to access indexed data
        """
        self.vector_store = vector_store
        self.index = None
        self._build_index()

    def _build_index(self):
        """Build BM25 index from vector store documents."""
        try:
            from rank_bm25 import BM25Okapi

            # Get all points from vector store to build BM25 index
            # This is simplified - in practice might need pagination for large collections
            all_points = self.vector_store.client.scroll(
                collection_name=self.vector_store.collection_name,
                limit=10000,  # Reasonable limit, can be increased if needed
                with_payload=True,
                with_vectors=False
            )[0]  # scroll returns (points, next_page_offset)

            if not all_points:
                logger.warning("No documents found for BM25 index")
                self.index = BM25Okapi([["empty"]])  # Empty index
                return

            # Extract searchable text from payloads
            corpus = []
            self.doc_ids = []

            for point in all_points:
                payload = point.payload
                searchable_text = payload.get('searchable_text', '')
                if searchable_text:
                    # Tokenize: split on spaces and filter out short words
                    tokens = [word.lower() for word in searchable_text.split()
                            if len(word) >= 2 and word.isalnum()]
                    corpus.append(tokens)
                    self.doc_ids.append(point.id)
                else:
                    # Fallback: tokenize content
                    content = payload.get('content', '')
                    tokens = [word.lower() for word in content.split()[:50]  # Limit to avoid huge tokens
                            if len(word) >= 2 and word.isalnum()]
                    corpus.append(tokens)
                    self.doc_ids.append(point.id)

            # Build BM25 index
            self.index = BM25Okapi(corpus)
            logger.info(f"Built BM25 index with {len(corpus)} documents")

        except ImportError:
            logger.error("rank_bm25 not installed. BM25 search will not work.")
            self.index = None
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {e}")
            self.index = None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using BM25 keyword matching.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results with BM25 scores
        """
        if not self.index or not hasattr(self.index, 'get_scores'):
            logger.warning("BM25 index not available")
            return []

        try:
            # Tokenize query same way as corpus
            query_tokens = [word.lower() for word in query.split()
                          if len(word) >= 2 and word.isalnum()]

            if not query_tokens:
                return []

            # Get BM25 scores
            scores = self.index.get_scores(query_tokens)

            # Get top results
            top_indices = scores.argsort()[-top_k:][::-1]  # Sort desc, take top_k
            top_scores = scores[top_indices]

            results = []
            for idx, score in zip(top_indices, top_scores):
                if score > 0:  # Only include results with some relevance
                    result = {
                        "id": self.doc_ids[idx],
                        "score": float(score),
                        "search_type": "bm25",
                        # Payload will be retrieved by hybrid method
                    }
                    results.append(result)

            logger.debug(f"BM25 search returned {len(results)} results for: '{query}'")
            return results

        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []


class HybridRetriever:
    """Combines BM25 keyword search and vector semantic search."""

    def __init__(self,
                 collection_name: str = "synapse_code",
                 alpha: float = 0.3):
        """Initialize hybrid retriever.

        Args:
            collection_name: Qdrant collection name
            alpha: Weight for vector search (0=all BM25, 1=all vector)
        """
        self.collection_name = collection_name
        self.alpha = alpha  # Partial weight for vector search

        # Initialize components
        self.vector_store = QdrantVectorStore(collection_name)
        self.bm25_retriever = BM25Retriever(self.vector_store)

        logger.info(f"Initialized hybrid retriever (BM25: {1-alpha:.1f}, Vector: {alpha:.1f})")

    def index_chunks(self, chunks: List[CodeChunk]) -> int:
        """Index chunks in both BM25 and vector stores."""
        # Vector store indexing
        vector_count = self.vector_store.index_chunks(chunks)

        # BM25 index is built automatically in BM25Retriever init
        # But we need to rebuild it after new chunks
        self.bm25_retriever._build_index()

        return vector_count

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining BM25 and vector similarity.

        Algorithm:
        1. Get BM25 results (keyword exact matches)
        2. Get vector results (semantic similarity)
        3. Fuse scores: score = (1-alpha) * bm25_score + alpha * vector_score
        4. Return top_k by fused score
        """
        try:
            # Overfetch candidates (3x requested) for better fusion
            overfetch_k = top_k * 3

            # Get BM25 results
            bm25_results = self.bm25_retriever.search(query, overfetch_k)

            # Get vector results
            vector_results = self.vector_store.search(query, overfetch_k)

            # Fuse scores using reciprocal rank fusion as approximation
            # Simple linear combination: score = (1-alpha) * bm25_score + alpha * vector_score
            fused_results = self._fuse_scores(bm25_results, vector_results, self.alpha)

            # Sort by fused score and take top_k
            fused_results.sort(key=lambda x: x['score'], reverse=True)
            final_results = fused_results[:top_k]

            # --- FINAL FIX ---
            # For any results that were BM25-only, their payload might be missing.
            # Retrieve them now.
            ids_to_fetch = [r['id'] for r in final_results if 'payload' not in r or r['payload'] is None]
            if ids_to_fetch:
                try:
                    points = self.vector_store.client.retrieve(
                        collection_name=self.collection_name,
                        ids=ids_to_fetch,
                        with_payload=True,
                        with_vectors=False
                    )
                    payloads_by_id = {point.id: point.payload for point in points}
                    for result in final_results:
                        if result['id'] in payloads_by_id:
                            result['payload'] = payloads_by_id[result['id']]
                except Exception as e:
                    logger.warning(f"Failed to retrieve some payloads: {e}")
            # --- END FINAL FIX ---


            logger.debug(f"Hybrid search returned {len(final_results)} results")
            return final_results

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    def _fuse_scores(self,
                    bm25_results: List[Dict[str, Any]],
                    vector_results: List[Dict[str, Any]],
                    alpha: float) -> List[Dict[str, Any]]:
        """Fuse BM25 and vector search scores.

        Args:
            bm25_results: Results from BM25 search
            vector_results: Results from vector search
            alpha: Weight for vector scores (0=all BM25, 1=all vector)

        Returns:
            Results with fused scores
        """
        # Normalize scores to 0-1 range before fusion
        def normalize_scores(results):
            if not results:
                return results

            scores = [r['score'] for r in results]
            min_score, max_score = min(scores), max(scores)

            if max_score == min_score:
                # All same score, set to 1.0
                for r in results:
                    r['normalized_score'] = 1.0
            else:
                # Linear normalization to 0-1
                for r in results:
                    r['normalized_score'] = (r['score'] - min_score) / (max_score - min_score)

            return results

        # Normalize both result sets
        bm25_normalized = normalize_scores(bm25_results.copy())
        vector_normalized = normalize_scores(vector_results.copy())

        # Create lookup by document ID
        bm25_lookup = {r['id']: r for r in bm25_normalized}
        vector_lookup = {r['id']: r for r in vector_normalized}

        # Fuse scores for all unique documents
        fused_results = []

        # Add all BM25 results
        for result in bm25_normalized:
            doc_id = result['id']
            bm25_score = result['normalized_score']
            vector_score = vector_lookup.get(doc_id, {}).get('normalized_score', 0.0)

            fused_score = (1 - alpha) * bm25_score + alpha * vector_score

            fused_result = result.copy()
            fused_result['score'] = fused_score
            fused_result['bm25_score'] = bm25_score
            fused_result['vector_score'] = vector_score
            fused_result['search_type'] = 'hybrid'

            # --- BUG FIX ---
            # Ensure payload from vector search is preserved
            if 'payload' not in fused_result and doc_id in vector_lookup:
                fused_result['payload'] = vector_lookup[doc_id].get('payload')
            # --- END BUG FIX ---

            fused_results.append(fused_result)

        # Add vector-only results (not in BM25)
        for result in vector_normalized:
            doc_id = result['id']
            if doc_id not in bm25_lookup:
                bm25_score = 0.0
                vector_score = result['normalized_score']

                fused_score = (1 - alpha) * bm25_score + alpha * vector_score

                fused_result = result.copy()
                fused_result['score'] = fused_score
                fused_result['bm25_score'] = bm25_score
                fused_result['vector_score'] = vector_score
                fused_result['search_type'] = 'hybrid'
                fused_results.append(fused_result)

        return fused_results