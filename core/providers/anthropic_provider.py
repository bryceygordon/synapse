"""
Anthropic (Claude) provider implementation.

This module provides integration with Anthropic's Claude API using the Messages API.
"""

import os
import json
import inspect
import re
from typing import get_type_hints, get_origin, get_args, Any

from anthropic import Anthropic
from core.providers.base_provider import BaseProvider, ToolCall, ProviderResponse


# Type mapping for converting Python types to JSON schema types
TYPE_MAPPING = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def parse_docstring_args(docstring: str) -> dict[str, str]:
    """Parse the 'Args:' section of a docstring."""
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


class AnthropicProvider(BaseProvider):
    """Provider implementation for Anthropic's Claude AI."""

    def create_client(self) -> Anthropic:
        """
        Create and return an Anthropic client instance.

        Returns:
            Anthropic client configured with API key from environment

        Raises:
            ValueError: If ANTHROPIC_API_KEY environment variable is not set
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it to your Anthropic API key."
            )

        return Anthropic(api_key=api_key)

    def send_message(
        self,
        client: Anthropic,
        messages: list[dict],
        system_prompt: str,
        model: str,
        tools: list[dict],
        **kwargs
    ) -> ProviderResponse:
        """
        Send a message to Claude and return the response.

        Args:
            client: Anthropic client instance
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: System instructions for Claude
            model: Claude model identifier (e.g., 'claude-sonnet-4.5')
            tools: List of tool schemas in Anthropic format
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            ProviderResponse with standardized response data
        """
        # Set default max_tokens if not provided
        max_tokens = kwargs.pop("max_tokens", 4096)

        # Build the API request
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }

        # Add tools if provided
        if tools:
            request_params["tools"] = tools

        # Add any additional parameters
        request_params.update(kwargs)

        # Make the API call
        response = client.messages.create(**request_params)

        # Parse the response
        text_content = None
        tool_calls = []

        for content_block in response.content:
            if content_block.type == "text":
                text_content = content_block.text
            elif content_block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=content_block.id,
                        name=content_block.name,
                        arguments=content_block.input
                    )
                )

        return ProviderResponse(
            text=text_content,
            tool_calls=tool_calls,
            raw_response=response,
            finish_reason=response.stop_reason or "unknown"
        )

    def format_tool_schemas(self, agent_instance: Any) -> list[dict]:
        """
        Generate Anthropic-compatible tool schemas from agent methods.

        Claude's tool schema format is slightly different from OpenAI's:
        - No "type": "function" wrapper
        - Uses "input_schema" instead of "parameters"
        - Otherwise similar structure

        Args:
            agent_instance: The agent object with methods to expose as tools

        Returns:
            List of tool schemas in Anthropic format
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

                # Handle generic types like list[str]
                origin = get_origin(param_type)
                args = get_args(param_type)

                # Build the property schema
                prop_schema = {
                    "description": param_descriptions.get(param.name, "No description available.")
                }

                if origin is list:
                    # It's a list type
                    prop_schema["type"] = "array"
                    if args:
                        # We have type arguments like list[str]
                        item_type = args[0]
                        prop_schema["items"] = {
                            "type": TYPE_MAPPING.get(item_type, "string")
                        }
                else:
                    # Simple type
                    prop_schema["type"] = TYPE_MAPPING.get(param_type, "string")

                properties[param.name] = prop_schema

                if param.default is inspect.Parameter.empty:
                    required.append(param.name)

            # Anthropic format: no "type" wrapper, uses "input_schema"
            schema = {
                "name": tool_name,
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            schemas.append(schema)

        return schemas

    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        """
        Format tool execution results for Anthropic.

        Anthropic expects tool results in a specific message format.

        Args:
            tool_call_id: The ID of the tool call being responded to
            result: The string result from executing the tool

        Returns:
            Dictionary formatted for Anthropic's tool result format
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_call_id,
            "content": result
        }

    def supports_streaming(self) -> bool:
        """
        Indicate whether streaming is supported.

        Returns:
            True (Anthropic supports streaming, though not implemented yet)
        """
        return True  # Anthropic supports streaming, but we're not implementing it in Phase 2
