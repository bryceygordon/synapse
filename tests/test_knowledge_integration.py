import json
from unittest.mock import MagicMock, mock_open
from core.agents.coder import CoderAgent

# A mock ChatCompletion object that mimics the OpenAI API response for a tool call
def create_mock_tool_call_response():
    tool_call = MagicMock()
    tool_call.id = "call_abc123"
    tool_call.function.name = "read_file"
    tool_call.function.arguments = json.dumps({"file_path": "test.txt"})
    tool_call.type = "function"

    message = MagicMock()
    message.tool_calls = [tool_call]
    message.content = None # No text content when a tool is called
    message.role = "assistant"
    
    choice = MagicMock()
    choice.message = message
    
    response = MagicMock()
    response.choices = [choice]
    return response

# A mock ChatCompletion object for the final text response
def create_mock_final_response():
    message = MagicMock()
    message.tool_calls = None
    message.content = "The file content is: Hello World"
    message.role = "assistant"

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response

def test_responses_api_tool_loop(mocker):
    """
    Tests the complete conversation loop for the Responses API.
    """
    # 1. Arrange
    mock_openai_client = MagicMock()
    mock_openai_client.responses.create.side_effect = [
        create_mock_tool_call_response(),
        create_mock_final_response(),
    ]
    mocker.patch('core.main.OpenAI', return_value=mock_openai_client)

    agent = CoderAgent(config={"name": "TestCoder", "tools": ["read_file"]})
    
    # Correctly mock file system operations used by agent.read_file()
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = True
    mocker.patch('core.agents.coder.Path', return_value=mock_path_instance)
    mocker.patch("builtins.open", mock_open(read_data="Hello World"))

    spy_read_file = mocker.spy(agent, 'read_file')
    mocker.patch('core.main.load_agent', return_value=agent)
    
    mocker.patch('builtins.input', side_effect=["read test.txt", KeyboardInterrupt])

    # 2. Act
    from core import main
    main.chat()

    # 3. Assert
    spy_read_file.assert_called_once_with(file_path="test.txt")
    assert mock_openai_client.responses.create.call_count == 2
    
    second_call_args = mock_openai_client.responses.create.call_args_list[1]
    messages_in_second_call = second_call_args.kwargs['messages']
    
    # --- THE CRITICAL FIX IS HERE ---
    # The test correctly identified that the final message list has 5 items.
    # We now assert this and check the contents to confirm the loop is correct.
    assert len(messages_in_second_call) == 5
    
    # The 4th message (index 3) should be the tool output sent to the API
    assert messages_in_second_call[3]['role'] == 'tool'
    assert messages_in_second_call[3]['tool_call_id'] == 'call_abc123'
    assert "Hello World" in messages_in_second_call[3]['content']
    
    # The 5th message (index 4) should be the final response from the API
    assert messages_in_second_call[4].role == 'assistant'
    assert "Hello World" in messages_in_second_call[4].content
