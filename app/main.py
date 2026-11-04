import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.config import build_llm
from app.conversation import build_messages, classifier_context
from app.crisis.classifier import LLMCrisisClassifier
from app.crisis.detector import CrisisDetector
from app.llm import LLMClient, LLMUnavailable, Message, UnconfiguredLLM
from app.messages import CRISIS_MESSAGE, DISCLAIMER

STATIC_DIR = Path(__file__).parent / "static"

COMPANION_SYSTEM = (
    "You are a warm, calm AI companion helping someone through an urge to return to "
    "nicotine, social media or porn. Use simple techniques (urge surfing, breathing, "
    "distraction). You are an AI, never claim to be human or a therapist, and don't "
    "give medical, legal or relationship advice. Stay on topic. Remember what the "
    "user has already told you in this conversation and don't ask for it again."
)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    # Held by the browser for the current tab only; the server stores nothing.
    history: list[HistoryItem] = Field(default_factory=list, max_length=100)


class ChatResponse(BaseModel):
    crisis: bool
    reply: str


def _event(**fields: str) -> str:
    return json.dumps(fields) + "\n"


def create_app(llm: LLMClient | None = None) -> FastAPI:
    llm = llm or UnconfiguredLLM()
    detector = CrisisDetector(LLMCrisisClassifier(llm))
    app = FastAPI(title="Wavebreak")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/chat/start")
    async def chat_start() -> dict[str, str]:
        return {"disclaimer": DISCLAIMER}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        history = [Message(h.role, h.content) for h in req.history]
        result = await detector.check(req.message, classifier_context(history))
        if result.is_crisis:
            return ChatResponse(crisis=True, reply=CRISIS_MESSAGE)
        try:
            chunks = [c async for c in llm.stream(COMPANION_SYSTEM, build_messages(history, req.message))]
        except LLMUnavailable:
            raise HTTPException(status_code=503, detail="Companion unavailable")
        return ChatResponse(crisis=False, reply="".join(chunks))

    @app.post("/chat/stream")
    async def chat_stream(req: ChatRequest) -> StreamingResponse:
        """Newline-delimited JSON events: crisis, delta (a piece of the reply), or error."""
        history = [Message(h.role, h.content) for h in req.history]

        async def events() -> AsyncIterator[str]:
            result = await detector.check(req.message, classifier_context(history))
            if result.is_crisis:
                yield _event(type="crisis", text=CRISIS_MESSAGE)
                return
            try:
                async for chunk in llm.stream(COMPANION_SYSTEM, build_messages(history, req.message)):
                    yield _event(type="delta", text=chunk)
            except LLMUnavailable:
                yield _event(type="error")

        return StreamingResponse(events(), media_type="application/x-ndjson")

    return app


app = create_app(build_llm())
