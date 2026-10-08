import pytest
from pathlib import Path
from backend.knowledge.versioning import active_kb_version, list_snapshots, get_snapshot_dir_for_version


def test_active_kb_version_default():
    ver = active_kb_version()
    assert ver == "existing_rules"


def test_list_snapshots():
    snaps = list_snapshots()
    assert isinstance(snaps, list)


def test_get_snapshot_dir_for_version_missing():
    with pytest.raises(FileNotFoundError):
        get_snapshot_dir_for_version("cpic:1999-01-01")
