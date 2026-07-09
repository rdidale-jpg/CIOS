# Flora Sprint 1 PR8 — Governed Canvas Feedback and Human Knowledge Capture Completion Report

**Date:** 2026-07-09  
**Commit boundary:** governed Enterprise Canvas feedback capture only

## Summary

PR8 adds a bounded, governed feedback pathway from Enterprise Canvas tile detail and lineage inspection views. Authorised users can confirm, challenge, correct, add context, add labelled Human-Supplied Knowledge, identify Unknown candidates, flag Contradiction candidates, request Evidence or suggest refresh.

Every submission is stored as candidate feedback with contributor attribution, enterprise/tile/judgement/lineage references, statement, rationale, expected consequence, visibility classification, lifecycle status and append-only audit history. Submission does not update canonical Evidence, Observations, Enterprise Model state, pain priorities or analytical projections.

## Human-Supplied Knowledge treatment

Human knowledge is explicitly labelled as direct knowledge, interpretation, account knowledge, calibration or validation. It preserves who supplied it, their role or basis of knowledge, when it was supplied, the related displayed judgement, whether it supports, weakens or contradicts the judgement and whether documentary Evidence may exist. It is not displayed as independently verified fact.

## Unknown, Contradiction and Evidence-request treatment

Unknown and Contradiction submissions create governed candidate classifications within the feedback record. They preserve why the issue matters and what could resolve it. Evidence requests record what Evidence is required, why it matters, the judgement it could strengthen, weaken or retire, likely owner/source and urgency/accountability event where supplied. No research is performed automatically.

## Lifecycle and review behaviour

Feedback lifecycle states are separate from Observation lifecycle, Evidence status, confidence and canonical acceptance: submitted, under review, accepted as Human-Supplied Knowledge, rejected, deferred, needs Evidence, superseded and withdrawn.

Authorised reviewers can append status-change records. Unauthorised users cannot review feedback.

## Audit history and supersession

Each submitted record includes an initial audit event. Status changes append a new record containing the accumulated audit history. Corrections and replacements use supersession references rather than silently editing the original statement.

## Access control and confidentiality

Feedback submission, viewing and review are checked server-side against product-session user, enterprise access and feedback roles. Standard feedback can be seen by authorised enterprise feedback users. Restricted and account-confidential feedback require review/restricted privileges.

## Tests and results

Targeted Blueprint-import, Canvas read-model, Canvas UI, lineage and feedback tests pass together:

- `pytest tests/test_flora_blueprint_import_validation.py tests/test_flora_blueprint_import_registry.py tests/test_flora_blueprint_import_review_planning.py tests/test_flora_blueprint_import_promotion.py tests/test_flora_enterprise_canvas.py tests/test_flora_enterprise_canvas_feedback.py -q` — 48 passed, 1 warning.

Feedback-specific tests cover authorised and unauthorised submission, Canvas tile linkage, lineage linkage, confirmation, challenge, correction, Human-Supplied Knowledge labelling, Unknown candidate, Contradiction candidate, Evidence request, confidentiality filtering, status display data, authorised review-state change, unauthorised review rejection, append-only audit history, supersession, deterministic feedback identity, and no canonical Evidence, Observation or Enterprise Model mutation.

Full repository suite comparison: `pytest -q` reported 48 failed, 526 passed, 2 skipped and 1 warning. The latest merged PR7 completion report recorded the baseline as 48 failed, 513 passed, 2 skipped and 1 warning, so the failure count did not increase and the 13 added feedback tests account for the increased pass count.

## Deferred workflows

Canonical feedback acceptance remains deferred. PR8 does not implement automatic canonical updates, automatic Observation or Evidence creation, automatic pain reprioritisation, AI approval, automatic Unknown/Contradiction resolution, Provider Fit, opportunity scoring, MOD-specific logic, extra Canvas lenses, collaboration, messaging or document editing.

## Confirmation

Feedback creates governed candidate intelligence only. It does not directly change canonical intelligence displayed in the Twin.
