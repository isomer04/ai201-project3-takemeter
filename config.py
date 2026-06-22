"""Shared configuration for TakeMeter inference, evaluation, and the Groq baseline.

LABEL_MAP intentionally excludes "filter": per the project taxonomy, filter
posts have no stance and are excluded from the 3-way signal/hype/panic
classifier entirely (see README.md "Labels" and data/taxonomy.md). Rows
labeled "filter" map to NaN here and get dropped the same way the Colab
notebook drops unknown labels, so the local split matches the notebook's
split exactly.
"""

import os

# Hugging Face Hub model repo holding the fine-tuned weights.
# Set this after running the Colab fine-tuning notebook and pushing the
# model with `model.push_to_hub(...)` / `tokenizer.push_to_hub(...)`.
HF_MODEL_ID = os.environ.get("TAKEMETER_MODEL_ID", "isomer007/takemeter-distilbert")

LABEL_MAP = {
    "hype": 0,
    "panic": 1,
    "signal": 2,
}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}
NUM_LABELS = len(LABEL_MAP)

RANDOM_SEED = 42  # must match the Colab notebook's train_test_split seed

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(_REPO_ROOT, "data", "takemeter_dataset.csv")
RESULTS_DIR = os.path.join(_REPO_ROOT, "results")

GROQ_MODEL = "llama-3.3-70b-versatile"
