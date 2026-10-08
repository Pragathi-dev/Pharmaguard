"""
Mandatory Regression & Validation Test Suite for Pharmacogenomic (PGx) Interpretation Layer.
Validates strand orientation, risk-allele matching, unphased ambiguity handling,
wildtype resolution statuses, and structural variant limitations.
"""

import pytest
from backend.pgx.data_model import VariantCall
from backend.pgx.gene_interpreters import (
    CYP2C19Interpreter, DPYDInterpreter, CYP2C9Interpreter, SLCO1B1Interpreter, CYP2D6Interpreter
)
from backend.pgx.interpreter import PharmacogenomicPipeline


def test_cyp2c19_star2_allele_orientation():
    """
    CYP2C19*2 (rs4244285) in GRCh37:
    REF = A (risk allele), ALT = G (wildtype allele).
    GT 1/1 (G/G) = *1/*1 (Normal Metabolizer).
    GT 0/1 (A/G) = *1/*2 (Intermediate Metabolizer).
    GT 0/0 (A/A) = *2/*2 (Poor Metabolizer).
    """
    interpreter = CYP2C19Interpreter()

    # 1/1 (G/G) -> Wildtype (*1/*1)
    v_wt = VariantCall("S1", "CYP2C19", "10", 96521422, "A", "G", "1/1", "rs4244285")
    res_wt = interpreter.interpret("S1", [v_wt], 50)
    assert res_wt.diplotype == "*1/*1"
    assert res_wt.phenotype == "Normal Metabolizer"
    assert res_wt.status_code == "INFERRED_WILDTYPE"

    # 0/1 (A/G) -> Heterozygous (*1/*2)
    v_het = VariantCall("S2", "CYP2C19", "10", 96521422, "A", "G", "0/1", "rs4244285")
    res_het = interpreter.interpret("S2", [v_het], 50)
    assert res_het.diplotype == "*1/*2"
    assert res_het.phenotype == "Intermediate Metabolizer"
    assert res_het.status_code == "CONFIDENTLY_RESOLVED"

    # 0/0 (A/A) -> Homozygous Mutated (*2/*2)
    v_hom = VariantCall("S3", "CYP2C19", "10", 96521422, "A", "G", "0/0", "rs4244285")
    res_hom = interpreter.interpret("S3", [v_hom], 50)
    assert res_hom.diplotype == "*2/*2"
    assert res_hom.phenotype == "Poor Metabolizer"
    assert res_hom.status_code == "CONFIDENTLY_RESOLVED"


def test_dpyd_hapb3_allele_orientation():
    """
    DPYD HapB3 (rs75017182) in GRCh37:
    REF = G (HapB3 risk allele), ALT = A (wildtype allele).
    GT 1/1 (A/A) = *1/*1 (Normal Metabolizer, AS 2.0).
    GT 0/1 (G/A) = *1/HapB3 (Intermediate Metabolizer, AS 1.5).
    GT 0/0 (G/G) = HapB3/HapB3 (Intermediate Metabolizer, AS 1.0).
    """
    interpreter = DPYDInterpreter()

    # 1/1 (A/A) -> Wildtype (*1/*1)
    v_wt = VariantCall("S1", "DPYD", "1", 98348885, "G", "A", "1/1", "rs75017182")
    res_wt = interpreter.interpret("S1", [v_wt], 50)
    assert res_wt.diplotype == "*1/*1"
    assert res_wt.phenotype == "Normal Metabolizer"
    assert res_wt.activity_score == 2.0

    # 0/1 (G/A) -> *1/c.1129-5923C>G
    v_het = VariantCall("S2", "DPYD", "1", 98348885, "G", "A", "0/1", "rs75017182")
    res_het = interpreter.interpret("S2", [v_het], 50)
    assert res_het.diplotype == "*1/c.1129-5923C>G"
    assert res_het.phenotype == "Intermediate Metabolizer"
    assert res_het.activity_score == 1.5

    # 0/0 (G/G) -> c.1129-5923C>G/c.1129-5923C>G
    v_hom = VariantCall("S3", "DPYD", "1", 98348885, "G", "A", "0/0", "rs75017182")
    res_hom = interpreter.interpret("S3", [v_hom], 50)
    assert res_hom.diplotype == "c.1129-5923C>G/c.1129-5923C>G"
    assert res_hom.phenotype == "Intermediate Metabolizer"
    assert res_hom.activity_score == 1.0


def test_unphased_double_heterozygote_ambiguity():
    """
    Unphased CYP2C19 *2 (rs4244285) + *17 (rs12248560) double heterozygote (0/1 and 0/1).
    Should return status_code = 'AMBIGUOUS_DIPLOTYPE' with candidate diplotypes.
    """
    interpreter = CYP2C19Interpreter()

    v2 = VariantCall("S1", "CYP2C19", "10", 96521422, "A", "G", "0/1", "rs4244285", is_phased=False)
    v17 = VariantCall("S1", "CYP2C19", "10", 96501538, "C", "T", "0/1", "rs12248560", is_phased=False)

    res = interpreter.interpret("S1", [v2, v17], 50)
    assert res.status_code == "AMBIGUOUS_DIPLOTYPE"
    assert "*2/*17" in res.candidate_diplotypes or "*1/*2,17" in res.candidate_diplotypes
    assert any("Unphased compound" in w for w in res.warnings)


def test_phased_double_heterozygote_resolution():
    """
    Phased CYP2C19 *2 + *17 (0|1 and 1|0).
    Should resolve deterministically without ambiguity warning.
    """
    interpreter = CYP2C19Interpreter()

    v2 = VariantCall("S1", "CYP2C19", "10", 96521422, "A", "G", "0|1", "rs4244285", is_phased=True)
    v17 = VariantCall("S1", "CYP2C19", "10", 96501538, "C", "T", "1|0", "rs12248560", is_phased=True)

    res = interpreter.interpret("S1", [v2, v17], 50)
    assert res.status_code == "CONFIDENTLY_RESOLVED"
    assert res.diplotype == "*2/*17"


def test_cyp2d6_sv_limitation_status():
    """
    CYP2D6 interpretations must explicitly assign SUCCESS_WITH_SV_LIMITATIONS.
    """
    interpreter = CYP2D6Interpreter()

    v4 = VariantCall("S1", "CYP2D6", "22", 42524244, "G", "A", "0/1", "rs3892097")
    res = interpreter.interpret("S1", [v4], 50)
    assert res.status_code == "SUCCESS_WITH_SV_LIMITATIONS"
    assert any("Structural Variant Limitation" in w for w in res.warnings)
