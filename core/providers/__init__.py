"""
Provider abstraction layer for multi-platform AI support.

This module provides a factory pattern for loading AI providers (Claude, OpenAI, etc.)
and ensures consistent interfaces across different platforms.
"""

from core.providers.base_provider import BaseProvider, ToolCall, ProviderResponse


def get_provider(provider_name: str) -> BaseProvider:
    """
    Factory function to get a provider instance by name.

    Args:
        provider_name: Name of the provider ('anthropic', 'openai', etc.)

    Returns:
        Instance of the requested provider

    Raises:
        ValueError: If provider_name is not supported

    Example:
        >>> provider = get_provider('anthropic')
        >>> client = provider.create_client()
    """
    provider_name = provider_name.lower()

    if provider_name == "anthropic":
        from core.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider()
    elif provider_name == "openai":
        from core.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()
    else:
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Supported providers: anthropic, openai"
        )


__all__ = [
    'BaseProvider',
    'ToolCall',
    'ProviderResponse',
    'get_provider',
]
