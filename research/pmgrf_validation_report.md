# PharmaGuard Multi-Gene Risk Framework (PMGRF) Validation Report
**Dataset**: 1000 Genomes Phase 3 (2,504 Cohort Samples)  
**Genome Assembly**: GRCh37 / hg19  
**Target Audience**: Pharmacogenomics & Computational Biology Conference Proceedings  

## Executive Summary
This validation report evaluates the population distribution, phenotype frequency spectrum, and composite risk contributions of the **PharmaGuard Multi-Gene Risk Framework (PMGRF)** across 2,504 diverse individuals from the 1000 Genomes Project.
- **Cohort Size**: `N = 2,504` multi-ethnic samples
- **Evaluated Pharmacogenes**: `CYP2C19`, `CYP2C9`, `DPYD`, `SLCO1B1`, `CYP2D6`
- **Composite Population Risk**: Low Risk (84.94%), Moderate Risk (15.02%), High Risk (0.04%)

## Table 1: Pharmacogene Phenotype Frequency & PMGRF Composite Score Impact
Frequency breakdown of CPIC standardized phenotypes across all 5 pharmacogenes and their corresponding mean population composite risk score.
| Gene | Phenotype Classification | PMGRF Severity Weight | Sample Count (N) | Population Frequency (%) | Mean PMGRF Composite Score |
|---|---|---|---|---|---|
| `CYP2C19` | Normal Metabolizer | +0 | 2,399 | 95.81% | 1.28 |
| `CYP2C19` | Intermediate Metabolizer | +1 | 105 | 4.19% | 2.00 |
| `CYP2C9` | Normal Metabolizer | +0 | 2,278 | 90.97% | 1.21 |
| `CYP2C9` | Intermediate Metabolizer | +1 | 212 | 8.47% | 2.31 |
| `CYP2C9` | Poor Metabolizer | +2 | 14 | 0.56% | 3.43 |
| `DPYD` | Normal Metabolizer | +0 | 1,587 | 63.38% | 0.63 |
| `DPYD` | Intermediate Metabolizer | +2 | 909 | 36.3% | 2.50 |
| `DPYD` | Poor Metabolizer | +3 | 8 | 0.32% | 3.38 |
| `SLCO1B1` | Normal Function | +0 | 2,094 | 83.63% | 0.99 |
| `SLCO1B1` | Decreased Function | +2 | 381 | 15.22% | 2.90 |
| `SLCO1B1` | Poor Function | +3 | 29 | 1.16% | 3.69 |
| `CYP2D6` | Normal Metabolizer | +0 | 2,249 | 89.82% | 1.25 |
| `CYP2D6` | Intermediate Metabolizer | +1 | 255 | 10.18% | 1.90 |

## Table 2: Gene Risk Contribution Analysis for Elevated Risk Tiers
Identifies which pharmacogenes contribute most frequently to placing individuals into **Moderate (Scores 3–5)** and **High (Scores 6+)** risk categories.
| Gene | Moderate Risk Contributions (N=376) | Mod Risk Share (%) | High Risk Contributions (N=1) | High Risk Share (%) | Total Population Non-Normal Count (N=2,504) | Overall Population Frequency (%) |
|---|---|---|---|---|---|---|
| `DPYD` | 283 | 75.27% | 1 | 100.0% | 917 | 36.62% |
| `SLCO1B1` | 217 | 57.71% | 1 | 100.0% | 410 | 16.37% |
| `CYP2C9` | 122 | 32.45% | 0 | 0.0% | 226 | 9.03% |
| `CYP2D6` | 96 | 25.53% | 1 | 100.0% | 255 | 10.18% |
| `CYP2C19` | 48 | 12.77% | 0 | 0.0% | 105 | 4.19% |

## Table 3: Cross-Population Multi-Gene Risk Category Distribution
Distribution of PMGRF cumulative risk tiers across global continental superpopulations.
| Superpopulation | Code | Total Cohort (N) | Low Risk (Score 0-2) | Moderate Risk (Score 3-5) | High Risk (Score 6+) | Mean Risk Score |
|---|---|---|---|---|---|---|
| African | `AFR` | 661 | 596 (90.2%) | 65 (9.8%) | 0 (0.0%) | 1.24 |
| Admixed American | `AMR` | 347 | 278 (80.1%) | 69 (19.9%) | 0 (0.0%) | 1.48 |
| East Asian | `EAS` | 504 | 426 (84.5%) | 77 (15.3%) | 1 (0.2%) | 1.14 |
| European | `EUR` | 503 | 376 (74.8%) | 127 (25.2%) | 0 (0.0%) | 1.64 |
| South Asian | `SAS` | 489 | 451 (92.2%) | 38 (7.8%) | 0 (0.0%) | 1.14 |

## Key Research Insights & Discussion
1. **Primary Drivers of Moderate Risk**: `SLCO1B1` (Decreased Function, score +2) and `DPYD` (Intermediate Metabolizer `c.1129-5923C>G`, score +2) are the primary drivers elevating patients into the Moderate Risk category.
2. **Population Disparities**: European (`EUR`) and Admixed American (`AMR`) populations exhibit the highest frequencies of Moderate Risk (25.2% and 19.9% respectively), largely driven by higher allele frequencies of `SLCO1B1*5` and `DPYD HapB3`.
3. **High Risk Rarity**: High Risk (composite score >= 6) is rare (0.04% of population), representing compound severe functional loss across 3+ distinct pharmacogene pathways simultaneously.