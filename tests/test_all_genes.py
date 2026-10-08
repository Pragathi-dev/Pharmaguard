"""
Comprehensive Integration Tests for all 5 Pharmacogenes (CYP2C19, CYP2C9, DPYD, SLCO1B1, CYP2D6).
Phase D & E Validation.
"""

import pytest
from backend.pgx.data_model import VariantCall
from backend.pgx.gene_interpreters import (
    CYP2C9Interpreter, DPYDInterpreter, SLCO1B1Interpreter, CYP2D6Interpreter
)
from backend.pgx.interpreter import PharmacogenomicPipeline


def test_cyp2c9_phenotypes():
    interpreter = CYP2C9Interpreter()

    # Wildtype
    res_wt = interpreter.interpret("S1", [], 50)
    assert res_wt.diplotype == "*1/*1"
    assert res_wt.phenotype == "Normal Metabolizer"
    assert res_wt.activity_score == 2.0

    # *1/*2 (Heterozygous rs1799853)
    v2 = VariantCall("S2", "CYP2C9", "10", 96699917, "C", "T", "0/1", "rs1799853")
    res_het2 = interpreter.interpret("S2", [v2], 50)
    assert res_het2.diplotype == "*1/*2"
    assert res_het2.phenotype == "Normal Metabolizer"

    # *1/*3 (Heterozygous rs1057910)
    v3 = VariantCall("S3", "CYP2C9", "10", 96702047, "C", "T", "0/1", "rs1057910")
    res_het3 = interpreter.interpret("S3", [v3], 50)
    assert res_het3.diplotype == "*1/*3"
    assert res_het3.phenotype == "Intermediate Metabolizer"

    # *3/*3 (Homozygous rs1057910)
    v3_hom = VariantCall("S4", "CYP2C9", "10", 96702047, "C", "T", "1/1", "rs1057910")
    res_hom3 = interpreter.interpret("S4", [v3_hom], 50)
    assert res_hom3.diplotype == "*3/*3"
    assert res_hom3.phenotype == "Poor Metabolizer"


def test_dpyd_activity_scores():
    interpreter = DPYDInterpreter()

    # Wildtype (*1/*1, AS 2.0)
    res_wt = interpreter.interpret("S1", [], 50)
    assert res_wt.diplotype == "*1/*1"
    assert res_wt.phenotype == "Normal Metabolizer"
    assert res_wt.activity_score == 2.0

    # *1/*2A (Heterozygous rs3918290, AS 1.0)
    v2a = VariantCall("S2", "DPYD", "1", 97547947, "T", "A", "0/1", "rs3918290")
    res_2a = interpreter.interpret("S2", [v2a], 50)
    assert res_2a.diplotype in ["*1/*2A", "*2A/*1"]
    assert res_2a.phenotype == "Intermediate Metabolizer"
    assert res_2a.activity_score == 1.0

    # *2A/*2A (Homozygous rs3918290, AS 0.0)
    v2a_hom = VariantCall("S3", "DPYD", "1", 97547947, "T", "A", "1/1", "rs3918290")
    res_2a_hom = interpreter.interpret("S3", [v2a_hom], 50)
    assert res_2a_hom.diplotype == "*2A/*2A"
    assert res_2a_hom.phenotype == "Poor Metabolizer"
    assert res_2a_hom.activity_score == 0.0


def test_slco1b1_transport_functions():
    interpreter = SLCO1B1Interpreter()

    # Wildtype (*1A/*1A)
    res_wt = interpreter.interpret("S1", [], 50)
    assert res_wt.phenotype == "Normal Function"

    # *1A/*5 (Heterozygous rs4149056)
    v5 = VariantCall("S2", "SLCO1B1", "12", 21331549, "T", "C", "0/1", "rs4149056")
    res_het5 = interpreter.interpret("S2", [v5], 50)
    assert res_het5.phenotype == "Decreased Function"

    # *5/*5 (Homozygous rs4149056)
    v5_hom = VariantCall("S3", "SLCO1B1", "12", 21331549, "T", "C", "1/1", "rs4149056")
    res_hom5 = interpreter.interpret("S3", [v5_hom], 50)
    assert res_hom5.phenotype == "Poor Function"


def test_cyp2d6_and_sv_warnings():
    interpreter = CYP2D6Interpreter()

    # Wildtype (*1/*1)
    res_wt = interpreter.interpret("S1", [], 50)
    assert res_wt.diplotype == "*1/*1"
    assert res_wt.phenotype == "Normal Metabolizer"
    assert any("Structural Variant Limitation" in w for w in res_wt.warnings)

    # *4/*4 (Homozygous rs3892097)
    v4 = VariantCall("S2", "CYP2D6", "22", 42524244, "G", "A", "1/1", "rs3892097")
    res_hom4 = interpreter.interpret("S2", [v4], 50)
    assert res_hom4.diplotype == "*4/*4"
    assert res_hom4.phenotype == "Poor Metabolizer"


def test_full_pipeline_synthetic_vcf():
    pipeline = PharmacogenomicPipeline()
    vcf_path = "backend/pharmaguard_synthetic (1).vcf"

    res = pipeline.analyze_vcf_for_sample(vcf_path, target_sample_id="SAMPLE_001")

    assert "CYP2C19" in res
    assert "CYP2D6" in res
    assert "DPYD" in res
    assert "SLCO1B1" in res
    assert "CYP2C9" in res

    assert res["CYP2C19"].phenotype in ["Intermediate Metabolizer", "Poor Metabolizer"]
    assert res["CYP2D6"].phenotype == "Poor Metabolizer"
