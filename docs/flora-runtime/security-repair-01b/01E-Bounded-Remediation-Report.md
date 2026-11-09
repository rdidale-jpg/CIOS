# FLORA 01E — Bounded Security Remediation Closure

**READY FOR PR REVIEW.** The three confirmed defect groups are corrected; all seven unchanged adversarial assertions and 23 focused closure checks pass. No material unresolved code-level defect was demonstrated within the agreed scope. This is a bounded engineering closure recommendation, not universal security coverage or production acceptance. **No commit, push, PR creation, merge or deployment is authorized or performed.**

Branch remains `codex/flora-security-repair-01b`, HEAD `83aee1aaf5a49b36d8c5e397d75b99624422fac3`. The index is empty. Earlier reports, tests and evidence remain preserved; they describe their historical states. The companion `01E-Bounded-Remediation-Evidence.json` records identities, hashes, commands, exact comparisons and the full accumulated file inventory. All validation uses synthetic/local storage.

## Root causes and corrections

| Confirmed root cause | Bounded correction | Closure evidence |
| --- | --- | --- |
| Financial scope checked `enterprise_id`, while canonical ingestion wrote `canonical_enterprise_id`. | Existing financial-run evaluator rejects conflicting claim identifiers. `apply_accepted` calls a guarded downstream `process_reviewed_evidence` boundary which reloads the persisted run, validates all destination fields and actual Enterprise normalization, and applies current capability, workspace and ACL checks before the first Evidence save. The existing protected-write transaction covers Evidence, model and run status. | Original cross-Enterprise/workspace write fails closed. Downstream foreign/conflicting/anonymous calls leave protected data unchanged. Authorized apply creates Evidence and actual model attributes. |
| Candidate deletion performed raw destructive writes after one stale preview, without the service transaction, strict scope/ACL or atomic audit. | Deletion uses the existing verified-service envelope with recent authentication, exact loaded package scope and applicable ACL, current actor/capability checks, a fresh package/governance check immediately before effects, and an ACL/authority check before return. Domain deletion ledger and mandatory resource authority audit share the filesystem journal/SQLite transaction. | All five original deletion assertions pass. Authorized deletion commits one contextual resource audit. Both ledger and authority-audit faults roll back protected deletion. Concurrent promotion waits for failed deletion to recover, then commits successfully. Concurrent revocation serializes after an executing deletion and denies the next call. |
| Recovery treated a possibly incomplete manifest as the complete original snapshot, then deleted unlisted originals and discarded backups. | Snapshot publication fsyncs a separate manifest SHA256 seal. Recovery validates the seal, structure, safe paths, complete parent/directory metadata, unique backup references, exact backup inventory, contents, modes and file types before any restore/delete. Inconsistent snapshots are retained and authority resolution fails closed. The transaction preserves the original failure and adds a recovery-error note instead of concealing either diagnosis. | Original valid-JSON omission no longer deletes the victim or discards recovery evidence. Missing entry, extra backup, corrupted backup and incomplete directory metadata preserve original protected data and block subsequent transactions. Interrupted valid recovery retains its journal and successfully restores on retry. |

The seal detects corruption; it does not authenticate storage against an attacker who can rewrite both private metadata and backups. Private security storage and the canonical writer lock remain trust assumptions. Unsealed pending journals are rejected; upgrading a deployment with such an artifact requires explicit inspected recovery, never a permissive fallback.

Immediately adjacent lifecycle inspection found the equivalent cancellation service relied on its caller. It now uses the existing `package.review` envelope, persisted package scope, actor and applicable ACL enforcement; its HTTP caller passes verified headers and returns a safe denial. Existing cancellation/governance rules remain. Promotion/supersession lifecycle helpers remain internal to the existing guarded promotion flow; no separate permission engine or unrelated service refactor was introduced.

## Seven original adversarial outcomes

The original `tests/test_flora_security_01d_pr_review.py` is byte-for-byte unchanged. All seven pass in the final combined 30-case run:

- **PASS** `tests/test_flora_security_01d_pr_review.py::test_candidate_delete_intersects_persisted_scope_and_existing_acl[denied-resource-acl]`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_candidate_delete_intersects_persisted_scope_and_existing_acl[missing-persisted-workspace]`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_direct_candidate_deletion_cannot_continue_after_committed_revocation`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_candidate_deletion_audit_failure_preserves_protected_data`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_valid_json_manifest_omission_cannot_silently_delete_snapshot_data`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_completed_promotion_cannot_be_deleted_using_stale_candidate_preview`
- **PASS** `tests/test_flora_security_01d_pr_review.py::test_financial_apply_validates_actual_canonical_enterprise_target`

The 23 focused tests cover allowed deletion and financial apply/model updates, downstream destination denials, recent-auth/actor/confirmation restrictions, mandatory authority-audit rollback, cancellation scope/ACL, corrupted snapshots, interrupted restore, native writer contention with promotion/revocation, and persisted scope/ACL changes before and after deletion effects. Authorization producers are real; no permissive fixture was added. Fault/interleaving hooks do not replace permission decisions.

## Fresh regression and integrity results

| Gate | Final result |
| --- | --- |
| Existing 01A–01D security | 358 passed (349 + 9) |
| Seven original PR-review adversarial tests | 7 passed |
| Focused 01E closure tests | 23 passed |
| Total selected security | **388 passed**, zero failures/skips |
| Complete established domain gate | **404 passed, 22 inherited failures, 10 original skips** |
| Factory | 88 passed, 8 original skips |
| Experience | 56 passed, 2 original skips |
| Governance | 157 passed |
| Supplemental explicit historical domain fixture | 39 passed |
| Historical legacy suite | 3 passed, 24 historical failures |
| Legacy positive obligations | 19/19 mappings reference passing security tests |
| Existing protected-store comparisons | 128 unchanged |
| Added protected-store comparisons | 18 unchanged |
| Total protected-store comparisons | **146 unchanged** |
| Committed record audit digests | 17 matching |
| Selected healthy audit chains | 15 valid |

Exact ID/status comparison shows no new failure or skip in the established gates; all 22 domain first-failure signatures and all 24 legacy first-failure signatures match 01D. The 22 also retain their previously reproduced original-HEAD evidence. Ten skips still require unavailable retained TEL-W6/BNK-W1 inputs; no new skip was introduced. The five pre-existing legacy failures remain separately recorded in the companion.

Established gates plus the new security checks contain **890 disjoint active IDs: 834 passed, 46 baseline failures, 10 skips**. The 46 are 22 domain and 24 legacy; security is green. Repeated executions and original-HEAD/archived diagnostics are not added to coverage. The previously approved concurrency harness correction and preserved archive remain unchanged; active concurrency acceptance passed.

The affected five-module financial diagnostic selection adds **47 distinct IDs: 35 passed, 12 failed**. All IDs/statuses and normalized failure signatures match an isolated reconstruction of pre-01E accumulated code, whose source/test hashes were checked against the 01D input manifest. Original HEAD has 39 passed/8 failed in that selection; four later failures are pre-existing protected-read contract changes, not introduced by 01E. These extra harness failures are visible qualification gaps, not silently incorporated into the 22-domain baseline. Counting these additional current diagnostics as well gives **937 IDs: 869 passed, 58 baseline/historical failures, 10 skips**. The new real-authority financial positive tests demonstrate legitimate apply and model updates rather than weakening those historical suites.

Additional financial diagnostic register (unchanged versus pre-01E):

- `tests/test_flora_ai_financial_report_review.py::test_ai_financial_report_review_applies_accepted_claim`: update_reviews(run['run_id'], {f"action_{run['claims'][0]['claim_id']}": ['accept']})
- `tests/test_flora_ai_financial_report_review.py::test_review_page_exposes_accept_amend_reject`: html = ai_review.run_page(run['run_id'])
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_records_source_retrieval_failure`: assert run['status'] == 'source_retrieval_failed'
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_records_provider_not_configured`: assert run['provider_status'] == 'not_executed'
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_refresh_creates_missing_nested_directories`: assert run['status'] == 'completed'
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_persistence_failure_is_not_provider_failure`: assert run['status'] == 'persistence_failed'
- `tests/test_flora_ai_financial_report_review.py::test_provider_request_failures_remain_classified`: assert run['status'] == 'provider_request_failed'
- `tests/test_flora_ai_financial_report_review.py::test_missing_financial_intelligence_run_returns_usable_page`: html, status = review.financial_intelligence_run_response('fi-0304783822cb')
- `tests/test_flora_ai_financial_report_review.py::test_old_financial_intelligence_url_does_not_raise`: html = review.financial_intelligence_run_page('fi-old-missing')
- `tests/test_flora_ai_financial_report_review.py::test_flora_data_dir_defaults_to_render_persistent_pilot_storage`: assert status['ready'] is True
- `tests/test_flora_ai_financial_report_review.py::test_provider_timeout_is_distinct_and_records_safe_diagnostic`: assert run['status'] == 'provider_timeout'
- `tests/test_flora_ai_financial_report_review.py::test_progress_run_deduplicates_refresh_clicks`: html = review.financial_intelligence_progress_page(first['run_id'])

The first general-domain run used the wrong harness variable (`FLORA_DATA_ROOT` instead of `FLORA_DATA_DIR`), producing two extra read-only-default-path failures. It is retained as diagnostic evidence. The entire 26-module domain selection was rerun with the correct per-module synthetic directories; final comparison above uses that run. Financial baseline/pre-01E/current comparisons were likewise rerun with the correct variable. Initial new corruption checks also counted intentionally retained private journals as unexpected application files; the final comparator records the full map, verifies every protected application file unchanged, and independently asserts retained journal/evidence and closed subsequent authority. Existing security assertions were not changed.

For corruption tests, 4 of the 18 added comparisons distinguish protected application data from the deliberately retained private recovery artifacts, whose full observed hash maps are also recorded. The other 14 compare the complete existing helper inventory. No successful recovery or mutation is reported after mandatory audit or restoration failure. Promotion accepted after failed-deletion recovery and existing independently committed feedback retain their data and audit evidence.

## Security closure boundary

1. **HTTP/direct services:** existing authentication, CSRF/origin and protected-route/public-data controls remain covered by 01A–01D tests. Reviewed financial apply and its downstream service, destructive candidate deletion, and adjacent cancellation enforce their own boundary independently of HTTP wrappers. This is not an inventory of every internal repository primitive as an independently callable authenticated API.
2. **Mutation authority:** existing resolver/evaluator supplies current human identity, active membership, effective capability and selected workspace. Persisted resource scope and applicable Canvas ACL intersect those grants. Candidate imports may legitimately precede creation of a Canvas ACL; an existing ACL is always intersected, and missing package scope never defaults to the selected workspace.
3. **Canonical destination:** human-reviewed financial ingestion binds actual normalized destination to the authoritative run. Conflicting aliases cannot authorize another Enterprise. Trusted worker/offline ingestion primitives retain their existing integration contract; no new public unauthenticated ingestion route is introduced.
4. **Transactions/audit:** consequential mutations participate in the canonical authority writer transaction and protected journal. Candidate deletion includes its contextual resource audit and domain ledger; rejection restores protected data. Tests exercise promotion and revocation ordering with actual SQLite contention, not an invented concurrency policy.
5. **Recovery failure:** complete snapshot metadata and backups are checked before destructive undo. Validation failure preserves artifacts and blocks access pending recovery. A valid interrupted restore can retry. Retaining evidence may require operator action; availability is not obtained by discarding unsafe undo.
6. **Operational assumptions:** one local canonical authority database and shared protected root, supported fsync/rename/locking semantics, participating writers, private security-directory permissions and sufficient snapshot/reserve capacity. Local process tests are not proof against device failure or split-instance topology.
7. **Remaining inherited/accepted risks:** the 22 domain and 24 historical legacy failures are explicit product/contract issues; ten retained-input gaps and the 12 unchanged additional financial diagnostic failures remain reported. Their first failures do not prove subsequent assertions. No new critical/high finding remains demonstrated in the bounded repair. Medium/low follow-up does not automatically reopen unrelated completed domains.

## Changed-file inventory and preservation

Exactly eight existing implementation files changed in this task:

- `cios/applications/flora/access.py`
- `cios/applications/flora/document_review.py`
- `cios/applications/flora/protected_storage.py`
- `cios/applications/flora/security_store.py`
- `cios/applications/flora/security.py`
- `cios/applications/flora/blueprint_import/lifecycle.py`
- `cios/applications/flora/blueprint_import/views.py`
- `cios/applications/flora/memory/service.py`

Three task deliverables were added:

- `tests/test_flora_security_01e_bounded_remediation.py`
- `docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Evidence.json`

No earlier tests, reports or evidence were edited. Complete pre-task application/test/document hashes and final implementation hashes are retained in the companion and `work/security-repair-01e/input-manifest.json`. The companion lists every accumulated relevant modified/untracked file against HEAD; private scratch, synthetic stores and detached comparison worktrees are excluded from proposed PR content. Syntax compilation and `git diff --check` pass. A scoped high-confidence credential scan found no new private-key/token patterns; synthetic test data is intentional. This is not a guarantee that every possible sensitive identifier has been classified for publication.

## Remaining risks, proposed PR and next engineering phase

**Critical/high:** none unresolved demonstrated within the agreed three-group/adjacent lifecycle scope after these assertions. This does not certify every service or external writer.

**Medium/low follow-up:** historical domain/financial harness contract reconciliation and retained-package availability remain prioritized product/test work. No additional unrelated remediation cycle is started here. Audit chains establish internal consistency, not off-host tamper resistance.

**Operational/deployment:** actual production disk capacity (including snapshot/reserve overhead), load/lock contention, multi-instance/shared-mount topology, backup restoration, off-host disaster recovery, fsync/power-loss behavior and migration/rollback remain unqualified. Unsealed pending journals require inspected recovery before upgrade. Missing workspace ownership must not be fabricated. Deployment is not approved; production was unchanged.

Proposed PR scope: accumulated FLORA 01B–01E verified owner/workspace authority and bounded security/integrity repairs, with tests and explicitly historical versus current evidence. It must be stacked on draft **#539**, pinned to the current baseline SHA. The previous read-only inspection found #539 open/draft/unmerged with that exact head. Changes to the dependency require renewed compatibility checks; no update or merge of #539 is required merely to review this pinned stack. Proposed title: **FLORA 01B–01E: verified workspace authority and bounded integrity repairs**.

Recommendation: close this bounded remediation phase and proceed to controlled peer review preparation, with the inherited failure registers and operational limits visible. Commit/publication require separate authorization. Engineering can return to product development; production qualification remains a separate gate. No commit, push, PR action, merge, deployment, production identity provisioning or production configuration/data modification occurred.
