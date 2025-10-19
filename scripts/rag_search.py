#!/usr/bin/env python3
"""CLI wrapper for RAG code search - callable by Claude Code and other tools.

Usage:
    python scripts/rag_search.py "search query" [top_k]

Examples:
    python scripts/rag_search.py "how does authentication work" 3
    python scripts/rag_search.py "find all database models" 5

Requirements:
    - Qdrant running on localhost:6333
    - Codebase indexed (run scripts/index_codebase.py first)
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.rag.hybrid_retriever import HybridRetriever

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def format_results(query: str, results: list) -> str:
    """Format search results in a human-readable format."""
    if not results:
        return f"No results found for query: '{query}'\n"

    output_lines = [
        f"# Code Search Results: '{query}'",
        f"Found {len(results)} relevant code chunks\n"
    ]

    for i, result in enumerate(results, 1):
        payload = result.get('payload', {})
        score = result.get('score', 0.0)

        # Extract metadata
        file_path = payload.get('file_path', 'unknown')
        start_line = payload.get('start_line', '?')
        end_line = payload.get('end_line', '?')
        chunk_type = payload.get('chunk_type', 'code').title()
        content = payload.get('content', '')

        # Format result
        output_lines.extend([
            f"## Result {i}: {chunk_type} (relevance: {score:.2f})",
            f"**File:** {file_path}:{start_line}",
            f"**Lines:** {start_line}-{end_line}",
            "",
            "```python",
            content,
            "```",
            ""
        ])

    return "\n".join(output_lines)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/rag_search.py 'your search query' [top_k]")
        print("\nExamples:")
        print("  python scripts/rag_search.py 'authentication' 3")
        print("  python scripts/rag_search.py 'how does the todoist agent work' 5")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    try:
        # Initialize RAG retriever
        logger.info("Initializing RAG retriever...")
        retriever = HybridRetriever(
            collection_name="synapse_code",
            alpha=0.3  # 70% keyword (BM25), 30% semantic (vector)
        )

        # Perform search
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        results = retriever.search(query, top_k=top_k)

        # Format and print results
        formatted_output = format_results(query, results)
        print(formatted_output)

    except ConnectionError as e:
        print("ERROR: Cannot connect to Qdrant vector database.", file=sys.stderr)
        print("Make sure Qdrant is running: docker run -d -p 6333:6333 qdrant/qdrant", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Search failed: {e}", file=sys.stderr)
        logger.exception("Search failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
