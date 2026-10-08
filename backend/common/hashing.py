import hashlib
from pathlib import Path
from typing import Union


def sha256_file(path: Union[str, Path]) -> str:
    """
    Computes the SHA-256 checksum hex string for a given file.
    Reads the file in 1 MB chunks to handle large genomic files efficiently.

    Args:
        path (str | Path): Path to the target file.

    Returns:
        str: Lowercase 64-character SHA-256 hex digest.

    Raises:
        FileNotFoundError: If the specified path does not exist.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Cannot calculate SHA-256 hash. File not found: {file_path}")

    sha256_hash = hashlib.sha256()
    chunk_size = 1024 * 1024  # 1 MB chunking

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()
