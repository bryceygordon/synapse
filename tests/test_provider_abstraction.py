"""
Tests for provider abstraction layer.

This module verifies that:
1. BaseProvider enforces the abstract interface
2. ToolCall and ProviderResponse data classes work correctly
3. Provider factory loads providers correctly
4. Unknown providers raise appropriate errors
"""

import pytest
from core.providers import BaseProvider, ToolCall, ProviderResponse, get_provider


class TestDataClasses:
    """Test the standardized data classes."""

    def test_tool_call_creation(self):
        """Test ToolCall dataclass initialization."""
        tool_call = ToolCall(
            id="call_123",
            name="read_file",
            arguments={"file_path": "test.py"}
        )

        assert tool_call.id == "call_123"
        assert tool_call.name == "read_file"
        assert tool_call.arguments == {"file_path": "test.py"}

    def test_provider_response_creation(self):
        """Test ProviderResponse dataclass initialization."""
        tool_calls = [
            ToolCall(id="call_1", name="tool1", arguments={}),
            ToolCall(id="call_2", name="tool2", arguments={"arg": "value"})
        ]

        response = ProviderResponse(
            text="Here's my response",
            tool_calls=tool_calls,
            raw_response={"some": "data"},
            finish_reason="stop"
        )

        assert response.text == "Here's my response"
        assert len(response.tool_calls) == 2
        assert response.tool_calls[0].id == "call_1"
        assert response.finish_reason == "stop"

    def test_provider_response_no_text(self):
        """Test ProviderResponse with no text (tool calls only)."""
        tool_calls = [ToolCall(id="call_1", name="tool1", arguments={})]

        response = ProviderResponse(
            text=None,
            tool_calls=tool_calls,
            raw_response={},
            finish_reason="tool_use"
        )

        assert response.text is None
        assert len(response.tool_calls) == 1
        assert response.finish_reason == "tool_use"

    def test_provider_response_no_tool_calls(self):
        """Test ProviderResponse with no tool calls (text only)."""
        response = ProviderResponse(
            text="Just text",
            tool_calls=[],
            raw_response={},
            finish_reason="stop"
        )

        assert response.text == "Just text"
        assert len(response.tool_calls) == 0


class TestBaseProvider:
    """Test that BaseProvider enforces abstract methods."""

    def test_cannot_instantiate_base_provider(self):
        """Test that BaseProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseProvider()

    def test_subclass_must_implement_all_methods(self):
        """Test that subclasses must implement all abstract methods."""

        class IncompleteProvider(BaseProvider):
            def create_client(self):
                return None

        # Should raise TypeError because not all abstract methods are implemented
        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_complete_subclass_can_be_instantiated(self):
        """Test that a complete implementation can be instantiated."""

        class CompleteProvider(BaseProvider):
            def create_client(self):
                return "mock_client"

            def send_message(self, client, messages, system_prompt, model, tools, **kwargs):
                return ProviderResponse(
                    text="test",
                    tool_calls=[],
                    raw_response={},
                    finish_reason="stop"
                )

            def format_tool_schemas(self, agent_instance):
                return []

            def format_tool_results(self, tool_call_id, result):
                return {"id": tool_call_id, "result": result}

            def supports_streaming(self):
                return False

            def get_assistant_message(self, response):
                return {"role": "assistant", "content": response.text}

        # Should not raise
        provider = CompleteProvider()
        assert provider is not None
        assert provider.create_client() == "mock_client"
        assert provider.supports_streaming() is False


class TestProviderFactory:
    """Test the provider factory function."""

    def test_get_anthropic_provider(self):
        """Test loading the Anthropic provider."""
        provider = get_provider("anthropic")
        assert provider is not None
        assert provider.__class__.__name__ == "AnthropicProvider"

    def test_get_openai_provider(self):
        """Test loading the OpenAI provider."""
        provider = get_provider("openai")
        assert provider is not None
        assert provider.__class__.__name__ == "OpenAIProvider"

    def test_unknown_provider_raises_error(self):
        """Test that unknown provider names raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("unknown_provider")

        assert "unknown provider" in str(exc_info.value).lower()
        assert "unknown_provider" in str(exc_info.value)

    def test_provider_name_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        # All should load the same provider
        provider1 = get_provider("ANTHROPIC")
        provider2 = get_provider("Anthropic")
        provider3 = get_provider("AnThRoPiC")

        assert provider1.__class__.__name__ == "AnthropicProvider"
        assert provider2.__class__.__name__ == "AnthropicProvider"
        assert provider3.__class__.__name__ == "AnthropicProvider"

    def test_empty_provider_name(self):
        """Test that empty provider name raises ValueError."""
        with pytest.raises(ValueError):
            get_provider("")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
