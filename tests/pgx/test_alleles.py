import pytest
from pathlib import Path
from backend.pgx.knowledge_files import load_knowledge
from backend.pgx.alleles import match_haplotype_alleles


def test_match_haplotype_alleles_wildtype():
    kb = load_knowledge("data/knowledge")
    allele_def = kb.alleles["CYP2C19"]

    # All defining sites HOM_REF
    site_calls = {
        "CYP2C19:chr10:94781859:G>A": {"status": "HOM_REF", "gt": "0/0"},
        "CYP2C19:chr10:94781944:G>A": {"status": "HOM_REF", "gt": "0/0"},
        "CYP2C19:chr10:94761900:C>T": {"status": "HOM_REF", "gt": "0/0"}
    }

    matched = match_haplotype_alleles(site_calls, allele_def)
    assert matched == ["*1"]


def test_match_haplotype_alleles_star2_het():
    kb = load_knowledge("data/knowledge")
    allele_def = kb.alleles["CYP2C19"]

    site_calls = {
        "CYP2C19:chr10:94781859:G>A": {"status": "HET", "gt": "0/1"},
        "CYP2C19:chr10:94781944:G>A": {"status": "HOM_REF", "gt": "0/0"},
        "CYP2C19:chr10:94761900:C>T": {"status": "HOM_REF", "gt": "0/0"}
    }

    matched = match_haplotype_alleles(site_calls, allele_def)
    assert "*2" in matched
