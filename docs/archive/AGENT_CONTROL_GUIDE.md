# Agent Control & Configuration Guide

## Complete Control Over Your AI Agents

Yes, you have **full control** over all agents! This guide explains how to configure, switch, and customize your AI agents.

---

## Quick Answer to Your Questions

### 1. Do we have control over the OpenAI agent?
**YES - 100% control!** Everything is defined in YAML files that you can edit.

### 2. How do we update or switch agents?
**Edit the YAML file or pass `--agent-name` flag** - No code changes needed!

### 3. What vector stores are being used?
**Currently: LOCAL FILE-BASED KNOWLEDGE SYSTEM**
- The old OpenAI vector store is deprecated (commented out in coder.yaml:44)
- Knowledge is stored in `knowledge/*.md` files
- Accessed via `query_rules` and `update_rules` tools

---

## Available Agents

### Current Agent Configurations

```bash
agents/
├── coder.yaml              # Anthropic/Claude for coding tasks
├── todoist.yaml            # Anthropic/Claude for GTD task management
└── todoist_openai.yaml     # OpenAI/GPT for GTD task management
```

---

## How to Switch Agents

### Method 1: Command Line Flag (Recommended)
```bash
# Use Anthropic Claude for Todoist
python -m core.main chat --agent-name todoist

# Use OpenAI GPT for Todoist
python -m core.main chat --agent-name todoist_openai

# Use Claude for coding
python -m core.main chat --agent-name coder
```

### Method 2: Set as Default
The default agent is "coder" - you can change this in `core/main.py:146`:
```python
def chat(agent_name: str = "coder"):  # Change this default
```

---

## Agent Configuration Structure

### Anatomy of an Agent YAML File

```yaml
# agents/todoist_openai.yaml
name: TodoistAgent                    # Display name
class_name: TodoistAgent              # Python class to instantiate
provider: openai                      # Provider: "anthropic" or "openai"
model: gpt-4o-mini                    # Model identifier

system_prompt: >                      # The agent's instructions
  You are a GTD assistant...
  [entire system prompt here]

tools:                                # Available tools/functions
  - get_current_time
  - create_task
  - list_tasks
  # ... more tools
```

---

## How to Update an Agent

### 1. Change the Model

**Switch to GPT-4o (more powerful but costlier):**
```bash
# Edit agents/todoist_openai.yaml
model: gpt-4o-mini  # Change this line
↓
model: gpt-4o       # To this
```

**Available OpenAI Models:**
- `gpt-4o` - Most capable
- `gpt-4o-mini` - Fast and cheap
- `gpt-4-turbo` - Previous generation
- `gpt-3.5-turbo` - Cheapest option

**Available Anthropic Models:**
- `claude-sonnet-4-20250514` - Current best (Sonnet 4)
- `claude-opus-4-20250514` - Most powerful (when available)
- `claude-3-5-sonnet-20241022` - Previous gen Sonnet 3.5

### 2. Modify the System Prompt

```bash
# Edit the agent YAML file
nano agents/todoist_openai.yaml

# Change the system_prompt section
system_prompt: >
  # Your new instructions here
  You are a specialized assistant that...
```

**Tips for System Prompts:**
- Use YAML's `>` for multi-line strings
- Be specific about behavior
- Include examples of desired output
- Reference tools the agent has access to

### 3. Add or Remove Tools

```yaml
tools:
  - get_current_time
  - create_task
  - list_tasks
  # Add new tool here:
  - my_custom_tool
```

**Note:** The tool must exist as a method in the agent class (`core/agents/todoist.py`)

### 4. Add Custom Parameters

You can add any custom fields to the YAML:
```yaml
provider: openai
model: gpt-4o-mini
max_tokens: 2000          # Custom parameter
temperature: 0.7          # Custom parameter
custom_setting: "value"   # Your own fields
```

These are accessible in the agent via `self.config['custom_setting']`

---

## Knowledge / Vector Store System

### Current Implementation: Local File-Based

**Location:** `knowledge/` directory

**Files:**
1. **`todoist_system.md`** - System design (read-only foundation)
2. **`todoist_rules.md`** - Learned preferences (agent updates this)
3. **`todoist_context.md`** - Deep context about people/places

**How It Works:**
```python
# Agent calls this tool:
query_rules(query="What are the user's label preferences?")

# Reads from knowledge files and returns relevant sections
# Agent can also update:
update_rules(content="New rule: ...", section="preferences")
```

**Advantages:**
- ✅ No external API dependencies
- ✅ Full transparency (readable markdown)
- ✅ Version controlled with git
- ✅ Easy to edit manually
- ✅ No additional costs

### Legacy: OpenAI Vector Store (Deprecated)

**Old approach (commented out in coder.yaml:44):**
```yaml
# vector_store_id: "vs_68edffae626481919dd5804af5c27b4e"
```

This was OpenAI's file_search feature. It's been replaced by the local knowledge system because:
- More control
- No vendor lock-in
- Easier to debug
- Lower costs

---

## Creating a New Agent Configuration

### Example: Create a "Writing Assistant" using OpenAI

1. **Create the YAML file:**
```bash
nano agents/writer_openai.yaml
```

2. **Define the configuration:**
```yaml
name: WriterAgent
class_name: WriterAgent
provider: openai
model: gpt-4o

system_prompt: >
  You are a professional writing assistant.

  Your role:
  - Help with drafting and editing
  - Improve clarity and style
  - Suggest better word choices
  - Check grammar and flow

  Always ask clarifying questions before major edits.

tools:
  - read_file
  - write_file
  - list_files
```

3. **Create the Python class:**
```bash
nano core/agents/writer_openai.py
```

```python
from core.agents.base import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.tools = config.get("tools", [])

    def read_file(self, path: str) -> str:
        """Read a file from disk."""
        # Implementation
        pass

    # ... implement other tools
```

4. **Use it:**
```bash
python -m core.main chat --agent-name writer_openai
```

---

## Switching Between Providers

### Same Agent, Different Provider

You already have this with Todoist:
- `todoist.yaml` → Uses Anthropic Claude
- `todoist_openai.yaml` → Uses OpenAI GPT

**To create more variants:**
```bash
# Copy existing config
cp agents/todoist.yaml agents/todoist_gemini.yaml

# Edit to use different provider
nano agents/todoist_gemini.yaml

# Change:
provider: openai
↓
provider: gemini  # (after implementing GeminiProvider)
```

---

## Cost Optimization Strategies

### 1. Use Cheaper Models for Simple Tasks
```yaml
# For basic tasks
model: gpt-4o-mini        # $0.15 per 1M tokens

# For complex reasoning
model: gpt-4o             # $2.50 per 1M tokens
```

### 2. Reduce Token Usage
```yaml
# Add to your YAML
max_tokens: 1000          # Limit response length
```

### 3. Local Knowledge vs Vector Store
Current file-based system = **FREE**
Old OpenAI vector store = **$0.10/GB/day**

---

## Environment Variables

### Required API Keys

**`.env` file:**
```bash
# For Anthropic agents
ANTHROPIC_API_KEY=sk-ant-api03-...

# For OpenAI agents
OPENAI_API_KEY=sk-proj-...

# For your Todoist agent
TODOIST_API_TOKEN=...
```

**Check which keys are set:**
```bash
grep -E "(ANTHROPIC|OPENAI|TODOIST)" .env
```

---

## Agent Switching Examples

### Scenario 1: Compare Responses

Run the same query with both providers:
```bash
# Test with Claude
echo "Process my inbox" | python -m core.main chat --agent-name todoist

# Test with GPT
echo "Process my inbox" | python -m core.main chat --agent-name todoist_openai
```

### Scenario 2: Cost vs Quality Trade-off

**During development (cheap & fast):**
```yaml
provider: openai
model: gpt-4o-mini
```

**In production (high quality):**
```yaml
provider: anthropic
model: claude-sonnet-4-20250514
```

### Scenario 3: Provider-Specific Features

Some tasks might work better on specific providers:
- **Anthropic**: Long context, analytical tasks
- **OpenAI**: Creative tasks, image generation (future)

---

## Advanced Configuration

### Per-Provider Settings

The `send_message()` method accepts `**kwargs` for provider-specific params:

**OpenAI-specific:**
```python
response = provider.send_message(
    client=client,
    messages=messages,
    system_prompt=prompt,
    model=model,
    tools=tools,
    temperature=0.7,      # OpenAI parameter
    top_p=0.9,           # OpenAI parameter
    frequency_penalty=0  # OpenAI parameter
)
```

**Anthropic-specific:**
```python
response = provider.send_message(
    client=client,
    messages=messages,
    system_prompt=prompt,
    model=model,
    tools=tools,
    max_tokens=4096,     # Anthropic parameter
    temperature=0.7,     # Anthropic parameter
    top_k=40            # Anthropic parameter
)
```

### Adding Provider-Specific Config to YAML

```yaml
provider: openai
model: gpt-4o-mini

# These get passed as **kwargs
provider_params:
  temperature: 0.8
  top_p: 0.95
  presence_penalty: 0.1
```

Then in your code:
```python
kwargs = agent.config.get('provider_params', {})
response = provider.send_message(..., **kwargs)
```

---

## Troubleshooting

### Agent Won't Load
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('agents/todoist_openai.yaml'))"

# Check class exists
python -c "from core.agents.todoist_openai import TodoistAgent"
```

### Wrong Model Being Used
```bash
# Verify agent configuration
python -m core.main chat --agent-name todoist_openai
# Look for the "Model: gpt-4o-mini" line in output
```

### API Key Issues
```bash
# Verify keys are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"
```

---

## Best Practices

### 1. Version Control Your Configs
```bash
git add agents/
git commit -m "Update agent configuration"
```

### 2. Test Before Deploying
```bash
# Test with a simple query first
echo "hello" | python -m core.main chat --agent-name todoist_openai
```

### 3. Document Custom Changes
Add comments to your YAML:
```yaml
# Modified 2025-10-15: Switched to GPT-4o for better reasoning
model: gpt-4o

# Modified 2025-10-14: Added custom instructions for handling dates
system_prompt: >
  # ... custom instructions
```

### 4. Keep Backups
```bash
cp agents/todoist.yaml agents/todoist.yaml.backup
```

### 5. Monitor Costs
```bash
# Check OpenAI usage: https://platform.openai.com/usage
# Check Anthropic usage: https://console.anthropic.com/settings/usage
```

---

## Summary

| Aspect | Answer |
|--------|--------|
| **Control?** | 100% - Edit YAML files |
| **Switch agents?** | `--agent-name` flag or edit YAML |
| **Switch models?** | Change `model:` field in YAML |
| **Switch providers?** | Change `provider:` field in YAML |
| **Vector stores?** | Local file-based (`knowledge/*.md`) |
| **Update system prompt?** | Edit `system_prompt:` in YAML |
| **Add tools?** | Add to `tools:` list in YAML |
| **Cost control?** | Choose cheaper models in YAML |

**You have complete control over everything - no vendor lock-in!**
