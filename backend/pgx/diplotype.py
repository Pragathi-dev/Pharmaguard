from typing import Dict, List, Set, Tuple, Any
from backend.pgx.alleles import match_haplotype_alleles
from backend.pgx.knowledge_files import AlleleDefinition


def enumerate_diplotypes(
    site_calls_by_id: Dict[str, Dict[str, Any]],
    allele_def: AlleleDefinition,
    mode: str = "strict"
) -> Tuple[List[str], bool, List[str]]:
    """
    Enumerates candidate diplotypes for a sample given observed site calls.
    Handles unphased heterozygous variants and identifies missing defining sites.

    Returns:
        Tuple[List[str], bool, List[str]]: (candidate_diplotypes, phasing_ambiguous, missing_defining_sites)
    """
    # 1. Identify all defining sites for this gene
    all_defining_sites: Set[str] = set()
    for spec in allele_def.alleles.values():
        all_defining_sites.update(spec.defining_sites)

    # 2. Check site observation status
    missing_defining_sites = []
    het_sites = []
    hom_alt_sites = []

    for site_id in sorted(list(all_defining_sites)):
        site_info = site_calls_by_id.get(site_id, {})
        status = site_info.get("status", "NOT_IN_VCF")
        
        if status in ["NOT_IN_VCF", "NO_CALL", "FILTERED", "LOW_QUALITY", "MULTIALLELIC"]:
            if mode == "strict":
                missing_defining_sites.append(site_id)
        elif status == "HET":
            het_sites.append(site_id)
        elif status == "HOM_ALT":
            hom_alt_sites.append(site_id)

    # Determine matched alleles based on variant status
    matched_star_alleles = set()
    
    for spec in allele_def.alleles.values():
        if not spec.defining_sites:
            continue
        
        # If all defining sites for this star allele are present as HET or HOM_ALT
        has_var = True
        for s in spec.defining_sites:
            st = site_calls_by_id.get(s, {}).get("status", "NOT_IN_VCF")
            if st not in ["HET", "HOM_ALT"]:
                has_var = False
                break
        if has_var:
            matched_star_alleles.add(spec.name)

    candidate_list = []
    ref_allele = allele_def.reference_allele

    if not matched_star_alleles:
        candidate_list = [f"{ref_allele}/{ref_allele}"]
        phasing_ambiguous = False
    elif len(matched_star_alleles) == 1:
        allele = list(matched_star_alleles)[0]
        # Check if homozygous alt
        is_hom = True
        for s in allele_def.alleles[allele].defining_sites:
            if site_calls_by_id.get(s, {}).get("status") != "HOM_ALT":
                is_hom = False
                break
        if is_hom:
            candidate_list = [f"{allele}/{allele}"]
        else:
            candidate_list = [f"{ref_allele}/{allele}"]
        phasing_ambiguous = False
    else:
        # Multiple variant alleles present
        var_alleles = sorted(list(matched_star_alleles))
        candidate_list = []
        for a in var_alleles:
            candidate_list.append(f"{ref_allele}/{a}")
        
        if len(var_alleles) == 2:
            candidate_list.append(f"{var_alleles[0]}/{var_alleles[1]}")
            
        phasing_ambiguous = len(het_sites) >= 2

    # Standardize diplotype ordering (alphabetical sort per pair)
    norm_candidates = []
    for dip in candidate_list:
        parts = dip.split("/")
        if len(parts) == 2:
            s_parts = sorted(parts)
            norm_candidates.append(f"{s_parts[0]}/{s_parts[1]}")
        else:
            norm_candidates.append(dip)

    norm_candidates = sorted(list(set(norm_candidates)))
    return norm_candidates, phasing_ambiguous, missing_defining_sites
