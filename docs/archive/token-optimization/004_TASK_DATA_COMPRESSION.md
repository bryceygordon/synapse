# Mini-Project 004: Task Data Compression
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 4,000 input + 2,000 output per task
**Estimated Cost**: $0.003 total (Haiku)
**Priority**: 🎯 CRITICAL (Phase 3: Immediate Wins - 2,300-4,600 tokens saved)
**Time**: 2-4 hours total (spread across 5 mini-tasks)
**Impact**: 15-30% additional savings (Req: ~$3.50 → $2.50 per 1000 interactions)

---

## Problem Statement

**Current Issue**: `list_tasks()` and `get_task()` return full Todoist API objects with redundant fields that consume excessive tokens with every AI interaction.

**Token Cost Analysis**:

**Current Task Format** (~150-200 tokens per task):
```json
{
  "id": "8193847562",
  "content": "Buy groceries",
  "project_id": "2203306141",
  "section_id": null,
  "completed": false,
  "priority": 1,
  "due": "2025-10-15",
  "labels": ["next", "errand"],
  "description": null,
  "url": "https://todoist.com/showTask?id=8193847562",
  "created_at": "2025-10-15T14:32:00.000000Z",
  "creator_id": "12345678",
  "assignee_id": null,
  "assigner_id": null,
  "is_completed": false,
  "comments_count": 0
}
```

**Total per Inbox processing** (46 tasks): **~7,000-9,000 tokens**

---

## Solution Overview

**Compress All Task Data** to minimal essential fields using abbreviated keys.

**Target Task Format** (~30-50 tokens per task):
```json
{
  "id": "8193847562",
  "txt": "Buy groceries",
  "lbl": ["next", "errand"],
  "p": 1,
  "due": "2025-10-15"
}
```

**Compression Rules**:
- ✅ Keep `id` (necessary for task references)
- ✅ Replace `content` → `txt` (essential task description)
- ✅ Replace `labels` → `lbl` (only if non-empty)
- ✅ Replace `priority` → `p` (only if > 1, since 1 is default)
- ✅ Keep `due` as short date string
- ❌ Remove `project_id`, `section_id`, `completed`, `description`, `url`, `created_at`, etc.

**Savings**: ~120 tokens per task × 46 inbox tasks = **~5,500 tokens saved per inbox processing**

---

## Key Field Meaning (Update System Prompt)

**Add to system prompt**:
```yaml
TASK DATA FORMAT (compressed for token efficiency):
Tasks returned use abbreviated keys:
- txt: content/task description
- lbl: labels (only included if task has labels)
- p: priority (only included if > 1)
- due: due date as YYYY-MM-DD string
- crt: created date as YYYY-MM-DD string (rarely included)
- prj: project name (only for cross-project tasks)
```

---

## Implementation Strategy

### 1. Core Compression Method (`core.py`)
Add `_compress_task(task)` method that converts Todoist Task objects to compressed format.

### 2. Update Task Methods
- `list_tasks()`: Use `_compress_task()` when building task_list
- `get_task()`: Use `_compress_task()` for task_data
- `create_task()`: Return compressed version of created task
- `update_task()`: Return compressed version of updated task

### 3. Backward Compatibility
- LLM learns abbreviated keys via system prompt
- All essential information preserved (ID, content, labels, priority, due date)
- Optional fields (description, URL) accessible via separate `get_task()` calls if needed

---

## Mini-Tasks Breakdown

### Mini-Task 1: Implement Core Compression (30 min, $0.003)
- Add `_compress_task()` method to `core.py`
- Implement abbreviated field mapping
- Ensure all essential data preserved

### Mini-Task 2: Update list_tasks() (25 min, $0.002)
- Modify `list_tasks()` in `task_management.py`
- Use `_compress_task()` for all task output
- Keep existing filtering logic

### Mini-Task 3: Update get_task() & CRUD Methods (35 min, $0.003)
- Update `get_task()` to return compressed format
- Update `create_task()` and `update_task()` responses
- Ensure error handling preserved

### Mini-Task 4: Update System Prompt (20 min, $0.002)
- Add compression key explanations to system prompt
- Ensure LLM understands abbreviated format
- Test comprehension with small task set

### Mini-Task 5: Validation & Testing (25 min, $0.002)
- Measure token reduction
- Test all task operations work
- Verify LLM can use compressed data properly

**Total Time**: 2-4 hours
**Total Cost**: $0.012 per Haiku
**Savings**: 2,300-4,600 tokens per interaction

---

## Compression Field Mapping

| Original Field | Compressed | Logic | Inclusion Rule |
|----------------|------------|--------|----------------|
| `task.id` | `"id"` | Keep as-is | Always |
| `task.content` | `"txt"` | Abbreviated | Always |
| `task.labels` | `"lbl"` | Abbreviated | Only if `len > 0` |
| `task.priority` | `"p"` | Abbreviated | Only if `> 1` (not default) |
| `task.due.date` | `"due"` | Keep string | Only if exists |
| `task.created_at[:10]` | `"crt"` | Date only | Rarely needed |
| `task.project_id` | `"prj"` | Project name | For cross-project context |
| `task.section_id` | `"sec"` | Section name | Rarely |
| `task.description` | ❌ | Too verbose | Via separate query |

**Data is available** if LLM explicitly needs it via `get_comments()` or separate `get_task()` call.

---

## Code Examples

### Core Compression Method:
```python
def _compress_task(self, task: Task) -> dict:
    """Compress Todoist Task object to minimal token format."""
    compressed = {
        "id": task.id,
        "txt": task.content
    }

    # Only include non-default/empty fields
    if task.labels:
        compressed["lbl"] = task.labels
    if task.priority > 1:
        compressed["p"] = task.priority
    if task.due:
        compressed["due"] = task.due.date  # Date string only

    return compressed
```

### Updated list_tasks():
```python
def list_tasks(self, project_name: Optional[str] = None, ...) -> Dict[str, Any]:
    # ... existing filtering logic ...

    # Compress each task before returning
    compressed_tasks = [self._compress_task(t) for t in tasks]

    return self._success(f"Found {len(compressed_tasks)} tasks", compressed_tasks)
```

---

## Success Criteria

### ✅ Must Pass:
- [ ] `_compress_task()` method implemented and tested
- [ ] All task operation methods return compressed format
- [ ] Essential task data preserved (ID, content, labels, priority, due date)
- [ ] Token usage reduced by 2,000-4,000 tokens per large task list
- [ ] LLM can still perform all task operations properly
- [ ] Backward compatibility maintained for critical operations

### File Impacts:
- `core.py`: + ~20 lines (_compress_task method)
- `task_management.py`: ~6 methods updated (list, get, create, update)
- `agents/todoist.yaml`: System prompt updated with compression key meanings

---

## Validation Strategy

### Token Measurement:
```bash
# Before compression
./synapse todoist
> list inbox
# Note tokens: XXXX
# Note tasks returned: XX

# After compression
./synapse todoist
> list inbox
# Verify reduction: 200-400% fewer tokens
# Verify functionality: all tasks readable
```

### Functional Test:
```python
# Test task data access still works
agent = TodoistAgent(config)
result = await agent.list_tasks("Inbox")
compressed_tasks = result["data"]

# LLM should understand abbreviated keys
task = compressed_tasks[0]
assert task["id"]  # Task ID
assert task["txt"]  # Content
assert task.get("lbl", [])  # Labels if present
```

---

## Safety Features

### Incremental Rollback:
- Function name clearly indicates compression
- Can easily add `compress=False` parameter if needed
- Comment all compression logic clearly

### Validation Checks:
- Run with real Todoist data before deploy
- Test full workflow: list → get → update → create
- Ensure no task data lost in compression

---

## Quality Assurance

### Field Completeness Check:
- ID: ✅ Required for task references
- Content: ✅ Essential task description
- Labels: ✅ Needed for GTD categorization
- Priority: ✅ Important for task ordering
- Due Date: ✅ Critical for scheduling
- Created Date: ✅ Important for task age/relevance

### LLM Comprehension Test:
1. **Query**: "What are my next actions?"
   - Expects compressed task list
   - LLM must understand "txt", "lbl", "p" meanings

2. **Command**: "Complete task X from the list"
   - Uses shortened task IDs
   - Verifies task selection works

3. **Filter**: "Show only urgent tasks"
   - Tests priority ("p") field comprehension

---

## Next Steps After Completion

**Phase 4 Goals**: **2,000-4,000 tokens saved** (40-50% of remaining usage)

**Possible Optimizations**:
1. **Context-aware tool filtering**: Only load tools relevant to current task (~500 tokens saved)
2. **Knowledge base indexing**: Semantic chunking with summaries (~300-600 tokens saved)
3. **Message history summarization**: Compress conversation history (~500 tokens saved)

---

## Expected Outcomes

### Performance Impact:
- **Before**: 12,000 tokens/inbox workflow → **After**: 8,000 tokens/inbox workflow
- **% Savings**: **33% reduction** per inbox processing session
- **Dollar Impact**: ~$2.50 → $1.80 per 1000 inbox processes

### User Experience:
- ✅ All functionality preserved
- ✅ Performance may be perceived as faster (less data to process)
- ✅ LLM still has full task information when needed

---

## Ready to Execute

**Current Status**: ✅ Docstring compression completed
**Next Phase**: 🎯 **Task data compression** (highest ROI)

**Mini-Task 1**: Implement `_compress_task()` method in `core.py`

---
**Ready to save 2,300-4,600 tokens per interaction with a 30-minute implementation.**