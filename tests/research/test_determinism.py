import pytest
import pandas as pd
from backend.research.splits import make_splits


def test_splits_determinism():
    meta_df = pd.DataFrame([
        {"sample_id": f"S{i}", "relatedness_group": f"G{i//2}", "superpopulation": "EUR"}
        for i in range(10)
    ])

    splits1, hash1 = make_splits(meta_df, seed=2026)
    splits2, hash2 = make_splits(meta_df, seed=2026)

    assert hash1 == hash2
    assert splits1.equals(splits2)
