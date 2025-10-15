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

**Active Development**: Multi-provider refactoring in progress

- ✅ Core agent architecture established
- ✅ Dynamic tool schema generation working
- 🚧 **In Progress**: Provider abstraction layer for multi-platform support
- 🚧 **In Progress**: Claude/Anthropic integration (primary focus)
- 🔮 **Planned**: OpenAI provider (parked for future implementation)
- 🔮 **Planned**: Additional workflow agents (email, tasks, etc.)

## Quick Start (Coming Soon)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your agent
nano agents/my_agent.yaml

# Run your agent
python -m core.main chat
```

## Example Use Cases

- **Code Development**: Autonomous coding agent that reads, writes, tests, and commits code
- **Email Management**: Agent that triages, labels, and responds to emails based on your rules
- **Task Orchestration**: Integration with Todoist/task managers for intelligent task creation and prioritization
- **Document Processing**: Bulk analysis, summarization, or transformation of documents
- **Custom Workflows**: Any repetitive task that benefits from AI reasoning + programmatic actions

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
