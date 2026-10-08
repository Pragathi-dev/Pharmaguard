# PHARMAGUARD PHASE 2: CATALOGUE GAPS REPORT

**Target Genes Audited:** CYP2C19, CYP2C9, CYP2D6, DPYD, SLCO1B1  
**Source Reference:** CPIC Guideline Tables & PharmVar GRCh38 Allele Definitions

---

## 1. Catalogue Sourcing
All catalogued sites in `config/pgx_site_catalogue.yaml` were derived directly from CPIC/PharmVar defining variant tables (`backend/pgx/reference_data.py`).

## 2. Gaps & Un-catalogued Rare Variants
- **Rare Novel Variants:** Novel or rare indels not listed in PharmVar core defining tables are omitted from the site catalogue and flagged for exploratory ML feature engineering in Phase 5.
- **Copy Number Variations (CNVs):** Whole-gene duplications and deletions (e.g. CYP2D6 *5 gene deletion or dup) require structural variant depth callers and are handled via dedicated CNV flags in Phase 3.
