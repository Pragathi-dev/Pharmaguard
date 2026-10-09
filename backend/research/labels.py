import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.labels")


def build_labels(
    pgx_calls_full_df: pd.DataFrame,
    gold_availability_path: Optional[Path] = None,
    sample_metadata_df: Optional[pd.DataFrame] = None,
    coarse_groupings: Optional[Dict[str, Dict[str, str]]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Builds strict full-information labels for ML training and evaluation.

    Args:
        pgx_calls_full_df (pd.DataFrame): Phase 3 full-information strict calls dataframe.
        gold_availability_path (Optional[Path]): Path to gold_label_availability.json or GeT-RM table.
        sample_metadata_df (Optional[pd.DataFrame]): Sample metadata dataframe.
        coarse_groupings (Optional[Dict]): Map of gene -> (fine_label -> coarse_label).

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (labels_df, metadata_summary_dict)
    """
    if pgx_calls_full_df.empty:
        raise ValueError("Full-information PGx calls dataframe cannot be empty.")

    gold_samples_by_gene: Dict[str, List[str]] = {}
    if gold_availability_path and Path(gold_availability_path).is_file():
        try:
            with open(gold_availability_path, "r", encoding="utf-8") as f:
                g_data = json.load(f)
            gold_samples_by_gene = g_data.get("overlapping_samples_by_gene", {})
        except Exception as e:
            logger.warning(f"Could not load gold availability file: {e}")

    exclusions_by_gene: Dict[str, int] = {}
    conflicts_list: List[Dict[str, Any]] = []
    labeled_rows: List[Dict[str, Any]] = []

    target_genes = ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]
    for g in target_genes:
        exclusions_by_gene[g] = 0

    for idx, row in pgx_calls_full_df.iterrows():
        sid = str(row.get("sample_id", ""))
        gene = str(row.get("gene", "")).upper()
        phenotype = str(row.get("phenotype", ""))
        conf_flag = str(row.get("confidence_flag", ""))

        # Exclude UNRESOLVED or Indeterminate phenotypes
        if conf_flag == "UNRESOLVED" or phenotype in ["Indeterminate", "UNKNOWN", "None", ""]:
            exclusions_by_gene[gene] = exclusions_by_gene.get(gene, 0) + 1
            continue

        # Determine label source (gold vs silver)
        gold_samples_for_gene = gold_samples_by_gene.get(gene, [])
        is_gold = sid in gold_samples_for_gene

        label_source = "gold" if is_gold else "silver"
        label_conflict = False
        fine_label = phenotype

        # Determine coarse label
        coarse_label = fine_label
        if coarse_groupings and gene in coarse_groupings:
            coarse_label = coarse_groupings[gene].get(fine_label, fine_label)

        sv_assessed = False if gene == "CYP2D6" else bool(row.get("structural_variation_assessed", True))

        labeled_rows.append({
            "sample_id": sid,
            "gene": gene,
            "label_fine": fine_label,
            "label_coarse": coarse_label,
            "label_source": label_source,
            "label_conflict": label_conflict,
            "structural_variation_assessed": sv_assessed,
            "kb_version": str(row.get("kb_version", "cpic_2022_v1")),
            "engine_version": str(row.get("engine_version", "3.0.0")),
            "provenance_class": "DERIVED_SILVER_LABEL" if label_source == "silver" else "DERIVED_GOLD_LABEL",
            "schema_version": "1.0"
        })

    labels_df = pd.DataFrame(labeled_rows)

    summary = {
        "total_input_calls": len(pgx_calls_full_df),
        "total_labeled_rows": len(labels_df),
        "exclusions_by_gene": exclusions_by_gene,
        "conflicts_count": len(conflicts_list),
        "conflicts_detail": conflicts_list
    }

    logger.info(f"Built {len(labels_df)} labels from {len(pgx_calls_full_df)} input calls. Exclusions: {exclusions_by_gene}")
    return labels_df, summary
