# Mini-Project 003: Tool Docstring Compression
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 3,000 input + 1,000 output per task
**Estimated Cost**: $0.002 total (Haiku)
**Priority**: 🎯 HIGH (Phase 2: Immediate Wins - 600 tokens saved)
**Time**: 1-2 hours total (spread across 4 mini-tasks)
**Impact**: 15-25% additional savings (~7% overall reduction)

---

## Problem Statement

**Phase 1 completed**: Your `todoist.py` was split into modules, saving 2,000+ tokens.

**Current Issue**: All 34 public methods in the TodoistAgent still have verbose docstrings that get sent in every API call. Tool docstrings include:
- Implementation details (validation logic, API calls)
- Code examples in docstrings
- Parameter breakdowns that LLM knows from type hints
- Step-by-step processing instructions

**Example** (from `make_actionable` in wizards.py):
```python
def make_actionable(self, task_id: str, location: Literal["home", "house", "yard", "errand", "bunnings", "parents"], activity: Literal["chore", "maintenance", "call", "email", "computer"]) -> str:
    """
    Move task to Next Actions with location and activity context.

    This is the GTD-native tool for processing inbox tasks into actionable items.
    It enforces proper workflow by constraining context choices to valid enums.

    Location specifies WHERE the task happens (physical or virtual context).
    Activity specifies WHAT TYPE of action is required.

    Implementation details:
    - Validates task exists
    - Moves to Next Actions project
    - Adds both location and activity labels
    - Preserves priority, due dates, etc.

    Args:
        task_id: The ID of the task to make actionable
        location: WHERE task happens (home, house, yard, errand, bunnings, parents)
        activity: WHAT type of action (chore, maintenance, call, email, computer)

    Returns:
        JSON with status and task details
    """
    # Move verbose details to code comments later
    return self._success("Processing complete")
```

---

## Solution Overview

**Compress Every Tool Docstring** by:
- ✅ Keep 1-line user-facing description
- ❌ Remove implementation details (move to code comments)
- ❌ Remove verbose parameter explanations (LLM sees type hints)
- ❌ Remove code examples (too token-heavy)
- ❌ Remove step-by-step instructions

**Resulting Savings**: ~600 tokens (20-30 tokens per method × 25 methods)

---

## Architecture: Compressed Docstring Pattern

### Before (Verbose):
```python
def make_actionable(self, task_id: str, location: Literal[...], activity: Literal[...]) -> str:
    """
    Move task to Next Actions with location and activity context.

    This is the GTD-native tool for processing inbox tasks into actionable items.
    It enforces proper workflow by constraining context choices to valid enums.

    Location specifies WHERE the task happens (physical or virtual context).
    Activity specifies WHAT TYPE of action is required.

    Implementation details:
    - Validates task exists
    - Moves to Next Actions project
    - Adds both location and activity labels
    - Preserves priority, due dates, etc.

    Args:
        task_id: The ID of the task to make actionable
        location: WHERE task happens (home, house, yard, errand, bunnings, parents)
        activity: WHAT type of action (chore, maintenance, call, email, computer)

    Returns:
        JSON with status and task details
    """
```

### After (Compressed):
```python
def make_actionable(self, task_id: str, location: Literal[...], activity: Literal[...]) -> str:
    """Move inbox task to Next Actions with location/activity context."""
    # Implementation:
    # - Validates task exists via self._get_task()
    # - Moves to Next Actions project via update_task()
    # - Adds location/activity labels
    # - Preserves priority, due dates, etc.
```

---

## Mini-Tasks Breakdown

### Mini-Task 0: Setup & Analysis (10 min, $0.000)
- Create working directory
- Count current docstring tokens
- Identify all method docstrings to compress
- **Critical**: Document current token count for measurement

### Mini-Task 1: Wizard Methods Compression (25 min, $0.002)
- Compress 8 wizard methods in `wizards.py`
- Move implementation details to code comments
- Keep only essential descriptions

### Mini-Task 2: Task Management Compression (30 min, $0.002)
- Compress 14 CRUD methods in `task_management.py`
- Compress 4 listing methods
- Optimize for brevity

### Mini-Task 3: Workflow & Quick Capture Compression (25 min, $0.002)
- Compress 8 GTD workflow methods in `gtd_workflow.py`
- Compress 2 quick capture methods in `quick_capture.py`
- Finalize knowledge methods if any remain

### Mini-Task 4: Validation & Testing (15 min, $0.001)
- Measure token reduction
- Ensure functionality preserved
- Test imports work
- Verify methods still accessible

**Total Time**: 1-2 hours
**Total Cost**: $0.005-0.010

---

## Implementation Strategy

### 1. Maintain User-Facing Clarity
**✅ Keep**: Short, clear descriptions that tell user what the tool does
**❌ Remove**: Code patterns, implementation steps, redundant parameter docs

Example:
```python
# GOOD (keep):
"""Move inbox task to Next Actions with location/activity context."""

# BAD (remove):
"""Move task to Next Actions with location and activity context.
This is the GTD-native tool for processing inbox tasks into actionable items.
It enforces proper workflow by constraining context choices to valid enums.
[...]"""
```

### 2. Convert Implementation Details to Comments
**Pattern**: Move verbose implementation details to `#` comments after the docstring

Example:
```python
def make_actionable(self, task_id: str, location: Literal[...], activity: Literal[...]) -> str:
    """Move inbox task to Next Actions with location/activity context."""
    # Implementation: Validates task exists, moves to Next Actions project,
    # adds location and activity labels, preserves priority and due dates
```

### 3. Remove Redundant Parameter Documentation
**LLM already sees**: Python type hints (`task_id: str`, `location: Literal[...]`)
**So don't repeat in docstring**: Parameter descriptions that mirror type hints

### 4. Preserve Critical Information
**✅ Keep**: Information not obvious from type hints
**✅ Keep**: Error conditions or return value formats if non-obvious

---

## Expected Token Reduction

### Current Tool Docstrings (Aggregate):
- **lines of docstring text**: ~1,200 lines (total)
- **tokens per docstring**: ~20-40 tokens each
- **total tokens**: ~600-800 tokens

### After Compression:
- **lines of docstring text**: ~200 lines (1-2 lines per method)
- **tokens per docstring**: ~5-10 tokens each
- **total tokens**: ~150-250 tokens

**Net Savings**: **~400-600 tokens** (20-30 tokens per method × 25 methods)

---

## Editing Mechanics

### Pattern for Each Method:
1. **Read current docstring**
2. **Identify 1-line essential description**
3. **Move implementation details to `# Implementation:` comments**
4. **Remove parameter breakdowns (LLM sees type hints)**
5. **Remove return value details (usually obvious)**
6. **Verify functionality intact**

### Example Method-by-Method:
```python
#### Before (wizards.py - make_actionable):
def make_actionable(self, task_id: str, location: Literal[...], activity: Literal[...]) -> str:
    """
    Move task to Next Actions with location and activity context.

    This is the GTD-native tool for processing inbox tasks into actionable items.
    It enforces proper workflow by constraining context choices to valid enums.

    Location specifies WHERE the task happens (physical or virtual context).
    Activity specifies WHAT TYPE of action is required.

    Implementation details:
    - Validates task exists
    - Moves to Next Actions project
    - Adds both location and activity labels
    - Preserves priority, due dates, etc.

    Args:
        task_id: The ID of the task to make actionable
        location: WHERE task happens
        activity: WHAT type of action

    Returns:
        JSON with status and task details
    """

#### After:
def make_actionable(self, task_id: str, location: Literal[...], activity: Literal[...]) -> str:
    """Move inbox task to Next Actions with location/activity context."""
    # Implementation: Validates task exists, moves to Next Actions project,
    # adds location and activity labels, preserves priority, due dates, etc.
```

---

## Validation Strategy

### Token Measurement:
```bash
# Before compression (baseline)
./synapse todoist_full
> help
# Check "Tool schemas: XXXX tokens"

# After each mini-task
./synapse todoist_full
> help
# Verify reduction matches expectations

# Final validation
# Expected: 600 ± 100 tokens reduction
```

### Functionality Validation:
```python
# Test imports work
from core.agents.todoist import TodoistAgent

# Test basic functionality
agent = TodoistAgent({"timezone": "US/Pacific", "api_key": None})
result = agent.get_current_time()
print(result)  # Should output current time

# Test compressed methods still work (dry run)
result = agent._compress_task(mock_task)
print(result)  # Should compress properly
```

---

## Safety Features

### Backup Strategy:
- Original docstrings preserved in git history
- Each mini-task creates git commit
- Emergency rollback: `git checkout HEAD~1 -- core/agents/todoist/`

### Incremental Validation:
- Test after each mini-task (don't batch)
- Verify tool schemas still load
- Check agents still instantiable
- Run smoke tests for compressed methods

---

## Success Criteria

### ✅ Must Pass:
- [ ] All 34+ methods have compressed docstrings (< 2 lines each)
- [ ] Implementation details moved to `#` comments
- [ ] Tool schemas load successfully
- [ ] Agent instantiates without errors
- [ ] Token usage reduced by 400-600 tokens
- [ ] Functionality preserved (no broken imports)

### File Impact:
- `wizards.py`: 8 methods compressed (150-200 tokens saved)
- `task_management.py`: 18 methods compressed (300-400 tokens saved)
- `gtd_workflow.py`: 8 methods compressed (150-200 tokens saved)
- `quick_capture.py`: 2 methods compressed (50 tokens saved)

---

## For Small Models

### What to Do:
1. ✅ Read one module at a time (`wizards.py` first)
2. ✅ Compress docstrings method by method
3. ✅ Keep all `# Implementation:` comments
4. ✅ Test imports after each mini-task
5. ✅ Report token reduction measurements

### What NOT to Do:
1. ❌ Don't remove implementation comments
2. ❌ Don't compress docstrings below 1 line
3. ❌ Don't change method signatures
4. ❌ Don't skip validation steps
5. ❌ Don't proceed if imports fail

---

## Validation Pattern

Each mini-task tests:
1. **Import test**: `from core.agents.todoist import TodoistAgent` → ✅ Success
2. **Schema load**: `agent.tools` loads without errors → ✅ Success
3. **Method access**: `agent.make_actionable` exists → ✅ Success
4. **Token count**: Measure via `./synapse to > help` → ✅ Reduced

---

## Next Steps After Completion

**Task Data Compression** (Mini-Project 004):
- Compress full Todoist task objects to abbreviated format
- Save 2,300-4,600 tokens per interaction
- Update system prompt with abbreviated field meanings

**Specialized Agent Creation** (Mini-Project 005):
- Create `todoist_inbox.yaml` (inbox only - 5 tools)
- Create `todoist_review.yaml` (review only - 7 tools)
- Save 1,800-2,200 tokens when using specialized agents

---

## Ready to Execute

**First Command**:
```bash
# Create working analysis
./synapse todoist_full
> help
# Note current token count in output
```

**Time to Completion**: 1-2 hours across mini-tasks
**Cost**: $0.002-0.005 per Haiku
**Impact**: Enables 15-25% additional token savings