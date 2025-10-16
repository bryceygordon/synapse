# Inbox Processing Rules - GTD Clarify Phase

## Processing Strategy

- When user asks to "process inbox", list ALL inbox items first
- Process in batches that make sense based on complexity:
  - Simple/similar tasks: 5-10 at a time
  - Complex tasks requiring discussion: 1-3 at a time
  - Use judgment to optimize workflow
- After each batch, CONTINUE automatically until inbox is EMPTY
- Report progress: "Processed 8 items, 12 remaining..."

## Decision Tree for Each Item

1. **Is it a grocery item?** → Move to "groceries" (done, no contexts)
2. **Is it a question for someone?** → Move to "questions" + @person + (@call if phone)
3. **Is it recurring?** → Move to "routine" + contexts
4. **Is it just a reminder?** → Move to "reminder" + due date
5. **Is it an appointment?** → Create TWO tasks:
   - Main task → "processed" + contexts
   - Reminder → "reminder" + due date/time
6. **Is it actionable?** → Move to "processed" + contexts

## For Actionable Tasks

- Identify contexts (where/how/who/when)
- Combine contexts appropriately
- Set priority ONLY if user indicates criticality
- Set due date ONLY if must be done that exact day

## Reminder Task Pattern

For appointments needing notification, create TWO tasks:

**Example:** Doctor appointment Thursday at 2pm
1. "Doctor appointment - Dr. Smith" → processed, @errand, @waiting
2. "REMINDER: Doctor appointment 2pm" → reminder, due Thursday 2pm

**Rationale:** Separates actionable task from time-based notification

## Philosophies

### Priority
- **Priorities are SACRED** - use extremely sparingly
- Default: No priority (P4) for almost all tasks
- **Ranking**: P4/none (default), P3 (important), P2 (must do), P1 (critical)
- Only set when truly critical
- Never auto-assign unless explicitly requested

### Due Dates
- **Use for:** Planning what tasks to do on specific days
- **Don't use for:** Not applicable - use dates freely for planning
- **Important dates:** Mark with corresponding priority (P1-P3) based on importance
