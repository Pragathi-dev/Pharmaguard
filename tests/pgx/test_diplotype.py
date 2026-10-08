import pytest
from backend.pgx.knowledge_files import load_knowledge
from backend.pgx.diplotype import enumerate_diplotypes


def test_enumerate_diplotypes_hom_ref():
    kb = load_knowledge("data/knowledge")
    allele_def = kb.alleles["CYP2C19"]

    site_calls = {
        "CYP2C19:chr10:94781859:G>A": {"status": "HOM_REF"},
        "CYP2C19:chr10:94781944:G>A": {"status": "HOM_REF"},
        "CYP2C19:chr10:94761900:C>T": {"status": "HOM_REF"}
    }

    candidates, ambiguous, missing = enumerate_diplotypes(site_calls, allele_def, mode="strict")
    assert candidates == ["*1/*1"]
    assert ambiguous is False
    assert missing == []


def test_enumerate_diplotypes_missing_strict():
    kb = load_knowledge("data/knowledge")
    allele_def = kb.alleles["CYP2C19"]

    site_calls = {
        "CYP2C19:chr10:94781859:G>A": {"status": "HOM_REF"}
        # Missing other defining sites
    }

    candidates, ambiguous, missing = enumerate_diplotypes(site_calls, allele_def, mode="strict")
    assert len(missing) > 0
