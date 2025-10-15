"""
OpenAI provider implementation.

This module provides integration with OpenAI's API using the Chat Completions API.
"""

import os
import json
import inspect
import re
from typing import get_type_hints, get_origin, get_args, Any

from openai import OpenAI
from core.providers.base_provider import BaseProvider, ToolCall, ProviderResponse, TokenUsage


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


class OpenAIProvider(BaseProvider):
    """Provider implementation for OpenAI's GPT models."""

    def create_client(self) -> OpenAI:
        """
        Create and return an OpenAI client instance.

        Returns:
            OpenAI client configured with API key from environment

        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it to your OpenAI API key."
            )

        return OpenAI(api_key=api_key)

    def send_message(
        self,
        client: OpenAI,
        messages: list[dict],
        system_prompt: str,
        model: str,
        tools: list[dict],
        **kwargs
    ) -> ProviderResponse:
        """
        Send a message to OpenAI and return the response.

        Args:
            client: OpenAI client instance
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: System instructions for the model
            model: OpenAI model identifier (e.g., 'gpt-4o', 'gpt-4o-mini')
            tools: List of tool schemas in OpenAI format
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            ProviderResponse with standardized response data
        """
        # Build messages list with system prompt first
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        # Build the API request
        request_params = {
            "model": model,
            "messages": full_messages,
        }

        # Add tools if provided
        if tools:
            request_params["tools"] = tools

        # Add any additional parameters
        request_params.update(kwargs)

        # Make the API call
        response = client.chat.completions.create(**request_params)

        # Parse the response
        message = response.choices[0].message
        text_content = message.content
        tool_calls = []

        # Check for tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments)
                    )
                )

        # Extract token usage information
        usage = None
        if response.usage:
            usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )

        return ProviderResponse(
            text=text_content,
            tool_calls=tool_calls,
            raw_response=response,
            finish_reason=response.choices[0].finish_reason or "unknown",
            usage=usage
        )

    def format_tool_schemas(self, agent_instance: Any) -> list[dict]:
        """
        Generate OpenAI-compatible tool schemas from agent methods.

        OpenAI's tool schema format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "description",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }

        Args:
            agent_instance: The agent object with methods to expose as tools

        Returns:
            List of tool schemas in OpenAI format
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

            # OpenAI format: wrapped in "type": "function" with "function" object
            # Note: We can't use strict mode because it requires all properties to be required
            # (no optional parameters), which conflicts with our function signatures.
            # The prompt instructions serve as our primary guard against incorrect calls.
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
                }
            }
            schemas.append(schema)

        return schemas

    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        """
        Format tool execution results for OpenAI.

        OpenAI expects tool results as messages with role "tool".

        Args:
            tool_call_id: The ID of the tool call being responded to
            result: The string result from executing the tool

        Returns:
            Dictionary formatted for OpenAI's tool result format
        """
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        }

    def supports_streaming(self) -> bool:
        """
        Indicate whether streaming is supported.

        Returns:
            True (OpenAI supports streaming, though not implemented yet)
        """
        return True  # OpenAI supports streaming, but we're not implementing it yet

    def get_assistant_message(self, response: ProviderResponse) -> dict:
        """
        Extract the assistant message dict for OpenAI conversation history.

        For OpenAI, we need to return the message object from the response,
        which includes tool_calls if present.

        Args:
            response: The ProviderResponse from send_message

        Returns:
            Dictionary with 'role' and either 'content' or 'tool_calls'
        """
        message = response.raw_response.choices[0].message

        # Build the assistant message dict
        assistant_msg = {"role": "assistant"}

        # Add content if present
        if message.content:
            assistant_msg["content"] = message.content

        # Add tool_calls if present
        if message.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]

        return assistant_msg
