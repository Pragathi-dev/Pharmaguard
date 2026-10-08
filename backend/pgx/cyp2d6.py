from typing import Dict, List, Optional, Tuple, Any
from backend.pgx.knowledge_files import AlleleDefinition, PhenotypeDefinition
from backend.pgx.phenotype import map_diplotypes_to_phenotype


def evaluate_cyp2d6(
    candidate_diplotypes: List[str],
    phenotype_def: PhenotypeDefinition,
    allele_def: AlleleDefinition,
    missing_defining_sites: List[str],
    mode: str = "strict"
) -> Tuple[str, Optional[float], bool, str]:
    """
    Evaluates CYP2D6 SNV-only diplotypes and phenotypes.
    Always sets structural_variation_assessed = False.
    Flags STRUCTURAL_UNRESOLVED when structural variations cannot be ruled out.

    Args:
        candidate_diplotypes (List[str]): Diplotype candidates.
        phenotype_def (PhenotypeDefinition): Loaded CYP2D6 phenotype rules.
        allele_def (AlleleDefinition): Loaded CYP2D6 allele definitions.
        missing_defining_sites (List[str]): Missing defining site IDs.
        mode (str): Engine mode ('strict' or 'reference_default').

    Returns:
        Tuple[str, Optional[float], bool, str]: (phenotype, activity_score, structural_variation_assessed=False, confidence_flag)
    """
    phenotype, activity_score = map_diplotypes_to_phenotype(
        candidate_diplotypes, phenotype_def, allele_def
    )

    structural_variation_assessed = False

    # Determine confidence flag
    if missing_defining_sites and mode == "strict":
        confidence_flag = "STRUCTURAL_UNRESOLVED"
    elif any("*5" in d or "xN" in d for d in candidate_diplotypes):
        confidence_flag = "STRUCTURAL_UNRESOLVED"
    elif phenotype == "Indeterminate":
        confidence_flag = "STRUCTURAL_UNRESOLVED"
    else:
        # SNV calling was complete, but SV (CNVs/duplications/deletions) was not assessed.
        confidence_flag = "COMPLETE"

    return phenotype, activity_score, structural_variation_assessed, confidence_flag
