# core/providers/google_provider.py

import os
from typing import Any
import google.generativeai as genai
from .base_provider import BaseProvider, ProviderResponse, ToolCall, TokenUsage

class GoogleProvider(BaseProvider):
    """
    Provider for Google's Gemini models.
    """
    def create_client(self) -> Any:
        """
        Creates and configures the Gemini client.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        return genai

    def send_message(
        self,
        client: Any,
        system_prompt: str,
        user_prompt: str,
        model: str,
        tools: list[dict],
        discussion: list[dict]
    ) -> ProviderResponse:
        """
        Sends a message to the Gemini API.
        Note: Gemini API has a different structure for discussion history.
        """
        generation_config = {"temperature": 0.1}
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        # The Gemini API uses a specific model object.
        model_instance = client.GenerativeModel(
            model,
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_prompt
        )

        # Gemini's chat history is a list of alternating 'user' and 'model' roles.
        # We need to adapt the discussion history to this format.
        chat_history = []
        for msg in discussion:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Start a chat session with the history
        chat = model_instance.start_chat(history=chat_history)
        response = chat.send_message(user_prompt)

        # Extract text and calculate token usage
        response_text = response.text
        # Note: Gemini's Python SDK does not directly expose token counts in the same way.
        # This is a simplification. For precise counts, a more direct API call might be needed.
        input_tokens = model_instance.count_tokens(chat.history).total_tokens
        output_tokens = model_instance.count_tokens(response_text).total_tokens

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

        return ProviderResponse(
            text=response_text,
            tool_calls=[],
            raw_response=response,
            finish_reason="stop", # Gemini API doesn't always provide a finish reason in this flow
            usage=usage
        )

    # --- Stubs for methods not used by the tool-less agent ---
    def format_tool_schemas(self, agent_instance: Any) -> list[dict]:
        return []

    def format_tool_results(self, tool_call_id: str, result: str) -> dict:
        return {}

    def supports_streaming(self) -> bool:
        return False

    def get_assistant_message(self, response: ProviderResponse) -> dict:
        return {"role": "assistant", "content": response.text}
