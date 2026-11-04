from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.llm import LLMUnavailable, Message


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

    async def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]:
        contents = [
            types.Content(
                role="user" if m.role == "user" else "model",
                parts=[types.Part(text=m.content)],
            )
            for m in messages
        ]
        produced = False
        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system),
            )
            async for chunk in stream:
                if chunk.text:
                    produced = True
                    yield chunk.text
        except Exception as exc:
            raise LLMUnavailable(f"Gemini request failed: {type(exc).__name__}") from exc
        if not produced:
            raise LLMUnavailable("Gemini returned no text")
