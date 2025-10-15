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
  - Energy level (@lowenergy, @medenergy, @highenergy)
  - Duration (@short, @medium, @long)
  - Next action (what's the immediate physical action?)
- User responds: "yes"/"go ahead" or specifies changes
- NO preamble, NO summary - just present batch and suggestions
- Once approved, process ALL tasks in batch before moving to next batch

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
- **Every task MUST have a clear next action**
- Next action = immediate, physical action to move task forward
- Format: Either main task with @next OR subtask with @next
- Examples:
  - "Repair sprinkler" → Next: "Check shed for spare parts" @next
  - "Plan birthday party" → Next: "Call venue for availability" @next
  - "Buy groceries" → Can be its own @next (single simple action)

### Task Presentation Format
**NEVER use preambles or conclusions**. Present batches like this:

**Task 1:** Fix leaking tap
**Contexts:** @home @maintenance
**Energy:** @medenergy
**Duration:** @medium
**Next Action:** Get wrench from shed @next

**Task 2:** Buy paint
**Contexts:** @bunnings @errand
**Energy:** @lowenergy
**Duration:** @medium
**Next Action:** (This IS the next action) @next

(blank line between tasks)

User responds: "yes" or "change task 2 to @medenergy"

### Processing Batch Operations
- **NEVER process one task at a time** - always complete entire batch
- When user approves, execute ALL operations in sequence:
  - Move all tasks to destination project
  - Update all labels in one sweep
  - Create all subtasks
- Then ask: "Batch complete. Ready for next 5?"

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
