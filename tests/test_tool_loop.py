import json
from unittest.mock import MagicMock
import pytest
from core.agents.coder import CoderAgent

def test_full_tool_use_loop(mocker):
    """
    Tests that the second API call contains the complete transaction record
    (the original tool call and its output).
    """
    # 1. Arrange
    tool_call_mock = MagicMock()
    tool_call_mock.type = "function_call"
    tool_call_mock.name = "read_file"
    tool_call_mock.arguments = json.dumps({"file_path": "test.txt"})
    tool_call_mock.id = "call123"
    # The .model_dump() method is part of the Pydantic model structure used by OpenAI's library
    tool_call_mock.model_dump.return_value = {
        "type": "function_call",
        "name": "read_file",
        "arguments": json.dumps({"file_path": "test.txt"}),
        "id": "call123"
    }

    mock_tool_call_response = MagicMock()
    mock_tool_call_response.id = "response1"
    mock_tool_call_response.output = [tool_call_mock]

    mock_final_response = MagicMock()
    mock_final_response.id = "response2"
    mock_final_response.output = []
    mock_final_response.output_text = "The file contains: Hello"

    mock_openai_client = MagicMock()
    mock_openai_client.responses.create.side_effect = [
        mock_tool_call_response,
        mock_final_response
    ]

    mocker.patch('core.main.OpenAI', return_value=mock_openai_client)
    agent = CoderAgent(config={"name": "TestCoder", "tools": ["read_file"]})
    spy_read_file = mocker.spy(agent, 'read_file')
    mocker.patch('core.main.load_agent', return_value=agent)
    mock_input = mocker.patch('builtins.input')
    mock_input.side_effect = ["read test.txt", KeyboardInterrupt]

    # 2. Act
    from core import main
    main.chat()

    # 3. Assert
    spy_read_file.assert_called_once_with(file_path="test.txt")
    assert mock_openai_client.responses.create.call_count == 2
    
    # --- THE CRITICAL FIX IS HERE ---
    second_call_args = mock_openai_client.responses.create.call_args_list[1]
    input_to_second_call = second_call_args.kwargs['input']
    
    # Verify the input is a list with two items
    assert len(input_to_second_call) == 2
    # Verify the first item is the original tool call
    assert input_to_second_call[0]['type'] == 'function_call'
    assert input_to_second_call[0]['id'] == 'call123'
    # Verify the second item is the tool output
    assert input_to_second_call[1]['type'] == 'function_call_output'
    assert input_to_second_call[1]['call_id'] == 'call123'

