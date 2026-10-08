import pytest
import sys
from backend.knowledge.lookup import get_recommendations, list_supported_drugs


def test_lookup_offline_safety():
    """
    Guard test: ensures lookup API operates purely offline without performing HTTP network requests.
    """
    res = get_recommendations("CYP2C19", "Poor Metabolizer", "clopidogrel", kb_version="existing_rules")
    assert res.status == "FOUND"

    # Verify fetch script is NOT imported during lookup operations
    assert "scripts.knowledge.fetch_snapshots" not in sys.modules
