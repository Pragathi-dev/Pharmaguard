import pytest
import pandas as pd
from backend.pgx.engine import run_engine, interpret_gene
from backend.pgx.knowledge_files import load_knowledge


def test_interpret_gene_complete():
    kb = load_knowledge("data/knowledge")
    site_calls = pd.DataFrame([
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781859:G>A", "status": "HOM_REF"},
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781944:G>A", "status": "HOM_REF"},
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94761900:C>T", "status": "HOM_REF"}
    ])

    res = interpret_gene("S1", "CYP2C19", site_calls, kb, mode="strict")
    assert res.diplotype == "*1/*1"
    assert res.phenotype == "Normal Metabolizer"
    assert res.confidence_flag == "COMPLETE"
    assert res.missing_defining_sites == []


def test_run_engine_batch():
    site_calls = pd.DataFrame([
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781859:G>A", "status": "HOM_REF"},
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781944:G>A", "status": "HOM_REF"},
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94761900:C>T", "status": "HOM_REF"}
    ])

    df = run_engine(site_calls, mode="strict")
    assert not df.empty
    assert len(df) == 5  # 5 genes interpreted per sample
    assert set(df["gene"].unique()) == {"CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"}
