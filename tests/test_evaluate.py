import pandas as pd

from evaluate import load_test_split
import config


def test_load_test_split_excludes_filter_label(tmp_path, monkeypatch):
    csv_path = tmp_path / "tiny.csv"
    rows = []
    for label in ["signal", "hype", "panic"]:
        for i in range(10):
            rows.append({"text": f"{label} example {i}", "label": label})
    for i in range(5):
        rows.append({"text": f"filter example {i}", "label": "filter"})
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    monkeypatch.setattr(config, "DATASET_PATH", str(csv_path))
    test_df = load_test_split()

    assert "filter" not in test_df["label"].values
    assert set(test_df["label"].unique()).issubset({"signal", "hype", "panic"})


def test_load_test_split_is_reproducible(tmp_path, monkeypatch):
    csv_path = tmp_path / "tiny.csv"
    rows = []
    for label in ["signal", "hype", "panic"]:
        for i in range(10):
            rows.append({"text": f"{label} example {i}", "label": label})
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    monkeypatch.setattr(config, "DATASET_PATH", str(csv_path))
    first = load_test_split()
    second = load_test_split()

    assert list(first["text"]) == list(second["text"])
