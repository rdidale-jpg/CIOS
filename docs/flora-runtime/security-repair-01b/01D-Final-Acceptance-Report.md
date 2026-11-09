# FLORA 01D — final security acceptance and regression validation

## 1. Executive acceptance verdict

**REMEDIATED.** All mandatory active security and integrity assertions pass, and the named regression sets introduce no new failure, skip or status change relative to the established 01D baseline. This permits progression to **independent PR-readiness review only**. It does not authorise a commit, PR, release or deployment.

Fresh acceptance evidence comprises **358 passing security cases**: 261 previously accepted cases, seven independent-review adversarial cases, 81 remediation additions and nine new final-acceptance probes. All **61 originally required integrity comparisons** remain unchanged; 62 remediation and five final-acceptance comparisons also match, for **128 complete-store comparisons**. Seventeen committed feedback/profile audit digests match stored records, 15 selected healthy audit chains are internally consistent, and the HTTP cleanup deletion matches its resource audit.

The complete active selection contains **860 unique identities: 804 passed, 46 failed, ten skipped**. The 46 failures are the same 22 inherited domain failures and 24 historical legacy failures. The repository is not wholly green. The archived, superseded concurrency orchestration was also deliberately executed as a separate historical diagnostic and fails; that result is explicitly accounted for below, not hidden in green totals.

No production implementation or pre-existing code/test/report file was changed during this acceptance task. All 71 pre-task relevant files retain their hashes. New files are one nine-case verification module, this report and its machine-readable companion. Branch/HEAD and index remain unchanged.

## 2. Six-defect verification matrix

| Defect | Implementation behaviour independently checked | Fresh evidence / acceptance |
| --- | --- | --- |
| Feedback reads | Guarded retrieval uses current verified membership/effective read capability, persisted feedback workspace, current Canvas workspace and applicable ACL. Missing/conflicting scope stays closed; standard/restricted capability distinctions are retained. | Original wrong-workspace and ACL-disclosure cases pass. The 81-case remediation selection also passes scope/revocation/read-capability/visibility cases. No unauthorised record is returned by those denied services. |
| Feedback writes | Shared consequential-write envelope re-evaluates authority after acquiring the writer boundary and through append/commit. Repository append requires the server-only authorised service context and current resource checks. | Original revocation-at-append case passes. Pre-entry stale-context, pre/post-append revocation and current-denial matrices pass with unchanged stores. External committed revocation orders after an already executing writer and prevents subsequent writes. |
| Concurrent rollback | One canonical authority SQLite transaction coordinates participating writers and root recovery. Pending recovery precedes a contender's authority resolution/new snapshot. | Corrected original test passes; an additional probe observes real `SQLITE_BUSY` and the feedback request's native `BEGIN IMMEDIATE` before rollback. Accepted feedback survives. Previously accepted feedback also survives an unrelated failed profile commit. Four simultaneous feedback requests retain four records/audits; two actor edits preserve both keys in the shared profile file. |
| Recovery collisions | Recovery uses exclusive private journal temporaries, verifies copies and exact restored inventory/modes, and retains undo on failure. | Original recovery-looking filename is preserved. Existing repeated-rollback, interrupted/corrupt restoration, retained-evidence, retry, reservation-admission and process-interruption cases all pass in the 349-case run. No recovery success is accepted after a failed verification. |
| Cleanup | Direct destructive cleanup and HTTP recovery require current authority, recovery capability, selected resource workspace/ACL constraints and recent authentication. Confirmation/CSRF/origin controls remain in the HTTP path. | Original direct stale-authentication check and remediation cleanup matrix pass. Four new HTTP denials—stale authentication, missing grant, revoked membership and wrong workspace—return 403 and preserve every protected file. A recent, scoped HTTP request deletes exactly one eligible history version, retains two and commits the matching audit. |
| Commercial profiles | Each write requires effective edit authority, current membership, actor ownership and persisted selected workspace; unsupported roots and conflicting payload/record scope deny. Shared transaction/journal and read-after-write verification are present. | Original missing-edit-capability case and all remediation mutation/fault cases pass. Concurrent real actors retain both owned records in the same JSON file with matching audits. The previously added reader/writer case rejects uncommitted-value disclosure; no implicit view capability is granted to edit-only actors. |

These findings are based on code/call-path inspection, actual local HTTP and service execution, real opaque sessions from the producer, SQLite contention and persisted/audit comparisons. They are not inferred merely from test names. The scoped application implementation matches the prior remediation source manifest exactly.

## 3. All seven original adversarial outcomes

The active module remains `tests/test_flora_security_independent_readiness.py`; it was not edited during this acceptance task.

| Exact function / parameters | Fresh result |
| --- | --- |
| `test_feedback_read_enforces_current_resource_scope_and_acl[wrong-workspace]` | Passed |
| `test_feedback_read_enforces_current_resource_scope_and_acl[denied-acl]` | Passed |
| `test_direct_feedback_mutation_cannot_write_after_revocation` | Passed |
| `test_undo_cannot_erase_concurrently_accepted_direct_feedback` | Passed with the previously authorised orchestration correction |
| `test_recovery_preserves_existing_names_matching_temporary_pattern` | Passed |
| `test_direct_storage_cleanup_requires_recent_authentication` | Passed |
| `test_commercial_profile_write_requires_effective_edit_capability` | Passed |

No additional alteration to those seven bodies, authority fixtures or security assertions was made. None is skipped or xfailed.

## 4. Original versus corrected concurrency-test evidence

### Preservation and scope of authorisation

User authorisation from the remediation task was: **“Allow the interleaving correction; preserve the original file as historical evidence.”**

The original file remains at:
`history/pre-security-integrity-remediation/test_flora_security_independent_readiness.py`

Its independently checked SHA-256 is:
`81c1bf20de29891e2df0c01e8146c6638a85f7cb9346c81cc7bfc51798169720`.

AST comparison confirms that only the authorised concurrency function differs between the archive and active module. Every other function is unchanged. The original substantive assertion—an independently accepted feedback result must still exist after rollback—is literally retained in the active function's AST.

### Separate execution results

| Execution | Observed result | Interpretation |
| --- | --- | --- |
| Archived original orchestration, explicitly selected against the current implementation | **One failed**; `accepted is None`; one feedback record survives and authority remains valid | Feedback pauses while holding the writer boundary. The other thread tries to acquire the writer lock and cannot reach the point that captures the accepted result. After its lock failure/finally path releases feedback, the worker completes, but the harness never assigns `accepted`. The terminal assertion therefore fails on result bookkeeping, not demonstrated loss of the surviving feedback. |
| Corrected active orchestration | **One passed**, included in the seven-case gate | It starts the feedback request while the failing writer holds the lock, checks that it has not completed, rolls back/releases the writer boundary, then awaits the feedback result outside that boundary and verifies survival. |
| Added native-contention acceptance probe | **One passed** | A second connection receives real `SQLITE_BUSY` from the same database while the first writer owns the lock. The actual feedback request emits native `BEGIN IMMEDIATE` before rollback and remains unfinished while the first lock is held. It subsequently commits a surviving record with a matching audit. |

The additional probe records this ordering:

`failing writer owns lock → native SQLITE_BUSY → actual feedback BEGIN observed → rollback requested → rollback complete → feedback commit`.

The requests genuinely overlap; the production lock serializes their protected effects. The test does not launch feedback only after rollback, mock the authorization outcome, or wait for completion while retaining the required writer lock.

The original archive's one failure remains an ordinary failed diagnostic execution in `original-harness.xml`/`.log`. It is not changed to xfail/skip, suppressed, or counted as a passing active test. The six other archived copies are not separately executed: their AST-identical active counterparts already run, and the archive is preserved historical source rather than additional acceptance coverage.

## 5. Audit/integrity obligation assessment

The broader obligation was reopened and checked directly. The nineteen mapped legacy positives are supporting evidence, not the sole basis for acceptance.

| Obligation | Direct evidence |
| --- | --- |
| Protected data and mandatory audit agree | Fresh SQL/file comparisons reconcile **17 feedback/profile content digests** to committed records with resource identity and verified workspace/member/session references. **15 selected healthy audit chains** have correct predecessor/hash links. This establishes internal consistency, not external attestation against a compromised filesystem administrator. |
| Failed mandatory commit leaves no unaudited committed mutation | The prior 61 plus 62 remediation comparisons are rerun and equal. A new failed profile commit leaves already accepted feedback and the complete store unchanged. Existing partial/audit/final-commit fault cases cover feedback, paired profiles, cleanup, financial review and actual promotion. |
| Rollback preserves independent committed data | Native-contention/waiting feedback commits after recovery and survives; previously accepted feedback survives an unrelated failed commit. A separate four-request feedback test retains four distinct records and four matching audits. |
| No lost independent records/actor keys | Four concurrent feedback appends and two real, independently approved **synthetic** actors writing different keys in the same profile file retain every accepted record/key and corresponding audit. This verifies serialization of the storage operations; it does not add optimistic merge/conflict handling for clients intentionally replacing the same profile object. |
| Recovery failure cannot silently destroy state | Collision, repeat-rollback and interrupted/corrupt restoration cases pass; failed verification retains the journal and closes authority until successful retry. Native file/hash/mode checks and process-exit tests exercise the actual local protocol. |
| Cleanup permissions apply through HTTP and direct service calls | Direct stale-authentication check passes. HTTP stale-authentication test first confirms a live session with the recovery grant and authentication older than `RECENT`, then observes denial and complete-store equality. Other permission/scope denials and positive deletion/audit matching pass. |

**Assessment:** supported for the actual tested local architecture: one canonical authority database, protected root, participating writer protocol, real local SQLite and filesystem, and current guarded service entry points. No material active security/integrity assertion fails in that model. No production equivalence, distributed guarantee, arbitrary raw filesystem-writer safety, physical power-loss qualification or deployment acceptance is inferred.

There are **128 complete-store hash comparisons**: original 52 + nine 01C + 62 01D + five final-acceptance comparisons. The five new comparisons cover an unrelated failed profile commit and all four denied HTTP cleanup mutations. No file or SQLite store is excluded. Concurrency checks separately account for the independent successful writes that are supposed to remain; they do not incorrectly require the entire root to be unchanged when another transaction legitimately commits.

## 6. Complete security and regression results

| Gate | Fresh result | Exact-ID comparison |
| --- | --- | --- |
| Previously accepted security | **261 passed** | Same set; zero regressions |
| Original active adversarial checks | **Seven passed** | Same identities; only previously approved orchestration difference from archived original |
| 01D remediation additions | **81 passed** | Same remediation set |
| New final-acceptance probes | **Nine passed** | New module, separately identified |
| Total selected security | **358 passed**, zero failed/skipped | 349 prior + nine new |
| Originally required integrity | **61 unchanged** | Fresh 52 + nine artifacts |
| 01D / final additional integrity | **62 + five unchanged** | Total 128 comparisons |
| Factory | **88 passed, eight original skips** | Same IDs/statuses |
| Experience | **56 passed, two original skips** | Same IDs/statuses |
| Defined Governance | **157 passed** | Same IDs/statuses |
| Complete domain | **404 passed, 22 failed, ten skipped** | Same 436 IDs/statuses; no new failure |
| Supplemental units | **39 passed** | Same IDs, established explicit unit-authority fixture |
| Legacy positive mappings | **19/19 referenced evidence passes** | Broader obligation separately checked above |
| Historical legacy | **Three passed, 24 failed** | All 27 statuses unchanged from the 01D baseline; five pre-existing failure identities separately retained |

The active disjoint total is **860 test identities = 804 passed + 46 failed + ten skipped**. The 358 security cases, 436 domain cases, 39 supplemental cases and 27 historical cases do not overlap. Factory/Experience/Governance are subsets of the domain result. Repeated executions, 128 hash artifacts, mapping references and baseline reproduction runs are not extra passing coverage.

### New acceptance probes

`tests/test_flora_security_01d_final_acceptance.py` adds:

- One native SQLite contention/rollback/feedback-survival probe.
- One four-request concurrent feedback/audit no-loss probe.
- One two-actor shared-profile-file/audit no-loss probe.
- One already accepted feedback versus failed unrelated profile commit probe.
- Four HTTP cleanup denial cases: stale authentication, missing grant, revoked membership and wrong workspace.
- One positive recent/scoped HTTP cleanup deletion/audit case.

All nine pass. The initial and final executions are retained as repetitions of the same identities, not eighteen cases. No production code, existing test assertion, skip configuration or fixture identity provider was modified.

## 7. Test identity and baseline reconciliation

### Inherited domain failures

All **22/22** current failed identities were freshly reproduced in the clean detached original-HEAD worktree at `83aee1a...`. Their normalized first assertion/exception signatures match both current execution and the retained baseline register. **Zero identities remain unverified.** The new acceptance does not waive any inherited defect or count later, unreached assertions as passed.

The inherited register and per-ID impact classifications are carried into the companion JSON. These include presentation/navigation and qualification/attribution/Canvas acceptance items requiring product/governance reconciliation. Their age alone does not make them acceptable production risk.

### Historical legacy failures

All 27 historical IDs were also run at original HEAD and current code. Both have three passes/24 failures, but two previously documented wording-driven statuses differ from original HEAD:

- `tests/test_flora_pilot_auth.py::test_pilot_auto_sign_in_missing_canonical_configuration_fails_safely[FLORA_PILOT_OWNER_ID-owner]`: original passed, current failed.
- `tests/test_flora_pilot_auth.py::test_pilot_auto_sign_in_missing_canonical_configuration_fails_safely[FLORA_PILOT_WORKSPACE-workspace]`: original failed, current passed.

These are the already recorded 01B diagnostic-contract changes, **not new 01D acceptance regressions**. Neither restores automatic/shared authority. The positive/negative semantic replacements remain passing. The five separately recorded pre-existing failure identities fail in both fresh original-baseline and current runs; exact IDs/signatures are in the JSON. Raw legacy failures are not relabelled as security passes.

### Skips, diagnostics and unexecuted coverage

There are no new active failures, new skips or unexecuted mandatory test identities. All 26 domain modules completed. The ten existing retained-input skips are explicitly listed below and in JSON. They are missing hash-pinned input journeys, not successful workflows or release waivers.

Separate non-active diagnostic/comparison executions are fully accounted for:

- Original archived concurrency orchestration: one failed diagnostic, explained above.
- Original-baseline domain reproduction: 22 expected failures, matching current inherited failures.
- Original-baseline historical suites: three passed/24 failed, with the two known status transitions listed above.

No claim is made that every repository test outside the specified/added selections was executed. Later assertions inside already-failed historical/domain tests remain unexecuted within those failed cases and are not certified.

| Skipped identity | Retained reason |
| --- | --- |
| `tests/test_flora_factory_evidence_release_repair.py::test_retained_tel_w5_w6_reconciliation_and_replay` | Actual retained W6 package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1 |
| `tests/test_flora_factory_evidence_release_repair.py::test_retained_bnk_same_citation_contract` | Actual retained BNK package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1 |
| `tests/test_flora_factory_evidence_release_repair.py::test_retained_tel_count_reconciliation_independent_of_citation_assertions` | Actual retained W6 package unavailable; set FLORA_AUDIT_TEL_W6 / FLORA_AUDIT_BNK_W1 |
| `tests/test_flora_factory_presentation_repair.py::test_actual_retained_user_journey_and_honest_promotion[TEL-W6]` | Actual retained artifact not available: TEL-W6 |
| `tests/test_flora_factory_presentation_repair.py::test_actual_retained_user_journey_and_honest_promotion[BNK-W1]` | Actual retained artifact not available: BNK-W1 |
| `tests/test_flora_factory_researcher_model_repair.py::test_actual_retained_source_to_memory_retrieval_and_view[TEL-W6]` | Retained artifact unavailable: TEL-W6 |
| `tests/test_flora_factory_researcher_model_repair.py::test_actual_retained_source_to_memory_retrieval_and_view[BNK-W1]` | Retained artifact unavailable: BNK-W1 |
| `tests/test_flora_factory_researcher_model_repair.py::test_actual_tel_w5_w6_handoff_reuses_observation_and_confidence_history` | Retained artifact unavailable: TEL-W6 |
| `tests/test_flora_experience_discovery_repair.py::test_actual_retained_packages_use_generic_discovery_and_keep_factory_boundaries[TEL-W6]` | Actual retained artifact unavailable: TEL-W6 |
| `tests/test_flora_experience_discovery_repair.py::test_actual_retained_packages_use_generic_discovery_and_keep_factory_boundaries[BNK-W1]` | Actual retained artifact unavailable: BNK-W1 |

## 8. Exact code/test changes and evidence preservation

This acceptance task adds only:

- `tests/test_flora_security_01d_final_acceptance.py` — nine verification cases using the existing real producer, synthetic stores and actual HTTP/SQLite service boundaries. Trace and zero-timeout contender instrumentation observe native locking; they do not replace authorization or change production transaction behaviour.
- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Report.md` — this report.
- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Evidence.json` — exact identities/statuses, signatures, preserved-file hashes, contention observations, before/after maps, committed audit checks and diagnostic accounting.

**Production implementation changes: none. Existing file changes: none.** The input manifest covers all 71 pre-existing relevant files, whose hashes remain identical. All earlier reports/evidence, the original archive and the already corrected seven-check module remain intact. The second actor exists only in an explicitly approved synthetic test binding; no production identity/workspace was inspected or provisioned.

Local execution evidence is under `work/security-repair-01d-final-acceptance/`:

- `security-command.json`, `security.xml`, `security.log`: fresh prior 349-case selection, 349 passes, including all seven active adversarial checks.
- `final-additional.xml`/`.log`, `final-additional-tmp/*/acceptance-observation.json`: nine new passes and concrete contention/concurrent-write/HTTP observations.
- `domain/results.json`, per-module XML/logs and `domain.log`: all 26 regression modules.
- `baseline-command.json`, `baseline.xml`: clean detached original-HEAD reproduction of all 22 inherited IDs.
- `baseline-legacy-command.json`, `baseline-legacy.xml`, `legacy-command.json`, `legacy.xml`: original/current historical suites.
- `supplemental-command.json`, `supplemental-fixture.xml`: the established explicit unit-authority fixture, applied only to supplemental units.
- `original-harness.xml`/`.log` and original-harness observations: failed historical orchestration, retained separately.
- `reconcile.py`, `input-manifest.json`, `dependency.json`: exact-ID/status/hash/signature/audit reconciliation, input preservation and read-only dependency snapshot.

All pytest executions use `/workspace/cios-venv/bin/python`, isolated synthetic roots and explicit JUnit paths. No stop-on-first-failure option hides later selected tests. Existing units and real-security cases use their established separate identity fixtures; no production authority double is installed in real-security modules. Private scratch contains enrollment deliveries, sessions and raw test stores and must not be staged or published wholesale.

## 9. Residual operational risks and limits

- Evidence establishes the tested **local, single-canonical-authority, participating-writer** protocol. It does not establish live Render volume semantics, deployed process count/SHA, outside writers, mount/fsync/locking behaviour or distributed operation.
- The full-root snapshot protocol still costs disk space, inodes, I/O and lock time. Streaming hashes/reservation help but are not a physical ENOSPC, power-loss, hardware-corruption or load qualification. The repository's 1 GB disk declaration is not measured production headroom. Failed recovery may deliberately close authority and require operator repair; no unjournaled destructive fallback is approved.
- Independent backups, production restoration/rollback, legacy journal/ownership reconciliation and actual production account bindings remain unverified. Missing/conflicting historical scope must not be invented to reopen access.
- HTTP tests exercise real local server boundaries, origin/CSRF/cookie headers and replay policy, not a live TLS deployment or actual Safari/iPad cookie enforcement.
- Concurrent no-loss checks establish preservation of independent records/actor keys under serialized service operations. No new client-side optimistic merge contract for competing full-object replacements is implied. External provider costs/effects and committed-but-unacknowledged retry outcomes remain outside filesystem undo.
- The 22 inherited product failures and ten missing retained-input journeys are not waived. Their downstream unexecuted assertions still require separate product/governance review.

These limits do not invalidate the passing bounded assertions, but they prevent treating this acceptance as production safety or deployment approval. Independent PR-readiness review must examine the accumulated implementation and operating assumptions again.

## 10. Draft PR #539 dependency status

GitHub was queried read-only during this acceptance. Observed status:

- https://github.com/rdidale-jpg/CIOS/pull/539 — **open, draft, not merged**.
- Head branch: `codex/flora-security-repair-01a`.
- Head SHA: `83aee1aaf5a49b36d8c5e397d75b99624422fac3`, matching the local branch's unchanged HEAD.
- Reported base: `main`, SHA `dc9203e6880f8722e821d39cf53b689732edb0e7`.

The dependency remains unresolved for release/merge purposes. Its current state is verified, not assumed; its interfaces are not certified final or stable. Any later head/interface change requires renewed dependency review and relevant validation. No PR was created or modified and neither PR is authorised for merge/deployment by this result.

## 11. Git branch, HEAD and working-tree status

Branch: `codex/flora-security-repair-01b`.
HEAD: `83aee1aaf5a49b36d8c5e397d75b99624422fac3`.
Index: empty. All accumulated changes remain uncommitted.

No commit, push, PR creation/modification, merge, deployment, production provisioning, production setting change or production intelligence/data mutation occurred. Git diff whitespace checks and changed test compilation pass. A scoped reviewed-file credential-pattern scan excludes private scratch and does not claim to prove absence of every sensitive value.

The following status includes all prior accumulated 01B/01C/01D work and this task's three new files:

```text
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

The complete relevant accumulated inventory contains **74 files**, excluding private `work/` scratch:

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
- `tests/test_flora_security_admin_policy.py`
- `tests/test_flora_security_adversarial_remediation.py`
- `tests/test_flora_security_independent_readiness.py`
- `tests/test_flora_security_integrity_repair.py`
- `tests/test_flora_security_legacy_obligations.py`
- `tests/test_flora_security_owner_journey.py`
- `tests/test_flora_security_release_review.py`
- `tests/test_flora_security_repair_01b.py`
- `tests/test_flora_security_workspace_boundary.py`

**Final verdict: REMEDIATED. Progression is limited to independent PR-readiness review. All work remains uncommitted and production is unchanged.**
