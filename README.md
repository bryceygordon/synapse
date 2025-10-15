# Synapse AI Orchestration Engine

**A universal, configuration-driven framework for building multi-platform AI agent workflows**

## Vision

Synapse is designed to be a foundation for creating specialized AI agents that can work across any AI platform (Claude, OpenAI, Gemini, etc.) to automate diverse workflows. Whether you need a coding assistant, email organizer, task manager integration, or any custom automation, Synapse provides the architecture to build it easily.

## Core Philosophy

1. **Platform Agnostic**: Switch between AI providers through simple configuration changes
2. **Configuration-Driven**: Define agents declaratively via YAML - no code changes needed
3. **Object-Oriented**: Agent capabilities are Python methods that automatically become AI tools
4. **Modular**: Each provider implementation is isolated - adding new platforms doesn't affect existing ones
5. **Workflow-First**: Designed for building agentic workflows, not just chat interfaces

## Architecture

### Key Components

- **Agent Classes** (`core/agents/`): Define capabilities through methods (e.g., `read_file`, `send_email`, `create_task`)
- **Provider Layer** (`core/providers/`): Abstracts AI platform differences (API formats, tool schemas, context management)
- **Agent Loader** (`core/agent_loader.py`): Dynamically instantiates agents from YAML configurations
- **Schema Generator** (`core/schema_generator.py`): Converts Python methods to platform-specific tool schemas via introspection
- **Main Loop** (`core/main.py`): Orchestrates the conversation cycle and tool execution

### How It Works

1. Define an agent in YAML (specify provider, model, tools, system prompt)
2. Create an agent class with methods for your workflow (email reading, file operations, API calls, etc.)
3. Run Synapse - it automatically:
   - Loads your agent configuration
   - Connects to the specified AI provider
   - Exposes your methods as tools to the AI
   - Handles the conversation loop and tool execution

## Current Status

**Multi-Platform Support Complete** ✨

- ✅ Provider abstraction layer implemented
- ✅ Claude/Anthropic provider fully functional
- ✅ OpenAI/GPT provider fully functional
- ✅ Local file-based knowledge system (no vector DB required)
- ✅ Configuration-driven architecture working
- ✅ End-to-end testing verified
- ✅ Multiple agent variants (Todoist GTD with Claude & GPT, Coder)
- 🔮 **Planned**: Additional providers (Gemini, etc.)
- 🔮 **Planned**: More workflow agents

## Quick Start

```bash
# Clone the repository
git clone https://github.com/bryceygordon/synapse.git
cd synapse

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set up API keys in .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "TODOIST_API_TOKEN=your-token-here" >> .env  # If using Todoist agent

# Easy launcher (recommended)
./synapse todoist          # Todoist GTD with Claude
./synapse todoist-openai   # Todoist GTD with GPT-4o-mini
./synapse coder            # Coder agent with Claude

# Or use Python directly
python -m core.main chat --agent-name todoist
python -m core.main run "Create a new Python module" --agent-name coder
```

### Configuration

Edit agent YAML files to customize behavior:

```yaml
# agents/todoist_openai.yaml
name: TodoistAgent
provider: openai              # 'anthropic' or 'openai'
model: gpt-4o-mini           # or 'gpt-4o', 'claude-sonnet-4-20250514', etc.

system_prompt: >
  Your agent instructions...

tools:
  - get_current_time
  - create_task
  - list_tasks
  # ... more tools
```

**Available Agents:**
- `todoist` - GTD task manager with Claude Sonnet 4
- `todoist-openai` - GTD task manager with GPT-4o-mini (⭐ recommended for cost)
- `coder` - Software development agent with Claude Sonnet 4

## Example Use Cases

- **GTD Task Management**: Intelligent Todoist integration following GTD methodology with learning capabilities
- **Code Development**: Autonomous coding agent that reads, writes, tests, and commits code
- **Email Management**: Agent that triages, labels, and responds to emails based on your rules
- **Document Processing**: Bulk analysis, summarization, or transformation of documents
- **Custom Workflows**: Any repetitive task that benefits from AI reasoning + programmatic actions

**Current Working Agents:**
- ✅ **TodoistAgent**: Full GTD implementation with natural language task creation, context awareness, and preference learning
- ✅ **CoderAgent**: Autonomous software development with file operations and git integration

## Project Structure

```
synapse/
├── agents/              # Agent configuration files (YAML)
├── core/
│   ├── agents/          # Agent class implementations
│   ├── providers/       # AI platform integrations
│   ├── knowledge/       # RAG and context management
│   ├── agent_loader.py  # Dynamic agent instantiation
│   ├── schema_generator.py  # Tool schema generation
│   └── main.py          # CLI and main loop
└── tests/               # Test suite
```

## Philosophy: Why Synapse?

Most AI wrapper tools lock you into a specific platform or require significant code changes to switch providers. Synapse inverts this - your agent logic (the methods) remains constant, and the AI platform is just a configuration detail. This means:

- Build once, run on any AI platform
- Compare providers easily for your specific use case
- Future-proof against API changes or new platforms
- Focus on workflow logic, not API integration

## Contributing

This is currently a personal tool under active development. Documentation and contribution guidelines will be added as the architecture stabilizes.

## License

[To be determined]
