import pandas as pd
from backend.genomics.enums import SiteObservationStatus
from backend.genomics.qc import apply_genotype_qc, compute_sample_qc, QcConfig


def test_apply_genotype_qc_thresholds():
    """Verify DP and GQ threshold filtering."""
    cfg = QcConfig(min_dp=10, min_gq=20)

    # Valid PASS
    status, reason = apply_genotype_qc("PASS", 15, 30, cfg)
    assert status is None
    assert reason == "PASS"

    # DP low
    status, reason = apply_genotype_qc("PASS", 5, 30, cfg)
    assert status == SiteObservationStatus.LOW_QUALITY
    assert "DP_5_below_10" in reason

    # GQ low
    status, reason = apply_genotype_qc("PASS", 15, 12, cfg)
    assert status == SiteObservationStatus.LOW_QUALITY
    assert "GQ_12_below_20" in reason

    # FILTER fail
    status, reason = apply_genotype_qc("LowQual", 15, 30, cfg)
    assert status == SiteObservationStatus.FILTERED
    assert reason == "LowQual"


def test_compute_sample_qc():
    """Verify compute_sample_qc calculates region_call_rate and qc_pass."""
    df = pd.DataFrame([
        {"sample_id": "HG00265", "gene": "CYP2C19", "status": "HOM_REF", "phased": True},
        {"sample_id": "HG00265", "gene": "CYP2C19", "status": "HET", "phased": True},
        {"sample_id": "HG00265", "gene": "CYP2C19", "status": "NOT_IN_VCF", "phased": False}
    ])

    qc_df = compute_sample_qc(df, QcConfig(min_region_call_rate=0.60))

    assert len(qc_df) == 1
    row = qc_df.iloc[0]
    assert row["sample_id"] == "HG00265"
    assert row["n_catalogued"] == 3
    assert row["n_observed"] == 2
    assert row["n_not_in_vcf"] == 1
    assert row["region_call_rate"] == 0.6667
    assert bool(row["qc_pass"]) is True
