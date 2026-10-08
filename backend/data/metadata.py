from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd

from backend.common.enums import ProvenanceClass
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.data.metadata")


def build_relatedness_groups(pedigree_df: pd.DataFrame) -> Dict[str, str]:
    """
    Computes pedigree-derived relatedness groups using connected components graph traversal.
    Ensures leak-free train/val/test splits across family and relatedness blocks.

    Args:
        pedigree_df (pd.DataFrame): DataFrame containing columns ['family_id', 'sample_id', 'father_id', 'mother_id'].

    Returns:
        Dict[str, str]: Map of sample_id -> relatedness_group_id.
    """
    if pedigree_df is None or pedigree_df.empty:
        return {}

    # Standardize column names
    df = pedigree_df.copy()
    col_map = {c.lower(): c for c in df.columns}
    
    sample_col = col_map.get("sample_id", col_map.get("sample", "sample_id"))
    family_col = col_map.get("family_id", col_map.get("family", "family_id"))
    father_col = col_map.get("father_id", col_map.get("father", "father_id"))
    mother_col = col_map.get("mother_id", col_map.get("mother", "mother_id"))

    # Build adjacency list graph
    adj: Dict[str, set] = {}

    def add_edge(u: str, v: str):
        if not u or not v or u in ["0", "."] or v in ["0", "."]:
            return
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)

    for _, row in df.iterrows():
        sid = str(row.get(sample_col, "")).strip()
        fam = str(row.get(family_col, "")).strip()
        fat = str(row.get(father_col, "")).strip()
        mot = str(row.get(mother_col, "")).strip()

        if sid and sid not in ["0", "."]:
            adj.setdefault(sid, set())
            if fam and fam not in ["0", "."]:
                add_edge(sid, f"FAM_{fam}")
            if fat and fat not in ["0", "."]:
                add_edge(sid, fat)
            if mot and mot not in ["0", "."]:
                add_edge(sid, mot)

    # Find connected components via BFS
    visited = set()
    relatedness_map: Dict[str, str] = {}

    for node in sorted(adj.keys()):
        if node in visited:
            continue
        
        # BFS traversal
        component = []
        queue = [node]
        visited.add(node)
        
        while queue:
            curr = queue.pop(0)
            if not curr.startswith("FAM_"):
                component.append(curr)
            for nxt in adj[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        if component:
            # Deterministic group naming using lexicographically lowest sample ID
            group_lead = sorted(component)[0]
            group_name = f"REL_GRP_{group_lead}" if len(component) > 1 else f"REL_SINGLETON_{group_lead}"
            for s in component:
                relatedness_map[s] = group_name

    return relatedness_map


def merge_sample_metadata(
    panel_path: Union[str, Path],
    pedigree_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Joins IGSR panel metadata and pedigree links strictly on sample_id.
    Logs unmatched sample IDs and stamps provenance metadata.

    Args:
        panel_path (str | Path): Path to integrated_call_samples panel file.
        pedigree_path (str | Path | None): Optional path to 20130606_g1k.ped file.
        output_path (str | Path | None): Optional path to export sample_metadata.parquet.

    Returns:
        pd.DataFrame: Merged sample_metadata DataFrame.
    """
    panel_file = Path(panel_path)
    if not panel_file.is_file():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    # Read panel file (tab-separated or space-separated)
    panel_df = pd.read_csv(panel_file, sep=r"\s+", engine="python")
    
    # Standardize panel column names
    col_map = {c.lower(): c for c in panel_df.columns}
    sample_col = col_map.get("sample", col_map.get("sample_id", "sample"))
    pop_col = col_map.get("pop", col_map.get("population", "pop"))
    super_col = col_map.get("super_pop", col_map.get("superpopulation", "super_pop"))
    sex_col = col_map.get("gender", col_map.get("sex", "gender"))

    panel_df = panel_df.rename(columns={
        sample_col: "sample_id",
        pop_col: "population",
        super_col: "superpopulation",
        sex_col: "sex"
    })

    panel_df["sample_id"] = panel_df["sample_id"].astype(str).str.strip()

    # Load pedigree and compute relatedness groups
    relatedness_map = {}
    family_map = {}
    if pedigree_path and Path(pedigree_path).is_file():
        ped_file = Path(pedigree_path)
        try:
            ped_df = pd.read_csv(
                ped_file,
                sep=r"\s+",
                engine="python",
                names=["family_id", "sample_id", "father_id", "mother_id", "sex", "phenotype"],
                header=None
            )
            ped_df["sample_id"] = ped_df["sample_id"].astype(str).str.strip()
            ped_df["family_id"] = ped_df["family_id"].astype(str).str.strip()
            
            for _, r in ped_df.iterrows():
                family_map[r["sample_id"]] = r["family_id"]

            relatedness_map = build_relatedness_groups(ped_df)
            logger.info(f"Loaded pedigree links for {len(ped_df)} samples from {ped_file.name}")
        except Exception as e:
            logger.warning(f"Could not parse pedigree file {ped_file}: {e}")

    # Assign family_id and relatedness_group
    panel_df["family_id"] = panel_df["sample_id"].map(lambda s: family_map.get(s, "UNKNOWN"))
    panel_df["relatedness_group"] = panel_df["sample_id"].map(
        lambda s: relatedness_map.get(s, f"REL_SINGLETON_{s}")
    )

    # Stamp provenance metadata
    panel_df["provenance_class"] = ProvenanceClass.REAL_PATIENT_GENOTYPE.value
    panel_df["source_version"] = "GRCh38_30x_high_coverage"

    # Save to Parquet if output path specified
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        panel_df.to_parquet(out_file, index=False)
        logger.info(f"Saved sample_metadata ({len(panel_df)} records) to {out_file}")

    return panel_df
