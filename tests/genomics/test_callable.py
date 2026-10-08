from pathlib import Path
from backend.genomics.callable import parse_bed_file, evaluate_callable_evidence
from backend.genomics.enums import ReferenceEvidence
from backend.genomics.vcf_reader import read_vcf_records

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "genomics"


def test_parse_bed_file():
    """Verify parse_bed_file loads 0-based intervals from callable.bed."""
    bed_path = FIXTURES_DIR / "callable.bed"
    intervals = parse_bed_file(bed_path)

    assert "chr10" in intervals
    assert (94760000, 94765000) in intervals["chr10"]


def test_evaluate_callable_evidence_bed():
    """Verify evaluate_callable_evidence identifies position in BED interval."""
    bed_path = FIXTURES_DIR / "callable.bed"
    intervals = parse_bed_file(bed_path)

    is_callable, ev_type = evaluate_callable_evidence("chr10", 94761900, [], bed_intervals=intervals)
    assert is_callable is True
    assert ev_type == ReferenceEvidence.CALLABLE_BED


def test_evaluate_callable_evidence_gvcf_block():
    """Verify evaluate_callable_evidence identifies position in gVCF END block."""
    gvcf_path = FIXTURES_DIR / "gvcf_block.vcf"
    records, _, _ = read_vcf_records(gvcf_path)

    is_callable, ev_type = evaluate_callable_evidence("chr10", 94761900, records, sample_id="HG00265")
    assert is_callable is True
    assert ev_type == ReferenceEvidence.GVCF_BLOCK
