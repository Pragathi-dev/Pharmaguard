# PHASE 1: DATA ACQUISITION & DATA PROVENANCE

## 1. Objective
Build scripted, reproducible acquisition and validation of all datasets, with manifests that prove exactly what was used, and an explicit feasibility report on label availability.

## 2. Why This Phase Exists
Scientific validity depends on knowing exactly which data exist, where they came from, and which labels are real. The GeT-RM overlap decides whether we have gold labels.

## 3. Prerequisites
Phase 0 complete.

## 4. Inputs
- IGSR / 1000 Genomes high-coverage VCFs (or regional slices) for CYP2C19, CYP2C9, CYP2D6, DPYD, SLCO1B1 gene regions (GRCh38). **[VERIFY exact release and URLs on official IGSR pages; do not guess]**
- IGSR sample metadata: population, superpopulation, pedigree/relatedness file. **[VERIFY]**
- GeT-RM consensus tables. **[VERIFY availability, genes covered, and overlap with 1000G IDs]**
- CPIC / PharmVar / ClinPGx downloads (snapshots only; recorded in Phase 4)
- Professor's Drug/ADR dataset (if provided) at `data/external/professor_drug_adr.csv`

## 5. Outputs
- `data/raw/1000g/...` regional VCFs (gitignored) and `data/manifests/raw_manifest.json`
- `data/processed/sample_metadata.parquet`
- `data/processed/gold_label_availability.json`
- `data/manifests/pgx_regions.yaml` (gene to GRCh38 coordinates)
- `reports/phase1_data_report.md`

## 6. Technical Requirements
1. Acquisition via `scripts/data/download_1000g_regions.py` using tabix/HTTP range slicing to download **only** the 5 gene regions (plus flanks), not whole genomes. Support `--dry-run` and resume.
2. Every downloaded file hashed and recorded in the manifest with URL, date, size, sha256, provenance class.
3. Gene coordinates stored in a YAML file with explicit genome build; a validator rejects build mismatches (GRCh37 vs GRCh38).
4. Sample metadata table: join population/superpopulation/pedigree strictly on `sample_id`; log unmatched IDs.
5. **Gold-label feasibility check:** compute, per gene, the number of 1000G sample_ids that appear in GeT-RM. Write `gold_label_availability.json`. If overlap is under 30 samples for a gene, flag the gene `GOLD_INSUFFICIENT`; headline claims for that gene will be silver-only.
6. Professor dataset handling: if present, validate columns via configurable mapping (`config/pv_columns.yaml`), copy to `data/external/`, stamp `PHARMACOVIGILANCE_CONTEXT`, and **assert no genotype or sample-linking columns exist or are created**. If absent, the pipeline continues and logs `PV_CONTEXT_ABSENT`.
7. No network calls inside tests; use small fixture files.

## 7. Repository Changes
Create:
```
scripts/data/{download_1000g_regions.py,build_sample_metadata.py,check_gold_overlap.py,ingest_pv_context.py}
backend/data/{manifest.py,regions.py,metadata.py}
config/{data_sources.yaml,pv_columns.yaml}
data/manifests/pgx_regions.yaml
tests/data/{test_manifest,test_regions,test_metadata,test_gold_overlap,test_pv_ingest}.py
tests/fixtures/data/{mini_region.vcf.gz(+.tbi),mini_metadata.tsv,mini_getrm.csv}
```
Modify: none. Remove: none.

## 8. Data Schema
`sample_metadata`: `sample_id:str, population:str, superpopulation:str, sex:str?, family_id:str?, relatedness_group:str, provenance_class, source_version`

`raw_manifest` entry: `{path, url, sha256, bytes, retrieved_at, genome_build, provenance_class, tool_versions}`

`gold_label_availability`: `{gene: {n_gold_samples, n_overlap_1000g, status: OK|GOLD_INSUFFICIENT}}`

## 9. APIs / Interfaces
- `load_regions(path) -> dict[gene, Region(chrom, start, end, build)]`
- `write_manifest_entry(path, **meta) -> None` (append-safe, atomic)
- `verify_manifest(manifest_path) -> list[Mismatch]` (re-hash and compare)
- CLI: `python scripts/data/download_1000g_regions.py --genes all --dry-run`

## 10. Algorithms / Logic
- **Relatedness groups:** build connected components over pedigree links; assign `relatedness_group` so Phase 5 can group-split. Samples with missing pedigree get a singleton group.
- **Gold overlap:** normalize IDs (strip whitespace, case), intersect sets per gene, report counts and which superpopulations are represented.
- **Region download:** query by coordinates +/- flank (default 5 kb), concatenate per gene, index.

## 11. Error Handling
- Network failure: retry with backoff (3x), then fail with partial-file cleanup.
- Hash mismatch: abort and report.
- Missing GeT-RM: warning, `gold_available=false`, continue.
- Build mismatch: hard error.

## 12. Logging
Each download (URL, bytes, duration, sha256), unmatched sample IDs, overlap counts, and any skipped sources.

## 13. Testing Requirements
- Unit: manifest write/verify, region loading, build-mismatch rejection, pedigree grouping on a fixture family, ID normalization.
- Integration: run full ingestion on fixtures end-to-end offline.
- Edge: empty VCF region, duplicate sample IDs, professor CSV with missing columns, PV file containing a `sample_id` column (must be rejected).

## 14. Research Validation
Produce `reports/phase1_data_report.md` with: number of samples, per-superpopulation counts, number of relatedness groups, gold-label overlap per gene, and a statement of which headline claims are gold-supported. Numbers are filled by the script, not by hand.

## 15. Acceptance Criteria
- All 5 gene regions retrievable (or fixture-verified) with matching manifest hashes
- `verify_manifest` returns zero mismatches
- Gold-overlap JSON generated for all 5 genes
- PV ingestion refuses any sample-linking column
- All new tests pass offline; existing tests unchanged

## 16. Deliverables
Scripts, modules, configs, fixtures, tests, data report.

## 17. Definition of Done
- [ ] Manifests complete and verified
- [ ] Sample metadata with relatedness groups built
- [ ] Gold-label feasibility documented per gene
- [ ] PV context isolated and provenance-stamped (or absent-mode confirmed)
- [ ] Tests pass; report generated

## 18. Handoff to Next Phase
Available: raw regional VCFs, `sample_metadata.parquet`, `pgx_regions.yaml`, manifest tooling, gold-availability JSON. Stable contracts: `sample_id` format, `relatedness_group` column, region YAML schema. Phase 2 expects regional VCFs plus the regions file.

```text
PHASE 1 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
