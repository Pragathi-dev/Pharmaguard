from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union
import yaml


@dataclass
class TargetRegion:
    gene: str
    chrom: str
    gene_start: int
    gene_end: int
    start: int
    end: int
    genome_build: str
    description: str = ""

    @property
    def region_str(self) -> str:
        """Returns standard region query string format 'chr10:94757681-94858307'."""
        clean_chr = self.chrom if self.chrom.startswith("chr") else f"chr{self.chrom}"
        return f"{clean_chr}:{self.start}-{self.end}"


def load_regions(
    path: Union[str, Path],
    target_build: str = "GRCh38"
) -> Dict[str, TargetRegion]:
    """
    Loads target gene regions from YAML specification.
    Strictly validates genome build and hard-fails on build mismatch.

    Args:
        path (str | Path): Path to pgx_regions.yaml file.
        target_build (str): Required genome build (default: "GRCh38").

    Returns:
        Dict[str, TargetRegion]: Dictionary mapping gene symbol to TargetRegion instance.

    Raises:
        FileNotFoundError: If the region file does not exist.
        ValueError: If genome_build in file does not match target_build.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Target region specification file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    file_build = str(data.get("genome_build", "")).strip()
    if file_build.upper() != target_build.upper():
        raise ValueError(
            f"Genome build mismatch: expected '{target_build}', got '{file_build}' in {file_path}"
        )

    genes_raw = data.get("genes", {})
    regions = {}
    for gene_name, info in genes_raw.items():
        regions[gene_name] = TargetRegion(
            gene=gene_name,
            chrom=str(info.get("chrom")),
            gene_start=int(info.get("gene_start")),
            gene_end=int(info.get("gene_end")),
            start=int(info.get("start")),
            end=int(info.get("end")),
            genome_build=file_build,
            description=str(info.get("description", ""))
        )

    return regions
