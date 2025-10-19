# Mini-Project 002: Split Todoist Agent - FINAL PLAN
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Cost**: $0.015-0.025 total (Haiku)
**Priority**: 🔴 CRITICAL (delivers 70% AI maintenance savings)
**Time**: 3-4 hours total (spread across 6 mini-tasks)
**Platform**: Linux (with Python 3.8+)

---

## Architecture Decision: Method Attachment Pattern

We're using **Method Attachment** - methods stay as normal methods with `self`, but are defined in separate files and attached to the class at import time.

### How It Works:

```python
# task_management.py - Define methods normally
def create_task(self, content, ...):
    """Create a task."""
    # Use self.api, self._get_projects(), etc. - works normally!
    return self._success("Created")

# Attach to class at end of file
TodoistAgent.create_task = create_task

# __init__.py - Import modules (methods auto-attach)
from .core import TodoistAgent
import core.agents.todoist.task_management  # Side-effect: methods attach
```

**Why this works**:
- ✅ Methods keep exact same code (including `self` parameter)
- ✅ Small models just copy-paste methods
- ✅ No complex inheritance or mixins
- ✅ Import system automatically wires everything up

---

## Method-to-Module Mapping

### core.py (stays in class) - ~550 lines
- `__init__()` - Class initialization
- `_check_tasks_without_next_actions()` - Startup check
- `_get_projects()` - Cache helper
- `_find_project_by_name()` - Cache helper
- `_get_sections()` - Cache helper
- `_find_section_by_name()` - Cache helper
- `_get_labels()` - Cache helper
- `_get_tasks_list()` - Cache helper
- `_get_subtasks()` - Cache helper
- `_move_task_with_subtasks()` - Internal helper
- `_success()` - Response helper
- `_error()` - Response helper
- `get_current_time()` - Tool method (keep with core)

### task_management.py - ~570 lines
- `create_task()` - lines 190-304
- `list_tasks()` - lines 306-391
- `complete_task()` - lines 393-410
- `update_task()` - lines 412-479
- `get_task()` - lines 481-514
- `add_comment()` - lines 516-536
- `delete_task()` - lines 538-559
- `reopen_task()` - lines 561-581
- `move_task()` - lines 583-613
- `batch_move_tasks()` - lines 615-688
- `list_projects()` - lines 690-717
- `list_sections()` - lines 719-760
- `list_labels()` - lines 762-792
- `get_comments()` - lines 794-828

### knowledge.py - ~180 lines
- `query_rules()` - lines 830-879
- `update_rules()` - lines 881-1043

### quick_capture.py - ~60 lines
- `capture()` - lines 1045-1064
- `add_grocery()` - lines 1066-1085

### wizards.py - ~850 lines
- `make_actionable()` - lines 1087-1157
- `ask_question()` - lines 1159-1196
- `_calculate_reminder_time()` - lines 1198-1237
- `_find_staggered_slot()` - lines 1285-1318
- `set_reminder()` - lines 1320-1393
- `create_standalone_reminder()` - lines 1395-1447
- `set_routine_reminder()` - lines 1449-1519
- `reset_overdue_routines()` - lines 1521-1667
- `schedule_task()` - lines 2016-2031
- `process_wizard_output()` - lines 2211-2475
- `_parse_natural_date()` - lines 2477-2520

### gtd_workflow.py - ~850 lines
- `list_next_actions()` - lines 1669-1691
- `find_tasks_without_next_actions()` - lines 1693-1770
- `review_tasks_without_next_actions()` - lines 1772-1875
- `_process_no_next_action_review()` - lines 1877-2014
- `process_inbox()` - lines 2033-2209
- `suggest_next_action_tags()` - lines 2522-2664
- `process_subtask_tags()` - lines 2666-2789
- `suggest_task_formatting()` - lines 2791-2897

---

## 🚨 MINI-TASK 0: Create Backup (MANDATORY - DO THIS FIRST!)
**Time**: 2 minutes | **Cost**: $0.000

### Instructions:

```bash
# Create backup of original file
cp /home/bryceg/synapse/core/agents/todoist.py /home/bryceg/synapse/core/agents/todoist.py.backup

# Create target directory
mkdir -p /home/bryceg/synapse/core/agents/todoist

# Verify backup
ls -lh /home/bryceg/synapse/core/agents/todoist.py.backup
wc -l /home/bryceg/synapse/core/agents/todoist.py.backup
```

### Expected Output:
```
-rw-r--r-- 1 user user 95K Oct 18 12:00 /home/bryceg/synapse/core/agents/todoist.py.backup
2897 /home/bryceg/synapse/core/agents/todoist.py.backup
```

### ✅ Validation:
- [ ] Backup file exists
- [ ] Backup has 2897 lines
- [ ] Directory `core/agents/todoist/` exists

### 🚨 If something goes wrong later:

```bash
# EMERGENCY ROLLBACK - Run this to undo everything
rm -rf /home/bryceg/synapse/core/agents/todoist/
mv /home/bryceg/synapse/core/agents/todoist.py.backup /home/bryceg/synapse/core/agents/todoist.py
```

**If validation fails**: Report error to big model with exact error message.

---

## Mini-Task 1: Create Core Module
**Time**: 40 minutes | **Cost**: $0.004

### Objective:
Extract the TodoistAgent class shell with all helper methods and caches.

### Step 1A: Create `core/agents/todoist/core.py`

**COPY EXACTLY - Use the Read tool to get these line ranges from original file:**

1. **Lines 1-16**: Copy the entire import block
2. **Lines 18-147**: Copy class definition through `_error()` method

**How to do this**:
```bash
# Use the Read tool:
# Read lines 1-16 from /home/bryceg/synapse/core/agents/todoist.py
# Read lines 18-147 from /home/bryceg/synapse/core/agents/todoist.py
# Paste both into new file at /home/bryceg/synapse/core/agents/todoist/core.py
```

The file should look like:
```python
"""
TodoistAgent - GTD Personal Assistant
...
"""

import os
import json
# ... all imports from lines 1-16 ...

class TodoistAgent(BaseAgent):
    """
    A specialized agent for managing Todoist tasks using GTD methodology.
    ...
    """

    def __init__(self, config: dict):
        """Initialize the TodoistAgent with API connection."""
        # ... entire __init__ method ...

    def _check_tasks_without_next_actions(self):
        # ... method body ...

    def _get_projects(self) -> list[Project]:
        # ... method body ...

    # ... continue through _error() method ...
```

### Step 1B: Add `get_current_time()` to core.py

**COPY EXACTLY - Lines 153-187 from original file**

Paste at the end of `core.py` (inside the TodoistAgent class, same indentation as other methods).

### Step 1C: Add `_get_subtasks()` to core.py

**COPY EXACTLY - Lines 1239-1250 from original file**

Paste at the end of `core.py`.

### Step 1D: Add `_move_task_with_subtasks()` to core.py

**COPY EXACTLY - Lines 1252-1283 from original file**

Paste at the end of `core.py`.

### Step 1E: Create `core/agents/todoist/__init__.py`

**CREATE THIS FILE WITH EXACT CONTENT:**

```python
"""
TodoistAgent - GTD Personal Assistant

This package manages a Todoist system following strict GTD methodology.

Modules:
- core: TodoistAgent class with initialization and helper methods
- task_management: CRUD operations for tasks
- knowledge: Learning and rules management
- quick_capture: Quick entry methods (capture, groceries)
- wizards: Wizard processing and actionable tasks
- gtd_workflow: GTD workflow (inbox processing, next actions, reviews)
"""

from .core import TodoistAgent

# Import all other modules (methods will auto-attach to TodoistAgent)
# NOTE: These imports have side effects - they attach methods to the class
try:
    import core.agents.todoist.task_management
    import core.agents.todoist.knowledge
    import core.agents.todoist.quick_capture
    import core.agents.todoist.wizards
    import core.agents.todoist.gtd_workflow
except ImportError:
    # During incremental development, modules may not exist yet
    pass

__all__ = ['TodoistAgent']
```

### Step 1F: Update original `core/agents/todoist.py`

**REPLACE ENTIRE FILE WITH:**

```python
"""
Backward compatibility wrapper for TodoistAgent.

The TodoistAgent class has been split into multiple modules for better
organization and token efficiency. Import from core.agents.todoist instead.

New structure:
- core.agents.todoist.core: TodoistAgent class + helpers
- core.agents.todoist.task_management: Task CRUD operations
- core.agents.todoist.knowledge: Learning and rules
- core.agents.todoist.quick_capture: Quick entry methods
- core.agents.todoist.wizards: Wizard processing
- core.agents.todoist.gtd_workflow: GTD workflow methods
"""

from .todoist import TodoistAgent

__all__ = ['TodoistAgent']
```

### Validation:

```bash
# Check files created
ls -lh /home/bryceg/synapse/core/agents/todoist/
wc -l /home/bryceg/synapse/core/agents/todoist/core.py

# Test import (should work even though other modules don't exist yet)
python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

try:
    from core.agents.todoist import TodoistAgent
    print("✅ TodoistAgent import successful")
    print("✅ Class accessible:", TodoistAgent.__name__)
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)
EOF
```

### Expected Output:
```
✅ TodoistAgent import successful
✅ Class accessible: TodoistAgent
```

### ✅ Validation Checklist:
- [ ] `core/agents/todoist/core.py` exists (~550 lines)
- [ ] `core/agents/todoist/__init__.py` exists (~30 lines)
- [ ] `core/agents/todoist.py` updated (~15 lines)
- [ ] Import test passes

**If validation fails**: Report exact error message to big model. DO NOT try to fix it.

---

## Mini-Task 2: Extract Task Management Module
**Time**: 45 minutes | **Cost**: $0.004

### Objective:
Extract all task CRUD and project/section/label listing methods.

### Step 2A: Create `core/agents/todoist/task_management.py`

**START WITH THIS HEADER:**

```python
"""
Task management operations for TodoistAgent.

This module contains CRUD operations for tasks, projects, sections, and labels.
All methods are attached to the TodoistAgent class at import time.
"""

import json
from typing import Optional, Literal
from datetime import datetime


# Methods will be attached to TodoistAgent class
# They can use self.api, self._get_projects(), self._success(), etc.
```

### Step 2B: Copy Methods from Original File

**Use the Read tool to copy these EXACT line ranges:**

1. **Lines 190-304**: `create_task()` method
2. **Lines 306-391**: `list_tasks()` method
3. **Lines 393-410**: `complete_task()` method
4. **Lines 412-479**: `update_task()` method
5. **Lines 481-514**: `get_task()` method
6. **Lines 516-536**: `add_comment()` method
7. **Lines 538-559**: `delete_task()` method
8. **Lines 561-581**: `reopen_task()` method
9. **Lines 583-613**: `move_task()` method
10. **Lines 615-688**: `batch_move_tasks()` method
11. **Lines 690-717**: `list_projects()` method
12. **Lines 719-760**: `list_sections()` method
13. **Lines 762-792**: `list_labels()` method
14. **Lines 794-828**: `get_comments()` method

**IMPORTANT**:
- Copy methods EXACTLY as they are
- Keep all docstrings
- Keep `self` as first parameter
- Don't change indentation (methods should start at column 0, NOT indented)

### Step 2C: Add Method Attachment at End of File

**ADD THIS AT THE VERY END of `task_management.py`:**

```python


# ============================================================================
# ATTACH METHODS TO TodoistAgent CLASS
# ============================================================================

# Import the class (will be available after core.py loads)
from .core import TodoistAgent

# Attach all methods defined in this module
TodoistAgent.create_task = create_task
TodoistAgent.list_tasks = list_tasks
TodoistAgent.complete_task = complete_task
TodoistAgent.update_task = update_task
TodoistAgent.get_task = get_task
TodoistAgent.add_comment = add_comment
TodoistAgent.delete_task = delete_task
TodoistAgent.reopen_task = reopen_task
TodoistAgent.move_task = move_task
TodoistAgent.batch_move_tasks = batch_move_tasks
TodoistAgent.list_projects = list_projects
TodoistAgent.list_sections = list_sections
TodoistAgent.list_labels = list_labels
TodoistAgent.get_comments = get_comments
```

### Validation:

```bash
# Check file size
wc -l /home/bryceg/synapse/core/agents/todoist/task_management.py

# Test import and method attachment
python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

try:
    from core.agents.todoist import TodoistAgent

    # Check methods are attached
    methods = ['create_task', 'list_tasks', 'complete_task', 'update_task',
               'get_task', 'add_comment', 'delete_task', 'reopen_task',
               'move_task', 'batch_move_tasks', 'list_projects', 'list_sections',
               'list_labels', 'get_comments']

    for method in methods:
        if not hasattr(TodoistAgent, method):
            print(f"❌ Missing method: {method}")
            exit(1)

    print(f"✅ All {len(methods)} methods attached successfully")
    print("✅ task_management module working")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF
```

### Expected Output:
```
✅ All 14 methods attached successfully
✅ task_management module working
```

### ✅ Validation Checklist:
- [ ] `task_management.py` created (~570 lines)
- [ ] All 14 methods present
- [ ] Import test passes
- [ ] Method attachment test passes

**If validation fails**: Report exact error to big model. DO NOT try to fix it.

---

## Mini-Task 3: Extract Knowledge Module
**Time**: 20 minutes | **Cost**: $0.002

### Objective:
Extract knowledge and learning methods.

### Step 3A: Create `core/agents/todoist/knowledge.py`

**START WITH THIS HEADER:**

```python
"""
Knowledge and learning management for TodoistAgent.

Handles rule querying, learning, and knowledge file operations.
"""

import json
from pathlib import Path
from typing import Optional, Literal


# Methods will be attached to TodoistAgent class
```

### Step 3B: Copy Methods

**Use Read tool to copy these line ranges:**

1. **Lines 830-879**: `query_rules()` method
2. **Lines 881-1043**: `update_rules()` method

### Step 3C: Add Method Attachment

**ADD AT END OF FILE:**

```python


# ============================================================================
# ATTACH METHODS TO TodoistAgent CLASS
# ============================================================================

from .core import TodoistAgent

TodoistAgent.query_rules = query_rules
TodoistAgent.update_rules = update_rules
```

### Validation:

```bash
# Check file
wc -l /home/bryceg/synapse/core/agents/todoist/knowledge.py

# Test
python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

from core.agents.todoist import TodoistAgent

if hasattr(TodoistAgent, 'query_rules') and hasattr(TodoistAgent, 'update_rules'):
    print("✅ Knowledge methods attached")
else:
    print("❌ Methods missing")
    exit(1)
EOF
```

### ✅ Validation:
- [ ] `knowledge.py` created (~180 lines)
- [ ] Both methods attached
- [ ] Import test passes

---

## Mini-Task 4: Extract Quick Capture Module
**Time**: 15 minutes | **Cost**: $0.002

### Objective:
Extract quick capture methods.

### Step 4A: Create `core/agents/todoist/quick_capture.py`

**START WITH:**

```python
"""
Quick capture methods for TodoistAgent.

Handles rapid task entry (capture, groceries, etc.).
"""

import json


# Methods will be attached to TodoistAgent class
```

### Step 4B: Copy Methods

**Copy these line ranges:**

1. **Lines 1045-1064**: `capture()` method
2. **Lines 1066-1085**: `add_grocery()` method

### Step 4C: Add Method Attachment

```python


# ============================================================================
# ATTACH METHODS TO TodoistAgent CLASS
# ============================================================================

from .core import TodoistAgent

TodoistAgent.capture = capture
TodoistAgent.add_grocery = add_grocery
```

### Validation:

```bash
wc -l /home/bryceg/synapse/core/agents/todoist/quick_capture.py

python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

from core.agents.todoist import TodoistAgent

if hasattr(TodoistAgent, 'capture') and hasattr(TodoistAgent, 'add_grocery'):
    print("✅ Quick capture methods attached")
else:
    print("❌ Methods missing")
    exit(1)
EOF
```

### ✅ Validation:
- [ ] `quick_capture.py` created (~60 lines)
- [ ] Both methods attached

---

## Mini-Task 5: Extract Wizards Module
**Time**: 50 minutes | **Cost**: $0.005

### Objective:
Extract wizard and actionable task processing methods.

### Step 5A: Create `core/agents/todoist/wizards.py`

**START WITH:**

```python
"""
Wizard processing and task actionability for TodoistAgent.

Handles interactive wizards, reminder calculations, and making tasks actionable.
"""

import json
from typing import Literal
from datetime import datetime, timedelta


# Methods will be attached to TodoistAgent class
```

### Step 5B: Copy Methods

**Copy these line ranges (11 methods):**

1. **Lines 1087-1157**: `make_actionable()`
2. **Lines 1159-1196**: `ask_question()`
3. **Lines 1198-1237**: `_calculate_reminder_time()`
4. **Lines 1285-1318**: `_find_staggered_slot()`
5. **Lines 1320-1393**: `set_reminder()`
6. **Lines 1395-1447**: `create_standalone_reminder()`
7. **Lines 1449-1519**: `set_routine_reminder()`
8. **Lines 1521-1667**: `reset_overdue_routines()`
9. **Lines 2016-2031**: `schedule_task()`
10. **Lines 2211-2475**: `process_wizard_output()`
11. **Lines 2477-2520**: `_parse_natural_date()`

### Step 5C: Add Method Attachment

```python


# ============================================================================
# ATTACH METHODS TO TodoistAgent CLASS
# ============================================================================

from .core import TodoistAgent

TodoistAgent.make_actionable = make_actionable
TodoistAgent.ask_question = ask_question
TodoistAgent._calculate_reminder_time = _calculate_reminder_time
TodoistAgent._find_staggered_slot = _find_staggered_slot
TodoistAgent.set_reminder = set_reminder
TodoistAgent.create_standalone_reminder = create_standalone_reminder
TodoistAgent.set_routine_reminder = set_routine_reminder
TodoistAgent.reset_overdue_routines = reset_overdue_routines
TodoistAgent.schedule_task = schedule_task
TodoistAgent.process_wizard_output = process_wizard_output
TodoistAgent._parse_natural_date = _parse_natural_date
```

### Validation:

```bash
wc -l /home/bryceg/synapse/core/agents/todoist/wizards.py

python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

from core.agents.todoist import TodoistAgent

methods = ['make_actionable', 'ask_question', 'set_reminder',
           'create_standalone_reminder', 'set_routine_reminder',
           'reset_overdue_routines', 'schedule_task',
           'process_wizard_output']

for method in methods:
    if not hasattr(TodoistAgent, method):
        print(f"❌ Missing: {method}")
        exit(1)

print(f"✅ All {len(methods)} wizard methods attached")
EOF
```

### ✅ Validation:
- [ ] `wizards.py` created (~850 lines)
- [ ] All 11 methods attached

---

## Mini-Task 6: Extract GTD Workflow Module
**Time**: 50 minutes | **Cost**: $0.005

### Objective:
Extract GTD workflow methods (inbox processing, next actions, reviews).

### Step 6A: Create `core/agents/todoist/gtd_workflow.py`

**START WITH:**

```python
"""
GTD workflow operations for TodoistAgent.

Handles inbox processing, next action management, and task reviews.
"""

import json
from typing import Optional


# Methods will be attached to TodoistAgent class
```

### Step 6B: Copy Methods

**Copy these line ranges (8 methods):**

1. **Lines 1669-1691**: `list_next_actions()`
2. **Lines 1693-1770**: `find_tasks_without_next_actions()`
3. **Lines 1772-1875**: `review_tasks_without_next_actions()`
4. **Lines 1877-2014**: `_process_no_next_action_review()`
5. **Lines 2033-2209**: `process_inbox()`
6. **Lines 2522-2664**: `suggest_next_action_tags()`
7. **Lines 2666-2789**: `process_subtask_tags()`
8. **Lines 2791-2897**: `suggest_task_formatting()`

### Step 6C: Add Method Attachment

```python


# ============================================================================
# ATTACH METHODS TO TodoistAgent CLASS
# ============================================================================

from .core import TodoistAgent

TodoistAgent.list_next_actions = list_next_actions
TodoistAgent.find_tasks_without_next_actions = find_tasks_without_next_actions
TodoistAgent.review_tasks_without_next_actions = review_tasks_without_next_actions
TodoistAgent._process_no_next_action_review = _process_no_next_action_review
TodoistAgent.process_inbox = process_inbox
TodoistAgent.suggest_next_action_tags = suggest_next_action_tags
TodoistAgent.process_subtask_tags = process_subtask_tags
TodoistAgent.suggest_task_formatting = suggest_task_formatting
```

### Validation:

```bash
wc -l /home/bryceg/synapse/core/agents/todoist/gtd_workflow.py

python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

from core.agents.todoist import TodoistAgent

methods = ['list_next_actions', 'find_tasks_without_next_actions',
           'review_tasks_without_next_actions', 'process_inbox',
           'suggest_next_action_tags', 'process_subtask_tags',
           'suggest_task_formatting']

for method in methods:
    if not hasattr(TodoistAgent, method):
        print(f"❌ Missing: {method}")
        exit(1)

print(f"✅ All {len(methods)} GTD methods attached")
EOF
```

### ✅ Validation:
- [ ] `gtd_workflow.py` created (~850 lines)
- [ ] All 8 methods attached

---

## FINAL VALIDATION (After All Mini-Tasks Complete)

### Comprehensive Test Suite:

```bash
# 1. Check all files exist and have reasonable sizes
echo "=== File Structure ==="
find /home/bryceg/synapse/core/agents/todoist -name "*.py" -exec wc -l {} + | sort -n

# 2. Test full import and all methods
python3 << 'EOF'
import os
os.environ.setdefault('TODOIST_API_TOKEN', 'test_token')

print("=== Import Test ===")
from core.agents.todoist import TodoistAgent

print("✅ TodoistAgent imported successfully")

# Check all 47 methods are present
all_methods = [
    # Core (in class)
    '__init__', 'get_current_time',
    # Task Management (14 methods)
    'create_task', 'list_tasks', 'complete_task', 'update_task', 'get_task',
    'add_comment', 'delete_task', 'reopen_task', 'move_task', 'batch_move_tasks',
    'list_projects', 'list_sections', 'list_labels', 'get_comments',
    # Knowledge (2 methods)
    'query_rules', 'update_rules',
    # Quick Capture (2 methods)
    'capture', 'add_grocery',
    # Wizards (8 methods)
    'make_actionable', 'ask_question', 'set_reminder', 'create_standalone_reminder',
    'set_routine_reminder', 'reset_overdue_routines', 'schedule_task', 'process_wizard_output',
    # GTD Workflow (7 methods)
    'list_next_actions', 'find_tasks_without_next_actions', 'review_tasks_without_next_actions',
    'process_inbox', 'suggest_next_action_tags', 'process_subtask_tags', 'suggest_task_formatting'
]

missing = []
for method in all_methods:
    if not hasattr(TodoistAgent, method):
        missing.append(method)

if missing:
    print(f"❌ Missing methods: {', '.join(missing)}")
    exit(1)

print(f"✅ All {len(all_methods)} methods present")

# Try to instantiate (will fail without real API token, but tests structure)
try:
    # This will fail at API connection, but tests __init__ loads
    agent = TodoistAgent({'timezone': 'UTC'})
except ValueError as e:
    if "TODOIST_API_TOKEN" in str(e):
        print("✅ __init__ runs (API token validation works)")
    else:
        raise

print("\n=== ALL TESTS PASSED ===")
print("✅ Split successful!")
print("✅ All modules loaded")
print("✅ All methods attached")
print("✅ Agent structure intact")
EOF

# 3. Quick smoke test with actual agent startup
echo ""
echo "=== Smoke Test ==="
timeout 30 /home/bryceg/synapse/synapse <<< "get current time" || true
```

### Expected Final Structure:

```
core/agents/todoist/
├── __init__.py              # ~30 lines - Package init + imports
├── core.py                  # ~550 lines - Class + helpers
├── task_management.py       # ~570 lines - CRUD operations
├── knowledge.py             # ~180 lines - Rules & learning
├── quick_capture.py         # ~60 lines - Quick entry
├── wizards.py              # ~850 lines - Wizard processing
└── gtd_workflow.py         # ~850 lines - GTD workflow

Total: ~3090 lines (vs original 2897 - slight increase due to headers/attachments)
```

### Acceptance Criteria:

- [ ] All 6 module files created
- [ ] `core/agents/todoist.py` updated to wrapper
- [ ] Backup file preserved
- [ ] All 47 methods present on TodoistAgent class
- [ ] Import test passes
- [ ] No circular import errors
- [ ] Agent can be instantiated (with valid API token)
- [ ] Smoke test shows agent responds to commands

---

## Token Savings Verification

### Before Split:
```python
# AI needs task management functionality
# Must read entire todoist.py file
Read("core/agents/todoist.py")  # 2897 lines = ~15,000 tokens
```

### After Split:
```python
# AI needs task management functionality
# Only reads relevant module
Read("core/agents/todoist/task_management.py")  # 570 lines = ~3,000 tokens
```

**Savings: 12,000 tokens (80% reduction) when working on specific functionality**

### Real-World Scenarios:

| Task | Before | After | Savings |
|------|--------|-------|---------|
| Add new task field | 15,000 | 3,000 | 80% |
| Fix wizard bug | 15,000 | 4,500 | 70% |
| Update GTD workflow | 15,000 | 4,500 | 70% |
| Add knowledge rule | 15,000 | 2,000 | 87% |
| Understand architecture | 15,000 | 3,000 | 80% |

**Average savings: 77%**

---

## Success Report Template

```markdown
## Mini-Project 002: Split Todoist Agent - SUCCESS ✅

**Model**: Claude 3.5 Haiku
**Total Tokens**: XXX,XXX input + YY,YYY output
**Total Cost**: $0.0XX
**Total Time**: X hours YY minutes

**Results**:
- ✅ 6 modules created (core, task_management, knowledge, quick_capture, wizards, gtd_workflow)
- ✅ Original file preserved as backup
- ✅ All 47 methods accessible on TodoistAgent class
- ✅ No circular imports
- ✅ All validation tests passed
- ✅ Agent starts and responds to commands

**File Breakdown**:
- core.py: XXX lines
- task_management.py: XXX lines
- knowledge.py: XXX lines
- quick_capture.py: XXX lines
- wizards.py: XXX lines
- gtd_workflow.py: XXX lines

**Token Savings Achieved**:
- Single module read: ~3,000 tokens (vs 15,000)
- Typical session savings: 77%
- Future AI maintenance: $0.005-0.007 per session (vs $0.015-0.020)

**Ready for**: Phase 3 - Tool docstring compression
```

---

## Emergency Procedures

### If Tests Fail:

1. **DO NOT try to fix** - Small models should report errors
2. **Capture exact error message** - Include full traceback
3. **Report to big model** - Include which mini-task failed
4. **DO NOT proceed** - Stop and wait for big model guidance

### If Import Errors Occur:

```bash
# Check for syntax errors
python3 -m py_compile /home/bryceg/synapse/core/agents/todoist/*.py

# Check for circular imports
python3 -c "import core.agents.todoist; print('OK')"
```

### Complete Rollback:

```bash
# Undo everything
rm -rf /home/bryceg/synapse/core/agents/todoist/
mv /home/bryceg/synapse/core/agents/todoist.py.backup /home/bryceg/synapse/core/agents/todoist.py

# Verify restoration
wc -l /home/bryceg/synapse/core/agents/todoist.py  # Should be 2897
```

---

## Notes for Small Models

### DO:
✅ Follow instructions exactly
✅ Copy code blocks precisely (including all whitespace)
✅ Run validation commands after each mini-task
✅ Report errors immediately with full details
✅ Use Read tool to get exact line ranges
✅ Verify line counts match expectations

### DON'T:
❌ Try to fix errors yourself
❌ Skip validation steps
❌ Modify code while copying
❌ Proceed if tests fail
❌ Guess at line numbers
❌ Change indentation or formatting

### If Stuck:
1. Re-read the mini-task instructions
2. Check you copied exact line ranges
3. Verify validation commands
4. Report to big model if still stuck

---

## Ready to Execute

**Cost estimate**: $0.015-0.025 (Haiku) total across all 6 mini-tasks

**First mini-task**: Mini-Task 0 (Create backup) - Takes 2 minutes, critical for safety

**After completion**: Big model will review, test thoroughly, and commit changes

---

**END OF PLAN**

This plan is ready for execution by small models (Claude 3.5 Haiku or GPT-4o-mini).
