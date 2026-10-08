# PHASE 4: KNOWLEDGE LAYER (CPIC / PharmVar / ClinPGx)

## 1. Objective
Build a versioned, source-attributed knowledge layer that holds allele definitions, phenotype mappings, and drug recommendations from official sources (CPIC, PharmVar, ClinPGx/PharmGKB), with a lookup API that returns source text verbatim with citation metadata. Reconcile it against the existing hard-coded rules and report differences **without silently overwriting anything**.

## 2. Why This Phase Exists
The engine (Phase 3) and the dashboard (Phase 11) are only as defensible as their knowledge sources. Official, versioned snapshots make results reproducible and let a reviewer trace every recommendation to a guideline. This phase replaces "rules we typed once" with "rules we can cite".

## 3. Prerequisites
- Phase 0 complete (provenance helpers, config, directory layout).
- Phase 1 manifest tooling available.
- Existing rule/CPIC tables in the repo (inspect; they are the reconciliation baseline).
- This phase can run in parallel with Phases 2-3. Phase 3's allele and phenotype YAML files are the integration point.

## 4. Inputs
- Official sources, **each verified by the agent before use** (endpoints, file formats, licenses, terms of use; do not guess URLs):
  - CPIC (guidelines, allele definition tables, diplotype-to-phenotype tables, recommendation tables)
  - PharmVar (star allele definitions, core variants)
  - ClinPGx / PharmGKB (annotations, drug labels, evidence levels)
- Existing in-repo rule tables.
- `config/knowledge_sources.yaml` (source name, URL, format, license note, genes of interest, drugs of interest).
- Genes in scope: CYP2C19, CYP2C9, CYP2D6, DPYD, SLCO1B1. Drugs in scope: those the existing app already supports, plus CPIC drugs for these genes only if the guideline exists.

## 5. Outputs
- `data/knowledge/<source>/<snapshot_date>/` raw snapshots with `snapshot_manifest.json`
- `data/knowledge/alleles/<gene>.yaml` and `data/knowledge/phenotypes/<gene>.yaml` (Phase 3 formats, now sourced)
- `data/knowledge/recommendations/recommendations.parquet`
- `reports/knowledge_reconciliation.md`
- `reports/knowledge_coverage.md`
- `backend/knowledge/` package and tests

## 6. Technical Requirements
1. **Official sources only.** No scraping of unofficial mirrors. Respect each source's license and terms; record the license note in the snapshot manifest. If a source's terms forbid redistribution, store only derived/normalized fields and a fetch script, and document this.
2. **Snapshots are immutable and dated.** Each download goes to `data/knowledge/<source>/<YYYY-MM-DD>/` with sha256, URL, bytes, `retrieved_at`, and the source's own version string if it has one.
3. **Verbatim text.** Recommendation text, implications, and comments are stored exactly as published. The system never paraphrases or merges recommendation text.
4. **Never invent.** If a gene, phenotype, or drug combination is not in the source, lookup returns `NOT_AVAILABLE`. No default or inferred recommendation.
5. **Provenance:** every record stamped `KNOWLEDGE_BASE` with `source`, `source_version`, `retrieved_at`, `sha256`.
6. **Normalization:** map source-specific phenotype terms to the CPIC standard terms. Keep the original term in `source_phenotype_term`. Unmapped terms are listed in the coverage report, not guessed.
7. **Reconciliation, not replacement.** Compare official snapshots to the existing hard-coded rules and produce a report with: matches, mismatches (with both values), existing-only entries, source-only entries. **Do not switch the engine or the recommendations to the new source in this phase.** Switching happens only after the user approves the reconciliation report.
8. **Switch mechanism.** Implement a config flag `knowledge.active_source: existing_rules | snapshot:<date>` so the switch is a configuration change, reversible, and recorded in each result's `kb_version`.
9. **Offline operation.** Application runtime and tests never fetch from the network. Fetching occurs only in `scripts/knowledge/fetch_snapshots.py`.
10. **Evidence fields.** Keep CPIC `classification_of_recommendation` (e.g. Strong/Moderate/Optional) and ClinPGx evidence level separately; never merge them into one score.

## 7. Repository Changes
Create:
```
backend/knowledge/__init__.py
backend/knowledge/schema.py          # pydantic models, enums
backend/knowledge/loader.py          # read snapshots/normalized files
backend/knowledge/normalize.py       # source term -> CPIC standard term
backend/knowledge/versioning.py      # snapshot discovery, active-source selection
backend/knowledge/lookup.py          # get_recommendations(...)
backend/knowledge/reconcile.py       # compare against existing rules
scripts/knowledge/fetch_snapshots.py
scripts/knowledge/build_normalized_tables.py
scripts/knowledge/reconcile_with_existing.py
config/knowledge_sources.yaml
data/knowledge/{cpic,pharmvar,clinpgx}/.gitkeep
tests/knowledge/test_{schema,loader,normalize,versioning,lookup,reconcile}.py
tests/fixtures/knowledge/*   # tiny hand-made snapshots in the official formats
```
Modify: nothing in existing recommendation code (the switch flag is read by new code only; wiring into the engine adapter happens after approval).
Remove: nothing.

## 8. Data Schema
`recommendations` (Parquet), one row per gene-phenotype-drug-source:

| Column | Type | Notes |
|---|---|---|
| gene | str | |
| phenotype | str | CPIC standard term |
| source_phenotype_term | str | as published |
| activity_score_range | str? | where applicable |
| drug | str | normalized lowercase generic name |
| recommendation_text | str | verbatim |
| implication_text | str? | verbatim |
| classification_of_recommendation | str? | CPIC |
| evidence_level | str? | ClinPGx or CPIC as published |
| guideline_id | str | |
| guideline_url | str | |
| guideline_version | str | |
| source | enum | `cpic | pharmvar | clinpgx` |
| kb_version | str | `<source>:<snapshot_date>` |
| retrieved_at | str | ISO 8601 |
| provenance_class | enum | `KNOWLEDGE_BASE` |
| schema_version | str | |

`snapshot_manifest.json`:
```json
{
  "source": "cpic",
  "snapshot_date": "YYYY-MM-DD",
  "files": [{"path": "...", "url": "...", "sha256": "...", "bytes": 0}],
  "source_version": "<as published or null>",
  "license_note": "<as stated by source>"
}
```
Lookup result:
```json
{
  "status": "FOUND | NOT_AVAILABLE",
  "gene": "...", "phenotype": "...", "drug": "...",
  "recommendation_text": "...", "classification_of_recommendation": "...",
  "evidence_level": "...", "guideline_url": "...",
  "kb_version": "...", "source": "..."
}
```

## 9. APIs / Interfaces
- `get_recommendations(gene, phenotype, drug, kb_version=None) -> LookupResult`
- `list_supported_drugs(gene=None) -> list[str]`
- `list_snapshots() -> list[SnapshotInfo]`
- `active_kb_version() -> str`
- `reconcile(existing_rules, snapshot) -> ReconciliationReport`
- CLI: `python scripts/knowledge/fetch_snapshots.py --source cpic --dry-run`
- CLI: `python scripts/knowledge/build_normalized_tables.py --snapshot-date <date>`
- CLI: `python scripts/knowledge/reconcile_with_existing.py --snapshot-date <date>`
- No HTTP endpoint in this phase (Phase 10 exposes lookup).

## 10. Algorithms / Logic
1. **Fetch:** for each configured source, verify endpoint and terms, download, hash, write the snapshot manifest. Retry with backoff (3 times); clean partial files on failure.
2. **Parse:** read official formats into raw tables. Preserve all original columns in a `raw` snapshot parquet for traceability.
3. **Normalize:**
   - gene symbols uppercase, drug names lowercase generic
   - phenotype term mapping table maintained in `config/phenotype_term_map.yaml`, built from the sources' own vocabularies; unmapped terms are reported, never auto-mapped by fuzzy matching
4. **Allele and phenotype YAML generation:** convert PharmVar/CPIC allele definitions and diplotype-phenotype tables into the Phase 3 YAML formats, including the `source` and `source_version` header. Entries that cannot be converted losslessly are omitted and listed in `knowledge_coverage.md`.
5. **Lookup:** exact match on (gene, normalized phenotype, drug) within the selected `kb_version`. No fuzzy matching, no fallback to a "nearest" phenotype. Return `NOT_AVAILABLE` otherwise.
6. **Reconciliation:** join existing rules and snapshot rows on (gene, phenotype, drug). Classify each key:
   - `MATCH` (same recommendation meaning; compare exact text and also flag text differences for human review since wording may legitimately differ)
   - `MISMATCH` (different recommendation, show both)
   - `EXISTING_ONLY`
   - `SOURCE_ONLY`
   Never auto-resolve. Summaries (counts per gene) are computed.
7. **Version switching:** `versioning.py` reads `knowledge.active_source` from config; every downstream result carries the resulting `kb_version`.

## 11. Error Handling
| Failure | Handling |
|---|---|
| Source unreachable | Retry 3 times, then fail clearly; leave existing snapshots untouched |
| Format changed upstream | Schema validation error naming the column; no partial import |
| Hash mismatch on re-verify | Abort and report |
| License prohibits redistribution | Store fetch script and derived fields only; log decision |
| Unmapped phenotype term | Listed in coverage report; row kept with `phenotype=UNMAPPED` and excluded from lookup |
| Unknown gene/drug lookup | `NOT_AVAILABLE` |
| Missing snapshot for active source | Hard error with remedy message |

## 12. Logging
Source, URL, bytes, sha256 per download; snapshot date; counts of parsed, normalized, and dropped rows with reasons; unmapped terms; reconciliation counts by class and gene; active source at runtime.

## 13. Testing Requirements
Tests use small hand-made fixtures in the official formats; no network.
- Schema validation (valid and invalid rows)
- Normalization: known term maps, unknown term reported not guessed
- Lookup: found, unknown phenotype, unknown drug, wrong version, verbatim text preserved byte-for-byte
- Versioning: multiple snapshots, pinning, missing snapshot error, config switch
- Reconciliation: one fixture for each of MATCH, MISMATCH, EXISTING_ONLY, SOURCE_ONLY
- Immutability: re-running fetch for the same date does not overwrite
- Guard test: no code path in application runtime imports the fetch script or makes network calls
- Existing test suite unchanged and green

## 14. Research Validation
`reports/knowledge_coverage.md` (computed): genes x drugs covered, phenotype terms mapped/unmapped, allele definitions imported/omitted per gene, snapshot versions used. `reports/knowledge_reconciliation.md` (computed): counts and full list of mismatches. These support the paper's reproducibility section (exact KB versions) and flag any discrepancies in the original app's rules.

## 15. Acceptance Criteria
- Snapshots for each available source stored with verified hashes and license notes
- Allele and phenotype YAMLs generated for all genes where official data exists; gaps listed
- Lookup returns verbatim text and citation metadata for every FOUND case; `NOT_AVAILABLE` otherwise
- Reconciliation report generated, with every mismatch listed and no silent changes to existing rules
- `knowledge.active_source` defaults to `existing_rules`; switching to a snapshot is a config-only change
- Offline tests pass; no network access in tests or runtime
- Full existing suite green

## 16. Deliverables
Knowledge package, fetch/normalize/reconcile scripts, snapshots, normalized tables, sourced allele/phenotype YAMLs, term map, two reports, tests, fixtures.

## 17. Definition of Done
- [ ] Official snapshots fetched, hashed, and dated
- [ ] Licenses and terms recorded per source
- [ ] Normalized recommendation table built with verbatim text
- [ ] Reconciliation and coverage reports generated
- [ ] Version-switch flag implemented, default unchanged
- [ ] Reconciliation reviewed and approved by the project owner before any switch
- [ ] All tests pass

## 18. Handoff to Next Phase
Available: versioned knowledge snapshots, sourced allele/phenotype YAMLs, `get_recommendations` lookup, reconciliation report. **Stable contracts:** the `recommendations` schema, the `LookupResult` shape, and the `kb_version` string format. After the owner approves the reconciliation, set `knowledge.active_source` to the chosen snapshot; Phase 3's engine and Phase 10's API read recommendations only through `backend/knowledge/lookup.py`.

```text
PHASE 4 STATUS REQUIREMENT:
Do not proceed to the next phase until all acceptance criteria and tests for this phase pass.
```
