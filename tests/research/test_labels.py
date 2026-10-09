import pytest
import pandas as pd
from backend.research.labels import build_labels


def test_build_labels_basic():
    pgx_calls_df = pd.DataFrame([
        {
            "sample_id": "HG00096", "gene": "CYP2C19", "diplotype": "*1/*1",
            "phenotype": "Normal Metabolizer", "confidence_flag": "COMPLETE",
            "structural_variation_assessed": True, "kb_version": "cpic_2022_v1", "engine_version": "3.0.0"
        },
        {
            "sample_id": "HG00096", "gene": "CYP2D6", "diplotype": "*1/*1",
            "phenotype": "Normal Metabolizer", "confidence_flag": "COMPLETE",
            "structural_variation_assessed": False, "kb_version": "cpic_2022_v1", "engine_version": "3.0.0"
        },
        {
            "sample_id": "HG00097", "gene": "CYP2C19", "diplotype": None,
            "phenotype": "Indeterminate", "confidence_flag": "PARTIAL",
            "structural_variation_assessed": True, "kb_version": "cpic_2022_v1", "engine_version": "3.0.0"
        }
    ])

    labels_df, summary = build_labels(pgx_calls_df)

    assert len(labels_df) == 2  # HG00097 excluded due to PARTIAL / Indeterminate
    assert set(labels_df["sample_id"].unique()) == {"HG00096"}

    cyp2d6_row = labels_df[labels_df["gene"] == "CYP2D6"].iloc[0]
    assert bool(cyp2d6_row["structural_variation_assessed"]) is False
    assert summary["exclusions_by_gene"]["CYP2C19"] == 1
