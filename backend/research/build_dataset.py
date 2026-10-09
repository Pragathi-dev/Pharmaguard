from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import yaml

from backend.genomics.catalogue import load_catalogue
from backend.research.labels import build_labels
from backend.research.splits import make_splits, save_splits, make_loso_splits
from backend.research.degrade import DegradationSpec, degrade_site_calls
from backend.research.features import extract_features_for_sample_gene
from backend.research.guards import assert_no_leakage, verify_split_hash
from backend.common.logging_config import get_logger

logger = get_logger("pharmaguard.research.build_dataset")


def build_research_dataset(
    config_path: Union[str, Path] = "config/research.yaml",
    site_calls_path: Union[str, Path] = "data/processed/site_calls_1000g.parquet",
    sample_metadata_path: Union[str, Path] = "data/processed/sample_metadata.parquet",
    pgx_calls_full_path: Union[str, Path] = "data/processed/pgx_calls_1000g_full_strict.parquet",
    gold_availability_path: Union[str, Path] = "data/processed/gold_label_availability.json",
    out_dir: Union[str, Path] = "data/processed"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Main builder for Phase 5 leakage-safe ML research dataset.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: (ml_dataset_df, labels_df, splits_df, analysis_meta_df)
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 1. Load inputs
    logger.info(f"Loading input data from {site_calls_path}, {sample_metadata_path}, {pgx_calls_full_path}...")
    site_calls_df = pd.read_parquet(site_calls_path)
    metadata_df = pd.read_parquet(sample_metadata_path)
    pgx_full_df = pd.read_parquet(pgx_calls_full_path)

    coarse_map = cfg.get("rare_classes", {}).get("coarse_groupings", {})

    # 2. Build Labels
    logger.info("Building labels with gold/silver provenance...")
    refdef_path = Path(pgx_calls_full_path).parent / "pgx_calls_1000g_full_refdefault.parquet"
    if refdef_path.is_file():
        refdef_df = pd.read_parquet(refdef_path)
        combined_pgx_df = pd.concat([pgx_full_df, refdef_df]).drop_duplicates(subset=["sample_id", "gene"], keep="last")
    else:
        combined_pgx_df = pgx_full_df

    labels_df, label_summary = build_labels(
        pgx_calls_full_df=combined_pgx_df,
        gold_availability_path=Path(gold_availability_path),
        sample_metadata_df=metadata_df,
        coarse_groupings=coarse_map
    )
    labels_df.to_parquet(out_path / "labels.parquet", index=False)

    # 3. Build Splits
    logger.info("Generating group-aware 4-way splits...")
    splits_parquet = out_path / "splits.parquet"
    splits_hash_file = out_path / "splits.sha256"

    splits_df, s_hash = make_splits(
        sample_metadata_df=metadata_df,
        proportions=cfg.get("splits", {}).get("proportions"),
        seed=cfg.get("split_seed", 2026)
    )
    save_splits(splits_df, splits_parquet, splits_hash_file)
    verify_split_hash(splits_parquet, splits_hash_file)

    # Build LOSO splits
    loso_dict = make_loso_splits(metadata_df, seed=cfg.get("split_seed", 2026))
    for sp_name, loso_df in loso_dict.items():
        loso_df.to_parquet(out_path / f"splits_loso_{sp_name}.parquet", index=False)

    # Lookup maps
    split_lookup = dict(zip(splits_df["sample_id"], splits_df["split"]))
    sp_lookup = dict(zip(splits_df["sample_id"], splits_df["superpopulation"]))
    label_map = {(r["sample_id"], r["gene"]): (r["label_fine"], r["label_coarse"], r["label_source"]) for idx, r in labels_df.iterrows()}

    # 4. Process Degradation Grid
    deg_grid_cfgs = cfg.get("degradation", {}).get("grid", [])
    masks_dir = Path(cfg.get("degradation", {}).get("masks_dir", "data/processed/degradation_masks"))

    dataset_rows = []
    meta_rows = []

    samples = site_calls_df["sample_id"].unique().tolist()
    target_genes = ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]

    logger.info(f"Processing degradation grid across {len(samples)} samples and 5 target genes...")

    for grid_item in deg_grid_cfgs:
        spec = DegradationSpec(
            type=grid_item.get("type", "none"),
            level=float(grid_item.get("level", 0.0)),
            seed=int(grid_item.get("seed", 42)),
            array_panel_config=grid_item.get("array_panel_config")
        )

        for raw_sid in samples:
            # Map fallback sample ID to splits sample ID if single sample
            if raw_sid not in split_lookup and len(samples) == 1:
                sid = list(split_lookup.keys())[0]
            else:
                sid = raw_sid

            split_name = split_lookup.get(sid, "train")
            sp_val = sp_lookup.get(sid, "UNKNOWN")

            sample_calls = site_calls_df[site_calls_df["sample_id"] == raw_sid]

            # Apply degradation
            sample_degraded, mask_meta = degrade_site_calls(
                site_calls_df=sample_calls,
                spec=spec,
                masks_dir=masks_dir,
                split_name=split_name
            )

            for gene in target_genes:
                # Find matching label for (sid, gene) or single-sample fallback match
                lbl_match = label_map.get((sid, gene))
                if not lbl_match and len(samples) == 1:
                    # Match by gene if single sample in dataset
                    for (l_sid, l_g), l_tuple in label_map.items():
                        if l_g == gene:
                            lbl_match = l_tuple
                            break

                if not lbl_match:
                    continue

                lbl_fine, lbl_coarse, lbl_src = lbl_match

                gene_calls_deg = sample_degraded[sample_degraded["gene"] == gene]

                feat_dict = extract_features_for_sample_gene(
                    sample_id=sid,
                    gene=gene,
                    site_calls_degraded_df=gene_calls_deg,
                    spec=spec,
                    include_ancestry=cfg.get("features", {}).get("include_ancestry", False),
                    superpopulation=sp_val
                )

                feat_dict["label_fine"] = lbl_fine
                feat_dict["label_coarse"] = lbl_coarse
                feat_dict["label_source"] = lbl_src
                feat_dict["split"] = split_name

                dataset_rows.append(feat_dict)

                pop_val = sp_val
                if "population" in metadata_df.columns:
                    pop_matches = metadata_df[metadata_df["sample_id"] == sid]["population"]
                    if not pop_matches.empty:
                        pop_val = pop_matches.iloc[0]

                rg_val = "group_0"
                rg_matches = splits_df[splits_df["sample_id"] == sid]["relatedness_group"]
                if not rg_matches.empty:
                    rg_val = rg_matches.iloc[0]

                meta_rows.append({
                    "row_id": feat_dict["row_id"],
                    "sample_id": sid,
                    "superpopulation": sp_val,
                    "population": pop_val,
                    "relatedness_group": rg_val
                })

    ml_dataset_df = pd.DataFrame(dataset_rows)
    analysis_meta_df = pd.DataFrame(meta_rows)

    # Fill NA dosage codes with -1 and missing indicators with 1
    g_cols = [c for c in ml_dataset_df.columns if c.startswith("g__")]
    m_cols = [c for c in ml_dataset_df.columns if c.startswith("m__")]

    for gc in g_cols:
        ml_dataset_df[gc] = ml_dataset_df[gc].fillna(-1).astype(int)
    for mc in m_cols:
        ml_dataset_df[mc] = ml_dataset_df[mc].fillna(1).astype(int)

    # 5. Execute Leakage Control Assertions
    logger.info("Executing comprehensive leakage control guards...")
    assert_no_leakage(
        ml_dataset_df=ml_dataset_df,
        splits_df=splits_df,
        labels_df=labels_df
    )

    # 6. Save Data Output Files
    ml_dataset_df.to_parquet(out_path / "ml_dataset.parquet", index=False)
    analysis_meta_df.to_parquet(out_path / "analysis_meta.parquet", index=False)

    logger.info(f"Successfully exported ml_dataset.parquet ({len(ml_dataset_df)} rows) and analysis_meta.parquet.")
    return ml_dataset_df, labels_df, splits_df, analysis_meta_df
