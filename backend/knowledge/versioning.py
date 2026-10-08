import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml

from backend.knowledge.schema import SnapshotInfo


def active_kb_version(config_path: Optional[Union[str, Path]] = None) -> str:
    """
    Returns active KB version string from config/base.yaml.

    Returns:
        str: Active KB version flag (e.g. 'existing_rules' or 'cpic:2026-10-09').
    """
    if config_path is None:
        config_path = Path("config/base.yaml")
    
    cfg_file = Path(config_path)
    if cfg_file.is_file():
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return str(data.get("knowledge", {}).get("active_source", "existing_rules"))

    return "existing_rules"


def list_snapshots(snapshot_dir: Optional[Union[str, Path]] = None) -> List[SnapshotInfo]:
    """
    Discovers all available knowledge base snapshots in data/knowledge/<source>/<date>/.

    Returns:
        List[SnapshotInfo]: List of snapshot information objects.
    """
    if snapshot_dir is None:
        snapshot_dir = Path("data/knowledge")

    base_path = Path(snapshot_dir)
    snapshots = []

    if not base_path.is_dir():
        return []

    sources = ["cpic", "pharmvar", "clinpgx"]
    for src in sources:
        src_path = base_path / src
        if not src_path.is_dir():
            continue

        for date_dir in sorted(src_path.iterdir(), reverse=True):
            if date_dir.is_dir() and not date_dir.name.startswith("."):
                manifest_file = date_dir / "snapshot_manifest.json"
                source_ver = None
                license_note = ""
                file_count = len([f for f in date_dir.glob("*") if f.is_file()])

                if manifest_file.is_file():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            m_data = json.load(f)
                        source_ver = m_data.get("source_version")
                        license_note = m_data.get("license_note", "")
                    except Exception:
                        pass

                snapshots.append(SnapshotInfo(
                    source=src,
                    snapshot_date=date_dir.name,
                    path=str(date_dir),
                    source_version=source_ver,
                    license_note=license_note,
                    file_count=file_count
                ))

    return snapshots


def get_snapshot_dir_for_version(
    kb_version: str,
    snapshot_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Resolves kb_version string to absolute snapshot directory path.

    Raises:
        FileNotFoundError: If matching snapshot directory is missing.
    """
    if snapshot_dir is None:
        snapshot_dir = Path("data/knowledge")

    base_path = Path(snapshot_dir)

    if kb_version.startswith("snapshot:"):
        kb_version = kb_version.replace("snapshot:", "")

    if ":" in kb_version:
        source, date_str = kb_version.split(":", 1)
        target_dir = base_path / source / date_str
        if not target_dir.is_dir():
            raise FileNotFoundError(
                f"Missing snapshot for active source '{kb_version}' at {target_dir}. "
                f"Run 'python scripts/knowledge/fetch_snapshots.py --source {source}' to download."
            )
        return target_dir

    # Fallback to latest snapshot across sources
    snapshots = list_snapshots(snapshot_dir)
    if not snapshots:
        raise FileNotFoundError(
            f"No knowledge base snapshots found in {base_path}. "
            f"Run scripts/knowledge/fetch_snapshots.py to create initial snapshot."
        )

    return Path(snapshots[0].path)
