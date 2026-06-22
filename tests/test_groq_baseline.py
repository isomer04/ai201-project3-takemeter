from groq_baseline import classify_with_groq, SYSTEM_PROMPT


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


def test_classify_with_groq_matches_exact_label():
    client = FakeClient("signal")
    result = classify_with_groq(client, SYSTEM_PROMPT, "some post")
    assert result == "signal"


def test_classify_with_groq_returns_none_for_unmatched_output():
    client = FakeClient("not a real label")
    result = classify_with_groq(client, SYSTEM_PROMPT, "some post")
    assert result is None
