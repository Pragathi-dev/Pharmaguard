import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from backend.common.hashing import sha256_file
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.splits")


def make_splits(
    sample_metadata_df: pd.DataFrame,
    proportions: Optional[Dict[str, float]] = None,
    seed: int = 2026,
    version: str = "1.0"
) -> Tuple[pd.DataFrame, str]:
    """
    Creates group-aware 4-way splits (train/val/calib/test) by relatedness_group.

    Args:
        sample_metadata_df (pd.DataFrame): Dataframe containing sample_id, relatedness_group, superpopulation.
        proportions (Optional[Dict]): Ratios for train, val, calib, test (e.g. 0.60, 0.10, 0.15, 0.15).
        seed (int): Random seed for deterministic partition.
        version (str): Split version string.

    Returns:
        Tuple[pd.DataFrame, str]: (splits_df, splits_sha256_hash)
    """
    if proportions is None:
        proportions = {"train": 0.60, "val": 0.10, "calib": 0.15, "test": 0.15}

    required_cols = {"sample_id", "relatedness_group", "superpopulation"}
    if not required_cols.issubset(set(sample_metadata_df.columns)):
        raise ValueError(f"sample_metadata_df missing required columns: {required_cols - set(sample_metadata_df.columns)}")

    rng = np.random.default_rng(seed)

    # 1. Group samples by relatedness_group
    groups = sample_metadata_df["relatedness_group"].unique().tolist()
    rng.shuffle(groups)

    # Calculate target group counts
    total_groups = len(groups)
    n_train = int(round(total_groups * proportions["train"]))
    n_val = int(round(total_groups * proportions["val"]))
    n_calib = int(round(total_groups * proportions["calib"]))
    n_test = total_groups - (n_train + n_val + n_calib)

    group_to_split: Dict[str, str] = {}

    # Stratify groups by dominant superpopulation if multiple superpopulations exist
    groups_by_sp: Dict[str, List[str]] = {}
    for g in groups:
        sp = sample_metadata_df[sample_metadata_df["relatedness_group"] == g]["superpopulation"].mode().iloc[0]
        groups_by_sp.setdefault(sp, []).append(g)

    # Greedy stratified allocation
    train_g, val_g, calib_g, test_g = [], [], [], []

    for sp, g_list in sorted(groups_by_sp.items()):
        rng.shuffle(g_list)
        n_g = len(g_list)
        tr = max(1, int(round(n_g * proportions["train"]))) if n_g >= 4 else max(1, int(n_g * proportions["train"]))
        va = max(1, int(round(n_g * proportions["val"]))) if n_g >= 4 else 0
        ca = max(1, int(round(n_g * proportions["calib"]))) if n_g >= 4 else 0
        te = n_g - (tr + va + ca)

        train_g.extend(g_list[:tr])
        val_g.extend(g_list[tr:tr+va])
        calib_g.extend(g_list[tr+va:tr+va+ca])
        test_g.extend(g_list[tr+va+ca:])

    for g in train_g:
        group_to_split[g] = "train"
    for g in val_g:
        group_to_split[g] = "val"
    for g in calib_g:
        group_to_split[g] = "calib"
    for g in test_g:
        group_to_split[g] = "test"

    # Map back to sample level
    splits_rows = []
    for idx, row in sample_metadata_df.iterrows():
        sid = str(row["sample_id"])
        rg = str(row["relatedness_group"])
        sp = str(row["superpopulation"])
        split_name = group_to_split.get(rg, "train")

        splits_rows.append({
            "sample_id": sid,
            "relatedness_group": rg,
            "superpopulation": sp,
            "split": split_name,
            "split_seed": seed,
            "split_version": version
        })

    splits_df = pd.DataFrame(splits_rows).sort_values(by="sample_id").reset_index(drop=True)

    # Compute hash of deterministic dataframe string representation
    df_bytes = splits_df.to_csv(index=False).encode("utf-8")
    splits_hash = hashlib.sha256(df_bytes).hexdigest()

    logger.info(f"Created group-aware splits ({total_groups} groups across {len(splits_df)} samples). Hash: {splits_hash[:12]}")
    return splits_df, splits_hash


def save_splits(
    splits_df: pd.DataFrame,
    out_parquet: Path,
    out_hash: Path
) -> str:
    """Saves splits dataframe and sha256 hash file."""
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    splits_df.to_parquet(out_parquet, index=False)

    calculated_hash = sha256_file(out_parquet)
    with open(out_hash, "w", encoding="utf-8") as f:
        f.write(calculated_hash + "\n")

    return calculated_hash


def make_loso_splits(
    sample_metadata_df: pd.DataFrame,
    seed: int = 2026
) -> Dict[str, pd.DataFrame]:
    """
    Generates Leave-One-Superpopulation-Out (LOSO) split dataframes.

    Returns:
        Dict[str, pd.DataFrame]: Map of left_out_superpop -> splits_loso_df.
    """
    superpops = sample_metadata_df["superpopulation"].unique().tolist()
    loso_dict = {}

    for target_sp in superpops:
        loso_rows = []
        for idx, row in sample_metadata_df.iterrows():
            sid = str(row["sample_id"])
            rg = str(row["relatedness_group"])
            sp = str(row["superpopulation"])
            split_name = "test" if sp == target_sp else "train"

            loso_rows.append({
                "sample_id": sid,
                "relatedness_group": rg,
                "superpopulation": sp,
                "split": split_name,
                "split_seed": seed,
                "split_version": f"loso_{target_sp}"
            })

        loso_dict[target_sp] = pd.DataFrame(loso_rows).sort_values(by="sample_id").reset_index(drop=True)

    return loso_dict
