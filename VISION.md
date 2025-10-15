# Synapse Vision Document

## Core Purpose

**Synapse is a universal framework for building AI-powered agentic workflows across any domain.**

This is NOT just a coding assistant. This is NOT just another AI wrapper. Synapse is designed to be the foundation for automating any repetitive, decision-driven workflow where AI reasoning combined with programmatic actions creates value.

---

## The Problem We're Solving

Current AI tools either:
1. Lock you into a specific platform (OpenAI, Claude, etc.)
2. Require significant coding for each new workflow
3. Don't provide a clean separation between AI platform and workflow logic
4. Make it hard to add new capabilities or switch providers

**Synapse solves this by making both the AI platform AND the workflow logic pluggable.**

---

## Design Philosophy

### 1. **Workflow-First, Not Chat-First**

Synapse is optimized for building agents that DO things, not just answer questions. The architecture assumes:
- Agents have specific domains (code, email, tasks, documents, etc.)
- Agents have tools (methods) that perform real actions
- Conversations are means to an end, not the end itself

### 2. **Platform Agnostic**

The AI provider (Claude, OpenAI, Gemini, etc.) is just a configuration detail. Your agent logic should work identically regardless of which AI is reasoning about the problem. This means:
- No vendor lock-in
- Easy A/B testing between providers
- Future-proof against API changes
- Use the best model for each specific task

### 3. **Configuration Over Code**

Creating a new agent should be as simple as:
1. Writing a YAML config file
2. Implementing methods for your domain
3. Running Synapse

No framework boilerplate. No complex inheritance hierarchies. No coupling to API details.

### 4. **Methods Are Tools**

Agent capabilities are just Python methods with docstrings and type hints. Synapse's introspection system automatically:
- Discovers available methods
- Generates platform-specific tool schemas
- Handles invocation and error handling
- Manages serialization

This means adding a new capability to an agent is just adding a method.

### 5. **Composable and Modular**

Each piece of Synapse is independent:
- **Providers** don't know about agents
- **Agents** don't know about providers
- **Tools** don't know about either
- **Knowledge stores** are pluggable
- **Workflows** are isolated from each other

Adding a new provider doesn't touch agent code. Adding a new agent doesn't touch provider code.

---

## Intended Use Cases

### Current: Code Development
- Read, write, test, and commit code autonomously
- Follow TDD workflows
- Integrate with existing project structures
- Respect security boundaries

### Near-Term: Email Management
**Agent**: `EmailAgent`
**Tools**: `read_inbox`, `send_email`, `label_email`, `create_draft`, `search_emails`
**Workflow**: Triage emails, auto-respond to common queries, flag important messages, summarize threads

### Near-Term: Task Orchestration
**Agent**: `TaskAgent`
**Tools**: `create_task`, `update_task`, `get_tasks`, `prioritize_tasks`, `schedule_task`
**Workflow**: Create tasks from emails/messages, intelligent prioritization, deadline management, integration with Todoist/other platforms

### Near-Term: Document Processing
**Agent**: `DocumentAgent`
**Tools**: `read_document`, `summarize`, `extract_data`, `convert_format`, `batch_process`
**Workflow**: Bulk document analysis, data extraction, format conversion, intelligent summarization

### Long-Term: Custom Workflows
The architecture should support ANY workflow where:
1. There's a clear domain (finance, research, content creation, etc.)
2. Actions can be expressed as Python methods
3. An AI can reason about when to use each action

**Examples:**
- Financial analysis and reporting
- Research paper summarization and synthesis
- Content generation and editing
- Data pipeline orchestration
- System administration tasks
- Customer support automation

---

## Key Architectural Decisions

### Provider Abstraction Layer
All AI platform differences are encapsulated in provider classes. This means:
- Tool schema generation is provider-specific
- Response parsing is provider-specific
- Context management is provider-specific
- BUT: Agent logic is completely provider-agnostic

### Object-Oriented Agent Design
Agents are objects instantiated from YAML configurations. This enables:
- Dynamic discovery of capabilities
- Runtime introspection for tool schemas
- Clear separation of concerns
- Easy testing (mock the provider, test the agent)

### Local-First Knowledge Management
Instead of relying on provider-specific vector stores (OpenAI's vector stores, Claude's future offerings), Synapse uses local ChromaDB by default. This ensures:
- No vendor lock-in for RAG capabilities
- Full control over indexed content
- Consistent behavior across providers
- Privacy (your data stays local)

### Configuration-Driven Everything
Every aspect of an agent is declared in YAML:
- Which provider to use
- Which model to use
- System prompt
- Available tools
- Knowledge sources
- Workflow-specific parameters

This makes it trivial to:
- Version control agent configurations
- Share agent designs
- A/B test different configurations
- Switch providers without code changes

---

## Success Criteria

Synapse is successful when:

1. **A new workflow agent can be created in under 1 hour** (assuming domain methods exist)
2. **Switching providers requires changing one line in a YAML file**
3. **The same agent logic works identically across all supported providers**
4. **Adding a new provider requires zero changes to existing agent code**
5. **Non-technical users can configure existing agents** (given documentation)
6. **The architecture scales to 10+ providers and 50+ agent types without refactoring**

---

## Anti-Goals

Synapse is NOT trying to be:
- A general-purpose chatbot interface
- A visual workflow builder (it's code and config files)
- A hosted service (it's a local tool)
- A batteries-included solution (you bring your agent logic)
- A replacement for LangChain/AutoGPT/etc. (different philosophy)

---

## Development Principles

When making any architectural decision, ask:

1. **Does this couple agent logic to a specific provider?** → If yes, reject it
2. **Does this make adding a new workflow harder?** → If yes, reject it
3. **Does this require changing multiple files to add a provider?** → If yes, reject it
4. **Does this assume a specific use case (like coding)?** → If yes, reject it
5. **Does this make the system more modular and composable?** → If yes, accept it

---

## The Long-Term Vision

Synapse should become the **go-to foundation for building personal AI automation**. When someone thinks "I want an AI to handle my emails" or "I need AI to manage my tasks" or "I want to automate this repetitive workflow", they should be able to:

1. Find or create an agent class for that domain
2. Configure it via YAML
3. Run it with their preferred AI provider
4. Have it just work

The measure of success is: **How many different workflows can run on Synapse without modifying the core engine?**

---

## Current Status → Vision Gap

**Where we are:**
- Solid architecture for coding workflows
- Coupled to OpenAI's experimental Responses API (problematic)
- Single agent type (CoderAgent)
- Provider-specific knowledge management

**Where we're going:**
- Provider abstraction layer (any AI platform)
- Multiple agent types (Email, Task, Document, Custom)
- Local knowledge management (platform-agnostic RAG)
- Clear patterns for adding new workflows

**This refactoring is the bridge between current state and long-term vision.**

---

## For Developers Working on Synapse

When implementing features or fixing bugs, always keep the end vision in mind:

- **Not just coding** → Will this work for email/task/document agents?
- **Not just OpenAI** → Does this assume a specific provider's capabilities?
- **Not just one workflow** → Is this design general enough for 10 agent types?
- **Not just now** → Will this architecture scale to 50+ agents and 10+ providers?

**The vision is the north star. The architecture is how we get there. Every commit should move us closer.**
