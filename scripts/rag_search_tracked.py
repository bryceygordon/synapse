#!/usr/bin/env python3
"""RAG search with usage tracking and feedback.

This wrapper around rag_search.py:
1. Logs every search query with timestamp
2. Provides clear feedback that RAG was used
3. Tracks usage statistics

Usage:
    python scripts/rag_search_tracked.py "search query" [top_k]

The usage log is stored at: logs/rag_usage.log
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.rag.hybrid_retriever import HybridRetriever


def log_usage(query: str, top_k: int, results_count: int, search_time: float):
    """Log RAG usage to file for tracking."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "rag_usage.log"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "top_k": top_k,
        "results_count": results_count,
        "search_time_seconds": round(search_time, 3)
    }

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def print_rag_feedback(query: str, results_count: int, search_time: float):
    """Print clear feedback that RAG was used."""
    print("=" * 70)
    print("🔍 RAG SEARCH EXECUTED")
    print("=" * 70)
    print(f"Query:          {query}")
    print(f"Results found:  {results_count}")
    print(f"Search time:    {search_time:.3f}s")
    print(f"Method:         Hybrid (BM25 + Vector Semantic)")
    print(f"Logged:         logs/rag_usage.log")
    print("=" * 70)
    print()


def format_results(query: str, results: list) -> str:
    """Format search results."""
    if not results:
        return f"No results found for query: '{query}'\n"

    output_lines = [
        f"# Search Results ({len(results)} matches)",
        ""
    ]

    for i, result in enumerate(results, 1):
        payload = result.get('payload', {})
        score = result.get('score', 0.0)

        file_path = payload.get('file_path', 'unknown')
        start_line = payload.get('start_line', '?')
        end_line = payload.get('end_line', '?')
        chunk_type = payload.get('chunk_type', 'code').title()
        content = payload.get('content', '')

        output_lines.extend([
            f"## [{i}] {chunk_type} - Relevance: {score:.2f}",
            f"📁 **File:** {file_path}:{start_line}",
            f"📍 **Lines:** {start_line}-{end_line}",
            "",
            "```python",
            content,
            "```",
            ""
        ])

    return "\n".join(output_lines)


def main():
    """Main CLI entry point with tracking."""
    import time

    if len(sys.argv) < 2:
        print("Usage: python scripts/rag_search_tracked.py 'your search query' [top_k]")
        print("\nThis is the TRACKED version that logs all usage.")
        print("Use this to ensure RAG is being utilized.")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    try:
        # Initialize RAG retriever
        retriever = HybridRetriever(
            collection_name="synapse_code",
            alpha=0.3
        )

        # Perform search with timing
        search_start = time.time()
        results = retriever.search(query, top_k=top_k)
        search_time = time.time() - search_start

        # Log usage
        log_usage(query, top_k, len(results), search_time)

        # Print feedback FIRST (so user knows RAG was used)
        print_rag_feedback(query, len(results), search_time)

        # Print results
        formatted_output = format_results(query, results)
        print(formatted_output)

    except ConnectionError as e:
        print("❌ ERROR: Cannot connect to Qdrant vector database.", file=sys.stderr)
        print("Make sure Qdrant is running: docker run -d -p 6333:6333 qdrant/qdrant", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ ERROR: Search failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
