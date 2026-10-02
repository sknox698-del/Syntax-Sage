import unittest
from unittest.mock import patch

from app.ai_client import AIClientError, SYSTEM_PROMPT, EXPLANATION_SYSTEM_PROMPT, ask_ai, stream_ai


class TestAIClient(unittest.TestCase):

    @patch("app.ai_client.ollama.chat")
    def test_ask_ai_returns_response(self, mock_chat):
        mock_chat.return_value = {
            "message": {
                "content": "Test response"
            }
        }

        result = ask_ai("Hello")

        self.assertEqual(result, "Test response")
        self.assertEqual(mock_chat.call_args.kwargs["messages"][0]["content"], SYSTEM_PROMPT)

    @patch("app.ai_client.ollama.chat")
    def test_ask_ai_handles_connection_error(self, mock_chat):
        mock_chat.side_effect = ConnectionError("Ollama offline")

        with self.assertRaises(AIClientError):
            ask_ai("Hello")

    @patch("app.ai_client.ollama.chat")
    def test_stream_ai_returns_chunks(self, mock_chat):
        mock_chat.return_value = [
            {
                "message": {
                    "content": "Hello "
                }
            },
            {
                "message": {
                    "content": "Steve!"
                }
            },
        ]

        result = "".join(stream_ai("Hello"))

        self.assertEqual(result, "Hello Steve!")
        self.assertEqual(mock_chat.call_args.kwargs["messages"][0]["content"], SYSTEM_PROMPT)


    @patch("app.ai_client.ollama.chat")
    def test_stream_ai_uses_system_prompt_override(self, mock_chat):
        mock_chat.return_value = [{"message": {"content": "Explanation"}}]

        result = "".join(stream_ai("Explain source", system_prompt=EXPLANATION_SYSTEM_PROMPT))

        self.assertEqual(result, "Explanation")
        self.assertEqual(mock_chat.call_args.kwargs["messages"], [
            {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
            {"role": "user", "content": "Explain source"},
        ])
        self.assertTrue(mock_chat.call_args.kwargs["stream"])

    @patch("app.ai_client.ollama.chat")
    def test_stream_ai_none_uses_default_system_prompt(self, mock_chat):
        mock_chat.return_value = []
        list(stream_ai("Hello", system_prompt=None))
        self.assertEqual(mock_chat.call_args.kwargs["messages"][0]["content"], SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()