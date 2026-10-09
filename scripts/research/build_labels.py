#!/usr/bin/env python3
"""
CLI Script to generate labels.parquet from full-information engine calls and gold availability.
"""
import argparse
from pathlib import Path
import pandas as pd
import yaml

from backend.research.labels import build_labels
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.cli_labels")


def main():
    parser = argparse.ArgumentParser(description="Generate full-information labels dataframe.")
    parser.add_argument("--config", type=str, default="config/research.yaml", help="Path to config")
    parser.add_argument("--pgx-calls", type=str, default="data/processed/pgx_calls_1000g_full_strict.parquet", help="Path to full-info pgx calls")
    parser.add_argument("--gold-availability", type=str, default="data/processed/gold_label_availability.json", help="Path to gold availability json")
    parser.add_argument("--sample-metadata", type=str, default="data/processed/sample_metadata.parquet", help="Path to sample metadata")
    parser.add_argument("--out-dir", type=str, default="data/processed", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    pgx_full_df = pd.read_parquet(args.pgx_calls)
    meta_df = pd.read_parquet(args.sample_metadata)

    labels_df, summary = build_labels(
        pgx_calls_full_df=pgx_full_df,
        gold_availability_path=Path(args.gold_availability),
        sample_metadata_df=meta_df,
        coarse_groupings=cfg.get("rare_classes", {}).get("coarse_groupings")
    )

    out_file = out_dir / "labels.parquet"
    labels_df.to_parquet(out_file, index=False)

    print("\n--- LABELS SUMMARY ---")
    print(f"Total Labeled Rows: {len(labels_df)}")
    print("Labels by Source:")
    print(labels_df["label_source"].value_counts().to_string())
    print("\nExclusions by Gene:")
    for g, count in summary["exclusions_by_gene"].items():
        print(f"  {g}: {count}")


if __name__ == "__main__":
    main()
