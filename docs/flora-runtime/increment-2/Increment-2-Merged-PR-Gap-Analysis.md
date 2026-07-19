# Increment 2 Merged PR Gap Analysis

| ID | Requirement | Status | Evidence | Gap | Required action |
|---|---|---|---|---|---|
| I2-01-001..004 | Preserve baselines and historical evidence. | Implemented | Runtime constant and tests retain `e7dca8e`; original dataset path unchanged. | None. | None. |
| I2-02-001..003 | Bounded Lloyds Explain DoD. | Complete after reconciliation | Existing Explain runtime and tests; reconciliation added validation/repeatability tests. | Original merge lacked deterministic validators and source-passage package fields. | Added validators and package metadata. |
| I2-03-001..005 | Context Package specification. | Complete after reconciliation | `ContextPackage` now contains focus/question IDs, source passages, policy/baseline fields, exclusions, limitations and hash. | Merged package omitted substantive passages and several metadata fields. | Added fields while preserving existing contract names. |
| I2-04-001..002 | JSON/schema validation. | Implemented differently | Pydantic frozen models with `extra='forbid'`; no standalone JSON Schema file. | Implemented as model validation, not separate schema artefact. | Accepted as equivalent for current Python runtime; future schema export condition noted. |
| I2-05-001..003 | Semantic validation. | Complete after reconciliation | `validate_context_package` checks lineage, source passages, Unknowns and tensions. | No deterministic semantic package validator in merge. | Added validator and tests. |
| I2-06-001..002 | Deterministic Question Validator. | Partially implemented | Fixed question constant and package question ID. | No public unsupported-question API exists in Increment 2 slice. | Condition for later route/API hardening; no broadening now. |
| I2-07-001..002 | Deterministic Context Planner. | Implemented differently | Builder deterministically selects fixed corpus for fixed Lloyds question. | Planner is implicit in builder, not separate class. | No further action; separate planner would broaden code. |
| I2-08-001..003 | Governed retrieval. | Complete after reconciliation | Builder reads only Lloyds evaluation dataset and records authority/access/exclusion fields. | Exclusion reasons and freshness/access fields were missing. | Added metadata and exclusions. |
| I2-09-001..003 | Context Package Builder. | Implemented | `assemble_lloyds_context_package`; no canonical writes. | None. | None. |
| I2-10-001..002 | Immutability. | Implemented | Frozen Pydantic models; hash tests and repeatability test. | None. | None. |
| I2-11-001..003 | Bounded worker package-only reasoning. | Implemented | `explain_lloyds_changes(package)` uses package parameter and hard-coded bounded transformation. | No external model invocation; acceptable bounded deterministic worker. | None. |
| I2-12-001..003 | Claim classification. | Partially implemented | `ChangeAssessment` separates fact basis, interpretation, evidence IDs, observation IDs, limits and confidence. | No explicit enum field per claim category. | Accepted with condition; current structure provides equivalent separation. |
| I2-13-001..003 | Strategic coherence boundary. | Implemented | Scope and prohibited output fields exclude recommendations, scores and broad strategy. | None. | None. |
| I2-14-001..004 | Output Validator. | Complete after reconciliation | `validate_bounded_explanation` rejects unknown IDs and prohibited language; tests cover rejection. | Original merge had no deterministic output validator. | Added validator and tests; safe-unavailable rendering remains future route condition. |
| I2-15-001..004 | User experience. | Partially implemented | Increment 1 Lloyds route exists; no unrestricted chat in this slice. | No rendered Increment 2 Explain workspace surface. | Condition: add UI route before user acceptance; not added to avoid broadening. |
| I2-16-001..003 | Runtime audit. | Partially implemented | Pipeline emits JSON output with package ID/hash; general pipeline has telemetry/audit. | Increment 2 explain audit event lacks all required fields. | Condition: add non-canonical audit record before production. |
| I2-17-001..002 | Repeatability. | Complete after reconciliation | Test runs three executions over one frozen package and compares semantic structures. | Original merge lacked explicit repeatability test. | Added test. |
| I2-18-001..003 | Validation fixtures. | Material gap | Dataset covers several cases but no fixture matrix defines all required outcomes. | Many required negative fixtures missing. | Remaining condition; do not fabricate broad fixture suite in reconciliation. |
| I2-19-001..002 | Semantic evaluation replay. | Material gap | Existing readiness evaluation predates merge. | No separately versioned Increment 2 replay artefact found. | Remaining condition. |
| I2-20-001 | Two-reviewer acceptance. | Material gap | Existing readiness decision notes missing two-reviewer scores. | No merged two-reviewer scorecards found. | Remaining condition. |
| I2-21-001..002 | Architecture constraints. | Implemented | Runtime follows fixed package-to-explain path; no direct canonical query inside worker. | None material after package-field reconciliation. | None. |
| I2-22-001 | Prohibited capabilities. | Implemented for Explain slice | Tests and code prohibit recommendations/scoring; no canonical write in Explain. | Wider repo has older strategic-sales prototype with recommendation eligibility terminology outside Increment 2 Explain. | Keep out of Increment 2 acceptance scope. |
| I2-23-001..002 | Required deliverables. | Complete after reconciliation | Checklist, gap analysis, report created. | Missing before reconciliation. | Created. |
| I2-24-001..002 | Testing. | Partially implemented | Pytest checks run; prohibited scan run. | Not all requested suites exist or were feasible in current repo. | Record limitations. |
| I2-25-001 | Acceptance criteria. | Accepted with conditions | Core runtime after reconciliation passes, but UX/audit/fixtures/replay/reviewer artefacts incomplete. | Conditions remain. | Formal decision below. |
| I2-26-001 | Completion decision. | Implemented | Reconciliation report uses exact decision. | None. | None. |
| I2-27-001 | Completion report. | Implemented | Reconciliation report. | None. | None. |

Decision: **Increment 2 accepted with conditions**.
