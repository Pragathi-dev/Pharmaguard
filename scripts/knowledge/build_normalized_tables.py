#!/usr/bin/env python3
"""
CLI script to convert raw knowledge base snapshots into normalized Parquet recommendation tables and sourced YAML definitions.
Generates data/knowledge/recommendations/recommendations.parquet.
"""
import argparse
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import yaml

from backend.knowledge.loader import load_raw_snapshot, load_snapshot_manifest
from backend.knowledge.normalize import create_recommendation_record, map_phenotype_term, normalize_drug_name
from backend.knowledge.versioning import list_snapshots
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.knowledge.build")

TARGET_DRUGS_MAP = {
    "clopidogrel": ["clopidogrel", "32968", "194000"],
    "warfarin": ["warfarin", "11289", "10689"],
    "fluorouracil": ["fluorouracil", "capecitabine", "5-fu", "4492"],
    "simvastatin": ["simvastatin", "36567"],
    "codeine": ["codeine", "2670"]
}


def _detect_drug_name(raw_item: dict) -> Optional[str]:
    """Detects drug name from item fields (drug, drugid, drugrecommendation, comments)."""
    explicit_drug = raw_item.get("drug")
    if explicit_drug:
        return normalize_drug_name(explicit_drug)

    drugid = str(raw_item.get("drugid", "")).lower()
    item_str = json_str = str(raw_item).lower()

    for canon_drug, keywords in TARGET_DRUGS_MAP.items():
        for kw in keywords:
            if kw in drugid or kw in item_str:
                return canon_drug

    return None


def main():
    parser = argparse.ArgumentParser(description="Build normalized recommendations table from snapshots.")
    parser.add_argument("--snapshot-date", type=str, default=None, help="Snapshot date (YYYY-MM-DD)")
    parser.add_argument("--out-dir", type=str, default="data/knowledge/recommendations", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshots = list_snapshots()
    if not snapshots:
        logger.warning("No snapshots found. Executing fetch_snapshots.py first...")
        from scripts.knowledge.fetch_snapshots import main as fetch_main
        fetch_main()
        snapshots = list_snapshots()

    records = []
    unmapped_terms = []

    for sn in snapshots:
        if args.snapshot_date and sn.snapshot_date != args.snapshot_date:
            continue

        raw_data = load_raw_snapshot(sn.source, sn.snapshot_date)
        retrieved_at = datetime.datetime.utcnow().isoformat() + "Z"

        for item in raw_data:
            rec_text = item.get("drugrecommendation") or item.get("recommendation_text") or ""
            classification = item.get("classification") or item.get("classification_of_recommendation")
            guideline_id = str(item.get("guidelineid") or item.get("guideline_id") or f"CPIC:{sn.source}")

            detected_drug = _detect_drug_name(item)
            if not detected_drug:
                continue

            # Process phenotypes (dictionary or string)
            phenotypes_obj = item.get("phenotypes")
            gene_ph_pairs = []

            if isinstance(phenotypes_obj, dict):
                for g_name, ph_val in phenotypes_obj.items():
                    gene_ph_pairs.append((g_name, ph_val))
            elif item.get("gene") and item.get("phenotype"):
                gene_ph_pairs.append((item.get("gene"), item.get("phenotype")))

            for gene, raw_ph in gene_ph_pairs:
                if gene not in ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]:
                    continue

                implications_obj = item.get("implications")
                impl_text = implications_obj.get(gene) if isinstance(implications_obj, dict) else item.get("implication_text")

                rec_obj, is_mapped = create_recommendation_record(
                    gene=gene,
                    raw_phenotype=raw_ph,
                    drug=detected_drug,
                    recommendation_text=rec_text,
                    guideline_id=guideline_id,
                    guideline_url=item.get("guideline_url", "https://cpicpgx.org"),
                    guideline_version=item.get("guideline_version", "2022.1"),
                    source=sn.source,
                    snapshot_date=sn.snapshot_date,
                    retrieved_at=retrieved_at,
                    activity_score_range=str(item.get("activityscore", {}).get(gene)) if isinstance(item.get("activityscore"), dict) else item.get("activity_score_range"),
                    implication_text=impl_text,
                    classification_of_recommendation=classification,
                    evidence_level=item.get("evidence_level", "High")
                )

                records.append(rec_obj.to_dict())
                if not is_mapped:
                    unmapped_terms.append((sn.source, gene, raw_ph))

    df = pd.DataFrame(records)
    out_parquet = out_dir / "recommendations.parquet"
    df.to_parquet(out_parquet, index=False)

    logger.info(f"Built normalized recommendations table at {out_parquet} ({len(df)} records).")
    if unmapped_terms:
        logger.warning(f"Found {len(unmapped_terms)} unmapped phenotype terms.")


if __name__ == "__main__":
    main()
