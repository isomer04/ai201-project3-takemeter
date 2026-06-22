import torch
from transformers import DistilBertConfig, DistilBertForSequenceClassification

from classifier import TakeClassifier


class StubTokenizer:
    """Minimal tokenizer stub: returns fixed-shape tensors, no vocab needed."""

    def __call__(self, text, return_tensors="pt", truncation=True, max_length=256,
                 return_token_type_ids=False):
        return {
            "input_ids": torch.tensor([[101, 2000, 102]]),
            "attention_mask": torch.tensor([[1, 1, 1]]),
        }


def make_test_classifier():
    cfg = DistilBertConfig(num_labels=3, vocab_size=30522)
    model = DistilBertForSequenceClassification(cfg)
    model.eval()
    id_to_label = {0: "hype", 1: "panic", 2: "signal"}
    return TakeClassifier(model=model, tokenizer=StubTokenizer(), id_to_label=id_to_label)


def test_classify_returns_a_known_label():
    clf = make_test_classifier()
    result = clf.classify("BTC to the moon")
    assert result["label"] in {"hype", "panic", "signal"}


def test_classify_probs_sum_to_one():
    clf = make_test_classifier()
    result = clf.classify("BTC to the moon")
    total = sum(result["probs"].values())
    assert abs(total - 1.0) < 1e-4


def test_classify_confidence_matches_top_prob():
    clf = make_test_classifier()
    result = clf.classify("BTC to the moon")
    assert result["confidence"] == max(result["probs"].values())


def test_classify_probs_keys_match_id_to_label():
    clf = make_test_classifier()
    result = clf.classify("BTC to the moon")
    assert set(result["probs"].keys()) == {"hype", "panic", "signal"}
