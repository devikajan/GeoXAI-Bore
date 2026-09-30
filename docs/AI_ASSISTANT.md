# Gemini assistant

The React interface has a movable **AI help** button. It supports conversational
help with borewell inputs, risk categories, SHAP explanations, maintenance, and
the latest assessment result.

The assistant is designed for a broad range of users and technical experience. It provides
automatic same-language replies and direct selection for English, Telugu, Hindi,
Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Urdu, and Odia,
along with short practical steps and electrical safety guidance.
The assistant also supports microphone input when the browser provides the
Web Speech API and can read every answer aloud. Voice support depends on the
browser, operating system, microphone permission, and installed speech voices.
Closing the assistant stops any active speech playback.

Copy `.env.example` to `.env` in the repository root and fill in:

```text
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Choose another supported Gemini model by changing `GEMINI_MODEL`. Restart the
Python server after changing the file. The key stays on the server; `.env` is
ignored by Git. Never put this key in a `VITE_` environment variable.

For the React chatbot, start the backend from the repository root:

```powershell
python -m pip install fastapi uvicorn requests python-dotenv
python -m uvicorn backend.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Chat requests go to `POST /chat` on port 8000.
The backend allows local frontend origins on ports 5173 and 4173. Hosted frontend
origins can be supplied through the `CORS_ORIGINS` environment variable.

Conversation history is kept in the current browser session and sent to Gemini
with each question. Use **Clear chat** to reset it. The latest assessment result
is included automatically so the assistant can explain its score and strongest
risk drivers.
Provider failures show an error without exposing the API key. Failed React
messages stay in the input for retry. ML predictions remain independent of
Gemini and need the remaining project dependencies.

Backend tests use mocked Gemini responses, with no real key or API usage:

```powershell
python -m pip install httpx
python -m unittest discover -s tests -v
```

For production hosting, follow the [deployment guide](DEPLOYMENT.md).
