# PHARMAGUARD PHASE 1: DATA ACQUISITION & PROVENANCE REPORT

**Generated At:** 2026-10-08  
**System:** PharmaGuard Pharmacogenomic Decision-Support System  
**Pipeline Build:** GRCh38 1000 Genomes High-Coverage Baseline

---

## 1. Executive Summary
Phase 1 established scripted, reproducible acquisition of 1000 Genomes regional VCF data for target pharmacogenes (CYP2C19, CYP2C9, CYP2D6, DPYD, SLCO1B1), constructed a leak-free sample metadata parquet table with pedigree-derived relatedness groups, audited gold-standard label availability (GeT-RM), and enforced data isolation for pharmacovigilance context datasets.

---

## 2. Sample Metadata & Population Breakdown
- **Total Samples:** 2,504
- **Pedigree-Derived Relatedness Groups:** 2,504
- **Genome Build:** GRCh38 (hg38)
- **Provenance Class:** `REAL_PATIENT_GENOTYPE`
- **Metadata Parquet File:** `data/processed/sample_metadata.parquet`

### Superpopulation Breakdown
| Superpopulation Code | Description | Sample Count | Percentage |
| :--- | :--- | :---: | :---: |
| **AFR** | African | 661 | 26.40% |
| **EAS** | East Asian | 504 | 20.13% |
| **EUR** | European | 503 | 20.09% |
| **SAS** | South Asian | 489 | 19.53% |
| **AMR** | Admixed American | 347 | 13.86% |
| **Total** | | **2,504** | **100.0%** |

---

## 3. Targeted Regional VCF Acquisition
All 5 target gene regions were sliced for GRCh38 coordinates with +/- 5 kb flanking sequences. File digests and metadata are recorded in `data/manifests/raw_manifest.json` and verified with `verify_manifest()`.

| Gene | Chromosome | Region Coordinates (GRCh38 + 5kb flank) | Local File Path | Manifest Status |
| :--- | :--- | :--- | :--- | :---: |
| **CYP2C19** | chr10 | chr10:94,757,681-94,858,307 | `data/raw/1000g/CYP2C19_GRCh38.vcf.gz` | VERIFIED |
| **CYP2C9** | chr10 | chr10:94,933,658-94,995,091 | `data/raw/1000g/CYP2C9_GRCh38.vcf.gz` | VERIFIED |
| **CYP2D6** | chr22 | chr22:42,121,499-42,135,881 | `data/raw/1000g/CYP2D6_GRCh38.vcf.gz` | VERIFIED |
| **DPYD** | chr1 | chr1:97,073,510-97,926,794 | `data/raw/1000g/DPYD_GRCh38.vcf.gz` | VERIFIED |
| **SLCO1B1** | chr12 | chr12:21,126,048-21,244,788 | `data/raw/1000g/SLCO1B1_GRCh38.vcf.gz` | VERIFIED |

---

## 4. Gold-Label Feasibility Audit (GeT-RM Consensus)
Per PRD Technical Requirement 5, genes with under 30 overlapping gold consensus samples are flagged as `GOLD_INSUFFICIENT`.

| Target Gene | GeT-RM Gold Samples | 1000G Overlap Count | Status | Evidence Level Claim |
| :--- | :---: | :---: | :---: | :--- |
| **CYP2C19** | 3 | 2 | `GOLD_INSUFFICIENT` | Silver-Derived / Exploratory |
| **CYP2C9** | 1 | 1 | `GOLD_INSUFFICIENT` | Silver-Derived / Exploratory |
| **CYP2D6** | 2 | 2 | `GOLD_INSUFFICIENT` | Silver-Derived / Exploratory |
| **DPYD** | 1 | 1 | `GOLD_INSUFFICIENT` | Silver-Derived / Exploratory |
| **SLCO1B1** | 1 | 1 | `GOLD_INSUFFICIENT` | Silver-Derived / Exploratory |

### Headline Claims Statement
Because all 5 target genes currently have < 30 overlapping gold consensus samples in the local consensus audit, **headline validation claims for these genes are silver-only (`DERIVED_SILVER_LABEL`)**. Models trained in subsequent phases will explicitly disclose silver-derived label status in decision-support evidence disclaimers.

---

## 5. Pharmacovigilance Context Ingestion
- **Status:** `PV_CONTEXT_ABSENT` (Professor CSV not provided at `data/external/professor_drug_adr.csv`).
- **Pipeline Behavior:** The ingestion module `scripts/data/ingest_pv_context.py` logged `PV_CONTEXT_ABSENT` and allowed the data pipeline to proceed safely without failure.
- **Security Check Verification:** Tested via `tests/data/test_pv_ingest.py`. Datasets containing `sample_id` or genotype columns trigger a mandatory `ValueError` SECURITY REJECTION per Agent Rule 3.

---

## 6. Manifest Verification Output
Running `verify_manifest("data/manifests/raw_manifest.json")` returned **0 mismatches** (`[]`). All raw regional VCF files match their recorded SHA-256 digests and file sizes.
