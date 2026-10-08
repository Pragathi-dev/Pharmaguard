from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml


@dataclass
class CatalogueSite:
    site_id: str
    gene: str
    chrom: str
    pos: int
    ref: str
    alt: str
    rsid: Optional[str] = None
    role: str = "defining"
    star_allele: Optional[str] = None
    source_ref: Optional[str] = None

    def __post_init__(self):
        if not self.chrom.startswith("chr"):
            self.chrom = f"chr{self.chrom}"
        self.ref = self.ref.upper().strip()
        self.alt = self.alt.upper().strip()


@dataclass
class Catalogue:
    genome_build: str
    catalogue_source: str
    sites_by_gene: Dict[str, List[CatalogueSite]] = field(default_factory=dict)
    all_sites: List[CatalogueSite] = field(default_factory=list)


def load_catalogue(
    path: Union[str, Path],
    target_build: str = "GRCh38"
) -> Catalogue:
    """
    Loads site catalogue YAML file, validates build and duplicates.

    Args:
        path (str | Path): Path to pgx_site_catalogue.yaml.
        target_build (str): Required genome build (default: "GRCh38").

    Returns:
        Catalogue: Validated Catalogue instance.

    Raises:
        FileNotFoundError: If catalogue file does not exist.
        ValueError: If build mismatch, duplicate site_id, or missing coordinates found.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Catalogue file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    build = str(data.get("genome_build", "")).strip()
    if build.upper() != target_build.upper():
        raise ValueError(
            f"Genome build mismatch: catalogue build is '{build}', expected '{target_build}'"
        )

    source = str(data.get("catalogue_source", "existing_rules")).strip()
    genes_data = data.get("genes", {})

    sites_by_gene: Dict[str, List[CatalogueSite]] = {}
    all_sites: List[CatalogueSite] = []
    seen_site_ids = set()

    for gene_name, gene_info in genes_data.items():
        gene_sites = []
        raw_sites = gene_info.get("sites", [])

        for idx, s in enumerate(raw_sites):
            site_id = str(s.get("site_id", "")).strip()
            chrom = str(s.get("chrom", "")).strip()
            pos = s.get("pos", None)
            ref = str(s.get("ref", "")).strip()
            alt = str(s.get("alt", "")).strip()

            if not site_id or not chrom or pos is None or not ref or not alt:
                raise ValueError(
                    f"Catalogue entry missing required coordinates in gene {gene_name} at index {idx}: {s}"
                )

            if site_id in seen_site_ids:
                raise ValueError(f"Duplicate site_id '{site_id}' found in catalogue at gene {gene_name}")

            seen_site_ids.add(site_id)

            site_obj = CatalogueSite(
                site_id=site_id,
                gene=gene_name,
                chrom=chrom,
                pos=int(pos),
                ref=ref,
                alt=alt,
                rsid=s.get("rsid"),
                role=str(s.get("role", "defining")),
                star_allele=s.get("star_allele"),
                source_ref=s.get("source_ref")
            )
            gene_sites.append(site_obj)
            all_sites.append(site_obj)

        sites_by_gene[gene_name] = gene_sites

    return Catalogue(
        genome_build=build,
        catalogue_source=source,
        sites_by_gene=sites_by_gene,
        all_sites=all_sites
    )
