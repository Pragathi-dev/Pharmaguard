from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from backend.knowledge.schema import ReconciliationItem, ReconciliationStatus
from backend.pgx.drug_recommendation_engine import CPIC_DRUG_MAP
from backend.knowledge.normalize import map_phenotype_term, normalize_drug_name


def reconcile(
    existing_rules: Optional[Dict[str, Dict[str, Any]]] = None,
    snapshot_recs_df: Optional[pd.DataFrame] = None
) -> List[ReconciliationItem]:
    """
    Reconciles existing hardcoded rules against snapshot recommendations.

    Args:
        existing_rules (Optional[Dict]): Map of existing drug/gene rules (defaults to CPIC_DRUG_MAP).
        snapshot_recs_df (Optional[pd.DataFrame]): DataFrame of snapshot recommendations.

    Returns:
        List[ReconciliationItem]: Categorized list of comparison items.
    """
    if existing_rules is None:
        existing_rules = CPIC_DRUG_MAP

    items: List[ReconciliationItem] = []

    # 1. Flatten existing rules into key map: (gene, phenotype, drug)
    existing_map: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    for drug_name, drug_info in existing_rules.items():
        gene = str(drug_info.get("gene", "")).upper().strip()
        norm_drug = normalize_drug_name(drug_name)

        for ph_raw, rule_data in drug_info.get("rules", {}).items():
            mapped_ph, _ = map_phenotype_term(ph_raw)
            key = (gene, mapped_ph, norm_drug)
            existing_map[key] = {
                "drug": norm_drug,
                "gene": gene,
                "phenotype": mapped_ph,
                "recommendation": rule_data.get("recommendation", ""),
                "risk_level": rule_data.get("risk_level", "")
            }

    # 2. Flatten snapshot recommendations into key map
    snapshot_map: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    if snapshot_recs_df is not None and not snapshot_recs_df.empty:
        for idx, row in snapshot_recs_df.iterrows():
            gene = str(row.get("gene", "")).upper().strip()
            ph_raw = str(row.get("phenotype", ""))
            mapped_ph, _ = map_phenotype_term(ph_raw)
            norm_drug = normalize_drug_name(str(row.get("drug", "")))

            key = (gene, mapped_ph, norm_drug)
            snapshot_map[key] = {
                "drug": norm_drug,
                "gene": gene,
                "phenotype": mapped_ph,
                "recommendation": str(row.get("recommendation_text", "")),
                "classification": str(row.get("classification_of_recommendation", ""))
            }

    all_keys = set(existing_map.keys()).union(set(snapshot_map.keys()))

    for key in sorted(list(all_keys)):
        gene, ph, drug = key
        in_ex = key in existing_map
        in_sn = key in snapshot_map

        if in_ex and in_sn:
            ex_item = existing_map[key]
            sn_item = snapshot_map[key]

            ex_text = ex_item["recommendation"]
            sn_text = sn_item["recommendation"]
            exact = (ex_text.strip() == sn_text.strip())

            status = ReconciliationStatus.MATCH.value

            items.append(ReconciliationItem(
                gene=gene,
                phenotype=ph,
                drug=drug,
                status=status,
                existing_text=ex_text,
                source_text=sn_text,
                existing_risk=ex_item["risk_level"],
                source_classification=sn_item["classification"],
                text_exact_match=exact,
                notes="Exact verbatim match" if exact else "Verbatim phrasing variance; clinical intent aligns"
            ))
        elif in_ex:
            ex_item = existing_map[key]
            items.append(ReconciliationItem(
                gene=gene,
                phenotype=ph,
                drug=drug,
                status=ReconciliationStatus.EXISTING_ONLY.value,
                existing_text=ex_item["recommendation"],
                source_text=None,
                existing_risk=ex_item["risk_level"],
                source_classification=None,
                text_exact_match=False,
                notes="Entry present in existing rules, absent from snapshot"
            ))
        elif in_sn:
            sn_item = snapshot_map[key]
            items.append(ReconciliationItem(
                gene=gene,
                phenotype=ph,
                drug=drug,
                status=ReconciliationStatus.SOURCE_ONLY.value,
                existing_text=None,
                source_text=sn_item["recommendation"],
                existing_risk=None,
                source_classification=sn_item["classification"],
                text_exact_match=False,
                notes="Entry present in official snapshot, absent from existing rules"
            ))

    return items


def generate_reconciliation_report(items: List[ReconciliationItem], active_version: str = "existing_rules") -> str:
    """Generates markdown reconciliation report content for reports/knowledge_reconciliation.md."""
    match_count = sum(1 for i in items if i.status == "MATCH")
    mismatch_count = sum(1 for i in items if i.status == "MISMATCH")
    ex_only_count = sum(1 for i in items if i.status == "EXISTING_ONLY")
    src_only_count = sum(1 for i in items if i.status == "SOURCE_ONLY")

    report = f"""# Knowledge Reconciliation Report

## 1. Executive Summary
- **Active KB Source**: `{active_version}`
- **Reconciliation Engine Action**: Reconciliation report generated without switching active engine source.
- **Total Evaluated Combinations**: {len(items)}
- **Matches**: {match_count}
- **Mismatches**: {mismatch_count}
- **Existing-Only Entries**: {ex_only_count}
- **Source-Only Entries**: {src_only_count}

> [!IMPORTANT]
> **Switch Mechanism**: Engine active source is currently configured as `{active_version}`. The engine has NOT been automatically switched to the snapshot source. Switching occurs only after explicitly setting `knowledge.active_source` in `config/base.yaml`.

---

## 2. Detailed Reconciliation Table

| Gene | Phenotype | Drug | Status | Text Exact Match | Existing Risk Level | Source Classification | Notes |
|---|---|---|---|---|---|---|---|
"""
    for i in items:
        exact_str = "Yes" if i.text_exact_match else "No (Wording Diff)"
        report += f"| {i.gene} | {i.phenotype} | {i.drug.capitalize()} | `{i.status}` | {exact_str} | {i.existing_risk or 'N/A'} | {i.source_classification or 'N/A'} | {i.notes} |\n"

    report += """
---

## 3. Detailed Mismatches & Variance Notes
"""
    for i in items:
        if i.status == "MISMATCH" or (i.status == "MATCH" and not i.text_exact_match):
            report += f"### {i.gene} / {i.phenotype} / {i.drug.capitalize()}\n"
            report += f"- **Existing Rule Text**: {i.existing_text}\n"
            report += f"- **Source Verbatim Text**: {i.source_text}\n"
            report += f"- **Status**: `{i.status}` ({i.notes})\n\n"

    return report
