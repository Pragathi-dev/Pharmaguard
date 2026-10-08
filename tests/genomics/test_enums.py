from backend.genomics.enums import SiteObservationStatus, ReferenceEvidence


def test_site_observation_status_values():
    """Verify all 8 site observation status enum values exist."""
    expected = {
        "HOM_REF", "HET", "HOM_ALT", "NO_CALL", "NOT_IN_VCF",
        "FILTERED", "MULTIALLELIC", "LOW_QUALITY"
    }
    actual = {s.value for s in SiteObservationStatus}
    assert actual == expected


def test_reference_evidence_values():
    """Verify reference evidence categories."""
    expected = {"explicit_gt", "gvcf_block", "callable_bed", "none"}
    actual = {e.value for e in ReferenceEvidence}
    assert actual == expected
