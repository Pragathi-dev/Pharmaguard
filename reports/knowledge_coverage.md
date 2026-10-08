# Knowledge Coverage Report

## 1. Scope & Snapshot Versions Used
- **Active KB Source Configuration**: `existing_rules`
- **Discovered Snapshots**: 3 snapshots
  - `cpic` (2026-10-09): 2 files, license: 'Creative Commons Attribution 4.0 International (CC BY 4.0) License'
  - `pharmvar` (2026-10-09): 2 files, license: 'Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) License'
  - `clinpgx` (2026-10-09): 2 files, license: 'Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) License'

---

## 2. Target Gene & Drug Coverage Matrix

| Gene | Target Drug | Total Recommendations | Mapped Phenotypes Covered | Unmapped Phenotypes | Status |
|---|---|---|---|---|---|
| CYP2C19 | Clopidogrel | 34 | Ultrarapid Metabolizer, Rapid Metabolizer, Normal Metabolizer, Intermediate Metabolizer, Poor Metabolizer, Indeterminate | 0 | `COVERED` |
| CYP2C19 | Warfarin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C19 | Fluorouracil | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C19 | Simvastatin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C19 | Codeine | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C9 | Clopidogrel | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C9 | Warfarin | 6 | Normal Metabolizer, Intermediate Metabolizer, Poor Metabolizer | 0 | `COVERED` |
| CYP2C9 | Fluorouracil | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C9 | Simvastatin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2C9 | Codeine | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2D6 | Clopidogrel | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2D6 | Warfarin | 22 | Intermediate Metabolizer, Normal Metabolizer, Poor Metabolizer, Ultrarapid Metabolizer, Indeterminate | 0 | `COVERED` |
| CYP2D6 | Fluorouracil | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2D6 | Simvastatin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| CYP2D6 | Codeine | 35 | Ultrarapid Metabolizer, Indeterminate, Intermediate Metabolizer, Normal Metabolizer, Poor Metabolizer | 0 | `COVERED` |
| DPYD | Clopidogrel | 5 | Normal Metabolizer, Intermediate Metabolizer, Poor Metabolizer | 0 | `COVERED` |
| DPYD | Warfarin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| DPYD | Fluorouracil | 11 | Normal Metabolizer, Intermediate Metabolizer, Poor Metabolizer | 0 | `COVERED` |
| DPYD | Simvastatin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| DPYD | Codeine | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| SLCO1B1 | Clopidogrel | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| SLCO1B1 | Warfarin | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| SLCO1B1 | Fluorouracil | 0 | None | 0 | `NO_SNAPSHOT_DATA` |
| SLCO1B1 | Simvastatin | 12 | Increased Function, Normal Function, Decreased Function, Poor Function, Indeterminate | 0 | `COVERED` |
| SLCO1B1 | Codeine | 0 | None | 0 | `NO_SNAPSHOT_DATA` |

---

## 3. Allele & Phenotype YAML Conversion Audit
- **CYP2C19**: 100% losslessly imported from PharmVar / CPIC.
- **CYP2C9**: 100% losslessly imported from PharmVar / CPIC.
- **CYP2D6**: 100% losslessly imported from PharmVar / CPIC (SNV scope).
- **DPYD**: 100% losslessly imported from PharmVar / CPIC (Catalogued scope).
- **SLCO1B1**: 100% losslessly imported from PharmVar / CPIC.
