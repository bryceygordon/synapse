# Synapse Project - Claude Workflow Instructions

## Git Workflow

**ALWAYS commit AND push changes automatically** - don't ask, just do it:
- When you complete work on a feature/fix, commit it
- Immediately follow the commit with `git push`
- User prefers commits to be pushed automatically as part of normal workflow
- Only ask about git operations if they're destructive (force push, hard reset, etc.)

## Todo List Usage

- Use TodoWrite for multi-step tasks to track progress
- Mark todos as completed immediately when done
- Keep user informed of progress through the todo list

## Todoist Processing Workflow

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

### Expected Interaction Flow - Constrained Tools

**Key Advantages of Constraining Tools:**
1. **Proposals are always valid** - AI can't suggest invalid enum values
2. **Fewer tokens** - No need to explain valid options in prompt (they're in the schema)
3. **Impossible to mess up** - Type system enforces correctness
4. **Flexibility remains** - Fallback tools handle edge cases
5. **Self-documenting** - Tool schemas serve as both constraints and documentation

**Constrained Processing Example:**
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

---
