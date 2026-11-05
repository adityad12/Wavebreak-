import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, StringConstraints

from app.config import build_llm
from app.conversation import build_messages, classifier_context, system_with_memory
from app.crisis.classifier import LLMCrisisClassifier
from app.crisis.detector import CrisisDetector
from app.llm import LLMClient, LLMUnavailable, Message, UnconfiguredLLM
from app.memory import MAX_FACT_CHARS, MAX_FACTS, MAX_SUMMARY_CHARS, MemoryUnavailable, MemoryUpdater
from app.messages import CRISIS_MESSAGE, DISCLAIMER

STATIC_DIR = Path(__file__).parent / "static"

COMPANION_SYSTEM = (
    "You are Wavebreak, a warm, calm AI companion helping someone through an urge to "
    "return to nicotine, social media or porn. Use simple techniques (urge surfing, "
    "breathing, distraction). You are an AI, never claim to be human or a therapist, and "
    "don't give medical, legal or relationship advice. Stay on topic. Remember what the "
    "user has already told you in this conversation and don't ask for it again.\n\n"
    "Identity: you are Wavebreak. Never introduce yourself as Gemini, Google's assistant or "
    "a Google model. If asked who built you or what model you run on, say you're Wavebreak, "
    "an AI companion, and that you don't have details about the technology behind you. "
    "Never claim to be human."
)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


Fact = Annotated[str, StringConstraints(min_length=1, max_length=MAX_FACT_CHARS)]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    # All of this is held by the browser for the current tab only; the server stores nothing.
    history: list[HistoryItem] = Field(default_factory=list, max_length=100)
    summary: str = Field(default="", max_length=MAX_SUMMARY_CHARS)
    facts: list[Fact] = Field(default_factory=list, max_length=MAX_FACTS)


class ChatResponse(BaseModel):
    crisis: bool
    reply: str


class MemoryRequest(BaseModel):
    summary: str = Field(default="", max_length=MAX_SUMMARY_CHARS)
    facts: list[Fact] = Field(default_factory=list, max_length=MAX_FACTS)
    messages: list[HistoryItem] = Field(min_length=1, max_length=100)


class MemoryResponse(BaseModel):
    summary: str
    facts: list[str]


def _event(**fields: str) -> str:
    return json.dumps(fields) + "\n"


def create_app(llm: LLMClient | None = None) -> FastAPI:
    llm = llm or UnconfiguredLLM()
    detector = CrisisDetector(LLMCrisisClassifier(llm))
    memory = MemoryUpdater(llm)
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
        result = await detector.check(req.message, classifier_context(history, req.summary, req.facts))
        if result.is_crisis:
            return ChatResponse(crisis=True, reply=CRISIS_MESSAGE)
        system = system_with_memory(COMPANION_SYSTEM, req.summary, req.facts)
        try:
            chunks = [c async for c in llm.stream(system, build_messages(history, req.message))]
        except LLMUnavailable:
            raise HTTPException(status_code=503, detail="Companion unavailable")
        return ChatResponse(crisis=False, reply="".join(chunks))

    @app.post("/chat/memory", response_model=MemoryResponse)
    async def chat_memory(req: MemoryRequest) -> MemoryResponse:
        """Fold old messages into the summary and notes. Stores nothing; the page keeps the result."""
        messages = [Message(m.role, m.content) for m in req.messages]
        try:
            state = await memory.update(req.summary, list(req.facts), messages)
        except MemoryUnavailable:
            raise HTTPException(status_code=503, detail="Memory update unavailable")
        return MemoryResponse(summary=state.summary, facts=state.facts)

    @app.post("/chat/stream")
    async def chat_stream(req: ChatRequest) -> StreamingResponse:
        """Newline-delimited JSON events: crisis, delta (a piece of the reply), or error."""
        history = [Message(h.role, h.content) for h in req.history]

        async def events() -> AsyncIterator[str]:
            result = await detector.check(req.message, classifier_context(history, req.summary, req.facts))
            if result.is_crisis:
                yield _event(type="crisis", text=CRISIS_MESSAGE)
                return
            system = system_with_memory(COMPANION_SYSTEM, req.summary, req.facts)
            try:
                async for chunk in llm.stream(system, build_messages(history, req.message)):
                    yield _event(type="delta", text=chunk)
            except LLMUnavailable:
                yield _event(type="error")

        return StreamingResponse(events(), media_type="application/x-ndjson")

    return app


app = create_app(build_llm())
