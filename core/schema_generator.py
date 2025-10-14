import inspect
from typing import get_type_hints

# A mapping from Python types to JSON Schema types.
TYPE_MAPPING = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

def generate_tool_schemas(agent_instance: object) -> list[dict]:
    """
    Generates OpenAI-compatible tool schemas by introspecting an agent's methods.

    This function looks for methods on the agent instance that are listed in its
    'tools' attribute. It then parses their docstrings and type hints to
    automatically generate the JSON schema required by the OpenAI API.

    The docstring is expected to follow a simple format:
    - The first line is the function's description.
    - An 'Args:' section describes the parameters.

    Args:
        agent_instance: An initialized agent object (e.g., CoderAgent).

    Returns:
        A list of dictionaries, where each dictionary is a valid OpenAI tool schema.
    """
    schemas = []
    tool_names = getattr(agent_instance, 'tools', [])

    for tool_name in tool_names:
        method = getattr(agent_instance, tool_name, None)
        if not method or not callable(method):
            continue

        docstring = inspect.getdoc(method)
        if not docstring:
            continue

        # Parse the docstring
        lines = docstring.strip().split('\n')
        description = lines[0]
        
        # Get function signature and type hints
        signature = inspect.signature(method)
        type_hints = get_type_hints(method)
        
        properties = {}
        required = []

        for param in signature.parameters.values():
            if param.name == 'self':
                continue
            
            param_type = type_hints.get(param.name)
            if not param_type:
                continue # Skip params without type hints for robustness
                
            properties[param.name] = {
                "type": TYPE_MAPPING.get(param_type, "string"),
                "description": f"Description for {param.name}." # Placeholder
            }
            
            if param.default is inspect.Parameter.empty:
                required.append(param.name)

        schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
        schemas.append(schema)

    return schemas

