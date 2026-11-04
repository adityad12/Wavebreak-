from app.llm import LLMClient

_SYSTEM = (
    "You are a safety classifier for a recovery support chat. Decide whether the "
    "user's message shows signs of crisis: suicidal thoughts, self-harm, overdose "
    "risk, or dangerous withdrawal symptoms. Answer with exactly one word: YES or NO."
)


class LLMCrisisClassifier:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def is_crisis(self, text: str) -> bool:
        answer = await self._llm.complete(_SYSTEM, text)
        return answer.strip().upper().startswith("YES")
