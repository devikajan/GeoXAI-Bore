# GeoXAI-Bore Frontend

The GeoXAI-Bore frontend is a React + TypeScript application for individual borewell failure-risk assessment through the FastAPI backend.

## Features

- Single-borewell prediction using all 13 model inputs
- Ensemble probability from Random Forest and XGBoost
- Risk-score, model-comparison, and SHAP contribution graphs
- SHAP-based feature drivers
- Risk category and recommended action
- On-demand GenAI field brief grounded in each prediction
- Responsive desktop and mobile layout

## GenAI Field Brief

After running a single-borewell assessment, select **Generate field brief** to ask the backend's configured Gemini model for a concise interpretation. The brief contains an assessment, evidence from the supplied SHAP drivers and measurements, and a practical next step.

The API key is used only by the backend. Never put it in `frontend/.env`, browser code, or a CSV file. Copy the root `.env.example` to `.env` and set:

```text
GEMINI_API_KEY=your_server_side_key
GEMINI_MODEL=gemini-2.0-flash
```

The GenAI endpoint is `POST /genai/explanation`. If the key is missing or the provider is unavailable, the normal ML prediction still works and the frontend displays the configuration error. The generated text is advisory and grounded only in the supplied prediction; it is not a replacement for model validation or field inspection.

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
