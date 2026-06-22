"""Single inference entry point for the Groq zero-shot baseline model.
Used by both app.py and groq_baseline.py so there is exactly one place
that knows how to turn text into a label via Groq.
"""

import os

from dotenv import load_dotenv
from groq import Groq

import config

load_dotenv()

SYSTEM_PROMPT = """
You are classifying posts and comments from r/CryptoCurrency by quality of take.

signal: The post backs its claim with real, checkable evidence - on-chain data, a named mechanism, or a concrete historical comparison. Direction (bullish/bearish) does not matter.
Example: "9 UMA whale wallets control 53.1% of voting power. Same wallets fund $12.5M Polymarket side-bets on markets they resolve."

hype: A bullish claim with no real evidence behind it - bare price targets, FOMO, "to the moon."
Example: "SOL is so back. This is the floor, screenshot this. LFG"

panic: A bearish claim with no real evidence behind it - doom, "scam," nothing backing it up.
Example: "It's over. Retail gets dumped on again while insiders cash out. The whole space is a rigged casino."

Respond with ONLY one of these exact words: signal, hype, panic
Do not explain your reasoning.
"""

_client = None


def classify_with_groq(client, system_prompt: str, text: str) -> str | None:
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify this post:\n\n{text}"},
        ],
        temperature=0,
        max_tokens=20,
    )
    raw = response.choices[0].message.content.strip().lower()
    for label in sorted(config.LABEL_MAP, key=len, reverse=True):
        if raw == label or label in raw:
            return label
    return None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=api_key)
    return _client


def classify(text: str) -> dict:
    client = _get_client()
    label = classify_with_groq(client, SYSTEM_PROMPT, text)
    if label is None:
        raise RuntimeError("Groq returned an unparseable response.")
    return {"label": label}
