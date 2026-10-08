from pathlib import Path
from scripts.data.check_gold_overlap import check_gold_label_overlap

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "data"


def test_check_gold_label_overlap_fixture(tmp_path):
    """Verify check_gold_label_overlap correctly calculates overlap and flags status."""
    meta_path = tmp_path / "sample_metadata.parquet"
    
    # Create sample metadata parquet from fixture panel
    import pandas as pd
    panel_df = pd.read_csv(FIXTURES_DIR / "mini_metadata.tsv", sep=r"\s+", engine="python").rename(columns={
        "sample": "sample_id", "super_pop": "superpopulation"
    })
    panel_df.to_parquet(meta_path, index=False)

    getrm_path = FIXTURES_DIR / "mini_getrm.csv"
    out_json = tmp_path / "gold_label_availability.json"

    res = check_gold_label_overlap(meta_path, getrm_path, out_json)

    assert res["gold_available"] is True
    assert "genes" in res
    assert "CYP2C19" in res["genes"]

    # Since overlap is 3 (< 30 threshold), status must be GOLD_INSUFFICIENT
    cyp2c19 = res["genes"]["CYP2C19"]
    assert cyp2c19["status"] == "GOLD_INSUFFICIENT"
    assert cyp2c19["n_overlap_1000g"] == 3
    assert out_json.is_file()


def test_check_gold_label_overlap_missing_file(tmp_path):
    """Verify check_gold_label_overlap handles absent GeT-RM gracefully."""
    meta_path = tmp_path / "sample_metadata.parquet"
    getrm_path = tmp_path / "non_existent_getrm.csv"
    out_json = tmp_path / "gold_label_availability.json"

    res = check_gold_label_overlap(meta_path, getrm_path, out_json)

    assert res["gold_available"] is False
    assert res["genes"]["CYP2C19"]["status"] == "GOLD_INSUFFICIENT"
    assert res["genes"]["CYP2C19"]["n_overlap_1000g"] == 0
