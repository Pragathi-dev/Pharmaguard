import json
import os
import tempfile
from pathlib import Path
from typing import Union, Dict, Any, List

from backend.common.hashing import sha256_file


def write_manifest_entry(
    manifest_path: Union[str, Path],
    entry: Dict[str, Any]
) -> None:
    """
    Atomically writes or updates an entry in the raw dataset manifest JSON file.

    Args:
        manifest_path (str | Path): Path to raw_manifest.json.
        entry (dict): Dictionary representing the manifest item.
    """
    file_path = Path(manifest_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    if file_path.is_file():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
                if not isinstance(entries, list):
                    entries = [entries]
        except (json.JSONDecodeError, OSError):
            entries = []

    # Update existing entry by path or append new entry
    entry_path = str(entry.get("path", ""))
    updated = False
    for i, item in enumerate(entries):
        if str(item.get("path", "")) == entry_path:
            entries[i] = entry
            updated = True
            break

    if not updated:
        entries.append(entry)

    # Atomic write via temp file
    temp_dir = file_path.parent
    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
        json.dump(entries, tf, indent=2)
        temp_name = tf.name

    os.replace(temp_name, file_path)


def verify_manifest(manifest_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Re-computes SHA-256 digests and file sizes for all files listed in the manifest.

    Args:
        manifest_path (str | Path): Path to raw_manifest.json.

    Returns:
        List[Dict[str, Any]]: List of mismatch descriptions. Empty list if all match.
    """
    file_path = Path(manifest_path)
    if not file_path.is_file():
        return [{"path": str(file_path), "issue": "manifest_not_found"}]

    with open(file_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    if not isinstance(entries, list):
        entries = [entries]

    mismatches = []
    for item in entries:
        target_path_str = item.get("path", "")
        expected_sha256 = item.get("sha256", "")
        expected_bytes = item.get("bytes", None)

        target_file = Path(target_path_str)
        if not target_file.is_file():
            mismatches.append({
                "path": target_path_str,
                "issue": "missing_file",
                "details": f"File listed in manifest does not exist at {target_file}"
            })
            continue

        actual_bytes = target_file.stat().st_size
        if expected_bytes is not None and actual_bytes != expected_bytes:
            mismatches.append({
                "path": target_path_str,
                "issue": "bytes_mismatch",
                "details": f"Expected {expected_bytes} bytes, got {actual_bytes} bytes"
            })
            continue

        actual_sha256 = sha256_file(target_file)
        if actual_sha256.lower() != expected_sha256.lower():
            mismatches.append({
                "path": target_path_str,
                "issue": "hash_mismatch",
                "details": f"Expected sha256 {expected_sha256}, got {actual_sha256}"
            })

    return mismatches
