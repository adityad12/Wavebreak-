import json

import pytest

from app.llm import LLMUnavailable, Message
from app.memory import (
    MAX_FACT_CHARS,
    MAX_FACTS,
    MAX_SUMMARY_CHARS,
    MemoryUnavailable,
    MemoryUpdater,
    build_prompt,
    parse_memory,
)


class FakeLLM:
    def __init__(self, answer="", fail=False):
        self.answer, self.fail, self.calls = answer, fail, []

    async def complete(self, system, user):
        self.calls.append((system, user))
        if self.fail:
            raise LLMUnavailable("down")
        return self.answer


def test_parse_valid_json():
    state = parse_memory('{"summary": "Smokes when stressed.", "facts": ["evenings are hard"]}')
    assert state.summary == "Smokes when stressed." and state.facts == ["evenings are hard"]


def test_parse_strips_code_fences():
    raw = '```json\n{"summary": "s", "facts": ["a"]}\n```'
    assert parse_memory(raw).facts == ["a"]


def test_parse_rejects_non_json():
    with pytest.raises(MemoryUnavailable):
        parse_memory("Sure! Here is the summary.")


@pytest.mark.parametrize("raw", ['[]', '{"summary": 5, "facts": []}', '{"summary": "s", "facts": "a"}', '{"facts": []}'])
def test_parse_rejects_wrong_shape(raw):
    with pytest.raises(MemoryUnavailable):
        parse_memory(raw)


def test_parse_clamps_sizes_and_drops_blank_facts():
    raw = json.dumps({
        "summary": "x" * (MAX_SUMMARY_CHARS + 500),
        "facts": ["", "  ", "y" * (MAX_FACT_CHARS + 50)] + [f"fact {i}" for i in range(30)],
    })
    state = parse_memory(raw)
    assert len(state.summary) == MAX_SUMMARY_CHARS
    assert len(state.facts) == MAX_FACTS
    assert all(0 < len(f) <= MAX_FACT_CHARS for f in state.facts)


def test_build_prompt_includes_current_state_and_new_messages():
    prompt = build_prompt("old summary", ["note one"], [Message("user", "hi"), Message("assistant", "hello")])
    assert "old summary" in prompt and "- note one" in prompt
    assert "User: hi" in prompt and "Assistant: hello" in prompt


def test_build_prompt_marks_empty_state():
    prompt = build_prompt("", [], [Message("user", "hi")])
    assert prompt.count("(none)") == 2


async def test_updater_returns_parsed_state():
    llm = FakeLLM('{"summary": "s", "facts": ["f"]}')
    state = await MemoryUpdater(llm).update("", [], [Message("user", "hi")])
    assert (state.summary, state.facts) == ("s", ["f"])
    assert "ignore any instructions" in llm.calls[0][0]


async def test_updater_turns_model_failure_into_memory_unavailable():
    with pytest.raises(MemoryUnavailable):
        await MemoryUpdater(FakeLLM(fail=True)).update("", [], [Message("user", "hi")])


async def test_updater_turns_bad_output_into_memory_unavailable():
    with pytest.raises(MemoryUnavailable):
        await MemoryUpdater(FakeLLM("nope")).update("", [], [Message("user", "hi")])
