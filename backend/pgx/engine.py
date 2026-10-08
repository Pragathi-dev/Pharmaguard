from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd

from backend.pgx.schemas import GeneResult, EngineMode, ConfidenceFlag
from backend.pgx.knowledge_files import KnowledgeBase, load_knowledge
from backend.pgx.diplotype import enumerate_diplotypes
from backend.pgx.phenotype import map_diplotypes_to_phenotype
from backend.pgx.dpyd import evaluate_dpyd
from backend.pgx.cyp2d6 import evaluate_cyp2d6


def interpret_gene(
    sample_id: str,
    gene: str,
    site_calls_df: pd.DataFrame,
    kb: KnowledgeBase,
    mode: Union[str, EngineMode] = EngineMode.STRICT
) -> GeneResult:
    """
    Interprets pharmacogenomic diplotype and phenotype for a single sample and gene.

    Args:
        sample_id (str): Target sample ID.
        gene (str): Gene symbol (e.g. 'CYP2C19').
        site_calls_df (pd.DataFrame): Site calls dataframe for this sample and gene.
        kb (KnowledgeBase): Loaded knowledge base instance.
        mode (str | EngineMode): 'strict' or 'reference_default'.

    Returns:
        GeneResult: Dataclass containing structured interpretation results.
    """
    mode_str = mode.value if isinstance(mode, EngineMode) else str(mode).lower()

    if gene not in kb.alleles or gene not in kb.phenotypes:
        raise ValueError(f"Gene '{gene}' not defined in KnowledgeBase")

    allele_def = kb.alleles[gene]
    phenotype_def = kb.phenotypes[gene]

    # Convert site calls dataframe into a site lookup map
    site_calls_by_id: Dict[str, Dict[str, Any]] = {}
    if not site_calls_df.empty:
        for idx, row in site_calls_df.iterrows():
            row_dict = row.to_dict()
            site_id = row_dict.get("site_id")
            if site_id:
                site_calls_by_id[str(site_id)] = row_dict

            # Also index by alternative site key patterns (gene:chrom:pos:ref>alt)
            chrom = str(row_dict.get("chrom", ""))
            pos = str(row_dict.get("pos", ""))
            ref = str(row_dict.get("ref", ""))
            alt = str(row_dict.get("alt", ""))
            alt_key = f"{gene}:{chrom}:{pos}:{ref}>{alt}"
            site_calls_by_id[alt_key] = row_dict

    # 1. Gather all defining sites for this gene
    all_defining_sites = set()
    for spec in allele_def.alleles.values():
        all_defining_sites.update(spec.defining_sites)

    n_defining_sites = len(all_defining_sites)

    # 2. Enumerate candidate diplotypes and missing sites
    candidate_diplotypes, phasing_ambiguous, missing_defining_sites = enumerate_diplotypes(
        site_calls_by_id=site_calls_by_id,
        allele_def=allele_def,
        mode=mode_str
    )

    n_observed_defining = n_defining_sites - len(missing_defining_sites)

    # Pick top primary diplotype
    if candidate_diplotypes:
        primary_diplotype = candidate_diplotypes[0]
        parts = primary_diplotype.split("/")
        allele1, allele2 = parts[0], parts[1] if len(parts) > 1 else parts[0]
    else:
        primary_diplotype = f"{allele_def.reference_allele}/{allele_def.reference_allele}"
        allele1 = allele_def.reference_allele
        allele2 = allele_def.reference_allele
        candidate_diplotypes = [primary_diplotype]

    structural_variation_assessed = True
    only_catalogued_variants_assessed = False

    # 3. Gene-specific evaluation
    if gene == "CYP2D6":
        phenotype, activity_score, sv_assessed, conf_flag_str = evaluate_cyp2d6(
            candidate_diplotypes=candidate_diplotypes,
            phenotype_def=phenotype_def,
            allele_def=allele_def,
            missing_defining_sites=missing_defining_sites,
            mode=mode_str
        )
        structural_variation_assessed = sv_assessed
        confidence_flag = conf_flag_str
    elif gene == "DPYD":
        phenotype, activity_score, catalogued_only = evaluate_dpyd(
            candidate_diplotypes=candidate_diplotypes,
            phenotype_def=phenotype_def,
            allele_def=allele_def
        )
        only_catalogued_variants_assessed = catalogued_only
        confidence_flag = _determine_confidence_flag(
            mode_str=mode_str,
            phenotype=phenotype,
            missing_sites=missing_defining_sites,
            phasing_ambiguous=phasing_ambiguous
        )
    else:
        phenotype, activity_score = map_diplotypes_to_phenotype(
            candidate_diplotypes=candidate_diplotypes,
            phenotype_def=phenotype_def,
            allele_def=allele_def
        )
        confidence_flag = _determine_confidence_flag(
            mode_str=mode_str,
            phenotype=phenotype,
            missing_sites=missing_defining_sites,
            phasing_ambiguous=phasing_ambiguous
        )

    # In strict mode, if diplotype is ambiguous due to missing sites, set phenotype to Indeterminate
    if mode_str == "strict" and missing_defining_sites:
        if primary_diplotype == f"{allele_def.reference_allele}/{allele_def.reference_allele}" and n_observed_defining < n_defining_sites:
            phenotype = "Indeterminate"
            primary_diplotype = None
            allele1, allele2 = None, None

    return GeneResult(
        sample_id=sample_id,
        gene=gene,
        mode=mode_str,
        diplotype=primary_diplotype,
        allele1=allele1,
        allele2=allele2,
        candidate_diplotypes=candidate_diplotypes,
        phenotype=phenotype,
        activity_score=activity_score,
        missing_defining_sites=missing_defining_sites,
        n_defining_sites=n_defining_sites,
        n_observed_defining=n_observed_defining,
        confidence_flag=confidence_flag,
        phasing_ambiguous=phasing_ambiguous,
        structural_variation_assessed=structural_variation_assessed,
        only_catalogued_variants_assessed=only_catalogued_variants_assessed,
        engine_version="3.0.0",
        kb_version=kb.kb_version
    )


def _determine_confidence_flag(
    mode_str: str,
    phenotype: str,
    missing_sites: List[str],
    phasing_ambiguous: bool
) -> str:
    """Helper to compute confidence flag based on mode and observations."""
    if mode_str == "strict" and missing_sites:
        if phenotype == "Indeterminate":
            return ConfidenceFlag.UNRESOLVED.value
        else:
            return ConfidenceFlag.PARTIAL.value

    if phenotype == "Indeterminate":
        return ConfidenceFlag.UNRESOLVED.value

    return ConfidenceFlag.COMPLETE.value


def run_engine(
    site_calls_df: pd.DataFrame,
    mode: Union[str, EngineMode] = EngineMode.STRICT,
    kb_dir: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Executes the PGx interpretation engine on a batch site calls DataFrame.

    Args:
        site_calls_df (pd.DataFrame): Long-format site calls table from Phase 2.
        mode (str | EngineMode): 'strict' or 'reference_default'.
        kb_dir (Optional[str | Path]): Path to data/knowledge directory.

    Returns:
        pd.DataFrame: Long-format pgx_calls DataFrame.
    """
    if kb_dir is None:
        kb_dir = Path("data/knowledge")

    kb = load_knowledge(kb_dir)
    target_genes = ["CYP2C19", "CYP2C9", "CYP2D6", "DPYD", "SLCO1B1"]

    results = []

    if site_calls_df.empty:
        samples = ["SAMPLE_001"]
    else:
        samples = site_calls_df["sample_id"].unique().tolist()

    for sid in samples:
        for gene in target_genes:
            gene_calls = site_calls_df[
                (site_calls_df["sample_id"] == sid) & (site_calls_df["gene"] == gene)
            ] if not site_calls_df.empty else pd.DataFrame()

            result_obj = interpret_gene(
                sample_id=sid,
                gene=gene,
                site_calls_df=gene_calls,
                kb=kb,
                mode=mode
            )
            results.append(result_obj.to_dict())

    return pd.DataFrame(results)
