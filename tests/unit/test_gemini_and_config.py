import pytest

from app import config
from app.gemini import GeminiLLM
from app.llm import LLMUnavailable, Message, UnconfiguredLLM


class FakeModels:
    def __init__(self, text=None, error=None, chunks=(), stream_error_after=None):
        self.text, self.error, self.calls = text, error, []
        self.chunks, self.stream_error_after = chunks, stream_error_after

    async def generate_content(self, model, contents, config):
        self.calls.append((model, contents, config.system_instruction))
        if self.error:
            raise self.error
        return type("Resp", (), {"text": self.text})()

    async def generate_content_stream(self, model, contents, config):
        self.calls.append((model, contents, config.system_instruction))
        if self.error:
            raise self.error

        async def gen():
            for i, text in enumerate(self.chunks):
                if self.stream_error_after is not None and i == self.stream_error_after:
                    raise RuntimeError("secret-key-xyz")
                yield type("Chunk", (), {"text": text})()

        return gen()


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


async def collect(llm, messages):
    return [c async for c in llm.stream("sys", messages)]


async def test_stream_yields_chunks_and_skips_empty_ones():
    models = FakeModels(chunks=["Hel", "", "lo"])
    llm = GeminiLLM("k", "m1", client=fake_client(models))
    assert await collect(llm, [Message("user", "hi")]) == ["Hel", "lo"]


async def test_stream_sends_history_with_gemini_roles():
    models = FakeModels(chunks=["ok"])
    llm = GeminiLLM("k", "m1", client=fake_client(models))
    await collect(llm, [Message("user", "a"), Message("assistant", "b"), Message("user", "c")])
    _, contents, system = models.calls[0]
    assert [(c.role, c.parts[0].text) for c in contents] == [("user", "a"), ("model", "b"), ("user", "c")]
    assert system == "sys"


async def test_stream_with_no_text_raises_unavailable():
    llm = GeminiLLM("k", "m", client=fake_client(FakeModels(chunks=["", ""])))
    with pytest.raises(LLMUnavailable):
        await collect(llm, [Message("user", "hi")])


async def test_stream_start_error_becomes_unavailable():
    llm = GeminiLLM("k", "m", client=fake_client(FakeModels(error=RuntimeError("boom"))))
    with pytest.raises(LLMUnavailable):
        await collect(llm, [Message("user", "hi")])


async def test_stream_error_midway_becomes_unavailable_without_leaking_details():
    llm = GeminiLLM("k", "m", client=fake_client(FakeModels(chunks=["a", "b"], stream_error_after=1)))
    received = []
    with pytest.raises(LLMUnavailable) as info:
        async for chunk in llm.stream("sys", [Message("user", "hi")]):
            received.append(chunk)
    assert received == ["a"] and "secret-key-xyz" not in str(info.value)


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
