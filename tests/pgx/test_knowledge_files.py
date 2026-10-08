import pytest
from pathlib import Path
from backend.pgx.knowledge_files import load_knowledge, KnowledgeBase, AlleleDefinition, PhenotypeDefinition


def test_load_knowledge():
    kb_dir = Path("data/knowledge")
    kb = load_knowledge(kb_dir)

    assert isinstance(kb, KnowledgeBase)
    assert set(kb.alleles.keys()) == {"CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"}
    assert set(kb.phenotypes.keys()) == {"CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"}

    cyp2c19_a = kb.alleles["CYP2C19"]
    assert isinstance(cyp2c19_a, AlleleDefinition)
    assert cyp2c19_a.reference_allele == "*1"
    assert "*2" in cyp2c19_a.alleles

    cyp2c19_p = kb.phenotypes["CYP2C19"]
    assert isinstance(cyp2c19_p, PhenotypeDefinition)
    assert len(cyp2c19_p.rules) > 0


def test_load_knowledge_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_knowledge("non_existent_dir_123")
