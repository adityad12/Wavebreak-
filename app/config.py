import os

from dotenv import load_dotenv

from app.gemini import GeminiLLM
from app.llm import LLMClient, UnconfiguredLLM

DEFAULT_MODEL = "gemini-3.5-flash-lite"


def build_llm() -> LLMClient:
    """Pick the LLM from the environment (.env is loaded if present)."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return UnconfiguredLLM()
    return GeminiLLM(api_key, os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
