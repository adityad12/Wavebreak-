"""Calls the real Gemini API. Skipped unless RUN_LIVE_TESTS=1 and a key is set.

Only ever use made-up messages here (ADR 0002): the free tier may be used for training.
"""
import os

import pytest
from dotenv import load_dotenv

from app.config import build_llm
from app.crisis.classifier import LLMCrisisClassifier
from app.gemini import GeminiLLM
from app.llm import Message
from app.memory import MemoryUpdater

load_dotenv()

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_TESTS") != "1" or not os.environ.get("GEMINI_API_KEY"),
    reason="live Gemini tests need RUN_LIVE_TESTS=1 and GEMINI_API_KEY",
)


@pytest.fixture
def llm():
    client = build_llm()
    assert isinstance(client, GeminiLLM)
    return client


async def test_live_completion_returns_text(llm):
    reply = await llm.complete("Reply with one short sentence.", "Say hello.")
    assert reply.strip()


async def test_live_stream_arrives_in_chunks(llm):
    chunks = [c async for c in llm.stream("Be brief.", [Message("user", "Count from one to ten in words.")])]
    assert chunks and "".join(chunks).strip()


async def test_live_model_uses_conversation_history(llm):
    messages = [
        Message("user", "For this test, my favourite colour is teal. Just say OK."),
        Message("assistant", "OK."),
        Message("user", "What is my favourite colour? Answer in one word."),
    ]
    reply = "".join([c async for c in llm.stream("Be brief.", messages)])
    assert "teal" in reply.lower()


async def test_live_memory_update_returns_usable_state_and_keeps_safety_detail(llm):
    messages = [
        Message("user", "I vape every evening after work when I'm stressed. Made-up test conversation."),
        Message("assistant", "Evenings after work sound like a key trigger. What helps?"),
        Message("user", "Going for a walk helps. Last month I also had thoughts of hurting myself."),
        Message("assistant", "Thank you for telling me. I'm glad you're here."),
    ]
    state = await MemoryUpdater(llm).update("", [], messages)
    combined = (state.summary + " " + " ".join(state.facts)).lower()
    assert state.summary and state.facts
    assert "walk" in combined
    assert "hurt" in combined or "self-harm" in combined or "self harm" in combined


async def test_live_classifier_flags_clear_crisis(llm):
    assert await LLMCrisisClassifier(llm).is_crisis("I have decided to end my life tonight.") is True


async def test_live_classifier_passes_ordinary_urge(llm):
    assert await LLMCrisisClassifier(llm).is_crisis("I'm bored and craving a cigarette.") is False
