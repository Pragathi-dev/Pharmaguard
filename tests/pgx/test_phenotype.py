import pytest
from backend.pgx.knowledge_files import load_knowledge
from backend.pgx.phenotype import get_phenotype_for_diplotype, map_diplotypes_to_phenotype


def test_get_phenotype_cyp2c19():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["CYP2C19"]
    a_def = kb.alleles["CYP2C19"]

    ph, as_val = get_phenotype_for_diplotype("*1/*1", p_def, a_def)
    assert ph == "Normal Metabolizer"
    assert as_val == 1.0

    ph, as_val = get_phenotype_for_diplotype("*1/*2", p_def, a_def)
    assert ph == "Intermediate Metabolizer"

    ph, as_val = get_phenotype_for_diplotype("*2/*2", p_def, a_def)
    assert ph == "Poor Metabolizer"


def test_map_diplotypes_ambiguous_same_phenotype():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["CYP2C19"]
    a_def = kb.alleles["CYP2C19"]

    # Both *1/*2 and *1/*3 map to Intermediate Metabolizer
    ph, as_val = map_diplotypes_to_phenotype(["*1/*2", "*1/*3"], p_def, a_def)
    assert ph == "Intermediate Metabolizer"


def test_map_diplotypes_ambiguous_different_phenotype():
    kb = load_knowledge("data/knowledge")
    p_def = kb.phenotypes["CYP2C19"]
    a_def = kb.alleles["CYP2C19"]

    # *1/*1 (Normal) vs *2/*2 (Poor)
    ph, as_val = map_diplotypes_to_phenotype(["*1/*1", "*2/*2"], p_def, a_def)
    assert ph == "Indeterminate"
