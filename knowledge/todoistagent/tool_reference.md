# Todoist Agent Tool Reference

Complete documentation for all TodoistAgent tools.

## Core Task Operations

### create_task
Creates a new task in Todoist.

**Parameters:**
- `content` (required): Task title/description
- `project_name` (default: "Inbox"): Project name (e.g., "Processed", "Inbox", "Groceries")
- `labels` (optional): List of context labels as strings (e.g., ["home", "chore"])
  - **CRITICAL**: Must be an array/list, NOT a string!
  - Correct: `["next", "yard", "home"]`
  - WRONG: `"@next @yard @home"` or `"next yard home"`
  - Do NOT include @ prefix - it's stripped automatically
- `priority` (default: 1): Priority level 1-4 (1=lowest/none, 4=highest)
- `due_string` (optional): Due date
  - **Format**: YYYY-MM-DD for specific dates (e.g., "2025-11-03")
  - With time: "2025-11-03 10:00" or "2025-11-03 at 10am"
  - Recurring: "every monday", "every 2 weeks", etc.
  - **CRITICAL**: For non-recurring tasks, ALWAYS use YYYY-MM-DD format for accuracy
- `description` (optional): Additional notes/context for the task
- `section_name` (optional): Section name within the project
- `parent_id` (optional): Parent task ID to create a subtask
- `duration` (optional): Task duration amount (e.g., 30)
- `duration_unit` (default: "minute"): Duration unit ("minute" or "day")

**Example:**
```python
create_task(
    content="Mow the lawn",
    project_name="Processed",
    labels=["yard", "highenergy", "weather"],
    due_string="2025-10-20"
)
```

### list_tasks
Lists tasks from Todoist.

**Parameters:**
- `project_name` (optional): Filter by project name (e.g., "Inbox", "Processed")
- `label` (optional): Filter by label (e.g., "home", "urgent")
- `filter_query` (optional): Search term to filter tasks by content
- `sort_by` (optional): Sort order
  - Options: "created_asc", "created_desc", "priority_asc", "priority_desc"

**Returns:** JSON with tasks array containing:
- `id`: Task ID
- `content`: Task title
- `labels`: Array of labels (check this for malformed tags!)
- `priority`: Priority level
- `due`: Due date string
- `project_id`: Project ID
- `created_at`: Creation timestamp

**Example:**
```python
list_tasks(project_name="Inbox")
list_tasks(label="yard")
list_tasks(filter_query="doctor")
```

### update_task
Updates an existing task.

**Parameters:**
- `task_id` (required): The ID of the task to update
- `content` (optional): New task description
- `labels` (optional): New labels list (replaces existing)
  - **CRITICAL**: Must be an array/list, NOT a string!
  - Correct: `["next", "yard", "home"]`
  - WRONG: `"@next @yard @home"`
- `priority` (optional): New priority 1-4
- `due_string` (optional): New due date (use "no date" to remove)
- `description` (optional): New description
- `duration` (optional): New task duration amount
- `duration_unit` (default: "minute"): Duration unit ("minute" or "day")

**Example:**
```python
update_task(
    task_id="abc123",
    labels=["yard", "maintenance"],
    priority=2
)
```

### complete_task
Marks a task as complete.

**Parameters:**
- `task_id` (required): The ID of the task to complete

**Example:**
```python
complete_task(task_id="abc123")
```

### move_task
Moves a task to a different project.

**Parameters:**
- `task_id` (required): The ID of the task to move
- `project_name` (required): The name of the destination project

**Example:**
```python
move_task(task_id="abc123", project_name="Processed")
```

### delete_task
Permanently deletes a task.

**WARNING**: This cannot be undone. Consider completing the task instead.

**Parameters:**
- `task_id` (required): The ID of the task to delete

**Example:**
```python
delete_task(task_id="abc123")
```

## Additional Tools (Not in LITE mode)

These tools are available in FULL mode but removed from LITE to reduce token usage.
Query this topic if you need them.

### get_task
Gets detailed information about a specific task.

**Parameters:**
- `task_id` (required): The ID of the task to retrieve

**Returns:** Complete task details including description, URL, etc.

### reopen_task
Reopens a completed task.

**Parameters:**
- `task_id` (required): The ID of the task to reopen

### add_comment
Adds a comment to a task.

**Parameters:**
- `task_id` (required): The ID of the task
- `comment` (required): The comment text to add

### get_comments
Gets all comments for a task.

**Parameters:**
- `task_id` (required): The ID of the task

### list_projects
Lists all projects in Todoist.

**No parameters required.**

**Returns:** List of all projects with their IDs and names.

### list_sections
Lists sections, optionally filtered by project.

**Parameters:**
- `project_name` (optional): Project name to filter sections

### list_labels
Lists all personal labels in Todoist.

**No parameters required.**

**Returns:** List of all labels with their names and colors.

### update_rules
Updates the learned rules knowledge file and commits to git.

**IMPORTANT**: Always ask for user approval before storing new rules.

**Parameters:**
- `section` (required): The section to update (e.g., "Processing Rules")
- `rule_content` (required): The rule or preference to add (markdown formatted)
- `operation` (default: "append"): How to update ("append" or "replace")

**Example:**
```python
update_rules(
    section="Task Patterns",
    rule_content="- Tasks mentioning 'lawn' should get @yard @chore",
    operation="append"
)
```

## Common Patterns

### Fixing Illegal Labels
When you find tasks with malformed labels like `["yard,@maintenance,@weather"]`:

1. Use `list_tasks()` to get ALL tasks
2. Examine the `labels` array in the DATA payload (not formatted text!)
3. Identify illegal labels containing:
   - Commas: "yard,maintenance" → should be ["yard", "maintenance"]
   - @ symbols: "@home" → should be "home"
4. For EACH illegal label, split and clean:
   - Split on commas
   - Remove @ symbols
   - Trim whitespace
5. Call `update_task(task_id="...", labels=["yard", "maintenance", "weather"])`
6. Process ALL tasks (not just first page)

### Processing Inbox
When user asks to "process inbox":

1. Call `list_tasks(project_name="Inbox")` to get all inbox items
2. Process in batches sized appropriately for task complexity (typically 5-10 at a time)
3. For each item, determine destination project based on GTD rules
4. Use `batch_move_tasks()` for moving multiple tasks efficiently
5. Use `update_task()` to add labels, set priority, etc.
6. Continue until inbox is EMPTY
7. Report progress: "Processed 8 items, 12 remaining..."

### Creating Tasks with Dates
When user says "remind me next Monday":

1. Call `get_current_time()` to get today's date
2. Calculate the exact date (e.g., today is 2025-10-15, next Monday is 2025-10-20)
3. Use explicit format: `due_string="2025-10-20"`
4. **DO NOT** use natural language like "next Monday" for non-recurring tasks

For recurring tasks, natural language is OK:
- `due_string="every monday"`
- `due_string="every 2 weeks"`

## Tool Schema Token Costs

| Tool | Tokens (LITE) | Tokens (FULL) |
|------|--------------|---------------|
| get_current_time | 51 | 51 |
| query_knowledge | 85 | 85 |
| create_task | 218 | 218 |
| list_tasks | 109 | 109 |
| update_task | 188 | 188 |
| complete_task | 62 | 62 |
| move_task | 82 | 82 |
| delete_task | 62 | 62 |
| get_task | - | 63 |
| reopen_task | - | 64 |
| add_comment | - | 81 |
| get_comments | - | 62 |
| list_projects | - | 42 |
| list_sections | - | 59 |
| list_labels | - | 42 |
| update_rules | - | 145 |

**Total:**
- LITE (8 tools): 857 tokens
- FULL (16 tools): 1,415 tokens

**Savings: 558 tokens (39%)**
