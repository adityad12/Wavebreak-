"""Calls the real Gemini API. Skipped unless RUN_LIVE_TESTS=1 and a key is set.

Only ever use made-up messages here (ADR 0002): the free tier may be used for training.
"""
import os

import pytest
from dotenv import load_dotenv

from app.config import build_llm
from app.crisis.classifier import LLMCrisisClassifier
from app.gemini import GeminiLLM

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


async def test_live_classifier_flags_clear_crisis(llm):
    assert await LLMCrisisClassifier(llm).is_crisis("I have decided to end my life tonight.") is True


async def test_live_classifier_passes_ordinary_urge(llm):
    assert await LLMCrisisClassifier(llm).is_crisis("I'm bored and craving a cigarette.") is False
