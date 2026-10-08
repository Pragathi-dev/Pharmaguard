from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml


@dataclass
class StarAlleleSpec:
    name: str
    function: str
    activity_score: Optional[float]
    defining_sites: List[str]


@dataclass
class AlleleDefinition:
    gene: str
    source: str
    source_version: str
    genome_build: str
    reference_allele: str
    alleles: Dict[str, StarAlleleSpec]


@dataclass
class PhenotypeRule:
    condition: Optional[str] = None
    min_as: Optional[float] = None
    max_as: Optional[float] = None
    phenotype: str = "Indeterminate"
    activity_score: Optional[float] = None


@dataclass
class PhenotypeDefinition:
    gene: str
    source: str
    source_version: str
    mapping_type: str
    rules: List[PhenotypeRule]


@dataclass
class KnowledgeBase:
    alleles: Dict[str, AlleleDefinition] = field(default_factory=dict)
    phenotypes: Dict[str, PhenotypeDefinition] = field(default_factory=dict)
    kb_version: str = "cpic_2022_v1"


def load_knowledge(kb_dir: Union[str, Path]) -> KnowledgeBase:
    """
    Loads and validates all star-allele and phenotype mapping YAML files from knowledge directory.

    Args:
        kb_dir (str | Path): Path to data/knowledge directory.

    Returns:
        KnowledgeBase: KnowledgeBase container object.

    Raises:
        FileNotFoundError: If expected knowledge files are missing.
        ValueError: If YAML schemas are invalid.
    """
    kb_path = Path(kb_dir)
    alleles_dir = kb_path / "alleles"
    phenotypes_dir = kb_path / "phenotypes"

    if not alleles_dir.is_dir() or not phenotypes_dir.is_dir():
        raise FileNotFoundError(f"Knowledge subdirectories missing at {kb_path} (expected 'alleles' and 'phenotypes')")

    target_genes = ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]
    
    alleles_dict = {}
    phenotypes_dict = {}

    for gene in target_genes:
        a_file = alleles_dir / f"{gene}.yaml"
        p_file = phenotypes_dir / f"{gene}.yaml"

        if not a_file.is_file():
            raise FileNotFoundError(f"Allele definition file missing for {gene}: {a_file}")
        if not p_file.is_file():
            raise FileNotFoundError(f"Phenotype mapping file missing for {gene}: {p_file}")

        # Parse Alleles YAML
        with open(a_file, "r", encoding="utf-8") as f:
            a_data = yaml.safe_load(f)
        
        allele_specs = {}
        for item in a_data.get("alleles", []):
            name = str(item.get("name", "")).strip()
            spec = StarAlleleSpec(
                name=name,
                function=str(item.get("function", "")),
                activity_score=item.get("activity_score", None),
                defining_sites=[str(s) for s in item.get("defining_sites", [])]
            )
            allele_specs[name] = spec

        alleles_dict[gene] = AlleleDefinition(
            gene=gene,
            source=str(a_data.get("source", "existing_rules")),
            source_version=str(a_data.get("source_version", "1.0")),
            genome_build=str(a_data.get("genome_build", "GRCh38")),
            reference_allele=str(a_data.get("reference_allele", "*1")),
            alleles=allele_specs
        )

        # Parse Phenotypes YAML
        with open(p_file, "r", encoding="utf-8") as f:
            p_data = yaml.safe_load(f)

        rules_list = []
        for r in p_data.get("rules", []):
            rules_list.append(PhenotypeRule(
                condition=r.get("condition"),
                min_as=float(r["min_as"]) if "min_as" in r else None,
                max_as=float(r["max_as"]) if "max_as" in r else None,
                phenotype=str(r.get("phenotype", "Indeterminate")),
                activity_score=r.get("activity_score")
            ))

        phenotypes_dict[gene] = PhenotypeDefinition(
            gene=gene,
            source=str(p_data.get("source", "cpic")),
            source_version=str(p_data.get("source_version", "1.0")),
            mapping_type=str(p_data.get("mapping_type", "diplotype_function")),
            rules=rules_list
        )

    return KnowledgeBase(
        alleles=alleles_dict,
        phenotypes=phenotypes_dict,
        kb_version="cpic_2022_v1"
    )
