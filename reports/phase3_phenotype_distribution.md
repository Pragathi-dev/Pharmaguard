# Phase 3: Phenotype Distribution Report

## 1. Summary Overview
This report documents the phenotype distribution and confidence flag metrics produced by the Phase 3 PGx Engine in both `STRICT` (preserves missingness, Baseline B1) and `REFERENCE_DEFAULT` (legacy assumption, Baseline B0) modes.

## 2. Metric Breakdown

### 2.1 Phenotype Distribution (STRICT vs REFERENCE_DEFAULT)
| Gene | Engine Mode | Phenotype | Count | Percentage |
|---|---|---|---|---|
| CYP2C19 | STRICT | Intermediate Metabolizer | 1 | 100.0% |
| CYP2C9 | STRICT | Indeterminate | 1 | 100.0% |
| CYP2D6 | STRICT | Indeterminate | 1 | 100.0% |
| DPYD | STRICT | Indeterminate | 1 | 100.0% |
| SLCO1B1 | STRICT | Indeterminate | 1 | 100.0% |
| CYP2C19 | REFERENCE_DEFAULT | Intermediate Metabolizer | 1 | 100.0% |
| CYP2C9 | REFERENCE_DEFAULT | Normal Metabolizer | 1 | 100.0% |
| CYP2D6 | REFERENCE_DEFAULT | Normal Metabolizer | 1 | 100.0% |
| DPYD | REFERENCE_DEFAULT | Normal Metabolizer | 1 | 100.0% |
| SLCO1B1 | REFERENCE_DEFAULT | Normal Function | 1 | 100.0% |

### 2.2 Confidence Flags Breakdown (STRICT Mode)
| Gene | Confidence Flag | Description | Count |
|---|---|---|---|
| CYP2C19 | PARTIAL | Partial defining site observation; diplotype constrained | 1 |
| CYP2C9 | PARTIAL | Partial defining site observation; diplotype unassigned | 1 |
| CYP2D6 | STRUCTURAL_UNRESOLVED | Structural variation (CNV/hybrid) not assessed by short reads | 1 |
| DPYD | PARTIAL | Partial defining site observation; uncatalogued variants unassessed | 1 |
| SLCO1B1 | PARTIAL | Partial defining site observation; diplotype unassigned | 1 |

## 3. Conclusions & Key Findings
1. **Preservation of Missingness:** In `STRICT` mode, unobserved defining sites are explicitly flagged and result in `PARTIAL` confidence flags or `Indeterminate` phenotypes rather than assuming wild-type reference alleles.
2. **CYP2D6 Safety Flag:** `CYP2D6` interpretations set `structural_variation_assessed = False` and assign `STRUCTURAL_UNRESOLVED`, preventing false normal calls.
3. **DPYD Scope:** `DPYD` interpretations explicitly log `only_catalogued_variants_assessed = True`.
