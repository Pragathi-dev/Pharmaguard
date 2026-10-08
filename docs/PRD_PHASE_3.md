# PHASE 3: DETERMINISTIC PGx INTERPRETATION ENGINE

## 1. Objective
Build a deterministic, versioned star-allele, diplotype and phenotype engine that consumes the Phase 2 `site_calls` table and produces structured per-sample, per-gene results, including which defining sites were missing. The engine must run in two modes: `reference_default` (legacy behaviour, baseline B0) and `strict` (missing defining sites prevent a confident call, baseline B1).

## 2. Why This Phase Exists
This engine is (a) the authoritative clinical logic shown to users, (b) the source of silver labels from full-information data, (c) the baseline B0/B1 in experiments, and (d) the source of the `rule_call` feature for the ML model. Its correctness and its explicit handling of uncertainty underpin the whole research claim.

## 3. Prerequisites
- Phases 0-2 complete and approved.
- `site_calls` and `sample_qc` tables, site catalogue, status enum (Phase 2).
- Existing rule/CPIC logic in the repo (inspect first; reuse; do not discard).
- Phase 4 (knowledge layer) may run in parallel. If its snapshots are not ready, use the existing tables and label the version `existing_rules`.

## 4. Inputs
- `data/processed/site_calls_1000g.parquet` (or fixtures)
- `config/pgx_site_catalogue.yaml`
- Allele definition files in `data/knowledge/alleles/<gene>.yaml` (star allele to defining variants, function). Source: existing rule tables initially; PharmVar/CPIC snapshots when Phase 4 delivers them.
- Phenotype mapping files in `data/knowledge/phenotypes/<gene>.yaml` (diplotype or activity score to CPIC phenotype term).
- Existing sample VCF and existing expected recommendations (for regression).

## 5. Outputs
- `backend/pgx/` package
- `data/processed/pgx_calls_1000g_full_strict.parquet` (full-information strict calls: silver label source)
- `data/processed/pgx_calls_1000g_full_refdefault.parquet`
- `reports/phase3_phenotype_distribution.md`
- `reports/phase3_regression_vs_existing.md`
- `reports/phase3_pharmcat_crosscheck.md` (or a "not run" note)
- Golden test fixtures and tests

## 6. Technical Requirements
1. **No hard-coded allele or phenotype data in Python.** Load from versioned YAML/JSON files. Each file declares `source`, `source_version`, `retrieved_at` or `existing_rules`.
2. **Do not invent definitions or phenotype mappings.** Entries must come from the existing rule tables or official CPIC/PharmVar documents. Anything unsourced is omitted and logged as `UNDEFINED`.
3. **Two modes** selectable by argument:
   - `reference_default`: any defining site not observed is treated as reference. This reproduces legacy behaviour exactly (baseline B0).
   - `strict`: if any defining site needed to discriminate alleles is not observed, the gene result is `PARTIAL` or `UNRESOLVED`, not a confident call (baseline B1).
4. **Output per (sample, gene)**: `diplotype`, `allele1`, `allele2`, `candidate_diplotypes` (list, when ambiguous), `phenotype` (CPIC term, or `Indeterminate`), `activity_score` (only where CPIC defines one, else null), `missing_defining_sites` (list of `site_id`), `n_defining_sites`, `n_observed_defining`, `confidence_flag`, `phasing_ambiguous` (bool), `engine_version`, `kb_version`, `mode`.
5. **`confidence_flag` values:** `COMPLETE`, `PARTIAL`, `UNRESOLVED`, `STRUCTURAL_UNRESOLVED`.
6. **Gene-specific scope:**
   - CYP2C19, CYP2C9, SLCO1B1: SNV-based star-allele or function-class calling.
   - DPYD: variant-based activity score model as defined by CPIC; unknown or untested variants do not contribute and the result must record that only catalogued variants were assessed.
   - CYP2D6: SNV-only. Always set `structural_variation_assessed=false`. Set `STRUCTURAL_UNRESOLVED` when SNV evidence is consistent with possible deletion, duplication, or hybrid alleles, or when the catalogue cannot exclude them. Do **not** report CYP2D6 accuracy beyond this scope, and do not output an activity score that implies copy number was known.
7. **Phasing:** when het genotypes at multiple defining sites make the diplotype ambiguous and no phase information exists, enumerate candidate diplotypes, compute the phenotype for each, and report `phenotype` only if all candidates agree; otherwise `Indeterminate` with `phasing_ambiguous=true` and the candidate list.
8. **Determinism and reproducibility:** identical input and versions give identical output; output is independent of row order.
9. **Backward compatibility:** the legacy recommendation output for the existing sample VCF must stay unchanged. The engine is introduced behind a stable interface; existing code paths continue to work.
10. **Optional PharmCAT cross-check:** if PharmCAT is installable (Java required), provide a script that runs it on selected samples and reports concordance of diplotype and phenotype. If not installable, write a "not run, reason" report. Do not fabricate concordance.

## 7. Repository Changes
Create:
```
backend/pgx/__init__.py
backend/pgx/schemas.py          # dataclasses/pydantic result models
backend/pgx/knowledge_files.py  # loaders + validators for allele/phenotype YAML
backend/pgx/alleles.py          # site calls -> per-haplotype allele candidates
backend/pgx/diplotype.py        # candidate enumeration, phasing ambiguity
backend/pgx/phenotype.py        # diplotype/activity score -> CPIC phenotype
backend/pgx/engine.py           # public entry point; modes; confidence flags
backend/pgx/cyp2d6.py           # SNV-only scope and structural flagging
backend/pgx/dpyd.py             # activity-score logic
data/knowledge/alleles/{CYP2C19,CYP2C9,CYP2D6,DPYD,SLCO1B1}.yaml
data/knowledge/phenotypes/{CYP2C19,CYP2C9,CYP2D6,DPYD,SLCO1B1}.yaml
scripts/pgx/run_engine_on_site_calls.py
scripts/pgx/crosscheck_pharmcat.py
tests/pgx/test_{schemas,knowledge_files,alleles,diplotype,phenotype,engine,cyp2d6,dpyd,modes,regression}.py
tests/fixtures/pgx/*.parquet|*.yaml
```
Modify: a thin adapter so existing recommendation code can call the engine (optional, behind a flag). Default behaviour unchanged. Record each edit in the phase report.
Remove: nothing. Existing hard-coded tables stay until Phase 4 reconciliation is approved.

## 8. Data Schema
`pgx_calls` (Parquet):

| Column | Type | Notes |
|---|---|---|
| sample_id | str | |
| gene | str | |
| mode | enum | `reference_default` or `strict` |
| diplotype | str? | e.g. `*1/*2`, null if unresolved |
| allele1 / allele2 | str? | |
| candidate_diplotypes | list[str] | length 1 when unambiguous |
| phenotype | str | CPIC term or `Indeterminate` |
| activity_score | float? | only where CPIC defines one |
| missing_defining_sites | list[str] | `site_id`s |
| n_defining_sites | int | |
| n_observed_defining | int | |
| confidence_flag | enum | see section 6.5 |
| phasing_ambiguous | bool | |
| structural_variation_assessed | bool | false for CYP2D6 |
| engine_version | str | semantic version |
| kb_version | str | allele/phenotype file versions |
| provenance_class | enum | `DERIVED_SILVER_LABEL` when run on full information |
| schema_version | str | |

Allele definition YAML:
```yaml
gene: CYP2C19
source: pharmvar | cpic | existing_rules
source_version: "<version or date>"
alleles:
  - name: "*2"
    function: "No function"
    defining_sites: [site_id, ...]   # all must be alt on the haplotype
reference_allele: "*1"
```
Phenotype mapping YAML:
```yaml
gene: CYP2C19
source: cpic
source_version: "<version>"
mapping_type: diplotype_function | activity_score
rules:
  - condition: "<function pair or AS range>"
    phenotype: "<CPIC term>"
```

## 9. APIs / Interfaces
- `run_engine(site_calls_df, mode, kb_dir, genes=None) -> pandas.DataFrame` (schema in section 8)
- `interpret_gene(sample_site_calls, gene, mode, kb) -> GeneResult`
- `load_knowledge(kb_dir) -> KnowledgeBase` (validates schemas, versions, undefined entries)
- `engine_version() -> str`
- CLI: `python scripts/pgx/run_engine_on_site_calls.py --site-calls data/processed/site_calls_1000g.parquet --mode strict --out data/processed/pgx_calls_1000g_full_strict.parquet`
- No new HTTP endpoint in this phase (Phase 10).

## 10. Algorithms / Logic
For each (sample, gene):
1. Collect catalogued defining sites and their statuses.
2. **Observation filter:**
   - `reference_default`: statuses other than `HET`/`HOM_ALT` are treated as reference for allele matching.
   - `strict`: only `HOM_REF`, `HET`, `HOM_ALT` count as observed. `NOT_IN_VCF`, `NO_CALL`, `FILTERED`, `LOW_QUALITY`, `MULTIALLELIC` are unobserved and added to `missing_defining_sites`.
3. **Haplotype resolution:**
   - Homozygous-alt sites are assigned to both haplotypes.
   - Heterozygous sites are distributed across two haplotypes in every possible way (bounded; cap enumeration and flag `UNRESOLVED` if the cap is exceeded).
   - If phase is known from `|` genotypes, restrict to the consistent assignment.
4. **Allele matching:** for each haplotype, find the star allele whose defining sites are all present as alt on that haplotype; handle nested/superset definitions by choosing the most specific match per the definition file's declared precedence. No match gives the reference allele (`*1`), subject to step 5.
5. **Strict-mode rule:** if any defining site for any allele that could change the result is unobserved, the call cannot be COMPLETE. Determine whether the missing sites could alter the phenotype class:
   - If they could: `confidence_flag=PARTIAL` (or `UNRESOLVED` if no diplotype can be proposed), `phenotype=Indeterminate`.
   - If provably irrelevant (e.g. the phenotype is identical across all possible resolutions): `PARTIAL` with the phenotype reported and the missing sites listed. Implement this by enumerating possible completions of the missing sites and comparing phenotypes.
6. **Phenotype:** map each candidate diplotype to its CPIC phenotype via the phenotype file. If candidates disagree: `Indeterminate`.
7. **DPYD:** sum per-variant activity contributions per the loaded definition; record `only_catalogued_variants_assessed=true`.
8. **CYP2D6:** run the SNV logic, then set `structural_variation_assessed=false`; set `STRUCTURAL_UNRESOLVED` when the rules in section 6.6 trigger.
9. Attach `engine_version`, `kb_version`, `mode`.

Silver labels: run in `strict` mode on full-information `site_calls`. Samples or genes with `PARTIAL`/`UNRESOLVED`/`STRUCTURAL_UNRESOLVED` at full information are **excluded from silver labelling** for that gene and the exclusion counts are reported.

## 11. Error Handling
| Failure | Handling |
|---|---|
| Missing allele or phenotype file | Hard error naming the file |
| Allele references a site not in the catalogue | Validation error at load time |
| Unknown gene in input | Skip with warning |
| Enumeration cap exceeded | `UNRESOLVED`, logged |
| Phenotype mapping gap for a diplotype | `Indeterminate` plus `UNDEFINED_MAPPING` log; never guess |
| Conflicting definitions in one file | Validation error |

## 12. Logging
Engine and KB versions, mode, counts by `confidence_flag` per gene, number of ambiguous phasing cases, undefined-mapping events, CYP2D6 structural-flag counts, runtime.

## 13. Testing Requirements
Unit and golden tests:
- **Golden cases** written only from official CPIC/PharmVar documentation or the existing validated rules. Each test cites its source in a comment. Never invent expected values.
- Homozygous reference, het, hom-alt for each gene.
- Compound heterozygote with known phase vs unknown phase.
- Strict mode: one missing defining site leads to `PARTIAL`/`Indeterminate`; the same input in `reference_default` yields a confident call (this pair of tests encodes the research premise).
- Missing site that provably cannot change phenotype: phenotype reported, `PARTIAL`.
- CYP2D6 always `structural_variation_assessed=false`; structural flag fires per rule.
- DPYD activity score aggregation; unknown variants not counted.
- Determinism: shuffled row order gives identical output.
- Enumeration cap behaviour.
- Knowledge-file validation errors.

Regression:
- Existing sample VCF through the legacy path yields output identical to the pre-phase snapshot.
- Engine in `reference_default` mode matches the legacy results on that sample; any differences must be listed and justified in `reports/phase3_regression_vs_existing.md`.

Integration:
- Run both modes on fixture `site_calls`; schema validation passes.
- Full existing suite green.

## 14. Research Validation
Generate `reports/phase3_phenotype_distribution.md` from computed values only:
- per-gene phenotype distribution on 1000G (full information, strict), overall and by superpopulation
- counts excluded from silver labelling and why
- rare phenotype classes and their counts (input to Phase 5 stratification)
- if gold labels exist: engine-vs-gold concordance per gene, with discrepancies listed individually (this validates label quality, not the ML model)
- PharmCAT concordance if run

## 15. Acceptance Criteria
- All 5 genes produce schema-valid output in both modes on fixtures and on 1000G (where available).
- Strict mode never returns `COMPLETE` when any relevant defining site is unobserved (assertion test).
- `reference_default` reproduces legacy output on the sample VCF, with documented diffs only.
- No allele or phenotype data hard-coded in Python (verified by test scanning for gene tables in `.py` files).
- CYP2D6 outputs always carry `structural_variation_assessed=false`.
- Determinism test passes.
- Phenotype distribution report generated from the data, not typed by hand.
- All new tests pass; full existing suite green.

## 16. Deliverables
Engine package, knowledge YAML files (sourced and versioned), scripts, silver-label parquet outputs, golden fixtures and tests, three reports.

## 17. Definition of Done
- [ ] Both modes implemented and tested
- [ ] Knowledge loaded from versioned files; unsourced entries omitted and listed
- [ ] Phasing ambiguity and structural flagging implemented
- [ ] Legacy regression documented and passing
- [ ] Silver-label exclusions counted and reported
- [ ] Gold concordance reported if gold data exists, otherwise marked not available
- [ ] All tests pass; no existing behavior changed

## 18. Handoff to Next Phase
Available: `backend/pgx` engine, `pgx_calls` schema, silver-label tables, phenotype distribution report. **Stable contracts:** the `pgx_calls` schema, `confidence_flag` values, the two mode names, and `run_engine` signature. Phase 4 supplies official knowledge snapshots and a reconciliation report; after its approval the engine's knowledge directory may be repointed without code changes. Phase 5 uses `strict` full-information calls as labels and `run_engine` on degraded `site_calls` to compute the `rule_call` feature.

```text
PHASE 3 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
