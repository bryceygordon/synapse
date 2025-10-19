# Mini-Project 005: Multi-Model Routing
**Model**: Claude 3.5 Sonnet (for planning only - execution can use Haiku)
**Estimated Tokens**: 1,500 input + 1,000 output per task
**Estimated Cost**: $0.004 total (Haiku)
**Priority**: 🎯 CRITICAL (Phase 4.1: 83% cost reduction for simple queries)
**Time**: 4-6 hours total (spread across 6 mini-tasks)
**Impact**: 40-50% overall cost reduction (83% cheaper for ~40% of requests)

---

## Problem Statement

**Current Issue**: All requests use the same expensive model (gpt-4o or claude-sonnet-4.5) regardless of complexity. Simple CRUD operations costing $0.15 with gpt-4o-mini.

**Token Cost Analysis**:
- **Current**: Every request uses $2.50/1M token model
- **Target**: Route simple queries to $0.15/1M token model
- **Savings**: 83% cost reduction for ~40% of requests
- **Monthly Impact**: $9 → $4.20 (35% savings at current usage)

---

## Solution Overview

**Implement Intelligent Model Routing** based on request complexity:

| Task Type | Model | Cost Ratio | Use Cases |
|-----------|-------|------------|-----------|
| **Simple** | gpt-4o-mini | 16x cheaper | List tasks, get time, basic queries |
| **Medium** | gpt-4o | Baseline | Inbox processing, task creation |
| **Complex** | claude-sonnet-4.5 | 20% more expensive | Weekly reviews, complex reasoning |

**Auto-detection logic**:
- Keywords: "show", "list", "get", "what", "how many"
- Context: Short messages (< 20 words)
- Command patterns: Direct CRUD operations

---

## Architecture Context

**Files that need modification**:
1. `core/providers/openai_provider.py` - Add model selection logic
2. `core/main.py` - Add routing decision to chat function
3. Agent YAML configs - Default model per agent

**Current flow**:
```
User → chat() → provider.send_message(model=agent.model) → API
```

**Target flow**:
```
User → chat() → _select_model() → provider.send_message(model=selected) → API
```

---

## Implementation Strategy

### Mini-Task 0: Current State Analysis (20 min, $0.001)
- Examine current provider and main.py architecture
- Document current model usage patterns
- **Critical**: Baseline measure current usage with `./synapse to > help`

### Mini-Task 1: Core Routing Function (45 min, $0.002)
- Add `_select_model()` method to provider or main.py
- Implement keyword-based detection
- Simple/medium/complex tiers

### Mini-Task 2: Provider Integration (30 min, $0.002)
- Update `send_message()` to accept model parameter
- Ensure backward compatibility with agent.model defaults
- Test with different models

### Mini-Task 3: Chat Function Routing (30 min, $0.002)
- Modify `chat()` to call `_select_model()`
- Integrate with user message analysis
- Preserve agent-level model defaults

### Mini-Task 4: Agent-Specific Defaults (25 min, $0.002)
- Update agent configs with appropriate default models
- Simple agents → gpt-4o-mini, complex agents → claude-sonnet-4.5

### Mini-Task 5: Validation & Testing (45 min, $0.003)
- Test routing logic with various message types
- Verify model selection accuracy
- Measure token cost savings
- **Critical validation**: Ensure complex tasks still use powerful models

**Total Time**: 4-6 hours
**Total Cost**: $0.012 per Haiku

---

## Detection Logic

### Simple Query Detection (`→ gpt-4o-mini`)
```python
simple_keywords = ["list", "show", "get", "find", "what", "how many", "count"]
simple_patterns = ["tasks in", "time", "status", "check if"]

def _is_simple_query(message: str) -> bool:
    msg_lower = message.lower()
    word_count = len(message.split())

    # Keyword match in first 2-3 words
    first_words = msg_lower.split()[:3]
    has_keyword = any(kw in first_words for kw in simple_keywords)

    # Short message + keyword
    is_short_and_keyword = word_count < 20 and has_keyword

    # Direct commands
    is_direct_command = any(msg_lower.startswith(p) for p in simple_patterns)

    return is_short_and_keyword or is_direct_command
```

### Complex Query Detection (`→ claude-sonnet-4.5`)
```python
complex_keywords = ["analyze", "review", "plan", "optimize", "complex", "explain"]
complex_contexts = ["weekly", "strategy", "learn", "teach", "complex workflow"]

def _is_complex_query(message: str) -> bool:
    msg_lower = message.lower()

    # Explicit complexity markers
    has_complex_marker = any(kw in msg_lower for kw in complex_keywords)

    # Context-based (weekly review, etc.)
    has_complex_context = any(ctx in msg_lower for ctx in complex_contexts)

    # Long messages (>50 words)
    is_long_message = len(message.split()) > 50

    return has_complex_marker or has_complex_context or is_long_message
```

---

## Code Examples

### Provider Integration:
```python
# core/providers/openai_provider.py
def send_message(self, client, messages, system_prompt, model=None, tools=None):
    """Send message with optional model override."""

    # Use provided model or default to gpt-4o for backward compatibility
    model = model or "gpt-4o"

    # Rest of existing send_message logic...
```

### Main Chat Function:
```python
# core/main.py
def chat(agent_name: str):
    """Main chat function with intelligent model routing."""

    user_message = get_user_input()

    # Auto-select model based on message complexity
    selected_model = _select_model_for_message(user_message, agent_config.get('default_model', 'gpt-4o'))

    # Send with selected model
    response = provider.send_message(..., model=selected_model)

    # Display model used for transparency
    display_model_info(selected_model)

    return response
```

### Model Selection Function:
```python
def _select_model_for_message(message: str, agent_default: str) -> str:
    """Select optimal model for user message."""

    # Always use agent default if explicitly set
    if agent_default in ['gpt-4o-mini', 'gpt-4o', 'claude-sonnet-4.5']:
        return agent_default

    # Auto-detection for 'auto' setting
    if _is_simple_query(message):
        return "gpt-4o-mini"
    elif _is_complex_query(message):
        return "claude-sonnet-4.5"
    else:
        return "gpt-4o"  # Medium complexity default
```

---

## Success Criteria

### ✅ Must Pass:
- [ ] Simple queries route to gpt-4o-mini (83% cost reduction)
- [ ] Complex queries still use claude-sonnet-4.5 (no degradation)
- [ ] Agent defaults respected (todoist_inbox uses mini, todoist_review uses sonnet)
- [ ] Backward compatibility maintained (existing configs work)
- [ ] Model selection logged for analysis
- [ ] No functionality degradation (>95% routing accuracy)

### File Impacts:
- `core/providers/openai_provider.py`: +15 lines (model parameter support)
- `core/main.py`: +30 lines (routing logic)
- Agent configs: Update default_model fields

---

## Validation Strategy

### Model Selection Testing:
```python
# Test various message types
test_cases = [
    ("list my tasks", "gpt-4o-mini"),
    ("show inbox", "gpt-4o-mini"),
    ("analyze my productivity this week", "claude-sonnet-4.5"),
    ("help me plan my day", "gpt-4o"),
]

for message, expected_model in test_cases:
    selected = _select_model_for_message(message)
    assert selected == expected_model, f"Expected {expected_model}, got {selected}"
```

### Cost Impact Measurement:
```bash
# Before routing
./synapse to > list tasks  # Cost: $0.002
./synapse to > analyze my week  # Cost: $0.008

# After routing
./synapse to > list tasks  # Cost: $0.0003 (83% savings)
./synapse to > analyze my week  # Cost: $0.008 (unchanged)
```

### Accuracy Validation:
- **Target accuracy**: >95% correct model selection
- **Fallback**: Medium complexity (gpt-4o) if detection fails
- **Learning**: Log misclassifications for algorithm improvement

---

## Safety Features

### Conservative Fallback:
```python
# If in doubt, use more powerful model (never downgrade complex tasks)
def _select_model_conservative(message: str) -> str:
    if _is_simple_query(message):
        return "gpt-4o-mini"  # Safe - underpowered model for simple task
    else:
        return "gpt-4o"  # Conservative - never risk underpowering
```

### Override Mechanisms:
```yaml
# agents/todoist.yaml - Force model if needed
model_override: claude-sonnet-4.5  # Skip auto-detection for critical agent
```

### Emergency Rollback:
```bash
# Disable routing temporarily
export SYNAPSE_FORCE_MODEL=gpt-4o

# Or modify agent config
default_model: gpt-4o  # Override to single model
```

---

## Quality Assurance

### Routing Accuracy Testing:
1. **Simple queries** (→ mini): "list tasks", "what time", "show inbox"
2. **Complex queries** (→ sonnet): "weekly review", "analyze patterns", "strategize"
3. **Medium queries** (→ gpt-4o): "process inbox", "move task", "set reminder"

### Performance Validation:
- **Speed**: gpt-4o-mini responses < 2 seconds
- **Quality**: No degradation in response quality
- **Cost**: Verify >80% cost reduction for simple queries

---

## Next Steps After Completion

**Phase 4.2**: Local Tool Execution
- Execute deterministic tools locally before API calls
- Save 1,000-2,000 tokens per avoided roundtrip
- Example: "What's the time?" → Local execution, no API call

**Phase 4.3**: Batch Operations
- Process inbox in batches instead of one-by-one
- 46 tasks × 2 calls = 92 API calls → 2 calls total
- >90% token savings per inbox processing

---

## Expected Outcomes

### Performance Impact:
- **Simple queries**: 83% cheaper, slightly faster responses
- **Complex queries**: Same cost, same quality
- **Overall**: 40% cost reduction across all interactions

### User Experience:
- ✅ Transparent model selection (may show "Using fast model")
- ✅ No perceived degradation in response quality
- ✅ Faster responses for simple queries
- ✅ Cost savings without feature reduction

---

## Ready to Execute

**Current Status**: All prerequisites complete (task compression, docstring compression)
**Next Mini-Task**: Implement core routing function

**First Command**:
```bash
./synapse to > list tasks  # Baseline simple query cost
# Expected: ~$0.002
```

---

**Time to Completion**: 4-6 hours across mini-tasks
**Cost**: $0.012 per Haiku
**Impact**: 40-50% cost reduction through intelligent routing

---