from typing import Dict, List, Optional, Set, Any
from backend.pgx.knowledge_files import AlleleDefinition, StarAlleleSpec


def match_haplotype_alleles(
    site_calls_by_id: Dict[str, Dict[str, Any]],
    allele_def: AlleleDefinition,
    mode: str = "strict"
) -> List[str]:
    """
    Matches candidate star-alleles for a set of site observations on a single haplotype or sample.

    Args:
        site_calls_by_id (Dict): Map of site_id -> row dict (status, GT, etc.).
        allele_def (AlleleDefinition): Loaded star-allele definitions.
        mode (str): Execution mode ('strict' or 'reference_default').

    Returns:
        List[str]: Candidate matching star-allele names.
    """
    matched_alleles = []

    # Sort star-alleles by number of defining sites (descending) to match most specific allele first
    sorted_specs = sorted(
        allele_def.alleles.values(),
        key=lambda s: len(s.defining_sites),
        reverse=True
    )

    for spec in sorted_specs:
        if not spec.defining_sites:
            continue

        all_sites_alt = True
        for site_id in spec.defining_sites:
            site_info = site_calls_by_id.get(site_id, {})
            status = site_info.get("status", "NOT_IN_VCF")
            gt = site_info.get("gt", "./.")
            
            # Check if ALT allele is present
            if status in ["HET", "HOM_ALT"] or (gt and gt not in ["0/0", "0|0", "./.", "."]):
                pass
            else:
                all_sites_alt = False
                break

        if all_sites_alt:
            matched_alleles.append(spec.name)

    if not matched_alleles:
        matched_alleles.append(allele_def.reference_allele)

    return matched_alleles
