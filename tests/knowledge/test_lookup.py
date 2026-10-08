import pytest
from backend.knowledge.lookup import get_recommendations, list_supported_drugs


def test_lookup_existing_rules_found():
    res = get_recommendations("CYP2C19", "Poor Metabolizer", "clopidogrel", kb_version="existing_rules")
    assert res.status == "FOUND"
    assert res.gene == "CYP2C19"
    assert res.drug == "clopidogrel"
    assert "Avoid Clopidogrel" in res.recommendation_text
    assert res.kb_version == "existing_rules"
    assert res.source == "existing_rules"


def test_lookup_existing_rules_unknown_drug():
    res = get_recommendations("CYP2C19", "Poor Metabolizer", "unknown_drug_xyz", kb_version="existing_rules")
    assert res.status == "NOT_AVAILABLE"
    assert res.recommendation_text is None


def test_lookup_existing_rules_unknown_phenotype():
    res = get_recommendations("CYP2C19", "Non_Existent_Phenotype", "clopidogrel", kb_version="existing_rules")
    assert res.status == "NOT_AVAILABLE"
    assert res.recommendation_text is None


def test_list_supported_drugs():
    drugs = list_supported_drugs()
    assert "clopidogrel" in drugs
    assert "warfarin" in drugs

    cyp2c19_drugs = list_supported_drugs("CYP2C19")
    assert cyp2c19_drugs == ["clopidogrel"]
