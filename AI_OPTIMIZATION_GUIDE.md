# AI Optimization Guide: Working on Synapse
**Purpose**: Minimize token costs when AI assistants (Claude Code, etc.) work on this project
**Created**: 2025-10-18
**Critical**: Read this BEFORE starting any work on Synapse

---

## 🎯 Core Principle

**When AI works on Synapse, every file read costs tokens. Bad organization = wasted money.**

This guide optimizes for:
1. **Minimal context loading** - AI reads only what's needed
2. **Fast navigation** - Clear structure = fewer file reads
3. **Efficient caching** - Claude Code caches frequently-read content
4. **Big-to-small delegation** - Expensive models plan, cheap models execute

---

## 📊 Current Token Costs (Baseline)

### When You (Claude Code) Work on Synapse

| Operation | Files Read | Token Cost | Why So High? |
|-----------|-----------|------------|--------------|
| Add new tool to TodoistAgent | 3-5 files | **18,000-25,000** | `todoist.py` is 2,897 lines - monolithic |
| Update workflow docs | 4-6 files | **13,500** | Docs scattered, redundant |
| Fix a bug | 2-4 files | **10,000-15,000** | Large files, unclear structure |
| Understand GTD workflow | 6+ files | **15,000-20,000** | Knowledge spread across files |

**Monthly cost at current pace**: ~$15-30 (150+ interactions)

**After optimization**: ~$3-8 (70% reduction)

---

## 🔴 CRITICAL ISSUES (Must Fix First)

### Issue 1: `todoist.py` is a 2,897-line Monolith

**File**: `/home/bryceg/synapse/core/agents/todoist.py`

**Problem**:
- Single file with 50+ methods (15,000-18,000 tokens per read)
- Every small change requires reading entire file
- 70% of AI work touches this file

**Impact**: **18,000 tokens per read** × 5 reads/day = 90,000 tokens/day waste

**Solution**: Split into focused modules (see Implementation Plan below)

---

### Issue 2: Documentation is Scattered & Redundant

**Current State**: 8 markdown files with overlapping content

| File | Lines | Overlap | Should Be |
|------|-------|---------|-----------|
| `LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md` | 967 | 60% with next 2 | Archived or merged |
| `TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md` | 530 | 70% with status | Merged to status |
| `TOKEN_OPTIMIZATION_STATUS.md` | 163 | Summary only | Keep (reference) |
| `claude.md` (root) | 612 | 50% with .claude/ | Delete (use .claude/ version) |
| `.claude/claude.md` | 80 | Outdated | Expand to 800-900 lines |
| `NO_NEXT_ACTION_WIZARD_FEATURE.md` | 744 | Design doc | Archive after shipping |
| `WIZARD_COMPLETE_DELETE_FEATURE.md` | 367 | Design doc | Archive after shipping |
| `EXPECTED_INTERACTION_FLOW.md` | 226 | Workflow | Merge to .claude/claude.md |

**Impact**: Reading workflow context = **13,500 tokens** (should be 4,500)

**Solution**: Consolidate to `.claude/claude.md` (single source of truth)

---

### Issue 3: Obsolete Knowledge Files

**Problem**:
- `/home/bryceg/synapse/knowledge/todoist_rules.md` (272 lines) - **DEPRECATED**
  - Contains "Weekly Review" (user does daily reviews)
  - Overlaps with `/home/bryceg/synapse/knowledge/todoistagent/learned_rules.md`

**Impact**: AI reads both, gets confused (+600 tokens wasted)

**Solution**: Delete obsolete file, consolidate to `knowledge/todoistagent/` only

---

## ✅ OPTIMIZATION STRATEGY

### Tier 1: File Structure (70% Token Reduction)

#### 1.1 Split `todoist.py` into Logical Modules

**Current**:
```
core/agents/todoist.py (2,897 lines)
```

**Optimized**:
```
core/agents/todoist/
├── __init__.py              (30 lines - exports TodoistAgent)
├── base.py                  (400 lines - TodoistAgent class, __init__, caching)
├── task_tools.py            (600 lines - create/update/complete/list/delete)
├── gtd_tools.py             (600 lines - capture/make_actionable/ask_question)
├── reminder_tools.py        (400 lines - set_reminder/routine_reminder/reset_overdue)
├── knowledge_tools.py       (500 lines - query_knowledge/update_rules/learning)
└── wizard_integration.py    (300 lines - process_inbox/review wizards)
```

**Token Savings**:
- Before: 15,000 tokens per read (always read full file)
- After: 2,000-3,000 tokens per read (read only relevant module)
- **Savings: 70-80% (10,000-12,000 tokens per session)**

**When to read which file**:
- Adding new task CRUD → read `task_tools.py` only
- Adding GTD workflow → read `gtd_tools.py` only
- Debugging reminders → read `reminder_tools.py` only
- All: Still import from `from core.agents.todoist import TodoistAgent` (clean API)

---

#### 1.2 Consolidate Documentation

**Action**: Create single authoritative source in `.claude/claude.md`

**Structure** (800-900 lines total):
```markdown
# Synapse Project Guide (for AI Assistants)

## Quick Reference (100 lines)
- Project structure
- Key files & their purpose
- Common operations

## Git & Workflow Rules (150 lines)
- Auto-commit policy
- Todo list usage
- Token optimization rules

## Todoist Agent Specifics (400 lines)
- GTD workflow
- Wizard integration
- Task formatting rules
- Knowledge management

## Token Optimization Checklist (150 lines)
- Before starting work
- During development
- Before committing

## Troubleshooting (100 lines)
- Common issues
- Where to find things
```

**Files to DELETE** (after consolidation):
- `/home/bryceg/synapse/claude.md` (612 lines) - duplicates .claude/ version
- `/home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md` - merge to .claude/
- `/home/bryceg/synapse/LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md` - archive
- `/home/bryceg/synapse/TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md` - archive

**Files to KEEP** (updated):
- `/home/bryceg/synapse/.claude/claude.md` - **PRIMARY SOURCE** (expand to 900 lines)
- `/home/bryceg/synapse/TOKEN_OPTIMIZATION_STATUS.md` - quick status reference
- `/home/bryceg/synapse/AI_OPTIMIZATION_GUIDE.md` - this file (meta-guide)

**Token Savings**: 13,500 → 4,500 tokens (67% reduction)

---

#### 1.3 Remove Obsolete Files

**Immediate Deletes**:
1. `/home/bryceg/synapse/knowledge/todoist_rules.md` - **DEPRECATED** (use todoistagent/ version)
2. `/home/bryceg/synapse/docs/archive/` - 1,650 lines of dead docs (move to git history)
3. `/home/bryceg/synapse/core/agents/todoist_openai.py` - duplicate of todoist.py (2,897 lines!)

**Token Savings**: ~4,000 tokens (eliminated from searches)

---

### Tier 2: Code Patterns (30-40% Per-Call Reduction)

#### 2.1 Compress Tool Docstrings

**Current Pattern** (verbose):
```python
def get_current_time(self) -> str:
    """
    Get the current date and time in the user's timezone.

    Returns current datetime information including:
    - Full datetime with timezone
    - Current date in YYYY-MM-DD format (for Todoist due_date)
    - Day of week
    - Time in 24-hour and 12-hour formats

    This is essential for determining due dates and understanding temporal context.
    """
```

**Optimized Pattern** (concise):
```python
def get_current_time(self) -> str:
    """Get current datetime in user's timezone (YYYY-MM-DD format for Todoist)."""
    # Returns: full datetime, date, day of week, time in 24h/12h formats
    # Used for: due date calculations, temporal context
```

**Apply to all 50+ tool methods in todoist.py**

**Token Savings**: ~600-800 tokens per API call (when tools are included in schemas)

---

#### 2.2 Use Module-Level Docstrings

**Pattern**: Put detailed docs at module level, keep method docs terse

```python
# task_tools.py
"""
Task CRUD Operations for TodoistAgent

This module provides core task manipulation tools:
- create_task: Full-featured task creation with all Todoist options
- update_task: Modify existing tasks (labels, dates, priority, etc.)
- complete_task: Mark tasks complete
- delete_task: Permanently remove tasks
- list_tasks: Query tasks by project/label/filter

Common patterns:
- Use create_task for flexible task creation
- Prefer GTD-native tools (capture, make_actionable) for workflow
- All methods return JSON: {"status": "success|error", "message": "...", "data": {...}}
"""

def create_task(self, content: str, **kwargs) -> str:
    """Create task with full Todoist options."""
    # Implementation details in code comments, not docstring
```

**Benefit**: AI reads module docstring once (cached), method docstrings stay minimal

---

### Tier 3: Claude Code Caching Optimization

#### 3.1 Organize for Prompt Caching

**Claude Code caches**: Recently-read files in conversation context

**Strategy**: Structure files so commonly-accessed content is:
1. **Small** (easier to cache entire file)
2. **Stable** (doesn't change often = longer cache hits)
3. **Self-contained** (doesn't require reading related files)

**Best Candidates for Caching**:
- `.claude/claude.md` (800-900 lines, stable, read every session)
- `core/agents/todoist/base.py` (400 lines, stable class structure)
- `agents/todoist.yaml` (74 lines, stable config)
- `TOKEN_OPTIMIZATION_STATUS.md` (163 lines, updated weekly)

**Worst Candidates** (split these):
- `todoist.py` (2,897 lines - too large to cache efficiently)
- Long documentation files (967 lines - exceed cache window)

---

#### 3.2 Front-Load Critical Context

**Pattern**: Put most important info first in files

```markdown
# .claude/claude.md

## CRITICAL RULES (Always Read First) ⚠️
1. Auto-commit + push (don't ask)
2. Use TodoWrite for multi-step tasks
3. Read AI_OPTIMIZATION_GUIDE.md before starting
4. Check TOKEN_OPTIMIZATION_STATUS.md for current priorities

## Quick File Reference
- Add task tools: core/agents/todoist/task_tools.py
- GTD workflow: core/agents/todoist/gtd_tools.py
- Wizards: core/wizard/inbox_wizard.py
- Tests: tests/agents/test_todoist.py

[... rest of detailed documentation ...]
```

**Benefit**: AI can read first 200 lines (cached), get oriented, then read specific sections

---

### Tier 4: Workflow Optimization

#### 4.1 The Big-to-Small Model Delegation Pattern

**Philosophy**: Use expensive models for planning, cheap models for execution

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Planning (Claude 3.5 Sonnet - Expensive)      │
│ - Analyze problem                                        │
│ - Explore codebase                                       │
│ - Create detailed implementation plan                    │
│ - Break into 5-10 mini-tasks                            │
│ - Generate task specifications                           │
│ Cost: ~50,000 tokens ($0.15)                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Execution (Haiku or GPT-4o-mini - Cheap)      │
│ - Execute mini-task #1 (2,000 tokens)                   │
│ - Execute mini-task #2 (2,000 tokens)                   │
│ - Execute mini-task #3 (2,000 tokens)                   │
│ - ... (8 more tasks)                                     │
│ Cost: 10 × 2,000 = 20,000 tokens ($0.02 Haiku)         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Verification (Claude 3.5 Sonnet - Expensive)  │
│ - Review all changes                                     │
│ - Run integration tests                                  │
│ - Commit & push                                          │
│ Cost: ~15,000 tokens ($0.045)                           │
└─────────────────────────────────────────────────────────┘

Total Cost: $0.215 (vs $0.50+ doing everything with Sonnet)
Savings: 57%
```

**When to Use**:
- Large refactorings (split todoist.py → 6 files)
- Documentation consolidation
- Repetitive edits (compress 50 docstrings)
- Test creation (generate 10 test cases)

**When NOT to Use**:
- Exploratory work (need big model's reasoning)
- Debugging complex issues
- Architectural decisions

---

#### 4.2 Mini-Task Specification Format

**Template for delegating to small models**:

```markdown
# Mini-Task: [Concise Title]
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 2,000-3,000
**Files to Read**: [Exactly 1-2 files, with line ranges]
**Files to Edit**: [Exactly 1 file]

## Context (100 words max)
[Just enough background - no exploration needed]

## Task
[Precise, step-by-step instructions]

## Acceptance Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)
- [ ] Criterion 3 (testable)

## Code Snippet (if applicable)
[Exact code to insert/replace - minimize decision-making]

## Validation Command
```bash
# Command to verify success (must pass)
```
```

**Example** (see TASK_TEMPLATES.md for full examples)

---

## 📋 MANDATORY CHECKLIST (Before Starting Work)

### Before Any Session

- [ ] Read this file (AI_OPTIMIZATION_GUIDE.md) - 5 min
- [ ] Check TOKEN_OPTIMIZATION_STATUS.md - what's the current priority?
- [ ] Identify task type:
  - [ ] **Exploration** → Use big model (Sonnet)
  - [ ] **Well-defined change** → Create mini-tasks for small model
  - [ ] **Quick fix** → Just do it with current model

### During Work

- [ ] **Minimize file reads**:
  - Read only necessary files
  - Use line ranges when reading large files
  - Check if cached context is sufficient before re-reading

- [ ] **Use focused imports**:
  ```python
  # ❌ BAD (forces reading entire 2,897-line file)
  from core.agents.todoist import TodoistAgent
  # Read full todoist.py to understand class

  # ✅ GOOD (after split - reads only 400 lines)
  from core.agents.todoist import TodoistAgent
  # Only reads todoist/base.py (400 lines)
  ```

- [ ] **Batch related changes**:
  - Don't make 1 commit per docstring change
  - Group into logical units (all docstrings in one commit)

### Before Committing

- [ ] **Validate changes** (don't create broken code):
  ```bash
  python -m pytest tests/  # Run tests
  ./synapse to            # Smoke test
  ```

- [ ] **Auto-commit + push** (per .claude/claude.md rules):
  ```bash
  git add <files>
  git commit -m "feat: descriptive message"
  git push
  ```

- [ ] **Update TOKEN_OPTIMIZATION_STATUS.md** if you completed optimization work

---

## 🎯 PRIORITY OPTIMIZATION ROADMAP

### Phase 1: Critical Structure (This Week)
**Estimated Savings**: 70% token reduction per session
**Effort**: 8-12 hours (can delegate to small models)

1. **Split todoist.py** (6 hours)
   - Create `core/agents/todoist/` module structure
   - Delegate to small models (see SPLIT_TODOIST_MINI_PROJECTS.md)
   - 5-6 mini-tasks × 2,000 tokens each = 12,000 tokens ($0.01 with Haiku)

2. **Consolidate docs** (3 hours)
   - Expand `.claude/claude.md` to 800-900 lines
   - Delete redundant files
   - Can do with single small model (one mini-task)

3. **Delete obsolete files** (1 hour)
   - Remove `knowledge/todoist_rules.md`
   - Remove `docs/archive/`
   - Remove `core/agents/todoist_openai.py` duplicate

**Impact**: Working on Synapse drops from 18,000 → 5,000 tokens per session

---

### Phase 2: Code Quality (Next Week)
**Estimated Savings**: 30% per API call
**Effort**: 4-6 hours

1. **Compress docstrings** (4 hours)
   - All 50+ tool methods in todoist modules
   - Delegate to small model (see COMPRESS_DOCSTRINGS_MINI_PROJECT.md)
   - Single mini-task: 3,000 tokens ($0.003 with Haiku)

2. **Add module-level docs** (2 hours)
   - Detailed context at module level
   - Keep method docs terse

**Impact**: Tool schema generation drops from 2,700 → 1,800 tokens

---

### Phase 3: Workflow Integration (Ongoing)
**Estimated Savings**: 50-70% on large projects
**Effort**: 15 min per large task (to create mini-projects)

1. **Create template library** (TASK_TEMPLATES.md)
   - Common mini-task patterns
   - Specification format
   - Delegation checklist

2. **Document big-to-small workflow** (BIG_TO_SMALL_WORKFLOW.md)
   - When to delegate
   - How to break down tasks
   - Cost calculations

---

## 💰 COST IMPACT PROJECTION

### Current Monthly Costs (AI Working on Synapse)

**Assumptions**:
- 20 sessions/month with Claude Code (Claude 3.5 Sonnet)
- Average session: 35,000 input tokens (file reads) + 5,000 output
- Sonnet pricing: $3/M input, $15/M output

**Calculation**:
```
Input:  20 × 35,000 = 700,000 tokens × $0.000003 = $2.10
Output: 20 × 5,000  = 100,000 tokens × $0.000015 = $1.50
Total: $3.60/month
```

---

### After Optimization (Structure + Delegation)

**Assumptions**:
- 10 big model sessions (planning/exploration): 15,000 input + 8,000 output each
- 40 small model sessions (execution): 3,000 input + 1,000 output each

**Big Model** (Sonnet):
```
Input:  10 × 15,000 = 150,000 × $0.000003 = $0.45
Output: 10 × 8,000  = 80,000  × $0.000015 = $1.20
Subtotal: $1.65
```

**Small Model** (Haiku - $0.25/M input, $1.25/M output):
```
Input:  40 × 3,000  = 120,000 × $0.00000025 = $0.03
Output: 40 × 1,000  = 40,000  × $0.00000125 = $0.05
Subtotal: $0.08
```

**Total**: $1.73/month (52% savings)

**At Higher Volume** (100 sessions/month):
- Current: $18/month
- Optimized: $8.65/month
- **Savings: $9.35/month ($112/year)**

---

## 🔧 TOOLS & COMMANDS

### Token Usage Analysis
```bash
# View current file sizes
find . -name "*.py" -o -name "*.md" | xargs wc -l | sort -rn | head -20

# Check git repo size
du -sh .git

# Identify redundant docs (word overlap analysis)
# TODO: Create script for this
```

### Quick Navigation
```bash
# After splitting todoist.py
cd core/agents/todoist/
ls -lh  # See module sizes

# Find where a method lives
grep -r "def make_actionable" core/agents/todoist/
```

### Validation
```bash
# Smoke test agent
./synapse to
> get current time
> exit

# Run full test suite
python -m pytest tests/

# Check imports still work
python -c "from core.agents.todoist import TodoistAgent; print('OK')"
```

---

## 📚 RELATED DOCUMENTATION

**Primary Docs** (Read These):
1. `.claude/claude.md` - Primary workflow guide (800-900 lines after consolidation)
2. `AI_OPTIMIZATION_GUIDE.md` - This file (meta-guide for AI work)
3. `TOKEN_OPTIMIZATION_STATUS.md` - Current priorities & status

**Implementation Guides** (Reference When Needed):
4. `BIG_TO_SMALL_WORKFLOW.md` - Delegation pattern (to be created)
5. `TASK_TEMPLATES.md` - Mini-task templates (to be created)
6. `SPLIT_TODOIST_MINI_PROJECTS.md` - Specific plan for splitting todoist.py (next step)

**Archived** (Git History Only):
- `LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md` - Moved to git history
- `TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md` - Completed, archived
- `docs/archive/*` - Old design docs

---

## ⚠️ CRITICAL DON'TS

### ❌ Don't Do These (Waste Tokens)

1. **Don't read full files when you need a snippet**
   ```python
   # ❌ BAD
   Read(file_path="/home/bryceg/synapse/core/agents/todoist.py")  # 2,897 lines

   # ✅ GOOD
   Read(file_path="/home/bryceg/synapse/core/agents/todoist.py",
        offset=200, limit=50)  # Just the method you need
   ```

2. **Don't explore when you have a map**
   - Check `.claude/claude.md` first (Quick File Reference section)
   - If unclear, ask user: "Should I explore or do you know where X is?"

3. **Don't repeat work**
   - Use git log to see recent changes
   - Check if someone already optimized this

4. **Don't batch reads of unrelated files**
   - Claude Code charges for tokens even if you don't use the content
   - Read files as you need them, not speculatively

5. **Don't create new docs without checking for existing ones**
   - We have too many docs already
   - Update existing or consolidate

---

## ✅ ALWAYS DO THESE (Save Tokens)

1. **Check context first**
   - "Do I already have this file in context?"
   - "Can I use cached info instead of re-reading?"

2. **Read selectively**
   - Use `offset` and `limit` parameters
   - Read function signatures before full implementations

3. **Batch related operations**
   - Don't commit after every tiny change
   - Group logical units (all docstrings, all imports, etc.)

4. **Validate before committing**
   - One broken commit = 2× cost (fix later)
   - Run tests, smoke test agent

5. **Use the delegation pattern for repetitive work**
   - If you're doing the same edit 10+ times, create mini-tasks
   - Example: Compressing 50 docstrings → delegate to Haiku

---

## 🎓 LEARNING FROM THIS PROJECT

### Key Insights

1. **File size matters exponentially**
   - 3,000-line file = 15,000 tokens
   - 6 × 500-line files = 2,500 tokens (when you only read one)
   - **5× more efficient with good structure**

2. **Documentation redundancy is invisible but expensive**
   - 8 docs with 60% overlap = reading same content 3-4 times
   - Consolidation = 1× cost instead of 4×

3. **Model delegation is powerful**
   - Planning (Sonnet): $0.15
   - Execution (Haiku): $0.02
   - **7.5× cheaper for well-defined work**

4. **Prompt caching works best with small, stable files**
   - 800-line doc (stable) = cached after first read
   - 3,000-line code (changes often) = rarely cached
   - **Split for cacheability**

---

## 📞 QUESTIONS TO ASK USER

If uncertain during work:

1. **Before exploring**: "I could explore the codebase (15k tokens) or you could point me to the file - which do you prefer?"

2. **Before creating docs**: "Should I create a new doc or update existing [X]?"

3. **Before large refactor**: "This is a big change (50k+ tokens). Should I create mini-tasks for a small model or just do it?"

4. **Before committing**: "I've made [X] changes. Auto-commit now or continue with more work?"

---

## 🚀 NEXT STEPS

**Immediate** (Do Today):
1. Create `BIG_TO_SMALL_WORKFLOW.md` (delegation pattern guide)
2. Create `SPLIT_TODOIST_MINI_PROJECTS.md` (6 mini-tasks to split todoist.py)
3. Execute first mini-task with small model (validate pattern)

**This Week**:
1. Complete Phase 1 optimizations (structure)
2. Consolidate documentation to `.claude/claude.md`
3. Delete obsolete files

**Ongoing**:
1. Use delegation pattern for all large projects
2. Track token savings (log before/after metrics)
3. Update this guide with learnings

---

**Last Updated**: 2025-10-18
**Status**: Initial version - implement Phase 1 immediately
**Owner**: Synapse AI Orchestration Engine
**Next Review**: After Phase 1 completion (1 week)
