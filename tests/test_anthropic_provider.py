"""
Tests for Anthropic/Claude provider implementation.

This module tests:
1. Client creation with/without API key
2. Message sending with mocked responses
3. Tool call extraction from Claude responses
4. Tool schema generation in Anthropic format
5. Tool result formatting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.providers.anthropic_provider import AnthropicProvider
from core.providers import ToolCall, ProviderResponse


class TestClientCreation:
    """Test Anthropic client creation."""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-api-key"})
    @patch("core.providers.anthropic_provider.Anthropic")
    def test_create_client_with_api_key(self, mock_anthropic):
        """Test that client is created when API key is present."""
        provider = AnthropicProvider()
        client = provider.create_client()

        mock_anthropic.assert_called_once_with(api_key="test-api-key")

    @patch.dict("os.environ", {}, clear=True)
    def test_create_client_without_api_key(self):
        """Test that ValueError is raised when API key is missing."""
        provider = AnthropicProvider()

        with pytest.raises(ValueError) as exc_info:
            provider.create_client()

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)


class TestMessageSending:
    """Test sending messages to Claude."""

    def test_send_message_text_only(self):
        """Test sending a message that returns only text."""
        provider = AnthropicProvider()
        mock_client = Mock()

        # Mock response with text content
        mock_response = Mock()
        mock_response.content = [Mock(type="text", text="Hello from Claude!")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        response = provider.send_message(
            client=mock_client,
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a helpful assistant",
            model="claude-sonnet-4.5",
            tools=[]
        )

        assert isinstance(response, ProviderResponse)
        assert response.text == "Hello from Claude!"
        assert len(response.tool_calls) == 0
        assert response.finish_reason == "end_turn"

    def test_send_message_with_tool_calls(self):
        """Test sending a message that returns tool calls."""
        provider = AnthropicProvider()
        mock_client = Mock()

        # Mock response with tool use
        mock_tool_use = Mock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.id = "call_123"
        mock_tool_use.name = "read_file"
        mock_tool_use.input = {"file_path": "test.py"}

        mock_response = Mock()
        mock_response.content = [mock_tool_use]
        mock_response.stop_reason = "tool_use"
        mock_client.messages.create.return_value = mock_response

        response = provider.send_message(
            client=mock_client,
            messages=[{"role": "user", "content": "Read test.py"}],
            system_prompt="You are a coding assistant",
            model="claude-sonnet-4.5",
            tools=[{"name": "read_file"}]
        )

        assert isinstance(response, ProviderResponse)
        assert response.text is None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "call_123"
        assert response.tool_calls[0].name == "read_file"
        assert response.tool_calls[0].arguments == {"file_path": "test.py"}
        assert response.finish_reason == "tool_use"

    def test_send_message_with_text_and_tool_calls(self):
        """Test response containing both text and tool calls."""
        provider = AnthropicProvider()
        mock_client = Mock()

        # Mock response with both text and tool use
        mock_text = Mock(type="text")
        mock_text.text = "I'll read that file for you."

        mock_tool = Mock(type="tool_use")
        mock_tool.id = "call_456"
        mock_tool.name = "read_file"
        mock_tool.input = {"file_path": "config.yaml"}

        mock_response = Mock()
        mock_response.content = [mock_text, mock_tool]
        mock_response.stop_reason = "tool_use"
        mock_client.messages.create.return_value = mock_response

        response = provider.send_message(
            client=mock_client,
            messages=[{"role": "user", "content": "Show me config.yaml"}],
            system_prompt="You are helpful",
            model="claude-sonnet-4.5",
            tools=[{"name": "read_file"}]
        )

        assert response.text == "I'll read that file for you."
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "read_file"

    def test_send_message_with_kwargs(self):
        """Test that additional kwargs are passed to API."""
        provider = AnthropicProvider()
        mock_client = Mock()

        mock_response = Mock()
        mock_response.content = [Mock(type="text", text="Test")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider.send_message(
            client=mock_client,
            messages=[{"role": "user", "content": "Test"}],
            system_prompt="System",
            model="claude-sonnet-4.5",
            tools=[],
            temperature=0.7,
            top_p=0.9
        )

        # Verify kwargs were passed through
        call_args = mock_client.messages.create.call_args[1]
        assert call_args["temperature"] == 0.7
        assert call_args["top_p"] == 0.9


class TestToolSchemaGeneration:
    """Test generation of Anthropic-format tool schemas."""

    def test_format_tool_schemas_single_tool(self):
        """Test schema generation for a single tool."""
        provider = AnthropicProvider()

        # Create a mock agent with a tool method
        class MockAgent:
            tools = ["test_tool"]

            def test_tool(self, arg1: str, arg2: int = 10) -> str:
                """
                A test tool that does something.

                Args:
                    arg1: First argument
                    arg2: Second argument with default
                """
                return "result"

        agent = MockAgent()
        schemas = provider.format_tool_schemas(agent)

        assert len(schemas) == 1
        schema = schemas[0]

        # Anthropic format checks
        assert "type" not in schema  # No "type": "function" wrapper
        assert schema["name"] == "test_tool"
        assert schema["description"] == "A test tool that does something."
        assert "input_schema" in schema  # Not "parameters"

        input_schema = schema["input_schema"]
        assert input_schema["type"] == "object"
        assert "arg1" in input_schema["properties"]
        assert "arg2" in input_schema["properties"]
        assert input_schema["properties"]["arg1"]["type"] == "string"
        assert input_schema["properties"]["arg2"]["type"] == "integer"
        assert input_schema["required"] == ["arg1"]  # arg2 has default

    def test_format_tool_schemas_multiple_tools(self):
        """Test schema generation for multiple tools."""
        provider = AnthropicProvider()

        class MockAgent:
            tools = ["tool1", "tool2"]

            def tool1(self, text: str) -> str:
                """Tool one."""
                return "ok"

            def tool2(self, count: int) -> str:
                """Tool two."""
                return "ok"

        agent = MockAgent()
        schemas = provider.format_tool_schemas(agent)

        assert len(schemas) == 2
        assert schemas[0]["name"] == "tool1"
        assert schemas[1]["name"] == "tool2"

    def test_format_tool_schemas_no_docstring(self):
        """Test that tools without docstrings are skipped."""
        provider = AnthropicProvider()

        class MockAgent:
            tools = ["no_doc_tool"]

            def no_doc_tool(self, arg: str) -> str:
                return "result"

        agent = MockAgent()
        schemas = provider.format_tool_schemas(agent)

        assert len(schemas) == 0  # Should be skipped


class TestToolResultFormatting:
    """Test formatting of tool results."""

    def test_format_tool_results(self):
        """Test that tool results are formatted correctly for Anthropic."""
        provider = AnthropicProvider()

        result = provider.format_tool_results(
            tool_call_id="call_123",
            result='{"status": "success", "content": "file contents"}'
        )

        assert result["type"] == "tool_result"
        assert result["tool_use_id"] == "call_123"
        assert result["content"] == '{"status": "success", "content": "file contents"}'


class TestProviderFeatures:
    """Test provider feature support."""

    def test_supports_streaming(self):
        """Test that Anthropic supports streaming."""
        provider = AnthropicProvider()
        assert provider.supports_streaming() is True


class TestIntegration:
    """Integration tests with mocked agent."""

    def test_full_workflow(self):
        """Test a complete workflow: schema generation → message → tool call."""
        provider = AnthropicProvider()

        # 1. Create mock agent
        class MockAgent:
            tools = ["calculate"]

            def calculate(self, expression: str) -> str:
                """
                Calculate a mathematical expression.

                Args:
                    expression: The expression to calculate
                """
                return "42"

        agent = MockAgent()

        # 2. Generate schemas
        schemas = provider.format_tool_schemas(agent)
        assert len(schemas) == 1
        assert schemas[0]["name"] == "calculate"

        # 3. Mock client and response
        mock_client = Mock()
        mock_tool_use = Mock(type="tool_use")
        mock_tool_use.id = "call_calc"
        mock_tool_use.name = "calculate"
        mock_tool_use.input = {"expression": "2+2"}
        mock_response = Mock()
        mock_response.content = [mock_tool_use]
        mock_response.stop_reason = "tool_use"
        mock_client.messages.create.return_value = mock_response

        # 4. Send message
        response = provider.send_message(
            client=mock_client,
            messages=[{"role": "user", "content": "What is 2+2?"}],
            system_prompt="You are a calculator",
            model="claude-sonnet-4.5",
            tools=schemas
        )

        # 5. Verify tool call
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "calculate"
        assert response.tool_calls[0].arguments == {"expression": "2+2"}

        # 6. Format tool result
        tool_result = provider.format_tool_results(
            tool_call_id=response.tool_calls[0].id,
            result="42"
        )
        assert tool_result["type"] == "tool_result"
        assert tool_result["content"] == "42"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
