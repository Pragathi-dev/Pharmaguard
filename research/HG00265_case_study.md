# PharmaGuard Precision Medicine Case Study: Sample HG00265
**Patient ID**: `HG00265`  
**Population**: GBR (British in England and Wales)  
**Superpopulation**: EUR (European)  
**Genomic Data Source**: 1000 Genomes Project Phase 3  
**Overall PMGRF Risk Category**: **MODERATE RISK (Composite Score: 3)**  

---
## Executive Summary & Clinical Vignette
Patient `HG00265` is a adult of European ancestry undergoing clinical pharmacogenomic evaluation prior to potential therapeutic initiation. Multi-gene panel sequencing was processed through the PharmaGuard engine to evaluate 5 core pharmacogenes (`CYP2C19`, `CYP2C9`, `DPYD`, `SLCO1B1`, `CYP2D6`) across 5 target therapeutics (`Clopidogrel`, `Warfarin`, `Fluorouracil / 5-FU`, `Simvastatin`, `Codeine`).

The analysis identified **two distinct actionable loss-of-function variants** in `CYP2C9` (`*3`) and `DPYD` (`c.1129-5923C>G`), yielding a **Composite PMGRF Risk Score of 3 (Moderate Risk)**. Immediate prescribing modifications are required for **Warfarin** and **Fluorouracil** to prevent severe adverse drug reactions.

---
## 1. Raw Genomic Variants Detected
Targeted VCF extraction identified key single nucleotide polymorphisms (SNPs) across the 5 primary pharmacogenomic locus regions:

| Gene | Genomic Coordinate (GRCh37) | dbSNP ID (rsID) | Ref / Alt Allele | Genotype Call | Functional Allele Assignment |
|---|---|---|---|---|---|
| **CYP2C9** | chr10:96,702,047 | `rs1057910` | A / C | `1/0` (Het) | `CYP2C9*3` (Decreased Function) |
| **DPYD** | chr1:98,206,489 | `rs75017182` | C / T | `0/1` (Het) | `DPYD c.1129-5923C>G` / `HapB3` (Decreased Function) |
| **CYP2C19** | chr10:96,522,463 | `rs4244285` | G / A | `0/0` (WT) | `CYP2C19*1` (Wildtype Normal) |
| **SLCO1B1** | chr12:21,288,346 | `rs4149056` | T / C | `0/0` (WT) | `SLCO1B1*1A` (Wildtype Normal) |
| **CYP2D6** | chr22:42,524,947 | `rs3892097` | C / T | `0/0` (WT) | `CYP2D6*1` (Wildtype Normal) |

---
## 2. Diplotype Assignment
PharmVar-compliant diplotype resolution algorithms mapped the detected variant profiles to canonical star-allele diplotypes:

| Gene | Assigned Diplotype | Allele 1 | Allele 2 | Resolution Status | Resolution Confidence |
|---|---|---|---|---|---|
| `CYP2C9` | **`*1/*3`** | `*1` (Normal) | `*3` (Decreased) | `CONFIDENTLY_RESOLVED` | 100% |
| `DPYD` | **`*1/c.1129-5923C>G`** | `*1` (Normal) | `c.1129-5923C>G` (Decreased) | `CONFIDENTLY_RESOLVED` | 100% |
| `CYP2C19` | **`*1/*1`** | `*1` (Normal) | `*1` (Normal) | `CONFIDENTLY_RESOLVED` | 100% |
| `SLCO1B1` | **`*1A/*1A`** | `*1A` (Normal) | `*1A` (Normal) | `CONFIDENTLY_RESOLVED` | 100% |
| `CYP2D6` | **`*1/*41`** | `*1` (Normal) | `*41` (Normal/Sub-normal) | `CONFIDENTLY_RESOLVED` | 100% |

---
## 3. CPIC Phenotype Assignment
CPIC Activity Score (AS) calculation rules translated diplotypes into standardized clinical metabolic phenotypes:

| Gene | Diplotype | Activity Score (AS) | CPIC Clinical Phenotype | Functional Status |
|---|---|---|---|---|
| **CYP2C9** | `*1/*3` | **1.0** | **Intermediate Metabolizer** | Reduced Clearance (S-warfarin) |
| **DPYD** | `*1/c.1129-5923C>G` | **1.5** | **Intermediate Metabolizer** | Reduced DPD Catabolism (5-FU) |
| **CYP2C19** | `*1/*1` | **2.0** | **Normal Metabolizer** | Standard Bioactivation |
| **SLCO1B1** | `*1A/*1A` | **2.0** | **Normal Function** | Standard Hepatic Transport |
| **CYP2D6** | `*1/*41` | **2.0** | **Normal Metabolizer** | Standard Conversion to Morphine |

---
## 4. PMGRF Composite Risk Score Calculation
The PharmaGuard Multi-Gene Risk Framework (PMGRF) aggregates individual gene severity weights ($W_g$) into a single composite score:

$$S_{\text{total}} = \sum_{g \in \mathcal{G}} W_g(P_g) = W_{\text{CYP2C9}}(\text{IM}) + W_{\text{DPYD}}(\text{IM}) + W_{\text{CYP2C19}}(\text{NM}) + W_{\text{SLCO1B1}}(\text{NF}) + W_{\text{CYP2D6}}(\text{NM})$$

$$S_{\text{total}} = 1 + 2 + 0 + 0 + 0 = \mathbf{3}$$

| Gene | Assigned Phenotype | PMGRF Severity Weight ($W_g$) | Contribution Status |
|---|---|---|---|
| `CYP2C9` | Intermediate Metabolizer | **+1** | **Active Contributor** |
| `DPYD` | Intermediate Metabolizer | **+2** | **Active Contributor** |
| `CYP2C19` | Normal Metabolizer | **0** | Baseline |
| `SLCO1B1` | Normal Function | **0** | Baseline |
| `CYP2D6` | Normal Metabolizer | **0** | Baseline |
| **Total PMGRF Score** | — | **3** | **MODERATE RISK TIER** (Range: 3–5) |

---
## 5. Drug-Specific Pharmacogenomic Recommendations
Applying CPIC dosing guidelines across all 5 target drugs yields specific prescribing actions for patient `HG00265`:

| Drug Name | Gene | Phenotype | Risk Level | Actionable Prescribing Recommendation |
|---|---|---|---|---|
| **Warfarin** | `CYP2C9` | Intermediate Metabolizer | <span style='color:orange;font-weight:bold;'>MODERATE</span> | **Reduce initial Warfarin starting dose by 25% to 50%** or utilize CPIC pharmacogenomic dosing algorithms; monitor INR frequently. |
| **Fluorouracil** | `DPYD` | Intermediate Metabolizer | <span style='color:orange;font-weight:bold;'>MODERATE</span> | **Reduce Fluorouracil or Capecitabine starting dose by 25% to 50%** based on activity score. Monitor closely for toxicities. |
| **Clopidogrel** | `CYP2C19` | Normal Metabolizer | <span style='color:green;font-weight:bold;'>LOW</span> | Initiate Clopidogrel at standard label-recommended dosage (75 mg once daily). |
| **Simvastatin** | `SLCO1B1` | Normal Function | <span style='color:green;font-weight:bold;'>LOW</span> | Initiate desired starting dose of Simvastatin according to product label. |
| **Codeine** | `CYP2D6` | Normal Metabolizer | <span style='color:green;font-weight:bold;'>LOW</span> | Initiate Codeine at standard label-recommended age- and weight-adjusted starting dose. |

---
## 6. Clinical Explanation & Rationale Narrative
Human-readable clinical rationale generated by the PharmaGuard Explainability Layer for healthcare provider review:

> **Warfarin Narrative Rationale**:  
> *Patient carries CYP2C9 \*1/\*3 resulting in an Intermediate Metabolizer phenotype. Reduced S-warfarin clearance increases drug accumulation and risk of over-anticoagulation. Initial dose reduction of 25-50% and frequent INR monitoring are recommended according to CPIC guidance.*

> **Fluorouracil / 5-FU Narrative Rationale**:  
> *Patient carries DPYD \*1/c.1129-5923C>G resulting in an Intermediate Metabolizer phenotype. Decreased DPD clearance leads to increased systemic drug exposure and risk of severe adverse toxicity. Starting dose reduction of 25-50% and close toxicity monitoring are recommended according to CPIC guidance.*

---
## 7. Interactive Dashboard UI Component Mapping
The structured data for `HG00265` maps directly to the UI elements in the PharmaGuard React Dashboard (`pharmaguard-frontend/src/App.jsx`):

```text
+-----------------------------------------------------------------------------------------+
| PHARMAGUARD CLINICAL DECISION SUPPORT PORTAL                   Patient/Sample: [HG00265] |
+-----------------------------------------------------------------------------------------+
| PMGRF MULTI-GENE RISK FRAMEWORK ASSESSMENT                                              |
| Total PMGRF Score: [ 3 ]   |   Risk Tier: [ MODERATE RISK ]   |   Contributing Genes: [ 2 ] |
+-----------------------------------------------------------------------------------------+
| PATIENT GENOTYPE PROFILE                | CPIC GUIDELINE LOOKUP                         |
| - CYP2C9  : Intermediate Metabolizer    | Selected Drug: [ Warfarin (CYP2C9)        v ] |
| - DPYD    : Intermediate Metabolizer    | Action: Reduce starting dose by 25% - 50%     |
| - CYP2C19 : Normal Metabolizer          | Evidence: VERIFIED CPIC Level A               |
| - SLCO1B1 : Normal Function             |                                               |
| - CYP2D6  : Normal Metabolizer          |                                               |
+-----------------------------------------------------------------------------------------+
| DRUG-SPECIFIC PHARMACOGENOMIC RECOMMENDATIONS (5 Target Therapeutics Evaluated)         |
|                                                                                         |
| 1. WARFARIN (CYP2C9) | Phenotype: Intermediate | Risk: [ MODERATE RISK (ORANGE BADGE) ]  |
|    Prescribing Action: Reduce initial Warfarin starting dose by 25% to 50%.            |
|    Explanation: Patient carries CYP2C9 *1/*3 resulting in Intermediate Metabolizer...   |
|                                                                                         |
| 2. FLUOROURACIL (DPYD) | Phenotype: Intermediate | Risk: [ MODERATE RISK (ORANGE BADGE) ]|
|    Prescribing Action: Reduce Fluorouracil or Capecitabine starting dose by 25% to 50% |
|    Explanation: Patient carries DPYD *1/c.1129-5923C>G resulting in Intermediate...     |
|                                                                                         |
| 3. CLOPIDOGREL (CYP2C19) | Phenotype: Normal | Risk: [ LOW RISK (GREEN BADGE) ]         |
|    Prescribing Action: Initiate Clopidogrel at standard dosage (75 mg daily).           |
|                                                                                         |
| 4. SIMVASTATIN (SLCO1B1) | Phenotype: Normal | Risk: [ LOW RISK (GREEN BADGE) ]         |
|    Prescribing Action: Initiate desired starting dose according to product label.       |
|                                                                                         |
| 5. CODEINE (CYP2D6) | Phenotype: Normal | Risk: [ LOW RISK (GREEN BADGE) ]             |
|    Prescribing Action: Initiate Codeine at standard starting dose.                      |
+-----------------------------------------------------------------------------------------+
```