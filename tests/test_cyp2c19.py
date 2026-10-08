"""
Unit Tests for CYP2C19 Pharmacogenomic Interpretation (Phase C Validation).
Verifies star-allele calling, diplotype assignment, and CPIC phenotype mapping with GRCh37 VCF allele orientations.
"""

import pytest
from backend.pgx.data_model import VariantCall
from backend.pgx.gene_interpreters import CYP2C19Interpreter


def test_cyp2c19_wildtype():
    """Wildtype (no detected non-reference variants) must yield *1/*1 (Normal Metabolizer)."""
    interpreter = CYP2C19Interpreter()
    v = VariantCall("SAMPLE_WT", "CYP2C19", "10", 96521422, "A", "G", "1/1", "rs4244285")
    res = interpreter.interpret("SAMPLE_WT", variants=[v], variants_examined_count=50)

    assert res.gene == "CYP2C19"
    assert res.assigned_star_alleles == ["*1", "*1"]
    assert res.diplotype == "*1/*1"
    assert res.phenotype == "Normal Metabolizer"
    assert res.activity_score == 1.0


def test_cyp2c19_heterozygous_star2():
    """Heterozygous rs4244285 (0/1 A/G) must yield *1/*2 (Intermediate Metabolizer)."""
    interpreter = CYP2C19Interpreter()
    v = VariantCall(
        sample_id="SAMPLE_HET2", gene="CYP2C19", chrom="10",
        pos=96521422, ref="A", alt="G", genotype="0/1", rsid="rs4244285"
    )
    res = interpreter.interpret("SAMPLE_HET2", variants=[v], variants_examined_count=50)

    assert res.assigned_star_alleles == ["*1", "*2"]
    assert res.diplotype == "*1/*2"
    assert res.phenotype == "Intermediate Metabolizer"
    assert res.activity_score == 0.5


def test_cyp2c19_homozygous_star2():
    """Homozygous rs4244285 (0/0 A/A) must yield *2/*2 (Poor Metabolizer)."""
    interpreter = CYP2C19Interpreter()
    v = VariantCall(
        sample_id="SAMPLE_HOM2", gene="CYP2C19", chrom="10",
        pos=96521422, ref="A", alt="G", genotype="0/0", rsid="rs4244285"
    )
    res = interpreter.interpret("SAMPLE_HOM2", variants=[v], variants_examined_count=50)

    assert res.assigned_star_alleles == ["*2", "*2"]
    assert res.diplotype == "*2/*2"
    assert res.phenotype == "Poor Metabolizer"
    assert res.activity_score == 0.0


def test_cyp2c19_compound_star2_star17():
    """Compound heterozygous *2/*17 must yield Intermediate Metabolizer (CPIC 2022 rule)."""
    interpreter = CYP2C19Interpreter()
    v2 = VariantCall(
        sample_id="SAMPLE_2_17", gene="CYP2C19", chrom="10",
        pos=96521422, ref="A", alt="G", genotype="0/1", rsid="rs4244285"
    )
    v17 = VariantCall(
        sample_id="SAMPLE_2_17", gene="CYP2C19", chrom="10",
        pos=96501538, ref="C", alt="T", genotype="0/1", rsid="rs12248560"
    )
    res = interpreter.interpret("SAMPLE_2_17", variants=[v2, v17], variants_examined_count=50)

    assert set(res.assigned_star_alleles) == {"*2", "*17"}
    assert res.diplotype in ["*17/*2", "*2/*17"]
    assert res.phenotype == "Intermediate Metabolizer"
    assert res.activity_score == 0.5


def test_cyp2c19_rapid_star17():
    """Heterozygous rs12248560 (0/1) must yield *1/*17 (Rapid Metabolizer)."""
    interpreter = CYP2C19Interpreter()
    v17 = VariantCall(
        sample_id="SAMPLE_17", gene="CYP2C19", chrom="10",
        pos=96501538, ref="C", alt="T", genotype="0/1", rsid="rs12248560"
    )
    res = interpreter.interpret("SAMPLE_17", variants=[v17], variants_examined_count=50)

    assert res.assigned_star_alleles == ["*1", "*17"]
    assert res.diplotype == "*1/*17"
    assert res.phenotype == "Rapid Metabolizer"
    assert res.activity_score == 1.5


def test_cyp2c19_ultrarapid_star17():
    """Homozygous rs12248560 (1/1) must yield *17/*17 (Ultrarapid Metabolizer)."""
    interpreter = CYP2C19Interpreter()
    v17 = VariantCall(
        sample_id="SAMPLE_UR", gene="CYP2C19", chrom="10",
        pos=96501538, ref="C", alt="T", genotype="1/1", rsid="rs12248560"
    )
    res = interpreter.interpret("SAMPLE_UR", variants=[v17], variants_examined_count=50)

    assert res.assigned_star_alleles == ["*17", "*17"]
    assert res.diplotype == "*17/*17"
    assert res.phenotype == "Ultrarapid Metabolizer"
    assert res.activity_score == 2.0
