"""
Unit tests for Integrated PMGRF Framework and CPIC Drug Recommendation Engine.
"""

import pytest
from backend.pgx.data_model import SampleGeneInterpretation
from backend.pgx.multigene_risk import MultiGeneRiskEvaluator, ComprehensivePatientProfile


def test_comprehensive_patient_profile_structure():
    sample_id = "TEST_PATIENT_01"
    interpretations = [
        SampleGeneInterpretation(sample_id, "CYP2C19", "10", 1, [], ["*1", "*2"], "*1/*2", "Intermediate Metabolizer", 0.5, "CPIC", "CONFIDENTLY_RESOLVED"), # +1, Clopidogrel Moderate
        SampleGeneInterpretation(sample_id, "CYP2C9", "10", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),        # +0, Warfarin Low
        SampleGeneInterpretation(sample_id, "DPYD", "1", 1, [], ["*1", "c.1129-5923C>G"], "*1/c.1129-5923C>G", "Intermediate Metabolizer", 1.5, "CPIC", "CONFIDENTLY_RESOLVED"), # +2, 5-FU Moderate
        SampleGeneInterpretation(sample_id, "SLCO1B1", "12", 1, [], ["*1A", "*5"], "*1A/*5", "Decreased Function", 1.0, "CPIC", "CONFIDENTLY_RESOLVED"),    # +2, Simvastatin Moderate
        SampleGeneInterpretation(sample_id, "CYP2D6", "22", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),        # +0, Codeine Low
    ]

    profile = MultiGeneRiskEvaluator.evaluate_comprehensive_patient_profile(interpretations, sample_id)

    assert profile.sample_id == "TEST_PATIENT_01"
    assert profile.pmgrf_score == 5
    assert profile.risk_category == "Moderate"
    assert len(profile.contributing_genes) == 3
    assert len(profile.drug_recommendations) == 5

    # Check exact dictionary key structure requested by user
    p_dict = profile.to_dict()
    assert set(p_dict.keys()) == {
        "sample_id", "pmgrf_score", "risk_category", "contributing_genes", "drug_recommendations"
    }

    # Verify all 5 drugs evaluated
    drugs = [d["drug_name"] for d in p_dict["drug_recommendations"]]
    assert set(drugs) == {"Clopidogrel", "Warfarin", "Fluorouracil", "Simvastatin", "Codeine"}

    rec_map = {d["drug_name"]: d for d in p_dict["drug_recommendations"]}
    assert rec_map["Clopidogrel"]["risk_level"] == "Moderate"
    assert rec_map["Warfarin"]["risk_level"] == "Low"
    assert rec_map["Fluorouracil"]["risk_level"] == "Moderate"
    assert rec_map["Simvastatin"]["risk_level"] == "Moderate"
    assert rec_map["Codeine"]["risk_level"] == "Low"
