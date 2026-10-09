# Phase 5 Rare Classes & Coarse Grouping Report

## 1. Overview
- **Rare Class Threshold**: < 20 labelled samples per split.
- **Handling Strategy**: Report explicitly without dropping rows silently. Coarse groupings defined where CPIC specifies broader activity score clusters.

---

## 2. Class Counts & Rare Class Flags

| Gene | Fine Phenotype Class | Split | Count | Rare Flag (<20) | Coarse Mapping |
|---|---|---|---|---|---|
| CYP2C19 | Intermediate Metabolizer | `train` | 8 | `YES` | `Reduced` |
| CYP2C19 | Intermediate Metabolizer | `val` | 0 | `YES` | `Reduced` |
| CYP2C19 | Intermediate Metabolizer | `calib` | 0 | `YES` | `Reduced` |
| CYP2C19 | Intermediate Metabolizer | `test` | 0 | `YES` | `Reduced` |
| CYP2C9 | Normal Metabolizer | `train` | 8 | `YES` | `Normal` |
| CYP2C9 | Normal Metabolizer | `val` | 0 | `YES` | `Normal` |
| CYP2C9 | Normal Metabolizer | `calib` | 0 | `YES` | `Normal` |
| CYP2C9 | Normal Metabolizer | `test` | 0 | `YES` | `Normal` |
| CYP2D6 | Normal Metabolizer | `train` | 8 | `YES` | `Normal` |
| CYP2D6 | Normal Metabolizer | `val` | 0 | `YES` | `Normal` |
| CYP2D6 | Normal Metabolizer | `calib` | 0 | `YES` | `Normal` |
| CYP2D6 | Normal Metabolizer | `test` | 0 | `YES` | `Normal` |
| DPYD | Normal Metabolizer | `train` | 8 | `YES` | `Normal` |
| DPYD | Normal Metabolizer | `val` | 0 | `YES` | `Normal` |
| DPYD | Normal Metabolizer | `calib` | 0 | `YES` | `Normal` |
| DPYD | Normal Metabolizer | `test` | 0 | `YES` | `Normal` |
| SLCO1B1 | Normal Function | `train` | 8 | `YES` | `Normal` |
| SLCO1B1 | Normal Function | `val` | 0 | `YES` | `Normal` |
| SLCO1B1 | Normal Function | `calib` | 0 | `YES` | `Normal` |
| SLCO1B1 | Normal Function | `test` | 0 | `YES` | `Normal` |
