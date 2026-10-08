import pytest
import pandas as pd
from backend.pgx.engine import run_engine
from backend.pgx.schemas import EngineMode, ConfidenceFlag


def test_modes_comparison_missing_sites():
    # Site calls missing defining site CYP2C19:chr10:94781859:G>A
    site_calls = pd.DataFrame([
        {
            "sample_id": "HG00096", "gene": "CYP2C19", "site_id": "CYP2C19:chr10:94761900:C>T",
            "chrom": "chr10", "pos": 94761900, "ref": "C", "alt": "T", "gt": "0/0", "status": "HOM_REF"
        }
    ])

    strict_res = run_engine(site_calls, mode=EngineMode.STRICT)
    refdef_res = run_engine(site_calls, mode=EngineMode.REFERENCE_DEFAULT)

    strict_row = strict_res[strict_res["gene"] == "CYP2C19"].iloc[0]
    refdef_row = refdef_res[refdef_res["gene"] == "CYP2C19"].iloc[0]

    assert strict_row["mode"] == "strict"
    assert refdef_row["mode"] == "reference_default"
    assert len(strict_row["missing_defining_sites"]) > 0
    assert strict_row["phenotype"] == "Indeterminate"
    assert refdef_row["phenotype"] == "Normal Metabolizer"
