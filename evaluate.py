"""Reproduces the notebook's locked test split locally and evaluates the
fine-tuned model on it — no API key, no Colab session required.

Mirrors the Colab notebook exactly: map labels via LABEL_MAP, drop rows that
don't map (this is how "filter" rows get excluded), then do the same
70/15/15 stratified split with the same random seed, so this script and the
notebook always agree on which rows are in the test set.
"""

import os

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

import config
from classifier import TakeClassifier


def load_test_split() -> pd.DataFrame:
    df = pd.read_csv(config.DATASET_PATH)
    df["label_id"] = df["label"].map(config.LABEL_MAP)
    df = df.dropna(subset=["label_id"])
    df["label_id"] = df["label_id"].astype(int)

    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=config.RANDOM_SEED, stratify=df["label_id"]
    )
    _val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=config.RANDOM_SEED, stratify=temp_df["label_id"]
    )
    return test_df.reset_index(drop=True)


def main():
    test_df = load_test_split()
    clf = TakeClassifier.from_pretrained()

    pred_labels = [clf.classify(text)["label"] for text in test_df["text"]]
    true_labels = test_df["label"].tolist()

    accuracy = np.mean([p == t for p, t in zip(pred_labels, true_labels)])
    print(f"Fine-tuned model accuracy: {accuracy:.3f}\n")

    label_names = [config.ID_TO_LABEL[i] for i in range(config.NUM_LABELS)]
    print(classification_report(true_labels, pred_labels, labels=label_names, zero_division=0))

    cm = confusion_matrix(true_labels, pred_labels, labels=label_names)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_names)
    disp.plot(cmap="Blues", colorbar=False)

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(config.RESULTS_DIR, "confusion_matrix.png")
    disp.figure_.savefig(out_path, dpi=150)
    print(f"\nSaved confusion matrix to {out_path}")


if __name__ == "__main__":
    main()
