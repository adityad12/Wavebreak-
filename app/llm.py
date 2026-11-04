from typing import Protocol


class LLMUnavailable(Exception):
    pass


class LLMClient(Protocol):
    """Provider adapter, so the model can be swapped later."""

    async def complete(self, system: str, user: str) -> str: ...


class UnconfiguredLLM:
    async def complete(self, system: str, user: str) -> str:
        raise LLMUnavailable("No LLM provider configured")
