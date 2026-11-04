from app.llm import Message

MAX_HISTORY = 20  # most recent messages sent to the model
CLASSIFIER_CONTEXT_USER_MESSAGES = 3


def build_messages(history: list[Message], message: str) -> list[Message]:
    """The recent history plus the new user message, ready to send to the model."""
    recent = history[-MAX_HISTORY:]
    while recent and recent[0].role != "user":
        recent = recent[1:]  # the model's turn must not come first
    return [*recent, Message("user", message)]


def classifier_context(history: list[Message]) -> list[str]:
    """Recent user messages, so the crisis check can read the latest one in context."""
    user_texts = [m.content for m in history if m.role == "user"]
    return user_texts[-CLASSIFIER_CONTEXT_USER_MESSAGES:]
