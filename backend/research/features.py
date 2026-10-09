import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd

from backend.genomics.catalogue import Catalogue
from backend.pgx.engine import interpret_gene
from backend.pgx.schemas import EngineMode
from backend.pgx.knowledge_files import KnowledgeBase, load_knowledge
from backend.research.degrade import DegradationSpec
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.features")

_KB_CACHE: Optional[KnowledgeBase] = None


def get_cached_kb() -> KnowledgeBase:
    global _KB_CACHE
    if _KB_CACHE is None:
        _KB_CACHE = load_knowledge("data/knowledge")
    return _KB_CACHE


def extract_features_for_sample_gene(
    sample_id: str,
    gene: str,
    site_calls_degraded_df: pd.DataFrame,
    spec: DegradationSpec,
    catalogue: Optional[Catalogue] = None,
    include_ancestry: bool = False,
    superpopulation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extracts ML feature representation for a single (sample, gene, degraded_view).
    Computes rule_call features strictly on the DEGRADED view.

    Returns:
        Dict[str, Any]: Feature row dictionary.
    """
    kb = get_cached_kb()
    view_id = spec.get_view_id(sample_id, gene)
    row_id = hashlib.sha256(f"{sample_id}:{gene}:{view_id}".encode("utf-8")).hexdigest()[:16]

    feature_dict: Dict[str, Any] = {
        "row_id": row_id,
        "sample_id": sample_id,
        "gene": gene,
        "view_id": view_id,
        "degradation_type": spec.type,
        "degradation_level": float(spec.level),
        "degradation_seed": int(spec.seed),
    }

    # 1. Site genotype dosage (g__) and missing indicators (m__)
    n_defining = 0
    n_missing_def = 0
    n_tag = 0
    n_missing_tag = 0
    phased_count = 0
    observed_count = 0

    if not site_calls_degraded_df.empty:
        for idx, row in site_calls_degraded_df.iterrows():
            site_id = str(row.get("site_id", f"{gene}:{row.get('chrom')}:{row.get('pos')}:{row.get('ref')}>{row.get('alt')}"))
            st = str(row.get("status", "NOT_IN_VCF"))
            role = str(row.get("role", "defining"))
            is_phased = bool(row.get("phased", False))

            if role == "defining":
                n_defining += 1
            else:
                n_tag += 1

            if st in ["NOT_IN_VCF", "NO_CALL", "FILTERED", "LOW_QUALITY", "MULTIALLELIC"]:
                g_val = -1
                m_val = 1
                if role == "defining":
                    n_missing_def += 1
                else:
                    n_missing_tag += 1
            else:
                m_val = 0
                observed_count += 1
                if is_phased:
                    phased_count += 1

                if st == "HOM_REF":
                    g_val = 0
                elif st == "HET":
                    g_val = 1
                elif st == "HOM_ALT":
                    g_val = 2
                else:
                    g_val = -1
                    m_val = 1

            feature_dict[f"g__{site_id}"] = g_val
            feature_dict[f"m__{site_id}"] = m_val

    n_obs_def = n_defining - n_missing_def
    frac_obs_def = (n_obs_def / n_defining) if n_defining > 0 else 1.0
    phased_frac = (phased_count / observed_count) if observed_count > 0 else 0.0

    feature_dict["n_missing_defining"] = n_missing_def
    feature_dict["n_missing_tag"] = n_missing_tag
    feature_dict["frac_observed_defining"] = float(frac_obs_def)
    feature_dict["phased_fraction"] = float(phased_frac)

    # 2. Compute rule_call features strictly on DEGRADED view
    b0_res = interpret_gene(
        sample_id=sample_id,
        gene=gene,
        site_calls_df=site_calls_degraded_df,
        kb=kb,
        mode=EngineMode.REFERENCE_DEFAULT
    )
    b1_res = interpret_gene(
        sample_id=sample_id,
        gene=gene,
        site_calls_df=site_calls_degraded_df,
        kb=kb,
        mode=EngineMode.STRICT
    )

    feature_dict["rule_call_b0"] = b0_res.phenotype
    feature_dict["rule_call_b1"] = b1_res.phenotype
    feature_dict["rule_conf_b1"] = b1_res.confidence_flag

    if include_ancestry:
        feature_dict["ancestry"] = superpopulation

    feature_dict["parent_row_id"] = None
    feature_dict["synthetic_flag"] = 0
    feature_dict["provenance_class"] = "AUGMENTED_REAL" if spec.type != "none" else "REAL_PATIENT_GENOTYPE"
    feature_dict["schema_version"] = "1.0"

    return feature_dict
