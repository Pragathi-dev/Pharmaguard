# PHASE 5: RESEARCH DATASET CONSTRUCTION

## 1. Objective
Build the leakage-safe research dataset: labels from full-information calls, group-aware train/val/calib/test splits, a seeded degradation simulator that produces realistic missing-genotype views, and the ML feature table. Every row must be traceable to a sample, a degradation configuration, a seed, and a provenance class.

## 2. Why This Phase Exists
All experimental claims (E1-E9) depend on the correctness of this dataset. A single leak (same family in train and test, label computed from the degraded view, imputer fit on all data) would invalidate the paper. This phase makes leakage structurally impossible and testable.

## 3. Prerequisites
- Phases 0-3 complete and approved. Phase 4 knowledge snapshots recommended but not required (record `kb_version` either way).
- `site_calls_1000g.parquet`, `sample_qc_1000g.parquet` (Phase 2).
- `pgx_calls_1000g_full_strict.parquet` (Phase 3 silver labels).
- `sample_metadata.parquet` with `relatedness_group`, `superpopulation` (Phase 1).
- `gold_label_availability.json` and, if available, GeT-RM consensus table (Phase 1).

## 4. Inputs
- Files listed above.
- `config/research.yaml` (new): seeds, split proportions, degradation grid, feature options, rare-class threshold.
- `backend/pgx.run_engine` (Phase 3) for computing `rule_call` on degraded views.

## 5. Outputs
- `data/processed/splits.parquet` (sample-level split assignment) and `data/processed/splits.sha256`
- `data/processed/labels.parquet`
- `data/processed/ml_dataset.parquet` (one table, or one per gene if size requires)
- `data/processed/degradation_masks/` (stored masks for frozen test views)
- `reports/phase5_dataset_card.md`
- `reports/phase5_split_audit.md`
- `reports/phase5_rare_classes.md`

## 6. Technical Requirements

### 6.1 Labels
1. Label = CPIC phenotype class from the **full-information strict** engine call (Phase 3), per sample and gene.
2. Label source per row: `gold` if a GeT-RM consensus phenotype exists for that sample and gene **and** the engine agrees or the discrepancy is recorded; otherwise `silver`. If gold and silver disagree, keep the **gold** label, set `label_conflict=true`, and list every case in the dataset card. Never silently choose.
3. Exclude from labelling any (sample, gene) where the full-information call is `PARTIAL`, `UNRESOLVED`, `STRUCTURAL_UNRESOLVED` or `Indeterminate`. Count and report exclusions per gene.
4. CYP2D6: label only the SNV-resolvable subset; carry `structural_variation_assessed=false` into the dataset card and every table.

### 6.2 Splits
1. Split unit is `relatedness_group` (never row, never sample). All genes, all degradation views, and all augmented derivatives of a sample stay together.
2. Four splits: `train`, `val` (early stopping/tuning), `calib` (conformal calibration only), `test` (touched once for final numbers). Default proportions 60/10/15/15, configurable.
3. Stratify at the group level by `superpopulation` and, where feasible, by the presence of rare phenotype classes. If exact stratification is impossible, use iterative or greedy balancing and **report the achieved balance**; do not claim stratification that was not achieved.
4. Save split assignments with a SHA-256 hash. All later phases load this file; no phase may re-split.
5. Secondary split for E5: leave-one-superpopulation-out assignments saved as separate files (`splits_loso_<SUPERPOP>.parquet`), built by the same group rules.
6. Split assignment is fixed before any model-dependent step.

### 6.3 Degradation simulator
1. Operates on `site_calls` (Phase 2 representation), never on labels.
2. Degradation types (each with configurable levels and a seed):
   - `random_dropout`: independently set a fraction p of **defining and tag** sites to `NOT_IN_VCF` (levels e.g. 0, 5, 10, 25, 50 percent; 0 is the full-information control).
   - `array_like`: retain only sites in a supplied "array panel" list (config file with site IDs); the panel list must be sourced from a documented public array manifest or declared as a hypothetical panel with a clear label. Do not invent a vendor's panel.
   - `low_coverage`: convert a fraction of genotypes to `NO_CALL`, with probability increasing for heterozygous genotypes (documented model) to mimic allele dropout.
   - `unphased`: remove phase information (`|` to `/`).
   - `combined`: optional composition of the above.
3. The simulator changes only the observation status and phase fields; it never alters true genotype values at retained sites.
4. Every degraded view has a `view_id` = hash(sample_id, degradation_type, level, seed). Frozen seeds for val/calib/test views; masks for those splits are stored on disk and hashed so they never change.
5. Training views may use multiple random seeds (data multiplication), but each is a distinct, logged `view_id`.

### 6.4 Features
Per (sample, gene, view):
1. Genotype features: for each catalogued site, a categorical code `0/1/2` for dosage (HOM_REF/HET/HOM_ALT) **only when observed**; otherwise a distinct missing code (CatBoost-native missing, plus an explicit missing indicator column).
2. Missing indicators: one binary column per site.
3. `n_missing_defining`, `n_missing_tag`, `frac_observed_defining`.
4. `rule_call_phenotype` and `rule_call_confidence_flag`: obtained by running the Phase 3 engine on the **degraded** view in `reference_default` mode (the B0 call) and, as a separate feature, in `strict` mode. The rule call is **never** computed from the full-information view.
5. `phased_fraction`.
6. `ancestry` (superpopulation): included as a nullable column controlled by `features.include_ancestry` (default `false`). When false, the column is absent from model inputs but retained in a separate `analysis_meta` table for stratified evaluation.
7. Never include: label, full-information diplotype, any column derived from full-information calls, `relatedness_group`, `split`.

### 6.5 Leakage controls (enforced in code and tests)
- Encoders, scalers and any statistic (e.g. allele frequency used as a feature) are fit on `train` rows only, then applied to others.
- No feature may be computed using val/calib/test labels or genotypes outside the row's own view.
- Population allele frequencies used as features, if any, come only from train samples.
- Test and calib view masks are frozen before any training.
- The dataset builder refuses to run if `splits.sha256` does not match the stored hash.

### 6.6 Rare classes
For each gene, list phenotype classes with fewer than `rare_class_threshold` (default 20) labelled samples per split. Do not drop silently. Report; where a class is too rare to evaluate, merge only if CPIC defines a coarser grouping, and record the mapping (e.g. `label_coarse`). Keep the original fine label.

## 7. Repository Changes
Create:
```
backend/research/__init__.py
backend/research/labels.py
backend/research/splits.py
backend/research/degrade.py
backend/research/features.py
backend/research/build_dataset.py
backend/research/guards.py          # leakage assertions usable by later phases
scripts/research/build_labels.py
scripts/research/make_splits.py
scripts/research/build_ml_dataset.py
config/research.yaml
config/array_panels/<panel>.yaml    # documented, sourced or labelled hypothetical
tests/research/test_{labels,splits,degrade,features,guards,build_dataset,determinism}.py
tests/fixtures/research/*
```
Modify: nothing in existing application code.
Remove: nothing.

## 8. Data Schema
`splits.parquet`: `sample_id, relatedness_group, superpopulation, split (train|val|calib|test), split_seed, split_version`

`labels.parquet`: `sample_id, gene, label_fine, label_coarse, label_source (gold|silver), label_conflict(bool), structural_variation_assessed(bool), kb_version, engine_version, provenance_class`

`ml_dataset.parquet`:

| Column | Type | Notes |
|---|---|---|
| row_id | str | hash(sample_id, gene, view_id) |
| sample_id | str | |
| gene | str | |
| view_id | str | |
| degradation_type | enum | `none|random_dropout|array_like|low_coverage|unphased|combined` |
| degradation_level | float | |
| degradation_seed | int | |
| g__<site_id> | category/int | dosage code or missing |
| m__<site_id> | int8 | missing indicator |
| n_missing_defining | int | |
| n_missing_tag | int | |
| frac_observed_defining | float | |
| rule_call_b0 | str | degraded-view reference_default phenotype |
| rule_call_b1 | str | degraded-view strict phenotype |
| rule_conf_b1 | enum | confidence_flag |
| phased_fraction | float | |
| ancestry | str? | present only if configured |
| label_fine | str | |
| label_coarse | str | |
| label_source | enum | |
| split | enum | copied from `splits.parquet` |
| parent_row_id | str? | null for real rows |
| synthetic_flag | int8 | 0 in this phase |
| provenance_class | enum | `AUGMENTED_REAL` for degraded views of real samples |
| schema_version | str | |

`analysis_meta.parquet`: `row_id, sample_id, superpopulation, population, relatedness_group` (never joined into model inputs).

## 9. APIs / Interfaces
- `build_labels(pgx_calls_full, gold_table, sample_metadata) -> labels_df`
- `make_splits(sample_metadata, config) -> splits_df` (deterministic given seed)
- `degrade(site_calls, spec: DegradationSpec, seed) -> site_calls_degraded, mask`
- `build_features(site_calls_degraded, engine, catalogue, config, train_stats) -> features_df`
- `assert_no_leakage(ml_dataset, splits, labels) -> None` (raises `LeakageError`)
- CLI:
  - `python scripts/research/make_splits.py --config config/research.yaml`
  - `python scripts/research/build_labels.py`
  - `python scripts/research/build_ml_dataset.py --config config/research.yaml`

## 10. Algorithms / Logic
1. **Labels:** merge silver (Phase 3 strict full-information calls) and gold; apply exclusions; compute `label_coarse` from the CPIC-defined grouping file if present.
2. **Splits:** compute group-level attributes (superpopulation composition, rare-class presence); assign groups to splits with a seeded greedy algorithm targeting proportions and stratification; verify no group appears twice; write hash.
3. **Degradation:** for each sample and each spec in the grid, apply the mask using a `numpy.random.Generator` seeded from `(base_seed, view_id)`; log kept/removed counts.
4. **Rule-call features:** run `run_engine` in both modes on each degraded view; cache by `view_id`.
5. **Feature assembly:** build `g__`, `m__` columns; compute counts; attach labels by (sample, gene); attach split; drop forbidden columns.
6. **Guards:** run all leakage assertions before writing output; write the dataset only if all pass.
7. **Frozen views:** val, calib and test views are generated once, stored, and loaded on later runs; train views may be regenerated from seeds.

## 11. Error Handling
| Failure | Handling |
|---|---|
| Group appears in two splits | `LeakageError`, abort |
| Split hash mismatch | Abort with message to restore or regenerate deliberately |
| Sample missing labels for a gene | Exclude row, count in report |
| Array panel file missing or unsourced | Abort for that degradation type, others continue |
| Degradation level out of range | Validation error |
| Too few groups for requested stratification | Report achieved balance; continue only if the minimum group count per split is met, else abort |
| Gold/silver conflict | Keep gold, flag, list |

## 12. Logging
Seeds, config hash, split hash, counts per split/gene/class/superpopulation, exclusions with reasons, degradation statistics (fraction of sites removed per view), engine and KB versions, wall time, and all guard results.

## 13. Testing Requirements
Unit and integration tests on small fixtures:
- **Split guards:** no `relatedness_group` or `sample_id` in more than one split; all views and genes of a sample share a split; hash verification catches tampering.
- **Determinism:** same seed and config give identical splits, masks and datasets (byte-equal hashes).
- **Degradation:** only observation status changes, genotype values at retained sites unchanged; level 0 equals the original; dropout fraction within statistical tolerance; array_like retains exactly the panel sites; masks reproducible.
- **Features:** missing indicators match missing statuses; no forbidden columns present (test iterates over a deny-list); `rule_call` equals the engine run on the degraded view and differs from the full-information call in at least one constructed case.
- **Label leakage:** label never appears as a feature; full-information diplotype never present in model inputs.
- **Fit-on-train-only:** a test that fits statistics on a dataset where val/test contain sentinel values and asserts they do not influence train-derived stats.
- **Rare classes:** class with fewer than threshold samples is reported, not dropped.
- **Gold/silver conflict** fixture is flagged and listed.
- Existing suite stays green.

## 14. Research Validation
Generate `reports/phase5_dataset_card.md` from computed values only:
- samples and labelled rows per split, gene, phenotype class, superpopulation, label source
- number of relatedness groups per split
- exclusions and their reasons
- degradation grid and fraction of defining sites actually removed
- achieved stratification balance
- gold/silver agreement statistics and conflicts

`reports/phase5_split_audit.md`: results of every leakage assertion. This feeds the paper's data and leakage-control section.

## 15. Acceptance Criteria
- Zero overlap of `relatedness_group` across splits (assertion passes on the real data)
- Re-running with the same seed reproduces identical hashes for splits and frozen views
- No forbidden column present in `ml_dataset`
- `rule_call_*` computed from degraded views only (proven by test)
- All label exclusions and rare classes reported, none dropped silently
- Dataset card and split audit generated and contain no hand-typed numbers
- `LeakageError` triggered correctly by deliberately corrupted fixtures
- All new tests pass; full existing suite green

## 16. Deliverables
Research package modules, scripts, config, fixtures, tests, splits, labels, ML dataset, masks, three reports.

## 17. Definition of Done
- [ ] Labels built with gold/silver provenance and conflict handling
- [ ] Group-aware 4-way split saved with hash; LOSO splits saved
- [ ] Degradation simulator implemented, seeded, with frozen eval views
- [ ] Feature table built with missing indicators and degraded-view rule calls
- [ ] Leakage guards implemented and tested (including negative tests)
- [ ] Dataset card and split audit generated
- [ ] Owner has reviewed the dataset card before Phase 6

## 18. Handoff to Next Phase
Available: `splits.parquet` (hash-locked), `labels.parquet`, `ml_dataset.parquet`, `analysis_meta.parquet`, frozen val/calib/test views, `guards.py`. **Stable contracts:** the `ml_dataset` schema and column prefixes `g__` / `m__`, the split names, the frozen-view rule, and the requirement that no later phase re-splits. Phase 6 trains and evaluates baselines on this table; Phase 7 uses `calib` exclusively for conformal calibration; Phase 8 may add synthetic rows to `train` only.

```text
PHASE 5 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
