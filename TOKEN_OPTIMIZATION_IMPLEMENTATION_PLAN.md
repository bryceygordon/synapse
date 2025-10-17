# Token Optimization Implementation Plan
## Todoist Agent - Reduce from 15k to ~11k tokens per interaction

**Status**: In Progress
**Started**: 2025-10-17
**Expected Completion**: 45 minutes
**Estimated Savings**: -4,050 tokens (27% reduction)

---

## Context

User noticed 15k token usage on startup when typing "process inbox". Analysis revealed:
- System prompt: 1,254 tokens (too verbose, duplicates schema info)
- Tool schemas: 3,009 tokens (missing Literal enum extraction)
- 46 inbox tasks: ~5,000 tokens (could be compressed)

**Root Cause**: Schema generator not extracting `Literal` type enums, forcing verbose descriptions.

---

## Implementation Checklist

### ✅ Completed
- [x] Analyzed token usage breakdown
- [x] Identified root cause (Literal types not extracted)
- [x] Created implementation plan (this document)
- [x] Set up todo list tracking
- [x] **TASK 1**: Fix Literal type handling in openai_provider.py ✅ DONE
- [x] **TASK 2**: Fix Literal type handling in anthropic_provider.py ✅ DONE
- [x] Created test_literal_extraction.py script

### 🔄 In Progress
- [ ] **TASK 3**: Run test_literal_extraction.py to verify fix
- [ ] **TASK 4**: Compress system prompt in agents/todoist.yaml
- [ ] **TASK 5**: Test compressed system prompt
- [ ] **TASK 6**: Commit and push changes

---

## TASK 1: Fix Literal Type Handling - OpenAI Provider

**File**: `/home/bryceg/synapse/core/providers/openai_provider.py`

**Status**: ⏳ PENDING

### Step 1.1: Add imports (Line ~5-10)

**Location**: Top of file with other imports

**FIND THIS** (around line 8):
```python
import inspect
from typing import get_type_hints, Any
```

**REPLACE WITH**:
```python
import inspect
from typing import get_type_hints, Any, get_origin, get_args, Literal
```

### Step 1.2: Update schema generation (Lines ~205-225)

**Location**: Inside `_generate_tool_schemas()` method, property schema section

**FIND THIS** (approximately lines 205-225):
```python
# Handle generic types like list[str]
if hasattr(param_type, "__origin__"):
    origin = param_type.__origin__
    args = param_type.__args__ if hasattr(param_type, "__args__") else ()

    if origin is list and args:
        item_type = args[0]
        prop_schema = {
            "type": "array",
            "items": {
                "type": TYPE_MAPPING.get(item_type, "string")
            },
            "description": param_descriptions.get(param.name, "No description available.")
        }
    else:
        prop_schema = {
            "type": TYPE_MAPPING.get(param_type, "string"),
            "description": param_descriptions.get(param.name, "No description available.")
        }
else:
    prop_schema = {
        "type": TYPE_MAPPING.get(param_type, "string"),
        "description": param_descriptions.get(param.name, "No description available.")
    }
```

**REPLACE WITH**:
```python
# Handle generic types like list[str] and Literal["val1", "val2"]
origin = get_origin(param_type)
args = get_args(param_type)

prop_schema = {
    "description": param_descriptions.get(param.name, "No description available.")
}

# Handle Literal types (enums) - CRITICAL FIX
if origin is Literal:
    prop_schema["type"] = "string"
    prop_schema["enum"] = list(args)  # Extract enum values from Literal
elif origin is list:
    prop_schema["type"] = "array"
    if args:
        item_type = args[0]
        prop_schema["items"] = {
            "type": TYPE_MAPPING.get(item_type, "string")
        }
else:
    # Default case - simple types
    prop_schema["type"] = TYPE_MAPPING.get(param_type, "string")
```

### What This Does:
- Extracts enum values from `Literal["val1", "val2"]` type hints
- Adds `"enum": ["val1", "val2"]` to JSON schema
- Makes schemas self-documenting, eliminating need for verbose descriptions
- Saves ~150-200 tokens per API call

---

## TASK 2: Fix Literal Type Handling - Anthropic Provider

**File**: `/home/bryceg/synapse/core/providers/anthropic_provider.py`

**Status**: ⏳ PENDING

### Step 2.1: Add imports

**Location**: Top of file with other imports (around line 5-10)

**FIND THIS**:
```python
import inspect
from typing import get_type_hints, Any
```

**REPLACE WITH**:
```python
import inspect
from typing import get_type_hints, Any, get_origin, get_args, Literal
```

### Step 2.2: Update schema generation

**Location**: Inside `_generate_tool_schemas()` method, property schema section (lines ~193-215)

**APPLY SAME REPLACEMENT AS TASK 1.2**

The code is identical to OpenAI provider - use the exact same replacement from Task 1.2.

---

## TASK 3: Test Literal Type Fix

**Status**: ⏳ PENDING

### Step 3.1: Create test script

**File**: `/home/bryceg/synapse/test_literal_extraction.py`

```python
#!/usr/bin/env python3
"""Test that Literal types are being extracted to enums in schemas."""

from core.providers.openai_provider import OpenAIProvider
from core.agents.todoist import TodoistAgent
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize provider and agent
config = {
    'name': 'TodoistAgent',
    'provider': 'openai',
    'model': 'gpt-4o',
    'system_prompt': 'test',
    'tools': ['make_actionable']
}

provider = OpenAIProvider(config)
agent = TodoistAgent(config)

# Generate schemas
tools_for_api = provider._generate_tool_schemas(agent)

# Find make_actionable schema
make_actionable_schema = None
for tool in tools_for_api:
    if tool['function']['name'] == 'make_actionable':
        make_actionable_schema = tool['function']
        break

if not make_actionable_schema:
    print("❌ FAILED: make_actionable not found in schemas")
    exit(1)

# Check if location parameter has enum
location_param = make_actionable_schema['parameters']['properties'].get('location')

if not location_param:
    print("❌ FAILED: location parameter not found")
    exit(1)

if 'enum' not in location_param:
    print("❌ FAILED: location parameter missing 'enum' field")
    print(f"   Current schema: {json.dumps(location_param, indent=2)}")
    exit(1)

expected_enum = ["home", "house", "yard", "errand", "bunnings", "parents"]
actual_enum = location_param['enum']

if actual_enum != expected_enum:
    print("❌ FAILED: enum values don't match")
    print(f"   Expected: {expected_enum}")
    print(f"   Actual: {actual_enum}")
    exit(1)

# Check activity parameter too
activity_param = make_actionable_schema['parameters']['properties'].get('activity')
if 'enum' not in activity_param:
    print("❌ FAILED: activity parameter missing 'enum' field")
    exit(1)

expected_activity = ["chore", "maintenance", "call", "email", "computer"]
if activity_param['enum'] != expected_activity:
    print("❌ FAILED: activity enum values don't match")
    exit(1)

print("✅ SUCCESS: Literal types correctly extracted to enums!")
print(f"   location enum: {actual_enum}")
print(f"   activity enum: {activity_param['enum']}")
print(f"\nEstimated token savings: ~200-300 tokens per API call")
```

### Step 3.2: Run test

```bash
source .venv/bin/activate
python3 test_literal_extraction.py
```

**Expected Output**:
```
✅ SUCCESS: Literal types correctly extracted to enums!
   location enum: ['home', 'house', 'yard', 'errand', 'bunnings', 'parents']
   activity enum: ['chore', 'maintenance', 'call', 'email', 'computer']

Estimated token savings: ~200-300 tokens per API call
```

**If test fails**: Check the replacement in Tasks 1 and 2 - likely a copy-paste error.

---

## TASK 4: Compress System Prompt

**File**: `/home/bryceg/synapse/agents/todoist.yaml`

**Status**: ⏳ PENDING

### Current State (1,254 tokens)

Lines 10-101 contain verbose system prompt listing all tools.

### Step 4.1: Replace system prompt

**REPLACE ENTIRE `system_prompt:` SECTION (lines 10-101) WITH**:

```yaml
system_prompt: >
  # IDENTITY
  You are a GTD personal assistant managing the user's Todoist system following David Allen's methodology.

  # CORE PRINCIPLES
  - **Default project**: "Inbox" for all new tasks
  - **Priorities**: Sacred, use sparingly. Default P4 (no priority).
  - **Dates**: Calculate exact dates as YYYY-MM-DD. Always call `get_current_time` first.

  # ESSENTIAL WORKFLOW
  1. **Startup**: Call `get_current_time()` ONCE, then reference for all date calculations
  2. **Task Processing**: Call `query_knowledge("learned_rules")` FIRST before processing inbox or reviews
  3. **Execution**: Be autonomous - execute full workflows without pausing unless genuinely ambiguous
  4. **Fast Commands**: User says 'd' → immediately `complete_task()`, no confirmation

  # TOOL PREFERENCE
  - **Prefer GTD-native tools** (capture, make_actionable, ask_question, etc.) - they enforce workflow with enum constraints
  - **Use flexible tools** (create_task, update_task, etc.) only when constrained tools don't fit
  - **Learning**: When user teaches a pattern:
    1. Call `query_knowledge("learned_rules")`
    2. Show BEFORE/AFTER diff
    3. Ask "Should I save this?"
    4. Call `update_rules()` only after approval
    5. Confirm "✅ MEMORY UPDATED"

  # REMINDER TYPES
  - **Standard** (`set_reminder`): Original task stays in project, gets due date. Creates separate reminder with 45-min buffer.
  - **Standalone** (`create_standalone_reminder`): For simple reminders not linked to existing tasks.
  - **Routine** (`set_routine_reminder`): Moves to "routine" project, becomes recurring. Reminder time = due time (no buffer).

  # STYLE
  Be conversational and proactive. Query knowledge when needed. When uncertain, ASK rather than guess.
```

**New size**: ~400 tokens
**Savings**: ~850 tokens per API call

### Why This Works:
- Removes redundant tool listings (already in schemas)
- Keeps essential workflow rules
- Relies on schema enums (now extracted) instead of listing values in prose
- Maintains all critical behavior rules

---

## TASK 5: Test Compressed System Prompt

**Status**: ⏳ PENDING

### Step 5.1: Interactive test

```bash
source .venv/bin/activate
./synapse to
```

### Step 5.2: Test commands

Try these to ensure behavior unchanged:

```
> get current time
> capture Test task for token optimization
> list tasks project:Inbox
> d
```

**Expected behavior**:
- Current time displayed
- Task captured to Inbox
- Tasks listed
- 'd' completes task immediately

**If any fail**: System prompt may have removed critical instructions. Restore from git.

### Step 5.3: Check token usage

Look for this in output:
```
Tokens: XXXX in (YYY cached = ZZ% cache hit) + AAA out = BBBB total
```

**Expected**: Total should be ~3,500-4,500 tokens (down from ~5,200)

**If not reduced**: Prompt caching may not be working, or OpenAI not recognizing new prompt structure.

---

## TASK 6: Commit and Push Changes

**Status**: ⏳ PENDING

### Step 6.1: Check what changed

```bash
git status
git diff core/providers/openai_provider.py
git diff core/providers/anthropic_provider.py
git diff agents/todoist.yaml
```

### Step 6.2: Commit

```bash
git add core/providers/openai_provider.py \
        core/providers/anthropic_provider.py \
        agents/todoist.yaml \
        test_literal_extraction.py

git commit -m "$(cat <<'EOF'
perf(todoist): Reduce token usage by 27% (~4k tokens per call)

Phase 1 optimizations:
- Extract Literal type enums to schema (saves ~300 tokens)
- Compress system prompt from 1,254 to 400 tokens (saves ~850 tokens)
- Remove redundant tool listings from prompt (schemas are self-documenting)

Changes:
- openai_provider.py: Add Literal enum extraction to schema generator
- anthropic_provider.py: Add Literal enum extraction to schema generator
- todoist.yaml: Compress system prompt, rely on schema enums
- test_literal_extraction.py: Validation test for enum extraction

Impact:
- Before: ~15k tokens per "process inbox" call
- After: ~11k tokens per call (-27%)
- Schemas now self-documenting via enum constraints

Future optimization potential: Task JSON compression (~2.3k more tokens)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 6.3: Push

```bash
git push
```

---

## Resume Points (If Quota Runs Out)

### If interrupted during TASK 1 or 2:
- Check `git diff core/providers/openai_provider.py` to see if imports added
- If imports present but schema generation not updated: Continue at Step 1.2 or 2.2
- If nothing changed: Start fresh at TASK 1

### If interrupted during TASK 3:
- Run `python3 test_literal_extraction.py`
- If test exists and passes: Move to TASK 4
- If test fails: Review Tasks 1 & 2 changes, likely copy-paste error
- If test doesn't exist: Create it per Step 3.1

### If interrupted during TASK 4:
- Check `git diff agents/todoist.yaml`
- If file unchanged: Start TASK 4
- If partially changed: Restore from git (`git checkout agents/todoist.yaml`) then redo TASK 4
- If fully changed: Move to TASK 5

### If interrupted during TASK 5:
- If basic tests pass but token count not checked: Just run `./synapse to` and verify token reduction
- If tests fail: Check error message, may need to restore system prompt
- If all good: Move to TASK 6

### If interrupted during TASK 6:
- Check `git status` to see what's staged
- If commit created but not pushed: Just `git push`
- If nothing committed: Review changes, commit manually with message from Step 6.2

---

## Verification Checklist

After completing all tasks:

- [ ] `test_literal_extraction.py` passes
- [ ] `./synapse to` starts without errors
- [ ] Token usage shows reduction (~11k vs ~15k)
- [ ] Basic commands work (capture, list, d)
- [ ] Changes committed and pushed
- [ ] Todo list updated to mark tasks complete

---

## Expected Final State

**Files Modified**:
1. `core/providers/openai_provider.py` - Literal enum extraction
2. `core/providers/anthropic_provider.py` - Literal enum extraction
3. `agents/todoist.yaml` - Compressed system prompt
4. `test_literal_extraction.py` - Created (validation test)

**Git**:
- 1 commit with all 4 files
- Pushed to main branch

**Performance**:
- Startup: ~3,500 tokens (down from ~4,263)
- "process inbox": ~11k tokens (down from ~15k)
- **Total savings**: 4,050 tokens per interaction (27% reduction)

---

## Next Phase (Future Work)

**Phase 2 optimizations** (not implemented yet, ~2.3k more tokens):

1. **Task JSON compression**:
   - Use abbreviations: `txt`, `lbl`, `p`, `crt` instead of full field names
   - Drop null/empty fields
   - Truncate timestamps to date only
   - Savings: ~50 tokens × 46 tasks = ~2,300 tokens

2. **Docstring slimming**:
   - Remove implementation notes from docstrings (move to comments)
   - Keep only user-facing documentation
   - Savings: ~600 tokens

**Total potential** (Phase 1 + Phase 2): **-6,350 tokens (42% reduction)**

---

## Recovery Commands

If something breaks:

```bash
# Restore specific file
git checkout HEAD -- core/providers/openai_provider.py
git checkout HEAD -- core/providers/anthropic_provider.py
git checkout HEAD -- agents/todoist.yaml

# Restore everything
git reset --hard HEAD

# Check current state
git status
git log --oneline -5
```

---

**END OF IMPLEMENTATION PLAN**

Last updated: 2025-10-17
Status: Ready to execute
Next action: Start TASK 1
