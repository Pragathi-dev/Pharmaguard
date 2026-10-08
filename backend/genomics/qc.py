from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import yaml

from backend.genomics.enums import SiteObservationStatus


@dataclass
class QcConfig:
    min_dp: int = 10
    min_gq: int = 20
    min_region_call_rate: float = 0.80
    allowed_filters: List[str] = None

    def __post_init__(self):
        if self.allowed_filters is None:
            self.allowed_filters = ["PASS", ".", "0", ""]


def load_qc_config(path: Union[str, Path]) -> QcConfig:
    """
    Loads QC thresholds from yaml file.
    """
    p = Path(path)
    if not p.is_file():
        return QcConfig()

    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    cfg = data.get("qc_thresholds", {})
    return QcConfig(
        min_dp=int(cfg.get("min_dp", 10)),
        min_gq=int(cfg.get("min_gq", 20)),
        min_region_call_rate=float(cfg.get("min_region_call_rate", 0.80)),
        allowed_filters=cfg.get("allowed_filters", ["PASS", ".", "0", ""])
    )


def apply_genotype_qc(
    vcf_filter: Optional[str],
    dp: Optional[int],
    gq: Optional[int],
    qc_cfg: QcConfig
) -> Tuple[Optional[SiteObservationStatus], str]:
    """
    Applies FILTER, DP, and GQ quality thresholds.

    Returns:
        Tuple[Optional[SiteObservationStatus], str]: (status_override, filter_reason)
    """
    clean_filter = str(vcf_filter).strip() if vcf_filter else "PASS"
    if clean_filter and clean_filter not in qc_cfg.allowed_filters:
        return SiteObservationStatus.FILTERED, clean_filter

    if dp is not None and dp < qc_cfg.min_dp:
        return SiteObservationStatus.LOW_QUALITY, f"DP_{dp}_below_{qc_cfg.min_dp}"

    if gq is not None and gq < qc_cfg.min_gq:
        return SiteObservationStatus.LOW_QUALITY, f"GQ_{gq}_below_{qc_cfg.min_gq}"

    return None, "PASS"


def compute_sample_qc(
    site_calls_df: pd.DataFrame,
    qc_cfg: QcConfig = None
) -> pd.DataFrame:
    """
    Computes per-sample, per-gene QC metrics table.
    """
    if qc_cfg is None:
        qc_cfg = QcConfig()

    if site_calls_df is None or site_calls_df.empty:
        return pd.DataFrame(columns=[
            "sample_id", "gene", "n_catalogued", "n_observed", "n_not_in_vcf",
            "n_no_call", "n_low_quality", "region_call_rate", "qc_pass", "any_unphased"
        ])

    records = []
    grouped = site_calls_df.groupby(["sample_id", "gene"])

    for (sid, gene), group in grouped:
        n_cat = len(group)
        n_not_vcf = (group["status"] == SiteObservationStatus.NOT_IN_VCF.value).sum()
        n_no_call = (group["status"] == SiteObservationStatus.NO_CALL.value).sum()
        n_low_qual = (group["status"] == SiteObservationStatus.LOW_QUALITY.value).sum()
        
        # Observed means called genotype present
        n_obs = n_cat - n_not_vcf - n_no_call
        call_rate = round(float(n_obs / n_cat), 4) if n_cat > 0 else 0.0
        qc_pass = bool(call_rate >= qc_cfg.min_region_call_rate)

        any_unphased = bool((~group["phased"]).any()) if "phased" in group.columns else True

        records.append({
            "sample_id": sid,
            "gene": gene,
            "n_catalogued": int(n_cat),
            "n_observed": int(n_obs),
            "n_not_in_vcf": int(n_not_vcf),
            "n_no_call": int(n_no_call),
            "n_low_quality": int(n_low_qual),
            "region_call_rate": call_rate,
            "qc_pass": qc_pass,
            "any_unphased": any_unphased
        })

    return pd.DataFrame(records)
