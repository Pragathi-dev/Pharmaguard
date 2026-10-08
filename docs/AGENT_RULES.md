# PharmaGuard Agent Rules (apply to every phase)

1. Rules (CPIC-based engine) stay authoritative. ML only adds supporting evidence and never overrides rules.
2. NEVER invent data, metrics, CPIC recommendations, ADR associations, or clinical claims.
   Unrun results are written as <RESULT_TO_BE_GENERATED>.
3. NEVER join datasets at patient level across provenance classes. Every record has a provenance_class.
4. Synthetic or augmented data is allowed in the training split only, never in val/calib/test.
5. Split order: split by relatedness_group -> fit encoders on train only -> degrade -> augment (train only).
6. Do not rewrite working modules. Prefer extending via new modules. State KEEP/MODIFY/REPLACE/ADD.
7. No training at API startup. All training runs via scripts with fixed seeds, logged config, git hash, data hash.
8. Existing tests must keep passing. Run the full suite before and after.
9. No network calls in tests. Use fixtures.
10. UI/API language: "Decision-support evidence", "Exploratory", "Not clinically validated".
11. Windows PowerShell commands only.
12. If something cannot be done validly, STOP and report. Do not work around it.
## Git Rules

Antigravity must NOT automatically commit or push changes to GitHub.

After completing a phase:

1. Implement the requested changes.
2. Run all relevant tests.
3. Report all modified, added, and deleted files.
4. Report test results.
5. Do not run `git commit`.
6. Do not run `git push`.
7. Wait for the developer to review and commit the changes.