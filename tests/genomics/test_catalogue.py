from pathlib import Path
import pytest
import yaml

from backend.genomics.catalogue import load_catalogue, Catalogue

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOGUE_YAML = PROJECT_ROOT / "config" / "pgx_site_catalogue.yaml"


def test_load_catalogue_valid():
    """Verify loading pgx_site_catalogue.yaml correctly populates all target genes."""
    cat = load_catalogue(CATALOGUE_YAML, target_build="GRCh38")
    assert isinstance(cat, Catalogue)
    assert cat.genome_build == "GRCh38"
    assert len(cat.sites_by_gene) == 5
    assert len(cat.all_sites) >= 10


def test_load_catalogue_build_mismatch_fails(tmp_path):
    """Verify load_catalogue raises ValueError on GRCh37 build mismatch."""
    yaml_file = tmp_path / "bad_build.yaml"
    data = {"genome_build": "GRCh37", "genes": {}}
    yaml_file.write_text(yaml.dump(data), encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_catalogue(yaml_file, target_build="GRCh38")

    assert "Genome build mismatch" in str(excinfo.value)


def test_load_catalogue_duplicate_site_id_rejected(tmp_path):
    """Verify duplicate site_id in catalogue raises ValueError."""
    yaml_file = tmp_path / "dup_sites.yaml"
    data = {
        "genome_build": "GRCh38",
        "genes": {
            "CYP2C19": {
                "sites": [
                    {"site_id": "SITE1", "chrom": "chr10", "pos": 100, "ref": "A", "alt": "G"},
                    {"site_id": "SITE1", "chrom": "chr10", "pos": 200, "ref": "C", "alt": "T"}
                ]
            }
        }
    }
    yaml_file.write_text(yaml.dump(data), encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_catalogue(yaml_file, target_build="GRCh38")

    assert "Duplicate site_id 'SITE1'" in str(excinfo.value)
