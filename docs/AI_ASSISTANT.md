# Gemini assistant

React has an **AI assistant** button in the lower-right corner. Streamlit has an
**AI Assistant** page in the sidebar. Both support conversational help with
borewell inputs, risk categories, SHAP, maintenance, and CSV uploads.

The assistant is designed for a broad range of users and technical experience. It provides
English and Telugu answers, short practical steps, and electrical safety guidance.
The React assistant also supports microphone input when the browser provides the
Web Speech API and can read every answer aloud. Voice support depends on the
browser, operating system, microphone permission, and installed speech voices.

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
The backend allows local frontend origins on ports 5173 and 4173. If you change
the frontend port, update the allowed origins in `backend/main.py`.

For Streamlit, install the project `requirements.txt` and run `streamlit run app.py`
from the repository root. Its assistant calls Gemini directly from Python;
FastAPI is not required for the Streamlit assistant.

Conversation history is kept in the current browser/Streamlit session and sent
to Gemini with each question (at most the latest nine exchanges and question).
Use **Clear chat** to reset it. Results and datasets are not attached automatically;
share a result in your message if you want the assistant to discuss it.
Provider failures show an error without exposing the API key. Failed React
messages stay in the input for retry. ML predictions remain independent of
Gemini and need the remaining project dependencies.

Backend tests use mocked Gemini responses, with no real key or API usage:

```powershell
python -m pip install httpx
python -m unittest discover -s tests -v
```
