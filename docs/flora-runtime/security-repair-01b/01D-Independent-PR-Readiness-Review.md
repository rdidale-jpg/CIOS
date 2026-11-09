# FLORA 01D — Independent PR-Readiness Review

## 1. Executive verdict

**REVIEW BLOCKED. DEPLOYMENT NOT APPROVED.**

Seven new executable required-safe assertions fail across three material defect groups. Existing REMEDIATED evidence is reproducible but incomplete as a service-boundary assurance claim. Production implementation was not changed during this review. All 74 pre-existing relevant files were preserved byte-for-byte. No commit, staging, push, PR operation, merge, deployment, account provisioning or production configuration/data change was performed.

Baseline: `codex/flora-security-repair-01b`, HEAD `83aee1aaf5a49b36d8c5e397d75b99624422fac3`. The review covers accumulated tracked changes and untracked implementation, tests and reports. Earlier reports remain historical evidence, not the current verdict. A machine-readable companion records test identities, observations, signatures, input hashes and dependency metadata.

## 2. Complete changed-file inventory

The accumulated tracked patch is retained in `work/security-repair-01d-pr-review/accumulated-tracked.patch` (32 tracked files). The relevant inventory below includes all modified/untracked source, tests, dependencies and 01B–01D reports: 74 preserved inputs plus this report, its evidence companion and one new adversarial test module (77 files). There are no tracked deletions. Private `work/` contains baseline worktrees, test stores, logs and review scripts; it is not proposed PR content and must not be staged wholesale.

- `cios/applications/flora/access.py`
- `cios/applications/flora/blueprint_import/mapping.py`
- `cios/applications/flora/blueprint_import/planning.py`
- `cios/applications/flora/blueprint_import/promotion.py`
- `cios/applications/flora/blueprint_import/review.py`
- `cios/applications/flora/blueprint_import/review_plan.py`
- `cios/applications/flora/blueprint_import/views.py`
- `cios/applications/flora/commercial_mission.py`
- `cios/applications/flora/document_review.py`
- `cios/applications/flora/enterprise_canvas/access.py`
- `cios/applications/flora/enterprise_canvas/feedback.py`
- `cios/applications/flora/enterprise_canvas/service.py`
- `cios/applications/flora/enterprise_intelligence/runtime.py`
- `cios/applications/flora/live/worker.py`
- `cios/applications/flora/pilot_auth.py`
- `cios/applications/flora/protected_storage.py`
- `cios/applications/flora/security.py`
- `cios/applications/flora/security_operator.py`
- `cios/applications/flora/security_store.py`
- `cios/applications/flora/security_web.py`
- `cios/applications/flora/storage_maintenance.py`
- `cios/applications/flora/web/app.py`
- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Evidence.json`
- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/01D-Independent-PR-Readiness-Evidence.json`
- `docs/flora-runtime/security-repair-01b/01D-Independent-PR-Readiness-Review.md`
- `docs/flora-runtime/security-repair-01b/Adversarial-Remediation-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Adversarial-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/Completion-Report.md`
- `docs/flora-runtime/security-repair-01b/Controlled-PR-Proposal.md`
- `docs/flora-runtime/security-repair-01b/Failure-Root-Cause-Matrix.json`
- `docs/flora-runtime/security-repair-01b/Final-Acceptance-Comparison.json`
- `docs/flora-runtime/security-repair-01b/Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/Independent-Release-Readiness-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Independent-Release-Readiness-Review.md`
- `docs/flora-runtime/security-repair-01b/Inherited-Failure-Register.json`
- `docs/flora-runtime/security-repair-01b/Legacy-Positive-Obligation-Reconciliation.json`
- `docs/flora-runtime/security-repair-01b/Regression-Remediation-Comparison.json`
- `docs/flora-runtime/security-repair-01b/Regression-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/Regression-Remediation-Source-Manifest.json`
- `docs/flora-runtime/security-repair-01b/Release-Readiness-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Release-Readiness-Review.md`
- `docs/flora-runtime/security-repair-01b/Security-Integrity-Remediation-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Security-Integrity-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/Service-Authorisation-Coverage-Matrix.md`
- `docs/flora-runtime/security-repair-01b/Workspace-Blocker-Resolution-Report.md`
- `docs/flora-runtime/security-repair-01b/history/pre-regression-remediation/Final-Acceptance-Comparison.json`
- `docs/flora-runtime/security-repair-01b/history/pre-regression-remediation/Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/history/pre-release-readiness-review/Final-Acceptance-Comparison.json`
- `docs/flora-runtime/security-repair-01b/history/pre-release-readiness-review/Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/history/pre-release-readiness-review/Regression-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/history/pre-security-integrity-remediation/test_flora_security_independent_readiness.py`
- `pyproject.toml`
- `requirements.txt`
- `tests/flora_security_fixtures.py`
- `tests/test_enterprise_intelligence_reasoning.py`
- `tests/test_flora_blueprint_import_promotion.py`
- `tests/test_flora_blueprint_import_review_planning.py`
- `tests/test_flora_blueprint_import_validation.py`
- `tests/test_flora_enterprise_canvas.py`
- `tests/test_flora_experience_assurance_repair.py`
- `tests/test_flora_factory_evidence_release_repair.py`
- `tests/test_flora_factory_presentation_repair.py`
- `tests/test_flora_factory_researcher_model_repair.py`
- `tests/test_flora_import_model_reconciliation.py`
- `tests/test_flora_intelligence_integrity.py`
- `tests/test_flora_security_01d_final_acceptance.py`
- `tests/test_flora_security_01d_pr_review.py`
- `tests/test_flora_security_admin_policy.py`
- `tests/test_flora_security_adversarial_remediation.py`
- `tests/test_flora_security_independent_readiness.py`
- `tests/test_flora_security_integrity_repair.py`
- `tests/test_flora_security_legacy_obligations.py`
- `tests/test_flora_security_owner_journey.py`
- `tests/test_flora_security_release_review.py`
- `tests/test_flora_security_repair_01b.py`
- `tests/test_flora_security_workspace_boundary.py`

## 3. Security architecture and complete-diff review

The accumulated implementation uses server-issued verified identity, persisted membership and capability evaluation rather than browser-created authority. Session validity/revocation, CSRF, public-route classification, strict persisted resource scope, ACL intersection and administrator promotion policy were inspected alongside their call sites. No new header/cookie/environment shortcut granting production privilege was found. Financial guarded reads, Canvas feedback, commercial profile updates and recent-auth cleanup have protected-write entry points and supporting negative/positive evidence. Public Banking classification and protected route boundaries retain their earlier tests. These conclusions are bounded by the concrete defects below and are not a claim that every route or service is proved secure.

The central write envelope coordinates canonical SQLite authority, revalidation, filesystem undo and audit. Participating writers serialize; direct destructive lifecycle deletion does not participate. An HTTP mutation envelope therefore cannot establish direct-service safety. Financial run scope does not bind the downstream canonical destination. Recovery validates declared backups but does not establish manifest completeness before deleting undeclared files.

The full accumulated diff includes authentication/session/operator modules, web integration, access/resource helpers, financial/Blueprint/Canvas/profile/cleanup services, dependency additions and domain test fixture changes. The verified security fixture is explicitly isolated from real-boundary tests; supplemental tests use it explicitly. No broad cleanup or refactoring was performed. No accidental production credential was found by the scoped high-confidence scan; synthetic credentials are intentional test inputs. This scan does not certify absence of every sensitive identifier, and scratch artifacts are excluded from publication.

Untested residual coverage: direct Blueprint upload/restage/identity/lifecycle operations need a bounded boundary audit during remediation. Upload intentionally retains validation outcomes; it must not be assigned deletion semantics without domain review. Raw repository primitives are trusted internals, not automatically exposed endpoints. Production multi-instance/filesystem qualification remains absent.

## 4. New adversarial findings

All seven cases in `tests/test_flora_security_01d_pr_review.py` ran against real verified-authority producers and isolated synthetic stores: **7 failed in 2.67 seconds**, no setup errors, skips or expected failures. Logs/JUnit: `work/security-repair-01d-pr-review/verified-probes.*`; per-case observations are indexed in the companion. Fault hooks alter interleavings or injected storage failures, not authorization outcomes.

### P1 — Financial canonical target is not bound to authorized run

`access.require_financial_run_authority` validates run/document scope and optional claim `enterprise_id`, but `document_review.claim_to_evidence` uses `canonical_enterprise_id`. `apply_accepted` then invokes the real canonical processing service. A claim with the allowed alias and a conflicting canonical destination passed the run check, wrote Evidence for another Enterprise and changed that Enterprise's model. Its authoritative workspace and Canvas ACL denied the actor. Protected storage changed. This is a verified-human cross-Enterprise/workspace write; no anonymous exploit is claimed.

Required correction: bind every destination identifier used by canonicalisation to authoritative run/resource scope before any write, reject conflicting aliases, and retain downstream ACL/workspace/capability enforcement inside the existing transaction/evaluator. Cover actual Evidence and Enterprise Model destinations.

### P1 — Candidate deletion lacks complete direct-service protection

`TwinImportLifecycleService.delete_candidate` in `blueprint_import/lifecycle.py` checks capability and optional package workspace, then takes one preview and directly deletes protected files before appending its domain ledger. It lacks the protected-write envelope, mandatory resource ACL intersection, strict missing-scope rejection, authority revalidation and atomic audit/undo. `views.delete_candidate_import` does not repair the direct call boundary.

Five independent cases demonstrate: an explicitly denied resource ACL still permits deletion; empty persisted package workspace still permits deletion; independently committed membership/session revocation after preview still permits deletion; mandatory deletion-ledger failure returns an error after deleting package/staging; and a real successful canonical promotion between preview and delete loses its source archive and package registry. The promotion executed one actual canonical mutation; this is not a fabricated status. HTTP wrappers do not protect direct service callers.

Required correction: integrate this destructive service with the existing authority transaction and journal, strict authoritative resource scope and ACL checks, and serialized governance revalidation. Audit failure must preserve protected data. A committed promotion must make deletion unavailable. Although the lifecycle file itself is unchanged from baseline, its direct service is reachable using the new production authority path; unchanged source is not evidence of a safe integration.

### P1 — Valid-JSON manifest omission causes destructive recovery

`ProtectedJournal.restore` trusts the manifest file list as complete. Local fault injection removed one original-file entry from published `manifest.json` while leaving its actual backup present and every remaining declared hash valid. Transaction failure triggered undo, which deleted the original file as supposedly new, verified against the same incomplete list, and discarded the journal/backup. Authority remained usable. Before/after store hashes differ.

This is corruption of a private recovery artifact, not evidence that a browser can edit it. It is nevertheless silent destructive recovery in the claimed corruption-handling boundary. Validate a bound, complete manifest/backup inventory before destructive restore; preserve journal evidence and fail closed on discrepancies. Do not simply tolerate the missing entry.

Exact new failed IDs:

- `tests/test_flora_security_01d_pr_review.py::test_candidate_delete_intersects_persisted_scope_and_existing_acl[denied-resource-acl]`
- `tests/test_flora_security_01d_pr_review.py::test_candidate_delete_intersects_persisted_scope_and_existing_acl[missing-persisted-workspace]`
- `tests/test_flora_security_01d_pr_review.py::test_direct_candidate_deletion_cannot_continue_after_committed_revocation`
- `tests/test_flora_security_01d_pr_review.py::test_candidate_deletion_audit_failure_preserves_protected_data`
- `tests/test_flora_security_01d_pr_review.py::test_valid_json_manifest_omission_cannot_silently_delete_snapshot_data`
- `tests/test_flora_security_01d_pr_review.py::test_completed_promotion_cannot_be_deleted_using_stale_candidate_preview`
- `tests/test_flora_security_01d_pr_review.py::test_financial_apply_validates_actual_canonical_enterprise_target`

## 5. Acceptance evidence reconciliation

Retained raw JUnit, SHA256 maps, SQLite audit records/chains and mapping identities were independently reparsed. Existing production/test hashes exactly match the acceptance manifest, so broad suites were not redundantly rerun. The seven new probes were executed freshly. Cached results remain valid for their original coverage, but the expanded security gate is red.

| Gate | Independently verified result |
| --- | --- |
| Existing security | 349 + 9 = 358 passed |
| Previous seven adversarial cases | All 7 passed, included in 349 |
| New independent adversarial cases | 7 failed |
| Store integrity comparisons | 52 + 9 + 62 + 5 = 128 unchanged |
| Committed audit record digests | 17 matching |
| Audit chains | 15 valid stores |
| Complete domain | 404 passed, 22 failed, 10 skipped |
| Factory | 88 passed, 8 skipped |
| Experience | 56 passed, 2 skipped |
| Governance | 157 passed |
| Supplemental explicit-authority fixture | 39 passed |
| Legacy positive mappings | 19/19 references resolve to passing tests |
| Historical legacy suite | 3 passed, 24 failed, separately reported |

Existing active identities are disjoint: 860 = 804 passed + 46 failed + 10 skipped. Including the seven new cases gives **867 = 804 passed + 53 failed + 10 skipped**. The 46 prior failures are 22 domain and 24 historical legacy contracts. Baseline reproductions and the archived diagnostic are separate executions, not extra active coverage. No existing tests were weakened, skipped or removed. The 19 positive mappings remain satisfied for their enumerated behaviors; they cannot establish broader canonical destination or destructive lifecycle safety now contradicted by new evidence.

All ten unchanged skips require unavailable retained TEL-W6/BNK-W1 artifacts. These are legitimate explicit input gaps, not security-test exclusions, and do not prove retained-package acceptance:

- `tests/test_flora_factory_evidence_release_repair.py::test_retained_tel_w5_w6_reconciliation_and_replay`: Actual retained W6 package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1
- `tests/test_flora_factory_evidence_release_repair.py::test_retained_bnk_same_citation_contract`: Actual retained BNK package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1
- `tests/test_flora_factory_evidence_release_repair.py::test_retained_tel_count_reconciliation_independent_of_citation_assertions`: Actual retained W6 package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1
- `tests/test_flora_factory_presentation_repair.py::test_actual_retained_user_journey_and_honest_promotion[TEL-W6]`: Actual retained artifact not available: TEL-W6
- `tests/test_flora_factory_presentation_repair.py::test_actual_retained_user_journey_and_honest_promotion[BNK-W1]`: Actual retained artifact not available: BNK-W1
- `tests/test_flora_factory_researcher_model_repair.py::test_actual_retained_source_to_memory_retrieval_and_view[TEL-W6]`: Retained artifact unavailable: TEL-W6
- `tests/test_flora_factory_researcher_model_repair.py::test_actual_retained_source_to_memory_retrieval_and_view[BNK-W1]`: Retained artifact unavailable: BNK-W1
- `tests/test_flora_factory_researcher_model_repair.py::test_actual_tel_w5_w6_handoff_reuses_observation_and_confidence_history`: Retained artifact unavailable: TEL-W6
- `tests/test_flora_experience_discovery_repair.py::test_actual_retained_packages_use_generic_discovery_and_keep_factory_boundaries[TEL-W6]`: Actual retained artifact unavailable: TEL-W6
- `tests/test_flora_experience_discovery_repair.py::test_actual_retained_packages_use_generic_discovery_and_keep_factory_boundaries[BNK-W1]`: Actual retained artifact unavailable: BNK-W1

## 6. Archived concurrency harness assessment

The original file remains preserved with SHA256 `81c1bf20de29891e2df0c01e8146c6638a85f7cb9346c81cc7bfc51798169720`. AST comparison confirms only `test_undo_cannot_erase_concurrently_accepted_direct_feedback` changed and the substantive accepted-feedback survival assertion remains unchanged. The archived diagnostic fails because it awaits feedback while retaining the authority writer lock, so the accepted result is not captured; its observation still records one surviving feedback record and valid authority. It remains reported separately.

The corrected active case passes. Additional native SQLite evidence records SQLITE_BUSY, a real feedback BEGIN attempt before rollback, no completion while the writer lock is held, and successful feedback/audit persistence after rollback. This supports the approved orchestration correction rather than masking lost accepted feedback. It does not cover the nonparticipating deletion or manifest defect identified here.

## 7. Inherited failure risk register

All **22 confirmed, 0 unverified**: retained baseline JUnit from the isolated clean HEAD worktree has identical IDs and normalized first-failure signatures to current domain JUnit. Baseline was not reset or altered. The companion preserves both signatures per ID. Historical status equality does not waive impact or prove assertions after the first failure. No direct authorization exploit is established solely by these first assertions. Product and governance contract gaps remain deployment holds until resolved or explicitly accepted by responsible reviewers.

| Exact test ID | Baseline/current first failing expression | Impact / release classification |
| --- | --- | --- |
| `tests/test_flora_banking_increment44_executive_navigation.py::test_account_default_opportunities_breadcrumbs_and_evidence_drilldown` | `assert "data-default-opportunities='3'" in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_increment44_executive_navigation.py::test_ai_native_reference_model_collapsed_and_separate` | `assert "Explore capability model" in top` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_increment44_executive_navigation.py::test_landing_budget_conclusion_and_signals` | `assert html.index("UK banks are moving") < html.index("Three industry signals")` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_increment44_executive_navigation.py::test_pestle_only_outlook_not_landing_or_portfolio` | `assert "UK Banking PESTLE view" in industry_outlook_page()` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_increment451_visual_correction.py::test_featured_subset_has_full_exploration_route_and_counts_match_projection` | `assert "Featured intelligence" in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_increment45_visual_intelligence.py::test_ai_native_maturity_journey_renders_as_visual_progression` | `assert "AI-native maturity rail" in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_financial_behaviour_narrative_has_required_causal_sections` | `assert "What the financial results imply about behaviour" in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace` | `assert term in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_industry_opportunity_totals_reconcile_to_account_opportunities` | `assert f"Flora working estimate £{portfolio_mid}m" in html or f"Flora working estimate: £{portfolio_mid}m" in html` | Computed totals agree before failure; rendered estimate label differs. Presentation/qualification acceptance unresolved. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_pestle_forces_map_to_specific_banks_themes_and_non_generic_outputs` | `assert category in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_rendered_acceptance_artefacts_exist` | `assert artefact in industry` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_industry_reinvention_increment42.py::test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist` | `assert "Google Cloud" in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_analyst_views_preserve_attribution_without_fake_consensus` | `assert "What analysts broadly like" in html` | Analyst-section/attribution acceptance is unresolved; later provenance assertions do not execute after the first heading failure. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_each_bank_page_uses_executive_structure_and_preserves_inspection` | `assert section in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_pipeline_reconciliation_horizons_and_value_meaning` | `assert "What the financial results are telling us" in html` | Pipeline display/qualification contract unresolved; initial arithmetic preconditions pass, later rendered qualification assertions are not reached. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion` | `assert text in html` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded` | `assert "No reliable view" in html` | Supplier metadata preconditions pass; displayed unknown/fallback wording differs. Needs semantic/product contract reconciliation. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_opportunities_have_values_feedback_and_preserve_originals` | `assert action in html` | Feedback controls absent under legacy expectations; do not restore anonymous mutations just to satisfy an old UI assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_banking_portfolio_increment3.py::test_theme_relevance_ranking_and_pipeline_are_deterministic` | `assert theme in first` | Presentation/navigation or rendered-content contract differs; no authorization bypass is established by this first assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs` | `assert "href='/digital-twins/MOD'>Open Twin" in home` | Old direct Open Twin link differs from current Canvas navigation; existing authorized import setup reaches the navigation assertion. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route` | `assert "/blueprint-import/history" in html` | Anonymous home does not contain the expected import-history link; source-data privacy and anonymous write closure must be preserved when reconciling navigation. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |
| `tests/test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model` | `assert "executive situation briefing" in html` | Authenticated Canvas renders 200 but the old briefing heading is absent; later authority/lineage/read-only assertions in this case are not reached. Product-release acceptance hold pending reviewed contract reconciliation or explicit waiver; not waived because inherited. |

The historical legacy suite is accounted separately: 24 failures include 19 retired insecure expectations plus the five pre-existing failures below. Original and current totals are both 3 passed/24 failed, with two previously documented missing-configuration wording cases exchanging pass/fail status; these are not new 01D regressions. Exact signatures and swaps are in the companion. No claim is made that unchanged counts alone prove identical tests.

- `tests/test_flora_pilot_auth.py::test_cios_owner_can_upload_inspect_and_stage_mod_package_without_canonical_mutation` — failed at original baseline and current head.
- `tests/test_flora_pilot_auth.py::test_owner_managed_enterprise_policy_is_case_normalised_and_workspace_bound` — failed at original baseline and current head.
- `tests/test_flora_pilot_import_bypass.py::test_configured_module_complete_http_commercial_context_and_twin_map` — failed at original baseline and current head.
- `tests/test_flora_pilot_import_bypass.py::test_deployed_equivalent_pilot_route_imports_candidate_to_executive_workspace` — failed at original baseline and current head.
- `tests/test_flora_pilot_import_bypass.py::test_pilot_configure_save_and_recompose_uses_narrow_actor_scope` — failed at original baseline and current head.

## 8. Dependency assessment: draft PR #539

Fresh read-only GitHub inspection: #539 is open, draft and unmerged, head `83aee1aaf5a49b36d8c5e397d75b99624422fac3` on `codex/flora-security-repair-01a`, base `main` at `dc9203e6880f8722e821d39cf53b689732edb0e7`. The current work is exactly based on that pinned dependency. A stacked peer review can be technically independent without first merging or changing #539; the dependency and excluded baseline diff must be explicit. Changes to #539 or main require renewed compatibility/diff checks. Merging #539 would not repair the new 01B–01D findings. No remote PR modification occurred.

## 9. Residual operational risks

Deployment is not approved. Actual production mount semantics, fsync/rename durability, SQLite locks, process/instance topology and all external writers remain unqualified. The intended small persistent disk (including a 1 GB configuration assumption) is not measured available snapshot capacity: root snapshots, copies, simultaneous artifacts and ENOSPC recovery require sizing and load tests. A canonical writer lock can cause latency/timeouts under real workload; local serialization tests do not establish throughput or fairness. Multiple instances, split mounts or nonparticipating scripts can invalidate local journal assumptions; the deletion finding is an in-application nonparticipant, not an external-writer waiver.

Production backup restoration, off-host retention, disaster recovery, power loss/device failure and recovery of incomplete artifacts require separate rehearsals. The demonstrated manifest corruption defect is an implementation blocker, not merely an operational caveat. Migration must inventory authoritative workspace/ACL metadata and fail closed on missing/conflicting scope without fabricating ownership. Rollback must coordinate authority schema, audit and protected data; no production migration/rollback or identity provisioning was exercised. The 22 inherited failures and ten retained-artifact gaps remain visible product qualification limits. No deployment suitability is inferred from local acceptance.

## 10. Exact Git status

The index remains empty; branch and HEAD are unchanged. Status below includes pre-existing private `work/` artifacts. All additions from this review are uncommitted. The report and evidence are grouped under the existing untracked documentation directory.

```
 M cios/applications/flora/access.py
 M cios/applications/flora/blueprint_import/mapping.py
 M cios/applications/flora/blueprint_import/planning.py
 M cios/applications/flora/blueprint_import/promotion.py
 M cios/applications/flora/blueprint_import/review.py
 M cios/applications/flora/blueprint_import/review_plan.py
 M cios/applications/flora/blueprint_import/views.py
 M cios/applications/flora/commercial_mission.py
 M cios/applications/flora/document_review.py
 M cios/applications/flora/enterprise_canvas/access.py
 M cios/applications/flora/enterprise_canvas/feedback.py
 M cios/applications/flora/enterprise_canvas/service.py
 M cios/applications/flora/enterprise_intelligence/runtime.py
 M cios/applications/flora/live/worker.py
 M cios/applications/flora/pilot_auth.py
 M cios/applications/flora/security.py
 M cios/applications/flora/storage_maintenance.py
 M cios/applications/flora/web/app.py
 M pyproject.toml
 M requirements.txt
 M tests/flora_security_fixtures.py
 M tests/test_enterprise_intelligence_reasoning.py
 M tests/test_flora_blueprint_import_promotion.py
 M tests/test_flora_blueprint_import_review_planning.py
 M tests/test_flora_blueprint_import_validation.py
 M tests/test_flora_enterprise_canvas.py
 M tests/test_flora_experience_assurance_repair.py
 M tests/test_flora_factory_evidence_release_repair.py
 M tests/test_flora_factory_presentation_repair.py
 M tests/test_flora_factory_researcher_model_repair.py
 M tests/test_flora_import_model_reconciliation.py
 M tests/test_flora_intelligence_integrity.py
?? cios/applications/flora/protected_storage.py
?? cios/applications/flora/security_operator.py
?? cios/applications/flora/security_store.py
?? cios/applications/flora/security_web.py
?? docs/flora-runtime/security-repair-01b/
?? tests/test_flora_security_01d_final_acceptance.py
?? tests/test_flora_security_01d_pr_review.py
?? tests/test_flora_security_admin_policy.py
?? tests/test_flora_security_adversarial_remediation.py
?? tests/test_flora_security_independent_readiness.py
?? tests/test_flora_security_integrity_repair.py
?? tests/test_flora_security_legacy_obligations.py
?? tests/test_flora_security_owner_journey.py
?? tests/test_flora_security_release_review.py
?? tests/test_flora_security_repair_01b.py
?? tests/test_flora_security_workspace_boundary.py
?? work/
```

## 11. Recommended next controlled action

Keep this review blocked and all work uncommitted. Undertake a bounded remediation of canonical financial destination binding, candidate deletion's existing evaluator/ACL/transaction/governance/audit boundary, and complete recovery-manifest validation. Preserve these seven required-safe assertions; make them pass without permissive fixtures or exclusions. Inspect adjacent demonstrated-equivalent direct service entry points, then rerun the affected acceptance/security suites and meaningful domain regressions, rechecking exact identities and before/after storage integrity. Obtain a renewed independent readiness verdict before any separately authorized commit or publication. Production qualification is a separate gate even after code review blockers are resolved.
