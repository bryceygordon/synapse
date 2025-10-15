# Project Structure - Workflow States

## Projects = Workflow States

In this system, projects represent workflow states, not traditional containers.

### Available Projects

- **Inbox**: All new items land here first - DEFAULT for all new tasks
- **processed**: Active actionable tasks (items move here after clarification)
- **routine**: Recurring tasks and habits
- **reminder**: Date-based reminders (often paired with actionable tasks)
- **questions**: Things to ask people
- **groceries**: Shopping list (BYPASS GTD - just add items directly, no contexts)

### Critical Rules

1. **ALWAYS create new tasks in "Inbox"** (not "processed")
2. Tasks only move to other projects during processing/clarification
3. Exception: Groceries can go directly to "groceries" project
4. The # symbol is ONLY for display/documentation - use plain names in API calls
   - Example: Use "Inbox" NOT "#inbox" in create_task() or move_task()

### Default Project Rule

When creating tasks, always default to project_name="Inbox" unless:
- User explicitly specifies another project
- It's a grocery item (use "groceries")
