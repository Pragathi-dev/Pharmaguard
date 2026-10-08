from pathlib import Path
import pytest
from backend.genomics.catalogue import load_catalogue
from backend.genomics.enums import SiteObservationStatus, ReferenceEvidence
from backend.genomics.site_extractor import extract_site_calls

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "genomics"
CATALOGUE_YAML = PROJECT_ROOT / "config" / "pgx_site_catalogue.yaml"


def test_extract_site_calls_explicit_homref():
    """Verify site extractor emits HOM_REF, HET, HOM_ALT with explicit GT evidence."""
    vcf_path = FIXTURES_DIR / "explicit_homref.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)

    assert not df.empty
    cyp2c19_df = df[df["gene"] == "CYP2C19"]
    
    statuses = set(cyp2c19_df["status"].tolist())
    assert "HOM_REF" in statuses
    assert "HET" in statuses
    assert "HOM_ALT" in statuses

    # Verify reference evidence for explicit GT HOM_REF
    hom_ref_rows = cyp2c19_df[cyp2c19_df["status"] == "HOM_REF"]
    for _, r in hom_ref_rows.iterrows():
        assert r["reference_evidence"] == "explicit_gt"


def test_extract_site_calls_missing_site_preserves_not_in_vcf():
    """Verify absent catalogued site becomes NOT_IN_VCF, NEVER silently HOM_REF."""
    vcf_path = FIXTURES_DIR / "missing_site.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)
    cyp2c19_df = df[df["gene"] == "CYP2C19"]

    # Site 94761900 is absent from missing_site.vcf
    absent_site = cyp2c19_df[cyp2c19_df["pos"] == 94761900].iloc[0]
    assert absent_site["status"] == "NOT_IN_VCF"
    assert absent_site["reference_evidence"] == "none"


def test_extract_site_calls_multiallelic():
    """Verify multiallelic site is classified as MULTIALLELIC."""
    vcf_path = FIXTURES_DIR / "multiallelic.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)
    cyp2c19_df = df[df["gene"] == "CYP2C19"]
    
    multi_row = cyp2c19_df[cyp2c19_df["pos"] == 94761900].iloc[0]
    assert multi_row["status"] == "MULTIALLELIC"


def test_extract_site_calls_low_qual():
    """Verify DP/GQ below threshold leads to LOW_QUALITY / FILTERED."""
    vcf_path = FIXTURES_DIR / "low_qual.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)
    cyp2c19_df = df[df["gene"] == "CYP2C19"]

    low_row = cyp2c19_df[cyp2c19_df["pos"] == 94761900].iloc[0]
    assert low_row["status"] in ["LOW_QUALITY", "FILTERED"]


def test_extract_site_calls_chr_prefix_mismatch():
    """Verify contig '10' vs 'chr10' mismatch is harmonized cleanly."""
    vcf_path = FIXTURES_DIR / "chr_prefix.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)
    cyp2c19_df = df[df["gene"] == "CYP2C19"]

    row = cyp2c19_df[cyp2c19_df["pos"] == 94761900].iloc[0]
    assert row["status"] == "HET"
    assert row["chrom"] == "chr10"


def test_extract_site_calls_callable_bed():
    """Verify callable BED turns an absent record into HOM_REF with callable_bed evidence."""
    vcf_path = FIXTURES_DIR / "missing_site.vcf"
    bed_path = FIXTURES_DIR / "callable.bed"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat, callable_bed_path=bed_path)
    cyp2c19_df = df[df["gene"] == "CYP2C19"]

    # Pos 94761900 is in callable.bed -> should become HOM_REF (callable_bed)
    callable_row = cyp2c19_df[cyp2c19_df["pos"] == 94761900].iloc[0]
    assert callable_row["status"] == "HOM_REF"
    assert callable_row["reference_evidence"] == "callable_bed"


def test_property_assertion_no_homref_without_evidence():
    """PROPERTY CHECK ASSERTION: Zero rows may have status=HOM_REF and reference_evidence=none."""
    vcf_path = FIXTURES_DIR / "explicit_homref.vcf"
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")

    df = extract_site_calls(vcf_path, cat)
    invalid = df[(df["status"] == "HOM_REF") & (df["reference_evidence"] == "none")]
    assert len(invalid) == 0, "Property violation: HOM_REF found with reference_evidence=none"
