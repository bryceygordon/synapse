from unittest.mock import MagicMock
from core.agents.coder import CoderAgent

def test_file_search_tool_is_added_with_function_tools(mocker):
    """
    Tests that both function tools and file_search tool are correctly added
    with the proper FLAT structure for function tools.
    """
    # 1. Arrange
    agent_config = {
        "name": "KnowledgeableCoder",
        "tools": ["read_file"], # Include a function tool for this test
        "vector_store_id": "vs_test123"
    }
    agent = CoderAgent(config=agent_config)

    mock_openai_client = MagicMock()
    mock_openai_client.responses.create.return_value = MagicMock(output_text="OK", output=[])
    mocker.patch('core.main.OpenAI', return_value=mock_openai_client)
    mocker.patch('core.main.load_agent', return_value=agent)
    mocker.patch('builtins.input', side_effect=["hello", KeyboardInterrupt])

    # 2. Act
    from core import main
    main.chat()

    # 3. Assert
    mock_openai_client.responses.create.assert_called_once()
    call_args = mock_openai_client.responses.create.call_args
    api_tools = call_args.kwargs.get("tools", [])

    assert len(api_tools) == 2

    # Check that the FIRST tool is our function tool with a FLAT structure.
    assert api_tools[0]["type"] == "function"
    assert api_tools[0]["name"] == "read_file" # Check the 'name' key directly
    assert "description" in api_tools[0]
    assert "parameters" in api_tools[0]
    
    # Check that the SECOND tool is file_search
    assert api_tools[1]["type"] == "file_search"
    assert api_tools[1]["vector_store_ids"] == ["vs_test123"]
