# Synapse AI Orchestration Engine

## Project Overview

Synapse is a universal, configuration-driven framework for building multi-platform AI agent workflows. It's designed to be platform-agnostic, allowing you to switch between AI providers (Claude, OpenAI, Gemini, etc.) through simple YAML configuration changes without touching code.

**Core Philosophy:**
- **Platform Agnostic**: AI provider is just a configuration detail
- **Configuration-Driven**: Define agents declaratively via YAML
- **Object-Oriented**: Agent capabilities are Python methods that automatically become AI tools
- **Modular**: Each provider and agent is isolated and independently testable
- **Workflow-First**: Designed for agentic workflows, not just chat interfaces

## Project Structure

```
synapse/
├── agents/                    # Agent configuration files (YAML)
│   ├── coder.yaml            # CoderAgent configuration
│   └── todoist.yaml          # TodoistAgent configuration
├── core/
│   ├── agents/               # Agent class implementations
│   │   ├── base.py          # BaseAgent abstract class
│   │   ├── coder.py         # Coding assistant agent
│   │   └── todoist.py       # GTD/Todoist integration agent
│   ├── providers/            # AI platform integrations
│   │   ├── base_provider.py # Abstract provider interface
│   │   ├── anthropic_provider.py # Claude/Anthropic implementation
│   │   └── __init__.py      # Provider factory
│   ├── knowledge/            # RAG and context management
│   │   ├── base_store.py    # Abstract knowledge store interface
│   │   ├── local_vector_store.py # ChromaDB implementation
│   │   └── __init__.py      # Knowledge store factory
│   ├── agent_loader.py       # Dynamic agent instantiation from YAML
│   ├── schema_generator.py  # Tool schema generation via introspection
│   ├── main.py              # CLI entry point (Typer)
│   └── logger.py            # Logging configuration
├── tests/                    # Test suite
│   ├── test_provider_abstraction.py
│   ├── test_anthropic_provider.py
│   ├── test_main_refactored.py
│   ├── test_knowledge_abstraction.py
│   ├── test_todoist_agent.py
│   └── archived_openai/     # Old OpenAI tests (parked for future)
├── knowledge/                # Knowledge files for TodoistAgent
│   ├── todoist_system.md    # GTD system design (read-only)
│   ├── todoist_rules.md     # Learned preferences
│   └── todoist_context.md   # Deep context about user's system
├── test_todoist_live.py     # Live integration tests with real API
├── requirements.txt          # Python dependencies
└── .env                     # Environment variables (API keys)
```

## Architecture

### Provider Abstraction Layer

All AI platform differences are encapsulated in provider classes:

**BaseProvider Interface:**
- `create_client()` - Initialize AI client
- `send_message()` - Send message and get response
- `format_tool_schemas()` - Generate platform-specific tool definitions
- `format_tool_results()` - Format tool execution results

**Current Providers:**
- ✅ `AnthropicProvider` - Claude (primary provider)
- 🔮 `OpenAIProvider` - Parked for future reintegration

### Agent System

**BaseAgent:**
- Loads configuration from YAML
- Methods automatically discovered as tools via introspection
- Provider-agnostic - works with any provider

**Agent Types:**
1. **CoderAgent** - Software development assistant with file operations, testing, git
2. **TodoistAgent** - GTD task management with full Todoist API integration

### Knowledge Store System

**BaseKnowledgeStore Interface:**
- `initialize()` - Setup with domain-specific config
- `query()` - Search for relevant context
- `sync()` - Index new data
- `clear()` - Reset store
- `get_stats()` - Store statistics

**Implementations:**
- `LocalVectorStore` - ChromaDB for file-based RAG (used by CoderAgent)
- 🔮 Future: EmailStore, TaskStore, DatabaseStore, etc.

## Current Agents

### TodoistAgent

**Purpose:** GTD (Getting Things Done) personal assistant for Todoist

**Key Features:**
- Real-time temporal awareness via `get_current_time()`
- Full Todoist API integration (15 tool methods)
- Automatic startup sequence (gets time + loads rules on launch)
- Natural language date parsing ("tomorrow at 2pm", "every monday at 9am")
- Task creation timestamps (`created_at`) included in all task listings
- Sortable task lists (by creation date or priority, ascending/descending)
- Subtask support (parent_id)
- Task durations
- Section organization
- Comment management

**Tools:**
- `get_current_time()` - Real-time date/time in user timezone
- `create_task()` - Create tasks with all parameters
- `list_tasks()` - Query by project/label/filter with sorting (includes created_at timestamps)
  - Sort options: `created_asc`, `created_desc`, `priority_asc`, `priority_desc`
- `get_task()` - Get detailed task info
- `update_task()` - Modify existing tasks
- `complete_task()` - Mark done
- `reopen_task()` - Uncomplete tasks
- `delete_task()` - Permanently delete
- `move_task()` - Move between projects
- `add_comment()` - Add task comments
- `get_comments()` - Retrieve comments
- `list_projects()` - See all projects
- `list_sections()` - See sections
- `list_labels()` - See all labels
- `query_rules()` - Read knowledge files

**GTD System:**
The agent follows the user's specific GTD methodology:
- Projects as workflow states (#inbox, #processed, #routine, #reminder, #questions, #groceries)
- Contexts as primary organization (@home, @yard, @errand, @computer, @chore, @bec, @waiting, etc.)
- Conservative priority usage (P1-P4, mostly P1)
- Due dates only for hard deadlines
- Learning protocol - asks before storing new rules

**Configuration:** `agents/todoist.yaml`

**Environment:**
- `TODOIST_API_TOKEN` - API key from Todoist
- `TIMEZONE` - User timezone (default: UTC)

### CoderAgent

**Purpose:** Software development assistant

**Tools:** File operations, testing, git operations, etc.

**Configuration:** `agents/coder.yaml`

## CLI Usage

### Main Commands

```bash
# Interactive chat with agent
synapse chat --agent-name <agent>

# Autonomous goal execution
synapse run "goal description" --agent-name <agent> --max-steps 15
```

### Convenient Aliases

```bash
# Quick access to TodoistAgent
synapse-todoist

# Quick access to CoderAgent
synapse-coder
```

These aliases are defined in `~/.zshrc` and handle venv activation automatically.

### Startup Behavior

**TodoistAgent** automatically:
1. Calls `get_current_time()` to know current date/time
2. Calls `query_rules()` to load GTD system knowledge
3. Greets user with temporal awareness

This happens **before** you type anything, so the agent is ready immediately.

### Beautiful CLI Output

Synapse uses **Rich** library for gorgeous terminal output:

**Features:**
- 🎨 **Syntax-highlighted JSON** - Tool results displayed with color-coded JSON
- 📊 **Rich Tables** - Task listings shown in beautiful formatted tables
- 📦 **Panels** - Assistant responses framed in elegant panels
- ⏳ **Animated Spinners** - Smooth "Thinking..." animations instead of static text
- 🎯 **Color-coded Tool Calls** - Easy-to-read tool invocations with argument highlighting

**Task List Display:**
When TodoistAgent returns task lists, they're automatically displayed as Rich tables with:
- Content, Labels, Priority, Due Date, Creation Date columns
- Color-coded priorities and labels
- Automatic truncation (shows first 10 tasks)
- Rounded box styling

**Example Output:**
```
╭─────── 📋 list_tasks - Found 5 task(s) ───────╮
│ Content              Labels   Priority  Due    │
│ Buy groceries        @errand  P2       today   │
│ Write documentation  @work             tomorrow│
│ Call dentist         @phone   P4       friday  │
╰──────────────────────────────────────────────╯
```

All JSON tool results are syntax-highlighted with the Monokai theme for easy reading.

## Development

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_key_here
TODOIST_API_TOKEN=your_token_here

# Optional
TIMEZONE=Australia/Sydney  # For TodoistAgent time awareness
```

### Testing

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_todoist_agent.py -v

# Run live integration tests (creates real Todoist tasks with @test label)
python test_todoist_live.py
```

**Test Philosophy:**
- Unit tests mock all API calls
- Live integration tests (`test_todoist_live.py`) hit real APIs
- All test tasks labeled with `@test` for easy identification
- Live tests automatically clean up after themselves

### Adding a New Agent

1. **Create agent class** in `core/agents/your_agent.py`:
   - Inherit from `BaseAgent`
   - Add methods for agent capabilities (these become tools)
   - Use type hints and docstrings (used for tool schema generation)

2. **Create configuration** in `agents/your_agent.yaml`:
   ```yaml
   name: YourAgent
   class_name: YourAgent
   provider: anthropic
   model: claude-sonnet-4-20250514
   system_prompt: >
     Your agent's instructions...
   tools:
     - tool_method_1
     - tool_method_2
   ```

3. **Add to agent loader** if needed (auto-discovery coming soon)

4. **Create tests** in `tests/test_your_agent.py`

### Adding a New Provider

1. **Create provider class** in `core/providers/your_provider.py`:
   - Inherit from `BaseProvider`
   - Implement all abstract methods
   - Handle provider-specific API details

2. **Register in factory** in `core/providers/__init__.py`

3. **Create tests** in `tests/test_your_provider.py`

4. **Update agent configs** to use new provider (just change `provider: your_provider`)

## Important Patterns & Conventions

### Rich CLI Output (MANDATORY)

**ALL user-facing output MUST use Rich library formatting:**

**DO:**
- ✅ Use `console.print()` instead of `print()`
- ✅ Wrap responses in `Panel()` with appropriate styling
- ✅ Use `console.status()` for loading/thinking states
- ✅ Display tables with `Table()` for structured data
- ✅ Syntax-highlight JSON with `Syntax()`
- ✅ Color-code tool names, arguments, and results
- ✅ Use Rich markup: `[bold]`, `[cyan]`, `[dim]`, etc.

**DON'T:**
- ❌ Use plain `print()` statements
- ❌ Output raw JSON without syntax highlighting
- ❌ Show unformatted lists or data structures
- ❌ Use static "Loading..." text (use spinners instead)

**Example Pattern:**
```python
# Good ✅
console.print(Panel(
    result,
    title="[bold green]Success[/bold green]",
    border_style="green",
    box=box.ROUNDED
))

# Bad ❌
print(f"Success: {result}")
```

**For New Features:**
When adding new CLI output, always use Rich formatting from the start. Check `core/main.py`'s `display_tool_result()` function for examples.

### Testing Requirements (MANDATORY)

**ALL new functionality MUST have comprehensive tests:**

**DO:**
- ✅ Write tests for every new function, method, or feature
- ✅ Create unit tests that mock external dependencies (API calls, file I/O)
- ✅ Test both success and error cases
- ✅ Test edge cases (empty inputs, long inputs, null values, etc.)
- ✅ Use descriptive test names that explain what is being tested
- ✅ Mock external dependencies with `unittest.mock` or `pytest-mock`
- ✅ Verify behavior, not implementation details
- ✅ Run tests before committing (`pytest tests/ -v`)

**DON'T:**
- ❌ Skip tests because functionality "seems simple"
- ❌ Write tests that depend on external services (except in live integration tests)
- ❌ Test implementation details that might change
- ❌ Commit code without running tests first
- ❌ Leave failing tests in the codebase

**Test Organization:**
- **Unit Tests**: `tests/test_*.py` - Mock all external dependencies
- **Integration Tests**: `test_*_live.py` (root level) - Test with real APIs
- **Test Naming**: `test_<what_it_does>` (e.g., `test_displays_task_list_as_table`)

**Example Test Structure:**
```python
import pytest
from unittest.mock import Mock, patch

class TestYourFeature:
    """Test suite for your feature."""

    @patch('module.external_dependency')
    def test_success_case(self, mock_dependency):
        """Test that feature works correctly with valid input."""
        # Arrange
        mock_dependency.return_value = "expected"

        # Act
        result = your_function("input")

        # Assert
        assert result == "expected"
        mock_dependency.assert_called_once_with("input")

    @patch('module.external_dependency')
    def test_error_case(self, mock_dependency):
        """Test that feature handles errors gracefully."""
        # Arrange
        mock_dependency.side_effect = Exception("API error")

        # Act & Assert
        with pytest.raises(Exception):
            your_function("input")
```

**When to Write Tests:**
1. **Before committing** - Every commit should include tests for new functionality
2. **After fixing bugs** - Add regression tests to prevent the bug from returning
3. **When refactoring** - Ensure existing tests still pass
4. **For CLI output** - Test Rich formatting, table creation, panel display
5. **For API integrations** - Test response parsing, error handling, data transformation

**Testing Checklist (see Development Workflow below)**

### Provider Abstraction

**DO:**
- ✅ Keep all provider-specific code in provider classes
- ✅ Use `BaseProvider` interface methods
- ✅ Return standardized `ProviderResponse` and `ToolCall` objects

**DON'T:**
- ❌ Add provider-specific code to agents
- ❌ Import provider SDKs outside of provider classes
- ❌ Couple agent logic to any specific platform

### Tool Method Design

```python
def tool_method(self, param: str, optional: int = None) -> str:
    """
    Brief description of what this tool does.

    Args:
        param: Description of param
        optional: Description of optional param
    """
    try:
        # Implementation
        result = do_something()
        return self._success("Success message", data={"key": "value"})
    except Exception as e:
        return self._error("ErrorType", f"Error message: {str(e)}")
```

**Key Points:**
- Return JSON strings (use `_success()` and `_error()` helpers)
- Always include docstrings (used for tool schema generation)
- Use type hints (used for parameter validation)
- Handle errors gracefully

### Label Handling (TodoistAgent)

Labels can be passed as strings or lists - both work:
```python
labels="test"        # Auto-converts to ["test"]
labels=["test"]      # Already correct format
```

The agent automatically:
- Converts strings to lists
- Strips `@` prefix (user can use `@home` or `home`)

### Testing with Real APIs

When creating live integration tests:
- Use `@test` label on all test items
- Clean up after yourself (delete test items)
- Add small delays (`time.sleep(2)`) between operations for API sync
- Handle both success and error cases

## Known Issues & Quirks

### Todoist API

1. **ResultsPaginator:** The Python SDK returns `ResultsPaginator` objects, not lists
   - Solution: Use `next(iter(paginator))` to get the actual list
   - Applied in: `_get_projects()`, `_get_sections()`, `_get_labels()`, `_get_tasks_list()`

2. **Datetime Serialization:** Task/Comment objects contain datetime objects
   - Solution: Convert to strings with `str(obj.created_at)` before JSON serialization
   - Applied in: `get_task()`, `get_comments()`

3. **Move Task Response:** `move_task()` returns dict, not Task object
   - Solution: Fetch the task again after moving to get updated object
   - Applied in: `move_task()`

### Chat Behavior

- Long first responses are normal - the AI is processing the extensive system prompt
- TodoistAgent startup sequence runs automatically, no user input needed
- If chat seems stuck, it's likely waiting for API response (be patient)

## Vision & Roadmap

See `VISION.md` and `REFACTORING_ROADMAP.md` for detailed information.

**Current Status:**
- ✅ Multi-provider architecture complete
- ✅ Claude/Anthropic provider fully functional
- ✅ Pluggable knowledge store system
- ✅ TodoistAgent with comprehensive API integration
- ✅ Configuration-driven agent system

**Future Plans:**
- 🔮 OpenAI provider reintegration
- 🔮 Additional agents (EmailAgent, DocumentAgent, etc.)
- 🔮 Additional knowledge stores (EmailStore, TaskStore, etc.)
- 🔮 More workflow automation

## Git Workflow

**Commit Style:** Conventional commits with emoji
```
feat(scope): Description
fix(scope): Description
refactor(scope): Description
test(scope): Description
docs(scope): Description
```

**Important:**
- All commits include Claude Code attribution
- Tests must pass before committing
- Keep commits focused and atomic
- Push to `main` branch
- **ALWAYS commit and push after completing a feature or fix**

**Testing Checklist:**
When adding new functionality, ensure tests are comprehensive:
1. ✅ Create test file `tests/test_<feature>.py` if it doesn't exist
2. ✅ Write tests for all new functions/methods
3. ✅ Test success cases with valid inputs
4. ✅ Test error cases with invalid inputs
5. ✅ Test edge cases (empty, null, very long, etc.)
6. ✅ Mock all external dependencies (APIs, file I/O, databases)
7. ✅ Run tests locally: `pytest tests/test_<feature>.py -v`
8. ✅ Verify all tests pass before committing

**Commit Checklist (for Claude Code):**
1. ✅ Run all relevant tests (`pytest tests/ -v`)
2. ✅ Ensure ALL tests pass (no failures)
3. ✅ Update documentation (claude.md)
4. ✅ `git add -A`
5. ✅ `git commit` with proper message format
6. ✅ `git push`

This ensures all work is tested, documented, and saved to the remote repository.

## Resources

- **Documentation:** See `README.md`, `VISION.md`, `REFACTORING_ROADMAP.md`
- **Todoist API:** https://developer.todoist.com/rest/v2/
- **Anthropic API:** https://docs.anthropic.com/
- **Main Branch:** All development on `main`

## Quick Reference

### Start TodoistAgent
```bash
synapse-todoist
```

### Run Tests
```bash
pytest tests/ -v
python test_todoist_live.py
```

### Create Task (in chat)
```
Create a task "Buy groceries" in #processed with @errand label due tomorrow at 2pm
```

### List Tasks (in chat)
```
Show me all tasks with @test label
```

### Debug Agent
Check `core/main.py` for CLI logic and `core/agents/todoist.py` for TodoistAgent implementation.

---

**Last Updated:** 2025-10-15
**Current Model:** claude-sonnet-4-20250514
**Python Version:** 3.13.7
