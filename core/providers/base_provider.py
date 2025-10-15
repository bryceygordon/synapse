"""
Abstract base class for AI provider implementations.

This module defines the interface that all AI providers (Claude, OpenAI, Gemini, etc.)
must implement to work with Synapse's agent orchestration system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    """
    Standardized representation of a tool call from an AI provider.

    Attributes:
        id: Unique identifier for this tool call
        name: Name of the tool/function to invoke
        arguments: Dictionary of arguments to pass to the tool
    """
    id: str
    name: str
    arguments: dict


@dataclass
class ProviderResponse:
    """
    Standardized representation of an AI provider's response.

    Attributes:
        text: The text content of the response (if any)
        tool_calls: List of tool calls requested by the AI (if any)
        raw_response: The original response object from the provider
        finish_reason: Why the response ended (e.g., 'stop', 'tool_use', 'length')
    """
    text: str | None
    tool_calls: list[ToolCall]
    raw_response: Any
    finish_reason: str


class BaseProvider(ABC):
    """
    Abstract base class for AI provider implementations.

    All providers (Anthropic, OpenAI, Gemini, etc.) must implement this interface
    to ensure consistent behavior across different AI platforms.
    """

    @abstractmethod
    def create_client(self) -> Any:
        """
        Create and return a client instance for this provider.

        This should handle:
        - Loading API keys from environment variables
        - Initializing the provider's SDK client
        - Any necessary authentication

        Returns:
            Client instance (type varies by provider)

        Raises:
            ValueError: If API key is missing or invalid
        """
        pass

    @abstractmethod
    def send_message(
        self,
        client: Any,
        messages: list[dict],
        system_prompt: str,
        model: str,
        tools: list[dict],
        **kwargs
    ) -> ProviderResponse:
        """
        Send a message to the AI provider and return the response.

        Args:
            client: The provider's client instance
            messages: List of message dictionaries in provider format
            system_prompt: System instructions for the AI
            model: Model identifier (provider-specific)
            tools: List of tool schemas in provider format
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse with standardized response data

        Raises:
            Exception: Various provider-specific exceptions
        """
        pass

    @abstractmethod
    def format_tool_schemas(self, agent_instance: Any) -> list[dict]:
        """
        Generate provider-specific tool schemas from agent methods.

        This introspects the agent's methods and generates tool schemas
        in the format required by this specific provider.

        Args:
            agent_instance: The agent object with methods to expose as tools

        Returns:
            List of tool schema dictionaries in provider format
        """
        pass

    @abstractmethod
    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        """
        Format tool execution results for the provider.

        Different providers expect different formats for tool results.

        Args:
            tool_call_id: The ID of the tool call being responded to
            result: The string result from executing the tool

        Returns:
            Dictionary formatted for this provider
        """
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """
        Indicate whether this provider supports streaming responses.

        Returns:
            True if streaming is supported, False otherwise
        """
        pass
