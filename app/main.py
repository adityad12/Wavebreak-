from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import build_llm
from app.crisis.classifier import LLMCrisisClassifier
from app.crisis.detector import CrisisDetector
from app.llm import LLMClient, LLMUnavailable, UnconfiguredLLM
from app.messages import CRISIS_MESSAGE, DISCLAIMER

COMPANION_SYSTEM = (
    "You are a warm, calm AI companion helping someone through an urge to return to "
    "nicotine, social media or porn. Use simple techniques (urge surfing, breathing, "
    "distraction). You are an AI, never claim to be human or a therapist, and don't "
    "give medical, legal or relationship advice. Stay on topic."
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    crisis: bool
    reply: str


def create_app(llm: LLMClient | None = None) -> FastAPI:
    llm = llm or UnconfiguredLLM()
    detector = CrisisDetector(LLMCrisisClassifier(llm))
    app = FastAPI(title="Wavebreak")

    @app.get("/chat/start")
    async def chat_start() -> dict[str, str]:
        return {"disclaimer": DISCLAIMER}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        result = await detector.check(req.message)
        if result.is_crisis:
            return ChatResponse(crisis=True, reply=CRISIS_MESSAGE)
        try:
            reply = await llm.complete(COMPANION_SYSTEM, req.message)
        except LLMUnavailable:
            raise HTTPException(status_code=503, detail="Companion unavailable")
        return ChatResponse(crisis=False, reply=reply)

    return app


app = create_app(build_llm())
