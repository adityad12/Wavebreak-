from app.crisis.classifier import LLMCrisisClassifier
from app.crisis.detector import CrisisDetector
from app.crisis.keywords import keyword_hits
from app.llm import LLMUnavailable


class FakeLLM:
    def __init__(self, answer="NO", fail=False):
        self.answer, self.fail = answer, fail
        self.prompts = []

    async def complete(self, system, user):
        self.prompts.append(user)
        if self.fail:
            raise LLMUnavailable("down")
        return self.answer


def detector(answer="NO", fail=False):
    return CrisisDetector(LLMCrisisClassifier(FakeLLM(answer, fail)))


def test_keywords_match_case_insensitively():
    assert keyword_hits("I want to KILL MYSELF") == ["kill myself"]


def test_keywords_ignore_harmless_text():
    assert keyword_hits("I really want a cigarette") == []


def test_keywords_match_word_variants():
    assert keyword_hits("thinking about suicide, maybe an overdose") == ["suicide", "overdose"]


def test_keywords_require_a_word_boundary():
    assert keyword_hits("a scut myself") == []


async def test_classifier_parses_yes_and_no():
    assert await LLMCrisisClassifier(FakeLLM(" yes.")).is_crisis("x") is True
    assert await LLMCrisisClassifier(FakeLLM("No")).is_crisis("x") is False


async def test_classifier_prompt_is_just_the_message_without_context():
    llm = FakeLLM()
    await LLMCrisisClassifier(llm).is_crisis("hello")
    assert llm.prompts == ["hello"]


async def test_classifier_prompt_includes_context_before_latest_message():
    llm = FakeLLM()
    await LLMCrisisClassifier(llm).is_crisis("yes", ["thinking of ending things"])
    assert "thinking of ending things" in llm.prompts[0]
    assert llm.prompts[0].endswith("Latest message:\nyes")


async def test_keyword_alone_declares_crisis():
    r = await detector("NO").check("I want to kill myself")
    assert r.is_crisis and r.keyword_hits and not r.classifier_flagged


async def test_classifier_alone_declares_crisis():
    r = await detector("YES").check("I just can't see the point anymore")
    assert r.is_crisis and not r.keyword_hits and r.classifier_flagged


async def test_neither_is_not_crisis():
    r = await detector("NO").check("I really want a cigarette")
    assert not r.is_crisis


async def test_classifier_failure_falls_back_to_keywords():
    assert (await detector(fail=True).check("I want to die")).is_crisis
    r = await detector(fail=True).check("I want a cigarette")
    assert not r.is_crisis and r.classifier_failed
