"""
Unit tests for PharmaGuard Multi-Gene Risk Framework (PMGRF).
"""

import pytest
from backend.pgx.data_model import SampleGeneInterpretation
from backend.pgx.multigene_risk import MultiGeneRiskEvaluator, PHENOTYPE_SEVERITY_SCORES


def test_phenotype_severity_scores_mapping():
    evaluator = MultiGeneRiskEvaluator()

    # CYP2C19
    assert evaluator.get_phenotype_severity_score("CYP2C19", "Normal Metabolizer") == 0
    assert evaluator.get_phenotype_severity_score("CYP2C19", "Intermediate Metabolizer") == 1
    assert evaluator.get_phenotype_severity_score("CYP2C19", "Poor Metabolizer") == 2
    assert evaluator.get_phenotype_severity_score("CYP2C19", "Rapid Metabolizer") == 1
    assert evaluator.get_phenotype_severity_score("CYP2C19", "Ultrarapid Metabolizer") == 2

    # CYP2C9
    assert evaluator.get_phenotype_severity_score("CYP2C9", "Normal Metabolizer") == 0
    assert evaluator.get_phenotype_severity_score("CYP2C9", "Intermediate Metabolizer") == 1
    assert evaluator.get_phenotype_severity_score("CYP2C9", "Poor Metabolizer") == 2

    # DPYD
    assert evaluator.get_phenotype_severity_score("DPYD", "Normal Metabolizer") == 0
    assert evaluator.get_phenotype_severity_score("DPYD", "Intermediate Metabolizer") == 2
    assert evaluator.get_phenotype_severity_score("DPYD", "Poor Metabolizer") == 3

    # SLCO1B1
    assert evaluator.get_phenotype_severity_score("SLCO1B1", "Normal Function") == 0
    assert evaluator.get_phenotype_severity_score("SLCO1B1", "Decreased Function") == 2
    assert evaluator.get_phenotype_severity_score("SLCO1B1", "Poor Function") == 3

    # CYP2D6
    assert evaluator.get_phenotype_severity_score("CYP2D6", "Normal Metabolizer") == 0
    assert evaluator.get_phenotype_severity_score("CYP2D6", "Intermediate Metabolizer") == 1
    assert evaluator.get_phenotype_severity_score("CYP2D6", "Poor Metabolizer") == 2
    assert evaluator.get_phenotype_severity_score("CYP2D6", "Ultrarapid Metabolizer") == 2


def test_low_risk_composite_score():
    sample_id = "SAMPLE_LOW_RISK"
    interpretations = [
        SampleGeneInterpretation(sample_id, "CYP2C19", "10", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 1.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation(sample_id, "CYP2C9", "10", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation(sample_id, "DPYD", "1", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation(sample_id, "SLCO1B1", "12", 1, [], ["*1A", "*1A"], "*1A/*1A", "Normal Function", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation(sample_id, "CYP2D6", "22", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
    ]

    result = MultiGeneRiskEvaluator.evaluate_sample_risk(interpretations, sample_id)

    assert result.sample_id == "SAMPLE_LOW_RISK"
    assert result.total_score == 0
    assert result.risk_category == "Low"
    assert len(result.contributing_genes) == 0
    assert len(result.evaluated_genes) == 5
    assert "Normal / Baseline" in result.explanation


def test_moderate_risk_composite_score():
    sample_id = "SAMPLE_MOD_RISK"
    interpretations = {
        "CYP2C19": SampleGeneInterpretation(sample_id, "CYP2C19", "10", 1, [], ["*1", "*2"], "*1/*2", "Intermediate Metabolizer", 0.5, "CPIC", "CONFIDENTLY_RESOLVED"), # +1
        "SLCO1B1": SampleGeneInterpretation(sample_id, "SLCO1B1", "12", 1, [], ["*1A", "*5"], "*1A/*5", "Decreased Function", 1.0, "CPIC", "CONFIDENTLY_RESOLVED"),   # +2
        "CYP2D6": SampleGeneInterpretation(sample_id, "CYP2D6", "22", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),        # +0
    }

    result = MultiGeneRiskEvaluator.evaluate_sample_risk(interpretations, sample_id)

    assert result.total_score == 3
    assert result.risk_category == "Moderate"
    assert len(result.contributing_genes) == 2
    genes_contrib = [g["gene"] for g in result.contributing_genes]
    assert "CYP2C19" in genes_contrib
    assert "SLCO1B1" in genes_contrib
    
    # Check output dictionary keys requirement
    res_dict = result.to_dict()
    assert "total_score" in res_dict
    assert "risk_category" in res_dict
    assert "contributing_genes" in res_dict
    assert "explanation" in res_dict


def test_high_risk_composite_score():
    sample_id = "SAMPLE_HIGH_RISK"
    interpretations = [
        {"gene": "CYP2C19", "phenotype": "Poor Metabolizer", "diplotype": "*2/*2"},     # +2
        {"gene": "DPYD", "phenotype": "Poor Metabolizer", "diplotype": "*2A/*2A"},       # +3
        {"gene": "SLCO1B1", "phenotype": "Decreased Function", "diplotype": "*1A/*5"},   # +2
    ]

    result = MultiGeneRiskEvaluator.evaluate_sample_risk(interpretations, sample_id)

    assert result.total_score == 7
    assert result.risk_category == "High"
    assert len(result.contributing_genes) == 3
    assert "HIGH" in result.explanation
