import pytest
from backend.knowledge.schema import (
    RecommendationRecord,
    LookupResult,
    LookupStatus,
    SnapshotManifest,
    SnapshotInfo,
    ReconciliationItem
)


def test_recommendation_record_schema():
    rec = RecommendationRecord(
        gene="CYP2C19",
        phenotype="Poor Metabolizer",
        source_phenotype_term="Poor Metabolizer",
        drug="clopidogrel",
        recommendation_text="Avoid Clopidogrel.",
        guideline_id="CPIC:1",
        guideline_url="https://cpicpgx.org",
        guideline_version="2022.1",
        source="cpic",
        kb_version="cpic:2026-10-09",
        retrieved_at="2026-10-09T00:00:00Z"
    )

    assert rec.gene == "CYP2C19"
    assert rec.provenance_class == "KNOWLEDGE_BASE"
    assert rec.schema_version == "1.0"
    d = rec.to_dict()
    assert d["drug"] == "clopidogrel"
    assert d["source"] == "cpic"


def test_lookup_result_schema():
    res = LookupResult(
        status=LookupStatus.FOUND.value,
        gene="CYP2C19",
        phenotype="Poor Metabolizer",
        drug="clopidogrel",
        recommendation_text="Avoid Clopidogrel.",
        kb_version="existing_rules",
        source="existing_rules"
    )

    assert res.status == "FOUND"
    assert res.recommendation_text == "Avoid Clopidogrel."
