import json
import pytest
from pathlib import Path
from backend.knowledge.loader import load_snapshot_manifest, load_raw_snapshot, load_normalized_recommendations


def test_load_normalized_recommendations_fallback(tmp_path):
    df = load_normalized_recommendations(tmp_path / "non_existent.parquet")
    assert df.empty
    assert "gene" in df.columns
    assert "recommendation_text" in df.columns


def test_load_raw_snapshot_from_fixture():
    fixture_path = Path("tests/fixtures/knowledge/cpic_fixture.json")
    assert fixture_path.is_file()

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["gene"] == "CYP2C19"
