# Just-In-Time (JIT) Knowledge Architecture

## Overview

The Just-In-Time Knowledge Architecture is a system-wide pattern that dramatically reduces token usage by loading knowledge modules on-demand rather than upfront. This approach maintains accuracy while optimizing for cost and performance.

## Problem

Traditional agent implementations load all knowledge into the system prompt, resulting in:
- **Massive token consumption**: 10,475 tokens for simple operations
- **Poor cost efficiency**: Paying for unused knowledge on every request
- **Slow response times**: Large prompts increase latency
- **Context bloat**: Knowledge files grow over time, making everything worse

### Example: TodoistAgent Token Breakdown (Before)
```
System Prompt:      4,702 tokens (45%)
Knowledge Files:    3,682 tokens (35%)  ← Auto-loaded every session!
Tool Schemas:       1,472 tokens (14%)
Conversation:         600 tokens (6%)
------------------------
TOTAL:             10,475 tokens
```

## Solution: Just-In-Time Knowledge Loading

Instead of loading all knowledge upfront, we:
1. **Slim the system prompt** to essential instructions and references
2. **Split knowledge into modular topics** (separate markdown files)
3. **Expose `query_knowledge(topic)` as a tool** for AI to use on-demand
4. **Leverage prompt caching** for frequently-used content

### Architecture Benefits

- ✅ **54.5% token reduction** (10,475 → 4,768 tokens)
- ✅ **System-wide pattern** applicable to ALL agents
- ✅ **Maintains accuracy** - AI loads knowledge when needed
- ✅ **Automatic caching** - repeat queries cost nearly nothing
- ✅ **Modular knowledge** - easy to maintain and expand
- ✅ **Self-documenting** - Topics are cataloged in index.json

## Implementation Guide

### 1. Create Knowledge Directory Structure

```
knowledge/
└── {agent_name}/
    ├── index.json           # Topic catalog with metadata
    ├── topic1.md            # Modular knowledge file
    ├── topic2.md
    └── ...
```

### 2. Define Knowledge Index

Create `knowledge/{agent_name}/index.json`:

```json
{
  "description": "Just-In-Time knowledge base for {AgentName}",
  "topics": {
    "topic_name": {
      "file": "topic_file.md",
      "description": "Brief description of what this topic contains",
      "tokens_approx": 500
    }
  }
}
```

### 3. Split System Prompt

**BEFORE (bloated):**
```yaml
system_prompt: >
  You are an assistant...

  # PROJECT STRUCTURE
  [4,000 tokens of detailed documentation]

  # CONTEXT LABELS
  [2,000 tokens of label definitions]

  # PROCESSING RULES
  [1,500 tokens of decision trees]

  # ... etc
```

**AFTER (lean):**
```yaml
system_prompt: >
  You are an assistant...

  # YOUR TOOLS
  - **query_knowledge(topic)**: Load specific knowledge on-demand

  ## Available Knowledge Topics
  - "topic1" - Brief description
  - "topic2" - Brief description

  # WORKFLOW
  1. When you need specific guidance, call query_knowledge(topic)
  2. Use the knowledge to inform your decisions
  3. Execute user's request
```

### 4. Update Agent Configuration

No additional code needed! The `BaseAgent` class already provides:
- ✅ `query_knowledge(topic)` method
- ✅ Knowledge index loading
- ✅ Error handling for missing topics

### 5. Remove Auto-Loading

In `core/main.py`, modify startup sequences to NOT auto-load knowledge:

```python
# BEFORE: "Initialize - get current time and load rules"
# AFTER: "Initialize - get current time"
messages.append({
    "role": "user",
    "content": "Initialize - get current time"  # No "load rules"!
})
```

## Example: TodoistAgent Refactoring

### Token Reduction Achieved

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| System Prompt | 4,702 tokens | 708 tokens | 84.9% |
| Total Session | 10,475 tokens | 4,768 tokens | 54.5% |
| Cached Tokens | 0 | 4,480 tokens | N/A |

### Knowledge Topics Created

1. **project_structure.md** (~400 tokens) - Project workflow states
2. **context_labels.md** (~800 tokens) - All context labels with examples
3. **processing_rules.md** (~600 tokens) - GTD inbox processing decision tree
4. **date_syntax.md** (~500 tokens) - Date format reference
5. **label_fixing.md** (~300 tokens) - Label fixing procedures
6. **learned_rules.md** (~1000 tokens) - User-approved learned rules

### Usage Pattern

```python
# AI decides it needs label guidance
response = agent.query_knowledge("context_labels")

# Result: 800 tokens loaded on-demand
# Without JIT: 3,682 tokens loaded upfront (4.6x waste!)
```

## Best Practices

### 1. Keep System Prompt Minimal
- Core identity and principles only
- Reference knowledge topics, don't duplicate them
- Aim for <1,000 tokens

### 2. Organize Knowledge Logically
- One topic = one concern
- Aim for 300-1,000 tokens per topic
- Use descriptive names

### 3. Update Index Metadata
- Keep token estimates accurate
- Write clear descriptions
- Order topics by usage frequency (most common first)

### 4. Let AI Decide
- Don't auto-load knowledge on startup
- Trust the AI to query_knowledge() when needed
- Monitor which topics are frequently accessed

### 5. Leverage Caching
- OpenAI gpt-4o-mini: Automatic caching for content >1,024 tokens
- Anthropic Claude: Use prompt caching headers
- Cached tokens cost 50% less (or free in some cases)

## Applying to Other Agents

This pattern is **system-wide** and should be applied to ALL Synapse agents:

1. **CoderAgent** - Likely has similar prompt bloat
2. **CustomAgents** - Any agent with >2,000 token system prompt
3. **Future Agents** - Use JIT architecture from day one

### Migration Checklist

- [ ] Analyze current token usage (use test script)
- [ ] Identify knowledge sections in system prompt
- [ ] Create `knowledge/{agent_name}/` directory
- [ ] Split knowledge into modular files
- [ ] Create `index.json` catalog
- [ ] Refactor system prompt to reference topics
- [ ] Remove auto-loading from startup sequence
- [ ] Test token reduction
- [ ] Verify accuracy maintained

## Monitoring and Optimization

### Track Token Usage

Use the built-in token tracking in `core/main.py`:

```python
# Per-turn display
console.print(
    f"Tokens: {response.usage.input_tokens} in + "
    f"{response.usage.output_tokens} out = "
    f"{response.usage.total_tokens} total"
)

# Session summary on exit
display_token_usage(session_tokens, agent.name, agent.model)
```

### Identify Hot Topics

Monitor which topics are queried most frequently:

```python
# Add to BaseAgent.__init__
self._knowledge_access_counts = {}

# Track in query_knowledge()
self._knowledge_access_counts[topic] = \
    self._knowledge_access_counts.get(topic, 0) + 1
```

### Optimize Cache Hits

- Keep frequently-accessed topics >1,024 tokens for automatic caching
- Structure topics to be reusable across multiple requests
- Monitor cache hit rates in token usage reports

## Cost Analysis

### Example Session (3 requests)

**Before JIT:**
- Request 1: 10,475 input + 377 output = 10,852 tokens
- Request 2: 10,475 input + 423 output = 10,898 tokens
- Request 3: 10,475 input + 312 output = 10,787 tokens
- **Total: 32,537 tokens**

**After JIT (with caching):**
- Request 1: 4,768 input (0 cached) + 377 output = 5,145 tokens
- Request 2: 4,768 input (4,480 cached) + 423 output = 5,191 tokens
- Request 3: 4,768 input (4,480 cached) + 312 output = 5,080 tokens
- **Total: 15,416 tokens**

**Savings: 52.6% reduction** (32,537 → 15,416 tokens)

With OpenAI's 50% discount on cached tokens, the effective cost is even lower!

## Technical Implementation

### BaseAgent.query_knowledge() Method

```python
def query_knowledge(self, topic: str) -> str:
    """
    Retrieve specific knowledge on-demand (Just-In-Time loading).

    This is a tool exposed to AI agents to query their knowledge base
    only when needed, dramatically reducing token usage.
    """
    try:
        index = self._load_knowledge_index()

        if topic not in index.get("topics", {}):
            available = list(index.get("topics", {}).keys())
            return json.dumps({
                "status": "error",
                "error": f"Topic '{topic}' not found",
                "available_topics": available
            })

        topic_info = index["topics"][topic]
        topic_file = self.knowledge_dir / topic_info["file"]

        if not topic_file.exists():
            return json.dumps({
                "status": "error",
                "error": f"Knowledge file not found: {topic_file}"
            })

        content = topic_file.read_text()

        return json.dumps({
            "status": "success",
            "topic": topic,
            "description": topic_info.get("description", ""),
            "content": content
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to load knowledge: {str(e)}"
        })
```

### Knowledge Directory Resolution

```python
# In BaseAgent.__init__
self.knowledge_dir = Path("knowledge") / self.name.lower().replace(" ", "_")
```

Examples:
- `TodoistAgent` → `knowledge/todoistagent/`
- `CoderAgent` → `knowledge/coderagent/`
- `My Custom Agent` → `knowledge/my_custom_agent/`

## Future Enhancements

1. **Analytics Dashboard** - Track which topics are accessed most
2. **Auto-Optimization** - Merge rarely-used topics, split hot topics
3. **Version Control** - Track knowledge changes over time
4. **A/B Testing** - Compare prompt variations for accuracy
5. **Shared Knowledge** - Cross-agent knowledge bases (e.g., common GTD principles)

## Conclusion

The Just-In-Time Knowledge Architecture is a foundational pattern for Synapse that:
- Reduces token usage by 50%+
- Maintains or improves accuracy
- Scales to any agent
- Leverages provider caching automatically

Apply this pattern to ALL agents for maximum efficiency and cost savings.

---

**Date Implemented:** October 15, 2025
**Agent:** TodoistAgent (OpenAI gpt-4o-mini)
**Token Reduction:** 54.5% (10,475 → 4,768 tokens)
**Status:** ✅ Production Ready
