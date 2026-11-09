# FLORA 01F — Controlled local commit inventory

This is the exact approved selection for one local FLORA 01B–01E commit. Source baseline: `83aee1aaf5a49b36d8c5e397d75b99624422fac3`; branch: `codex/flora-security-repair-01b`. The dependency is draft #539 at that exact SHA; fresh read-only verification found it open, draft and unmerged, with main base `dc9203e6880f8722e821d39cf53b689732edb0e7`.

01E source/test hashes and the complete 82-file reviewed inventory match. Read-only reconciliation rechecked retained raw JUnit, exact IDs, signatures, 146 integrity comparisons, 17 audit digests and 15 chains without rewriting prior evidence. The seven unchanged original adversarial tests were freshly rerun: **7 passed**. No source/test/dependency changes were made in 01F. The accepted 388 security passes and unchanged 404/22/10 domain result remain the validation boundary; no broad rediscovery or repeated full-suite run was needed.

01E documents are the current acceptance record. Included 01D reports and registers are essential historical references and retain their original verdicts/counts. The archived concurrency file is historical, outside active pytest collection. Local `work/` provenance paths in JSON and historical inventories refer to excluded scratch; these metadata references are not committed SQLite stores, synthetic data or logs. Raw validation artifacts remain local. The current evidence records a bounded readiness result, not a universal security guarantee or deployment approval.

The proposed PR description is in `01F-Proposed-PR-Description.md`. Commit/publication state is reported separately after the local commit; this inventory does not authorize push, PR creation/modification, merge, deployment or production changes.

## Production security and integrity implementation (24 files)

- `cios/applications/flora/access.py`
- `cios/applications/flora/blueprint_import/lifecycle.py`
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
- `cios/applications/flora/memory/service.py`
- `cios/applications/flora/pilot_auth.py`
- `cios/applications/flora/protected_storage.py`
- `cios/applications/flora/security.py`
- `cios/applications/flora/security_operator.py`
- `cios/applications/flora/security_store.py`
- `cios/applications/flora/security_web.py`
- `cios/applications/flora/storage_maintenance.py`
- `cios/applications/flora/web/app.py`

## Regression, adversarial and domain test support (24 files)

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
- `tests/test_flora_security_01e_bounded_remediation.py`
- `tests/test_flora_security_admin_policy.py`
- `tests/test_flora_security_adversarial_remediation.py`
- `tests/test_flora_security_independent_readiness.py`
- `tests/test_flora_security_integrity_repair.py`
- `tests/test_flora_security_legacy_obligations.py`
- `tests/test_flora_security_owner_journey.py`
- `tests/test_flora_security_release_review.py`
- `tests/test_flora_security_repair_01b.py`
- `tests/test_flora_security_workspace_boundary.py`

## Required dependency/configuration changes (2 files)

- `pyproject.toml`
- `requirements.txt`

## Current evidence and essential historical references (11 files)

- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Evidence.json`
- `docs/flora-runtime/security-repair-01b/01D-Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/01D-Independent-PR-Readiness-Evidence.json`
- `docs/flora-runtime/security-repair-01b/01D-Independent-PR-Readiness-Review.md`
- `docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Evidence.json`
- `docs/flora-runtime/security-repair-01b/01E-Bounded-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/01F-Commit-Preparation.md`
- `docs/flora-runtime/security-repair-01b/01F-Proposed-PR-Description.md`
- `docs/flora-runtime/security-repair-01b/Inherited-Failure-Register.json`
- `docs/flora-runtime/security-repair-01b/Legacy-Positive-Obligation-Reconciliation.json`
- `docs/flora-runtime/security-repair-01b/history/pre-security-integrity-remediation/test_flora_security_independent_readiness.py`

**Total: 61 files.**

## Excluded but preserved historical files (23)

- `docs/flora-runtime/security-repair-01b/Adversarial-Remediation-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Adversarial-Remediation-Report.md`
- `docs/flora-runtime/security-repair-01b/Completion-Report.md`
- `docs/flora-runtime/security-repair-01b/Controlled-PR-Proposal.md`
- `docs/flora-runtime/security-repair-01b/Failure-Root-Cause-Matrix.json`
- `docs/flora-runtime/security-repair-01b/Final-Acceptance-Comparison.json`
- `docs/flora-runtime/security-repair-01b/Final-Acceptance-Report.md`
- `docs/flora-runtime/security-repair-01b/Independent-Release-Readiness-Evidence.json`
- `docs/flora-runtime/security-repair-01b/Independent-Release-Readiness-Review.md`
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

Additionally excluded: all private `work/` scratch/comparison worktrees, SQLite databases/journals, synthetic runtime stores, raw local logs, caches and bytecode. No historical evidence is deleted or altered to achieve this selection. No unrelated source changes are included.

## Remaining limits

22 inherited domain failures, 24 historical legacy failures and 12 additional financial diagnostic failures remain explicitly accounted; ten retained-artifact skips remain. Production storage/capacity, locking/load and topology, backup/disaster recovery, crash consistency, external writers and migration/rollback are unqualified. Unsealed pending recovery journals need inspected recovery before upgrade. No deployment approval is inferred from peer-review readiness.
