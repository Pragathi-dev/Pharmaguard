from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class SourceEnum(str, Enum):
    CPIC = "cpic"
    PHARMVAR = "pharmvar"
    CLINPGX = "clinpgx"
    EXISTING_RULES = "existing_rules"


class LookupStatus(str, Enum):
    FOUND = "FOUND"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ProvenanceClassEnum(str, Enum):
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"


class ReconciliationStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    EXISTING_ONLY = "EXISTING_ONLY"
    SOURCE_ONLY = "SOURCE_ONLY"


@dataclass
class RecommendationRecord:
    gene: str
    phenotype: str
    source_phenotype_term: str
    drug: str
    recommendation_text: str
    guideline_id: str
    guideline_url: str
    guideline_version: str
    source: str
    kb_version: str
    retrieved_at: str
    activity_score_range: Optional[str] = None
    implication_text: Optional[str] = None
    classification_of_recommendation: Optional[str] = None
    evidence_level: Optional[str] = None
    provenance_class: str = "KNOWLEDGE_BASE"
    schema_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gene": self.gene,
            "phenotype": self.phenotype,
            "source_phenotype_term": self.source_phenotype_term,
            "activity_score_range": self.activity_score_range,
            "drug": self.drug,
            "recommendation_text": self.recommendation_text,
            "implication_text": self.implication_text,
            "classification_of_recommendation": self.classification_of_recommendation,
            "evidence_level": self.evidence_level,
            "guideline_id": self.guideline_id,
            "guideline_url": self.guideline_url,
            "guideline_version": self.guideline_version,
            "source": self.source,
            "kb_version": self.kb_version,
            "retrieved_at": self.retrieved_at,
            "provenance_class": self.provenance_class,
            "schema_version": self.schema_version
        }


@dataclass
class LookupResult:
    status: str
    gene: str
    phenotype: str
    drug: str
    recommendation_text: Optional[str] = None
    classification_of_recommendation: Optional[str] = None
    evidence_level: Optional[str] = None
    guideline_url: Optional[str] = None
    kb_version: str = "existing_rules"
    source: str = "existing_rules"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "gene": self.gene,
            "phenotype": self.phenotype,
            "drug": self.drug,
            "recommendation_text": self.recommendation_text,
            "classification_of_recommendation": self.classification_of_recommendation,
            "evidence_level": self.evidence_level,
            "guideline_url": self.guideline_url,
            "kb_version": self.kb_version,
            "source": self.source
        }


@dataclass
class SnapshotManifestFile:
    path: str
    url: str
    sha256: str
    bytes: int


@dataclass
class SnapshotManifest:
    source: str
    snapshot_date: str
    files: List[Dict[str, Any]]
    source_version: Optional[str] = None
    license_note: str = ""


@dataclass
class SnapshotInfo:
    source: str
    snapshot_date: str
    path: str
    source_version: Optional[str] = None
    license_note: str = ""
    file_count: int = 0


@dataclass
class ReconciliationItem:
    gene: str
    phenotype: str
    drug: str
    status: str  # MATCH | MISMATCH | EXISTING_ONLY | SOURCE_ONLY
    existing_text: Optional[str] = None
    source_text: Optional[str] = None
    existing_risk: Optional[str] = None
    source_classification: Optional[str] = None
    text_exact_match: bool = False
    notes: str = ""
