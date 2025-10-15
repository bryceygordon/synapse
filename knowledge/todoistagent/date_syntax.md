# Todoist Date Syntax Reference

## Critical Date Format Rule

- **NON-RECURRING tasks**: ALWAYS calculate exact date, use YYYY-MM-DD format
- **RECURRING tasks**: Use natural language (e.g., "every monday")
- **NEVER guess** at natural language for specific dates

**Why:** Eliminates ambiguity, ensures 100% accuracy

## Explicit Date Format (RECOMMENDED)

- **Date only:** "2025-11-03" (YYYY-MM-DD)
- **With time:** "2025-11-03 10:00" (24-hour format preferred)
- Times interpreted in user's timezone (Australia/Sydney)

## Natural Language (ONLY for recurring/simple)

- **Acceptable:** "today", "tomorrow"
- **AVOID:** "next monday", "first monday of next month", "in 3 days"
- **Why avoid?** Requires calculation anyway - use YYYY-MM-DD!

## Recurring Tasks

- **Simple:** "every day", "every monday", "every weekend"
- **Multiple:** "every monday, wednesday, friday"
- **Intervals:** "every 3 days", "every 2 weeks", "every month"
- **Alternating:** "every other day", "every other week"
- **Nth weekday:** "every 2nd tuesday", "every last friday"
- **From completion:** "every! 3 days" (reschedules from completion)
- **With time:** "every monday at 9am"

## Date Calculation Process

1. Call `get_current_time()` to get today (e.g., "2025-10-15")
2. Parse user's request (e.g., "first monday of next month")
3. Calculate exact date:
   - Next month = November 2025
   - First Monday = November 3, 2025
4. Format as YYYY-MM-DD: "2025-11-03"
5. Add time if specified: "2025-11-03 10:00"

## Examples (CORRECT WAY)

- User: "tomorrow at 10am" → AI: `"2025-10-16 10:00"`
- User: "next Monday" → AI: `"2025-10-20"`
- User: "first Monday of next month" → AI: `"2025-11-03"`
- User: "every Friday at 5pm" → AI: `"every friday at 5pm"` (recurring OK)
- User: "in 3 days" → AI calculates: `"2025-10-18"`

## Best Practices

1. **ALWAYS call get_current_time first** - know what "today" is!
2. Calculate exact dates, use YYYY-MM-DD
3. Use natural language ONLY for recurring
4. Include times in 24-hour format
