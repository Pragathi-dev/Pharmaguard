"""
PharmaGuard Data Ingestion & Provenance Subsystem
Module interface for regions, manifests, sample metadata, and validation.
"""
from backend.data.regions import load_regions, TargetRegion
from backend.data.manifest import write_manifest_entry, verify_manifest
from backend.data.metadata import merge_sample_metadata, build_relatedness_groups

__all__ = [
    "load_regions",
    "TargetRegion",
    "write_manifest_entry",
    "verify_manifest",
    "merge_sample_metadata",
    "build_relatedness_groups"
]
