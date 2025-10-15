# Inbox Processing Rules - GTD Clarify Phase

## Processing Strategy

- When user asks to "process inbox", list ALL inbox items first
- Process in batches (5-10 at a time)
- After each batch, CONTINUE automatically until inbox is EMPTY
- Report progress: "Processed 5 items, 12 remaining..."

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
- Default: No priority (P1) for almost all tasks
- Only set when truly critical
- Never auto-assign unless explicitly requested

### Due Dates
- **Due dates mean "MUST be done on this exact day"**
- NOT "I'd like to do this by then"
- Use for: Hard deadlines, appointments, time-critical items
- Don't use for: Soft goals, aspirational timelines
