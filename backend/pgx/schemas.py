from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class EngineMode(str, Enum):
    REFERENCE_DEFAULT = "reference_default"
    STRICT = "strict"


class ConfidenceFlag(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"
    STRUCTURAL_UNRESOLVED = "STRUCTURAL_UNRESOLVED"


@dataclass
class GeneResult:
    sample_id: str
    gene: str
    mode: str
    diplotype: Optional[str]
    allele1: Optional[str]
    allele2: Optional[str]
    candidate_diplotypes: List[str] = field(default_factory=list)
    phenotype: str = "Indeterminate"
    activity_score: Optional[float] = None
    missing_defining_sites: List[str] = field(default_factory=list)
    n_defining_sites: int = 0
    n_observed_defining: int = 0
    confidence_flag: str = "UNRESOLVED"
    phasing_ambiguous: bool = False
    structural_variation_assessed: bool = True
    only_catalogued_variants_assessed: bool = False
    engine_version: str = "3.0.0"
    kb_version: str = "cpic_2022_v1"
    provenance_class: str = "DERIVED_SILVER_LABEL"
    schema_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "gene": self.gene,
            "mode": self.mode,
            "diplotype": self.diplotype,
            "allele1": self.allele1,
            "allele2": self.allele2,
            "candidate_diplotypes": self.candidate_diplotypes,
            "phenotype": self.phenotype,
            "activity_score": self.activity_score,
            "missing_defining_sites": self.missing_defining_sites,
            "n_defining_sites": self.n_defining_sites,
            "n_observed_defining": self.n_observed_defining,
            "confidence_flag": self.confidence_flag,
            "phasing_ambiguous": self.phasing_ambiguous,
            "structural_variation_assessed": self.structural_variation_assessed,
            "only_catalogued_variants_assessed": self.only_catalogued_variants_assessed,
            "engine_version": self.engine_version,
            "kb_version": self.kb_version,
            "provenance_class": self.provenance_class,
            "schema_version": self.schema_version
        }
