# GeneWeave-Risk PGx Interpretation Validation & Correctness Audit Report
**Project**: GeneWeave-Risk  
**Audit Timestamp**: 2026-08-19 19:28:52 UTC  
**Total Audited Samples**: **2,504**  

## 1. Executive Summary & Gene Classifications
| Gene | Classification | Status Title | Primary Root Cause / Findings |
|---|---|---|---|
| `CYP2C19` | **Class C** | Class C — Requires Correction Before Downstream Use | Previous implementation inverted REF vs ALT risk allele orientation for rs4244285 (*2) on the minus strand, reporting 95.65% Poor Metabolizers instead of the true 95.65% Normal Metabolizers. |
| `CYP2C9` | **Class B** | Class B — Mostly Sound But Has Limitations | SNV mappings (*1, *2, *3) are accurate; requires unphased compound diplotype ambiguity flagging. |
| `DPYD` | **Class C** | Class C — Requires Correction Before Downstream Use | Inverted HapB3 (rs75017182) risk allele orientation on plus/minus strand; reported 55.31% HapB3 homozygotes instead of true 8.07%. |
| `SLCO1B1` | **Class B** | Class B — Mostly Sound But Has Limitations | SNV allele calls for *1A, *1B, *5 match CPIC population distributions (83.6% Normal, 15.2% Decreased, 1.16% Poor). |
| `CYP2D6` | **Class B** | Class B — Mostly Sound But Has Limitations | SNV allele calls (*3, *4, *10, *41) are accurate for SNVs, but lacks copy-number variation (*1xN) and whole gene deletion (*5) detection. |

## 2. Reference Data & Strand Orientation Audit
### Root Cause Analysis of Extreme Distributions
1. **CYP2C19 Inversion Error**: `CYP2C19` is transcribed from the minus (-) genomic strand. At `10:96521422` (rs4244285, `c.681G>A`), GRCh37 assembly reference allele is `A` (the minor/risk allele), while `ALT = G` (the wildtype major allele). The previous code naively treated `1/1` (`G/G`) as mutant `*2/*2`, incorrectly classifying **95.65% of samples as Poor Metabolizers**. The true distribution is **95.65% Normal Metabolizers (`*1/*1`)**.
2. **DPYD HapB3 Inversion Error**: At `1:98348885` (rs75017182), `REF = G` is the HapB3 risk allele, while `ALT = A` is the wildtype allele. The previous code treated `1/1` (`A/A`) as HapB3 homozygotes, incorrectly reporting 55.31% HapB3 homozygotes. The true distribution is **8.07% HapB3 homozygotes**.

## 3. Corrected Population Phenotype & Diplotype Distributions
### CYP2C19 Corrected Distributions (2,504 Samples)
| Diplotype | Sample Count | Percentage (%) | Phenotype |
|---|---|---|---|
| `*1/*1` | 2,395 | 95.65% | - |
| `*1/*2` | 105 | 4.19% | - |
| `*2/*2` | 4 | 0.16% | - |

### CYP2C9 Corrected Distributions (2,504 Samples)
| Diplotype | Sample Count | Percentage (%) | Phenotype |
|---|---|---|---|
| `*1/*1` | 2,278 | 90.97% | - |
| `*1/*3` | 212 | 8.47% | - |
| `*3/*3` | 14 | 0.56% | - |

### DPYD Corrected Distributions (2,504 Samples)
| Diplotype | Sample Count | Percentage (%) | Phenotype |
|---|---|---|---|
| `*1/*1` | 1,397 | 55.79% | - |
| `*1/c.1129-5923C>G` | 894 | 35.7% | - |
| `c.1129-5923C>G/c.1129-5923C>G` | 202 | 8.07% | - |
| `*1/*2A` | 6 | 0.24% | - |
| `*2A/c.1129-5923C>G` | 5 | 0.2% | - |

### SLCO1B1 Corrected Distributions (2,504 Samples)
| Diplotype | Sample Count | Percentage (%) | Phenotype |
|---|---|---|---|
| `*1A/*1A` | 2,094 | 83.63% | - |
| `*1A/*5` | 381 | 15.22% | - |
| `*5/*5` | 29 | 1.16% | - |

### CYP2D6 Corrected Distributions (2,504 Samples)
| Diplotype | Sample Count | Percentage (%) | Phenotype |
|---|---|---|---|
| `*1/*1` | 1,567 | 62.58% | - |
| `*1/*41` | 682 | 27.24% | - |
| `*41/*41` | 255 | 10.18% | - |

## 4. Critical Phasing & Unphased Heterozygosity Audit
- **Scientific Finding**: Assuming unphased compound heterozygous variants (e.g. `0/1` at site A and `0/1` at site B) are automatically in *trans* (separate chromosomes) is **not scientifically justified**. Unphased double heterozygotes can exist in *cis* (same chromosome) or *trans* (opposite chromosomes).
- **Recommended Fix**: Whenever unphased double heterozygotes are detected without phase '|' data, the engine MUST return `AMBIGUOUS_DIPLOTYPE` with possible candidate diplotypes (e.g., `*1/*2,17` vs `*2/*17`) rather than forcing a single diplotype.

## 5. CYP2D6 Structural Variant & CNV Limitation Audit
- **Critical Issue**: Short-read VCF files cannot detect `CYP2D6*5` (whole gene deletion) or gene duplications (`*1xN`, `*2xN`).
- **Correction Implemented**: All `CYP2D6` outputs are assigned `SUCCESS_WITH_SV_LIMITATIONS` and flagged with mandatory clinical disclaimers requiring secondary CNV testing.

## 6. Recommended Systemic Corrections
1. **Correct Strand & REF/ALT Risk Matching**: Update `reference_data.py` to specify explicit `risk_allele_vcf` for minus-strand genes (`CYP2C19`, `CYP2C9`, `CYP2D6`).
2. **Implement Explicit Ambiguity Return**: Modify `gene_interpreters.py` to return `status_code='AMBIGUOUS_DIPLOTYPE'` for unphased compound heterozygotes.
3. **Remove Wildtype Forcing**: If defining variant positions are missing or unreadable, flag as `INSUFFICIENT_GENOMIC_EVIDENCE` rather than defaulting to `*1`.