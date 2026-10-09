"""
PharmaGuard Research Dataset & Leakage Guard Package
"""
from backend.research.labels import build_labels
from backend.research.splits import make_splits, save_splits, make_loso_splits
from backend.research.degrade import DegradationSpec, degrade_site_calls
from backend.research.features import extract_features_for_sample_gene
from backend.research.guards import (
    LeakageError,
    assert_no_leakage,
    assert_no_split_leakage,
    verify_split_hash,
    assert_no_forbidden_features
)
from backend.research.build_dataset import build_research_dataset

__all__ = [
    "build_labels",
    "make_splits",
    "save_splits",
    "make_loso_splits",
    "DegradationSpec",
    "degrade_site_calls",
    "extract_features_for_sample_gene",
    "LeakageError",
    "assert_no_leakage",
    "assert_no_split_leakage",
    "verify_split_hash",
    "assert_no_forbidden_features",
    "build_research_dataset"
]
