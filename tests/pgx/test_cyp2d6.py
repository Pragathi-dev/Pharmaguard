import pytest
from backend.pgx.knowledge_files import load_knowledge
from backend.pgx.cyp2d6 import evaluate_cyp2d6


def test_evaluate_cyp2d6_sv_assessed_false():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["CYP2D6"]
    a_def = kb.alleles["CYP2D6"]

    ph, as_val, sv_assessed, conf_flag = evaluate_cyp2d6(
        candidate_diplotypes=["*1/*1"],
        phenotype_def=p_def,
        allele_def=a_def,
        missing_defining_sites=[],
        mode="strict"
    )

    assert sv_assessed is False
    assert ph == "Normal Metabolizer"
    assert conf_flag == "COMPLETE"


def test_evaluate_cyp2d6_structural_unresolved():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["CYP2D6"]
    a_def = kb.alleles["CYP2D6"]

    ph, as_val, sv_assessed, conf_flag = evaluate_cyp2d6(
        candidate_diplotypes=["*1/*5"],
        phenotype_def=p_def,
        allele_def=a_def,
        missing_defining_sites=[],
        mode="strict"
    )

    assert sv_assessed is False
    assert conf_flag == "STRUCTURAL_UNRESOLVED"
