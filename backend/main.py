from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from backend.gemini_assistant import AssistantError, chat_reply

from backend.schemas import BorewellInput


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:4173", "http://127.0.0.1:4173"],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be blank")
        return value.strip()


class RiskDriver(BaseModel):
    feature: str = Field(min_length=1, max_length=100)
    shap_value: float
    impact: str = Field(min_length=1, max_length=200)


class AssessmentContext(BaseModel):
    risk_category: Literal["Low", "Medium", "High"]
    ensemble_probability: float = Field(ge=0, le=1)
    top_features: list[RiskDriver] = Field(default_factory=list, max_length=5)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)
    language: Literal["auto", "en", "te"] = "auto"
    simple_mode: bool = True
    assessment: AssessmentContext | None = None

    @field_validator("messages")
    @classmethod
    def conversation_order(cls, value):
        if any(message.role != ("user" if index % 2 == 0 else "assistant")
               for index, message in enumerate(value)) or value[-1].role != "user":
            raise ValueError("Conversation must alternate user and assistant and end with a user message")
        return value


@app.post("/chat")
def chat(data: ChatRequest):
    try:
        return {"reply": chat_reply(
            [message.model_dump() for message in data.messages],
            language=data.language,
            simple_mode=data.simple_mode,
            assessment=data.assessment.model_dump() if data.assessment else None,
        )}
    except AssistantError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from None


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
    from backend.prediction import predict_borewell

    result = predict_borewell(
        data.model_dump()
    )

    return result


@app.post("/explain")
def explain(data: BorewellInput):
    from backend.explain import explain_borewell

    result = explain_borewell(
        data.model_dump()
    )

    return {
        "top_features": result[:5]
    }
