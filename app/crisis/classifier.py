from app.llm import LLMClient

_SYSTEM = (
    "You are a safety classifier for a recovery support chat. Decide whether the "
    "user's latest message shows signs of crisis: suicidal thoughts, self-harm, "
    "overdose risk, or dangerous withdrawal symptoms. Earlier messages may be shown "
    "for context, and a short reply can only be understood in light of them. "
    "Answer with exactly one word: YES or NO."
)


class LLMCrisisClassifier:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def is_crisis(self, text: str, context: list[str] | None = None) -> bool:
        prompt = text
        if context:
            earlier = "\n".join(f"- {c}" for c in context)
            prompt = f"Earlier context:\n{earlier}\n\nLatest message:\n{text}"
        answer = await self._llm.complete(_SYSTEM, prompt)
        return answer.strip().upper().startswith("YES")
