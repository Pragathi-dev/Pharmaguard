from pathlib import Path
import pandas as pd
from backend.data.metadata import build_relatedness_groups, merge_sample_metadata

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "data"


def test_build_relatedness_groups_connected_components():
    """Verify pedigree connected components assign same relatedness group to family members."""
    ped_df = pd.DataFrame([
        {"family_id": "1463", "sample_id": "NA12878", "father_id": "NA12877", "mother_id": "NA12889"},
        {"family_id": "1463", "sample_id": "NA12877", "father_id": "0", "mother_id": "0"},
        {"family_id": "1463", "sample_id": "NA12889", "father_id": "0", "mother_id": "0"},
        {"family_id": "FAM_SINGLE", "sample_id": "HG00096", "father_id": "0", "mother_id": "0"}
    ])

    groups = build_relatedness_groups(ped_df)

    # NA12878, NA12877, NA12889 are in the same family -> same group lead (NA12877)
    assert groups["NA12878"] == groups["NA12877"]
    assert groups["NA12877"] == groups["NA12889"]
    assert groups["NA12878"].startswith("REL_GRP_")

    # HG00096 is a singleton
    assert groups["HG00096"].startswith("REL_SINGLETON_")


def test_merge_sample_metadata_fixture(tmp_path):
    """Verify merge_sample_metadata joins panel and pedigree files into Parquet."""
    panel_path = FIXTURES_DIR / "mini_metadata.tsv"
    ped_path = FIXTURES_DIR / "mini_pedigree.tsv"
    out_parquet = tmp_path / "sample_metadata.parquet"

    df = merge_sample_metadata(panel_path, ped_path, out_parquet)

    assert len(df) == 8
    assert "sample_id" in df.columns
    assert "population" in df.columns
    assert "superpopulation" in df.columns
    assert "relatedness_group" in df.columns
    assert "provenance_class" in df.columns

    assert out_parquet.is_file()
    parquet_df = pd.read_parquet(out_parquet)
    assert len(parquet_df) == 8
    assert (parquet_df["provenance_class"] == "REAL_PATIENT_GENOTYPE").all()
