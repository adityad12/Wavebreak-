import pytest

from app import config
from app.gemini import GeminiLLM
from app.llm import LLMUnavailable, UnconfiguredLLM


class FakeModels:
    def __init__(self, text=None, error=None):
        self.text, self.error, self.calls = text, error, []

    async def generate_content(self, model, contents, config):
        self.calls.append((model, contents, config.system_instruction))
        if self.error:
            raise self.error
        return type("Resp", (), {"text": self.text})()


def fake_client(models):
    aio = type("Aio", (), {"models": models})()
    return type("Client", (), {"aio": aio})()


async def test_complete_sends_model_system_and_user_and_returns_text():
    models = FakeModels(text="hello")
    llm = GeminiLLM("k", "m1", client=fake_client(models))
    assert await llm.complete("sys", "hi") == "hello"
    assert models.calls == [("m1", "hi", "sys")]


async def test_empty_text_raises_unavailable():
    llm = GeminiLLM("k", "m", client=fake_client(FakeModels(text=None)))
    with pytest.raises(LLMUnavailable):
        await llm.complete("s", "u")


async def test_provider_error_becomes_unavailable_without_leaking_details():
    llm = GeminiLLM("k", "m", client=fake_client(FakeModels(error=RuntimeError("secret-key-xyz"))))
    with pytest.raises(LLMUnavailable) as info:
        await llm.complete("s", "u")
    assert "secret-key-xyz" not in str(info.value)


def test_build_llm_unconfigured_without_key(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert isinstance(config.build_llm(), UnconfiguredLLM)


def test_build_llm_uses_gemini_with_key_and_model_override(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "custom-model")
    llm = config.build_llm()
    assert isinstance(llm, GeminiLLM) and llm._model == "custom-model"


def test_build_llm_default_model(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert config.build_llm()._model == config.DEFAULT_MODEL
