# Mini-Project 002: Split Todoist Agent
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 15,000 input + 5,000 output
**Estimated Cost**: $0.01-0.02 (Haiku)
**Priority**: 🔴 CRITICAL (delivers 70% AI maintenance savings)
**Time**: 4-6 hours total (spread across 8 mini-tasks)
**Platform**: Linux (with Python 3.8+)

---

## Overview

**Problem**: `core/agents/todoist.py` is a monolithic 2,897-line file (confirmed). Every AI session working on Synapse reads this entire file (15,000 tokens), wasting tokens even when only using 10-20% of the functionality.

**Solution**: Split into 6 focused modules averaging 480 lines each. When an AI needs task management, it reads only the Task Management module (~3,000 tokens) instead of the full file (15,000 tokens).

**Impact**:
- **Before**: Any Synapse code work = 15,000 tokens (read whole file)
- **After**: Task work = 3,000 tokens (read 1 module), Core changes = 2,000 tokens, etc.
- **Savings**: 70% reduction per session ($0.015-0.02 → $0.005-0.007)
- **Additional Benefits**: Better maintainability, easier testing, clearer dependencies

**Structure After Split**:
```
core/agents/
├── todoist/
│   ├── __init__.py              # Public exports
│   ├── core.py                  # Infrastructure (480 lines)
│   ├── data_access.py           # API helpers (480 lines)
│   ├── task_management.py       # CRUD operations (480 lines)
│   ├── knowledge.py             # Learning/rules (480 lines)
│   ├── wizards.py               # Wizard processing (480 lines)
│   └── gtd_workflow.py          # High-level GTD (480 lines)
├── base.py                      # Unchanged
└── todoist.py                   # Thin wrapper → moved to todoist/__init__.py
```

---

## 8 Mini-Tasks (Bite-Sized for Small Models)

### Mini-Task 1: Create Module Structure & Core Module
**Time**: 30 minutes | **Cost**: $0.003 | **Lines**: +480

**Objective**: Set up the 6-module structure and extract core infrastructure.

**What to do**:
1. Create `/core/agents/todoist/` directory
2. Create `__init__.py` with base imports
3. Move core classes to `core.py`:
   - `TodoistAgent` class (infrastructure only)
   - `__init__()`, `_check_tasks_without_next_actions()`
   - Basic caches (`_projects_cache`, etc.)
   - Utility methods (`_success()`, `_error()`, `get_current_time()`)

**Validation**:
```bash
# Test basic import works
python -c "from core.agents.todoist.core import TodoistAgent; print('Core import: OK')"
# Check file sizes
wc -l core/agents/todoist/core.py
```

### Mini-Task 2: Extract Data Access Layer
**Time**: 30 minutes | **Cost**: $0.003

**Objective**: Extract all Data Access methods to their own module.

**Methods to move** (lines ~76-184 based on actual file):
- `_get_projects()`, `_get_sections()`, `_get_labels()`
- `_find_project_by_name()`, `_find_section_by_name()`
- `_get_tasks_list()` and related data access

**Target file**: `core/agents/todoist/data_access.py`

**Validation**:
```bash
wc -l core/agents/todoist/data_access.py
python -c "from core.agents.todoist.data_access import _get_projects; print('Data access: OK')"
```

### Mini-Task 3: Extract Task Management Core
**Time**: 40 minutes | **Cost**: $0.004

**Objective**: Extract core task CRUD operations.

**Methods to move**:
- `create_task()`, `list_tasks()`, `get_task()`
- `update_task()`, `complete_task()`, `delete_task()`
- `add_comment()`, `reopen_task()`

**Target file**: `core/agents/todoist/task_management.py`

**Import dependencies**:
- Needs data access (projects, labels, sections)
- Add imports at top of file

### Mini-Task 4: Extract Project/Section Management
**Time**: 30 minutes | **Cost**: $0.003

**Methods to move**:
- `move_task()`, `batch_move_tasks()`
- `list_projects()`, `list_sections()`, `list_labels()`
- `get_comments()`

**Target file**: Add to `task_management.py` (extend it)

**Note**: These build on CRUD operations, so group them logically.

### Mini-Task 5: Extract Knowledge & Learning
**Time**: 35 minutes | **Cost**: $0.004

**Methods to move**:
- `query_rules()`, `update_rules()`
- Knowledge file management
- Learning protocol methods

**Target file**: `core/agents/todoist/knowledge.py`

### Mini-Task 6: Extract Quick Entry & Capture
**Time**: 25 minutes | **Cost**: $0.003

**Methods to move**:
- `capture()`, `add_grocery()`
- Simple input processing methods

**Target file**: Add to main `task_management.py` (keep simple methods together)

### Mini-Task 7: Extract Wizard Processing Logic
**Time**: 45 minutes | **Cost**: $0.005

**Objective**: Extract complex wizard and decision-making logic.

**Methods to move**:
- `make_actionable()`, `ask_question()`
- `process_wizard_output()`, `schedule_task()`
- `_calculate_reminder_time()`, time utilities
- Reminder setting methods

**Target file**: `core/agents/todoist/wizards.py`

**Note**: This is the most complex extraction due to interdependencies.

### Mini-Task 8: Extract GTD Workflow
**Time**: 50 minutes | **Cost**: $0.005

**Methods to move**:
- `list_next_actions()`, `find_tasks_without_next_actions()`
- `process_inbox()`, `review_tasks_without_next_actions()`
- `_process_no_next_action_review()`,workflow orchestration
- Natural date parsing (`_parse_natural_date()`)
- Task formatting suggestions

**Target file**: `core/agents/todoist/gtd_workflow.py`

**Note**: This builds on wizards but focuses on high-level GTD operations.

---

## Acceptance Criteria (ALL must pass)

### Functional Tests
- [ ] Agent import works: `from core.agents.todoist import TodoistAgent`
- [ ] Agent initialization completes without errors
- [ ] All 7 modules exist (including `__init__.py`)
- [ ] Each module is 400-600 lines
- [ ] Core functionality works: `get_current_time()`, `list_tasks()`
- [ ] Auto-check runs on startup: `find_tasks_without_next_actions()`

### File Structure
```bash
# Directory structure
core/agents/
├── todoist/
│   ├── __init__.py         # 50-100 lines
│   ├── core.py             # 400-500 lines
│   ├── data_access.py      # 400-500 lines
│   ├── task_management.py  # 500-600 lines
│   ├── knowledge.py        # 400-500 lines
│   ├── wizards.py          # 500-600 lines
│   └── gtd_workflow.py     # 500-600 lines
└── todoist.py              # Moved to __init__.py
```

### Token Savings Verification
- [ ] Single module reads: ~3,000 tokens vs 15,000
- [ ] Import overhead: minimal (only used modules loaded)
- [ ] Full agent functionality preserved

---

## Implementation Rules

### Import Strategy
**DO NOT** have circular imports. Structure imports hierarchically:
1. **Core** → can import from data_access
2. **Data Access** → no complex dependencies
3. **Task Management** → imports core + data_access
4. **Others** → import as needed

**Example imports**:
```python
# core.py
from .data_access import _get_projects, _get_labels
from .knowledge import query_rules  # OK: knowledge is simple

# wizards.py
from .task_management import create_task
from .core import TodoistAgent
```

### Wrapper Pattern
The `core/agents/todoist.py` file becomes a thin wrapper:
```python
# core/agents/todoist.py (after split)
from .todoist.core import TodoistAgent  # Re-export for backward compatibility
```

And `core/agents/todoist/__init__.py` becomes the main interface.

### Validation Commands
```bash
# Quick size check
find core/agents/todoist -name "*.py" -exec wc -l {} + | sort -n

# Functional test
python -c "
from core.agents.todoist import TodoistAgent
agent = TodoistAgent({'timezone': 'UTC'})
print('Agent init: OK')
print('Time:', agent.get_current_time())
"

# Import test all modules
python -c "
from core.agents.todoist.core import TodoistAgent
from core.agents.todoist.data_access import _get_projects
from core.agents.todoist.task_management import create_task
from core.agents.todoist.knowledge import query_rules
from core.agents.todoist.wizards import make_actionable
from core.agents.todoist.gtd_workflow import list_next_actions
print('All imports: OK')
"
```

---

## Success Report Template

```markdown
## Mini-Project 002: Split Todoist Agent - SUCCESS ✅

**Model**: Claude 3.5 Haiku
**Tokens**: XXX input + YYY output
**Cost**: $Z.ZZ
**Total Time**: 4.5 hours (across 8 mini-tasks)

**Results**:
- ✅ 6 modules created (400-600 lines each)
- ✅ Total lines: ~2,900 (preserved)
- ✅ All imports work
- ✅ Core functionality tested
- ✅ No regressions detected

**Savings Achieved**:
- Single module read: ~3,000 tokens (vs 15,000)
- Session cost reduction: 70%
- Future AI maintenance: $0.005-0.007 per session

**Updated Files**:
- `core/agents/todoist.py` → Thin wrapper
- Created `core/agents/todoist/` with 6 focused modules

**Ready for**: Tool docstring compression (Phase 3)
```

---

## Important Notes

### For Small Models
- Each mini-task is completely self-contained
- Clear validation commands for each step
- If validation fails, report exact error to big model
- Do NOT try to fix problems - return control to big model

### Risk Mitigation
- Keep original `todoist.py` as backup during development
- Test each mini-task before proceeding
- Big model validates after each mini-task completion
- Full rollback to original possible if needed

### Optimization Benefits
- **Today**: 70% AI cost reduction
- **Month-over-month**: $1.35 savings ($3.60 → $2.25)
- **Maintainability**: 6x easier to find/change code
- **Testing**: Each module can be unit tested separately

---

## Ready to Execute

**First Mini-Task**: Create directory structure and extract core infrastructure

**Cost analysis calculates to $0.02 total for full project** (split across 8x $0.002-0.005 tasks)

**Next**: After this completes, tool docstring compression (Phase 3) for additional 30% savings.
