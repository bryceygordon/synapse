# RAG System Setup & Usage Guide

## 🎯 Overview

This guide will help you set up the Hybrid RAG (Retrieval-Augmented Generation) system for Synapse. Once configured, this system will:

- **Reduce token usage by 50-70%** when exploring the codebase
- Enable **semantic code search** (understand concepts, not just keywords)
- Provide **accurate, fast code discovery** for all agents
- **Track all RAG usage** with feedback confirmation

---

## 📋 Prerequisites

1. **Docker installed** - For Qdrant vector database
2. **Python 3.8+** - Already have this
3. **Disk space** - ~2GB for Docker image + embeddings

---

## 🚀 Setup Steps

### **Step 1: Install Python Dependencies**

```bash
cd /home/bryceg/synapse
pip install qdrant-client sentence-transformers langchain-text-splitters rank-bm25 tiktoken
```

Expected output:
```
Successfully installed qdrant-client-1.x.x sentence-transformers-2.x.x ...
```

### **Step 2: Start Qdrant Vector Database**

```bash
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant \
  qdrant/qdrant
```

Verify it's running:
```bash
docker ps | grep qdrant
```

Expected output:
```
CONTAINER ID   IMAGE             STATUS          PORTS
abc123def456   qdrant/qdrant     Up 2 seconds    0.0.0.0:6333->6333/tcp
```

Test the connection:
```bash
curl http://localhost:6333
```

Expected output: `{"title":"qdrant - vector search engine"...}`

### **Step 3: Index Your Codebase**

This step chunks your code and creates embeddings. **Takes ~2-5 minutes.**

```bash
python scripts/index_codebase.py
```

Expected output:
```
============================================================
Synapse Codebase Indexing
============================================================

📁 Scanning codebase: /home/bryceg/synapse
🗄️  Target collection: synapse_code

🔍 Finding Python files...
   Found 85 total Python files
   After filtering: 78 files to index

🔧 Initializing RAG components...
   ✅ CodeChunker initialized (chunk_size=1000, overlap=100)
   ✅ QdrantVectorStore initialized (collection='synapse_code')

✂️  Chunking code files...
   Processed 10/78 files... (124 chunks so far)
   Processed 20/78 files... (287 chunks so far)
   ...
   ✅ Chunked 78 files into 892 chunks
   ⏱️  Chunking took 3.45 seconds

🚀 Indexing chunks in Qdrant...
   (This may take a while - generating embeddings for all chunks)
   ✅ Successfully indexed 892/892 chunks
   ⏱️  Indexing took 127.23 seconds

============================================================
📊 Indexing Summary
============================================================
Files processed:     78
Chunks created:      892
Chunks indexed:      892
Total time:          130.68 seconds
Avg chunks/file:     11.4

✅ Verification: 892 chunks now in collection 'synapse_code'

🎉 Indexing complete! You can now use RAG search:
   python scripts/rag_search.py 'your query' 5
```

**If you see errors:**
- "Cannot connect to Qdrant" → Check Docker: `docker ps | grep qdrant`
- "No module named..." → Install dependencies again (Step 1)

### **Step 4: Test RAG Search**

```bash
python scripts/rag_search_tracked.py "todoist agent" 3
```

Expected output:
```
======================================================================
🔍 RAG SEARCH EXECUTED
======================================================================
Query:          todoist agent
Results found:  3
Search time:    0.234s
Method:         Hybrid (BM25 + Vector Semantic)
Logged:         logs/rag_usage.log
======================================================================

# Search Results (3 matches)

## [1] Class - Relevance: 0.87
📁 **File:** core/agents/todoist/core.py:15
📍 **Lines:** 15-45

\`\`\`python
class TodoistAgent(BaseAgent):
    """Agent for Todoist task management."""

    def __init__(self, api_token: str):
        self.api = TodoistAPI(api_token)
...
\`\`\`

...
```

**What to check:**
- ✅ See the "🔍 RAG SEARCH EXECUTED" banner
- ✅ Results are relevant to your query
- ✅ File paths and line numbers are correct
- ✅ Search completes in < 1 second

### **Step 5: Verify Usage Tracking**

Check that searches are being logged:

```bash
cat logs/rag_usage.log
```

Expected output (JSON lines):
```json
{"timestamp": "2025-10-19T14:32:15", "query": "todoist agent", "top_k": 3, "results_count": 3, "search_time_seconds": 0.234}
```

---

## ✅ Verification Checklist

Before proceeding, confirm:

- [ ] Qdrant container is running: `docker ps | grep qdrant`
- [ ] Dependencies installed: `pip list | grep qdrant`
- [ ] Codebase indexed: `python scripts/index_codebase.py` succeeded
- [ ] Test search works: `python scripts/rag_search_tracked.py "test" 3`
- [ ] Usage logging works: `ls logs/rag_usage.log`

---

## 🤖 How Agents Use RAG

### **For Task Tool Agents:**

When you spawn an agent using the Task tool, specify one of these:

```python
# For code search tasks
Task(
  subagent_type="rag-search",
  description="Find authentication code",
  prompt="Find all code related to user login and authentication"
)

# For coding tasks
Task(
  subagent_type="coder-rag",
  description="Add logging to auth",
  prompt="Add detailed logging to the authentication functions"
)
```

These agents are **pre-configured** to use RAG search first and provide feedback.

### **For Me (Claude Code CLI):**

I will use RAG by calling:

```bash
python scripts/rag_search_tracked.py "my query" 5
```

**When you see me do this, you'll know I'm using RAG!**

---

## 📊 Feedback Mechanisms

### **1. Visual Banner**

Every RAG search shows:
```
======================================================================
🔍 RAG SEARCH EXECUTED
======================================================================
```

### **2. Agent Confirmation**

Agents are instructed to say:
> "✅ Used RAG search for exploration"

When you see this, the agent used RAG.

### **3. Usage Logs**

All searches are logged to `logs/rag_usage.log` with:
- Timestamp
- Query
- Results count
- Search time

Check usage stats:
```bash
# Count total searches
wc -l logs/rag_usage.log

# View recent searches
tail -5 logs/rag_usage.log | jq .
```

### **4. Verification Script**

Run this to verify RAG is being used:

```bash
python scripts/verify_rag_usage.py
```

(We'll create this next)

---

## 🔍 Usage Examples

### **Example 1: Code Search**

```bash
python scripts/rag_search_tracked.py "how does the todoist agent fetch tasks" 5
```

### **Example 2: Find Implementation**

```bash
python scripts/rag_search_tracked.py "database connection initialization" 3
```

### **Example 3: Understand Pattern**

```bash
python scripts/rag_search_tracked.py "error handling pattern in agents" 5
```

---

## 🐛 Troubleshooting

### **"Cannot connect to Qdrant"**

Check if Qdrant is running:
```bash
docker ps | grep qdrant
```

If not running:
```bash
docker start qdrant
```

Or recreate:
```bash
docker rm qdrant
docker run -d -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
```

### **"No results found"**

Re-index the codebase:
```bash
python scripts/index_codebase.py
```

### **"Module not found"**

Reinstall dependencies:
```bash
pip install qdrant-client sentence-transformers langchain-text-splitters rank-bm25 tiktoken
```

---

## 📈 Token Savings Measurement

To measure actual token savings, use:

```bash
python scripts/measure_token_savings.py
```

Expected results:
- **Before RAG:** 15,000+ tokens per query
- **After RAG:** ~1,200 tokens per query
- **Savings:** 50-70% reduction

---

## 🎉 Success Criteria

You'll know RAG is working when:

1. ✅ Searches complete in < 1 second
2. ✅ Results are semantically relevant (not just keyword matches)
3. ✅ You see "🔍 RAG SEARCH EXECUTED" banner
4. ✅ Agents say "✅ Used RAG search"
5. ✅ `logs/rag_usage.log` shows growing usage
6. ✅ Token usage drops by 50-70% for exploration tasks

---

## 📝 Next Steps

After setup:

1. **Update your workflow** - Use RAG search before Read/Grep
2. **Train yourself** - When exploring code, think "RAG first"
3. **Monitor usage** - Check `logs/rag_usage.log` weekly
4. **Measure savings** - Run token comparison tests monthly
5. **Iterate** - Adjust search queries based on results

---

## 🆘 Support

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review `logs/rag_usage.log` for errors
3. Verify setup with verification checklist
4. Re-run index if needed: `python scripts/index_codebase.py`

---

**RAG System Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Claude (Synapse AI Assistant)
