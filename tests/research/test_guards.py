import pytest
import pandas as pd
from backend.research.guards import (
    LeakageError,
    assert_no_split_leakage,
    assert_no_forbidden_features,
    assert_no_leakage
)


def test_assert_no_split_leakage_clean():
    splits_df = pd.DataFrame([
        {"sample_id": "S1", "relatedness_group": "G1", "split": "train"},
        {"sample_id": "S2", "relatedness_group": "G2", "split": "test"}
    ])
    # Should pass without error
    assert_no_split_leakage(splits_df)


def test_assert_no_split_leakage_raises_on_overlap():
    splits_df = pd.DataFrame([
        {"sample_id": "S1", "relatedness_group": "G1", "split": "train"},
        {"sample_id": "S2", "relatedness_group": "G1", "split": "test"}
    ])
    with pytest.raises(LeakageError):
        assert_no_split_leakage(splits_df)


def test_assert_no_forbidden_features_clean():
    cols = ["g__site1", "m__site1", "n_missing_defining", "rule_call_b0"]
    assert_no_forbidden_features(cols)


def test_assert_no_forbidden_features_raises_on_leakage():
    cols = ["g__site1", "m__site1", "label", "split"]
    with pytest.raises(LeakageError):
        assert_no_forbidden_features(cols)
