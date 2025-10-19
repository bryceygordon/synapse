#!/usr/bin/env python3
"""Verify RAG system is properly configured and being used.

This script checks:
1. Qdrant is running and accessible
2. Codebase is indexed
3. RAG search works correctly
4. Usage is being logged
5. Recent usage statistics

Usage:
    python scripts/verify_rag_usage.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_qdrant_running():
    """Check if Qdrant is running and accessible."""
    print("1️⃣  Checking Qdrant vector database...")
    try:
        response = requests.get("http://localhost:6333", timeout=5)
        if response.status_code == 200:
            print("   ✅ Qdrant is running on localhost:6333")
            return True
        else:
            print(f"   ❌ Qdrant returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Qdrant on localhost:6333")
        print("      Start with: docker run -d -p 6333:6333 --name qdrant qdrant/qdrant")
        return False
    except Exception as e:
        print(f"   ❌ Error checking Qdrant: {e}")
        return False


def check_collection_indexed():
    """Check if codebase is indexed in Qdrant."""
    print("\n2️⃣  Checking if codebase is indexed...")
    try:
        from core.rag.vector_store import QdrantVectorStore

        vector_store = QdrantVectorStore(collection_name="synapse_code")
        count = vector_store.get_chunk_count()

        if count > 0:
            print(f"   ✅ Found {count} code chunks indexed")
            return True
        else:
            print("   ❌ Collection is empty - no chunks indexed")
            print("      Run: python scripts/index_codebase.py")
            return False

    except Exception as e:
        print(f"   ❌ Error checking index: {e}")
        print("      Make sure dependencies are installed and Qdrant is running")
        return False


def check_rag_search_works():
    """Test that RAG search actually works."""
    print("\n3️⃣  Testing RAG search functionality...")
    try:
        from core.rag.hybrid_retriever import HybridRetriever

        retriever = HybridRetriever(collection_name="synapse_code", alpha=0.3)
        results = retriever.search("agent", top_k=3)

        if results and len(results) > 0:
            print(f"   ✅ RAG search works! Found {len(results)} results for test query 'agent'")
            return True
        else:
            print("   ⚠️  RAG search returned no results")
            print("      This might indicate the index is empty or corrupted")
            return False

    except Exception as e:
        print(f"   ❌ RAG search failed: {e}")
        return False


def check_usage_logging():
    """Check if usage logging is working."""
    print("\n4️⃣  Checking usage logging...")
    log_file = project_root / "logs" / "rag_usage.log"

    if not log_file.exists():
        print("   ⚠️  No usage log found yet (logs/rag_usage.log)")
        print("      This is normal if you haven't run any tracked searches")
        print("      Test with: python scripts/rag_search_tracked.py 'test' 3")
        return False

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        if len(lines) == 0:
            print("   ⚠️  Usage log exists but is empty")
            return False

        # Parse last entry
        last_entry = json.loads(lines[-1])
        timestamp = datetime.fromisoformat(last_entry['timestamp'])

        print(f"   ✅ Usage logging works! Found {len(lines)} logged searches")
        print(f"      Last search: '{last_entry['query']}' at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    except Exception as e:
        print(f"   ❌ Error reading usage log: {e}")
        return False


def show_usage_stats():
    """Show recent usage statistics."""
    print("\n5️⃣  Usage statistics (last 24 hours)...")
    log_file = project_root / "logs" / "rag_usage.log"

    if not log_file.exists():
        print("   No usage data yet")
        return

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        # Filter to last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        recent_searches = []

        for line in lines:
            try:
                entry = json.loads(line)
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if timestamp > cutoff:
                    recent_searches.append(entry)
            except:
                continue

        if not recent_searches:
            print("   No searches in last 24 hours")
            print(f"   Total all-time: {len(lines)} searches")
            return

        # Calculate stats
        total_searches = len(recent_searches)
        total_results = sum(s['results_count'] for s in recent_searches)
        avg_time = sum(s['search_time_seconds'] for s in recent_searches) / total_searches

        print(f"   📊 Last 24 hours:")
        print(f"      - Searches: {total_searches}")
        print(f"      - Total results: {total_results}")
        print(f"      - Avg search time: {avg_time:.3f}s")
        print(f"\n   🔍 Recent queries:")

        for entry in recent_searches[-5:]:  # Show last 5
            timestamp = datetime.fromisoformat(entry['timestamp'])
            time_str = timestamp.strftime("%H:%M:%S")
            print(f"      - [{time_str}] '{entry['query']}' → {entry['results_count']} results")

        print(f"\n   📈 All-time total: {len(lines)} searches")

    except Exception as e:
        print(f"   ❌ Error calculating stats: {e}")


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("🔍 RAG System Verification")
    print("=" * 70)
    print()

    checks = {
        "Qdrant running": check_qdrant_running(),
        "Codebase indexed": check_collection_indexed(),
        "RAG search works": check_rag_search_works(),
        "Usage logging": check_usage_logging(),
    }

    # Show statistics
    show_usage_stats()

    # Summary
    print("\n" + "=" * 70)
    print("📋 Verification Summary")
    print("=" * 70)

    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} - {check_name}")

    print()

    all_passed = all(checks.values())

    if all_passed:
        print("🎉 All checks passed! RAG system is fully operational.")
        print("\nYou can now use RAG search:")
        print("  python scripts/rag_search_tracked.py 'your query' 5")
        return 0
    else:
        print("⚠️  Some checks failed. Review errors above and fix issues.")
        print("\nSee RAG_SETUP_GUIDE.md for troubleshooting steps.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
