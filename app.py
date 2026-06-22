"""Gradio demo for TakeMeter. Run locally with `python app.py`, or deploy
this file + requirements.txt directly as a Hugging Face Space."""

import gradio as gr

import config
import groq_classifier
from classifier import TakeClassifier

_classifier = None

LABEL_COLORS = {
    "signal": "#22c55e",
    "hype": "#f59e0b",
    "panic": "#ef4444",
}

LABEL_DESCRIPTIONS = {
    "signal": "backed by evidence",
    "hype": "bullish, no evidence",
    "panic": "bearish, no evidence",
}

BUTTON_COLOR = "#3b82f6"


def _get_classifier() -> TakeClassifier:
    # Lazy-loaded so importing this module (e.g. for tests) doesn't trigger
    # a model download.
    global _classifier
    if _classifier is None:
        _classifier = TakeClassifier.from_pretrained()
    return _classifier


def _render_result_card(label: str, confidence: float | None = None) -> str:
    color = LABEL_COLORS[label]
    description = LABEL_DESCRIPTIONS[label]
    confidence_span = (
        f'<span style="color:#8a8f98;font-weight:400;font-size:13px">'
        f"{confidence:.0%} confidence</span>"
        if confidence is not None
        else ""
    )
    return (
        f'<div style="border-left:4px solid {color};border-radius:0 6px 6px 0;'
        'padding:12px 16px;background:#1c2129;font-family:sans-serif">'
        f'<div style="font-size:16px;font-weight:700;color:{color}">'
        f"{label.upper()} {confidence_span}</div>"
        f'<div style="font-size:13px;color:#8a8f98;margin-top:4px">{description}</div>'
        "</div>"
    )


def _render_error_card(message: str) -> str:
    return (
        '<div style="border-left:4px solid #ef4444;border-radius:0 6px 6px 0;'
        'padding:12px 16px;background:#1c2129;color:#8a8f98;font-family:sans-serif">'
        f"{message}"
        "</div>"
    )


def predict(text: str) -> str:
    if not text or not text.strip():
        return ""
    result = _get_classifier().classify(text)
    return _render_result_card(result["label"], result["confidence"])


def predict_groq(text: str) -> str:
    if not text or not text.strip():
        return ""
    try:
        result = groq_classifier.classify(text)
    except RuntimeError as exc:
        return _render_error_card(str(exc))
    return _render_result_card(result["label"])


def _render_legend(caption: str) -> str:
    rows = "".join(
        f'<div style="font-size:13px;margin-bottom:6px">'
        f'<span style="color:{LABEL_COLORS[label]}">●</span> '
        f"<strong>{label}</strong> — {LABEL_DESCRIPTIONS[label]}</div>"
        for label in ("signal", "hype", "panic")
    )
    return (
        '<div style="font-family:sans-serif;color:#e6e6e6">'
        '<div style="font-size:11px;color:#8a8f98;letter-spacing:0.05em;'
        'margin-bottom:8px">TAXONOMY</div>'
        f"{rows}"
        '<div style="font-size:11px;color:#5a5f68;margin-top:12px">'
        f"{caption}</div>"
        "</div>"
    )




CLASSIFY_BUTTON_CSS = (
    f"#classify-btn, #groq-classify-btn {{ background: {BUTTON_COLOR} !important; "
    "color: white !important; }"
)

with gr.Blocks(title="TakeMeter") as demo:
    gr.Markdown("# TakeMeter")
    gr.Markdown("Is this take backed by evidence?")

    with gr.Row():
        with gr.Column(scale=3):
            post_input = gr.Textbox(
                lines=4,
                label="Post text",
                placeholder="Paste a crypto-community post or comment...",
            )
            classify_btn = gr.Button(
                "Classify",
                elem_id="classify-btn",
            )
            result_card = gr.HTML()
        with gr.Column(scale=2):
            gr.HTML(_render_legend("DistilBERT, fine-tuned on 107 labeled r/CryptoCurrency posts"))

    classify_btn.click(fn=predict, inputs=post_input, outputs=result_card)

    gr.Markdown("## Groq base model")
    with gr.Row():
        with gr.Column(scale=3):
            groq_post_input = gr.Textbox(
                lines=4,
                label="Post text",
                placeholder="Paste a crypto-community post or comment...",
            )
            groq_classify_btn = gr.Button(
                "Classify with Groq",
                elem_id="groq-classify-btn",
            )
            groq_result_card = gr.HTML()
        with gr.Column(scale=2):
            gr.HTML(_render_legend(f"{config.GROQ_MODEL}, zero-shot, no fine-tuning"))

    groq_classify_btn.click(fn=predict_groq, inputs=groq_post_input, outputs=groq_result_card)

if __name__ == "__main__":
    demo.launch(css=CLASSIFY_BUTTON_CSS)
