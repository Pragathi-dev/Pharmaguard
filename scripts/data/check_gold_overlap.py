#!/usr/bin/env python3
"""
Check GeT-RM consensus gold label overlap with 1000 Genomes samples.
Generates data/processed/gold_label_availability.json.
"""
import json
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.data.gold_overlap")

TARGET_GENES = ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]
GOLD_THRESHOLD = 30


def check_gold_label_overlap(
    sample_metadata_path: Path,
    getrm_path: Path,
    output_path: Path
) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load 1000G sample metadata
    samples_df = None
    if sample_metadata_path.is_file():
        samples_df = pd.read_parquet(sample_metadata_path)
    else:
        # Fallback to panel file if parquet not yet generated
        panel_file = PROJECT_ROOT / "data" / "metadata" / "integrated_call_samples_v3.20130502.ALL.panel"
        if panel_file.is_file():
            samples_df = pd.read_csv(panel_file, sep=r"\s+", engine="python").rename(columns={
                "sample": "sample_id", "super_pop": "superpopulation"
            })

    if samples_df is None or samples_df.empty:
        logger.error("No 1000G sample metadata found.")
        g1k_samples = set()
        sample_pop_map = {}
    else:
        g1k_samples = set(samples_df["sample_id"].astype(str).str.strip().str.upper())
        sample_pop_map = dict(zip(
            samples_df["sample_id"].astype(str).str.strip().str.upper(),
            samples_df["superpopulation"]
        ))

    # 2. Check GeT-RM consensus availability
    getrm_df = None
    getrm_file = None
    
    if getrm_path and Path(getrm_path).is_file():
        getrm_file = Path(getrm_path)
    elif getrm_path is None or Path(getrm_path) == (PROJECT_ROOT / "data" / "external" / "getrm_consensus.csv"):
        possible_paths = [
            PROJECT_ROOT / "data" / "external" / "getrm_consensus.csv",
            PROJECT_ROOT / "data" / "knowledge" / "getrm_consensus.csv",
            PROJECT_ROOT / "tests" / "fixtures" / "data" / "mini_getrm.csv"
        ]
        for p in possible_paths:
            if p and Path(p).is_file():
                getrm_file = Path(p)
                break

    result = {
        "gold_available": False,
        "getrm_source_file": str(getrm_file) if getrm_file else None,
        "genes": {}
    }

    if getrm_file is None:
        logger.warning("GeT-RM consensus dataset unavailable (file not found). Setting gold_available=False.")
        for gene in TARGET_GENES:
            result["genes"][gene] = {
                "n_gold_samples": 0,
                "n_overlap_1000g": 0,
                "superpopulations_represented": [],
                "status": "GOLD_INSUFFICIENT"
            }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        return result

    try:
        getrm_df = pd.read_csv(getrm_file)
        col_map = {c.lower(): c for c in getrm_df.columns}
        sid_col = col_map.get("sample id", col_map.get("sample_id", col_map.get("sample", "sample_id")))
        gene_col = col_map.get("gene", "gene")

        getrm_df[sid_col] = getrm_df[sid_col].astype(str).str.strip().str.upper()
        result["gold_available"] = True
        logger.info(f"Loaded GeT-RM consensus data ({len(getrm_df)} records) from {getrm_file.name}")

        for gene in TARGET_GENES:
            gene_mask = getrm_df[gene_col].astype(str).str.upper() == gene.upper()
            gene_rows = getrm_df[gene_mask]
            
            gold_sample_ids = set(gene_rows[sid_col].unique()) if not gene_rows.empty else set()
            overlap_ids = gold_sample_ids.intersection(g1k_samples)

            n_gold = len(gold_sample_ids)
            n_overlap = len(overlap_ids)
            superpops = sorted(list({sample_pop_map[sid] for sid in overlap_ids if sid in sample_pop_map}))

            status = "OK" if n_overlap >= GOLD_THRESHOLD else "GOLD_INSUFFICIENT"

            result["genes"][gene] = {
                "n_gold_samples": n_gold,
                "n_overlap_1000g": n_overlap,
                "superpopulations_represented": superpops,
                "status": status
            }

            logger.info(f"Gene {gene}: n_gold={n_gold}, n_overlap_1000g={n_overlap}, status={status}")

    except Exception as e:
        logger.error(f"Error parsing GeT-RM data: {e}")
        result["gold_available"] = False
        for gene in TARGET_GENES:
            result["genes"][gene] = {
                "n_gold_samples": 0,
                "n_overlap_1000g": 0,
                "superpopulations_represented": [],
                "status": "GOLD_INSUFFICIENT"
            }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    logger.info(f"Saved gold_label_availability.json to {output_path}")
    return result


def main():
    meta_path = PROJECT_ROOT / "data" / "processed" / "sample_metadata.parquet"
    getrm_path = PROJECT_ROOT / "data" / "external" / "getrm_consensus.csv"
    out_path = PROJECT_ROOT / "data" / "processed" / "gold_label_availability.json"

    check_gold_label_overlap(meta_path, getrm_path, out_path)


if __name__ == "__main__":
    main()
