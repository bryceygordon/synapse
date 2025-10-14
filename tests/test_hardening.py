from unittest.mock import MagicMock
import pytest
import openai

# We need to import the specific function we are testing
from core.main import make_api_call

def test_api_call_retries_on_500_error(mocker):
    """
    Tests that the make_api_call function retries on APIStatusError (5xx)
    and succeeds on the final attempt.
    """
    # 1. Arrange
    # Mock the OpenAI client that will be passed to our function
    mock_client = MagicMock()

    # Create a mock response object for the final, successful call
    mock_success_response = MagicMock(id="success_id")

    # Set up the side_effect: fail twice, then succeed.
    mock_client.responses.create.side_effect = [
        openai.APIStatusError("Server error", response=MagicMock(), body=None),
        openai.APIStatusError("Server error", response=MagicMock(), body=None),
        mock_success_response
    ]

    # 2. Act
    # Call our hardened function
    result = make_api_call(client=mock_client, payload={})

    # 3. Assert
    # Check that the create method was called 3 times (1 initial + 2 retries)
    assert mock_client.responses.create.call_count == 3

    # Check that the final result is the successful response
    assert result.id == "success_id"

