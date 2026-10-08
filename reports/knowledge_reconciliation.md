# Knowledge Reconciliation Report

## 1. Executive Summary
- **Active KB Source**: `existing_rules`
- **Reconciliation Engine Action**: Reconciliation report generated without switching active engine source.
- **Total Evaluated Combinations**: 30
- **Matches**: 18
- **Mismatches**: 0
- **Existing-Only Entries**: 0
- **Source-Only Entries**: 12

> [!IMPORTANT]
> **Switch Mechanism**: Engine active source is currently configured as `existing_rules`. The engine has NOT been automatically switched to the snapshot source. Switching occurs only after explicitly setting `knowledge.active_source` in `config/base.yaml`.

---

## 2. Detailed Reconciliation Table

| Gene | Phenotype | Drug | Status | Text Exact Match | Existing Risk Level | Source Classification | Notes |
|---|---|---|---|---|---|---|---|
| CYP2C19 | Indeterminate | Clopidogrel | `SOURCE_ONLY` | No (Wording Diff) | N/A | No Recommendation | Entry present in official snapshot, absent from existing rules |
| CYP2C19 | Intermediate Metabolizer | Clopidogrel | `MATCH` | Yes | Moderate | Strong | Exact verbatim match |
| CYP2C19 | Normal Metabolizer | Clopidogrel | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| CYP2C19 | Poor Metabolizer | Clopidogrel | `MATCH` | Yes | High | Strong | Exact verbatim match |
| CYP2C19 | Rapid Metabolizer | Clopidogrel | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| CYP2C19 | Ultrarapid Metabolizer | Clopidogrel | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| CYP2C9 | Intermediate Metabolizer | Warfarin | `MATCH` | Yes | Moderate | Moderate | Exact verbatim match |
| CYP2C9 | Normal Metabolizer | Warfarin | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| CYP2C9 | Poor Metabolizer | Warfarin | `MATCH` | Yes | High | Strong | Exact verbatim match |
| CYP2D6 | Indeterminate | Codeine | `SOURCE_ONLY` | No (Wording Diff) | N/A | No Recommendation | Entry present in official snapshot, absent from existing rules |
| CYP2D6 | Indeterminate | Warfarin | `SOURCE_ONLY` | No (Wording Diff) | N/A | No Recommendation | Entry present in official snapshot, absent from existing rules |
| CYP2D6 | Intermediate Metabolizer | Codeine | `MATCH` | Yes | Moderate | Moderate | Exact verbatim match |
| CYP2D6 | Intermediate Metabolizer | Warfarin | `SOURCE_ONLY` | No (Wording Diff) | N/A | Optional | Entry present in official snapshot, absent from existing rules |
| CYP2D6 | Normal Metabolizer | Codeine | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| CYP2D6 | Normal Metabolizer | Warfarin | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| CYP2D6 | Poor Metabolizer | Codeine | `MATCH` | Yes | High | Strong | Exact verbatim match |
| CYP2D6 | Poor Metabolizer | Warfarin | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| CYP2D6 | Ultrarapid Metabolizer | Codeine | `MATCH` | Yes | High | Strong | Exact verbatim match |
| CYP2D6 | Ultrarapid Metabolizer | Warfarin | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| DPYD | Intermediate Metabolizer | Clopidogrel | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| DPYD | Intermediate Metabolizer | Fluorouracil | `MATCH` | Yes | Moderate | Strong | Exact verbatim match |
| DPYD | Normal Metabolizer | Clopidogrel | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| DPYD | Normal Metabolizer | Fluorouracil | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| DPYD | Poor Metabolizer | Clopidogrel | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| DPYD | Poor Metabolizer | Fluorouracil | `MATCH` | Yes | High | Strong | Exact verbatim match |
| SLCO1B1 | Decreased Function | Simvastatin | `MATCH` | Yes | Moderate | Strong | Exact verbatim match |
| SLCO1B1 | Increased Function | Simvastatin | `SOURCE_ONLY` | No (Wording Diff) | N/A | Strong | Entry present in official snapshot, absent from existing rules |
| SLCO1B1 | Indeterminate | Simvastatin | `SOURCE_ONLY` | No (Wording Diff) | N/A | No Recommendation | Entry present in official snapshot, absent from existing rules |
| SLCO1B1 | Normal Function | Simvastatin | `MATCH` | Yes | Low | Strong | Exact verbatim match |
| SLCO1B1 | Poor Function | Simvastatin | `MATCH` | Yes | High | Strong | Exact verbatim match |

---

## 3. Detailed Mismatches & Variance Notes
