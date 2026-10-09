import pytest
import pandas as pd
from backend.research.degrade import DegradationSpec
from backend.research.features import extract_features_for_sample_gene


def test_extract_features_degraded_rule_call():
    site_calls_deg = pd.DataFrame([
        {
            "sample_id": "HG00096", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781859:G>A",
            "chrom": "chr10", "pos": 94781859, "ref": "G", "alt": "A", "gt": "0/0", "status": "HOM_REF",
            "role": "defining", "phased": True
        }
    ])

    spec = DegradationSpec(type="random_dropout", level=0.1, seed=42)
    feat_dict = extract_features_for_sample_gene("HG00096", "CYP2C19", site_calls_deg, spec)

    assert "row_id" in feat_dict
    assert "g__CYP2C19:chr10:94781859:G>A" in feat_dict
    assert "m__CYP2C19:chr10:94781859:G>A" in feat_dict
    assert feat_dict["g__CYP2C19:chr10:94781859:G>A"] == 0
    assert feat_dict["m__CYP2C19:chr10:94781859:G>A"] == 0
    assert "rule_call_b0" in feat_dict
    assert "rule_call_b1" in feat_dict
