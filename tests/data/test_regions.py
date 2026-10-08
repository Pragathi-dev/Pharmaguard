from pathlib import Path
import pytest
import yaml

from backend.data.regions import load_regions, TargetRegion

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGIONS_YAML = PROJECT_ROOT / "data" / "manifests" / "pgx_regions.yaml"


def test_load_regions_valid():
    """Verify load_regions correctly parses all 5 target genes from pgx_regions.yaml."""
    regions = load_regions(REGIONS_YAML, target_build="GRCh38")
    
    assert len(regions) == 5
    assert set(regions.keys()) == {"CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"}

    cyp2c19 = regions["CYP2C19"]
    assert isinstance(cyp2c19, TargetRegion)
    assert cyp2c19.chrom == "chr10"
    assert cyp2c19.start == 94757681
    assert cyp2c19.end == 94858307
    assert cyp2c19.genome_build == "GRCh38"
    assert cyp2c19.region_str == "chr10:94757681-94858307"


def test_load_regions_build_mismatch_fails(tmp_path):
    """Verify load_regions raises ValueError on genome build mismatch (GRCh37 vs GRCh38)."""
    invalid_yaml = tmp_path / "invalid_regions.yaml"
    data = {
        "genome_build": "GRCh37",
        "genes": {
            "DPYD": {"chrom": "chr1", "start": 100, "end": 200, "gene_start": 105, "gene_end": 195}
        }
    }
    invalid_yaml.write_text(yaml.dump(data), encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_regions(invalid_yaml, target_build="GRCh38")

    assert "Genome build mismatch" in str(excinfo.value)
    assert "GRCh37" in str(excinfo.value)


def test_load_regions_missing_file():
    """Verify load_regions raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_regions("non_existent_regions.yaml")
