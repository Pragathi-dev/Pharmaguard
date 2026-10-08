"""
PharmaGuard Knowledge Layer Package
Versioned CPIC / PharmVar / ClinPGx Knowledge Base and Lookup API
"""
from backend.knowledge.schema import (
    RecommendationRecord,
    LookupResult,
    LookupStatus,
    SnapshotManifest,
    SnapshotInfo,
    ReconciliationItem,
    ReconciliationStatus,
    SourceEnum,
    ProvenanceClassEnum
)
from backend.knowledge.loader import (
    load_snapshot_manifest,
    load_raw_snapshot,
    load_normalized_recommendations
)
from backend.knowledge.normalize import map_phenotype_term, create_recommendation_record
from backend.knowledge.versioning import active_kb_version, list_snapshots, get_snapshot_dir_for_version
from backend.knowledge.lookup import get_recommendations, list_supported_drugs
from backend.knowledge.reconcile import reconcile, generate_reconciliation_report

__all__ = [
    "RecommendationRecord",
    "LookupResult",
    "LookupStatus",
    "SnapshotManifest",
    "SnapshotInfo",
    "ReconciliationItem",
    "ReconciliationStatus",
    "SourceEnum",
    "ProvenanceClassEnum",
    "load_snapshot_manifest",
    "load_raw_snapshot",
    "load_normalized_recommendations",
    "map_phenotype_term",
    "create_recommendation_record",
    "active_kb_version",
    "list_snapshots",
    "get_snapshot_dir_for_version",
    "get_recommendations",
    "list_supported_drugs",
    "reconcile",
    "generate_reconciliation_report"
]
