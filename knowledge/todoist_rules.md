# Learned GTD Rules

**Purpose:** This file stores learned preferences and patterns discovered through conversations.
**Maintained by:** TodoistAgent (updated with user approval)
**Last updated:** 2025-10-16 2025-10-16 2025-10-16 2025-10-16 2025-10-16 2025-10-16 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15 2025-10-15

---

## Weekly Review Process

The user has a specific weekly review workflow that must be followed:

When starting a weekly review, always begin with processing tasks from the Inbox project before moving on to the next projects.

### Intuitive Processing Workflow:
- **Agent presents pre-processed suggestions** for each batch based on learned patterns
- User responds with "go ahead" or specifies which items to change
- This streamlines the review process - agent does the heavy lifting, user just approves/refines
- Agent should confidently suggest: project, contexts, energy/timeframe labels, next actions
- User only needs to correct exceptions rather than specify everything from scratch

### Review Order:
1. **Inbox Processing** (free-flowing, natural language)
2. **#Processed Review** (oldest→newest, batches of 5 or less)
3. **#Routine Review** (fitness for purpose)
4. **#Reminder Review**
5. **Other Projects Review**

### Key Principles:
- Present items in **batches of 5 or less** to maintain smooth flow
- User gives natural language instructions - agent must intuit meaning
- Gather ALL information before processing any task (full optimization)
- Check for **recently completed next actions** and ask what needs to be done next
- Use task IDs to store context for future reference

---

## Task Processing Rules

When processing tasks for the user, present a maximum of 3 tasks at a time.

### Bulk Task Updates:
- **ALWAYS process multiple task updates in one batch** - never do them one at a time
- When fixing malformed tags, updating multiple tasks, or making bulk changes: complete ALL updates before asking for next steps
- User finds one-at-a-time processing inefficient and disruptive to workflow
- Complete the entire batch operation in sequence without waiting for individual confirmations

### Label Format Requirements:
- **NEVER use @@label format** - always single @ symbol
- All labels must be @label format (not @@label)
- Agent must fix any @@label errors immediately when spotted

### Task Presentation Format:
User prefers clean, nested presentation format:
```
**Task Title**
  - Contexts: @context1 @context2
  - Energy: @energylevel  
  - Timeframe: @timeframe
  - Special: @nokids (if applicable)
  - Next Action: [description] @next @contexts
```
This is much easier to read than inline format.

When presenting batches for weekly review, use the following format:

**Task X:** [Task Description]
**Contexts:** [List of contexts]
**Energy:** [Energy level]
**Timeframe:** [Timeframe]
**Next Action:** [Next action] @next  

Separate each task by a new line without any premables or conclusions.

### Batch Processing Requirement:
- **NEVER process tasks one at a time** during reviews
- **Process entire batches together** - all moves, updates, and subtask creation in sequence
- User finds one-at-a-time processing inefficient and disruptive to flow
- Complete all changes for a batch before asking for next steps

### Timeframe Labels (Task Duration Estimation):
- **@quick**: Short tasks (< 30 minutes)
- **@medium**: Medium tasks (30-60 minutes)
- **@long**: Long tasks (1-2+ hours)

### Energy Labels (Required for ALL chores):
- **@lowenergy**: Tasks needing minimal energy
- **@medenergy**: Tasks needing moderate energy
- **@highenergy**: Tasks needing significant energy
  - For @highenergy chores: Ask if kids need to be away
  - If yes, add **@nokids** tag

### Next Actions (CRITICAL):
- **EVERY task MUST have a @next subtask** (next action)
- Next action = immediate, physical action to move task forward
- Next action format: Subtask with `@next` label
- Examples:
  - Main: "Repair sprinkler out front"
  - Next: "Go to shed and check if spare sprinkler bodies available" @next
  - If parts needed: Create new task "Buy sprinkler parts from irrigation store"

### Task Name vs Description:
- If user's description is verbose, create snapshot task name
- Put full detail in task description field
- Task name should be easily recognizable at a glance

---

## Processing Patterns

### Duplicate Detection:
- ALWAYS check #processed for existing tasks before creating from inbox
- If duplicate found in inbox, delete inbox copy
- Maintain single source of truth for each task

### Task Optimization:
- Must gather ALL information before processing
- Every task should be fully categorized (contexts, energy, timeframe)
- Agent should learn user's categorization preferences
- Over time, **intuit** how user will categorize tasks and present suggestions
  - User can then just say "yes" or refine specific aspects

### Completed Next Actions Workflow:
- On every review (not just weekly), check recently completed @next actions
- Find parent tasks with completed next actions
- Ask user: "What's the next action for [task name]?"
- Update with new @next subtask

---

## Chore-Specific Rules

### All Chores Must Have:
1. Timeframe label (@quick, @medium, @long)
2. Energy label (@lowenergy, @medenergy, @highenergy)
3. Context labels (e.g., @home, @yard, @chore)
4. Next action subtask (@next)

### High Energy Chores:
- Always ask: "Do the kids need to be away?"
- If yes, add @nokids label

### Examples:
- "sweep under the couch":
  - @home @chore @long @medenergy
  - Next: "Get vacuum cleaner from cupboard" @next

---

## Context Inference Rules

*Agent will learn when to automatically apply which contexts based on user patterns*

---

## People Preferences

### Bec (Wife)
- *Agent will learn specific patterns about tasks involving Bec*

### William (Oldest Son)
- *Agent will learn specific patterns about tasks involving William*

### Reece (Middle Son)
- *Agent will learn specific patterns about tasks involving Reece*

### Alex (Youngest Son)
- *Agent will learn specific patterns about tasks involving Alex*

### Parents (Wendy & Ian)
- @parents is primarily an errand context (things to do at their house)
- *Agent will learn specific patterns*

---

## Task Patterns

*Agent learns common task types and how to handle them*

---

Tags must follow the format '@word' and cannot contain spaces or multiple '@' symbols in a row. Tags like '@this,@is,@a,@tag' are considered malformed and should be corrected.

Tags must not contain spaces.

When the user mentions a task number followed by 'd', it means to complete that task. For example, '5 d' means complete task 5.

### Poison/Spray Tasks:
- Tasks involving poisoning (pavers, spiders, weeds) are @weather dependent
- Always add @weather context to poison/spray tasks

### Task Completion Shorthand:
- User says "d" for done = complete the task immediately
- Quick way to mark tasks complete during reviews

### High Energy + Kids Consideration:
- @highenergy tasks often need @nokids tag
- @nokids = task requires kids to not be home
- Agent should suggest @nokids for disruptive high-energy tasks

### Simple Tasks as Next Actions:
- Some tasks are simple enough that the task itself IS the next action
- For these: add @next directly to the main task (no subtask needed)
- Examples: "sweep back patio", "call someone", "buy specific item"
- Use judgment - if task is single, clear action, it can be its own @next

### Weekly Review Planning Session:
- At END of weekly review, schedule @plan tasks into specific days
- This is separate step after all project reviews are complete

## Location-Specific Patterns

### Bunnings
- *Agent will learn what tasks typically require Bunnings*

### Parents' House
- *Agent will learn common errands at parents' house*

---

## Recurring Patterns

*Agent learns what tasks tend to recur and should go in #routine*

---

## Special Cases

*Agent learns exceptions and edge cases in the system*

---

## Notes

- All rules in this file have been approved by the user
- Rules are applied consistently once learned
- User can manually edit this file to refine rules

## Processing Rules

When the user mentions 'all tasks,' it refers specifically to tasks that are not completed unless stated otherwise.

---

Tasks with tags formatted like `@example@tag` are illegal and should be separated into distinct tags such as `@example` and `@tag`.

## Task Categorization Patterns

*Agent learns and adds patterns here as they're discovered and approved*

## Weekly Review Workflow

### Next Actions (CRITICAL GTD CONCEPT)
- Every **processed task** MUST have a clear next action.
- Items in the inbox are unprocessed and usually will NOT have a next action.
- Any task ending up in the #processed project must have a next action.
- Next action = immediate, physical action to move task forward
- Ensure next actions are "doable"; for instance, "Gather relevant tax documents" is doable, while "Complete tax return" is not.
- Format: Either main task with @next OR subtask with @next
### Examples:
  - "Repair sprinkler" → Next: "Check shed for spare parts" @next
  - "Plan birthday party" → Next: "Call venue for availability" @next
  - "Buy groceries" → Can be its own @next (single, simple action)

---

## User Patterns to Learn

### Task Management Preferences
- **Default Task Entry:** User typically adds new items directly into the "Inbox" for processing later.

---
