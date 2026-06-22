"""Single inference engine for TakeMeter. Used by both app.py and evaluate.py
so there is exactly one place that knows how to turn text into a label."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import config


class TakeClassifier:
    def __init__(self, model, tokenizer, id_to_label: dict):
        self.model = model
        self.tokenizer = tokenizer
        self.id_to_label = id_to_label

    @classmethod
    def from_pretrained(cls, model_id: str = None) -> "TakeClassifier":
        """Load the fine-tuned model from the Hugging Face Hub.

        Raises a clear error naming the env var / config value to fix if the
        model can't be found, since a missing/placeholder HF_MODEL_ID is the
        most likely failure on a fresh clone.
        """
        model_id = model_id or config.HF_MODEL_ID
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForSequenceClassification.from_pretrained(model_id)
        except Exception as exc:
            raise RuntimeError(
                f"Could not load model '{model_id}' from the Hugging Face Hub. "
                "Set TAKEMETER_MODEL_ID (env var) or config.HF_MODEL_ID to a "
                "real model repo id produced by the Colab fine-tuning notebook."
            ) from exc
        model.eval()

        # Trust the loaded model's own id2label over config.ID_TO_LABEL, but
        # only if they agree -- a model pushed with a different label order
        # would otherwise silently mislabel every prediction.
        model_id_to_label = {int(k): v for k, v in model.config.id2label.items()}
        if model_id_to_label != config.ID_TO_LABEL:
            raise RuntimeError(
                f"Model '{model_id}' has id2label={model_id_to_label}, which "
                f"does not match config.ID_TO_LABEL={config.ID_TO_LABEL}. "
                "The model was likely fine-tuned with a different LABEL_MAP."
            )
        return cls(model=model, tokenizer=tokenizer, id_to_label=model_id_to_label)

    def classify(self, text: str) -> dict:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=256,
            return_token_type_ids=False,
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits[0]
        probs = torch.nn.functional.softmax(logits, dim=-1)

        prob_by_label = {
            self.id_to_label[i]: probs[i].item() for i in range(len(self.id_to_label))
        }
        top_label = max(prob_by_label, key=prob_by_label.get)
        return {
            "label": top_label,
            "confidence": prob_by_label[top_label],
            "probs": prob_by_label,
        }
