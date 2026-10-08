import pytest
from backend.pgx.drug_recommendation_engine import DrugRecommendationEngine


def test_existing_drug_recommendations_pgx_regression():
    # Verify pre-existing recommendation engine remains fully compatible
    rec = DrugRecommendationEngine.get_recommendation_for_drug(
        "Clopidogrel",
        {"gene": "CYP2C19", "phenotype": "Poor Metabolizer", "diplotype": "*2/*2"}
    )
    assert rec is not None
    assert rec.risk_level == "High"
    assert "Prasugrel" in rec.recommendation or "Ticagrelor" in rec.recommendation
