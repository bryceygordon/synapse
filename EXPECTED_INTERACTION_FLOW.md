# Expected Interaction Flow - Constrained Tools Test

This document shows the expected behavior when the LLM uses the new constrained GTD tools.

## ✅ VERIFIED: Enum Constraints Are Working

The schema generator test confirms that `Literal` types are correctly converted to JSON Schema `enum` constraints.

---

## Expected Flow 1: Quick Capture

**User:** "Add 'clean out garage' to my inbox"

**LLM sees these tool options:**
```json
{
  "name": "capture",
  "parameters": {
    "content": {"type": "string", "description": "What needs capturing"}
  }
}
```

**LLM Response:**
```
[Tool call: capture(content="Clean out garage")]
→ Inbox
```

**Expected Outcome:** ✅ Task created in Inbox, no enum constraints needed (simple capture)

---

## Expected Flow 2: Processing with Enum Constraints

**User:** "Process the inbox"

**Step 1: LLM loads knowledge and lists tasks**
```
[Tool: query_knowledge("learned_rules")]
[Tool: list_tasks(project_name="Inbox")]

Found 5 tasks:
1. Clean out garage
2. Call Bec about dinner plans
3. Buy milk and bread
4. Fertilize the front lawn
5. Fix leaking tap in bathroom
```

**Step 2: LLM presents batch with suggestions**

**CRITICAL: LLM sees this schema for `make_actionable`:**
```json
{
  "name": "make_actionable",
  "parameters": {
    "task_id": {"type": "string"},
    "location": {
      "type": "string",
      "enum": ["home", "house", "yard", "errand", "bunnings", "parents"]
    },
    "activity": {
      "type": "string",
      "enum": ["chore", "maintenance", "call", "email", "computer"]
    },
    "energy": {
      "type": "string",
      "enum": ["lowenergy", "medenergy", "highenergy"]
    },
    "duration": {
      "type": "string",
      "enum": ["short", "medium", "long"]
    }
  }
}
```

**LLM's proposal (constrained by enum):**
```
**Task 1:** Clean out garage
**Location:** house (closest match - garage is part of house)
**Activity:** chore
**Energy:** highenergy
**Duration:** long
**Next Action:** Sort items into keep/donate/trash piles

**Task 2:** Call Bec about dinner plans
**Location:** home
**Activity:** call
**Energy:** lowenergy
**Duration:** short
```

**Key Point:** LLM **cannot** suggest:
- ❌ `location: "garage"` - not in enum
- ❌ `activity: "cleaning"` - not in enum
- ❌ `energy: "veryhigh"` - not in enum

It can ONLY choose from the valid enum values!

**User:** "yes"

**Step 3: LLM executes batch processing**
```
[Tool: make_actionable(
  task_id="task1_id",
  location="house",
  activity="chore",
  energy="highenergy",
  duration="long",
  next_action="Sort items into keep/donate/trash piles"
)]
✓ Processed + subtask: Sort items into keep/donate/trash piles

[Tool: make_actionable(
  task_id="task2_id",
  location="home",
  activity="call",
  energy="lowenergy",
  duration="short"
)]
✓ Processed [@next]
```

---

## Expected Flow 3: Question Task

**User:** "I need to ask William about his soccer practice schedule"

**LLM sees this schema:**
```json
{
  "name": "ask_question",
  "parameters": {
    "task_id": {"type": "string"},
    "person": {
      "type": "string",
      "enum": ["bec", "william", "reece", "alex", "parents"]
    },
    "via_call": {"type": "boolean"}
  }
}
```

**LLM Response:**
```
[Tool: capture(content="Ask William about soccer practice schedule")]
[Tool: ask_question(task_id="new_task_id", person="william", via_call=false)]
→ Questions (@william)
```

**Cannot suggest:** ❌ `person: "son"` or `person: "will"` - not in enum!

---

## Expected Flow 4: Grocery (Bypass GTD)

**User:** "Add milk to shopping list"

**LLM sees:**
```json
{
  "name": "add_grocery",
  "parameters": {
    "item": {"type": "string"}
  }
}
```

**LLM Response:**
```
[Tool: add_grocery(item="Milk")]
→ Groceries
```

**Expected:** ✅ Goes straight to groceries project, bypasses all GTD processing

---

## Expected Flow 5: Fallback to Flexible Tools

**User:** "Create a task in my 'Personal Projects' project with @experimental label"

**LLM Response:**
```
None of the constrained tools fit this request:
- capture() only goes to Inbox
- make_actionable() only goes to processed
- add_grocery() only goes to groceries

Using flexible fallback tool:

[Tool: create_task(
  content="...",
  project_name="Personal Projects",
  labels=["experimental"]
)]
```

**Expected:** ✅ LLM uses flexible `create_task` when constrained tools don't match the request

---

## Key Advantages of This Design

1. **Proposals are always valid** - LLM can't suggest "garage" when only "house" exists
2. **Fewer tokens** - No need to explain valid options in prompt (they're in the schema)
3. **Impossible to mess up** - Type system enforces correctness
4. **Flexibility remains** - Fallback tools handle edge cases
5. **Self-documenting** - Tool schemas serve as both constraints and documentation

---

## What You Should Expect

When you run the actual agent:

1. **Capture works instantly** - Just creates in Inbox
2. **Inbox processing presents constrained suggestions** - You'll only see valid enum values
3. **User approval → execution** - All suggestions execute successfully (no validation errors)
4. **Edge cases use flexible tools** - Agent knows when to break the shackles

The LLM's "thinking" is guided by what's possible, not what's forbidden.
