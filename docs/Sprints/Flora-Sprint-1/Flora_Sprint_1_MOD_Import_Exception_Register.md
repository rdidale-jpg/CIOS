# Flora Sprint 1 — MOD Import Exception Register

| ID | Stage | Exception | Classification | Impact | Disposition |
| --- | --- | --- | --- | --- | --- |
| MOD-PILOT-001 | Package receipt | Required secure archive `MOD-CDT-v1.2-HSK-Incorporated-Clean-Release.zip` was not available in the task environment. | Operational input/package availability defect | Real MOD workflow could not start; no package integrity, workbook discovery, staging, promotion, Canvas, lineage, feedback or idempotency evidence could be produced. | Remediation required: place the accepted archive in protected local storage outside the repository and rerun the pilot. |
| MOD-PILOT-002 | Preparation | A PR9 completion report was requested but no PR9 completion report file was present under `docs/Sprints/Flora-Sprint-1`. | Documentation/input availability defect | The pilot could not cite a PR9 completion report as an input document. | Remediation required: provide or merge the PR9 completion report, or confirm that the Sprint 1 completion and acceptance report is the intended PR9-equivalent record. |

## Sensitive-content handling

No MOD source content was opened, extracted, logged, copied into the repository, staged, or committed. No local Flora data derived from the MOD package was created.
