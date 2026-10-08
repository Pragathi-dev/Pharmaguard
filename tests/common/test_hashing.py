import hashlib
import pytest
from backend.common.hashing import sha256_file


def test_sha256_file_determinism(tmp_path):
    """Verify sha256_file computes correct SHA-256 hash for sample file."""
    test_file = tmp_path / "sample.txt"
    content = b"PharmaGuard Phase 0 Provenance Verification Data\n"
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    actual_hash = sha256_file(test_file)

    assert actual_hash == expected_hash
    assert len(actual_hash) == 64


def test_sha256_file_not_found():
    """Verify FileNotFoundError is raised when target file does not exist."""
    with pytest.raises(FileNotFoundError):
        sha256_file("non_existent_file_path_12345.vcf")
