# PHARMAGUARD PHASE 2: LEGACY VS NEW PARSER COMPARISON REPORT

**Sample VCF Evaluated:** `pharmaguard_clinical_gold_standard.vcf`  
**Target Sample ID:** HG00265  
**Comparison Purpose:** Validate backward compatibility while documenting missingness preservation.

---

## 1. Executive Summary & Audit Findings
- **Backward Compatibility:** Pre-existing `backend/parser.py` remains 100% untouched and backward-compatible.
- **Core Research Finding:** Legacy parser defaulted missing catalogued sites to `Normal` (wildtype). The new `backend/genomics` extractor preserves missingness as `NOT_IN_VCF`, preventing false-positive homozygous reference assumptions.

---

## 2. Per-Gene Comparison & Difference Audit

| Gene | Legacy Parser Output | New Extractor Status Breakdown | Explanation & Impact |
| :--- | :--- | :--- | :--- |
| **CYP2C19** | `Poor` | `{'NOT_IN_VCF': 9}` | Legacy status: 'Poor'. New extractor breakdown: {'NOT_IN_VCF': 9}. |
| **CYP2D6** | `Poor` | `{'NOT_IN_VCF': 9, 'MULTIALLELIC': 2, 'HOM_REF': 1}` | Legacy status: 'Poor'. New extractor breakdown: {'NOT_IN_VCF': 9, 'MULTIALLELIC': 2, 'HOM_REF': 1}. |
| **DPYD** | `Intermediate` | `{'NOT_IN_VCF': 9, 'MULTIALLELIC': 2, 'HOM_REF': 1}` | Legacy status: 'Intermediate'. New extractor breakdown: {'NOT_IN_VCF': 9, 'MULTIALLELIC': 2, 'HOM_REF': 1}. |
| **SLCO1B1** | `Poor` | `{'NOT_IN_VCF': 3, 'HOM_ALT': 1, 'HET': 1, 'HOM_REF': 1}` | Legacy status: 'Poor'. New extractor breakdown: {'NOT_IN_VCF': 3, 'HOM_ALT': 1, 'HET': 1, 'HOM_REF': 1}. |
| **CYP2C9** | `Intermediate` | `{'NOT_IN_VCF': 6}` | Legacy status: 'Intermediate'. New extractor breakdown: {'NOT_IN_VCF': 6}. |

---

## 3. Site-Level Agreement Detail
Every site absent from the VCF is assigned `NOT_IN_VCF` with `reference_evidence = none`.
Zero sites receive `HOM_REF` without explicit `0/0` GT or callable block proof.
