# Todoist Agent Shorthand and Tag Reference

## Shorthand Interpretation Rules

When processing user instructions from the wizard, parse the free-form string to determine the correct parameters for the `update_task` and `create_task` tools. The string is a space-separated list of commands.

### Priority
- `p1`, `p2`, `p3`, `p4`: Set the task priority.

### Due Date
- `due <natural language date>`: Use the entire string following `due` as the `due_string`. For example, `due tomorrow at 10am`, `due next friday`.

### Description
- `desc:"<text>"`: Use the text inside the quotes as the task's description.

### Labels (Context, Energy, Duration)
- Any word starting with `@` is a direct label.
- Any other word should be compared against the alias lists below.

## Tag Aliases

### Energy Tags
- `high` -> `highenergy`
- `med` -> `medenergy`
- `low` -> `lowenergy`

### Duration Tags
- `short`
- `medium`
- `long`

## Preferred Context Tags

This is the primary list of context tags. **DO NOT invent new tags.** Only use tags from this list unless the user explicitly asks you to create a new one.

- `phone`
- `email`
- `computer`
- `ai`
- `errand`
- `waiting`
- `next`
- `home`
- `chore`
- `yard`
- `parents`
- `bec`
- `william`
- `reece`
- `obsidian`
