import pytest
from backend.knowledge.normalize import map_phenotype_term, normalize_drug_name, create_recommendation_record


def test_map_phenotype_term_standard():
    term, is_mapped = map_phenotype_term("poor metabolizer")
    assert term == "Poor Metabolizer"
    assert is_mapped is True

    term2, is_mapped2 = map_phenotype_term("normal function")
    assert term2 == "Normal Function"
    assert is_mapped2 is True


def test_map_phenotype_term_unmapped():
    term, is_mapped = map_phenotype_term("novel_unseen_term_123")
    assert term == "novel_unseen_term_123"
    assert is_mapped is False


def test_normalize_drug_name():
    assert normalize_drug_name("5-FU") == "fluorouracil"
    assert normalize_drug_name("Clopidogrel") == "clopidogrel"
    assert normalize_drug_name("WARFARIN ") == "warfarin"


def test_create_recommendation_record():
    rec, is_mapped = create_recommendation_record(
        gene="cyp2c19",
        raw_phenotype="Intermediate Metabolizer",
        drug="Clopidogrel",
        recommendation_text="Avoid Clopidogrel.",
        guideline_id="G1",
        guideline_url="https://cpicpgx.org",
        guideline_version="1.0",
        source="cpic",
        snapshot_date="2026-10-09",
        retrieved_at="2026-10-09T00:00:00Z"
    )

    assert rec.gene == "CYP2C19"
    assert rec.drug == "clopidogrel"
    assert rec.phenotype == "Intermediate Metabolizer"
    assert rec.kb_version == "cpic:2026-10-09"
    assert rec.provenance_class == "KNOWLEDGE_BASE"
