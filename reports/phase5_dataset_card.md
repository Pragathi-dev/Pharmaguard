# Phase 5 Dataset Card: PharmaGuard Research Dataset

## 1. Executive Summary
- **Total Samples**: 2504
- **Total Relatedness Groups**: 2504
- **Total ML Dataset Rows**: 40
- **Target Genes**: CYP2C19, CYP2C9, CYP2D6, DPYD, SLCO1B1
- **CYP2D6 SV Scope**: `structural_variation_assessed = false` (SNV-only resolvable subset)

---

## 2. Split Composition & Stratification

| Split | Samples Count | Groups Count | Percentage |
|---|---|---|---|
| `train` | 1502 | 1502 | 60.0% |
| `val` | 250 | 250 | 10.0% |
| `calib` | 375 | 375 | 15.0% |
| `test` | 377 | 377 | 15.1% |

---

## 3. Label Breakdown per Gene and Phenotype Class

| Gene | Phenotype Class | Label Source | Count (Train) | Count (Val) | Count (Calib) | Count (Test) | Total |
|---|---|---|---|---|---|---|---|
| CYP2C19 | Intermediate Metabolizer | `silver` | 8 | 0 | 0 | 0 | 8 |
| CYP2C9 | Normal Metabolizer | `silver` | 8 | 0 | 0 | 0 | 8 |
| CYP2D6 | Normal Metabolizer | `silver` | 8 | 0 | 0 | 0 | 8 |
| DPYD | Normal Metabolizer | `silver` | 8 | 0 | 0 | 0 | 8 |
| SLCO1B1 | Normal Function | `silver` | 8 | 0 | 0 | 0 | 8 |

---

## 4. Degradation Grid Summary

| Degradation Type | Level | Seed | Total Views Generated |
|---|---|---|---|
| `array_like` | 1.0 | 201 | 5 |
| `low_coverage` | 0.2 | 301 | 5 |
| `none` | 0.0 | 42 | 5 |
| `random_dropout` | 0.05 | 101 | 5 |
| `random_dropout` | 0.1 | 102 | 5 |
| `random_dropout` | 0.25 | 103 | 5 |
| `random_dropout` | 0.5 | 104 | 5 |
| `unphased` | 1.0 | 401 | 5 |
