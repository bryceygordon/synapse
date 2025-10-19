# RAG Quick Start - 5 Minutes to Token Savings

## ⚡ Fast Track Setup

```bash
# 1. Install dependencies (30 seconds)
pip install qdrant-client sentence-transformers langchain-text-splitters rank-bm25 tiktoken

# 2. Start Qdrant (10 seconds)
docker run -d -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# 3. Index codebase (2-5 minutes)
python scripts/index_codebase.py

# 4. Test it works (5 seconds)
python scripts/rag_search_tracked.py "todoist agent" 3

# 5. Verify setup (5 seconds)
python scripts/verify_rag_usage.py
```

**Total time:** ~5 minutes

---

## 🔍 How to Know I'm Using RAG

### Look for this in my responses:

> ✅ **RAG Search Used**
> Query: `my search query`
> Results: 5
> Files: `core/agents/todoist.py:45`, `core/agents/base.py:12`

### Or this in the terminal output:

```
======================================================================
🔍 RAG SEARCH EXECUTED
======================================================================
Query:          my search query
Results found:  5
Search time:    0.234s
Method:         Hybrid (BM25 + Vector Semantic)
Logged:         logs/rag_usage.log
======================================================================
```

---

## 📊 Monitor Usage

```bash
# Quick check
cat logs/rag_usage.log | tail -5

# Full verification
python scripts/verify_rag_usage.py
```

---

## 🎯 Expected Results

**Before RAG:**
- Query: "How does X work?"
- Tokens: 15,000+

**After RAG:**
- Same query
- Tokens: ~1,200
- **Savings: 50-70%**

---

## 🆘 Problems?

```bash
# Qdrant not running?
docker ps | grep qdrant

# Not indexed?
python scripts/index_codebase.py

# Still broken?
python scripts/verify_rag_usage.py
```

---

## 📚 Full Docs

- **Setup:** `RAG_SETUP_GUIDE.md`
- **Summary:** `RAG_IMPLEMENTATION_COMPLETE.md`
- **Troubleshooting:** Both guides above

---

**🚀 Run the 5 commands above and you're done!**
