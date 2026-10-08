# PHASE 2: VCF PROCESSING & SITE EXTRACTION

## 1. Objective
Extend the existing VCF pipeline so that, for every pharmacogene site we care about, the system records an explicit **observation status**. The pipeline must distinguish "observed reference" from "not observed / missing". It must never silently treat a missing site as reference. Output a long-format `site_calls` table for both user-uploaded VCFs and the 1000 Genomes regional VCFs.

## 2. Why This Phase Exists
The core research claim is that deterministic callers fail when defining sites are missing but assumed reference. That claim cannot be tested, and the proposed model cannot be built, unless the data layer preserves missingness. Phases 3, 5, 6 and 7 all depend on this representation.

## 3. Prerequisites
- Phase 0 and Phase 1 complete and approved.
- `data/manifests/pgx_regions.yaml`, regional VCFs, `data/processed/sample_metadata.parquet`.
- `backend/common/*` utilities (logging, hashing, provenance, enums).
- Existing VCF parser and sample VCF (inspect first; extend, do not rewrite).

## 4. Inputs
- Regional 1000G VCFs from Phase 1 (`data/raw/1000g/`).
- User-uploaded VCF files (via the existing API path).
- `data/manifests/pgx_regions.yaml` (gene regions, genome build).
- A **site catalogue**: the list of defining and tag sites per gene. Source of truth is the Phase 4 / Phase 3 allele-definition tables. In this phase, use a config-driven catalogue file `config/pgx_site_catalogue.yaml`.
  - If the existing rule tables already define variant positions, derive the initial catalogue from them and mark `catalogue_source: existing_rules`.
  - Do NOT invent coordinates or alleles. If a site cannot be sourced from the existing rules or an official PharmVar/CPIC file, leave it out and list it in `reports/phase2_catalogue_gaps.md`.
- `config/qc.yaml` with thresholds (min DP, min GQ, min region call rate).

## 5. Outputs
- `backend/genomics/` package (modules listed in section 7)
- `config/pgx_site_catalogue.yaml`, `config/qc.yaml`
- `data/processed/site_calls_1000g.parquet` (long format)
- `data/processed/sample_qc_1000g.parquet`
- `reports/phase2_extraction_report.md`
- `reports/phase2_parser_comparison.md` (new extractor vs existing parser on the sample VCF)
- `reports/phase2_catalogue_gaps.md`
- Backward-compatible parser output (unchanged) plus the new representation alongside it

## 6. Technical Requirements
1. **Backward compatibility:** the existing parser's output and API response must be unchanged. The new representation is an additional function/endpoint-internal structure, not a replacement.
2. **Site status enum** (one definition, in `backend/genomics/enums.py`):
   `HOM_REF`, `HET`, `HOM_ALT`, `NO_CALL`, `NOT_IN_VCF`, `FILTERED`, `MULTIALLELIC`, `LOW_QUALITY`.
3. **Core rule:** for every catalogued site and every sample, emit exactly one row. A site absent from the VCF is `NOT_IN_VCF`, never `HOM_REF`.
4. **Distinguishing reference from missing:**
   - Single-sample VCFs and 1000G VCFs often list only variant sites. Absence of a record does not prove homozygous reference.
   - Provide a `callable_regions` mechanism: if a gVCF, reference-block records, or a user-supplied BED of callable regions is available, a site inside a callable region with no variant record becomes `HOM_REF`. If no callable-region evidence exists, it is `NOT_IN_VCF`.
   - For 1000G multi-sample VCFs, a site is considered observed for a sample if the record exists and the sample's GT is not `./.`. A catalogued site with no record in the VCF is `NOT_IN_VCF` for all samples, and is logged once per site (not once per sample).
   - Record the evidence type in a column `reference_evidence` (`explicit_gt | gvcf_block | callable_bed | none`).
5. **Normalization:** left-align and trim alleles, split multiallelic records into biallelic representation where possible, and harmonize contig names (`chr1` vs `1`). Use `bcftools norm` if available; otherwise a pure-Python fallback with a documented reduced scope. Never alter the original input files.
6. **Multiallelic handling:** if a catalogued alt allele cannot be matched unambiguously, status is `MULTIALLELIC` and the site is treated as not resolved downstream.
7. **QC:**
   - Per-genotype: DP < `min_dp` or GQ < `min_gq` becomes `LOW_QUALITY` (value retained in `dp`/`gq` columns).
   - FILTER not in (`PASS`, `.`) becomes `FILTERED`.
   - Per-sample, per-gene call rate over catalogued sites: `n_observed / n_catalogued`. Flag samples below `min_region_call_rate`.
   - Phasing: record `phased` (bool) per genotype from the GT separator.
8. **Genome build guard:** hard-fail if the VCF header or contig lengths indicate a build different from the catalogue build. If undetectable, log `BUILD_UNVERIFIED` and require an explicit `--assume-build` flag.
9. **Robustness:** malformed lines are skipped and counted, never crash the run. Empty VCF produces an empty-but-valid table with all sites `NOT_IN_VCF`.
10. **Performance:** use `cyvcf2` with region queries (tabix) when available; fall back to the existing parser otherwise. Process by gene region, not by whole file.
11. **Provenance:** every row carries `provenance_class` (`REAL_PATIENT_GENOTYPE` for 1000G; for user uploads use the same class with `source=user_upload`) and `source_file_sha256`.

## 7. Repository Changes
Create:
```
backend/genomics/__init__.py
backend/genomics/enums.py
backend/genomics/catalogue.py        # load/validate site catalogue
backend/genomics/vcf_reader.py       # region-based reader (cyvcf2 + fallback)
backend/genomics/normalize.py        # allele normalization, contig harmonization
backend/genomics/site_extractor.py   # produces site_calls rows
backend/genomics/qc.py               # per-genotype and per-sample QC
backend/genomics/callable.py         # callable-region / gVCF reference-block logic
scripts/genomics/extract_site_calls.py
scripts/genomics/compare_with_legacy_parser.py
config/pgx_site_catalogue.yaml
config/qc.yaml
tests/genomics/test_{enums,catalogue,normalize,site_extractor,qc,callable,vcf_reader}.py
tests/fixtures/genomics/*.vcf(.gz)   # tiny hand-written fixtures
```
Modify: only a thin, optional import hook in the existing VCF module if needed to expose the new extractor. Existing return values must not change. Document any such edit in the phase report.
Remove: nothing.

## 8. Data Schema
`site_calls` (Parquet, long format, one row per sample x catalogued site):

| Column | Type | Notes |
|---|---|---|
| sample_id | str | matches `sample_metadata` |
| gene | str | one of the 5 pharmacogenes |
| site_id | str | catalogue key, e.g. `CYP2C19:chr10:pos:ref>alt` |
| chrom | str | harmonized contig |
| pos | int | 1-based |
| ref | str | normalized |
| alt | str | normalized, nullable if `NOT_IN_VCF` |
| gt | str | `0/0`, `0/1`, `1/1`, `./.`, nullable |
| allele1 / allele2 | int? | nullable |
| status | enum | see section 6.2 |
| reference_evidence | enum | `explicit_gt | gvcf_block | callable_bed | none` |
| phased | bool | |
| dp | int? | |
| gq | int? | |
| filter | str? | |
| role | enum | `defining | tag` |
| provenance_class | enum | from Phase 0 |
| source_file_sha256 | str | |
| schema_version | str | |

`sample_qc`: `sample_id, gene, n_catalogued, n_observed, n_not_in_vcf, n_no_call, n_low_quality, region_call_rate, qc_pass(bool), any_unphased(bool)`

`pgx_site_catalogue.yaml` entry:
```yaml
CYP2C19:
  build: GRCh38
  catalogue_source: existing_rules | pharmvar:<version> | cpic:<version>
  sites:
    - site_id: ...
      chrom: ...
      pos: ...
      ref: ...
      alt: ...
      role: defining | tag
      rsid: ...        # nullable
      source_ref: ...  # where this entry came from
```

## 9. APIs / Interfaces
- `load_catalogue(path) -> Catalogue` (validates build, duplicates, allele sanity)
- `extract_site_calls(vcf_path, catalogue, qc_config, sample_ids=None, callable_bed=None) -> pandas.DataFrame`
- `compute_sample_qc(site_calls) -> pandas.DataFrame`
- `normalize_variant(chrom, pos, ref, alt, fasta=None) -> NormalizedVariant`
- CLI: `python scripts/genomics/extract_site_calls.py --vcf-dir data/raw/1000g --out data/processed/site_calls_1000g.parquet`
- CLI: `python scripts/genomics/compare_with_legacy_parser.py --vcf <sample.vcf>`
- No new public HTTP endpoint in this phase (Phase 10 exposes it). Existing endpoints unchanged.

## 10. Algorithms / Logic
For each gene, for each catalogued site, for each sample:
1. Fetch the VCF record(s) overlapping `chrom:pos` using a region query.
2. If no record:
   - if callable-region or gVCF-block evidence covers the position: `HOM_REF`, evidence `callable_bed`/`gvcf_block`.
   - else: `NOT_IN_VCF`, evidence `none`.
3. If records exist: normalize them, then match to the catalogued `ref>alt`.
   - No match on alt but record exists at the position: if the sample GT is `0/0`, status `HOM_REF` (explicit GT). Otherwise `MULTIALLELIC` if the alt differs from the catalogued alt and cannot be resolved.
4. Read the sample GT:
   - `./.` or `.|.` leads to `NO_CALL`.
   - Apply FILTER check (`FILTERED`), then DP/GQ check (`LOW_QUALITY`). Keep the underlying GT in the row so later phases can choose to use or ignore low-quality calls.
   - Otherwise `HOM_REF` / `HET` / `HOM_ALT` from allele counts against the catalogued alt.
5. Set `phased` from the GT separator (`|` phased, `/` unphased).
6. After all rows, compute `sample_qc` per (sample, gene).

Legacy comparison: run both the old parser and the new extractor on the sample VCF. Produce a table of per-site agreement. Differences are expected only where the old parser defaulted missing to reference; every difference must be listed and explained, not hidden.

## 11. Error Handling
| Failure | Handling |
|---|---|
| Malformed VCF line | Skip, increment counter, log line number |
| Missing index (`.tbi`) | Build index if possible, else fall back to a sequential scan with a warning |
| Contig naming mismatch | Harmonize automatically, log the mapping used |
| Genome build mismatch | Hard error with clear message |
| Catalogue entry missing coordinates | Reject at load time with entry name |
| Sample absent from metadata | Keep the row, flag `metadata_missing`, log |
| Empty VCF | Valid empty-status output, not a crash |

## 12. Logging
Per run: files processed with sha256, build check result, number of malformed lines skipped, count of sites by status, per-gene call rates, samples failing QC, normalization changes applied, and which reader (cyvcf2 or fallback) was used.

## 13. Testing Requirements
Unit tests (hand-built tiny fixtures; expected values written by hand from the fixture content):
- `HOM_REF` via explicit GT vs `NOT_IN_VCF` when the record is absent
- `NO_CALL` from `./.`
- `HET`, `HOM_ALT`, phased vs unphased
- `MULTIALLELIC` handling
- `FILTERED` and `LOW_QUALITY` thresholds
- `chr`-prefix mismatch
- Left-alignment of an indel
- Callable BED turning an absent record into `HOM_REF`
- Empty VCF; VCF with only a header; malformed record
- Build mismatch hard-fails
- Duplicate catalogue entries rejected

Integration tests:
- Full extraction on the fixture multi-sample VCF produces exactly (n_samples x n_sites) rows.
- Legacy parser comparison runs on the existing sample VCF and writes the comparison report.
- Existing test suite unchanged and passing.

Property check:
- No row may have `status=HOM_REF` with `reference_evidence=none`. Add this as an assertion test.

## 14. Research Validation
Generate `reports/phase2_extraction_report.md` from computed values only:
- distribution of `status` by gene (this quantifies how much natural missingness exists in the real data)
- per-gene call-rate distribution, overall and per superpopulation
- number of catalogued sites that are `NOT_IN_VCF` for all samples (catalogue vs VCF coverage gap)
- legacy-vs-new differences on the sample VCF

This feeds Experiment E1 (how much the reference-default assumption matters in real data).

## 15. Acceptance Criteria
- Extractor emits exactly one row per (sample, catalogued site) on all fixtures.
- Zero rows with `HOM_REF` and `reference_evidence=none`.
- All 8 status types are exercised by at least one passing test.
- Legacy parser output on the sample VCF is byte-identical to its pre-phase output.
- Comparison report lists every legacy-vs-new difference with an explanation.
- A malformed-line fixture runs to completion with the skip count logged.
- Build mismatch fixture fails with a clear error.
- `site_calls_1000g.parquet` and `sample_qc_1000g.parquet` generated, schema validated, and provenance columns populated.
- All new tests pass; the full existing suite is green.

## 16. Deliverables
All modules, configs, scripts, fixtures, tests, the Parquet outputs (or the fixture equivalents if full data was not downloaded), and the three reports.

## 17. Definition of Done
- [ ] Missing-vs-reference distinction implemented and tested
- [ ] Site catalogue loaded with no invented entries; gaps documented
- [ ] Normalization and QC working with config-driven thresholds
- [ ] Legacy parser behavior preserved; comparison report produced
- [ ] Parquet outputs generated with provenance and schema version
- [ ] All tests pass; no regression in the existing suite
- [ ] Phase 2 report committed

## 18. Handoff to Next Phase
Available: `backend/genomics` package, `site_calls` and `sample_qc` tables, site catalogue, status enum. **Stable contracts that must not change:** the `site_calls` schema, the status enum values, and the rule that missing is never reference. Phase 3 (PGx engine) consumes `site_calls` and must treat `NOT_IN_VCF`, `NO_CALL`, `FILTERED`, `LOW_QUALITY`, and `MULTIALLELIC` as non-observations in strict mode.

```text
PHASE 2 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
