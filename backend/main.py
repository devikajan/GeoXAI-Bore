from fastapi import FastAPI

from backend.schemas import BorewellInput
from backend.prediction import predict_borewell
from backend.explain import explain_borewell


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "GeoXAI-Bore Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict")
def predict(data: BorewellInput):

    result = predict_borewell(
        data.model_dump()
    )

    return result


@app.post("/explain")
def explain(data: BorewellInput):

    result = explain_borewell(
        data.model_dump()
    )

    return {
        "top_features": result[:5]
    }