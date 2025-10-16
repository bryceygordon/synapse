# Learned Rules and Preferences

This file stores user-approved learned rules and patterns that the agent learns over time.

## Weekly Review Workflow

When user requests "weekly review", follow this specific process:

### Review Order
1. **Inbox Processing** (first priority)
2. **Processed Review** (oldest → newest)
3. **Routine Review** (fitness for purpose)
4. **Reminder Review**
5. **Other Projects Review**
6. **Planning Session** (schedule @next tasks into specific days)

### Inbox Processing

- Present items in **batches of 5 or less**
- For each batch, INTUIT and suggest:
  - Project destination (usually "processed")
  - Location contexts (@home, @yard, @house, etc.)
  - Activity contexts (@chore, @maintenance, @errand, etc.)
  - **Verbal Expressiveness**: Convert verbose task entries into concise actions and use additional notes/description for context.
  - Energy level (@lowenergy, @medenergy, @highenergy)
  - Duration (@short, @medium, @long)
  - Next action (what's the immediate physical action?)
    - If the task is a multi-step job, create subtasks for each step with a subtask marked @next.
    - If the task is short and simple, the task itself should have the @next label.

### Processed Review
- List tasks oldest → newest
- Present in batches of 5 or less
- Check each task for **@next action**:
  - Does the task itself have @next label? OR
  - Does it have a subtask with @next label?
- If NO next action found:
  - Ask: "What's the next action for [task name]?"
  - Create subtask with @next label
- If task is complete, mark as done
- NO preamble, NO summary between batches

### Next Actions (CRITICAL GTD CONCEPT)
- Every **processed task** MUST have a clear next action.
- Items in the inbox are unprocessed and usually will NOT have a next action.
- Any task ending up in the #processed project must have a next action.
- Next action = immediate, physical action to move task forward
- Ensure next actions are "doable"; for instance, "Gather relevant tax documents" is doable, while "Complete tax return" is not.
- Format: Either main task with @next OR subtask with @next
- Examples:
  - "Repair sprinkler" → Next: "Check shed for spare parts" @next
  - "Plan birthday party" → Next: "Call venue for availability" @next
  - "Buy groceries" → Can be its own @next (single, simple action)

### Task Presentation Format
**CRITICAL: NO preambles, NO conclusions, NO explanations - ONLY present the tasks.**

WRONG (has preamble):
"Here are the first five tasks in the Inbox for processing:"

CORRECT (direct presentation):
**Task 1:** Fix leaking tap
**Contexts:** @home @maintenance
**Energy:** @medenergy
**Duration:** @medium
**Next Action:** Get wrench from shed

**Task 2:** Buy paint
**Contexts:** @bunnings @errand
**Energy:** @lowenergy
**Duration:** @medium
**Next Action:** (This IS the next action)

WRONG (has conclusion):
"Please review the suggested contexts, energy levels..."

After presenting batch, STOP. Wait for user response.

User responds: "yes" or "change task 2 to @medenergy"

**Task Numbering**: ALWAYS number 1-5 for each batch (not 6-10, 11-15, etc.)
- First batch: Tasks 1-5
- Second batch: Tasks 1-5 (renumber!)
- User says "task 2" = task 2 from current batch shown

### Processing Batch Operations
- **NEVER process one task at a time** - always complete entire batch
- When user approves, execute ALL operations in sequence:
  - Move all tasks to destination project ("processed")
  - Update all labels on each task (contexts, energy, duration)
  - Create subtask for next action with @next label (if not simple task)
  - For simple tasks (call, buy, email): add @next to main task instead
- After processing, present next batch immediately (NO "Batch complete" message)

### Task Categorization Patterns
Agent should LEARN and INTUIT from user corrections:
- Tasks mentioning "lawn", "garden", "fertilize" → @yard @chore @weather
- Tasks mentioning "sweep", "vacuum", "mop" → @house @chore
- Tasks mentioning "call", "email", "ask" → @lowenergy @short
- Hardware store items → @bunnings @errand @lowenergy
- High-energy chores → Ask: "Do kids need to be away?" → @nokids if yes
- Tasks involving physical work → usually @medenergy or @highenergy
- Tasks involving mental work (research, planning) → @computer @medenergy

### Duplicate Detection
- ALWAYS check #processed for existing tasks before creating from inbox
- If duplicate found, delete inbox copy
- Maintain single source of truth

### Label Format Requirements
- NEVER use @@label format - always single @ symbol
- Labels passed to API must be list WITHOUT @ prefix: ["home", "chore"]
- Fix any malformed labels immediately when spotted

### Simple Tasks = Next Actions
- Some tasks ARE their own next action (simple, single-step)
- Examples: "call dentist", "buy milk", "sweep patio"
- For these: add @next directly to main task (no subtask)
- Use judgment - if one clear action, it can be its own @next

## Chore-Specific Rules

### All Chores MUST Have:
1. Location context (@home, @house, @yard, etc.)
2. Activity context (@chore or @maintenance)
3. Energy label (@lowenergy, @medenergy, @highenergy)
4. Duration label (@short, @medium, @long)
5. Next action (@next on task or subtask)

### High Energy Chores:
- Always ask: "Do the kids need to be away?"
- If yes, add @nokids label
- Examples: deep cleaning, loud projects, dangerous work

### Weather-Dependent Tasks:
- Tasks involving outdoor work, poison/spray, painting → @weather
- User can't do these tasks if raining

## Learning Protocol

When you notice a pattern in how the user categorizes tasks:
1. Propose the rule: "I've noticed [pattern]. Should I remember: [specific rule]?"
2. Wait for user approval
3. If approved, add to this file in appropriate section
4. Confirm: "Rule saved. I'll apply this consistently."

## User Patterns to Learn

*Agent will learn and fill these in over time through conversations:*

### Task Management Preferences
- **Default Task Entry:** User typically adds new items directly into the "Inbox" for processing later.

### Autonomous Execution Preference (CRITICAL)
- **User values autonomous execution** - DO NOT create stop-start interactions
- Execute clear, unambiguous commands IMMEDIATELY without asking permission
- Commands like "move all tasks from X to Y" should:
  1. Fetch the tasks
  2. Move them (using batch_move_tasks if multiple)
  3. Report results
  - NO intermediate "I found 15 tasks, should I proceed?" steps
- Only ask for clarification when genuinely ambiguous or destructive (>20 deletions)
- Weekly review is DIFFERENT - that's interactive by design (user approves batches)
- Simple operations (move, update, complete) are NOT interactive - execute immediately

### Criteria Verification Preference
- When checking for tasks that don't meet specific criteria:
  - First, look for a definition of the criteria in the knowledge base.
  - If no definition is found, confirm the criteria details with the user before proceeding.

### Preference for Rule Categorization
- Always review existing categories to ensure a best fit before creating new ones for rules.

### Rule for Verbose Task Entry
1. **Task Identification**: Intuit the core action and simplify it into a concise task name.
   - Example: "Clean fridge"
2. **Subtask Creation**: Identify any additional actionable items and create subtasks if needed.
   - Example: "Find spare towels in cupboard" marked with @next.
3. **Description Addition**: Place further context or details into the task description.
   - Example: "Clean fridge out before grandparents come over."
4. **Labeling**: Apply all relevant labels as inferred from task content.
   - For instance, energy level, location, and activity type.

### Location Patterns
- Which tasks typically go to which locations
- When to use @house vs @home vs @yard

### Energy Assessment Patterns
- How user categorizes energy levels for different task types
- Which tasks tend to be @highenergy vs @medenergy

### Duration Patterns
- How user estimates timeframes for common tasks
- Which tasks are @short vs @medium vs @long

### People Involvement
- Common tasks involving @bec, @william, @reece, @alex
- Delegation patterns

### Bunnings/Shopping Patterns
- What items typically require Bunnings trip
- When to suggest @bunnings automatically

## Notes
- This file grows organically through use
- All patterns must be approved by user before saving
- Agent should proactively recognize patterns and ask to save them
- Helps reduce token usage by eliminating repeated explanations

## Processing Tasks

- Present tasks for processing in quantities that make sense based on complexity. 
  - More complex tasks might require more conversation and can be handled one at a time.

- For each task, INTUIT and suggest:
  - Project destination (usually "#processed")
  - Location contexts (@home, @yard, @house, etc.)
  - Activity contexts (@chore, @maintenance, @errand, etc.)
  - **Verbal Expressiveness**: Convert verbose task entries into concise actions and use additional notes/description for context.
  - Energy level (@lowenergy, @medenergy, @highenergy)
  - Duration (@short, @medium, @long)
  - Next action (what's the immediate physical action?)
    - If the task is a multi-step job, intuit possible steps and pick one as the next action.
    - Create subtasks for each step, choosing one to mark with @next.
    - If the task is short and simple, the task itself should have the @next label.

- Once all the criteria have been met, the task is considered processed and can be moved into an appropriate project, usually "#processed".

- **All tasks in any projects other than the Inbox** must meet these criteria. 
  - For tasks lacking attributes or detail, highlight and ask whether to move back to the inbox or correct it.
  - Intuit the correct form of the processed task and present it for your approval. 
  - Engage in conversation as needed to ensure task clarity and accuracy.


## Definitions and Standards

### Example of a Processed Task
- **Task Content:** Buy groceries for dinner
- **Project Destination:** #processed
- **Location Contexts:** @shopping
- **Activity Contexts:** @errand
- **Energy Level:** @lowenergy
- **Duration:** @short
- **Next Action:** Create list of items needed @next

### Example of an Unprocessed Task
- **Task Content:** Go shopping
- **Missing Information:**
  - No context for what type of shopping (e.g., groceries, clothes)
  - No energy level assigned
  - No duration estimated
  - No clear project destination
  - No next action specified

- **Note:** If a task is missing any of these critical elements, it should be considered unprocessed and require further refinement.

### Example of a Processed Task
- **Task Content:** Buy groceries for dinner
- **Project Destination:** #processed
- **Location Contexts:** @shopping
- **Activity Contexts:** @errand
- **Energy Level:** @lowenergy
- **Duration:** @short
- **Next Action:** Create list of items needed @next

### Example of an Unprocessed Task
- **Task Content:** Go shopping
- **Missing Information:**
  - No context for what type of shopping (e.g., groceries, clothes)
  - No energy level assigned
  - No duration estimated
  - No clear project destination
  - No next action specified

### Processed Task Definition
- A processed task is one that meets all the criteria outlined in the processing tasks rule.
- This includes:
  - Assigned project destination
  - Appropriate location contexts
  - Relevant activity contexts
  - Concise task action and additional notes/description for context
  - Correct energy level
  - Estimated duration
  - Clearly defined next action, with subtasks as necessary
- Once all criteria are met, the task can be moved to an appropriate project, usually "#processed."

---
