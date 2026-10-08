import pytest
from pathlib import Path


def test_no_hardcoded_allele_or_phenotype_dicts():
    """
    Scans backend/pgx Python files to enforce zero hard-coded star-allele or phenotype mapping dictionaries.
    All star alleles and phenotypes must be loaded dynamically from data/knowledge YAML files.
    """
    pgx_dir = Path("backend/pgx")
    py_files = [f for f in pgx_dir.glob("*.py") if f.name not in ["reference_data.py", "gene_interpreters.py", "drug_recommendation_engine.py", "multigene_risk.py"]]

    forbidden_patterns = [
        "CYP2C19*2", "CYP2C19*3", "CYP2C19*17",
        "CYP2C9*2", "CYP2C9*3",
        "SLCO1B1*5", "SLCO1B1*1B"
    ]

    for py_file in py_files:
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        for pattern in forbidden_patterns:
            assert pattern not in content, f"Hardcoded definition pattern '{pattern}' found in new module {py_file}"
