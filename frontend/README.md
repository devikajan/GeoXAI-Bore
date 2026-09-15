# GeoXAI-Bore Frontend

The GeoXAI-Bore frontend is a React + TypeScript application for borewell failure-risk assessment. It supports both individual borewell assessment and CSV batch prediction through the FastAPI backend.

## Features

- Single-borewell prediction using all 13 model inputs
- Ensemble probability from Random Forest and XGBoost
- SHAP-based feature drivers
- Risk category and recommended action
- CSV upload for scoring borewells from other states
- Batch risk summary and downloadable prediction results
- Fleet dashboard for scored datasets
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

## Dashboard

After a CSV is scored, the dashboard becomes active and provides:

- Sites in view, average failure probability, high-risk share, and total rows scored
- Risk distribution bars for Low, Medium, and High predictions
- Risk filtering for focused review
- State coverage and state filtering when the upload includes a `State` column
- A priority table showing the highest predicted-risk sites first

The dashboard currently summarizes the uploaded batch in the browser. It does not represent a persistent fleet or the complete Andhra Pradesh dataset because the FastAPI backend does not yet expose analytics or database endpoints. A future fleet dashboard should add backend endpoints for persisted records, server-side filters, and historical trends.

## Cross-State Dataset Upload

The current model was trained using the Andhra Pradesh borewell dataset. The upload feature allows the same trained model to score datasets from other states, provided each row uses the same feature definitions and units. This is inference on a new dataset; it does not retrain or recalibrate the model for that state.

The uploaded CSV must contain these columns:

```text
Borewell_Depth_ft
Water_Table_Depth_ft
Pump_Age_years
Daily_Usage_hours
Soil_Type
Region_Type
Annual_Rainfall_mm
Maintenance_Frequency_per_year
Motor_Temperature_C
Vibration_Level_mms
Voltage_Fluctuation_pct
Water_Yield_LPH
Casing_Pipe_Age_years
```

Additional columns are allowed. For example, `State`, `District`, `Borewell_ID`, latitude, and longitude can be included and will be preserved in the downloaded results.

The upload process:

1. Reads and validates the CSV in the browser.
2. Checks that all required columns are present.
3. Converts numeric model fields and validates each row.
4. Sends each row to the backend `/predict` endpoint.
5. Adds `Predicted_Risk_Category` and `Failure_Probability_6mo` to the downloadable CSV.

### Important model limitation

Predictions for another state should be treated as exploratory until the model is validated with local historical failure data. Differences in geology, rainfall, groundwater behavior, sensor calibration, soil labels, and operating practices can create dataset shift. A future backend version should support state-specific retraining, calibration, and validation before operational use.

## Development

From the repository root, install frontend dependencies and start Vite:

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses `http://localhost:8000` as the default API URL. To use another backend URL, create `frontend/.env`:

```text
VITE_API_URL=http://localhost:8000
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
