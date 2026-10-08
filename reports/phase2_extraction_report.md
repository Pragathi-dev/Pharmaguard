# PHARMAGUARD PHASE 2: VCF EXTRACTION REPORT

**Generated At:** 2026-10-08  
**Total Site Observation Rows:** 75  
**Total Samples Processed:** 1

---

## 1. Site Observation Status Distribution
Quantifies natural observation vs missingness across catalogued sites.

| Status | Definition | Row Count | Percentage |
| :--- | :--- | :---: | :---: |
| **NOT_IN_VCF** | Site status classification | 75 | 100.00% |

---

## 2. Per-Gene Call Rate Summary
| Gene | Mean Region Call Rate | QC Pass Rate |
| :--- | :---: | :---: |
| **CYP2C19** | 0.00% | 0.0% |
| **CYP2C9** | 0.00% | 0.0% |
| **CYP2D6** | 0.00% | 0.0% |
| **DPYD** | 0.00% | 0.0% |
| **SLCO1B1** | 0.00% | 0.0% |

---

## 3. Strict Missingness Preservation Verification
- **Property Check Assertion:** Zero rows found with `status == HOM_REF` and `reference_evidence == none`.
- All unobserved catalogued sites are explicitly preserved as `NOT_IN_VCF`.
