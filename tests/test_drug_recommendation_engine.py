"""
Unit tests for CPIC-Guideline-Based Drug Recommendation Engine with Explainability Layer.
"""

import pytest
from backend.pgx.data_model import SampleGeneInterpretation
from backend.pgx.drug_recommendation_engine import (
    DrugRecommendationEngine, DrugRecommendation
)


def test_clopidogrel_explainable_recommendations():
    # CYP2C19 Intermediate (*1/*2)
    interp_int = SampleGeneInterpretation("S1", "CYP2C19", "10", 1, [], ["*1", "*2"], "*1/*2", "Intermediate Metabolizer", 0.5, "CPIC", "CONFIDENTLY_RESOLVED")
    rec_int = DrugRecommendationEngine.get_recommendation_for_drug("Clopidogrel", interp_int)
    assert rec_int.risk_level == "Moderate"
    assert "Avoid Clopidogrel" in rec_int.recommendation
    assert "Patient carries CYP2C19 *1/*2 resulting in an Intermediate Metabolizer phenotype." in rec_int.explanation
    assert "Prasugrel" in rec_int.explanation
    assert rec_int.dashboard_metadata["action_required"] is True
    assert "Prasugrel" in rec_int.dashboard_metadata["alternative_drugs_suggested"]


def test_warfarin_explainable_recommendations():
    # CYP2C9 Poor (*3/*3)
    interp_poor = {"gene": "CYP2C9", "diplotype": "*3/*3", "phenotype": "Poor Metabolizer"}
    rec_poor = DrugRecommendationEngine.get_recommendation_for_drug("Warfarin", interp_poor)
    assert rec_poor.risk_level == "High"
    assert "Patient carries CYP2C9 *3/*3 resulting in a Poor Metabolizer phenotype." in rec_poor.explanation
    assert "50-80%" in rec_poor.explanation
    assert rec_poor.dashboard_metadata["action_required"] is True


def test_fluorouracil_explainable_recommendations():
    # DPYD Intermediate (*1/c.1129-5923C>G)
    interp_int = {"gene": "DPYD", "diplotype": "*1/c.1129-5923C>G", "phenotype": "Intermediate Metabolizer"}
    rec_int = DrugRecommendationEngine.get_recommendation_for_drug("Fluorouracil", interp_int)
    assert rec_int.risk_level == "Moderate"
    assert "Patient carries DPYD *1/c.1129-5923C>G resulting in an Intermediate Metabolizer phenotype." in rec_int.explanation
    assert "25-50%" in rec_int.explanation


def test_simvastatin_explainable_recommendations():
    # SLCO1B1 Decreased Function (*1A/*5)
    interp_dec = {"gene": "SLCO1B1", "diplotype": "*1A/*5", "phenotype": "Decreased Function"}
    rec_dec = DrugRecommendationEngine.get_recommendation_for_drug("Simvastatin", interp_dec)
    assert rec_dec.risk_level == "Moderate"
    assert "Patient carries SLCO1B1 *1A/*5 resulting in a Decreased Function phenotype." in rec_dec.explanation
    assert "<=20 mg" in rec_dec.explanation


def test_codeine_explainable_recommendations():
    # CYP2D6 Ultrarapid (*1/*1xN)
    interp_ur = {"gene": "CYP2D6", "diplotype": "*1/*1xN", "phenotype": "Ultrarapid Metabolizer"}
    rec_ur = DrugRecommendationEngine.get_recommendation_for_drug("Codeine", interp_ur)
    assert rec_ur.risk_level == "High"
    assert "Patient carries CYP2D6 *1/*1xN resulting in an Ultrarapid Metabolizer phenotype." in rec_ur.explanation
    assert "respiratory depression" in rec_ur.explanation


def test_get_all_drug_recommendations_with_explanations():
    interpretations = [
        SampleGeneInterpretation("S1", "CYP2C19", "10", 1, [], ["*1", "*2"], "*1/*2", "Intermediate Metabolizer", 0.5, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation("S1", "CYP2C9", "10", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation("S1", "DPYD", "1", 1, [], ["*1", "c.1129-5923C>G"], "*1/c.1129-5923C>G", "Intermediate Metabolizer", 1.5, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation("S1", "SLCO1B1", "12", 1, [], ["*1A", "*5"], "*1A/*5", "Decreased Function", 1.0, "CPIC", "CONFIDENTLY_RESOLVED"),
        SampleGeneInterpretation("S1", "CYP2D6", "22", 1, [], ["*1", "*1"], "*1/*1", "Normal Metabolizer", 2.0, "CPIC", "CONFIDENTLY_RESOLVED"),
    ]

    all_recs = DrugRecommendationEngine.get_all_drug_recommendations(interpretations)
    assert len(all_recs) == 5

    for r in all_recs:
        d_dict = r.to_dict()
        assert "explanation" in d_dict
        assert "dashboard_metadata" in d_dict
        assert d_dict["explanation"].startswith("Patient carries")
        assert d_dict["dashboard_metadata"]["gene"] == r.associated_gene
