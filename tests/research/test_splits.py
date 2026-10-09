import pytest
import pandas as pd
from backend.research.splits import make_splits, make_loso_splits
from backend.research.guards import assert_no_split_leakage


def test_make_splits_group_separation():
    meta_df = pd.DataFrame([
        {"sample_id": f"S{i}", "relatedness_group": f"G{i//2}", "superpopulation": "EUR" if i < 10 else "AFR"}
        for i in range(20)
    ])

    splits_df, s_hash = make_splits(meta_df, seed=2026)

    assert len(splits_df) == 20
    assert set(splits_df["split"].unique()).issubset({"train", "val", "calib", "test"})

    # Assert zero group overlap across splits
    assert_no_split_leakage(splits_df)


def test_make_loso_splits():
    meta_df = pd.DataFrame([
        {"sample_id": "S1", "relatedness_group": "G1", "superpopulation": "EUR"},
        {"sample_id": "S2", "relatedness_group": "G2", "superpopulation": "AFR"}
    ])

    loso_dict = make_loso_splits(meta_df)
    assert "EUR" in loso_dict
    assert "AFR" in loso_dict

    eur_loso = loso_dict["EUR"]
    assert eur_loso[eur_loso["sample_id"] == "S1"]["split"].iloc[0] == "test"
    assert eur_loso[eur_loso["sample_id"] == "S2"]["split"].iloc[0] == "train"
