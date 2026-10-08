# PharmaGuard Multi-Gene Risk Framework (PMGRF) Population Summary Report
**Dataset**: 1000 Genomes Phase 3 (2,504 Samples)  
**Framework**: PharmaGuard Multi-Gene Risk Framework (PMGRF)  
**Source Data**: `research/pgx_interpretation_results.csv`  

## 1. Population Risk Distribution Summary
| Risk Category | Score Range | Sample Count | Frequency (%) |
|---|---|---|---|
| **Low** | 0 - 2 | 2,127 | 84.94% |
| **Moderate** | 3 - 5 | 376 | 15.02% |
| **High** | 6+ | 1 | 0.04% |
| **Total Evaluated** | — | **2,504** | **100.00%** |

## 2. Superpopulation Breakdown
| Superpopulation | Total Samples | Low Risk (%) | Moderate Risk (%) | High Risk (%) |
|---|---|---|---|---|
| `AFR` | 661 | 596 (90.2%) | 65 (9.8%) | 0 (0.0%) |
| `AMR` | 347 | 278 (80.1%) | 69 (19.9%) | 0 (0.0%) |
| `EAS` | 504 | 426 (84.5%) | 77 (15.3%) | 1 (0.2%) |
| `EUR` | 503 | 376 (74.8%) | 127 (25.2%) | 0 (0.0%) |
| `SAS` | 489 | 451 (92.2%) | 38 (7.8%) | 0 (0.0%) |

## 3. Score Distribution Summary
- **Minimum Risk Score**: 0
- **Maximum Risk Score**: 6
- **Average Risk Score**: 1.31

## 4. Methodology & Severity Scoring Rules
The PMGRF calculates composite risk scores using individual gene phenotype severity points:
- **CYP2C19**: Normal (0), Intermediate (1), Poor (2), Rapid (1), Ultrarapid (2)
- **CYP2C9**: Normal (0), Intermediate (1), Poor (2)
- **DPYD**: Normal (0), Intermediate (2), Poor (3)
- **SLCO1B1**: Normal Function (0), Decreased Function (2), Poor Function (3)
- **CYP2D6**: Normal (0), Intermediate (1), Poor (2), Ultrarapid (2)