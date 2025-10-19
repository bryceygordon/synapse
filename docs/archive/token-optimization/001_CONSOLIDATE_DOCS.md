# Mini-Project 001: Consolidate Documentation
**Model**: Claude 3.5 Haiku or GPT-4o-mini
**Estimated Tokens**: 12,000 input + 3,000 output
**Estimated Cost**: $0.007 (Haiku) or $0.004 (GPT-4o-mini)
**Priority**: 🔴 CRITICAL (saves 67% tokens on context loading)
**Time**: 30-45 minutes

---

## Overview

**Problem**: Synapse documentation is scattered across 8+ markdown files with 60-70% redundant content. When AI needs workflow context, it must read 4-6 files (13,500 tokens).

**Solution**: Consolidate to single authoritative source in `.claude/claude.md`

**Impact**:
- Before: 13,500 tokens to understand workflow
- After: 4,500 tokens
- **Savings**: 67% reduction (9,000 tokens per context load)

---

## Files Involved

### Files to Read (for context)
1. `/home/bryceg/synapse/.claude/claude.md` (80 lines - current version)
2. `/home/bryceg/synapse/claude.md` (612 lines - root version)
3. `/home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md` (226 lines)
4. `/home/bryceg/synapse/AI_OPTIMIZATION_GUIDE.md` (just created - reference only)
5. `/home/bryceg/synapse/TOKEN_OPTIMIZATION_STATUS.md` (163 lines)

### Files to Create/Update
1. `/home/bryceg/synapse/.claude/claude.md` - **Expand to 800-900 lines** (PRIMARY SOURCE)

### Files to DELETE
1. `/home/bryceg/synapse/claude.md` (612 lines - duplicate)
2. `/home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md` (226 lines - merge content)

---

## Task Breakdown

### Task 1: Expand `.claude/claude.md` (Primary)

**File**: `/home/bryceg/synapse/.claude/claude.md`

**Current**: 80 lines (basic workflow)
**Target**: 800-900 lines (comprehensive guide)

**Structure to Create**:

```markdown
# Synapse Project Guide (for AI Assistants)
**Last Updated**: 2025-10-18
**Purpose**: Single source of truth for AI working on Synapse
**Read This**: Before starting any session

---

## 🚨 CRITICAL RULES (Always Follow)

1. **Auto-commit & Push**: When work is complete, commit AND push automatically
   - Don't ask permission for normal commits
   - Only ask for destructive git operations (force push, hard reset)
   - User prefers commits pushed as part of normal workflow

2. **Todo List Usage**: Use TodoWrite for multi-step tasks
   - Mark todos completed immediately when done
   - Keep user informed of progress

3. **Token Optimization**: Before starting work:
   - Check `AI_OPTIMIZATION_GUIDE.md` for current best practices
   - Read only files you need (use line ranges)
   - Use delegation pattern for large projects

4. **File Location Reference**: Check Quick File Reference below before exploring

---

## 📁 Quick File Reference

Know where things are before you search:

### Core Agent Code
- **TodoistAgent main**: `core/agents/todoist.py` (2,897 lines - **TO BE SPLIT**)
- **Base agent**: `core/agents/base.py`
- **OpenAI provider**: `core/providers/openai_provider.py`
- **Anthropic provider**: `core/providers/anthropic_provider.py`
- **Schema generator**: `core/schema_generator.py`

### Wizards
- **Inbox wizard**: `core/wizard/inbox_wizard.py`
- **No-next-action wizard**: `core/wizard/no_next_action_wizard.py`

### Configuration
- **Todoist agent config**: `agents/todoist.yaml` (current, optimized)
- **Coder agent config**: `agents/coder.yaml`
- **Main CLI**: `core/main.py`

### Knowledge Base
- **Learned rules**: `knowledge/todoistagent/learned_rules.md` (current)
- **Processing rules**: `knowledge/todoistagent/processing_rules.md`
- **Tool reference**: `knowledge/todoistagent/tool_reference.md`
- **Date syntax**: `knowledge/todoistagent/date_syntax.md`

### Tests
- **Todoist tests**: `tests/test_todoist_agent.py`
- **Provider tests**: `tests/test_anthropic_provider.py`, `tests/test_provider_abstraction.py`

### Documentation
- **AI optimization guide**: `AI_OPTIMIZATION_GUIDE.md` (meta-guide for AI work)
- **Token status**: `TOKEN_OPTIMIZATION_STATUS.md` (current priorities)
- **Workflow pattern**: `BIG_TO_SMALL_WORKFLOW.md` (delegation pattern)

---

## 🎯 Project Overview

**Synapse** is a modular, command-line-first AI orchestration engine.

**Key Features**:
- Multi-provider support (OpenAI, Anthropic)
- YAML-driven agent configuration
- Dynamic tool schema generation
- Just-in-time knowledge loading
- GTD workflow automation (TodoistAgent)

**Architecture**:
```
User Input → CLI (main.py)
           → Provider (openai/anthropic)
           → Agent (todoist/coder/etc)
           → Tools (query knowledge, manage tasks)
           → Response
```

**Current Focus**: Token optimization (reducing costs for AI working on Synapse)

---

## 🔧 Todoist Agent Specifics

[MERGE CONTENT FROM: claude.md, EXPECTED_INTERACTION_FLOW.md]

### Task Formatting Rules
**ALWAYS apply when processing ANY task (wizard or direct AI processing):**

- Verbose tasks must be reformatted into concise content + description
- Example: "Revisit the Minecraft server script. Particularly the creation of new servers and the potential to create new from seed."
  - **Content**: "Revisit minecraft server script"
  - **Description**: "Particularly the creation of new servers and the potential to create new servers from seed"

### Hybrid Processing Architecture

**AI Responsibilities:**
1. Batch suggest reformatted task content for ALL inbox tasks upfront
2. Suggest initial criteria (contexts, energy, duration) for each task
3. Handle natural language date/time parsing (user can say "tomorrow 8am" or "every day 8am")
4. Process wizard output (structured task ID + field changes) into Todoist API calls

**Python Wizard Responsibilities:**
1. Step through tasks one-by-one with simple prompts:
   - Simple vs multi-step? (prompts user to decide)
   - If multi-step: "What's the next action?" (user types free text)
   - Energy level: h/m/l (ENTER = accept AI suggestion)
   - Duration: s/m/l (ENTER = accept AI suggestion)
   - Contexts/labels: (user can use natural language: "take away shed, add house")
   - Due date/recurrence: (user can say "tomorrow" or "every day 8am", AI parses)
2. Allow pause at any time → auto-push all changes to Todoist before returning to AI chat
3. Output structured instructions to AI: task_id + field changes for batch processing

### Tag Rules
- **@next**: Applied to simple tasks OR the subtask that is the immediate next action
- **@plan**: Stacked with @next for tasks requiring specific scheduling
- Energy (@lowenergy/@medenergy/@highenergy) and duration (@short/@medium/@long) are mutually exclusive within their categories
- Other context tags can be compounded

### Daily Review Workflow
1. Process inbox (via wizard)
2. Find tasks in processed without next actions → assign new next actions
3. Schedule tasks with @plan tag (calendar integration)

**NOTE**: All references to "weekly review" should be removed - user does daily reviews only

### Automatic Checks on Agent Startup
- Run `find_tasks_without_next_actions()` automatically
- Alert user if any tasks in processed project lack:
  - Tasks without subtasks AND without @next label
  - Tasks with subtasks but no subtask has @next label

### Wizard-to-AI Communication Protocol
When wizard completes or pauses, it outputs structured instructions:
```
task_id: 123456789
- content: "Revisit minecraft server script"
- description: "Particularly the creation of new servers and the potential to create new servers from seed"
- labels: "take away shed, add house, add next"
- due_date: "tomorrow 8am"
- energy: m
- duration: l

task_id: 987654321
- labels: "add plan, add next"
- due_date: "every day 8am"
```

AI processes these instructions, parses natural language dates, and batches Todoist API calls.

---

## 🧠 Knowledge Management

### Just-In-Time (JIT) Architecture

Synapse uses JIT knowledge loading:
- Knowledge NOT embedded in system prompt
- AI calls `query_knowledge(topic)` when needed
- Keeps system prompt small (~400 tokens)

### Knowledge Structure

```
knowledge/todoistagent/
├── learned_rules.md      (User preferences, learned patterns)
├── processing_rules.md   (Inbox processing workflow)
├── tool_reference.md     (Tool usage patterns)
├── date_syntax.md        (Todoist date format reference)
├── context_labels.md     (Label taxonomy)
└── index.json            (Metadata for semantic search)
```

### Learning Protocol

When user teaches a new pattern:
1. AI calls `query_knowledge("learned_rules")`
2. Shows BEFORE/AFTER diff of proposed rule
3. Asks: "Should I save this?"
4. Only calls `update_rules()` after explicit approval
5. Confirms: "✅ MEMORY UPDATED"

**Critical**: Never update knowledge without user approval

---

## 🔄 Git Workflow

### Standard Operations (Auto)
```bash
# After completing work, automatically:
git add <relevant files>
git commit -m "feat: descriptive message

Details about changes...

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### Commit Message Format
- Prefix: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `perf:`
- First line: Concise summary (50-72 chars)
- Body: Details, context, impact
- Footer: Claude Code attribution

### When to Ask Permission
- Force push to main/master
- Hard reset (git reset --hard)
- Rewriting public history (rebase -i)
- Deleting branches

---

## 💰 Token Optimization (Current Phase)

### Phase 1: ✅ COMPLETE
- Literal type extraction (Anthropic + OpenAI)
- System prompt compression (1,254 → 400 tokens)
- Achieved: 38% reduction

### Phase 2: 🔄 IN PROGRESS
Priority optimizations:
1. Split `todoist.py` into modules (70% savings)
2. Consolidate documentation (67% savings)
3. Compress tool docstrings (30% savings)

### Before Starting Work

**Check**:
1. Read `AI_OPTIMIZATION_GUIDE.md` for current best practices
2. Check `TOKEN_OPTIMIZATION_STATUS.md` for priorities
3. Is this a large project? → Consider delegation pattern (see `BIG_TO_SMALL_WORKFLOW.md`)

**Minimize File Reads**:
```python
# ❌ BAD (reads full 2,897-line file)
Read(file_path="/home/bryceg/synapse/core/agents/todoist.py")

# ✅ GOOD (reads only what you need)
Read(file_path="/home/bryceg/synapse/core/agents/todoist.py",
     offset=200, limit=50)
```

**Use Quick File Reference** (above) before exploring

---

## 🧪 Testing

### Run Tests
```bash
# Full test suite
python -m pytest tests/

# Specific test file
python -m pytest tests/test_todoist_agent.py

# Specific test
python -m pytest tests/test_todoist_agent.py::test_create_task
```

### Smoke Test Agent
```bash
./synapse to
> get current time
> list inbox
> exit
```

### Validate Imports
```bash
# After refactoring
python -c "from core.agents.todoist import TodoistAgent; print('OK')"
```

---

## 🐛 Common Issues & Solutions

### Issue: "TodoistAgent not found"
**Cause**: Import path changed or __init__.py missing
**Fix**: Check `core/agents/__init__.py` and `core/agents/todoist/__init__.py`

### Issue: "Literal type not in schema"
**Cause**: Provider not extracting enums
**Fix**: Check provider has `get_origin(param_type) is Literal` handling

### Issue: "Knowledge not loading"
**Cause**: JIT knowledge path incorrect
**Fix**: Check `BaseAgent.knowledge_dir = "knowledge/{agent_name_lower}"`

### Issue: "Tests failing after refactor"
**Cause**: Imports changed, stale test references
**Fix**: Update test imports, check git diff

---

## 📚 Additional Resources

**For detailed guides, see**:
- `AI_OPTIMIZATION_GUIDE.md` - How to work efficiently on Synapse
- `BIG_TO_SMALL_WORKFLOW.md` - Delegation pattern for large projects
- `TOKEN_OPTIMIZATION_STATUS.md` - Current optimization status
- `README.md` - User-facing project documentation

**For examples**:
- `mini-projects/` - Small, well-defined tasks for cheap models
- `agents/examples/` - Example agent configurations

---

**END OF GUIDE**

This is the single source of truth for AI assistants working on Synapse.
Keep it updated, concise, and organized. Target: 800-900 lines max.
```

---

### Task 2: Delete Redundant Files

**Files to delete** (after content merged to `.claude/claude.md`):

1. `/home/bryceg/synapse/claude.md` (612 lines)
   - Duplicate of `.claude/claude.md` (older version)
   - Content merged above

2. `/home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md` (226 lines)
   - Workflow doc (merged to `.claude/claude.md`)

**Command**:
```bash
rm /home/bryceg/synapse/claude.md
rm /home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md
```

---

## Acceptance Criteria

- [ ] `.claude/claude.md` expanded to 800-900 lines
- [ ] All critical content from `claude.md` (root) merged
- [ ] All relevant content from `EXPECTED_INTERACTION_FLOW.md` merged
- [ ] File structure follows template above (8 main sections)
- [ ] Quick File Reference is accurate and complete
- [ ] Todoist-specific workflow details preserved
- [ ] Git workflow rules preserved
- [ ] Token optimization checklist included
- [ ] Root `claude.md` deleted
- [ ] `EXPECTED_INTERACTION_FLOW.md` deleted
- [ ] No syntax errors in markdown

---

## Validation

```bash
# Check new file exists and size
ls -lh /home/bryceg/synapse/.claude/claude.md
wc -l /home/bryceg/synapse/.claude/claude.md  # Should be 800-900 lines

# Check old files deleted
! test -f /home/bryceg/synapse/claude.md && echo "Root claude.md deleted: ✅"
! test -f /home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md && echo "EXPECTED_INTERACTION_FLOW.md deleted: ✅"

# Verify markdown is valid (no syntax errors)
# Install markdownlint if needed: npm install -g markdownlint-cli
markdownlint /home/bryceg/synapse/.claude/claude.md || echo "No markdownlint - skip this check"

# Check contains critical sections
grep -q "## 🚨 CRITICAL RULES" /home/bryceg/synapse/.claude/claude.md && echo "Critical rules: ✅"
grep -q "## 📁 Quick File Reference" /home/bryceg/synapse/.claude/claude.md && echo "Quick reference: ✅"
grep -q "## 🔧 Todoist Agent Specifics" /home/bryceg/synapse/.claude/claude.md && echo "Todoist specifics: ✅"
grep -q "## 💰 Token Optimization" /home/bryceg/synapse/.claude/claude.md && echo "Token optimization: ✅"
```

---

## Success Report Template

After completing task, report:

```markdown
## Mini-Project 001: Consolidate Docs - COMPLETE ✅

**Model Used**: [Claude 3.5 Haiku or GPT-4o-mini]
**Actual Tokens**: [X] input + [Y] output
**Actual Cost**: $[Z]

**Files Created/Updated**:
- ✅ `/home/bryceg/synapse/.claude/claude.md` ([X] lines)

**Files Deleted**:
- ✅ `/home/bryceg/synapse/claude.md`
- ✅ `/home/bryceg/synapse/EXPECTED_INTERACTION_FLOW.md`

**Validation Results**:
- File size: [X] lines (target: 800-900): [✅/❌]
- Old files deleted: [✅/❌]
- Contains critical sections: [✅/❌]
- Markdown valid: [✅/❌]

**Next Steps**:
- Big model: Review consolidated doc
- Big model: Commit & push
- Big model: Update TOKEN_OPTIMIZATION_STATUS.md
```

---

## On Failure

If validation fails or task is unclear:

1. **Report exact issue**:
   ```markdown
   ## Mini-Project 001: BLOCKED ⚠️

   **Issue**: [Exact error message or confusion]

   **Attempted**: [What you tried]

   **Need from big model**:
   - [Clarification needed]
   - [Decision needed]
   ```

2. **Do NOT attempt to fix** (ask big model)

3. **Include validation output** in report

---

## Notes for Small Model

### Content Merging Strategy

**From `claude.md` (root)**:
- Extract workflow sections
- Extract Todoist-specific rules
- Extract knowledge management info
- Skip redundant git rules (already in `.claude/claude.md`)

**From `EXPECTED_INTERACTION_FLOW.md`**:
- Extract wizard protocol
- Extract task formatting rules
- Extract AI/wizard responsibilities
- Merge into "Todoist Agent Specifics" section

**Preserve from current `.claude/claude.md`**:
- Git workflow rules
- Todo list usage
- All existing content (don't delete anything)

### Tone & Style

- Keep technical and precise
- Use emoji headers (🚨, 📁, 🔧, etc.) for visual scanning
- Use code blocks for commands and examples
- Keep examples realistic (actual file paths from Synapse)
- Target audience: AI assistants (Claude Code, etc.)

### Organization

1. **Front-load critical info** (rules, quick reference)
2. **Group related content** (Todoist stuff together, Git stuff together)
3. **Use clear headers** (AI can navigate easily)
4. **Provide examples** (show, don't just tell)

---

## Time Estimate

- Reading source files: 10 minutes
- Merging content to template: 20 minutes
- Validation: 5 minutes
- **Total**: 35 minutes

---

## Token Estimate

**Reading**:
- `.claude/claude.md`: 80 lines × 5 tokens/line = 400 tokens
- `claude.md`: 612 lines × 5 tokens/line = 3,060 tokens
- `EXPECTED_INTERACTION_FLOW.md`: 226 lines × 5 tokens/line = 1,130 tokens
- This mini-project spec: 450 lines × 5 tokens/line = 2,250 tokens
- **Total input**: ~6,840 tokens

**Writing**:
- New `.claude/claude.md`: 850 lines × 5 tokens/line = 4,250 tokens
- But incremental write (with caching) ~1,500 tokens
- **Total output**: ~1,500 tokens

**Grand total**: ~8,340 tokens

**Cost** (Haiku: $0.25/M input, $1.25/M output):
- Input: 6,840 × $0.00000025 = $0.0017
- Output: 1,500 × $0.00000125 = $0.0019
- **Total**: ~$0.0036 (well under $0.01)

---

**Ready to Execute**: Yes ✅
**Next Project**: Split todoist.py (after this completes)
