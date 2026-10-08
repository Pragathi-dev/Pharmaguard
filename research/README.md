# PharmaGuard Research & ML Subsystem

This directory contains research scripts, dataset auditing tools, baseline models, and validation benchmarks for the PharmaGuard pharmacogenomic decision-support platform.

## Structure
- `data/`: Managed genomic data hierarchy (`raw`, `interim`, `processed`, `external`, `knowledge`).
- `experiments/`: Experiment configuration logs, metrics, and artifact tracking.
- `models/`: Trained model binaries and calibration curves.
- `reports/`: Audit, baseline test logs, and scientific validation reports.

## Principles
1. **Provenance Enforcement**: All datasets MUST use standard `ProvenanceClass` metadata stamps (`docs/DATA_PROVENANCE_POLICY.md`).
2. **Deterministic Reproducibility**: Fixed seeds (`set_global_seed`) and logged SHA-256 file digests for every run.
3. **Clinical Priority**: Machine learning models complement CPIC rule-based engine and never override deterministic guidelines.
