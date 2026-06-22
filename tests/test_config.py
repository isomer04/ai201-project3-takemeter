import config


def test_label_map_excludes_filter():
    assert "filter" not in config.LABEL_MAP
    assert set(config.LABEL_MAP.keys()) == {"signal", "hype", "panic"}


def test_label_map_ids_are_contiguous_from_zero():
    ids = sorted(config.LABEL_MAP.values())
    assert ids == [0, 1, 2]


def test_id_to_label_is_exact_inverse():
    for label, idx in config.LABEL_MAP.items():
        assert config.ID_TO_LABEL[idx] == label


def test_random_seed_matches_notebook():
    assert config.RANDOM_SEED == 42
