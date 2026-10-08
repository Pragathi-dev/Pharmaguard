from pathlib import Path
from backend.genomics.vcf_reader import read_vcf_records

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "genomics"


def test_read_vcf_records_explicit_homref():
    """Verify read_vcf_records parses GT, DP, GQ from explicit_homref.vcf."""
    vcf_path = FIXTURES_DIR / "explicit_homref.vcf"
    records, samples, malformed = read_vcf_records(vcf_path)

    assert len(records) == 3
    assert samples == ["HG00265"]
    assert malformed == 0

    rec1 = records[0]
    assert rec1.pos == 94761900
    assert "HG00265" in rec1.genotypes
    gt = rec1.genotypes["HG00265"]
    assert gt.gt_str == "0/0"
    assert gt.dp == 30
    assert gt.gq == 99


def test_read_vcf_records_skips_malformed_lines():
    """Verify read_vcf_records skips malformed VCF lines without crashing."""
    vcf_path = FIXTURES_DIR / "malformed.vcf"
    records, samples, malformed = read_vcf_records(vcf_path)

    assert len(records) == 1
    assert malformed >= 1
    assert records[0].pos == 94761900


def test_read_vcf_records_empty_vcf():
    """Verify read_vcf_records on empty VCF returns 0 records and sample list."""
    vcf_path = FIXTURES_DIR / "empty.vcf"
    records, samples, malformed = read_vcf_records(vcf_path)

    assert len(records) == 0
    assert samples == ["HG00265"]
    assert malformed == 0
