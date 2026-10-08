# PHARMAGUARD DATA PROVENANCE POLICY

## 1. Executive Summary & Purpose
In clinical decision-support research, model reliability, auditability, and validation integrity depend on strict tracking of data origin. The **PharmaGuard Data Provenance Policy** defines mandatory governance rules for data classification, tracking, splitting, and lineage stamping across all datasets, models, and research artifacts.

---

## 2. Mandatory Rules of Data Governance

### Rule 1: No Cross-Provenance Patient Joins (Agent Rule 3)
- **NEVER join datasets at the patient level across different `provenance_class` categories.**
- Real patient genotypes (`REAL_PATIENT_GENOTYPE`) must not be merged or concatenated with synthetic records (`SYNTHETIC_RECOMBINANT`) or silver labels (`DERIVED_SILVER_LABEL`) into a single un-flagged entity.
- Every individual record processed by any pipeline MUST maintain an explicit `provenance_class` field.

### Rule 2: Synthetic Data Restrictions (Agent Rule 4)
- Synthetic (`SYNTHETIC_RECOMBINANT`) or augmented (`AUGMENTED_REAL`) data is **ONLY allowed in the training split (`train`)**.
- Synthetic data is **STRICTLY PROHIBITED** from validation (`val`), calibration (`calib`), or test (`test`) splits.
- All evaluation metrics reported in research reports must be computed exclusively on real reference data (`REAL_PATIENT_GENOTYPE`, `REAL_REFERENCE_LABEL`).

### Rule 3: Leak-Free Pipeline Execution Order (Agent Rule 5)
All dataset preparation and feature engineering MUST follow this strict sequence:
1. **Split by `relatedness_group`** (or family/population block) to prevent data leakage between train/val/test splits.
2. **Fit encoders and scalers on the `train` split ONLY.** Never fit transformers on full or merged datasets.
3. **Apply quality degradation / noise simulation** (if testing robustness) to target splits after splitting.
4. **Apply data augmentation (to the `train` split ONLY).**

---

## 3. Allowed Provenance Classes (`ProvenanceClass`)

Every dataset, record, or model input must belong to exactly one of the following 8 allowed `ProvenanceClass` enum values:

| Enum Value | Category Description | Examples / Sources |
| :--- | :--- | :--- |
| `REAL_PATIENT_GENOTYPE` | Verified patient VCF genomic profile | 1000 Genomes Project, Geisinger MyCode, clinical VCFs |
| `REAL_REFERENCE_LABEL` | Gold-standard clinical ground truth label | CPIC validated phenotype, FDA biomarker table |
| `DERIVED_SILVER_LABEL` | Inferred or algorithmically derived label | Rule-engine generated metabolizer phenotype |
| `KNOWLEDGE_BASE` | Authoritative guideline tables | CPIC gene-drug mappings, PharmGKB guidelines |
| `POPULATION_AGGREGATE` | Allele frequencies in general populations | gnomAD, 1000G population allele frequency tables |
| `PHARMACOVIGILANCE_CONTEXT` | Spontaneous adverse event reports | FDA FAERS, WHO VigiBase summaries |
| `AUGMENTED_REAL` | Real patient data modified by perturbation | Jittered/mutated real patient profiles (train split only) |
| `SYNTHETIC_RECOMBINANT` | In-silico generated recombinant profiles | Generative synthetic genomic profiles (train split only) |

---

## 4. Standardized Provenance Stamp Schema

Every data artifact, intermediate dataframe, or generated JSON report must contain a `provenance` metadata dictionary structured as follows:

```json
{
  "provenance_class": "REAL_PATIENT_GENOTYPE",
  "source": "1000_Genomes_Phase3_Chr12",
  "source_version": "v5b.20130502",
  "retrieved_at": "2026-10-08T18:30:00Z",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "schema_version": "1.0"
}
```

### Schema Field Requirements:
- `provenance_class` (str): Must match one of the 8 allowed `ProvenanceClass` strings.
- `source` (str): Human-readable dataset or repository identifier.
- `source_version` (str): Exact release tag, git commit hash, or publication version.
- `retrieved_at` (str): ISO 8601 UTC timestamp of acquisition (`YYYY-MM-DDTHH:MM:SSZ`).
- `sha256` (str): 64-character lowercase hex digest of the raw source file.
- `schema_version` (str): Provenance schema specification version (default `"1.0"`).

---

## 5. Verification & Audit Enforcement
- Programmatic checks in `backend/common/provenance.py` validate every `provenance_class` value against the `ProvenanceClass` enum, raising `ValueError` for unknown or missing classes.
- Research scripts will fail immediately if un-stamped data is passed to training or evaluation functions.
