# Mini-Project 002: Quick Reference

## What This Plan Does

Splits `core/agents/todoist.py` (2,897 lines) into 6 focused modules using the **Method Attachment Pattern**.

## Architecture: Method Attachment Pattern

```python
# wizards.py - Define methods normally with 'self'
def make_actionable(self, task_id, ...):
    """Make a task actionable."""
    # Use self.api, self._get_projects() - works normally!
    return self._success("Done")

# Attach to class at end of file
from .core import TodoistAgent
TodoistAgent.make_actionable = make_actionable

# __init__.py - Import modules (auto-attaches all methods)
from .core import TodoistAgent
import core.agents.todoist.wizards  # Side effect: methods attach
```

**Why this works for small models**:
- Methods stay exactly the same (keep `self` parameter)
- Small models just copy-paste methods
- No complex inheritance or mixins to understand
- Import system automatically wires everything

## Final Structure

```
core/agents/todoist/
├── __init__.py           ~30 lines   - Package imports
├── core.py              ~550 lines   - TodoistAgent class + helpers
├── task_management.py   ~570 lines   - 14 CRUD methods
├── knowledge.py         ~180 lines   - 2 knowledge methods
├── quick_capture.py      ~60 lines   - 2 quick entry methods
├── wizards.py           ~850 lines   - 11 wizard methods
└── gtd_workflow.py      ~850 lines   - 8 GTD workflow methods
```

## Token Savings

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Task work | 15,000 tokens | 3,000 | 80% |
| Wizard fix | 15,000 tokens | 4,500 | 70% |
| GTD update | 15,000 tokens | 4,500 | 70% |
| **Average** | **15,000** | **~3,500** | **77%** |

## Mini-Tasks Breakdown

### Task 0: Backup (2 min, $0.000)
- Create backup of original file
- Create target directory
- **Critical for safety**

### Task 1: Core Module (40 min, $0.004)
- Extract TodoistAgent class shell
- All helper methods (_get_projects, _success, etc.)
- Create __init__.py
- Update wrapper

### Task 2: Task Management (45 min, $0.004)
- 14 methods: create_task, list_tasks, etc.
- All CRUD operations
- Project/section/label listing

### Task 3: Knowledge (20 min, $0.002)
- 2 methods: query_rules, update_rules

### Task 4: Quick Capture (15 min, $0.002)
- 2 methods: capture, add_grocery

### Task 5: Wizards (50 min, $0.005)
- 11 methods: make_actionable, process_wizard_output, etc.
- Reminder calculations
- Wizard processing

### Task 6: GTD Workflow (50 min, $0.005)
- 8 methods: process_inbox, find_tasks_without_next_actions, etc.
- GTD methodology operations

**Total Time**: 3-4 hours
**Total Cost**: $0.015-0.025 (Haiku)

## Method Distribution

| Module | Public Methods | Private Helpers | Total Methods |
|--------|---------------|-----------------|---------------|
| core.py | 1 (get_current_time) | 12 helpers | 13 |
| task_management.py | 14 | 0 | 14 |
| knowledge.py | 2 | 0 | 2 |
| quick_capture.py | 2 | 0 | 2 |
| wizards.py | 8 public | 3 private | 11 |
| gtd_workflow.py | 7 public | 1 private | 8 |
| **TOTAL** | **34** | **16** | **50** |

## Safety Features

### Backup Strategy
- Original file preserved as `.backup`
- Can rollback at any time
- One command restores everything

### Incremental Validation
- Test after each mini-task
- Verify imports work
- Check method attachment
- Catch errors early

### Emergency Rollback
```bash
rm -rf core/agents/todoist/
mv core/agents/todoist.py.backup core/agents/todoist.py
```

## For Small Models

### What to Do
1. ✅ Follow instructions exactly
2. ✅ Use Read tool for exact line ranges
3. ✅ Copy code with exact indentation
4. ✅ Run validation after each task
5. ✅ Report errors immediately

### What NOT to Do
1. ❌ Don't modify code while copying
2. ❌ Don't try to fix errors
3. ❌ Don't skip validation
4. ❌ Don't proceed if tests fail
5. ❌ Don't guess line numbers

### Validation Pattern
Each mini-task has:
1. **Line ranges to copy** (exact)
2. **Code to paste** (exact location)
3. **Validation commands** (copy-paste)
4. **Expected output** (what success looks like)
5. **Error handling** (what to do if fails)

## Success Criteria

### Must Pass:
- [ ] All 6 modules created
- [ ] All 50 methods present on TodoistAgent
- [ ] Import test passes (no errors)
- [ ] No circular imports
- [ ] Agent can be instantiated
- [ ] Smoke test: agent responds to "get current time"

### File Sizes:
- core.py: ~550 lines
- task_management.py: ~570 lines
- knowledge.py: ~180 lines
- quick_capture.py: ~60 lines
- wizards.py: ~850 lines
- gtd_workflow.py: ~850 lines

## Why This Will Work

1. **Simple pattern**: Methods just get copied as-is
2. **Clear instructions**: Exact line numbers for everything
3. **Incremental testing**: Catch errors early
4. **Rollback safety**: Can undo at any time
5. **Method attachment**: Python supports this natively
6. **No refactoring**: Code stays identical

## Next Steps

1. **Review the full plan**: `/home/bryceg/synapse/mini-projects/002_SPLIT_TODOIST_FINAL.md`
2. **Execute with small model**: Use Haiku or GPT-4o-mini
3. **Follow mini-tasks in order**: Don't skip any
4. **Validate each step**: Use provided commands
5. **Big model reviews**: After completion

## Questions?

- **"Will this break anything?"** No - code stays identical, just in different files
- **"What if imports fail?"** Rollback procedure restores everything
- **"Can small models do this?"** Yes - it's just copy-paste with exact instructions
- **"What if a test fails?"** Small model reports to big model, doesn't try to fix
- **"How long will it take?"** 3-4 hours total across all mini-tasks

## Ready to Execute

The detailed plan is in: `002_SPLIT_TODOIST_FINAL.md`

First task: **Mini-Task 0** (create backup) - takes 2 minutes, critical for safety
