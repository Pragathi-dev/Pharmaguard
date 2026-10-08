#!/usr/bin/env python3
"""
Build sample_metadata.parquet with pedigree-derived relatedness groups.
"""
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.metadata import merge_sample_metadata
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.data.build_metadata")


def main():
    panel_file = PROJECT_ROOT / "data" / "metadata" / "integrated_call_samples_v3.20130502.ALL.panel"
    pedigree_file = PROJECT_ROOT / "data" / "metadata" / "20130606_g1k.ped"
    out_file = PROJECT_ROOT / "data" / "processed" / "sample_metadata.parquet"

    if not panel_file.is_file():
        logger.error(f"Panel file not found at {panel_file}")
        sys.exit(1)

    ped_path = pedigree_file if pedigree_file.is_file() else None
    df = merge_sample_metadata(panel_file, ped_path, out_file)

    n_samples = len(df)
    n_rel_groups = df["relatedness_group"].nunique()
    superpop_counts = df["superpopulation"].value_counts().to_dict()

    logger.info("=" * 60)
    logger.info("SAMPLE METADATA GENERATED SUCCESSFULLY")
    logger.info(f"Total Samples: {n_samples}")
    logger.info(f"Relatedness Groups: {n_rel_groups}")
    logger.info(f"Superpopulation Breakdown: {superpop_counts}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
