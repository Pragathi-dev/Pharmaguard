"""
Generate PMGRF Population-Wide Results and Summary Statistics.
Reads research/pgx_interpretation_results.csv, aggregates multi-gene risk scores per sample,
generates research/pmgrf_population_results.csv and research/pmgrf_summary_report.md.
Uses standard library csv module for maximum compatibility.
"""

import os
import sys
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.pgx.multigene_risk import MultiGeneRiskEvaluator

INPUT_CSV = PROJECT_ROOT / "research" / "pgx_interpretation_results.csv"
OUTPUT_CSV = PROJECT_ROOT / "research" / "pmgrf_population_results.csv"
OUTPUT_MD = PROJECT_ROOT / "research" / "pmgrf_summary_report.md"


def main():
    print("=== Generating PMGRF Population-Wide Risk Results ===", flush=True)

    if not INPUT_CSV.exists():
        print(f"Error: Input CSV not found at {INPUT_CSV}")
        sys.exit(1)

    # Group records by sample_id preserve order
    sample_order: List[str] = []
    sample_records: Dict[str, Dict[str, Any]] = defaultdict(dict)
    sample_superpop: Dict[str, str] = {}
    sample_pop: Dict[str, str] = {}

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total_rows = 0
        for row in reader:
            total_rows += 1
            sample_id = row["sample_id"]
            if sample_id not in sample_records:
                sample_order.append(sample_id)
                sample_superpop[sample_id] = row.get("superpopulation", "UNKNOWN")
                sample_pop[sample_id] = row.get("population", "UNKNOWN")

            gene = row["gene"]
            act_score_str = row.get("activity_score", "")
            try:
                act_score = float(act_score_str) if act_score_str != "" else None
            except ValueError:
                act_score = None

            sample_records[sample_id][gene] = {
                "gene": gene,
                "phenotype": row.get("phenotype", "Normal Metabolizer"),
                "diplotype": row.get("diplotype", "*1/*1"),
                "activity_score": act_score,
                "status_code": row.get("status_code", "CONFIDENTLY_RESOLVED")
            }

    print(f"Loaded {total_rows:,} records for {len(sample_order):,} unique samples from {INPUT_CSV.name}", flush=True)

    output_rows: List[Dict[str, Any]] = []
    cat_counts = {"Low": 0, "Moderate": 0, "High": 0}
    scores: List[int] = []
    superpop_stats = defaultdict(lambda: {"total": 0, "Low": 0, "Moderate": 0, "High": 0})

    for s_id in sample_order:
        gene_interps = sample_records[s_id]
        risk_res = MultiGeneRiskEvaluator.evaluate_sample_risk(gene_interps, s_id)

        sp = sample_superpop.get(s_id, "UNKNOWN")
        pop = sample_pop.get(s_id, "UNKNOWN")

        row_dict = {
            "sample_id": s_id,
            "superpopulation": sp,
            "population": pop,
            "CYP2C19 phenotype": gene_interps.get("CYP2C19", {}).get("phenotype", "Normal Metabolizer"),
            "CYP2C9 phenotype": gene_interps.get("CYP2C9", {}).get("phenotype", "Normal Metabolizer"),
            "DPYD phenotype": gene_interps.get("DPYD", {}).get("phenotype", "Normal Metabolizer"),
            "CYP2D6 phenotype": gene_interps.get("CYP2D6", {}).get("phenotype", "Normal Metabolizer"),
            "SLCO1B1 phenotype": gene_interps.get("SLCO1B1", {}).get("phenotype", "Normal Function"),
            "total_score": risk_res.total_score,
            "risk_category": risk_res.risk_category
        }
        output_rows.append(row_dict)

        cat_counts[risk_res.risk_category] = cat_counts.get(risk_res.risk_category, 0) + 1
        scores.append(risk_res.total_score)
        superpop_stats[sp]["total"] += 1
        superpop_stats[sp][risk_res.risk_category] += 1

    # Write CSV output to research/pmgrf_population_results.csv
    fieldnames = [
        "sample_id",
        "superpopulation",
        "population",
        "CYP2C19 phenotype",
        "CYP2C9 phenotype",
        "DPYD phenotype",
        "CYP2D6 phenotype",
        "SLCO1B1 phenotype",
        "total_score",
        "risk_category"
    ]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Saved population results ({len(output_rows):,} rows) to {OUTPUT_CSV}", flush=True)

    # Calculate statistics
    total_samples = len(output_rows)
    low_cnt = cat_counts["Low"]
    mod_cnt = cat_counts["Moderate"]
    high_cnt = cat_counts["High"]

    low_pct = round((low_cnt / total_samples) * 100, 2)
    mod_pct = round((mod_cnt / total_samples) * 100, 2)
    high_pct = round((high_cnt / total_samples) * 100, 2)

    avg_score = sum(scores) / total_samples if total_samples > 0 else 0
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0

    # Write summary report to research/pmgrf_summary_report.md
    md_lines = [
        "# PharmaGuard Multi-Gene Risk Framework (PMGRF) Population Summary Report",
        "**Dataset**: 1000 Genomes Phase 3 (2,504 Samples)  ",
        "**Framework**: PharmaGuard Multi-Gene Risk Framework (PMGRF)  ",
        "**Source Data**: `research/pgx_interpretation_results.csv`  \n",
        "## 1. Population Risk Distribution Summary",
        "| Risk Category | Score Range | Sample Count | Frequency (%) |",
        "|---|---|---|---|",
        f"| **Low** | 0 - 2 | {low_cnt:,} | {low_pct}% |",
        f"| **Moderate** | 3 - 5 | {mod_cnt:,} | {mod_pct}% |",
        f"| **High** | 6+ | {high_cnt:,} | {high_pct}% |",
        f"| **Total Evaluated** | — | **{total_samples:,}** | **100.00%** |",
        "",
        "## 2. Superpopulation Breakdown",
        "| Superpopulation | Total Samples | Low Risk (%) | Moderate Risk (%) | High Risk (%) |",
        "|---|---|---|---|---|",
    ]

    for sp in sorted(superpop_stats.keys()):
        sp_data = superpop_stats[sp]
        n_sp = sp_data["total"]
        sp_low = sp_data["Low"]
        sp_mod = sp_data["Moderate"]
        sp_high = sp_data["High"]
        md_lines.append(
            f"| `{sp}` | {n_sp:,} | {sp_low} ({round(sp_low/n_sp*100,1)}%) | {sp_mod} ({round(sp_mod/n_sp*100,1)}%) | {sp_high} ({round(sp_high/n_sp*100,1)}%) |"
        )

    md_lines.extend([
        "",
        "## 3. Score Distribution Summary",
        f"- **Minimum Risk Score**: {min_score}",
        f"- **Maximum Risk Score**: {max_score}",
        f"- **Average Risk Score**: {avg_score:.2f}",
        "",
        "## 4. Methodology & Severity Scoring Rules",
        "The PMGRF calculates composite risk scores using individual gene phenotype severity points:",
        "- **CYP2C19**: Normal (0), Intermediate (1), Poor (2), Rapid (1), Ultrarapid (2)",
        "- **CYP2C9**: Normal (0), Intermediate (1), Poor (2)",
        "- **DPYD**: Normal (0), Intermediate (2), Poor (3)",
        "- **SLCO1B1**: Normal Function (0), Decreased Function (2), Poor Function (3)",
        "- **CYP2D6**: Normal (0), Intermediate (1), Poor (2), Ultrarapid (2)",
    ])

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Saved summary report to {OUTPUT_MD}", flush=True)

    print("\n--- SUMMARY STATISTICS ---")
    print(f"Total Samples Evaluated : {total_samples:,}")
    print(f"Low Risk (0-2)          : {low_cnt:,} ({low_pct}%)")
    print(f"Moderate Risk (3-5)     : {mod_cnt:,} ({mod_pct}%)")
    print(f"High Risk (6+)          : {high_cnt:,} ({high_pct}%)")
    print("=== PMGRF Execution Complete ===")


if __name__ == "__main__":
    main()
