# Big-to-Small AI Delegation Workflow
**Purpose**: Use expensive models for planning, cheap models for execution
**Savings**: 50-70% on large projects
**Pattern**: Sonnet plans → Haiku executes → Sonnet verifies

---

## 🎯 Core Concept

**Expensive models** (Claude 3.5 Sonnet, GPT-4) are great at:
- ✅ Understanding complex systems
- ✅ Making architectural decisions
- ✅ Exploring unfamiliar code
- ✅ Creating comprehensive plans
- ✅ Debugging subtle issues

**Cheap models** (Claude 3.5 Haiku, GPT-4o-mini) are great at:
- ✅ Following precise instructions
- ✅ Repetitive edits
- ✅ Executing well-defined tasks
- ✅ Running tests
- ✅ Simple refactoring

**The Pattern**: Big model creates perfect instructions, small model follows them.

---

## 💰 Cost Comparison

### Model Pricing (As of 2025-10)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | Planning, exploration, debugging |
| **Claude 3.5 Haiku** | $0.25 | $1.25 | Execution, repetitive tasks |
| **GPT-4o** | $2.50 | $10.00 | Planning (slightly cheaper) |
| **GPT-4o-mini** | $0.15 | $0.60 | Execution (cheapest) |

**Savings Example** (Split todoist.py into 6 files):

**All Sonnet Approach**:
```
1. Exploration: 40,000 input + 10,000 output = $0.27
2. Planning: 20,000 input + 8,000 output = $0.18
3. Execution (6 files): 90,000 input + 15,000 output = $0.49
4. Testing: 15,000 input + 3,000 output = $0.09
Total: $1.03
```

**Delegated Approach**:
```
1. Exploration (Sonnet): 40,000 input + 10,000 output = $0.27
2. Planning (Sonnet): 20,000 input + 12,000 output = $0.24
3. Execution (Haiku, 6 tasks): 18,000 input + 6,000 output = $0.01
4. Testing (Haiku): 4,000 input + 1,000 output = $0.002
5. Verification (Sonnet): 10,000 input + 2,000 output = $0.06
Total: $0.582

Savings: $0.45 (44%)
```

At scale (10 large projects/month): **$4.50/month saved**

---

## 🔄 The Three-Phase Pattern

### Phase 1: Planning (Big Model)

**Model**: Claude 3.5 Sonnet or GPT-4
**Goal**: Understand problem, explore codebase, create atomic tasks
**Time**: 30-60 minutes
**Cost**: $0.20-0.50

#### Steps:

1. **Understand the Goal**
   ```
   User: "Split todoist.py into focused modules"

   Big Model:
   - Reads todoist.py (2,897 lines)
   - Analyzes class structure
   - Identifies logical groupings
   - Understands dependencies
   ```

2. **Explore Context**
   ```
   - How is TodoistAgent imported elsewhere?
   - What tests exist?
   - Are there similar patterns in the codebase?
   - What's the current file structure?
   ```

3. **Create Implementation Plan**
   ```markdown
   ## Plan: Split TodoistAgent into 6 Modules

   ### File Structure
   core/agents/todoist/
   ├── __init__.py (30 lines)
   ├── base.py (400 lines)
   ├── task_tools.py (600 lines)
   ├── gtd_tools.py (600 lines)
   ├── reminder_tools.py (400 lines)
   ├── knowledge_tools.py (500 lines)
   └── wizard_integration.py (300 lines)

   ### Dependencies
   - All modules import from base.py
   - No circular dependencies
   - Public API stays identical (import from __init__.py)
   ```

4. **Break into Mini-Tasks**
   ```
   Task 1: Create directory structure & __init__.py
   Task 2: Extract base TodoistAgent class to base.py
   Task 3: Extract task CRUD tools to task_tools.py
   Task 4: Extract GTD workflow tools to gtd_tools.py
   Task 5: Extract reminder tools to reminder_tools.py
   Task 6: Extract knowledge/learning tools to knowledge_tools.py
   Task 7: Extract wizard integration to wizard_integration.py
   Task 8: Update imports in test files
   Task 9: Verify imports work (smoke test)
   ```

5. **Create Mini-Task Specifications** (see template below)

---

### Phase 2: Execution (Small Model)

**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Goal**: Execute each mini-task precisely
**Time**: 5-15 minutes per task
**Cost**: $0.002-0.01 per task

#### Requirements for Small Model Success:

1. **Task is atomic** (one clear objective)
2. **Context is minimal** (read 1-2 files max)
3. **Instructions are precise** (no ambiguity)
4. **Success is verifiable** (clear acceptance criteria)

#### Example Mini-Task:

````markdown
# Mini-Task 2: Extract Base TodoistAgent Class

**Model**: Claude 3.5 Haiku
**Estimated Tokens**: 3,000 input + 800 output
**Files to Read**:
- `core/agents/todoist.py` (lines 1-100 only - __init__ and helpers)

**Files to Create**:
- `core/agents/todoist/base.py`

## Task

Create `core/agents/todoist/base.py` with the following content:

1. Copy imports from todoist.py (lines 1-15)
2. Copy TodoistAgent class definition (lines 18-25)
3. Copy __init__ method (lines 27-73)
4. Copy helper methods:
   - `_get_projects()` (lines 75-82)
   - `_find_project_by_name()` (lines 84-91)
   - `_get_sections()` (lines 92-99)
   - `_get_labels()` (lines 101-106)
   - `_success()` (lines 134-140)
   - `_error()` (lines 142-147)

5. Add module docstring:
```python
"""
TodoistAgent Base Class

Core TodoistAgent implementation including:
- API initialization
- Caching layer for projects/sections/labels
- Helper methods for success/error responses
- Timezone handling

All tool methods are in separate modules (task_tools, gtd_tools, etc.)
Import from __init__.py to get complete TodoistAgent with all tools.
"""
```

## Acceptance Criteria

- [ ] File created at `core/agents/todoist/base.py`
- [ ] Contains exactly the methods listed above
- [ ] Module docstring explains purpose
- [ ] No tool methods included (those go in other modules)
- [ ] Code is identical to original (no changes to logic)

## Validation

```bash
# File should exist
ls -lh core/agents/todoist/base.py

# Should be ~400 lines
wc -l core/agents/todoist/base.py

# Should contain TodoistAgent class
grep -q "class TodoistAgent" core/agents/todoist/base.py && echo "OK"
```

## Next Task

After completing this, move to Mini-Task 3: Extract Task Tools
````

**Small Model Executes**:
- Reads specified lines from todoist.py
- Creates new file exactly as specified
- Runs validation commands
- Reports success or failure

---

### Phase 3: Verification (Big Model)

**Model**: Claude 3.5 Sonnet or GPT-4
**Goal**: Ensure all changes work together, no regressions
**Time**: 15-30 minutes
**Cost**: $0.05-0.15

#### Steps:

1. **Review All Changes**
   ```bash
   git diff --stat
   # Review file-by-file
   ```

2. **Integration Testing**
   ```bash
   # Import still works
   python -c "from core.agents.todoist import TodoistAgent; print('OK')"

   # Run test suite
   python -m pytest tests/test_todoist_agent.py

   # Smoke test agent
   ./synapse to
   > get current time
   > exit
   ```

3. **Verify No Regressions**
   - All tests pass
   - Imports work from expected locations
   - Agent behavior unchanged
   - No new linting errors

4. **Commit & Push**
   ```bash
   git add core/agents/todoist/
   git commit -m "refactor: Split TodoistAgent into focused modules

   Improves token efficiency when AI works on Synapse:
   - Before: 15,000 tokens to read full todoist.py
   - After: 2,000-3,000 tokens to read relevant module
   - 70% reduction in context loading

   Structure:
   - base.py: Core class, init, helpers
   - task_tools.py: CRUD operations
   - gtd_tools.py: GTD workflow (capture, make_actionable)
   - reminder_tools.py: Reminders and routines
   - knowledge_tools.py: Learning and knowledge queries
   - wizard_integration.py: Inbox/review wizards

   Public API unchanged: still import from core.agents.todoist

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   Co-Authored-By: Claude <noreply@anthropic.com>"

   git push
   ```

5. **Update Documentation**
   - Update AI_OPTIMIZATION_GUIDE.md (mark Phase 1 complete)
   - Update TOKEN_OPTIMIZATION_STATUS.md (log savings)

---

## 📋 Mini-Task Specification Template

Use this template when creating tasks for small models:

````markdown
# Mini-Task [N]: [Clear, Concise Title]

**Model**: Claude 3.5 Haiku (or GPT-4o-mini)
**Estimated Tokens**: [X] input + [Y] output
**Estimated Cost**: $[Z]

**Files to Read**:
- `path/to/file.py` (lines X-Y)
- `path/to/other.py` (optional, lines A-B)

**Files to Create/Edit**:
- `path/to/new_file.py` (create)
- `path/to/existing.py` (edit lines 50-60)

---

## Context (100 words max)

[Just enough background to understand the task - no exploration needed]

Example:
"We're splitting todoist.py into modules. This task extracts the task CRUD
methods (create/update/complete/delete/list) into task_tools.py. These
methods are currently lines 203-850 in todoist.py."

---

## Task

[Precise, numbered steps - leave no ambiguity]

1. Create file `path/to/new_file.py`
2. Add module docstring (provided below)
3. Copy the following methods from `todoist.py`:
   - `create_task()` (lines 203-260)
   - `update_task()` (lines 262-340)
   - `complete_task()` (lines 342-365)
   - `delete_task()` (lines 367-390)
   - `list_tasks()` (lines 392-450)
4. Add imports at top:
   ```python
   from typing import Optional, Literal
   from todoist_api_python.models import Task
   ```
5. [Any other specific instructions]

---

## Code Snippets (if applicable)

Provide exact code to avoid ambiguity:

```python
"""
Module docstring goes here.
Explain what this module does.
"""

# Exact imports
from typing import Optional
import json

# Class stub if needed
class PartialClass:
    """Partial class definition"""
    pass
```

---

## Acceptance Criteria

- [ ] File created/edited as specified
- [ ] All specified methods included
- [ ] Imports correct and minimal
- [ ] No syntax errors (file is valid Python)
- [ ] Line count is approximately [X] lines (±50)
- [ ] [Any other specific checks]

---

## Validation

```bash
# Commands small model should run to verify success

# File exists and has correct size
ls -lh path/to/new_file.py
wc -l path/to/new_file.py  # Should be ~600 lines

# Contains expected methods
grep -q "def create_task" path/to/new_file.py && echo "create_task: OK"
grep -q "def update_task" path/to/new_file.py && echo "update_task: OK"
grep -q "def complete_task" path/to/new_file.py && echo "complete_task: OK"
grep -q "def delete_task" path/to/new_file.py && echo "delete_task: OK"
grep -q "def list_tasks" path/to/new_file.py && echo "list_tasks: OK"

# No syntax errors
python -m py_compile path/to/new_file.py && echo "Syntax: OK"
```

---

## On Failure

If validation fails:
1. Report exact error message
2. Do NOT attempt to fix (ask big model)
3. Include validation output in report

---

## Next Task

After validation passes, proceed to:
- Mini-Task [N+1]: [Next Task Title]

Or report completion if this is the last task.
````

---

## 🎯 When to Use This Pattern

### ✅ Good Use Cases

1. **Splitting large files** (like todoist.py)
   - Big model: Analyze structure, plan modules
   - Small model: Extract code to new files (6-8 tasks)
   - Savings: 40-60%

2. **Repetitive edits** (like compressing 50 docstrings)
   - Big model: Create template and pattern
   - Small model: Apply to each method (1 task)
   - Savings: 60-80%

3. **Documentation consolidation**
   - Big model: Analyze overlap, plan structure
   - Small model: Merge sections, delete files (3-4 tasks)
   - Savings: 50-70%

4. **Test creation**
   - Big model: Design test strategy
   - Small model: Generate test cases (1 task per module)
   - Savings: 40-60%

5. **Schema/config updates**
   - Big model: Design changes
   - Small model: Apply to each file (1 task per file)
   - Savings: 50-70%

---

### ❌ Bad Use Cases

1. **Debugging complex issues**
   - Requires exploration and reasoning
   - Small model will get stuck
   - Use big model throughout

2. **Architectural decisions**
   - Requires understanding tradeoffs
   - Small model lacks context
   - Use big model for design

3. **Exploratory work**
   - "Find all places where X is used"
   - Small model can't explore efficiently
   - Use big model's Explore agent

4. **One-off quick fixes**
   - Creating mini-tasks takes longer than just doing it
   - Use current model

5. **User interaction needed**
   - Small model can't make judgment calls
   - Use big model when user input likely

---

## 🎓 Best Practices

### For Big Model (Planning Phase)

1. **Be thorough in specifications**
   - Small model can't fill in blanks
   - Include exact line numbers
   - Provide code snippets
   - Clear acceptance criteria

2. **Make tasks atomic**
   - Each task = 1 clear objective
   - No dependencies between tasks (if possible)
   - Can be done in any order (ideal)

3. **Include validation commands**
   - Small model runs these to verify success
   - Catches errors early
   - Reduces big model verification time

4. **Estimate tokens**
   - Helps track if pattern is working
   - Alert if task is too large (split further)

---

### For Small Model (Execution Phase)

1. **Follow instructions exactly**
   - Don't add features or improvements
   - Don't explore or read extra files
   - Don't make decisions (ask if unclear)

2. **Run validation commands**
   - Always run the provided validation
   - Report results even if they pass
   - If fail, STOP and report to big model

3. **Report clearly**
   ```markdown
   ## Mini-Task 2: Extract Base Class - COMPLETE ✅

   **Created**: `core/agents/todoist/base.py` (402 lines)

   **Validation Results**:
   - File exists: ✅
   - Line count: 402 (target: ~400): ✅
   - Contains TodoistAgent class: ✅
   - Syntax valid: ✅

   **Ready for**: Mini-Task 3
   ```

4. **Don't fix failures**
   - If validation fails, report to big model
   - Big model will either fix spec or adjust task
   - Don't waste tokens debugging

---

## 📊 Tracking Success

### Metrics to Log

For each delegation project, track:

```markdown
## Project: [Name]
**Date**: 2025-10-18
**Goal**: [e.g., Split todoist.py into 6 modules]

### Token Usage

**Planning** (Claude 3.5 Sonnet):
- Exploration: 40,000 input + 10,000 output
- Plan creation: 20,000 input + 12,000 output
- Subtotal: 60,000 input + 22,000 output = $0.51

**Execution** (Claude 3.5 Haiku):
- Mini-task 1: 2,500 input + 600 output
- Mini-task 2: 3,200 input + 800 output
- Mini-task 3: 4,100 input + 900 output
- [... tasks 4-8 ...]
- Subtotal: 18,000 input + 6,000 output = $0.012

**Verification** (Claude 3.5 Sonnet):
- Review: 8,000 input + 1,500 output
- Testing: 3,000 input + 500 output
- Subtotal: 11,000 input + 2,000 output = $0.063

**Total**: $0.585

### Comparison

**If All Sonnet**: ~$1.05 (estimated)
**Actual Cost**: $0.585
**Savings**: $0.465 (44%)

### Learnings

- [What went well]
- [What could improve]
- [Template updates needed]
```

---

## 🔄 Iteration & Improvement

### After Each Project

1. **Review what worked**
   - Which mini-tasks were well-specified?
   - Did small model succeed on first try?
   - Were token estimates accurate?

2. **Update templates**
   - Add patterns that worked
   - Improve specification clarity
   - Better validation commands

3. **Adjust granularity**
   - Were tasks too large? (split more)
   - Were tasks too small? (combine)
   - Sweet spot: 2,000-5,000 tokens per task

4. **Document patterns**
   - Create reusable templates for common tasks
   - Build a library over time
   - Share learnings in this doc

---

## 📚 Example Projects

### Project 1: Split todoist.py (Full Example)

See `SPLIT_TODOIST_MINI_PROJECTS.md` for complete breakdown:
- 9 mini-tasks
- Estimated savings: 44%
- Actual time: [TBD]

### Project 2: Compress Docstrings (Full Example)

See `COMPRESS_DOCSTRINGS_MINI_PROJECT.md` for complete breakdown:
- 1 mini-task (batch operation)
- Estimated savings: 70%
- Actual time: [TBD]

### Project 3: Documentation Consolidation

See `CONSOLIDATE_DOCS_MINI_PROJECTS.md` for complete breakdown:
- 4 mini-tasks
- Estimated savings: 55%
- Actual time: [TBD]

---

## 🎯 Quick Decision Tree

```
Need to make code changes?
│
├─ Is it well-defined? (know exactly what to change)
│  ├─ Yes → Is it repetitive (10+ similar edits)?
│  │  ├─ Yes → USE DELEGATION (high savings)
│  │  └─ No → USE CURRENT MODEL (overhead not worth it)
│  │
│  └─ No → Need exploration?
│     ├─ Yes → USE BIG MODEL (exploration required)
│     └─ No → Ask user for clarification, then decide
│
└─ Is it a large project? (multiple files, complex)
   ├─ Yes → CAN I break into 5+ atomic tasks?
   │  ├─ Yes → USE DELEGATION (high savings)
   │  └─ No → USE BIG MODEL (too complex to delegate)
   │
   └─ No → USE CURRENT MODEL (quick fix)
```

---

## 🚀 Getting Started Checklist

To start using this pattern:

### Setup (One-Time)

- [ ] Read this document fully
- [ ] Review mini-task template
- [ ] Set up token tracking spreadsheet/log
- [ ] Create `mini-projects/` directory for task specs

### For Each New Project

- [ ] User requests change
- [ ] Decide: delegate or do directly? (use decision tree)
- [ ] If delegate:
  - [ ] **Phase 1** (Big Model): Explore, plan, create mini-tasks
  - [ ] **Phase 2** (Small Model): Execute each mini-task
  - [ ] **Phase 3** (Big Model): Verify, commit, update docs
  - [ ] **Log results**: Track token usage and savings

### After Project

- [ ] Log actual vs estimated tokens
- [ ] Update templates if needed
- [ ] Document learnings in this file

---

## 🔗 Related Documentation

- `AI_OPTIMIZATION_GUIDE.md` - Overall AI optimization strategy
- `TASK_TEMPLATES.md` - Library of reusable mini-task templates
- `SPLIT_TODOIST_MINI_PROJECTS.md` - Example project (splitting todoist.py)
- `TOKEN_OPTIMIZATION_STATUS.md` - Current priorities and status

---

**Last Updated**: 2025-10-18
**Status**: Initial version - ready to use
**First Project**: Split todoist.py (see SPLIT_TODOIST_MINI_PROJECTS.md)
**Feedback**: Update this doc after each delegation project
