# GeoXAI-Bore Frontend

The GeoXAI-Bore frontend is a React + TypeScript application for individual borewell failure-risk assessment through the FastAPI backend.

## Features

- Single-borewell prediction using all 13 model inputs
- Ensemble probability from Random Forest and XGBoost
- Risk-score, model-comparison, and SHAP contribution graphs
- SHAP-based feature drivers
- Plain-language result explanation with 12 selectable languages
- Risk category and recommended action
- Movable multilingual Gemini assistant grounded in the latest prediction
- Microphone input and read-aloud responses where the browser supports them
- Responsive desktop and mobile layout

## AI Assistant

Open **AI help** to ask questions about the model inputs, risk score, SHAP drivers,
or practical next steps. When an assessment is available, its result is supplied
to the assistant automatically.

The API key is used only by the backend. Never put it in `frontend/.env`, browser code, or a CSV file. Copy the root `.env.example` to `.env` and set:

```text
GEMINI_API_KEY=your_server_side_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

The assistant endpoint is `POST /chat`. If the key is missing or the provider is
unavailable, ML prediction still works and the assistant displays the server
error without exposing the key.

## Development

From the repository root, install frontend dependencies and start Vite:

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses `http://127.0.0.1:8000` as the default API URL. To use another backend URL, create `frontend/.env`:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Start the backend from the repository root:

```powershell
uvicorn backend.main:app --reload
```

The backend must have its Python dependencies installed from the repository `requirements.txt` file. The backend also needs CORS enabled for the frontend development origin.

## Commands

```powershell
npm run dev       # Start the development server
npm run build     # Type-check and create a production build
npm run lint      # Run Oxlint
npm run preview   # Preview the production build
```

See the repository [deployment guide](../docs/DEPLOYMENT.md) for production setup.
