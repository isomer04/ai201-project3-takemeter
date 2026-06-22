"""Standalone zero-shot baseline using Groq's llama-3.3-70b-versatile.
Reproduces the same locked test split as evaluate.py and the notebook.
Requires GROQ_API_KEY in .env (see .env.example).
"""

import os
import time

from dotenv import load_dotenv
from groq import Groq
from sklearn.metrics import classification_report

import config
from evaluate import load_test_split
from groq_classifier import SYSTEM_PROMPT, classify_with_groq

load_dotenv()


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
        )
    client = Groq(api_key=api_key)
    test_df = load_test_split()

    predictions, true_labels = [], []
    for _, row in test_df.iterrows():
        pred = classify_with_groq(client, SYSTEM_PROMPT, row["text"])
        if pred is not None:
            predictions.append(pred)
            true_labels.append(row["label"])
        time.sleep(0.1)

    unparseable = len(test_df) - len(predictions)
    if unparseable:
        print(f"Warning: {unparseable} responses could not be parsed.\n")
    if not predictions:
        raise RuntimeError("No responses could be parsed into a label; aborting.")

    accuracy = sum(p == t for p, t in zip(predictions, true_labels)) / len(predictions)
    print(f"Baseline accuracy: {accuracy:.3f} ({len(predictions)}/{len(test_df)} parseable)\n")
    label_names = [config.ID_TO_LABEL[i] for i in range(config.NUM_LABELS)]
    print(classification_report(true_labels, predictions, labels=label_names, zero_division=0))


if __name__ == "__main__":
    main()
