from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd

from backend.knowledge.schema import LookupResult, LookupStatus
from backend.knowledge.versioning import active_kb_version, get_snapshot_dir_for_version
from backend.knowledge.normalize import map_phenotype_term, normalize_drug_name
from backend.knowledge.loader import load_normalized_recommendations
from backend.pgx.drug_recommendation_engine import CPIC_DRUG_MAP, DRUG_ALIASES


def list_supported_drugs(gene: Optional[str] = None) -> List[str]:
    """
    Lists supported generic drug names, optionally filtered by gene.
    """
    drugs = ["clopidogrel", "warfarin", "fluorouracil", "simvastatin", "codeine"]
    if gene is None:
        return sorted(list(set(drugs)))

    g_upper = gene.upper().strip()
    gene_map = {
        "CYP2C19": ["clopidogrel"],
        "CYP2C9": ["warfarin"],
        "DPYD": ["fluorouracil"],
        "SLCO1B1": ["simvastatin"],
        "CYP2D6": ["codeine"]
    }
    return gene_map.get(g_upper, [])


def get_recommendations(
    gene: str,
    phenotype: str,
    drug: str,
    kb_version: Optional[str] = None
) -> LookupResult:
    """
    Retrieves pharmacogenomic drug recommendation with verbatim source text and citation metadata.

    Args:
        gene (str): Gene symbol (e.g. 'CYP2C19').
        phenotype (str): Phenotype term (e.g. 'Poor Metabolizer').
        drug (str): Drug name (e.g. 'clopidogrel').
        kb_version (Optional[str]): Target KB version. Defaults to active_kb_version().

    Returns:
        LookupResult: Structured lookup result object.
    """
    if kb_version is None:
        kb_version = active_kb_version()

    g_upper = str(gene).upper().strip()
    mapped_ph, _ = map_phenotype_term(phenotype)
    norm_drug = normalize_drug_name(drug)

    # 1. Existing Rules Mode
    if kb_version == "existing_rules" or kb_version.startswith("existing"):
        # Match against CPIC_DRUG_MAP
        canonical_drug = DRUG_ALIASES.get(norm_drug, norm_drug.capitalize())

        if canonical_drug in CPIC_DRUG_MAP:
            drug_info = CPIC_DRUG_MAP[canonical_drug]
            assoc_gene = drug_info.get("gene", "").upper()

            if assoc_gene == g_upper:
                rules = drug_info.get("rules", {})
                rule = rules.get(mapped_ph) or rules.get(phenotype)

                if not rule:
                    # Case insensitive search in rules keys
                    ph_lower = mapped_ph.lower()
                    for k, v in rules.items():
                        if k.lower() == ph_lower:
                            rule = v
                            break

                if rule:
                    rec_text = rule.get("recommendation")
                    return LookupResult(
                        status=LookupStatus.FOUND.value,
                        gene=g_upper,
                        phenotype=mapped_ph,
                        drug=norm_drug,
                        recommendation_text=rec_text,
                        classification_of_recommendation=rule.get("risk_level"),
                        evidence_level="High",
                        guideline_url=drug_info.get("guideline", "https://cpicpgx.org"),
                        kb_version="existing_rules",
                        source="existing_rules"
                    )

        return LookupResult(
            status=LookupStatus.NOT_AVAILABLE.value,
            gene=g_upper,
            phenotype=mapped_ph,
            drug=norm_drug,
            kb_version="existing_rules",
            source="existing_rules"
        )

    # 2. Snapshot Table Mode
    df = load_normalized_recommendations()
    if df.empty:
        return LookupResult(
            status=LookupStatus.NOT_AVAILABLE.value,
            gene=g_upper,
            phenotype=mapped_ph,
            drug=norm_drug,
            kb_version=kb_version,
            source=kb_version.split(":")[0] if ":" in kb_version else "snapshot"
        )

    # Filter matching rows
    matched = df[
        (df["gene"].str.upper() == g_upper) &
        (df["drug"].str.lower() == norm_drug) &
        (df["phenotype"] == mapped_ph)
    ]

    if not matched.empty:
        row = matched.iloc[0]
        return LookupResult(
            status=LookupStatus.FOUND.value,
            gene=g_upper,
            phenotype=mapped_ph,
            drug=norm_drug,
            recommendation_text=str(row["recommendation_text"]),
            classification_of_recommendation=row.get("classification_of_recommendation"),
            evidence_level=row.get("evidence_level"),
            guideline_url=row.get("guideline_url"),
            kb_version=str(row.get("kb_version", kb_version)),
            source=str(row.get("source", "snapshot"))
        )

    return LookupResult(
        status=LookupStatus.NOT_AVAILABLE.value,
        gene=g_upper,
        phenotype=mapped_ph,
        drug=norm_drug,
        kb_version=kb_version,
        source=kb_version.split(":")[0] if ":" in kb_version else "snapshot"
    )
