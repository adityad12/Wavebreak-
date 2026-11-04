from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal, Protocol


class LLMUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant"]
    content: str


class LLMClient(Protocol):
    """Provider adapter, so the model can be swapped later."""

    async def complete(self, system: str, user: str) -> str: ...

    def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]: ...


class UnconfiguredLLM:
    async def complete(self, system: str, user: str) -> str:
        raise LLMUnavailable("No LLM provider configured")

    async def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]:
        raise LLMUnavailable("No LLM provider configured")
        yield  # pragma: no cover  (makes this an async generator)
