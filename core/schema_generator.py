import inspect
import re
from typing import get_type_hints

TYPE_MAPPING = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

def parse_docstring_args(docstring: str) -> dict[str, str]:
    """Parses the 'Args:' section of a docstring."""
    args_section = re.search(r'Args:(.*)', docstring, re.S)
    if not args_section:
        return {}
    
    args_str = args_section.group(1)
    arg_lines = [line.strip() for line in args_str.strip().split('\n')]
    
    descriptions = {}
    for line in arg_lines:
        match = re.match(r'(\w+):\s*(.*)', line)
        if match:
            param_name, description = match.groups()
            descriptions[param_name] = description
            
    return descriptions

def generate_tool_schemas(agent_instance: object) -> list[dict]:
    """
    Generates OpenAI-compatible tool schemas by introspecting an agent's methods.
    This version creates the correct flat structure for function tools.
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

        lines = docstring.strip().split('\n')
        description = lines[0]
        
        param_descriptions = parse_docstring_args(docstring)
        
        signature = inspect.signature(method)
        type_hints = get_type_hints(method)
        
        properties = {}
        required = []

        for param in signature.parameters.values():
            if param.name == 'self':
                continue
            
            param_type = type_hints.get(param.name)
            if not param_type:
                continue
                
            properties[param.name] = {
                "type": TYPE_MAPPING.get(param_type, "string"),
                "description": param_descriptions.get(param.name, "No description available.")
            }
            
            if param.default is inspect.Parameter.empty:
                required.append(param.name)

        # --- THE CRITICAL FIX IS HERE ---
        # The schema is a single, flat dictionary.
        schema = {
            "type": "function",
            "name": tool_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
        schemas.append(schema)

    return schemas
