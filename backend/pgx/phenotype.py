from typing import Dict, List, Optional, Tuple, Any
from backend.pgx.knowledge_files import PhenotypeDefinition, AlleleDefinition, PhenotypeRule


def get_phenotype_for_diplotype(
    diplotype: str,
    phenotype_def: PhenotypeDefinition,
    allele_def: Optional[AlleleDefinition] = None
) -> Tuple[str, Optional[float]]:
    """
    Translates a single diplotype string (e.g. '*1/*2') into (phenotype, activity_score)
    using the loaded PhenotypeDefinition.

    Args:
        diplotype (str): Diplotype string formatted as 'allele1/allele2'.
        phenotype_def (PhenotypeDefinition): Phenotype rules loaded from YAML.
        allele_def (Optional[AlleleDefinition]): Allele definitions for activity score lookup.

    Returns:
        Tuple[str, Optional[float]]: (phenotype_string, activity_score)
    """
    parts = diplotype.split("/")
    if len(parts) != 2:
        return ("Indeterminate", None)

    a1, a2 = parts[0], parts[1]
    rev_diplotype = f"{a2}/{a1}"

    if phenotype_def.mapping_type == "diplotype_function":
        for rule in phenotype_def.rules:
            if rule.condition in [diplotype, rev_diplotype]:
                return (rule.phenotype, rule.activity_score)
        # Fallback if specific diplotype condition isn't listed: try activity score calculation
        if allele_def:
            as1 = allele_def.alleles[a1].activity_score if a1 in allele_def.alleles else None
            as2 = allele_def.alleles[a2].activity_score if a2 in allele_def.alleles else None
            if as1 is not None and as2 is not None:
                tot_as = as1 + as2
                return (_map_activity_score_to_phenotype(tot_as, phenotype_def), tot_as)

    elif phenotype_def.mapping_type == "activity_score":
        if allele_def:
            as1 = allele_def.alleles[a1].activity_score if (a1 in allele_def.alleles and allele_def.alleles[a1].activity_score is not None) else (1.0 if a1 == allele_def.reference_allele or a1.startswith("*1") else 1.0)
            as2 = allele_def.alleles[a2].activity_score if (a2 in allele_def.alleles and allele_def.alleles[a2].activity_score is not None) else (1.0 if a2 == allele_def.reference_allele or a2.startswith("*1") else 1.0)
            if as1 is not None and as2 is not None:
                tot_as = as1 + as2
                phenotype = _map_activity_score_to_phenotype(tot_as, phenotype_def)
                return (phenotype, tot_as)

    return ("Indeterminate", None)


def _map_activity_score_to_phenotype(activity_score: float, phenotype_def: PhenotypeDefinition) -> str:
    """Helper to match total activity score against min_as/max_as rules."""
    for rule in phenotype_def.rules:
        if rule.min_as is not None and rule.max_as is not None:
            if rule.min_as <= activity_score <= rule.max_as:
                return rule.phenotype
    return "Indeterminate"


def map_diplotypes_to_phenotype(
    candidate_diplotypes: List[str],
    phenotype_def: PhenotypeDefinition,
    allele_def: AlleleDefinition
) -> Tuple[str, Optional[float]]:
    """
    Maps candidate diplotype strings to a unified phenotype and activity score.

    Returns:
        Tuple[str, Optional[float]]: (phenotype, activity_score)
    """
    if not candidate_diplotypes:
        return ("Indeterminate", None)

    phenotypes = []
    scores = []

    for dip in candidate_diplotypes:
        ph, as_val = get_phenotype_for_diplotype(dip, phenotype_def, allele_def)
        phenotypes.append(ph)
        scores.append(as_val)

    # Check consistency across candidate diplotypes
    unique_phenotypes = set(phenotypes)
    
    if len(unique_phenotypes) == 1:
        chosen_phenotype = phenotypes[0]
        chosen_score = scores[0]
    else:
        chosen_phenotype = "Indeterminate"
        chosen_score = None

    return (chosen_phenotype, chosen_score)
