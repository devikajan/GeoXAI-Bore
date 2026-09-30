"""Server-side Gemini assistant shared by FastAPI and Streamlit."""
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SYSTEM_PROMPT = """You are the GeoXAI-Bore assistant. Help users understand borewell
inputs, groundwater, maintenance, risk categories, SHAP, CSV uploads, and this app.
The React app uses a Random Forest and XGBoost ensemble with SHAP explanations.
Do not invent measurements, predictions, dataset access, or actions you have taken.
Only interpret a site-specific prediction when supplied by the user. SHAP explains
model influence, not physical causation. Explain uncertainty and suggest field
inspection when appropriate. Reply concisely in the user's language, using plain text."""


class AssistantError(Exception):
    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.status_code = status_code


def chat_reply(messages):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key in {"replace_with_your_server_side_key", "your_key"}:
        raise AssistantError("AI assistant is not configured. Set GEMINI_API_KEY in the root .env file and restart the server.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise AssistantError("GEMINI_MODEL configuration is invalid.")
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "model" if item["role"] == "assistant" else "user",
                      "parts": [{"text": item["content"]}]} for item in messages],
        "generationConfig": {
            "maxOutputTokens": 2048,
            "thinkingConfig": {"thinkingLevel": "low"},
        },
    }
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": key}, json=payload, timeout=(5, 55),
        )
    except requests.Timeout:
        raise AssistantError("Gemini took too long to respond. Please try again.", 504) from None
    except requests.RequestException:
        raise AssistantError("Unable to connect to Gemini. Please try again.") from None
    if response.status_code in (401, 403):
        raise AssistantError("Gemini rejected the API key. Check the backend key and its permissions.")
    if response.status_code == 429:
        raise AssistantError("Gemini usage limit reached. Please try again later.", 429)
    if not response.ok:
        raise AssistantError("Gemini request failed. Check GEMINI_MODEL and your API configuration.", 502)
    try:
        parts = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
        reply = "\n".join(part["text"] for part in parts if part.get("text") and not part.get("thought")).strip()
    except (ValueError, IndexError, TypeError, KeyError):
        raise AssistantError("Gemini returned an unreadable response. Please try again.", 502) from None
    if not reply:
        raise AssistantError("Gemini could not answer this request. Try rephrasing your question.", 502)
    return reply
