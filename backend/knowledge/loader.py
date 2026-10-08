import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd

from backend.knowledge.schema import SnapshotManifest, RecommendationRecord


def load_snapshot_manifest(snapshot_dir: Union[str, Path]) -> SnapshotManifest:
    """
    Loads snapshot_manifest.json from a given snapshot directory.

    Raises:
        FileNotFoundError: If manifest file is missing.
    """
    s_path = Path(snapshot_dir)
    manifest_file = s_path / "snapshot_manifest.json"

    if not manifest_file.is_file():
        raise FileNotFoundError(f"Snapshot manifest not found at {manifest_file}")

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return SnapshotManifest(
        source=data.get("source", "unknown"),
        snapshot_date=data.get("snapshot_date", "unknown"),
        files=data.get("files", []),
        source_version=data.get("source_version"),
        license_note=data.get("license_note", "")
    )


def load_raw_snapshot(source: str, snapshot_date: str, base_dir: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Loads raw snapshot JSON data for a specific source and date."""
    if base_dir is None:
        base_dir = Path("data/knowledge")

    target_dir = Path(base_dir) / source / snapshot_date
    raw_file = target_dir / f"{source}_raw_recommendations.json"

    if not raw_file.is_file():
        # Fallback search for any .json file in date dir
        json_files = [f for f in target_dir.glob("*.json") if f.name != "snapshot_manifest.json"]
        if json_files:
            raw_file = json_files[0]
        else:
            raise FileNotFoundError(f"No raw snapshot data file found in {target_dir}")

    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, list) else [data]


def load_normalized_recommendations(parquet_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Loads normalized recommendations Parquet table.
    If file doesn't exist, returns empty DataFrame with expected schema.
    """
    if parquet_path is None:
        parquet_path = Path("data/knowledge/recommendations/recommendations.parquet")

    p_file = Path(parquet_path)
    if p_file.is_file():
        return pd.read_parquet(p_file)

    # Return empty DataFrame with expected schema
    return pd.DataFrame(columns=[
        "gene", "phenotype", "source_phenotype_term", "activity_score_range",
        "drug", "recommendation_text", "implication_text",
        "classification_of_recommendation", "evidence_level", "guideline_id",
        "guideline_url", "guideline_version", "source", "kb_version",
        "retrieved_at", "provenance_class", "schema_version"
    ])
