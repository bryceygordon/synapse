# tests/test_hardening.py

import pytest
import openai
from unittest.mock import MagicMock
from core.main import make_api_call, is_server_error

def test_api_call_retries_on_500_error(mocker):
    """
    Tests that the make_api_call function retries on APIStatusError (5xx)
    and succeeds on the final attempt.
    """
    # 1. Arrange
    mock_client = MagicMock()
    mock_success_response = MagicMock(id="success_id")
    
    # This is the fix: Create a mock response with a status_code.
    mock_http_response = MagicMock()
    mock_http_response.status_code = 500
    
    server_error = openai.APIStatusError(
        "Server error", response=mock_http_response, body=None
    )

    # Set up the side_effect: fail twice with the correct error, then succeed.
    mock_client.responses.create.side_effect = [
        server_error,
        server_error,
        mock_success_response
    ]

    # 2. Act
    result = make_api_call(client=mock_client, payload={})

    # 3. Assert
    assert mock_client.responses.create.call_count == 3
    assert result.id == "success_id"
