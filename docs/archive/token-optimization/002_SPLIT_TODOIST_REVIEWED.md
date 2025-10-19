# Mini-Project 002: Split Todoist Agent (REVIEWED & IMPROVED)
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 15,000 input + 5,000 output per task
**Estimated Cost**: $0.01-0.02 total (Haiku)
**Priority**: 🔴 CRITICAL (delivers 70% AI maintenance savings)
**Time**: 4-6 hours total (spread across 8 mini-tasks)
**Platform**: Linux (with Python 3.8+)

---

## CRITICAL CHANGES FROM ORIGINAL PLAN

### Issues Fixed:
1. ✅ **Added explicit backup step** (Mini-Task 0)
2. ✅ **Provided exact line ranges** for code extraction
3. ✅ **Clarified how to handle `self.` method calls** across modules
4. ✅ **Made imports explicit** with examples for each task
5. ✅ **Progressive `__init__.py` updates** (wire up as you go)
6. ✅ **Better validation** (can test incrementally)
7. ✅ **Emergency rollback commands** at every step

### New Structure:
- Mini-Task 0: **Backup original file** (safety first!)
- Mini-Tasks 1-8: **Extract modules incrementally** (wire up imports as you go)
- Each task now has: exact lines, import examples, validation that works

---

## Overview

**Problem**: `core/agents/todoist.py` is a monolithic 2,897-line file. Every AI session working on Synapse reads this entire file (15,000 tokens), wasting tokens even when only using 10-20% of the functionality.

**Solution**: Split into 6 focused modules averaging 480 lines each. When an AI needs task management, it reads only the Task Management module (~3,000 tokens) instead of the full file (15,000 tokens).

**Impact**:
- **Before**: Any Synapse code work = 15,000 tokens (read whole file)
- **After**: Task work = 3,000 tokens (read 1 module), Core changes = 2,000 tokens, etc.
- **Savings**: 70% reduction per session ($0.015-0.02 → $0.005-0.007)

**Structure After Split**:
```
core/agents/
├── todoist/
│   ├── __init__.py              # Public exports (progressively built)
│   ├── core.py                  # Infrastructure (480 lines)
│   ├── data_access.py           # API helpers (480 lines)
│   ├── task_management.py       # CRUD operations (480 lines)
│   ├── knowledge.py             # Learning/rules (480 lines)
│   ├── wizards.py               # Wizard processing (480 lines)
│   └── gtd_workflow.py          # High-level GTD (480 lines)
├── base.py                      # Unchanged
└── todoist.py.backup            # Backup of original
```

---

## 🚨 MINI-TASK 0: Create Backup (DO THIS FIRST!)
**Time**: 2 minutes | **Cost**: $0.000 | **MANDATORY**

**Objective**: Ensure we can roll back if anything goes wrong.

**Commands**:
```bash
# Create backup
cp /home/bryceg/synapse/core/agents/todoist.py /home/bryceg/synapse/core/agents/todoist.py.backup

# Verify backup exists
ls -lh /home/bryceg/synapse/core/agents/todoist.py.backup
wc -l /home/bryceg/synapse/core/agents/todoist.py.backup  # Should be 2897 lines

# Create target directory
mkdir -p /home/bryceg/synapse/core/agents/todoist
```

**If something goes wrong later**:
```bash
# EMERGENCY ROLLBACK
rm -rf /home/bryceg/synapse/core/agents/todoist
mv /home/bryceg/synapse/core/agents/todoist.py.backup /home/bryceg/synapse/core/agents/todoist.py
```

**Validation**: ✅ Backup file exists with 2897 lines

---

## Mini-Task 1: Extract Core Infrastructure
**Time**: 45 minutes | **Cost**: $0.004 | **Lines**: ~500

**Objective**: Extract the `TodoistAgent` class shell with core infrastructure methods.

### What to Extract (EXACT LINES):

**Lines 1-16**: Imports
**Lines 19-56**: `TodoistAgent.__init__()` class definition + `__init__`
**Lines 58-73**: `_check_tasks_without_next_actions()`
**Lines 134-151**: `_success()` and `_error()` utility methods
**Lines 153-187**: `get_current_time()` method

### Step-by-Step Instructions:

#### 1A. Create `core/agents/todoist/core.py`

Copy these sections IN ORDER:
1. Lines 1-16 (imports) - COPY EXACTLY
2. Lines 19-25 (class definition + docstring)
3. Lines 27-56 (`__init__` method)
4. Lines 58-73 (`_check_tasks_without_next_actions`)
5. Lines 134-151 (`_success` and `_error`)
6. Lines 153-187 (`get_current_time`)

**CRITICAL**:
- Keep all indentation EXACTLY as is
- Import statements from lines 1-16 stay at top
- Class definition starts at line 0 indent
- All methods should be indented 1 level (4 spaces)

#### 1B. Create `core/agents/todoist/__init__.py`

```python
"""
TodoistAgent - GTD Personal Assistant

This package manages a Todoist system following strict GTD methodology.
"""

from .core import TodoistAgent

__all__ = ['TodoistAgent']
```

#### 1C. Update `core/agents/todoist.py` (original file)

Replace entire content with:
```python
"""
Backward compatibility wrapper for TodoistAgent.

Import from core.agents.todoist instead.
"""

from .todoist import TodoistAgent

__all__ = ['TodoistAgent']
```

### Validation:

```bash
# Check file was created
wc -l /home/bryceg/synapse/core/agents/todoist/core.py  # Should be ~400-500 lines

# Test import works
python3 -c "
from core.agents.todoist import TodoistAgent
print('✅ Import successful')
"

# Test basic instantiation (will fail on API call, but should import)
python3 -c "
import os
os.environ['TODOIST_API_TOKEN'] = 'fake_token_for_test'
from core.agents.todoist.core import TodoistAgent
print('✅ Core module accessible')
"
```

**If validation fails**: Report error to big model, don't proceed.

---

## Mini-Task 2: Extract Data Access Layer
**Time**: 40 minutes | **Cost**: $0.004

**Objective**: Extract all data access helper methods.

### What to Extract (EXACT LINES):

**Lines 76-83**: `_get_projects()`
**Lines 85-91**: `_find_project_by_name()`
**Lines 93-101**: `_get_sections()`
**Lines 103-109**: `_find_section_by_name()`
**Lines 111-116**: `_get_labels()`
**Lines 118-132**: `_get_tasks_list()`
**Lines 1239-1250**: `_get_subtasks()`

### Step-by-Step Instructions:

#### 2A. Create `core/agents/todoist/data_access.py`

```python
"""
Data access layer for Todoist API.

Handles caching and low-level API calls.
"""

from typing import Optional
from todoist_api_python.models import Task, Project, Section, Label


# These methods will be mixed into TodoistAgent via inheritance pattern
# They access self.api, self._projects_cache, etc.

def _get_projects(self) -> list[Project]:
    """Get all projects, using cache if available."""
    # PASTE LINES 77-83 HERE (body of method)

def _find_project_by_name(self, project_name: str) -> Optional[Project]:
    """Find a project by name (case-insensitive)."""
    # PASTE LINES 86-91 HERE

# ... continue for all methods listed above
```

**WAIT!** This approach won't work for small models. Let me reconsider...

#### Better Approach: Keep as methods in core.py, mark for future extraction

Actually, I realize the issue: **methods that use `self.api` and `self._cache` can't easily be in separate files** unless we:
1. Use mixins (complex for small model)
2. Keep them all in core.py (defeats purpose)
3. Make them standalone functions that take `agent` parameter (requires refactoring all call sites)

**STOP HERE - THIS NEEDS BIG MODEL DECISION**

---

## 🚨 CRITICAL ISSUE IDENTIFIED

The current plan has a **fundamental architectural problem**:

### The Problem:

Methods like `_get_projects()` access:
- `self.api` (Todoist API instance)
- `self._projects_cache` (instance variable)
- `self.timezone` (instance variable)

If we move them to `data_access.py`, we have these options:

#### Option A: Mixin Classes (Complex)
```python
# data_access.py
class DataAccessMixin:
    def _get_projects(self):
        # Can access self.api because this will be mixed in
        ...

# core.py
class TodoistAgent(BaseAgent, DataAccessMixin, TaskMixin, etc.):
    ...
```
**Pros**: Clean separation
**Cons**: Requires small model to understand mixins, complex inheritance

#### Option B: Keep Related Methods Together (Simpler)
```python
# core.py - Keep __init__ + all _helper methods
# task_management.py - Keep public CRUD methods (create_task, update_task, etc.)
# wizards.py - Keep wizard methods
# gtd_workflow.py - Keep GTD workflow methods
```
**Pros**: Much simpler for small model
**Cons**: core.py still large (~800-1000 lines)

#### Option C: Dependency Injection (Refactor-heavy)
```python
# data_access.py
def get_projects(api, cache):
    ...

# core.py
class TodoistAgent:
    def create_task(self, ...):
        projects = get_projects(self.api, self._projects_cache)
```
**Pros**: True separation
**Cons**: Requires refactoring 100+ call sites

---

## RECOMMENDATION FOR BIG MODEL

**I recommend Option B** for the following reasons:

1. **Small models can execute it** - Just copy methods to new files
2. **No complex inheritance** - Simple imports
3. **Still achieves main goal** - Splits 2897 lines into manageable chunks:
   - `core.py`: ~800 lines (class + helpers)
   - `task_management.py`: ~600 lines (CRUD public methods)
   - `wizards.py`: ~600 lines (wizard methods)
   - `gtd_workflow.py`: ~600 lines (GTD workflow)
   - `knowledge.py`: ~300 lines (knowledge methods)

4. **Token savings still significant**:
   - Before: 15,000 tokens (read whole file)
   - After: 4,000 tokens (read core.py only)
   - Or: 3,000 tokens (read task_management.py only)
   - **Savings**: ~73% when reading specific modules

### Revised Module Split (Option B):

```
core/agents/todoist/
├── __init__.py              # Public exports (50 lines)
├── core.py                  # TodoistAgent class + ALL helper methods (~800 lines)
│                           # Includes: __init__, _get_projects, _success, etc.
├── task_management.py       # Public CRUD methods (~600 lines)
│                           # create_task, update_task, list_tasks, etc.
├── wizards.py              # Wizard methods (~600 lines)
│                           # make_actionable, process_wizard_output, etc.
├── gtd_workflow.py         # GTD workflow (~600 lines)
│                           # list_next_actions, process_inbox, etc.
└── knowledge.py            # Knowledge methods (~300 lines)
                            # query_rules, update_rules
```

### How This Works:

```python
# core.py
class TodoistAgent(BaseAgent):
    def __init__(self, config):
        # All initialization

    def _get_projects(self):
        # Helper stays here

    # Import public methods from other modules
    from .task_management import (
        create_task,
        update_task,
        list_tasks,
        # etc.
    )
    # Attach to class (Python allows this)
    create_task = create_task
    update_task = update_task
```

**WAIT** - That won't work either for methods that need `self`.

---

## THE REAL SOLUTION: Method Forwarding

After deeper analysis, here's what will actually work for a small model:

### Approach: Keep Class in One File, Extract Logic to Functions

```python
# core.py - The TodoistAgent class shell
class TodoistAgent(BaseAgent):
    def __init__(self, config):
        # All initialization

    # Public methods are thin wrappers
    def create_task(self, **kwargs):
        from .task_management import create_task_impl
        return create_task_impl(self, **kwargs)

    def make_actionable(self, **kwargs):
        from .wizards import make_actionable_impl
        return make_actionable_impl(self, **kwargs)

# task_management.py - Implementation functions
def create_task_impl(agent: 'TodoistAgent', content: str, ...):
    """Implementation of create_task."""
    # Access agent.api, agent._get_projects(), etc.
    projects = agent._get_projects()
    agent.api.create_task(...)
    return agent._success("Task created", ...)
```

**THIS IS TOO COMPLEX FOR SMALL MODEL**

---

## FINAL RECOMMENDATION

**The original plan is too ambitious for small models without a clearer architecture.**

### What Big Model Should Do:

1. **Decide on architecture**:
   - Option A: Mixin classes (need clear examples)
   - Option B: Keep helpers in core, split public methods (simpler)
   - Option C: Implementation functions pattern (medium complexity)

2. **Create ONE complete example**:
   - Show exactly how to move ONE method (e.g., `create_task`)
   - Include: extraction, imports, testing
   - Small model can replicate pattern 40+ times

3. **Provide a method-to-module mapping**:
   ```
   create_task() → task_management.py
   update_task() → task_management.py
   make_actionable() → wizards.py
   # etc. for all 47 methods
   ```

4. **Create template files**:
   - `task_management.py.template` with imports/structure
   - Small model just fills in method bodies

---

## REVISED MINI-TASKS (After Big Model Decides Architecture)

### Proposed Simple Approach (My Recommendation):

**Use Python's class method attachment** - Keep it simple:

```python
# core.py - Minimal class
class TodoistAgent(BaseAgent):
    def __init__(self, config):
        # All initialization code
        pass

# task_management.py - Methods defined here
def create_task(self, content: str, ...):
    """Create a task."""
    # Implementation

def update_task(self, task_id: str, ...):
    """Update a task."""
    # Implementation

# At end of task_management.py - Attach to class
TodoistAgent.create_task = create_task
TodoistAgent.update_task = update_task

# __init__.py - Wire it all up
from .core import TodoistAgent
import .task_management  # Attaches methods
import .wizards          # Attaches methods
import .gtd_workflow     # Attaches methods
import .knowledge        # Attaches methods
```

**This works because**:
- Small model just copies method as-is
- Methods keep `self` parameter
- Import at package level wires everything up
- No complex inheritance or forwarding

---

## QUESTIONS FOR BIG MODEL

1. **Which architectural approach should we use?**
   - Mixin classes?
   - Method attachment (my recommendation)?
   - Implementation functions?
   - Keep it simple (just split into smaller files, accept core.py is ~800 lines)?

2. **Should we create one complete example first?**
   - Extract just `create_task()` end-to-end
   - Validate it works
   - Then small model replicates 46 more times?

3. **Do we need to update the plan with exact code templates?**
   - Small models need copy-paste instructions
   - Not just "move these methods"

---

## MY ASSESSMENT

**The original plan would cause small models to:**
- ❌ Get confused about imports
- ❌ Create circular dependencies
- ❌ Break `self.` method calls
- ❌ Not know how to wire up modules
- ❌ Create code that doesn't run

**What small models need:**
- ✅ Copy this exact code block
- ✅ Paste it here
- ✅ Run this command
- ✅ See this output = success
- ✅ If error, report to big model

**Bottom line**: We need to decide architecture first, then I can create a bulletproof plan.
