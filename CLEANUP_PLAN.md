# Project Cleanup Plan

## Files to Remove

### Redundant Test Scripts
- `test_knowledge_query.py` - Simple query test, superseded by test_learning_protocol.py

### Completed/Outdated Documentation
- `REFACTORING_ROADMAP.md` - Refactoring completed, archive to docs/archive/
- `PROJECT_VISION.md` + `VISION.md` - Duplicate vision docs, consolidate into one

### Files to Keep (Active)
- `test_agent_conversation.py` - General conversation testing
- `test_knowledge_updates.py` - Knowledge CRUD testing
- `test_learning_protocol.py` - Before/after confirmation testing
- `test_weekly_review_automated.py` - Weekly review workflow testing
- All `tests/*.py` - Formal test suite
- `claude.md` - Main development guide
- `README.md` - Project readme
- `INSTALLATION.md` - Setup guide

## Documentation Consolidation

### Consolidate into claude.md:
1. **AGENT_CONTROL_GUIDE.md** - Agent control patterns section
2. **ARCHITECTURAL_BLUEPRINT.md** - Architecture overview section
3. **CONVERSATION_FLOW.md** - Conversation patterns section
4. **docs/JIT_KNOWLEDGE_ARCHITECTURE.md** - JIT Knowledge section

### Keep Separate:
- `ROADMAP.md` - Future plans
- One consolidated `VISION.md` (merge PROJECT_VISION.md into it)

## Actions

1. Remove redundant test: `test_knowledge_query.py`
2. Archive completed roadmap: `REFACTORING_ROADMAP.md` → `docs/archive/`
3. Merge `PROJECT_VISION.md` into `VISION.md`, then remove PROJECT_VISION.md
4. Add sections to `claude.md` from:
   - AGENT_CONTROL_GUIDE.md
   - ARCHITECTURAL_BLUEPRINT.md
   - CONVERSATION_FLOW.md
   - docs/JIT_KNOWLEDGE_ARCHITECTURE.md
5. Remove the 4 consolidated docs after adding to claude.md
6. Run full test suite to verify nothing broke
