from google import genai
from google.genai import types

from app.llm import LLMUnavailable


class GeminiLLM:
    """LLMClient backed by the Gemini API."""

    def __init__(self, api_key: str, model: str, client: genai.Client | None = None):
        self._client = client or genai.Client(api_key=api_key)
        self._model = model

    async def complete(self, system: str, user: str) -> str:
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=user,
                config=types.GenerateContentConfig(system_instruction=system),
            )
        except Exception as exc:
            raise LLMUnavailable(f"Gemini request failed: {type(exc).__name__}") from exc
        text = response.text
        if not text:
            # e.g. blocked by Gemini's own safety filters
            raise LLMUnavailable("Gemini returned no text")
        return text
