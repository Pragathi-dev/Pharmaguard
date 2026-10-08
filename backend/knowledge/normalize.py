from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
from backend.knowledge.schema import RecommendationRecord, ProvenanceClassEnum


_PHENOTYPE_MAP_CACHE: Optional[Dict[str, str]] = None


def get_phenotype_term_map() -> Dict[str, str]:
    """Loads and caches standard phenotype mapping table from config/phenotype_term_map.yaml."""
    global _PHENOTYPE_MAP_CACHE
    if _PHENOTYPE_MAP_CACHE is not None:
        return _PHENOTYPE_MAP_CACHE

    map_path = Path("config/phenotype_term_map.yaml")
    if map_path.is_file():
        with open(map_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _PHENOTYPE_MAP_CACHE = {str(k).lower().strip(): str(v).strip() for k, v in data.get("mappings", {}).items()}
    else:
        # Hardcoded fallback mapping table for offline robustness
        _PHENOTYPE_MAP_CACHE = {
            "normal metabolizer": "Normal Metabolizer",
            "intermediate metabolizer": "Intermediate Metabolizer",
            "poor metabolizer": "Poor Metabolizer",
            "rapid metabolizer": "Rapid Metabolizer",
            "ultrarapid metabolizer": "Ultrarapid Metabolizer",
            "normal function": "Normal Function",
            "decreased function": "Decreased Function",
            "poor function": "Poor Function",
            "indeterminate": "Indeterminate"
        }

    return _PHENOTYPE_MAP_CACHE


def map_phenotype_term(raw_term: str) -> Tuple[str, bool]:
    """
    Maps a raw source-specific phenotype term to standard CPIC term.

    Args:
        raw_term (str): As published in source.

    Returns:
        Tuple[str, bool]: (cpic_standard_term, is_mapped)
    """
    if not raw_term:
        return ("Indeterminate", False)

    cleaned = str(raw_term).lower().strip()
    mapping_dict = get_phenotype_term_map()

    if cleaned in mapping_dict:
        return (mapping_dict[cleaned], True)

    # Partial substring check if exact match missed
    if "poor" in cleaned or "deficient" in cleaned:
        return ("Poor Metabolizer" if "metabolizer" in cleaned or "function" not in cleaned else "Poor Function", True)
    elif "intermediate" in cleaned or "decreased" in cleaned:
        return ("Intermediate Metabolizer" if "function" not in cleaned else "Decreased Function", True)
    elif "ultrarapid" in cleaned:
        return ("Ultrarapid Metabolizer", True)
    elif "rapid" in cleaned:
        return ("Rapid Metabolizer", True)
    elif "normal" in cleaned or "extensive" in cleaned:
        return ("Normal Metabolizer" if "function" not in cleaned else "Normal Function", True)

    return (raw_term, False)


def normalize_drug_name(raw_drug: str) -> str:
    """Normalizes drug name to lowercase generic format."""
    if not raw_drug:
        return ""
    d = str(raw_drug).lower().strip()
    aliases = {
        "5-fu": "fluorouracil",
        "5-fluorouracil": "fluorouracil",
        "capecitabine": "fluorouracil",
        "fluorouracil / 5-fu": "fluorouracil"
    }
    return aliases.get(d, d)


def create_recommendation_record(
    gene: str,
    raw_phenotype: str,
    drug: str,
    recommendation_text: str,
    guideline_id: str,
    guideline_url: str,
    guideline_version: str,
    source: str,
    snapshot_date: str,
    retrieved_at: str,
    activity_score_range: Optional[str] = None,
    implication_text: Optional[str] = None,
    classification_of_recommendation: Optional[str] = None,
    evidence_level: Optional[str] = None
) -> Tuple[RecommendationRecord, bool]:
    """
    Constructs a normalized RecommendationRecord from raw attributes.

    Returns:
        Tuple[RecommendationRecord, bool]: (record, is_mapped)
    """
    mapped_phenotype, is_mapped = map_phenotype_term(raw_phenotype)
    norm_drug = normalize_drug_name(drug)
    kb_ver = f"{source}:{snapshot_date}"

    record = RecommendationRecord(
        gene=str(gene).upper().strip(),
        phenotype=mapped_phenotype,
        source_phenotype_term=str(raw_phenotype).strip(),
        activity_score_range=activity_score_range,
        drug=norm_drug,
        recommendation_text=str(recommendation_text).strip(),
        implication_text=implication_text,
        classification_of_recommendation=classification_of_recommendation,
        evidence_level=evidence_level,
        guideline_id=str(guideline_id),
        guideline_url=str(guideline_url),
        guideline_version=str(guideline_version),
        source=str(source),
        kb_version=kb_ver,
        retrieved_at=str(retrieved_at),
        provenance_class=ProvenanceClassEnum.KNOWLEDGE_BASE.value,
        schema_version="1.0"
    )

    return record, is_mapped
