from backend.genomics.normalize import harmonize_contig, normalize_variant


def test_harmonize_contig():
    """Verify contig string harmonization between 'chr10' and '10'."""
    assert harmonize_contig("10", target_has_chr=True) == "chr10"
    assert harmonize_contig("chr10", target_has_chr=True) == "chr10"
    assert harmonize_contig("chr10", target_has_chr=False) == "10"
    assert harmonize_contig("10", target_has_chr=False) == "10"


def test_normalize_variant_trimming():
    """Verify indel allele prefix and suffix trimming."""
    # AGT > A -> GT > "" at pos+1
    chrom, pos, ref, alt = normalize_variant("10", 100, "AGT", "A")
    assert chrom == "chr10"
    assert pos == 101
    assert ref == "GT"
    assert alt == ""

    # Simple SNP -> no pos shift
    chrom, pos, ref, alt = normalize_variant("chr22", 500, "C", "T")
    assert chrom == "chr22"
    assert pos == 500
    assert ref == "C"
    assert alt == "T"
