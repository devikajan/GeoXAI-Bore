import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from fastapi.testclient import TestClient
from backend.main import app


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.environment = patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "gemini-3.1-flash-lite"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.env_file = patch("backend.gemini_assistant.ENV_PATH", Path("__missing_test_env__"))
        self.env_file.start()
        self.addCleanup(self.env_file.stop)

    def request(self):
        return self.client.post("/chat", json={"messages": [{"role": "user", "content": "Explain SHAP"}]})

    @patch("backend.gemini_assistant.requests.post")
    def test_reply_and_history_mapping(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": "SHAP explains model influence."}]}}]}
        response = self.client.post("/chat", json={"messages": [
            {"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Explain SHAP"}]})
        self.assertEqual(response.json(), {"reply": "SHAP explains model influence."})
        payload = post.call_args.kwargs
        self.assertEqual(payload["json"]["contents"][1]["role"], "model")
        self.assertEqual(payload["headers"]["x-goog-api-key"], "test-key")

    @patch("backend.gemini_assistant.requests.post")
    def test_telugu_and_simple_mode_reach_system_instruction(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": "సమాధానం"}]}}]}
        response = self.client.post("/chat", json={
            "messages": [{"role": "user", "content": "నా బోరు ప్రమాదం వివరించండి"}],
            "language": "te",
            "simple_mode": True,
        })
        self.assertEqual(response.status_code, 200)
        instruction = post.call_args.kwargs["json"]["systemInstruction"]["parts"][0]["text"]
        self.assertIn("Telugu", instruction)
        self.assertIn("five action steps", instruction)

    @patch("backend.gemini_assistant.requests.post")
    def test_assessment_context_is_grounded_in_system_instruction(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": "Check the pump."}]}}]}
        response = self.client.post("/chat", json={
            "messages": [{"role": "user", "content": "Explain my result"}],
            "language": "en",
            "assessment": {
                "risk_category": "High",
                "ensemble_probability": 0.78,
                "top_features": [{"feature": "Motor temperature", "shap_value": 0.22, "impact": "increases failure risk"}],
            },
        })
        self.assertEqual(response.status_code, 200)
        instruction = post.call_args.kwargs["json"]["systemInstruction"]["parts"][0]["text"]
        self.assertIn('"risk_category": "High"', instruction)
        self.assertIn("trusted application data", instruction)

    @patch("backend.gemini_assistant.requests.post")
    def test_missing_key_does_not_call_provider(self, post):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            self.assertEqual(self.request().status_code, 503)
        post.assert_not_called()

    @patch("backend.gemini_assistant.requests.post")
    def test_provider_errors_are_sanitized(self, post):
        for status, expected in [(403, 503), (429, 429), (500, 502)]:
            with self.subTest(status=status):
                post.return_value = Mock(ok=False, status_code=status)
                response = self.request()
                self.assertEqual(response.status_code, expected)
                self.assertNotIn("test-key", response.text)

    @patch("backend.gemini_assistant.requests.post")
    def test_busy_model_uses_stable_fallback(self, post):
        busy = Mock(ok=False, status_code=503, text="temporarily unavailable")
        success = Mock(ok=True, status_code=200)
        success.json.return_value = {"candidates": [{"content": {"parts": [{"text": "Ready"}]}}]}
        post.side_effect = [busy, success]

        response = self.request()

        self.assertEqual(response.json(), {"reply": "Ready"})
        self.assertEqual(post.call_count, 2)
        self.assertIn("gemini-3.5-flash-lite", post.call_args_list[1].args[0])

    @patch("backend.gemini_assistant.requests.post", side_effect=requests.Timeout)
    def test_timeout(self, post):
        self.assertEqual(self.request().status_code, 504)

    @patch("backend.gemini_assistant.requests.post")
    def test_blocked_response(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {"promptFeedback": {"blockReason": "SAFETY"}}
        self.assertEqual(self.request().status_code, 502)

    def test_invalid_messages(self):
        for messages in [[], [{"role": "user", "content": " "}],
                         [{"role": "user", "content": "x" * 4001}],
                         [{"role": "assistant", "content": "Hello"}]]:
            self.assertEqual(self.client.post("/chat", json={"messages": messages}).status_code, 422)

    def test_invalid_language(self):
        response = self.client.post("/chat", json={
            "messages": [{"role": "user", "content": "Hello"}],
            "language": "xx",
        })
        self.assertEqual(response.status_code, 422)

    def test_supported_languages_are_accepted(self):
        supported = ["auto", "en", "te", "hi", "ta", "kn", "ml", "mr", "bn", "gu", "pa", "ur", "or"]
        with patch("backend.main.chat_reply", return_value="OK"):
            for language in supported:
                with self.subTest(language=language):
                    response = self.client.post("/chat", json={
                        "messages": [{"role": "user", "content": "Hello"}],
                        "language": language,
                    })
                    self.assertEqual(response.status_code, 200)

    def test_invalid_assessment_is_rejected(self):
        response = self.client.post("/chat", json={
            "messages": [{"role": "user", "content": "Explain my result"}],
            "assessment": {"risk_category": "Critical", "ensemble_probability": 4},
        })
        self.assertEqual(response.status_code, 422)

    def test_local_frontend_cors(self):
        response = self.client.options("/chat", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")


if __name__ == "__main__":
    unittest.main()
