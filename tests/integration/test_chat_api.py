from fastapi.testclient import TestClient

from app.llm import LLMUnavailable
from app.main import create_app
from app.messages import CRISIS_MESSAGE


class FakeLLM:
    """Answers the classifier prompt with `verdict` and the Companion with `reply`."""

    def __init__(self, verdict="NO", reply="Try a slow breath.", fail=False):
        self.verdict, self.reply, self.fail = verdict, reply, fail
        self.companion_calls = 0

    async def complete(self, system, user):
        if self.fail:
            raise LLMUnavailable("down")
        if "safety classifier" in system:
            return self.verdict
        self.companion_calls += 1
        return self.reply


def test_crisis_keyword_returns_fixed_message_and_skips_companion():
    llm = FakeLLM()
    client = TestClient(create_app(llm))
    body = client.post("/chat", json={"message": "thinking about suicide"}).json()
    assert body == {"crisis": True, "reply": CRISIS_MESSAGE}
    assert llm.companion_calls == 0


def test_crisis_from_classifier_returns_fixed_message():
    client = TestClient(create_app(FakeLLM(verdict="YES")))
    body = client.post("/chat", json={"message": "nothing matters anymore"}).json()
    assert body == {"crisis": True, "reply": CRISIS_MESSAGE}


def test_safe_message_gets_companion_reply():
    client = TestClient(create_app(FakeLLM()))
    body = client.post("/chat", json={"message": "craving a vape"}).json()
    assert body == {"crisis": False, "reply": "Try a slow breath."}


def test_unconfigured_llm_gives_503_for_safe_message():
    client = TestClient(create_app())
    assert client.post("/chat", json={"message": "craving a vape"}).status_code == 503


def test_unconfigured_llm_still_catches_keyword_crisis():
    client = TestClient(create_app())
    body = client.post("/chat", json={"message": "I want to die"}).json()
    assert body["crisis"] is True


def test_empty_and_oversized_messages_rejected():
    client = TestClient(create_app(FakeLLM()))
    assert client.post("/chat", json={"message": ""}).status_code == 422
    assert client.post("/chat", json={"message": "x" * 4001}).status_code == 422


def test_index_serves_chat_page_with_closable_disclaimer():
    response = TestClient(create_app()).get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="disclaimer"' in response.text and 'id="close"' in response.text


def test_disclaimer_endpoint():
    disclaimer = TestClient(create_app()).get("/chat/start").json()["disclaimer"]
    assert "isn't professional advice" in disclaimer
