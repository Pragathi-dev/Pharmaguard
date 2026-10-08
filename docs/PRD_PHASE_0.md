# PHASE 0: ARCHITECTURE & PROJECT FOUNDATION

## 1. Objective
Audit the existing PharmaGuard repository, record its state, and establish the research-grade project skeleton (config, logging, experiment tracking, provenance conventions) **without breaking any existing functionality**.

## 2. Why This Phase Exists
All later phases depend on stable conventions: paths, configs, schemas, seeds, and a verified baseline. It also confirms which of our KEEP/MODIFY/REPLACE assumptions are true.

## 3. Prerequisites
Existing repo; Python >=3.10, Node >=18; existing tests runnable.

## 4. Inputs
Existing repository; any existing `.cbm`/CatBoost code; existing tests; existing sample VCF.

## 5. Outputs
- `docs/AUDIT_PHASE0.md` (architecture audit)
- `docs/DATA_PROVENANCE_POLICY.md`
- `config/` skeleton and `research/` skeleton
- `reports/baseline_tests_phase0.txt`
- `backend/common/{logging_config,seed,hashing,provenance,enums}.py`

## 6. Technical Requirements
1. **Do not modify any existing source file** in this phase except `requirements*.txt` / `package.json` additions (append-only) and `.gitignore`.
2. Run existing backend tests, frontend build, and a sample-VCF end-to-end call. Save results verbatim. Do not fix failures. List them.
3. Audit report must cover: backend architecture, frontend architecture, VCF pipeline, rule/CPIC logic (where tables live, how they are versioned), existing CatBoost code/model (mark as UNVERIFIED), DB/report logic, auth, endpoints, tests, dashboard. Include a table mapping each component to KEEP/MODIFY/REPLACE/ADD with justification.
4. Create a deterministic-seed utility, structured logging (JSON lines), SHA-256 file hashing, and a provenance helper that stamps `provenance_class`, `source`, `retrieved_at`, `sha256`, `schema_version`.
5. Define the allowed `provenance_class` enum in one module; all later code imports it. Values:
   `REAL_PATIENT_GENOTYPE`, `REAL_REFERENCE_LABEL`, `DERIVED_SILVER_LABEL`, `KNOWLEDGE_BASE`, `POPULATION_AGGREGATE`, `PHARMACOVIGILANCE_CONTEXT`, `AUGMENTED_REAL`, `SYNTHETIC_RECOMBINANT`.
6. Pin dependencies in `requirements-research.txt`: catboost, scikit-learn, pandas, pyarrow, shap, cyvcf2 (optional; fall back to existing parser), pyyaml, pydantic, pytest, matplotlib.

## 7. Repository Changes
Create:
```
config/{base.yaml,paths.yaml}
backend/common/{__init__,logging_config,seed,hashing,provenance,enums}.py
research/{__init__.py,README.md}
data/{raw,interim,processed,external,knowledge}/.gitkeep
experiments/.gitkeep   reports/.gitkeep   models/.gitkeep
docs/{AUDIT_PHASE0.md,DATA_PROVENANCE_POLICY.md}
tests/common/test_{seed,hashing,provenance}.py
requirements-research.txt
```
Modify: `.gitignore` (ignore `data/raw`, `data/interim`, large artifacts). No source files.
Remove: nothing.

## 8. Data Schema
`provenance` stamp (dict):
`{provenance_class: enum, source: str, source_version: str, retrieved_at: ISO8601, sha256: str, schema_version: str}`

## 9. APIs / Interfaces
- `set_global_seed(seed: int) -> None` (python, numpy, catboost-compatible)
- `sha256_file(path) -> str`
- `make_provenance(cls, source, version, path=None) -> dict`
- `get_logger(name) -> logging.Logger` (JSON lines to `logs/`)

## 10. Algorithms / Logic
`set_global_seed` seeds `random`, `numpy`, and sets `PYTHONHASHSEED`. `make_provenance` rejects unknown classes with `ValueError`. Hashing reads in 1 MB chunks.

## 11. Error Handling
Missing config: clear `FileNotFoundError` naming the key. Unknown provenance class: `ValueError`. Failing baseline tests are recorded, not hidden.

## 12. Logging
Log audit steps, test command outputs, and library versions into `reports/baseline_tests_phase0.txt`.

## 13. Testing Requirements
- Unit: seed reproducibility (same seed gives same numpy draw), hash determinism, provenance validation, enum membership.
- Regression: pre-existing suite result identical before and after this phase.

## 14. Research Validation
None numerically. The deliverable is the reproducibility baseline: environment and versions recorded.

## 15. Acceptance Criteria
- Audit doc contains all required sections plus the KEEP/MODIFY/REPLACE table.
- Existing tests: same pass/fail set as before the phase.
- New tests pass.
- Zero diffs to existing source files (verify with `git diff --stat`).

## 16. Deliverables
All files listed in sections 5 and 7.

## 17. Definition of Done
- [ ] Audit complete and committed
- [ ] Baseline test log saved
- [ ] Common utilities with tests passing
- [ ] No existing source modified
- [ ] Provenance policy documented

## 18. Handoff to Next Phase
Stable: `backend/common.*` interfaces, `ProvenanceClass` enum, directory layout, config loading. Phase 1 expects `config/paths.yaml` and the provenance helper.

```text
PHASE 0 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
