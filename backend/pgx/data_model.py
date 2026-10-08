"""
Normalized Data Models for Pharmacogenomic (PGx) Variant Interpretation Layer.
Strictly decoupled, GRCh37 compatible, and deterministic.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class VariantCall:
    """Represents a single genomic variant call from VCF."""
    sample_id: str
    gene: str
    chrom: str
    pos: int
    ref: str
    alt: str
    genotype: str  # e.g., '0/1', '1/1', '0|1', '1|0', '1|1'
    rsid: Optional[str] = None
    is_phased: bool = False
    depth: Optional[int] = None
    quality: Optional[float] = None

    @property
    def key(self) -> str:
        """Unique GRCh37 variant identifier: chrom:pos:ref:alt"""
        return f"{self.chrom}:{self.pos}:{self.ref}:{self.alt}"


@dataclass
class StarAlleleDefinition:
    """Reference definition of a PharmVar star allele."""
    gene: str
    star_allele: str  # e.g., '*2'
    defining_variants: List[Dict[str, Any]]  # List of dicts with chrom, pos, ref, alt, rsid, impact
    function_status: str  # 'Normal Function', 'Decreased Function', 'No Function', 'Increased Function'
    activity_score: float  # e.g., 0.0, 0.5, 1.0, 2.0
    evidence_source: str = "PharmVar v5.2 (GRCh37)"
    description: str = ""


@dataclass
class StarAlleleCall:
    """Assigned star allele for an individual haplotype/allele."""
    star_allele: str  # e.g., '*2'
    function_status: str
    activity_score: float
    core_variants: List[VariantCall] = field(default_factory=list)
    evidence_source: str = "PharmVar v5.2 (GRCh37)"


@dataclass
class DiplotypeCall:
    """Assigned diplotype pair for a sample."""
    gene: str
    diplotype: str  # e.g., '*1/*2'
    allele_1: StarAlleleCall
    allele_2: StarAlleleCall
    is_unambiguous: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class PhenotypeResult:
    """CPIC standardized phenotype determination."""
    gene: str
    diplotype: str
    phenotype: str  # 'Normal Metabolizer', 'Intermediate Metabolizer', 'Poor Metabolizer', etc.
    activity_score: Optional[float]
    evidence_source: str = "CPIC Guidelines"
    guideline_version: str = "CPIC 2022"
    clinical_notes: str = ""


@dataclass
class SampleGeneInterpretation:
    """Complete per-sample, per-gene PGx interpretation result."""
    sample_id: str
    gene: str
    chrom: str
    variants_examined_count: int
    detected_variants: List[Dict[str, Any]]
    assigned_star_alleles: List[str]
    diplotype: str
    phenotype: str
    activity_score: Optional[float]
    evidence_source: str
    status_code: str  # 'CONFIDENTLY_RESOLVED', 'INFERRED_WILDTYPE', 'AMBIGUOUS_DIPLOTYPE', 'SUCCESS_WITH_SV_LIMITATIONS', 'INSUFFICIENT_GENOMIC_EVIDENCE'
    candidate_diplotypes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    clinical_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "gene": self.gene,
            "chrom": self.chrom,
            "variants_examined_count": self.variants_examined_count,
            "detected_variants": self.detected_variants,
            "assigned_star_alleles": self.assigned_star_alleles,
            "diplotype": self.diplotype,
            "phenotype": self.phenotype,
            "activity_score": self.activity_score,
            "evidence_source": self.evidence_source,
            "status_code": self.status_code,
            "candidate_diplotypes": self.candidate_diplotypes,
            "warnings": self.warnings,
            "clinical_notes": self.clinical_notes,
        }
