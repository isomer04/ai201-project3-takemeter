import pytest

import groq_classifier


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, reply_text):
        self._reply_text = reply_text

    def create(self, **kwargs):
        return FakeResponse(self._reply_text)


class FakeChat:
    def __init__(self, reply_text):
        self.completions = FakeCompletions(reply_text)


class FakeClient:
    def __init__(self, reply_text):
        self.chat = FakeChat(reply_text)


@pytest.fixture(autouse=True)
def reset_client_cache():
    groq_classifier._client = None
    yield
    groq_classifier._client = None


def test_classify_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        groq_classifier.classify("some post")


def test_classify_returns_label_on_success(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    groq_classifier._client = FakeClient("signal")
    result = groq_classifier.classify("some post")
    assert result == {"label": "signal"}


def test_classify_raises_on_unparseable_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    groq_classifier._client = FakeClient("not a real label")
    with pytest.raises(RuntimeError):
        groq_classifier.classify("some post")
