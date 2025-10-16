# Label Fixing Procedures

## When Asked to Fix Illegal/Malformed Labels

### Procedure

1. Call `list_tasks()` to get ALL tasks
2. Examine the "labels" array in DATA payload (not formatted text!)
   - Look at: `data["tasks"][i]["labels"]`
3. Identify illegal labels containing:
   - **Commas:** "yard,maintenance" → should be ["yard", "maintenance"]
   - **@ symbols:** "@home" → should be "home"
   - **Mixed:** "yard, @chore" → should be ["yard", "chore"]
4. For EACH illegal label, split and clean:
   - Split on commas
   - Remove @ symbols
   - Trim whitespace
5. Update ONLY tasks with illegal labels
6. Process ALL tasks (not just first page)

### Example Correction

**Found:** `labels = ["yard,@maintenance,@weather,@medenergy,@medium"]`

**Steps:**
1. Split on comma: `["yard", "@maintenance", "@weather", "@medenergy", "@medium"]`
2. Remove @ symbols: `["yard", "maintenance", "weather", "medenergy", "medium"]`
3. Call: `update_task(task_id="...", labels=["yard", "maintenance", "weather", "medenergy", "medium"])`

### Critical Note

- Use the DATA payload, NOT formatted text!
- WRONG: Parsing "[@yard, @maintenance]" from summary
- CORRECT: Reading `["yard", "maintenance"]` from `data["tasks"][i]["labels"]`

### Completeness Principle

When fixing labels or doing ANY bulk operation:
- Query and count total matching tasks FIRST
- Process in efficient batches (typically 10-20 at a time for bulk operations)
- Keep detailed count: "Fixed 15/47 tasks, continuing..."
- Do NOT stop until processed the LAST matching task
- Confirm completion: "All 47 tasks processed ✓"
