# PHARMAGUARD PHASE 0: ARCHITECTURE AUDIT REPORT

**Date:** October 8, 2026  
**System:** PharmaGuard Pharmacogenomic Decision-Support System  
**Audit Scope:** Full repository review across Backend, Frontend, VCF Pipeline, CPIC Rules, CatBoost Model, Persistence, Auth, Endpoints, Test Suite, and Dashboard UI.

---

## 1. Executive Summary & Purpose
This audit records the structural baseline of PharmaGuard prior to Phase 1 research development. The system currently functions as a hybrid rule-based and machine-learning decision-support framework. The primary finding of this audit is that while the **CPIC rule-based engine** (`backend/pgx/`) provides deterministic and scientifically sound star-allele calling and recommendation mappings, the **existing CatBoost model** (`geneweave_catboost.cbm`) is trained on heuristically generated synthetic data (`real_genomic_training_data.csv`) and must be marked **UNVERIFIED**.

---

## 2. Component Architecture Analysis

### 2.1 Backend Architecture
- **Tech Stack:** FastAPI 2.5, Uvicorn, Python 3.11+.
- **Structure:** Monolithic FastAPI application (`backend/main.py`) serving both REST endpoints and invoking internal domain packages (`backend.pgx`, `backend.database`, `backend.auth`).
- **Path Resolution:** Dynamically inserts project root to `sys.path`.
- **Status:** **KEEP**. Architecture is clean, decoupled, and straightforward.

### 2.2 Frontend Architecture
- **Tech Stack:** React (Vite 8.0), Vanilla CSS + Tailwind CSS, Lucide icons.
- **Structure:** Single Page Application (SPA) driven by `pharmaguard-frontend/src/App.jsx`.
- **Services:** `auth.js` (JWT token management in `localStorage`) and `interpretationEngine.js` (client-side risk aggregations and fallback interpretations).
- **Status:** **KEEP / MODIFY**. Keep core UI components; modify labels to strictly state "Decision-support evidence", "Exploratory", "Not clinically validated".

### 2.3 VCF Parsing Pipeline
- **Modules:** `backend/parser.py`, `backend/pgx/vcf_reader.py`.
- **Mechanism:** `parser.py` performs manual string scanning looking for key rsIDs (`rs1799853`, `rs1057910`, `rs12248560`, `rs3918290`, `rs4149056`, etc.) or `GENE=` INFO tags. `vcf_reader.py` parses multi-sample VCFs for target sample IDs.
- **Limitation:** Hardcoded rsID mapping covers only 25 variants. Lack of `cyvcf2` high-throughput streaming parser.
- **Status:** **MODIFY**. Retain current parsing logic as fallback; add `cyvcf2` streaming reader for standard VCF 4.2/4.3 specs.

### 2.4 CPIC Rule & Recommendation Engine
- **Modules:** `backend/pgx/drug_recommendation_engine.py`, `backend/pgx/gene_interpreters.py`, `backend/pgx/reference_data.py`, `backend/pgx/multigene_risk.py`.
- **Mechanism:** Deterministic lookup tables mapping star-alleles to activity scores and metabolizer phenotypes (e.g. CYP2C19 *2, *3, *17; CYP2D6 *4, *5; DPYD *2A; SLCO1B1 *5). Computes Polygenic Multigene Risk Framework (PMGRF) scores.
- **Authoritative Rule:** Per Agent Rule 1, CPIC guidelines are authoritative. ML supporting models never override CPIC rules.
- **Status:** **KEEP**. Highly structured, deterministic, and accurate.

### 2.5 Existing CatBoost ML Model & Data Generation
- **Files:** `backend/geneweave_catboost.cbm`, `backend/engine.py`, `backend/train_catboost.py`, `backend/generate_dataset.py`.
- **Audit Findings:**
  - `generate_dataset.py` generates 5,000 synthetic patient records using `random.choices()` and applies manual rule weights (`Normal: 10, Intermediate: 25, Poor: 40`, with a 1.35 multiplier for compound poor status).
  - Output is saved to `real_genomic_training_data.csv` despite containing zero real genomic data.
  - `train_catboost.py` fits a `CatBoostRegressor` on these categorical text columns.
  - `engine.py` calls `cb_model.predict()` and computes pseudo SHAP values and arbitrary conformal coverage bounds (`interval = [score - variance, score + variance]`).
- **Status:** **REPLACE (Mark UNVERIFIED)**. The existing model is an echo of simple hardcoded rules and does not represent real-world ML prediction.

### 2.6 Database & Persistence Layer
- **Modules:** `backend/database.py`.
- **Mechanism:** Asynchronous MongoDB connection using `motor.motor_asyncio`. Includes full URI validation, Atlas vs Localhost detection, and fallback to `IN_MEMORY_REPORTS` and `IN_MEMORY_DOCTORS` when MongoDB is unconfigured or unreachable.
- **Status:** **MODIFY**. Keep dual MongoDB/In-memory architecture; extend report document schema to include standardized provenance metadata.

### 2.7 Authentication & Security
- **Modules:** `backend/auth.py`.
- **Mechanism:** JWT authentication using `PyJWT` (HS256 algorithm, 24-hour expiration) and password hashing with `bcrypt`.
- **Status:** **KEEP**. Meets basic security requirements for research application.

### 2.8 REST API Endpoints
- **Endpoints:**
  - `GET /api/health`: Database connection status and diagnostic telemetry.
  - `POST /api/auth/register`: Doctor registration & token issue.
  - `POST /api/auth/login`: Doctor login & token issue.
  - `GET /api/auth/me`: Authenticated profile fetch.
  - `GET /api/reports`: Doctor patient report history.
  - `POST /api/analyze`: Combined VCF upload, parsing, ML scoring, PMGRF risk evaluation, and report persistence.
  - `POST /api/v1/clinical/recommendation`: Direct CPIC lookup for drug/gene pair.
- **Status:** **KEEP**. Fully functional and responsive.

### 2.9 Test Suite Audit
- **Files:** `tests/test_all_genes.py`, `tests/test_cyp2c19.py`, `tests/test_drug_recommendation_engine.py`, `tests/test_integrated_pmgrf_drug_recommendations.py`, `tests/test_multigene_risk.py`, `tests/test_regression.py`, `backend/test_pipeline.py`.
- **Pass Rate:** 27 out of 29 tests pass.
- **Failures in `backend/test_pipeline.py`:** `test_sample_isolation` and `test_insufficient_evidence_handling` fail when run from project root because they expect hardcoded relative file paths (`pharmaguard_synthetic (1).vcf` and `CYP2C19_1.002.vcf`) inside `backend/`. Per Phase 0 rules, these failures are recorded in `reports/baseline_tests_phase0.txt` and preserved.
- **Status:** **KEEP / ADD**. Keep existing suite; add `tests/common/` for core infrastructure testing.

### 2.10 UI Dashboard
- **Components:** `DoctorDashboard.jsx`, `AIRiskModule.jsx`, `PGxRiskModule.jsx`, `ClinicalSummaryCard.jsx`, `DrugRecommendationPanel.jsx`, `CPICGuidelineReference.jsx`, `PatientGenotypeProfile.jsx`.
- **Status:** **KEEP**. Modern, clean React layout with distinct card sections for PGx CPIC evidence vs exploratory AI risk metrics.

---

## 3. Component Mapping Table (KEEP / MODIFY / REPLACE / ADD)

| Component | Path | Action | Justification |
| :--- | :--- | :--- | :--- |
| **FastAPI App** | `backend/main.py` | **KEEP** | Core routing, startup health diagnostics, and upload handlers function correctly. |
| **Auth Module** | `backend/auth.py` | **KEEP** | Standard JWT signed token and bcrypt password hashing. |
| **Database Connector** | `backend/database.py` | **MODIFY** | Maintain Motor connection with in-memory fallback; update schema for provenance logging. |
| **VCF Parser** | `backend/parser.py` | **MODIFY** | Add `cyvcf2` VCF 4.2/4.3 reader support while preserving fallback rsID scanner. |
| **CatBoost Inference Engine** | `backend/engine.py` | **REPLACE** | Mark model UNVERIFIED. Replace hardcoded heuristics with research ML pipeline. |
| **CatBoost Training Script** | `backend/train_catboost.py` | **REPLACE** | Replace with reproducible script featuring fixed seeds, logging, and provenance. |
| **Synthetic Dataset Script** | `backend/generate_dataset.py` | **REPLACE** | Rule-weighted random generator violates provenance standards. |
| **CatBoost Model Binary** | `backend/geneweave_catboost.cbm` | **REPLACE** | Mark model UNVERIFIED. Re-train in Phase 2 on verified provenance data. |
| **CPIC Recommendation Engine** | `backend/pgx/` | **KEEP** | Deterministic, star-allele based recommendation logic stays authoritative. |
| **Frontend SPA** | `pharmaguard-frontend/src/` | **KEEP / MODIFY**| Maintain React components; enforce disclaimers ("Exploratory / Research only"). |
| **Common Utilities** | `backend/common/` | **ADD** | Foundation modules for seed, SHA-256 hashing, provenance, and JSON logging. |
| **Config Hierarchy** | `config/` | **ADD** | Centralized `base.yaml` and `paths.yaml` configuration files. |
| **Research Environment** | `research/`, `data/`, `models/` | **ADD** | Standardized data directory structure and experiment tracking hierarchy. |
| **Unit Test Suite** | `tests/common/` | **ADD** | Unit tests for seed, hashing, and provenance utilities. |

---

## 4. Phase 0 Audit Conclusion
The repository has a solid, well-factored foundation in its CPIC rule engine (`backend/pgx/`), FastAPI backend, and React dashboard. Phase 0 establishes the strict research control baseline (provenance policy, SHA-256 hashing, deterministic seeds, JSON logging, and YAML config) required before conducting machine learning experiments in Phase 1 and Phase 2.
