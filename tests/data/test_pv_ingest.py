from pathlib import Path
import pytest
import pandas as pd
from scripts.data.ingest_pv_context import ingest_pharmacovigilance_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "data"
CONFIG_YAML = PROJECT_ROOT / "config" / "pv_columns.yaml"


def test_ingest_pv_data_valid(tmp_path):
    """Verify valid PV CSV is ingested, stamped PHARMACOVIGILANCE_CONTEXT, and saved to Parquet."""
    in_csv = FIXTURES_DIR / "mini_pv.csv"
    out_parquet = tmp_path / "pv_context.parquet"

    success = ingest_pharmacovigilance_data(in_csv, CONFIG_YAML, out_parquet)

    assert success is True
    assert out_parquet.is_file()

    df = pd.read_parquet(out_parquet)
    assert len(df) == 5
    assert "provenance_class" in df.columns
    assert (df["provenance_class"] == "PHARMACOVIGILANCE_CONTEXT").all()


def test_ingest_pv_data_security_rejection():
    """Verify PV ingestion SECURITY REJECTION when CSV contains forbidden sample_id column."""
    invalid_csv = FIXTURES_DIR / "mini_pv_invalid.csv"
    out_parquet = Path("tmp_should_not_exist.parquet")

    with pytest.raises(ValueError) as excinfo:
        ingest_pharmacovigilance_data(invalid_csv, CONFIG_YAML, out_parquet)

    assert "SECURITY REJECTION" in str(excinfo.value)
    assert "forbidden sample-linking" in str(excinfo.value)
    assert not out_parquet.is_file()


def test_ingest_pv_data_absent(tmp_path):
    """Verify ingest_pharmacovigilance_data handles absent file gracefully."""
    absent_csv = tmp_path / "absent_pv.csv"
    out_parquet = tmp_path / "pv_context.parquet"

    success = ingest_pharmacovigilance_data(absent_csv, CONFIG_YAML, out_parquet)
    assert success is False
    assert not out_parquet.is_file()
