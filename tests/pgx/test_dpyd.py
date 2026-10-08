import pytest
from backend.pgx.knowledge_files import load_knowledge
from backend.pgx.dpyd import evaluate_dpyd


def test_evaluate_dpyd_only_catalogued_true():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["DPYD"]
    a_def = kb.alleles["DPYD"]

    ph, as_val, catalogued_only = evaluate_dpyd(
        candidate_diplotypes=["*1/*1"],
        phenotype_def=p_def,
        allele_def=a_def
    )

    assert catalogued_only is True
    assert ph == "Normal Metabolizer"
    assert as_val == 2.0
