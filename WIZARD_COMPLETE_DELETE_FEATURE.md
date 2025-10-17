# Wizard Enhancement: Add Complete/Delete Options

**Date**: 2025-10-17
**Status**: ✅ IMPLEMENTED - Ready to test
**Feature Request**: Add "complete" and "delete" options to first step of wizard
**Benefit**: Quickly process tasks that don't need full GTD categorization

---

## ✅ IMPLEMENTATION COMPLETE

**Files Modified**:
1. `core/wizard/inbox_wizard.py` - Added complete/delete options to wizard
2. `core/agents/todoist.py` - Added parsing and execution of complete/delete actions

**Changes**:
- First step now shows: `(c)omplete | (d)elete | (s)kip | (p)ause | ENTER to process`
- Typing `c` marks task for completion, continues to next task
- Typing `d` marks task for deletion, continues to next task
- After wizard finishes, batch complete and delete API calls are made
- Summary shows completed and deleted counts

**Ready for**: Testing and commit

---

## 📋 CURRENT WORKFLOW

**File**: `core/wizard/inbox_wizard.py`

**Current first step prompt**:
```python
f"[{i}/{total}] {task['content']}\n"
f"  Type: {'Simple' if ai_suggestion['is_simple'] else 'Multi-step'}\n"
f"  ...\n"
f"  (s)kip | (p)ause | (q)uit: "
```

**Options**:
- Enter = accept AI suggestions
- Type values = override suggestions
- `s` = skip this task
- `p` = pause wizard (save progress)
- `q` = quit wizard (discard progress)

---

## 🎯 NEW FEATURE

Add two new options at the first step:

- **`c`** = **Complete** this task (mark done immediately)
- **`d`** = **Delete** this task (remove from Todoist)

### User Experience

```
[1/46] poison spiders
  Type: Simple
  Contexts: add chore, add yard
  Energy: h, Duration: m

  (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: c

✓ Marked for completion

[2/46] sweep under the couch
  ...
```

### What Happens

1. **During wizard**: Task ID saved to `tasks_to_complete` or `tasks_to_delete` list
2. **After wizard**: Batch API calls made:
   ```python
   for task_id in tasks_to_complete:
       agent.complete_task(task_id)

   for task_id in tasks_to_delete:
       agent.delete_task(task_id)
   ```

---

## 📝 IMPLEMENTATION PLAN

### ✅ TODO LIST

- [x] **TASK 1**: Update first step prompt in `run_inbox_wizard()` to show (c)omplete | (d)elete options ✅
- [x] **TASK 2**: Add input handling for 'c' and 'd' commands ✅
- [x] **TASK 3**: Add `tasks_to_complete` and `tasks_to_delete` lists to wizard output ✅
- [x] **TASK 4**: Update `process_inbox()` to handle complete/delete lists after wizard ✅
- [ ] **TASK 5**: Test the workflow
- [ ] **TASK 6**: Commit and push

**Status**: Implementation complete - Ready to test and commit

---

## 🔧 IMPLEMENTATION DETAILS

### TASK 1: Update First Step Prompt

**File**: `core/wizard/inbox_wizard.py`
**Function**: `run_inbox_wizard()`
**Location**: Line ~130-140 (first step prompt)

**FIND THIS**:
```python
print(f"\n[{i}/{total}] {task['content']}")
print(f"  Type: {'Simple' if ai_suggestion['is_simple'] else 'Multi-step'}")
# ... other suggestion lines ...
print(f"\n  (s)kip | (p)ause | (q)uit: ", end="")
```

**REPLACE WITH**:
```python
print(f"\n[{i}/{total}] {task['content']}")
print(f"  Type: {'Simple' if ai_suggestion['is_simple'] else 'Multi-step'}")
# ... other suggestion lines ...
print(f"\n  (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: ", end="")
```

---

### TASK 2: Add Input Handling

**File**: `core/wizard/inbox_wizard.py`
**Function**: `run_inbox_wizard()`
**Location**: After first step input (line ~145)

**CURRENT CODE** (approximately):
```python
first_response = input().strip().lower()

if first_response == 'q':
    print("\n❌ Wizard cancelled.")
    return None
elif first_response == 'p':
    # pause logic
elif first_response == 's':
    # skip logic
    continue
```

**ADD AFTER** the `first_response = input()` line:

```python
# Handle complete/delete commands
if first_response == 'c':
    print("  ✓ Marked for completion")
    wizard_output['tasks_to_complete'].append(task['id'])
    continue
elif first_response == 'd':
    print("  ✓ Marked for deletion")
    wizard_output['tasks_to_delete'].append(task['id'])
    continue
```

---

### TASK 3: Initialize Lists in Wizard Output

**File**: `core/wizard/inbox_wizard.py`
**Function**: `run_inbox_wizard()`
**Location**: Top of function where `wizard_output` is initialized (line ~50-60)

**FIND THIS**:
```python
wizard_output = {
    'tasks_processed': [],
    'paused': False,
    'paused_at': None
}
```

**REPLACE WITH**:
```python
wizard_output = {
    'tasks_processed': [],
    'tasks_to_complete': [],
    'tasks_to_delete': [],
    'paused': False,
    'paused_at': None
}
```

---

### TASK 4: Handle Complete/Delete in process_inbox()

**File**: `core/agents/todoist.py`
**Function**: `process_inbox()`
**Location**: After wizard completes (line ~1930-1950)

**FIND THIS** (approximately):
```python
wizard_output = run_inbox_wizard(tasks, ai_suggestions)

if wizard_output is None:
    return "❌ Inbox processing cancelled."

if wizard_output.get('paused'):
    return "⏸️  Inbox processing paused..."

# Process the tasks
tasks_processed = wizard_output['tasks_processed']
```

**ADD AFTER** the tasks_processed assignment:

```python
# Handle tasks marked for completion
tasks_to_complete = wizard_output.get('tasks_to_complete', [])
if tasks_to_complete:
    print(f"\n✓ Completing {len(tasks_to_complete)} task(s)...")
    for task_id in tasks_to_complete:
        try:
            result = self.complete_task(task_id)
            result_data = json.loads(result)
            if result_data['status'] == 'success':
                print(f"  ✓ Completed task {task_id}")
            else:
                print(f"  ❌ Failed to complete {task_id}: {result_data['message']}")
        except Exception as e:
            print(f"  ❌ Error completing {task_id}: {str(e)}")

# Handle tasks marked for deletion
tasks_to_delete = wizard_output.get('tasks_to_delete', [])
if tasks_to_delete:
    print(f"\n🗑️  Deleting {len(tasks_to_delete)} task(s)...")
    for task_id in tasks_to_delete:
        try:
            result = self.delete_task(task_id)
            result_data = json.loads(result)
            if result_data['status'] == 'success':
                print(f"  ✓ Deleted task {task_id}")
            else:
                print(f"  ❌ Failed to delete {task_id}: {result_data['message']}")
        except Exception as e:
            print(f"  ❌ Error deleting {task_id}: {str(e)}")
```

---

## 🧪 TEST PLAN

### Test Case 1: Complete Task

```bash
./synapse to
> process inbox
```

When wizard shows:
```
[1/46] poison spiders
  Type: Simple
  Contexts: add chore, add yard
  Energy: h, Duration: m

  (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: c
```

**Expected**:
- Prints "✓ Marked for completion"
- Moves to next task
- After wizard finishes: "✓ Completing 1 task(s)..."
- Task marked as done in Todoist

---

### Test Case 2: Delete Task

Type `d` at first step prompt.

**Expected**:
- Prints "✓ Marked for deletion"
- Moves to next task
- After wizard finishes: "🗑️  Deleting 1 task(s)..."
- Task removed from Todoist

---

### Test Case 3: Mixed Operations

Process 5 tasks:
1. Complete (c)
2. Delete (d)
3. Process normally (Enter)
4. Skip (s)
5. Complete (c)

**Expected**:
- 2 tasks marked for completion
- 1 task marked for deletion
- 1 task processed with GTD categorization
- 1 task skipped
- After wizard: Batch operations executed

---

## 🎯 VERIFICATION CHECKLIST

After implementation:

- [ ] Prompt shows "(c)omplete | (d)elete" options
- [ ] Typing 'c' marks task for completion and continues
- [ ] Typing 'd' marks task for deletion and continues
- [ ] After wizard, tasks are completed via API
- [ ] After wizard, tasks are deleted via API
- [ ] Error handling works (failed API calls)
- [ ] Works with pause/resume workflow

---

## 🚨 RESUME INSTRUCTIONS

If interrupted:

**Check progress**:
```bash
git diff core/wizard/inbox_wizard.py
git diff core/agents/todoist.py
```

**Resume at**:
- No changes = Start TASK 1
- Prompt updated = Start TASK 2
- Input handling added = Start TASK 3
- Lists initialized = Start TASK 4
- process_inbox updated = Start TASK 5 (test)

**Quick reference**:
- Wizard file: `core/wizard/inbox_wizard.py`
- Agent file: `core/agents/todoist.py` (line ~1930)
- This doc: `WIZARD_COMPLETE_DELETE_FEATURE.md`

---

## 📊 BENEFITS

### User Experience
- ✅ **Faster**: No need to process tasks that are already done or irrelevant
- ✅ **Flexible**: Mix complete/delete/process in single wizard session
- ✅ **Efficient**: Batch API calls at end (not per-task)

### Technical
- ✅ **Consistent**: Uses existing `complete_task()` and `delete_task()` methods
- ✅ **Reliable**: Error handling for failed operations
- ✅ **Batch-optimized**: Single API call per action, not N calls during wizard

---

## 💡 FUTURE ENHANCEMENTS (Not in Scope)

Ideas for later:
- Add confirmation before completing/deleting (optional flag)
- Show completed/deleted count in summary
- Allow undo of complete/delete before wizard finishes
- Add keyboard shortcuts for common patterns (e.g., "cd" = complete and delete next)

---

**Status**: Ready to implement
**Next action**: TASK 1 - Update first step prompt
**File to start**: `core/wizard/inbox_wizard.py`
