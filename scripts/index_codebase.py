#!/usr/bin/env python3
"""Index the Synapse codebase into Qdrant vector database.

This script:
1. Finds all Python files in the project
2. Chunks them using language-aware chunking (preserves function/class boundaries)
3. Generates embeddings using sentence-transformers
4. Stores chunks and embeddings in Qdrant for hybrid search

Usage:
    python scripts/index_codebase.py

Requirements:
    - Qdrant running on localhost:6333
    - Dependencies installed: qdrant-client, sentence-transformers, langchain-text-splitters
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.rag.chunking import CodeChunker
from core.rag.vector_store import QdrantVectorStore


def main():
    """Index the entire Synapse codebase."""
    print("=" * 60)
    print("Synapse Codebase Indexing")
    print("=" * 60)
    print()

    # Configuration
    codebase_root = Path("/home/bryceg/synapse")
    collection_name = "synapse_code"

    # Paths to exclude
    exclude_patterns = [
        '__pycache__',
        '.venv',
        'venv',
        '.git',
        'qdrant_storage',
        '.pytest_cache',
        'node_modules',
        '.claude'
    ]

    print(f"📁 Scanning codebase: {codebase_root}")
    print(f"🗄️  Target collection: {collection_name}")
    print()

    # Find all Python files
    print("🔍 Finding Python files...")
    all_python_files = list(codebase_root.rglob("*.py"))

    # Filter out excluded paths
    python_files = [
        f for f in all_python_files
        if not any(pattern in str(f) for pattern in exclude_patterns)
    ]

    print(f"   Found {len(all_python_files)} total Python files")
    print(f"   After filtering: {len(python_files)} files to index")
    print()

    if not python_files:
        print("❌ No Python files found to index!")
        sys.exit(1)

    # Initialize components
    print("🔧 Initializing RAG components...")
    try:
        chunker = CodeChunker(
            language="python",
            chunk_size=1000,
            chunk_overlap=100
        )
        print("   ✅ CodeChunker initialized (chunk_size=1000, overlap=100)")

        vector_store = QdrantVectorStore(
            collection_name=collection_name,
            embedding_model="all-MiniLM-L6-v2",  # Explicitly use smaller model
            host="localhost",
            port=6333
        )
        print(f"   ✅ QdrantVectorStore initialized (collection='{collection_name}')")
    except Exception as e:
        print(f"\n❌ Failed to initialize components: {e}")
        print("\nMake sure:")
        print("  1. Qdrant is running: docker ps | grep qdrant")
        print("  2. Dependencies installed: pip list | grep -E '(qdrant|sentence)'")
        sys.exit(1)

    print()

    # Chunk all files
    print("✂️  Chunking code files...")
    all_chunks = []
    failed_files = []

    start_time = time.time()

    for i, file_path in enumerate(python_files, 1):
        try:
            chunks = chunker.chunk_file(str(file_path))
            all_chunks.extend(chunks)

            # Progress indicator every 10 files
            if i % 10 == 0:
                print(f"   Processed {i}/{len(python_files)} files... ({len(all_chunks)} chunks so far)")

        except Exception as e:
            failed_files.append((str(file_path), str(e)))
            continue

    chunk_time = time.time() - start_time

    print(f"   ✅ Chunked {len(python_files)} files into {len(all_chunks)} chunks")
    print(f"   ⏱️  Chunking took {chunk_time:.2f} seconds")

    if failed_files:
        print(f"   ⚠️  Failed to chunk {len(failed_files)} files:")
        for file_path, error in failed_files[:5]:  # Show first 5
            print(f"      - {file_path}: {error}")

    print()

    # Index chunks
    print("🚀 Indexing chunks in Qdrant...")
    print("   (This may take a while - generating embeddings for all chunks)")

    index_start = time.time()

    try:
        indexed_count = vector_store.index_chunks(all_chunks)
        index_time = time.time() - index_start

        print(f"   ✅ Successfully indexed {indexed_count}/{len(all_chunks)} chunks")
        print(f"   ⏱️  Indexing took {index_time:.2f} seconds")
        print()

        # Summary statistics
        print("=" * 60)
        print("📊 Indexing Summary")
        print("=" * 60)
        print(f"Files processed:     {len(python_files)}")
        print(f"Chunks created:      {len(all_chunks)}")
        print(f"Chunks indexed:      {indexed_count}")
        print(f"Total time:          {chunk_time + index_time:.2f} seconds")
        print(f"Avg chunks/file:     {len(all_chunks) / len(python_files):.1f}")
        print()

        # Verify index
        total_in_db = vector_store.get_chunk_count()
        print(f"✅ Verification: {total_in_db} chunks now in collection '{collection_name}'")
        print()
        print("🎉 Indexing complete! You can now use RAG search:")
        print(f"   python scripts/rag_search.py 'your query' 5")

    except Exception as e:
        print(f"\n❌ Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
