# Phase 5 Split Audit Report: Leakage & Group Partitioning

## 1. Leakage Guard Assertions Summary
- **Zero Relatedness Group Overlap**: PASSED (Verified across train/val/calib/test splits)
- **Zero Sample ID Overlap**: PASSED
- **Split File Hash Integrity**: PASSED (`splits.sha256` verified)
- **Forbidden Feature Columns Check**: PASSED

## 2. Achieved Stratification Balance by Superpopulation

| Superpopulation | Train Count | Val Count | Calib Count | Test Count | Total |
|---|---|---|---|---|---|
| `AFR` | 397 | 66 | 99 | 99 | 661 |
| `AMR` | 208 | 35 | 52 | 52 | 347 |
| `EAS` | 302 | 50 | 76 | 76 | 504 |
| `EUR` | 302 | 50 | 75 | 76 | 503 |
| `SAS` | 293 | 49 | 73 | 74 | 489 |
