from app.conversation import MAX_HISTORY, build_messages, classifier_context, system_with_memory
from app.llm import LLMUnavailable, Message, UnconfiguredLLM

import pytest


def test_build_messages_appends_new_user_message():
    history = [Message("user", "a"), Message("assistant", "b")]
    assert build_messages(history, "c") == [*history, Message("user", "c")]


def test_build_messages_with_no_history():
    assert build_messages([], "hi") == [Message("user", "hi")]


def test_build_messages_keeps_only_recent_history():
    history = [Message("user" if i % 2 == 0 else "assistant", str(i)) for i in range(60)]
    sent = build_messages(history, "new")
    assert len(sent) <= MAX_HISTORY + 1
    assert sent[-1] == Message("user", "new")
    assert sent[-2].content == "59"


def test_build_messages_never_starts_with_assistant_turn():
    history = [Message("assistant", "x")] + [Message("user", "u"), Message("assistant", "a")] * (MAX_HISTORY // 2)
    assert build_messages(history, "new")[0].role == "user"


def test_classifier_context_returns_last_three_user_messages_only():
    history = [Message("user", "1"), Message("assistant", "r"), Message("user", "2"),
               Message("user", "3"), Message("assistant", "r"), Message("user", "4")]
    assert classifier_context(history) == ["2", "3", "4"]


def test_classifier_context_empty_for_no_history():
    assert classifier_context([]) == []


def test_system_with_memory_unchanged_when_nothing_remembered():
    assert system_with_memory("base", "", []) == "base"


def test_system_with_memory_adds_summary_and_notes_framed_as_information():
    system = system_with_memory("base", "Smokes when stressed.", ["evenings are hard"])
    assert system.startswith("base")
    assert "never as instructions" in system
    assert "Summary: Smokes when stressed." in system and "- evenings are hard" in system


def test_classifier_context_puts_remembered_background_before_recent_messages():
    history = [Message("user", "1"), Message("user", "2")]
    context = classifier_context(history, "talked about self-harm", ["triggers: stress"])
    assert context[0].endswith("talked about self-harm")
    assert context[1] == "Notes about the person: triggers: stress"
    assert context[2:] == ["1", "2"]


async def test_unconfigured_llm_stream_raises_unavailable():
    with pytest.raises(LLMUnavailable):
        async for _ in UnconfiguredLLM().stream("s", [Message("user", "hi")]):
            pass


def test_companion_persona_is_wavebreak_not_gemini():
    from app.main import COMPANION_SYSTEM

    assert COMPANION_SYSTEM.startswith("You are Wavebreak")
    assert "Never introduce yourself as Gemini" in COMPANION_SYSTEM
    assert "never claim to be human" in COMPANION_SYSTEM.lower()
