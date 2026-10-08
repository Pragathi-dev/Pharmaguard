import pytest
from parser import extract_variants

def test_sample_isolation():
    """PROVES: SAMPLE_001 data never enters SAMPLE_002's prediction."""
    vcf_path = "pharmaguard_synthetic (1).vcf"
    
    profile_1, available_1, selected_1 = extract_variants(vcf_path, "SAMPLE_001")
    profile_2, available_2, selected_2 = extract_variants(vcf_path, "SAMPLE_002")
    
    assert selected_1 == "SAMPLE_001"
    assert selected_2 == "SAMPLE_002"
    
    # CYP2D6 is a perfect test case for isolation:
    # SAMPLE_001 has 1/1 (Poor) at rs3892097. SAMPLE_002 is 0/0 (Normal) for all CYP2D6 variants.
    assert profile_1['CYP2D6']['status'] == 'Poor'
    assert profile_2['CYP2D6']['status'] == 'Normal'

def test_insufficient_evidence_handling():
    """PROVES: 8-column VCFs fallback safely, no fabricated phenotypes."""
    profile, _, _ = extract_variants("CYP2C19_1.002.vcf")
    
    # Because CYP2C19_1.002.vcf lacks a GT column, the system MUST refuse to guess
    assert profile['CYP2C19']['status'] == 'INSUFFICIENT_GENOTYPE_DATA'
    # Because CYP2D6 isn't in the file at all
    assert profile['CYP2D6']['status'] == 'INSUFFICIENT_GENOMIC_EVIDENCE'