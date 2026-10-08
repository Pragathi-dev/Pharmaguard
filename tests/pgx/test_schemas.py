import pytest
from backend.pgx.schemas import EngineMode, ConfidenceFlag, GeneResult


def test_gene_result_schema_defaults():
    res = GeneResult(
        sample_id="SAMPLE_001",
        gene="CYP2C19",
        mode="strict",
        diplotype="*1/*2",
        allele1="*1",
        allele2="*2",
        phenotype="Intermediate Metabolizer"
    )
    assert res.sample_id == "SAMPLE_001"
    assert res.gene == "CYP2C19"
    assert res.mode == "strict"
    assert res.diplotype == "*1/*2"
    assert res.phenotype == "Intermediate Metabolizer"
    assert res.engine_version == "3.0.0"
    assert res.provenance_class == "DERIVED_SILVER_LABEL"

    d = res.to_dict()
    assert isinstance(d, dict)
    assert d["sample_id"] == "SAMPLE_001"
    assert d["diplotype"] == "*1/*2"


def test_engine_mode_enum():
    assert EngineMode.STRICT.value == "strict"
    assert EngineMode.REFERENCE_DEFAULT.value == "reference_default"


def test_confidence_flag_enum():
    assert ConfidenceFlag.COMPLETE.value == "COMPLETE"
    assert ConfidenceFlag.PARTIAL.value == "PARTIAL"
    assert ConfidenceFlag.UNRESOLVED.value == "UNRESOLVED"
    assert ConfidenceFlag.STRUCTURAL_UNRESOLVED.value == "STRUCTURAL_UNRESOLVED"
