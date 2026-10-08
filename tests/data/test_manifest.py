from pathlib import Path
from backend.common.hashing import sha256_file
from backend.data.manifest import write_manifest_entry, verify_manifest


def test_write_and_verify_manifest_valid(tmp_path):
    """Verify writing manifest entry and verifying matching file."""
    sample_file = tmp_path / "sample.vcf.gz"
    content = b"##fileformat=VCFv4.2\n#CHROM\tPOS\tID\n1\t100\trs123\n"
    sample_file.write_bytes(content)

    manifest_path = tmp_path / "manifest.json"
    entry = {
        "path": str(sample_file),
        "url": "https://example.org/sample.vcf.gz",
        "sha256": sha256_file(sample_file),
        "bytes": len(content),
        "retrieved_at": "2026-10-08T22:00:00Z",
        "genome_build": "GRCh38",
        "provenance_class": "REAL_PATIENT_GENOTYPE"
    }

    write_manifest_entry(manifest_path, entry)
    mismatches = verify_manifest(manifest_path)

    assert mismatches == [], f"Expected 0 mismatches, got: {mismatches}"


def test_verify_manifest_detects_hash_mismatch(tmp_path):
    """Verify verify_manifest detects file tampering or hash mismatch."""
    sample_file = tmp_path / "data.vcf.gz"
    sample_file.write_bytes(b"Original Content\n")

    manifest_path = tmp_path / "manifest.json"
    entry = {
        "path": str(sample_file),
        "url": "https://example.org/data.vcf.gz",
        "sha256": sha256_file(sample_file),
        "bytes": sample_file.stat().st_size,
        "genome_build": "GRCh38",
        "provenance_class": "REAL_PATIENT_GENOTYPE"
    }

    write_manifest_entry(manifest_path, entry)

    # Tamper with file
    sample_file.write_bytes(b"Tampered Content\n")

    mismatches = verify_manifest(manifest_path)
    assert len(mismatches) == 1
    assert mismatches[0]["issue"] in ["hash_mismatch", "bytes_mismatch"]


def test_verify_manifest_detects_missing_file(tmp_path):
    """Verify verify_manifest detects missing files."""
    missing_file = tmp_path / "non_existent.vcf.gz"
    manifest_path = tmp_path / "manifest.json"

    entry = {
        "path": str(missing_file),
        "sha256": "0" * 64,
        "bytes": 100
    }
    write_manifest_entry(manifest_path, entry)

    mismatches = verify_manifest(manifest_path)
    assert len(mismatches) == 1
    assert mismatches[0]["issue"] == "missing_file"
