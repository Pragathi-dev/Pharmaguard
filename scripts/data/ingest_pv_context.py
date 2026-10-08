#!/usr/bin/env python3
"""
Ingest optional Pharmacovigilance (Drug/ADR) context dataset.
Stamps PHARMACOVIGILANCE_CONTEXT and enforces strict security isolation:
REJECTS any dataset containing sample_id or genotype columns.
"""
import sys
from pathlib import Path
import yaml
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.common.enums import ProvenanceClass
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.data.pv_ingest")


def ingest_pharmacovigilance_data(
    input_csv: Path,
    config_yaml: Path,
    output_parquet: Path
) -> bool:
    if not input_csv.is_file():
        logger.info(f"PV_CONTEXT_ABSENT: File not found at {input_csv}. Pipeline continuing without PV context.")
        return False

    # Load configuration rules
    forbidden_cols = ["sample_id", "patient_id", "genotype", "vcf_sample", "subject_id", "individual_id"]
    column_mapping = {}
    
    if config_yaml.is_file():
        with open(config_yaml, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            pv_cfg = cfg.get("pv_dataset", {})
            forbidden_cols = pv_cfg.get("forbidden_columns", forbidden_cols)
            column_mapping = pv_cfg.get("column_mapping", {})

    # Read CSV
    df = pd.read_csv(input_csv)
    raw_columns_lower = [str(c).lower().strip() for c in df.columns]

    # SECURITY CHECK: REJECT any sample-linking or genotype columns (Agent Rule 3)
    for fc in forbidden_cols:
        if fc.lower() in raw_columns_lower:
            err_msg = (
                f"SECURITY REJECTION: Pharmacovigilance CSV '{input_csv.name}' contains "
                f"forbidden sample-linking/genotype column '{fc}'. "
                f"Cross-provenance patient joining is strictly prohibited by Agent Rule 3."
            )
            logger.error(err_msg)
            raise ValueError(err_msg)

    # Apply column mapping if provided
    if column_mapping:
        df = df.rename(columns=column_mapping)

    # Stamp provenance metadata
    df["provenance_class"] = ProvenanceClass.PHARMACOVIGILANCE_CONTEXT.value
    df["source_version"] = "Professor_PV_v1.0"

    # Save to Parquet
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_parquet, index=False)
    logger.info(f"Successfully ingested PV context dataset ({len(df)} records) -> {output_parquet}")
    return True


def main():
    in_csv = PROJECT_ROOT / "data" / "external" / "professor_drug_adr.csv"
    cfg_yaml = PROJECT_ROOT / "config" / "pv_columns.yaml"
    out_parquet = PROJECT_ROOT / "data" / "processed" / "pv_context.parquet"

    ingest_pharmacovigilance_data(in_csv, cfg_yaml, out_parquet)


if __name__ == "__main__":
    main()
