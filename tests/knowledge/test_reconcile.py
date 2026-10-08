import pytest
import pandas as pd
from backend.knowledge.reconcile import reconcile, generate_reconciliation_report


def test_reconcile_match_and_existing_only():
    snapshot_df = pd.DataFrame([
        {
            "gene": "CYP2C19",
            "phenotype": "Poor Metabolizer",
            "drug": "clopidogrel",
            "recommendation_text": "Avoid Clopidogrel. Use an alternative antiplatelet agent such as Prasugrel or Ticagrelor unless contraindicated.",
            "classification_of_recommendation": "Strong"
        }
    ])

    items = reconcile(snapshot_recs_df=snapshot_df)
    assert len(items) > 0

    cyp2c19_pm = [i for i in items if i.gene == "CYP2C19" and i.phenotype == "Poor Metabolizer" and i.drug == "clopidogrel"]
    assert len(cyp2c19_pm) == 1
    assert cyp2c19_pm[0].status == "MATCH"
    assert cyp2c19_pm[0].text_exact_match is True

    report = generate_reconciliation_report(items)
    assert "# Knowledge Reconciliation Report" in report
    assert "MATCH" in report
