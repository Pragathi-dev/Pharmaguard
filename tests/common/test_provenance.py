import pytest
from backend.common.enums import ProvenanceClass
from backend.common.provenance import make_provenance


def test_make_provenance_valid_enum(tmp_path):
    """Verify make_provenance constructs valid metadata dict with enum."""
    test_file = tmp_path / "reference.csv"
    test_file.write_bytes(b"sample_id,genotype\nHG00265,*1/*1\n")

    prov = make_provenance(
        cls=ProvenanceClass.REAL_PATIENT_GENOTYPE,
        source="1000Genomes_Phase3",
        version="v5b",
        path=test_file
    )

    assert prov["provenance_class"] == "REAL_PATIENT_GENOTYPE"
    assert prov["source"] == "1000Genomes_Phase3"
    assert prov["source_version"] == "v5b"
    assert prov["schema_version"] == "1.0"
    assert len(prov["sha256"]) == 64
    assert prov["retrieved_at"].endswith("Z")


def test_make_provenance_valid_string():
    """Verify make_provenance accepts valid string representation of enum."""
    prov = make_provenance(
        cls="KNOWLEDGE_BASE",
        source="CPIC_Guideline_2022",
        version="2022.1"
    )

    assert prov["provenance_class"] == "KNOWLEDGE_BASE"
    assert prov["sha256"] == ""


def test_make_provenance_invalid_class():
    """Verify ValueError is raised when invalid provenance class is passed."""
    with pytest.raises(ValueError) as excinfo:
        make_provenance(
            cls="INVALID_PROVENANCE_CLASS",
            source="Unknown",
            version="1.0"
        )
    assert "Invalid provenance class" in str(excinfo.value)
