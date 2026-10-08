from datetime import datetime, timezone
from pathlib import Path
from typing import Union, Optional, Dict, Any

from backend.common.enums import ProvenanceClass
from backend.common.hashing import sha256_file


def make_provenance(
    cls: Union[ProvenanceClass, str],
    source: str,
    version: str,
    path: Optional[Union[str, Path]] = None,
    schema_version: str = "1.0"
) -> Dict[str, Any]:
    """
    Constructs a standardized, validated provenance metadata dictionary.

    Args:
        cls (ProvenanceClass | str): Allowed provenance class enum or exact string name.
        source (str): Human-readable dataset or repository identifier.
        version (str): Source release tag, commit hash, or version string.
        path (str | Path | None): Optional path to compute source file SHA-256 digest.
        schema_version (str): Metadata schema specification version (default: "1.0").

    Returns:
        dict: Standardized provenance dictionary.

    Raises:
        ValueError: If `cls` is not a valid `ProvenanceClass` enum value.
    """
    # Validate provenance class
    if isinstance(cls, ProvenanceClass):
        prov_class_str = cls.value
    elif isinstance(cls, str):
        try:
            prov_class_str = ProvenanceClass(cls).value
        except ValueError:
            valid_options = [e.value for e in ProvenanceClass]
            raise ValueError(
                f"Invalid provenance class '{cls}'. Must be one of: {valid_options}"
            )
    else:
        raise ValueError(f"Invalid type for provenance class: {type(cls)}")

    # Compute SHA-256 if file path is provided
    file_sha256 = ""
    if path is not None:
        file_sha256 = sha256_file(path)

    timestamp_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "provenance_class": prov_class_str,
        "source": str(source),
        "source_version": str(version),
        "retrieved_at": timestamp_iso,
        "sha256": file_sha256,
        "schema_version": str(schema_version)
    }
