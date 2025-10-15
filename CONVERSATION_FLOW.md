# Conversation History Management in Synapse

## Overview

Synapse manages conversation history differently for each AI provider due to their distinct API requirements. This document explains how messages flow through the system and how each provider formats them.

---

## The Message Flow

### 1. User Input
```python
messages.append({"role": "user", "content": "What time is it?"})
```

### 2. Assistant Response with Tool Calls

#### Anthropic Format:
```python
{
    "role": "assistant",
    "content": [
        {"type": "text", "text": "Let me check the time"},
        {"type": "tool_use", "id": "toolu_123", "name": "get_current_time", "input": {}}
    ]
}
```

#### OpenAI Format:
```python
{
    "role": "assistant",
    "content": None,  # or text if present
    "tool_calls": [
        {
            "id": "call_abc",
            "type": "function",
            "function": {"name": "get_current_time", "arguments": "{}"}
        }
    ]
}
```

### 3. Tool Results Back to AI

This is where the **biggest difference** lies:

#### Anthropic: Single User Message with Array
```python
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "toolu_123",
            "content": "{\"status\": \"success\", \"data\": {...}}"
        }
    ]
})
```

#### OpenAI: Individual Tool Messages
```python
messages.extend([
    {
        "role": "tool",
        "tool_call_id": "call_abc",
        "content": "{\"status\": \"success\", \"data\": {...}}"
    }
])
```

**Key Insight:** Anthropic batches tool results into a single user message, while OpenAI requires each tool result as a separate message with role="tool".

---

## How Synapse Handles This

### The Abstraction Layer

**Provider Interface (`BaseProvider`):**
```python
class BaseProvider(ABC):
    @abstractmethod
    def get_assistant_message(self, response: ProviderResponse) -> dict:
        """Extract the assistant message for conversation history."""
        pass

    @abstractmethod
    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        """Format tool results for this provider."""
        pass
```

### Implementation Details

#### `get_assistant_message()` - Extracting Assistant Messages

**Anthropic Implementation:**
```python
def get_assistant_message(self, response: ProviderResponse) -> dict:
    return {
        "role": "assistant",
        "content": response.raw_response.content  # Already in correct format
    }
```

**OpenAI Implementation:**
```python
def get_assistant_message(self, response: ProviderResponse) -> dict:
    message = response.raw_response.choices[0].message
    assistant_msg = {"role": "assistant"}

    # Add content if present
    if message.content:
        assistant_msg["content"] = message.content

    # Add tool_calls if present
    if message.tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in message.tool_calls
        ]

    return assistant_msg
```

#### `format_tool_results()` - Formatting Tool Responses

**Anthropic:**
```python
def format_tool_results(self, tool_call_id: str, result: str) -> dict:
    return {
        "type": "tool_result",
        "tool_use_id": tool_call_id,
        "content": result
    }
```
*Returns a content block to be added to an array*

**OpenAI:**
```python
def format_tool_results(self, tool_call_id: str, result: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": result
    }
```
*Returns a complete message*

---

## The Magic in `main.py`

### Tool Result Handling (Lines 288-298)

```python
# Collect tool results in provider format
tool_results = []
for tool_call in response.tool_calls:
    result = tool_method(**tool_call.arguments)
    tool_results.append(
        provider.format_tool_results(tool_call.id, str(result))
    )

# Add to message history - provider-specific handling
if agent.provider == "anthropic":
    # Anthropic: Wrap all results in single user message
    messages.append({
        "role": "user",
        "content": tool_results  # List of tool_result blocks
    })
else:
    # OpenAI: Each result is already a complete message
    messages.extend(tool_results)  # Add multiple messages
```

**Why this works:**
- For Anthropic: `tool_results` is a list of `{"type": "tool_result", ...}` objects
- For OpenAI: `tool_results` is a list of `{"role": "tool", ...}` complete messages
- The provider determines the format via `format_tool_results()`

---

## Complete Conversation Example

### User asks: "What time is it?"

**Full message history (Anthropic):**
```python
[
    {"role": "user", "content": "What time is it?"},
    {
        "role": "assistant",
        "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "get_current_time", "input": {}}
        ]
    },
    {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_1", "content": "{...}"}
        ]
    },
    {"role": "assistant", "content": "It's 3:02 PM on Wednesday, October 15, 2025."}
]
```

**Full message history (OpenAI):**
```python
[
    {"role": "user", "content": "What time is it?"},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "get_current_time", "arguments": "{}"}}
        ]
    },
    {"role": "tool", "tool_call_id": "call_1", "content": "{...}"},
    {"role": "assistant", "content": "It's 3:02 PM on Wednesday, October 15, 2025."}
]
```

**Notice:**
- Anthropic: 4 messages (user → assistant → user → assistant)
- OpenAI: 4 messages but different roles (user → assistant → **tool** → assistant)

---

## Why This Architecture Matters

### 1. **Clean Separation of Concerns**
- `main.py` doesn't need to know provider details
- Provider handles its own message formatting
- Adding new providers (Gemini, Claude Opus) is straightforward

### 2. **Consistent Agent Code**
- TodoistAgent doesn't care which provider it uses
- Same tools, same methods, different backends
- Switch providers by changing one line in YAML config

### 3. **Correct Conversation Context**
- Each provider gets messages in the format it expects
- No manual conversion or error-prone if/else throughout codebase
- Provider validates its own message structure

---

## Error Handling Lessons Learned

### Initial Problem
```python
# ❌ This failed for OpenAI
messages.append({
    "role": "assistant",
    "content": response.raw_response.content  # ChatCompletion object has no .content
})
```

### Solution
```python
# ✅ Provider handles extraction
messages.append(provider.get_assistant_message(response))
```

### Why It Failed
- Anthropic's `response.content` is a list of content blocks (ready to use)
- OpenAI's `response` is a `ChatCompletion` object, not a message
- Needed `.choices[0].message` to get the actual message
- Message structure differs (content + tool_calls vs content array)

---

## Future Extensibility

### Adding a New Provider (e.g., Google Gemini)

1. **Create `gemini_provider.py`:**
```python
class GeminiProvider(BaseProvider):
    def get_assistant_message(self, response: ProviderResponse) -> dict:
        # Gemini-specific format
        return {...}

    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        # Gemini-specific format
        return {...}
```

2. **Register in `__init__.py`:**
```python
elif provider_name == "gemini":
    from core.providers.gemini_provider import GeminiProvider
    return GeminiProvider()
```

3. **Create agent config:**
```yaml
# agents/todoist_gemini.yaml
provider: gemini
model: gemini-1.5-pro
```

4. **Done!** No changes needed in `main.py` or agent code.

---

## Key Takeaways

1. **Message history is provider-specific** - No universal format exists
2. **Abstraction is crucial** - Providers handle their own quirks
3. **Tool results have different philosophies:**
   - Anthropic: "Tool results are part of the conversation flow"
   - OpenAI: "Tool results are special messages"
4. **The provider interface shields complexity** - main.py stays clean
5. **Testing both providers validates the abstraction** - If it works for 2 very different APIs, it'll work for others

---

## References

- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- Anthropic Tool Use: https://docs.anthropic.com/claude/docs/tool-use
- Provider Implementation: `core/providers/`
