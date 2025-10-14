cat <<EOF > ARCHITECTURAL_BLUEPRINT.md
# Architectural Blueprint

This blueprint outlines the structure of the Synapse engine, based on an object-oriented, configuration-driven pattern for the OpenAI Responses API.

## 1. The Core Engine (CLI Application)
* **Technology**: Python, using the `Typer` library.
* **Function**: Manages the main application loop. Its central responsibility is to use the `AgentLoader` to create an active `agent` instance and then mediate the conversation, invoking methods on that instance as requested by the AI.

## 2. Agent Class Hierarchy (`core/agents/`)
* **`base.py`**: Defines an abstract `BaseAgent` class. This class handles common logic like storing attributes from the config (`system_prompt`, `model`, etc.).
* **`coder.py`**: Defines the `CoderAgent(BaseAgent)` class. Its methods are the tools available to the agent: `read_file`, `write_file`, `run_shell_command`, etc.

## 3. Configuration (`agents/coder.yaml`)
* The blueprint for instantiating an agent object. It includes a `class_name` key to tell the loader which Python class to use.

## 4. Agent Loader & Introspector
* A sophisticated module that:
    1.  Reads an agent's `.yaml` configuration.
    2.  Dynamically imports the class specified by `class_name`.
    3.  Instantiates the class, passing the YAML attributes to its constructor.
    4.  Introspects the newly created agent object's methods (as defined in the YAML's `tools` list) and generates the required JSON Schemas for the OpenAI API directly from the methods' docstrings and type hints.

## 5. Method Invoker
* When the core loop receives a `tool_call` from the API, it uses Python's `getattr()` function to dynamically get the method from the active `agent` instance (e.g., `method = getattr(coder_agent, "run_shell_command")`).
* It then securely calls this method with the arguments provided by the AI.

## 6. Knowledge Stores (Vector Stores)
* Managed as standalone entities via the OpenAI API.
* A dedicated GitHub Actions workflow monitors the target project repository. On `git push`, the action automatically syncs the codebase to the agent's designated Vector Store.
EOF
