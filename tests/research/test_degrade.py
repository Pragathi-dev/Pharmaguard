import pytest
import pandas as pd
from backend.research.degrade import DegradationSpec, degrade_site_calls


def test_degrade_none():
    site_calls = pd.DataFrame([
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781859:G>A", "status": "HET", "gt": "0/1", "phased": True}
    ])

    spec = DegradationSpec(type="none", level=0.0, seed=42)
    deg_df, mask = degrade_site_calls(site_calls, spec)

    assert deg_df.equals(site_calls)
    assert mask["dropped_sites"] == 0


def test_degrade_unphased():
    site_calls = pd.DataFrame([
        {"sample_id": "S1", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94781859:G>A", "status": "HET", "gt": "0|1", "phased": True}
    ])

    spec = DegradationSpec(type="unphased", level=1.0, seed=42)
    deg_df, mask = degrade_site_calls(site_calls, spec)

    assert bool(deg_df.iloc[0]["phased"]) is False
    assert deg_df.iloc[0]["gt"] == "0/1"
