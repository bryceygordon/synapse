# tests/test_knowledge_integration.py

import json
from unittest.mock import MagicMock
from core.agents.coder import CoderAgent

# ... (keep the create_mock_tool_call_response and create_mock_final_response functions) ...
def create_mock_tool_call_response():
    """Creates a mock response with a tool call."""
    tool_call = MagicMock()
    tool_call.id = "call_abc123"
    tool_call.name = "read_file"
    tool_call.arguments = json.dumps({"file_path": "test.txt"})
    tool_call.type = "function_call"

    response = MagicMock()
    response.id = "resp_123"
    response.output = [tool_call]
    response.output_text = None
    return response

def create_mock_final_response():
    """Creates a mock final text response."""
    response = MagicMock()
    response.id = "resp_456"
    response.output = []
    response.output_text = "The file content is: Hello World"
    return response

def test_stateful_responses_api_tool_loop(mocker):
    """
    Tests the complete STATEFUL conversation loop for the Responses API.
    Asserts that client-side history is NOT sent, and `previous_response_id` is used.
    """
    # 1. Arrange
    mock_openai_client = MagicMock()
    mock_openai_client.responses.create.side_effect = [
        create_mock_tool_call_response(),
        create_mock_final_response(),
    ]
    mocker.patch('core.main.OpenAI', return_value=mock_openai_client)

    agent = CoderAgent(config={"name": "TestCoder", "tools": ["read_file"]})

    # Mock file operations to return structured JSON
    structured_output = json.dumps({"status": "success", "content": "Hello World"})
    
    # This is the fix: Use autospec=True to preserve the function signature
    mocker.patch.object(
        agent,
        'read_file',
        return_value=structured_output,
        autospec=True
    )
    
    # The spy is no longer needed with this approach.
    # spy_read_file = mocker.spy(agent, 'read_file')

    mocker.patch('core.main.load_agent', return_value=agent)
    mocker.patch('builtins.input', side_effect=["read test.txt", KeyboardInterrupt])

    # 2. Act
    from core import main
    main.chat()

    # 3. Assert
    assert mock_openai_client.responses.create.call_count == 2
    
    # --- Assertions for the FIRST API call (user prompt) ---
    first_call_args = mock_openai_client.responses.create.call_args_list[0].kwargs
    assert "previous_response_id" not in first_call_args
    assert first_call_args['input'][0]['content'] == "read test.txt"

    # --- Assertions for the SECOND API call (tool output) ---
    second_call_args = mock_openai_client.responses.create.call_args_list[1].kwargs
    
    # CRITICAL: Assert that the state is being managed by the API
    assert second_call_args['previous_response_id'] == 'resp_123'
    
    # CRITICAL: Assert that the input ONLY contains the tool output
    input_for_second_call = second_call_args['input']
    assert len(input_for_second_call) == 1
    tool_output_message = input_for_second_call[0]
    assert tool_output_message['type'] == 'function_call_output'
    assert tool_output_message['call_id'] == 'call_abc123'
    assert "Hello World" in tool_output_message['output']
