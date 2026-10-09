from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import pandas as pd

from backend.common.hashing import sha256_file
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.guards")


class LeakageError(Exception):
    """Raised when data leakage or split contamination is detected."""
    pass


FORBIDDEN_FEATURE_COLUMNS = {
    "label",
    "full_diplotype",
    "full_information_diplotype",
    "full_information_phenotype",
    "relatedness_group",
    "diplotype"
}


def assert_no_split_leakage(splits_df: pd.DataFrame) -> None:
    """
    Asserts zero overlap of relatedness_group or sample_id across splits.
    """
    if splits_df.empty:
        raise LeakageError("Splits dataframe is empty.")

    # Check relatedness_group overlap
    split_names = splits_df["split"].unique()
    groups_by_split: Dict[str, Set[str]] = {}

    for s in split_names:
        groups_by_split[s] = set(splits_df[splits_df["split"] == s]["relatedness_group"].unique())

    for i, s1 in enumerate(split_names):
        for s2 in split_names[i+1:]:
            overlap = groups_by_split[s1].intersection(groups_by_split[s2])
            if overlap:
                raise LeakageError(
                    f"LEAKAGE DETECTED: {len(overlap)} relatedness_groups overlap between '{s1}' and '{s2}' splits: {overlap}"
                )

    # Check sample_id overlap
    samples_by_split: Dict[str, Set[str]] = {}
    for s in split_names:
        samples_by_split[s] = set(splits_df[splits_df["split"] == s]["sample_id"].unique())

    for i, s1 in enumerate(split_names):
        for s2 in split_names[i+1:]:
            s_overlap = samples_by_split[s1].intersection(samples_by_split[s2])
            if s_overlap:
                raise LeakageError(
                    f"LEAKAGE DETECTED: {len(s_overlap)} sample_ids overlap between '{s1}' and '{s2}' splits: {s_overlap}"
                )

    logger.info("SPLIT LEAKAGE GUARD PASSED: Zero relatedness_group or sample_id overlap detected.")


def verify_split_hash(splits_parquet_path: Path, expected_hash_path: Path) -> None:
    """
    Verifies splits.parquet SHA256 matches stored splits.sha256.
    """
    if not splits_parquet_path.is_file():
        raise FileNotFoundError(f"Splits parquet file missing: {splits_parquet_path}")

    if not expected_hash_path.is_file():
        raise FileNotFoundError(f"Splits hash file missing: {expected_hash_path}")

    actual_hash = sha256_file(splits_parquet_path)
    with open(expected_hash_path, "r", encoding="utf-8") as f:
        stored_hash = f.read().strip()

    if actual_hash != stored_hash:
        raise LeakageError(
            f"SPLIT HASH MISMATCH FAILURE! Actual hash '{actual_hash}' does not match stored hash '{stored_hash}'. "
            f"Dataset cannot be built on tampered or out-of-date splits."
        )

    logger.info("SPLIT HASH GUARD PASSED: SHA256 integrity verified.")


def assert_no_forbidden_features(feature_columns: List[str]) -> None:
    """
    Asserts zero forbidden target/leakage columns exist in feature columns list.
    """
    feature_set = set(feature_columns)
    leaked_cols = FORBIDDEN_FEATURE_COLUMNS.intersection(feature_set)

    if leaked_cols:
        raise LeakageError(
            f"FEATURE LEAKAGE DETECTED: Forbidden leakage columns found in feature list: {leaked_cols}"
        )

    logger.info("FEATURE LEAKAGE GUARD PASSED: Zero forbidden feature columns found.")


def assert_no_leakage(
    ml_dataset_df: pd.DataFrame,
    splits_df: pd.DataFrame,
    labels_df: pd.DataFrame
) -> None:
    """
    Comprehensive leakage control assertion pipeline.
    Runs all guards before dataset output is exported.
    """
    # 1. Assert split group separation
    assert_no_split_leakage(splits_df)

    # 2. Assert zero forbidden feature columns
    if not ml_dataset_df.empty:
        assert_no_forbidden_features(ml_dataset_df.columns.tolist())

    # 3. Assert all samples in dataset exist in splits
    ds_samples = set(ml_dataset_df["sample_id"].unique()) if not ml_dataset_df.empty else set()
    sp_samples = set(splits_df["sample_id"].unique())
    missing_samples = ds_samples - sp_samples
    if missing_samples:
        raise LeakageError(f"LEAKAGE DETECTED: {len(missing_samples)} dataset samples not present in split file: {missing_samples}")

    logger.info("ALL LEAKAGE GUARDS PASSED CLEANLY.")
