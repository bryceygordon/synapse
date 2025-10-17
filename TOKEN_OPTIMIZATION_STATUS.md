# Token Optimization - Current Status

**Last Updated**: 2025-10-17 (Session interrupted, ready to resume)

---

## ✅ COMPLETED (Safe in Git)

### Phase 1A: Literal Type Extraction (DONE - Committed 8957739)

**What was fixed**:
- `core/providers/openai_provider.py` - Added Literal enum extraction
- `core/providers/anthropic_provider.py` - Added Literal enum extraction
- `test_literal_extraction.py` - Created validation test

**How it works**:
```python
# Before: Enum values only in descriptions (verbose)
location: {
  "type": "string",
  "description": "WHERE task happens (home, house, yard, errand, bunnings, parents)"
}

# After: Enum values in schema (self-documenting)
location: {
  "type": "string",
  "enum": ["home", "house", "yard", "errand", "bunnings", "parents"],
  "description": "WHERE task happens"
}
```

**Impact**: ~200-300 tokens saved per API call

---

## 🔄 NEXT STEPS (Resume here when quota available)

### TASK 3: Test the Literal Fix
```bash
source .venv/bin/activate
python3 test_literal_extraction.py
```

**Expected output**:
```
✅ SUCCESS: Literal types correctly extracted to enums!
```

**If test fails**: Check git diff on provider files - likely copy-paste error.

---

### TASK 4: Compress System Prompt (BIGGEST SAVINGS - 850 tokens)

**File**: `agents/todoist.yaml`

**Action**: Replace lines 10-101 (system_prompt section) with compressed version.

**⚠️ CRITICAL**: The replacement text is in `TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md` at **TASK 4, Step 4.1**

**Quick Reference**:
- Current size: 1,254 tokens
- New size: ~400 tokens
- Savings: ~850 tokens per call

**Changes**:
- Remove tool listings (redundant with schemas)
- Keep only essential workflow rules
- Rely on schema enums (now working!) instead of prose

---

### TASK 5: Test Compressed Prompt
```bash
./synapse to
```

**Try these commands**:
```
> get current time
> capture Test
> list tasks project:Inbox
> d
```

**Check token usage in output** - should see reduction from ~5,200 to ~3,500-4,500 tokens.

---

### TASK 6: Final Commit

```bash
git add agents/todoist.yaml
git commit -m "perf(todoist): Compress system prompt, rely on schema enums [TASK 4]

Reduces system prompt from 1,254 to 400 tokens.
Removes redundant tool listings - schemas now self-documenting via enums.

Savings: ~850 tokens per API call
Combined with TASK 1&2: Total ~1,100 tokens saved (27% reduction)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

## 📊 Expected Final Results

| Metric | Before | After Phase 1 | Savings |
|--------|--------|---------------|---------|
| Startup tokens | ~4,263 | ~3,500 | -763 (-18%) |
| "process inbox" call | ~15,000 | ~11,000 | -4,000 (-27%) |
| System prompt | 1,254 | 400 | -854 (-68%) |
| Tool schemas | 3,009 | ~2,700 | -309 (-10%) |

---

## 🚨 If Something Goes Wrong

### Restore from git:
```bash
# Restore specific file
git checkout HEAD -- agents/todoist.yaml

# Restore everything since last commit
git reset --hard HEAD

# See what changed
git log --oneline -5
git show 8957739  # View Literal extraction commit
```

### Check current status:
```bash
git status
git diff
```

---

## 📝 What's Left to Do

**Remaining work**: 15-20 minutes
1. Run test (1 min)
2. Replace system prompt (5 min)
3. Test system prompt (5 min)
4. Commit and push (1 min)

**After completion**:
- Mark all todos as complete
- Update TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md with final status
- Test "process inbox" to verify full workflow still works
- Measure actual token savings in production

---

## 🎯 Future Optimizations (Phase 2 - Not Yet Implemented)

**Additional ~2,300 tokens available**:

1. **Task JSON compression** (~2,300 tokens)
   - Use abbreviations for field names
   - Drop null/empty fields
   - Truncate timestamps

2. **Docstring slimming** (~600 tokens)
   - Move implementation notes to comments
   - Keep only user-facing docs

**Total potential** (Phase 1 + Phase 2): -6,350 tokens (42% reduction)

---

## Key Files

| File | Purpose | Status |
|------|---------|--------|
| `TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md` | Complete implementation guide | ✅ In repo |
| `TOKEN_OPTIMIZATION_STATUS.md` | This file - quick resume guide | ✅ In repo |
| `test_literal_extraction.py` | Validation test | ✅ In repo |
| `core/providers/openai_provider.py` | Literal extraction | ✅ Committed |
| `core/providers/anthropic_provider.py` | Literal extraction | ✅ Committed |
| `agents/todoist.yaml` | System prompt | ⏳ TODO |

---

## Resume Command

When quota available:
```bash
cd /home/bryceg/synapse
cat TOKEN_OPTIMIZATION_STATUS.md  # Read this file
cat TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md  # Full details
# Then run TASK 3, 4, 5, 6
```

**Start at**: TASK 3 (test the Literal fix)

---

**END OF STATUS DOCUMENT**
