#!/usr/bin/env python3
"""
CLI Script to generate group-aware splits and SHA256 integrity hash.
"""
import argparse
from pathlib import Path
import pandas as pd
import yaml

from backend.research.splits import make_splits, save_splits, make_loso_splits
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.cli_splits")


def main():
    parser = argparse.ArgumentParser(description="Generate group-aware ML splits.")
    parser.add_argument("--config", type=str, default="config/research.yaml", help="Path to config")
    parser.add_argument("--sample-metadata", type=str, default="data/processed/sample_metadata.parquet", help="Path to sample metadata")
    parser.add_argument("--out-dir", type=str, default="data/processed", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    metadata_df = pd.read_parquet(args.sample_metadata)

    splits_df, s_hash = make_splits(
        sample_metadata_df=metadata_df,
        proportions=cfg.get("splits", {}).get("proportions"),
        seed=cfg.get("split_seed", 2026)
    )

    out_parquet = out_dir / "splits.parquet"
    out_hash = out_dir / "splits.sha256"
    save_splits(splits_df, out_parquet, out_hash)

    # Build LOSO splits
    loso_dict = make_loso_splits(metadata_df, seed=cfg.get("split_seed", 2026))
    for sp_name, loso_df in loso_dict.items():
        loso_df.to_parquet(out_dir / f"splits_loso_{sp_name}.parquet", index=False)

    print("\n--- SPLITS SUMMARY ---")
    print(f"Total Samples: {len(splits_df)}")
    print(f"Total Relatedness Groups: {splits_df['relatedness_group'].nunique()}")
    print("Splits Distribution:")
    print(splits_df["split"].value_counts().to_string())
    print(f"Splits Hash: {s_hash[:16]}...")


if __name__ == "__main__":
    main()
