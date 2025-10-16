# Multi-Provider Refactoring Roadmap

**Goal**: Transform Synapse from OpenAI-specific to a universal multi-platform AI orchestration engine, with Claude/Anthropic as the primary initial provider.

**Strategy**: Build provider abstraction layer, implement Claude integration, park OpenAI for future reintegration, ensure each provider is completely isolated.

---

## Phase 1: Provider Abstraction Layer

**Goal**: Create the foundational architecture that allows multiple AI providers to coexist independently.

### Tasks

1. **Create provider module structure**
   - Create `core/providers/__init__.py`
   - Create `core/providers/base_provider.py` with abstract base class

2. **Define provider interface**
   ```python
   class BaseProvider(ABC):
       @abstractmethod
       def create_client(self) -> Any

       @abstractmethod
       def send_message(self, payload: dict) -> dict

       @abstractmethod
       def parse_response(self, response: Any) -> dict

       @abstractmethod
       def extract_tool_calls(self, response_dict: dict) -> list[ToolCall]

       @abstractmethod
       def format_tool_results(self, tool_outputs: list) -> Any

       @abstractmethod
       def supports_streaming(self) -> bool
   ```

3. **Create provider response/tool call data classes**
   - Standardized `ToolCall` dataclass
   - Standardized `ProviderResponse` dataclass
   - Shared across all providers

4. **Implement provider factory**
   - `get_provider(name: str) -> BaseProvider`
   - Raises clear error for unsupported providers

### Testing

**File**: `tests/test_provider_abstraction.py`

- Test provider factory returns correct type
- Test base class enforces abstract methods
- Test data classes serialize/deserialize correctly
- Verify provider not found raises appropriate error

### Success Criteria

- [ ] All tests pass
- [ ] Provider abstraction is documented with docstrings
- [ ] Factory pattern works for loading providers by name

### Commit Message
```
feat(providers): Add provider abstraction layer for multi-platform support

- Create BaseProvider abstract interface
- Add ToolCall and ProviderResponse data classes
- Implement provider factory pattern
- Add comprehensive tests for abstraction layer

This establishes the foundation for supporting multiple AI platforms
(Claude, OpenAI, Gemini, etc.) without coupling agent logic to any
specific provider.
```

---

## Phase 2: Anthropic/Claude Provider Implementation

**Goal**: Implement complete Claude integration as the primary provider.

### Tasks

1. **Create Anthropic provider class**
   - Create `core/providers/anthropic_provider.py`
   - Implement all BaseProvider abstract methods
   - Use Anthropic Messages API

2. **Implement Claude-specific features**
   - Tool use format: `{"name": "...", "input": {...}}`
   - Message history management (no stateful response IDs)
   - System prompt handling
   - Token counting and context management

3. **Add Claude tool schema formatter**
   - Update `core/schema_generator.py`
   - Add `generate_anthropic_schema(agent)` function
   - Claude format: `{"name": "...", "description": "...", "input_schema": {...}}`

4. **Add dependencies**
   - Add `anthropic` to requirements.txt
   - Add `tiktoken` for token counting (Anthropic uses same tokenizer as OpenAI)

### Testing

**File**: `tests/test_anthropic_provider.py`

- Test client creation with/without API key
- Test message sending with mock responses
- Test tool call extraction from Claude responses
- Test tool result formatting
- Test schema generation for Claude format
- Mock actual API calls (use fixtures)

### Success Criteria

- [ ] All tests pass
- [ ] Can create Claude client
- [ ] Can send/receive messages (mocked)
- [ ] Tool calls correctly parsed
- [ ] Schemas match Claude's expected format

### Commit Message
```
feat(providers): Implement Anthropic/Claude provider

- Add AnthropicProvider with full Messages API integration
- Implement Claude-specific tool use format
- Add message history management
- Generate Claude-compatible tool schemas
- Add comprehensive test suite with mocked API responses

Claude is now the primary AI provider for Synapse.
```

---

## Phase 3: Refactor Main Loop for Provider Abstraction

**Goal**: Update main.py to use provider abstraction instead of hardcoded OpenAI.

### Tasks

1. **Update BaseAgent configuration**
   - Add `provider` field to `core/agents/base.py`
   - Add `local_knowledge_path` field (for future RAG)
   - Update initialization logic

2. **Refactor main.py chat command**
   - Replace OpenAI client with `get_provider(agent.provider)`
   - Remove OpenAI-specific imports
   - Use provider methods instead of direct API calls
   - Update conversation loop to be provider-agnostic

3. **Refactor main.py run command**
   - Same changes as chat command
   - Maintain autonomous execution logic
   - Keep max_steps and goal-oriented behavior

4. **Update agent configuration**
   - Modify `agents/coder.yaml` to include `provider: anthropic`
   - Update model to `claude-sonnet-4.5`
   - Remove OpenAI-specific fields (vector_store_id for now)

5. **Handle backward compatibility**
   - Default to `anthropic` if provider not specified
   - Log warnings for deprecated config fields

### Testing

**File**: `tests/test_main_loop.py`

- Test chat loop initialization with Claude provider
- Test run loop initialization with Claude provider
- Test tool execution flow (end-to-end with mocked provider)
- Test conversation state management
- Test error handling (provider errors, tool errors)

### Success Criteria

- [ ] All tests pass
- [ ] Can start chat with Claude provider
- [ ] Can run autonomous goals with Claude provider
- [ ] Tool execution works end-to-end
- [ ] No OpenAI-specific code remains in main loop

### Commit Message
```
refactor(main): Decouple main loop from OpenAI, use provider abstraction

- Update main.py to use provider factory instead of OpenAI client
- Add provider field to BaseAgent configuration
- Refactor chat and run commands to be provider-agnostic
- Update coder.yaml to use Anthropic/Claude provider
- Add tests for refactored main loop

The main conversation loop now works with any provider implementing
the BaseProvider interface. OpenAI-specific code has been removed.
```

---

## Phase 4: Pluggable Knowledge Management System

**Goal**: Create a universal knowledge store abstraction that supports ANY domain (code, email, tasks, documents), not just file-based RAG.

**Philosophy**: Different agent types need different knowledge sources. CoderAgent needs codebase context, EmailAgent needs email history, TaskAgent needs task context. Make knowledge backends pluggable from day one.

### Tasks

1. **Create knowledge abstraction layer**
   - Create `core/knowledge/__init__.py` with factory pattern
   - Create `core/knowledge/base_store.py` with abstract interface

2. **Define abstract knowledge interface**
   ```python
   class BaseKnowledgeStore(ABC):
       @abstractmethod
       def initialize(self, config: dict) -> None
           """Initialize the knowledge store with domain-specific config."""

       @abstractmethod
       def query(self, query: str, k: int = 5) -> list[str]
           """Search for relevant context given a query."""

       @abstractmethod
       def sync(self, source: Any) -> None
           """Sync/index new data. Source type varies by implementation."""

       @abstractmethod
       def clear(self) -> None
           """Clear all stored knowledge."""

       @abstractmethod
       def get_stats(self) -> dict
           """Return statistics about the knowledge store."""
   ```

3. **Implement LocalVectorStore (ChromaDB)**
   - Create `core/knowledge/local_vector_store.py`
   - Implement BaseKnowledgeStore for file-based RAG
   - `sync(source: str)` accepts directory path
   - Index files with ChromaDB and sentence-transformers
   - This serves CoderAgent and DocumentAgent use cases

4. **Implement knowledge store factory**
   ```python
   def get_knowledge_store(store_type: str, config: dict) -> BaseKnowledgeStore:
       """Factory to create appropriate knowledge store."""
       if store_type == "local_vector_store":
           return LocalVectorStore(config)
       elif store_type == "email_store":  # Future
           return EmailStore(config)
       elif store_type == "task_store":  # Future
           return TaskStore(config)
       else:
           raise ValueError(f"Unknown knowledge store type: {store_type}")
   ```

5. **Update BaseAgent for pluggable knowledge**
   - Add `knowledge_store` attribute (optional)
   - Initialize from config: `knowledge_store: {type: ..., config: {...}}`
   - Agent classes remain agnostic to knowledge backend type

6. **Integrate with providers**
   - Providers check if `agent.knowledge_store` exists
   - If present, call `agent.knowledge_store.query(prompt)` before API call
   - Inject retrieved context into system prompt or messages
   - Provider doesn't care what type of knowledge store it is

7. **Add knowledge management CLI commands**
   - `python -m core.main knowledge sync --agent=coder --source=./`
   - `python -m core.main knowledge search --agent=coder "query"`
   - `python -m core.main knowledge stats --agent=coder`
   - Commands work with any knowledge store type

8. **Add dependencies**
   - Add `chromadb` to requirements.txt
   - Add `sentence-transformers` for embeddings

9. **Document extension pattern**
   - Add `docs/ADDING_KNOWLEDGE_STORES.md`
   - Show how to create EmailStore or TaskStore in future
   - Emphasize: adding new store type doesn't affect existing agents

### Configuration Examples

**CoderAgent with local vector store:**
```yaml
name: CoderAgent
class_name: CoderAgent
provider: anthropic
model: claude-sonnet-4.5
knowledge_store:
  type: local_vector_store
  config:
    path: ./knowledge
    collection_name: codebase
    chunk_size: 1000
tools:
  - read_file
  - write_file
```

**Future EmailAgent with email store:**
```yaml
name: EmailAgent
class_name: EmailAgent
provider: anthropic
model: claude-sonnet-4.5
knowledge_store:
  type: email_store
  config:
    email: user@example.com
    imap_server: imap.gmail.com
    max_messages: 100
tools:
  - read_inbox
  - send_email
```

**Agent with no knowledge store:**
```yaml
name: SimpleAgent
class_name: SimpleAgent
provider: anthropic
model: claude-sonnet-4.5
# No knowledge_store field - perfectly valid
tools:
  - do_something
```

### Testing

**File**: `tests/test_knowledge_abstraction.py`

- Test BaseKnowledgeStore enforces abstract methods
- Test knowledge store factory
- Test factory raises error for unknown type
- Test agent initialization with/without knowledge store

**File**: `tests/test_local_vector_store.py`

- Test LocalVectorStore initialization
- Test directory syncing/indexing
- Test search retrieval (relevance)
- Test clear operation
- Test stats generation
- Test with different file types (.py, .md, .txt)

**File**: `tests/test_knowledge_integration.py`

- Test provider queries knowledge store when present
- Test provider skips knowledge query when absent
- Test context injection into prompts
- Mock knowledge store responses

### Success Criteria

- [ ] All tests pass
- [ ] BaseKnowledgeStore abstraction is clean and extensible
- [ ] LocalVectorStore works for file-based indexing
- [ ] Providers integrate with knowledge stores generically
- [ ] Agent config supports knowledge_store field (optional)
- [ ] CLI commands work with any knowledge store type
- [ ] Documentation shows how to add new store types
- [ ] No hardcoded assumptions about ChromaDB in provider/agent code

### Commit Message
```
feat(knowledge): Add pluggable knowledge store system for multi-domain support

- Create BaseKnowledgeStore abstract interface for universal knowledge access
- Implement LocalVectorStore with ChromaDB for file-based RAG
- Add knowledge store factory pattern for extensibility
- Integrate with providers via generic query interface
- Add CLI commands for knowledge management
- Support optional knowledge stores in agent configs
- Add comprehensive test suite and extension documentation

Knowledge management is now domain-agnostic. CoderAgent uses local vector
stores for codebases, future EmailAgent can use email stores, TaskAgent
can use task stores - all through the same abstraction. Adding new
knowledge backends requires zero changes to existing code.
```

### Future Knowledge Store Implementations

These are NOT implemented now, but the architecture supports them:

**EmailStore** (`core/knowledge/email_store.py`):
- `sync(source: ImapConfig)` - Connect to email server
- `query(query: str)` - Search email history by semantic similarity
- Used by EmailAgent for email triage/response

**TaskStore** (`core/knowledge/task_store.py`):
- `sync(source: TodoistAPI)` - Fetch tasks from Todoist
- `query(query: str)` - Find related tasks by context
- Used by TaskAgent for task management

**DatabaseStore** (`core/knowledge/database_store.py`):
- `sync(source: ConnectionString)` - Index database schema
- `query(query: str)` - Find relevant tables/columns
- Used by DataAgent for SQL generation

**WebStore** (`core/knowledge/web_store.py`):
- `sync(source: list[URL])` - Crawl and index web pages
- `query(query: str)` - Search indexed web content
- Used by ResearchAgent for web research

---

## Phase 5: End-to-End Testing & Documentation

**Goal**: Verify complete workflow works and document the new architecture.

**PREREQUISITE**: Before starting this phase, obtain an Anthropic API key with usage-based billing:
1. Go to https://console.anthropic.com/
2. Create account and add payment method
3. Generate API key
4. Set environment variable: `export ANTHROPIC_API_KEY=your-key-here`
5. Estimated cost for testing: $5-20 total

### Tasks

1. **Archive old tests**
   - Move current OpenAI-specific tests to `tests/archived_openai/` (ALREADY DONE in Phase 1)

2. **Create end-to-end test**
   - Create `tests/test_e2e_claude_coder.py`
   - Test full cycle: user input → tool call → tool execution → response
   - Use real CoderAgent methods
   - Mock Anthropic API responses

3. **Manual testing checklist**
   - [ ] `python -m core.main chat` starts successfully
   - [ ] Can have conversation with Claude
   - [ ] Tools are invoked correctly
   - [ ] Tool results are parsed and used
   - [ ] `python -m core.main run "simple goal"` works
   - [ ] Knowledge store integration works (if enabled)

4. **Update documentation**
   - Update ROADMAP.md to reflect completion
   - Update ARCHITECTURAL_BLUEPRINT.md for provider layer
   - Add CLAUDE_SETUP.md with API key setup instructions

5. **Create example agent configs**
   - `agents/examples/coder_claude.yaml` - Fully configured example
   - `agents/examples/minimal.yaml` - Minimal working example
   - Add comments explaining each field

### Testing

**File**: `tests/test_e2e_claude_coder.py`

- Test complete conversation flow
- Test tool execution with real agent methods
- Test error recovery
- Test multi-turn conversations
- Test autonomous run mode

### Success Criteria

- [ ] All tests pass (new test suite)
- [ ] Manual testing checklist complete
- [ ] Documentation updated and accurate
- [ ] Example configs work out-of-the-box

### Commit Message
```
test(e2e): Add end-to-end tests and complete documentation

- Add comprehensive e2e tests for Claude CoderAgent workflow
- Archive old OpenAI-specific tests for future use
- Update all documentation to reflect provider abstraction
- Add Claude setup guide and example configurations
- Verify complete user journey from config to execution

Multi-provider refactoring complete. Synapse now works with Claude
as the primary provider, with architecture ready for adding additional
platforms (OpenAI, Gemini, etc.) independently.
```

---

## Phase 6 (Future): OpenAI Provider Reintegration

**Status**: PARKED - Not implementing now, but architecture ready

### When Ready to Implement

1. Create `core/providers/openai_provider.py`
2. Move old OpenAI logic from main.py (use git history)
3. Implement BaseProvider interface for OpenAI Responses API
4. Add OpenAI-specific schema generator
5. Handle stateful conversations with `previous_response_id`
6. Restore vector store integration
7. Move tests from `tests/archived_openai/` to active test suite
8. Create `agents/examples/coder_openai.yaml`

**Key Design Principle**: OpenAI provider should be entirely contained in `core/providers/openai_provider.py` and not affect any other code.

---

## Development Workflow for Each Phase

1. **Implement** - Write the code for the phase
2. **Test** - Write tests and ensure they all pass
3. **Verify** - Run the test suite: `python -m pytest tests/ -v`
4. **Commit** - Use conventional commit message from roadmap
5. **Push** - `git push origin main`
6. **Update Roadmap** - Check off completed tasks
7. **Move to Next Phase** - Don't skip ahead

---

## Success Metrics

**Technical**:
- [ ] Can switch providers by changing one line in YAML config
- [ ] Adding new provider requires only implementing BaseProvider
- [ ] Agent methods work identically across all providers
- [ ] No provider-specific code in main loop or agent classes
- [ ] Test suite covers all critical paths

**Functional**:
- [ ] Claude CoderAgent completes full development cycle (read → write → test → commit)
- [ ] Knowledge store enhances agent responses with relevant context
- [ ] Error handling is robust and informative
- [ ] Performance is acceptable (response times under 5s for simple queries)

**Strategic**:
- [ ] Architecture supports future workflow agents (email, tasks, etc.)
- [ ] Documentation enables new agent creation without code inspection
- [ ] Project vision is clear and compelling

---

## Notes & Constraints

- **No Mixing**: Each provider implementation is isolated - no shared state or cross-provider dependencies
- **Testing First**: Every phase must have passing tests before moving forward
- **Commit Discipline**: One commit per phase, pushed to remote after verification
- **Provider Parity**: All providers must implement the same BaseProvider interface completely
- **Future-Proof**: Design decisions should anticipate 5+ providers, not just 2
