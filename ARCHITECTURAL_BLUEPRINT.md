# Architectural Blueprint

**See VISION.md for the core purpose and philosophy**

This blueprint outlines the technical structure of the Synapse engine, based on an object-oriented, configuration-driven pattern that supports multiple AI providers and workflow types.

## Design Principles

1. **Provider Agnostic**: AI platform is a configuration detail, not architectural constraint
2. **Workflow Neutral**: Architecture supports any domain (code, email, tasks, documents, etc.)
3. **Method-as-Tool**: Agent capabilities are just Python methods with introspection
4. **Configuration-Driven**: YAML files define agent behavior, no code changes needed

---

## Core Components

### 1. The Core Engine (CLI Application)
**Location**: `core/main.py`
**Technology**: Python with `Typer` library

**Responsibilities**:
- Manages the main application loop (chat or autonomous run mode)
- Uses `AgentLoader` to instantiate configured agents
- Uses `ProviderFactory` to get the correct AI provider
- Mediates conversation between AI and agent tools
- Handles tool invocation via dynamic method calling
- Manages errors and logging

**Key Feature**: Provider-agnostic - works with any provider implementing `BaseProvider` interface

---

### 2. Provider Abstraction Layer
**Location**: `core/providers/`

**Structure**:
```
providers/
├── __init__.py              # Provider factory
├── base_provider.py         # Abstract interface
├── anthropic_provider.py    # Claude/Anthropic implementation
└── openai_provider.py       # OpenAI implementation (future)
```

**Purpose**: Encapsulates ALL platform-specific differences:
- API client creation
- Message sending/receiving
- Tool schema format differences
- Response parsing
- Tool call extraction
- Context management strategies

**Key Feature**: Adding a new provider requires NO changes to agent code or main loop

---

### 3. Agent Class Hierarchy
**Location**: `core/agents/`

**Structure**:
```
agents/
├── __init__.py
├── base.py          # BaseAgent abstract class
├── coder.py         # CoderAgent for development workflows
├── email.py         # EmailAgent for email management (future)
├── task.py          # TaskAgent for task orchestration (future)
└── [custom].py      # User-defined agents
```

**BaseAgent Responsibilities**:
- Initialize from configuration dictionary
- Store common attributes (name, model, provider, system_prompt, tools)
- Handle provider and knowledge store references
- Provide standardized response formatting

**Specialized Agent Responsibilities**:
- Define domain-specific methods (e.g., `read_file`, `send_email`, `create_task`)
- Each method becomes an AI tool automatically
- Methods return structured JSON for machine reasoning
- Implement domain-specific error handling

**Key Feature**: Methods are provider-agnostic - same code works with Claude, OpenAI, Gemini, etc.

---

### 4. Configuration System
**Location**: `agents/*.yaml`

**Example Structure**:
```yaml
name: CoderAgent
class_name: CoderAgent
provider: anthropic              # Which AI platform to use
model: claude-sonnet-4.5         # Provider-specific model
system_prompt: |
  [Agent instructions...]
local_knowledge_path: ./knowledge  # Optional RAG directory
tools:                           # Which methods to expose
  - read_file
  - write_file
  - run_tests
  - git_commit
```

**Purpose**: Blueprint for agent instantiation - defines behavior without code

**Key Feature**: Switching providers or models is a one-line config change

---

### 5. Agent Loader & Dynamic Instantiation
**Location**: `core/agent_loader.py`

**Workflow**:
1. Read agent's `.yaml` configuration
2. Dynamically import the class specified by `class_name`
3. Instantiate the class, passing YAML attributes to constructor
4. Return fully-configured agent instance

**Key Feature**: No hardcoded agent registry - any class can be loaded by name

---

### 6. Schema Generator & Introspection
**Location**: `core/schema_generator.py`

**Workflow**:
1. Receive agent instance and provider type
2. Introspect agent methods listed in `tools` config
3. Extract docstrings and type hints
4. Generate provider-specific tool schemas:
   - **OpenAI format**: `{"type": "function", "name": "...", "parameters": {...}}`
   - **Claude format**: `{"name": "...", "description": "...", "input_schema": {...}}`

**Key Feature**: Methods automatically become tools - no manual schema writing

---

### 7. Method Invoker (Dynamic Tool Execution)
**Location**: `core/main.py` (within conversation loop)

**Workflow**:
1. Provider returns tool calls from AI response
2. For each tool call:
   - Use `getattr(agent, function_name)` to get the method
   - Parse arguments from provider response
   - Securely invoke method with arguments
   - Capture result
3. Format results for provider
4. Send back to AI for next reasoning step

**Key Feature**: Secure, sandboxed execution with workspace validation

---

### 8. Knowledge Management
**Location**: `core/knowledge/`

**Current Implementation**: Local ChromaDB vector store

**Responsibilities**:
- Index directories of files (codebases, documents, etc.)
- Semantic search for relevant context
- Inject context into AI prompts
- Provider-agnostic (not tied to OpenAI vector stores)

**Future**: Pluggable knowledge sources (databases, APIs, web scraping)

**Key Feature**: Privacy-first, local RAG without vendor lock-in

---

## Data Flow

### Chat Mode:
```
User Input
  → Main Loop
  → Provider.send_message()
  → AI Provider API
  → Provider.parse_response()
  → Extract Tool Calls
  → Invoke Agent Methods
  → Format Tool Results
  → Provider.send_message() [with results]
  → AI Provider API
  → Final Response
  → Display to User
```

### Run Mode (Autonomous):
```
Goal Statement
  → Main Loop (max_steps iteration)
  → [Same as Chat Mode for each step]
  → Loop until: goal achieved OR max steps OR commit requested
  → Final Report
```

---

## Key Design Patterns

### 1. Strategy Pattern (Providers)
Different AI platforms = different strategies for same interface

### 2. Factory Pattern (Provider Loading)
`get_provider(name)` returns correct provider implementation

### 3. Introspection/Reflection (Schema Generation)
Methods discover their own schemas via docstrings and type hints

### 4. Dynamic Invocation (Tool Execution)
`getattr()` allows AI to call methods by name without hardcoded dispatch

### 5. Configuration Over Convention
Behavior defined in YAML, not code structure

---

## Extensibility Points

### Adding a New Provider:
1. Create `core/providers/new_provider.py`
2. Implement `BaseProvider` interface
3. Add schema formatter if needed
4. Register in provider factory
5. Done - all agents now support new provider

### Adding a New Agent Type:
1. Create `core/agents/new_agent.py` extending `BaseAgent`
2. Implement domain-specific methods
3. Create `agents/new_agent.yaml` config
4. Done - agent works with all providers

### Adding a New Tool to Existing Agent:
1. Add method to agent class with docstring and type hints
2. Add method name to `tools` list in YAML
3. Done - automatically becomes available to AI

---

## Security Considerations

- **Workspace Validation**: All file operations validated against workspace boundaries
- **Sandboxed Execution**: Shell commands run through secure executor
- **No Code Injection**: Tool arguments are typed and validated
- **API Key Management**: Environment variables, never in configs
- **Principle of Least Privilege**: Agents only get tools they need

---

## Testing Strategy

- **Unit Tests**: Each component tested in isolation
- **Integration Tests**: Provider + Agent + Main Loop tested together
- **Mocked Providers**: Fast tests without API calls
- **E2E Tests**: Real workflows with real agent methods (mocked AI responses)

---

## Future Architectural Considerations

- **Streaming Responses**: For long-running operations
- **Multi-Agent Collaboration**: Agents calling other agents
- **Workflow Orchestration**: DAG-based task dependencies
- **Plugin System**: User-contributed agents and providers
- **Web Interface**: Optional GUI for non-technical users

---

**This architecture prioritizes modularity, extensibility, and provider independence. Every decision should support the goal of running ANY workflow on ANY AI platform.**
