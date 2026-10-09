from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
import yaml

from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.degrade")


@dataclass
class DegradationSpec:
    type: str  # 'none' | 'random_dropout' | 'array_like' | 'low_coverage' | 'unphased' | 'combined'
    level: float = 0.0
    seed: int = 42
    array_panel_config: Optional[str] = None

    def get_view_id(self, sample_id: str, gene: str) -> str:
        key = f"{sample_id}:{gene}:{self.type}:{self.level}:{self.seed}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_array_panel_site_ids(panel_config_path: Union[str, Path]) -> List[str]:
    """Loads retained site IDs from array panel config YAML file."""
    p_file = Path(panel_config_path)
    if not p_file.is_file():
        raise FileNotFoundError(f"Array panel config file not found: {p_file}")

    with open(p_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return [str(s) for s in data.get("retained_site_ids", [])]


def degrade_site_calls(
    site_calls_df: pd.DataFrame,
    spec: DegradationSpec,
    masks_dir: Optional[Union[str, Path]] = None,
    split_name: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies seeded degradation simulator to a site calls dataframe.

    Args:
        site_calls_df (pd.DataFrame): Input site_calls dataframe from Phase 2.
        spec (DegradationSpec): Degradation parameters specification.
        masks_dir (Optional[Path]): Directory to store frozen evaluation masks.
        split_name (Optional[str]): Split name ('train', 'val', 'calib', 'test').

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (degraded_site_calls_df, mask_metadata)
    """
    if site_calls_df.empty:
        return site_calls_df.copy(), {"type": spec.type, "dropped_sites": 0}

    degraded_df = site_calls_df.copy()
    rng = np.random.default_rng(spec.seed)

    n_total = len(degraded_df)
    dropped_mask = np.zeros(n_total, dtype=bool)

    if spec.type == "none" or spec.level == 0.0:
        pass

    elif spec.type == "random_dropout":
        p_drop = float(spec.level)
        dropped_mask = rng.random(n_total) < p_drop

        degraded_df.loc[dropped_mask, "status"] = "NOT_IN_VCF"
        degraded_df.loc[dropped_mask, "gt"] = "./."
        degraded_df.loc[dropped_mask, "allele1"] = None
        degraded_df.loc[dropped_mask, "allele2"] = None

    elif spec.type == "array_like":
        if not spec.array_panel_config:
            raise ValueError("array_panel_config required for 'array_like' degradation type.")
        retained_sites = set(load_array_panel_site_ids(spec.array_panel_config))

        dropped_mask = ~degraded_df["site_id"].astype(str).isin(retained_sites)
        degraded_df.loc[dropped_mask, "status"] = "NOT_IN_VCF"
        degraded_df.loc[dropped_mask, "gt"] = "./."
        degraded_df.loc[dropped_mask, "allele1"] = None
        degraded_df.loc[dropped_mask, "allele2"] = None

    elif spec.type == "low_coverage":
        p_drop_hom = float(spec.level) * 0.5
        p_drop_het = float(spec.level) * 1.5

        for i in range(n_total):
            st = degraded_df.iat[i, degraded_df.columns.get_loc("status")]
            p_call = p_drop_het if st == "HET" else p_drop_hom
            if rng.random() < p_call:
                dropped_mask[i] = True
                degraded_df.iat[i, degraded_df.columns.get_loc("status")] = "NO_CALL"
                degraded_df.iat[i, degraded_df.columns.get_loc("gt")] = "./."
                degraded_df.iat[i, degraded_df.columns.get_loc("allele1")] = None
                degraded_df.iat[i, degraded_df.columns.get_loc("allele2")] = None

    elif spec.type == "unphased":
        degraded_df["phased"] = False
        degraded_df["gt"] = degraded_df["gt"].astype(str).str.replace("|", "/", regex=False)

    elif spec.type == "combined":
        # Unphase all + apply random dropout
        degraded_df["phased"] = False
        degraded_df["gt"] = degraded_df["gt"].astype(str).str.replace("|", "/", regex=False)
        p_drop = float(spec.level)
        dropped_mask = rng.random(n_total) < p_drop
        degraded_df.loc[dropped_mask, "status"] = "NOT_IN_VCF"
        degraded_df.loc[dropped_mask, "gt"] = "./."
        degraded_df.loc[dropped_mask, "allele1"] = None
        degraded_df.loc[dropped_mask, "allele2"] = None

    mask_meta = {
        "degradation_type": spec.type,
        "degradation_level": spec.level,
        "seed": spec.seed,
        "total_sites": n_total,
        "dropped_sites": int(dropped_mask.sum())
    }

    # If frozen split (val, calib, test), write mask file to disk
    if split_name in ["val", "calib", "test"] and masks_dir:
        m_dir = Path(masks_dir)
        m_dir.mkdir(parents=True, exist_ok=True)
        mask_file = m_dir / f"mask_{split_name}_{spec.type}_{spec.level}_{spec.seed}.json"
        if not mask_file.is_file():
            with open(mask_file, "w", encoding="utf-8") as f:
                json.dump(mask_meta, f, indent=2)

    return degraded_df, mask_meta
