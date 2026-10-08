from typing import Dict, List, Optional, Tuple, Any
from backend.pgx.knowledge_files import AlleleDefinition, PhenotypeDefinition
from backend.pgx.phenotype import map_diplotypes_to_phenotype


def evaluate_dpyd(
    candidate_diplotypes: List[str],
    phenotype_def: PhenotypeDefinition,
    allele_def: AlleleDefinition
) -> Tuple[str, Optional[float], bool]:
    """
    Evaluates DPYD diplotype and activity score, setting only_catalogued_variants_assessed to True.

    Args:
        candidate_diplotypes (List[str]): List of diplotypes (e.g. ['*1/*2A']).
        phenotype_def (PhenotypeDefinition): Loaded DPYD phenotype definitions.
        allele_def (AlleleDefinition): Loaded DPYD allele definitions.

    Returns:
        Tuple[str, Optional[float], bool]: (phenotype, activity_score, only_catalogued_variants_assessed=True)
    """
    phenotype, activity_score = map_diplotypes_to_phenotype(
        candidate_diplotypes, phenotype_def, allele_def
    )
    only_catalogued = True
    return phenotype, activity_score, only_catalogued
