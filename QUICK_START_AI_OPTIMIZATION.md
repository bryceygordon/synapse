# Quick Start: AI Optimization for Synapse
**Read This First** - 5 minute overview
**Created**: 2025-10-18

---

## 🎯 The Problem

When AI assistants (Claude Code, etc.) work on Synapse, **every file read costs tokens**.

**Current costs** (per session):
- Reading `todoist.py` (2,897 lines): **15,000 tokens**
- Loading workflow docs (8 scattered files): **13,500 tokens**
- **Total**: 18,000-25,000 tokens per session ($0.05-0.15)

**After optimization**: 5,000-8,000 tokens per session ($0.01-0.03)
**Savings**: 70% reduction

---

## 📚 Documentation Structure

### Start Here (You Are Here)
- **`QUICK_START_AI_OPTIMIZATION.md`** - This file (5 min overview)

### Core Guides (Read Before Working)
1. **`AI_OPTIMIZATION_GUIDE.md`** - Comprehensive guide for AI working on Synapse
   - File structure issues
   - Token optimization checklist
   - Mandatory practices
   - ~30 min read

2. **`BIG_TO_SMALL_WORKFLOW.md`** - Delegation pattern for large projects
   - Use expensive models for planning
   - Use cheap models for execution
   - 50-70% cost savings
   - ~20 min read

### Implementation
3. **`mini-projects/001_CONSOLIDATE_DOCS.md`** - First mini-project (ready to execute)
   - Consolidate 8 docs → 1 primary source
   - 67% token reduction for context loading
   - Estimated cost: $0.004 (Haiku)
   - Can be done by cheap model RIGHT NOW

### Reference
4. **`TOKEN_OPTIMIZATION_STATUS.md`** - Current status & priorities
5. **`.claude/claude.md`** - Primary workflow guide (to be expanded)

### Agent-Specific (Different Focus)
6. **`LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md`** - For AI agents using Synapse (not AI working on Synapse)

---

## 🔴 Critical Issues (Fix These First)

### Issue 1: `todoist.py` is 2,897 Lines
**Problem**: Single monolithic file
**Impact**: 15,000 tokens per read (read 5× per session = 75,000 tokens wasted)
**Solution**: Split into 6 focused modules
**Savings**: 70% (15,000 → 5,000 tokens per session)
**Status**: ⏳ Next after docs consolidation

### Issue 2: Docs Scattered Across 8 Files
**Problem**: Redundant content, unclear which is authoritative
**Impact**: 13,500 tokens to load workflow context
**Solution**: Consolidate to `.claude/claude.md` (single source)
**Savings**: 67% (13,500 → 4,500 tokens)
**Status**: 🎯 **READY TO EXECUTE** (see `mini-projects/001_CONSOLIDATE_DOCS.md`)

### Issue 3: Verbose Tool Docstrings
**Problem**: 10-15 line docstrings in schemas (sent on every API call)
**Impact**: 600-800 tokens per API call
**Solution**: Compress to 1-2 lines, move details to comments
**Savings**: 60% (600 → 240 tokens per call)
**Status**: ⏳ After file split

---

## ✅ What to Do Right Now

### Option 1: Execute First Mini-Project (RECOMMENDED)
**Time**: 30-45 minutes
**Cost**: $0.004 (Haiku) or $0.002 (GPT-4o-mini)
**Impact**: 67% reduction in context loading

```bash
# Read the mini-project spec
cat mini-projects/001_CONSOLIDATE_DOCS.md

# Execute with a small model (Haiku or GPT-4o-mini)
# This validates the delegation pattern works

# After completion, big model reviews & commits
```

**Why this first?**
- Easiest to validate (just merging text)
- High impact (67% savings)
- Proves delegation pattern works
- Enables faster work on future optimizations

---

### Option 2: Read Full Guides First
**Time**: 50-60 minutes
**Order**:
1. Read `AI_OPTIMIZATION_GUIDE.md` (30 min)
2. Read `BIG_TO_SMALL_WORKFLOW.md` (20 min)
3. Review `mini-projects/001_CONSOLIDATE_DOCS.md` (10 min)
4. Execute mini-project (30-45 min)

**Why read first?**
- Understand full context
- Learn delegation pattern thoroughly
- Make informed decisions

---

## 🎯 The Big-to-Small Pattern (Quick Version)

```
PHASE 1: Planning (Claude 3.5 Sonnet - Expensive)
└─ Explore codebase
└─ Create detailed plan
└─ Break into mini-tasks (atomic, well-specified)
└─ Cost: $0.20-0.50

PHASE 2: Execution (Claude 3.5 Haiku - Cheap)
└─ Execute mini-task 1 (2,000 tokens)
└─ Execute mini-task 2 (2,000 tokens)
└─ Execute mini-task 3 (2,000 tokens)
└─ Cost: $0.01-0.02 (10× cheaper)

PHASE 3: Verification (Claude 3.5 Sonnet - Expensive)
└─ Review all changes
└─ Run tests
└─ Commit & push
└─ Cost: $0.05-0.10

Total: $0.26-0.62 (vs $1.00+ doing everything with Sonnet)
Savings: 40-60%
```

**Key Insight**: Big models plan, small models execute.

---

## 💰 Expected Savings

### Current Monthly Costs (AI Working on Synapse)
- 20 sessions/month
- 35,000 input + 5,000 output per session
- **Cost**: $3.60/month

### After Phase 1 Optimization (Structure Fix)
- 20 sessions/month
- 15,000 input + 5,000 output per session
- **Cost**: $1.75/month
- **Savings**: $1.85/month (51%)

### With Delegation Pattern (Large Projects)
- 10 big model sessions: $1.65
- 40 small model sessions: $0.08
- **Cost**: $1.73/month
- **Savings**: $1.87/month (52%)

### At Scale (100 sessions/month)
- Current: $18/month
- Optimized: $8.65/month
- **Savings**: $9.35/month ($112/year)

---

## 📋 Optimization Roadmap

### Week 1 (This Week)
- [x] Create optimization guides (DONE - today)
- [ ] **Execute mini-project 001** (consolidate docs) - **DO THIS NOW**
- [ ] Split `todoist.py` into 6 modules (create 6-8 mini-tasks)
- [ ] Delete obsolete files

**Impact**: 70% token reduction per session

---

### Week 2
- [ ] Compress tool docstrings (batch operation, 1 mini-task)
- [ ] Add module-level docs
- [ ] Organize test files

**Impact**: 30% reduction in per-API-call costs

---

### Ongoing
- [ ] Use delegation pattern for all large projects
- [ ] Track token savings (before/after metrics)
- [ ] Update guides with learnings
- [ ] Create mini-task template library

**Impact**: 50-70% savings on future projects

---

## 🎓 Key Learnings to Apply

1. **File size matters exponentially**
   - 3,000-line file = 15,000 tokens
   - 6 × 500-line files = 2,500 tokens (when you only read one)
   - **5× more efficient with good structure**

2. **Documentation redundancy is invisible but expensive**
   - 8 docs with 60% overlap = reading same content 3-4 times
   - Consolidation = 1× cost instead of 4×

3. **Model delegation is powerful**
   - Planning (Sonnet): $0.15
   - Execution (Haiku): $0.02
   - **7.5× cheaper for well-defined work**

4. **Always minimize file reads**
   - Check `.claude/claude.md` for file locations BEFORE exploring
   - Use line ranges when reading large files
   - Batch related operations (don't commit after every tiny change)

---

## ⚠️ Critical Rules (Always Follow)

### Before Starting Work
- [ ] Read `.claude/claude.md` for project-specific rules
- [ ] Check `AI_OPTIMIZATION_GUIDE.md` for current best practices
- [ ] Identify task type:
  - **Exploration** → Use big model
  - **Well-defined** → Create mini-tasks for small model
  - **Quick fix** → Just do it with current model

### During Work
- [ ] Minimize file reads (use Quick File Reference in `.claude/claude.md`)
- [ ] Read only what you need (use `offset` and `limit` parameters)
- [ ] Batch related changes (don't make 1 commit per tiny edit)

### Before Committing
- [ ] Validate changes (run tests, smoke test agent)
- [ ] Auto-commit & push (per `.claude/claude.md` rules)
- [ ] Update `TOKEN_OPTIMIZATION_STATUS.md` if you completed optimization work

---

## 🚀 Next Steps

### RIGHT NOW (5 minutes)
1. Read this file (✅ you're doing it!)
2. Decide: Execute mini-project or read full guides first?

### IF EXECUTING MINI-PROJECT
1. Open `mini-projects/001_CONSOLIDATE_DOCS.md`
2. Use Claude 3.5 Haiku or GPT-4o-mini (cheap model)
3. Follow instructions exactly
4. Run validation commands
5. Report results (big model will review & commit)

### IF READING GUIDES FIRST
1. Read `AI_OPTIMIZATION_GUIDE.md` (30 min)
2. Read `BIG_TO_SMALL_WORKFLOW.md` (20 min)
3. Come back and execute mini-project

---

## 🔗 Quick Links

**Core Guides**:
- [AI_OPTIMIZATION_GUIDE.md](./AI_OPTIMIZATION_GUIDE.md) - Comprehensive guide
- [BIG_TO_SMALL_WORKFLOW.md](./BIG_TO_SMALL_WORKFLOW.md) - Delegation pattern
- [mini-projects/001_CONSOLIDATE_DOCS.md](./mini-projects/001_CONSOLIDATE_DOCS.md) - First task

**Reference**:
- [TOKEN_OPTIMIZATION_STATUS.md](./TOKEN_OPTIMIZATION_STATUS.md) - Current status
- [.claude/claude.md](./.claude/claude.md) - Workflow rules

**Agent-Specific** (different focus):
- [LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md](./LONG_TERM_TOKEN_OPTIMIZATION_STRATEGY.md) - For AI agents using Synapse

---

## 💬 Questions?

**"Should I execute the mini-project or read guides first?"**
→ Execute mini-project (proves pattern works, high impact, low cost)

**"Which model should I use for mini-projects?"**
→ Claude 3.5 Haiku (best price/performance) or GPT-4o-mini (cheapest)

**"What if mini-project fails?"**
→ Report error to big model (don't try to fix - wasted tokens)

**"How do I know if delegation is worth it?"**
→ Use for: 5+ similar edits, large refactors, well-defined tasks
→ Don't use for: exploration, debugging, one-off fixes

---

**Last Updated**: 2025-10-18
**Status**: Ready to execute
**First Action**: Execute `mini-projects/001_CONSOLIDATE_DOCS.md`
