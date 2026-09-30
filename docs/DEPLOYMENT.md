# Deploy GeoXAI-Bore

## Recommended architecture

Deploy both services on Render:

- **Frontend:** Render Static Site built from `frontend/`
- **Backend:** Render Web Service built from the repository root

This keeps the current React interface, prediction graphs, movable assistant,
and FastAPI validation. The repository also contains a legacy Streamlit app,
but a Streamlit-only deployment does not serve the current React interface.

## 1. Create the backend web service

Connect the GitHub repository and use these settings:

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Root directory | repository root |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/health` |

Add these environment variables in the Render dashboard:

```text
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Keep the API key in Render's environment settings. Do not commit `.env`.
After the first deployment, copy the public backend URL.

## 2. Create the frontend static site

Create a second service from the same repository with these settings:

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |

Add the backend URL as a build environment variable:

```text
VITE_API_URL=https://your-backend-service.onrender.com
```

Deploy the static site and copy its public URL.

## 3. Allow the hosted frontend

Return to the backend service and add the frontend URL:

```text
CORS_ORIGINS=https://your-frontend-site.onrender.com
```

Use a comma-separated list when more than one hosted frontend must access the
API. Redeploy the backend after changing this value.

## 4. Verify the deployment

1. Open `https://your-backend-service.onrender.com/health` and confirm that it
   returns `{"status":"ok"}`.
2. Open the frontend, run one assessment, and confirm that the score, risk band,
   model comparison, and SHAP drivers appear.
3. Open **AI help**, send a question, test **Read aloud**, and close the assistant
   while it is speaking to confirm playback stops.
4. Test the layout on a phone-sized window and drag the assistant to another
   unobstructed position.

Render free web services can pause after inactivity, so the first prediction or
chat request after a pause can take longer. A paid always-on backend removes that
cold start if the project requires immediate responses.

Official references:

- [Deploy a FastAPI application on Render](https://render.com/docs/deploy-fastapi)
- [Render web services](https://render.com/docs/web-services)
- [Render static sites](https://render.com/docs/static-sites)
- [Render environment variables and secrets](https://render.com/docs/configure-environment-variables)
