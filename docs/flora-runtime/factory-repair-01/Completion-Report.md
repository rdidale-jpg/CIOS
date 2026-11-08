# Flora Industry Twin Factory Repair 01 — completion report

Date: 8 November 2026. Scope: audit defects F01–F03 only. Baseline GitHub main:
`5c1348a0aa714b0b1a63c08443447012689bb97b`, including merged PRs #530–#533;
rechecked against `git ls-remote origin refs/heads/main` during final validation.

This repair changes integration code and isolated tests. It does not establish
complete Industry Twin acceptance, promote production intelligence, migrate old
releases, change accepted ADRs, or deploy the repair.

## Ownership and authority

The pre-implementation [assessment](Identity-and-Ownership-Assessment.md) records
the original identity break and the minimum correction. Canonical ownership stays
with the existing EvidenceRepository, mapping/review repositories, promotion
service and TwinImportLifecycleService. The identity decision is an overlay in the
existing GovernedIdentityResolutionRepository; archived producer bytes remain
unchanged. No new canonical store or identity service was introduced.

Accepted authorities remain:
[ADR-002](../../../architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md),
[ADR-009](../../../architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md),
[ADR-012](../../../architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md),
and [ADR-026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md).
ADR-012 distinguishes package and object acceptance, preserves source identity,
and requires idempotent, lineage-preserving canonical promotion. This change does
not treat draft model specifications or roadmap statements as runtime proof.

## Exact integration changes

| Failure/boundary | Implemented correction | Regression evidence | Limit and consequence |
| --- | --- | --- | --- |
| F01: UI defaults generate release-specific Evidence IDs while citations retain source IDs | `mapping.ImportMappingService` retains a free source ID or selects a scoped target. Promotion binds controlled citation fields and relationship endpoints through approved mappings; raw `source_payload`, locations and source IDs stay inspectable. Review/completion disclose source-to-canonical mappings. | New `test_ui_defaults_preserve_source_citation_and_lineage`, explicit mapping/operator/relationship tests, retained TEL/BNK tests. | No permissive lookup was added to EvidenceRepository, ClaimValidator or ADR-026. Missing external support in existing Enterprise partial imports remains ineligible, recorded in lineage, and excluded from model projection. |
| F02: unchanged Evidence duplicated across TEL releases | Mapping matches exact producer content and source ID within the full approved owner/Twin scope. Reuse appends source-release provenance without creating another logical Evidence row or changing confidence. Changed assertions require explicit reviewed update and retain `prior_canonical_version`. | Cross-release, alias, changed-content, corroborating, contradiction, collision and replay tests; actual TEL W5/W6 count test. | Exact identity/content only; similar URLs or wording never establish identity. Contradiction classification uses explicit source conflict metadata; other changed assertions remain unresolved pending owner review. |
| F03: missing identity and two current releases | New owner-authorised identity action validates the existing complete BlueprintManifest identity fields. Explicit mappings/identity changes regenerate review plans. Release matching includes access owner, workspace, Twin/type/subject/class/canonical owner/scope. Successful promotion stages new/current and prior/superseded lifecycle states inside existing compensation, exposed only through a successful execution receipt. | Identity/authority/stale approval/legacy rewrite, supersession, receipt-failure and hard-interruption tests. | No filename inference, automatic legacy relabelling or migration. Multiple current releases fail closed for explicit reconciliation. |
| Rejection may lose to older approval | CandidateReviewRepository now selects the latest timestamp, rather than hash filename order. UI defaults preserve manual mappings. | Rejected/deferred/quarantined/unsupported and staging-ineligible source tests. | Existing owner promotion permission and plan confirmation still apply. Review defaults alone do not execute promotion. |
| Reused Evidence was absent from review reconciliation totals | Existing review summary counts canonical Evidence reuse as unchanged, distinct from staging-only support records. | Cross-release and retained-package tests exercise the actual review coordinator. | Existing domain-wrapper persistence boundaries are unchanged. |
| Operator resolution and completion status | Existing review supports explicit canonical target/reuse/update decisions with rationale; identity requires owner authority, complete fields and confirmation. Completion reports release state and Evidence mapping separately from technical validation and full Twin acceptance. | Operator mapping and normal UI owner approval tests. | No Canvas, dossier or Navigator redesign. |

Implementation locations are existing modules under
`cios/applications/flora/blueprint_import/`: `mapping.py`, `review.py`,
`review_plan.py`, `planning.py`, `promotion.py`, `twin_governance.py`,
`lifecycle.py`, `views.py`, with two POST actions wired in `web/app.py`
(identity and Evidence mapping). Tests are in
`tests/test_flora_factory_evidence_release_repair.py`.

## Retained package evidence

No producer package was edited. Tests use explicit isolated governed identity
fixtures and owner decisions; those decisions are not production business
acceptance. The retained-package comparison uses the existing governed-identity
linking method on both baseline and repaired code. The new initial identity action
is tested separately through its operator handler.

| Actual artifact | SHA-256 | Isolated repaired outcome |
| --- | --- | --- |
| TEL W5, repository `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip` | `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07` | 92 Evidence records; all 92 source IDs resolve through canonical Evidence lookup. |
| TEL W6, user-supplied targeted enrichment corrected ZIP | `c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb` | After W5: 92 unchanged plus 10 new, 102 total; 92 records retain two release-provenance entries; W5 superseded, W6 current, W5 archive/history retained. |
| BNK W1, user-supplied manifest-compatible ZIP | `1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313` | 65 Evidence records and 65 source-ID lookups; same generic mapping path. |
| NRG | Not available | NOT TESTED. No artifact was invented or researched. |

Retained tests verify source payload equality and every recorded approved binding
against EvidenceRepository, including persisted generic-record lineage. They also
assert zero canonical Observations, preserving the existing wrapper/model
boundary. Same-approval and same-package UI replay change neither row counts nor
provenance. No Opportunity or Procurement is created by this repair.

## Before/after validation

| Suite | Baseline | Repaired | Interpretation |
| --- | --- | --- | --- |
| 383 existing tests, 28 modules | 366 passed / 17 failed | 366 passed / same 17 failed | No new failures. |
| 41 Repair 01 tests | 1 passed / 40 failed | 41 passed | Existing same-package UI replay already worked. New contract/path tests expose missing bindings, reconciliation, initial owner identity action and safeguards; failures are not 40 distinct production defects. |
| All selected tests | 367 passed / 57 failed | 407 passed / 17 pre-existing failures | No setup errors or skips in the valid comparison. |

[Machine-readable comparison](Regression-Comparison.json) records every module,
counts, duration and exact failing test names. The complete existing import/model
reconciliation suite passes 35/35, Material Pressure lifecycle 51/51, external change
interpretation 42/42, intelligence integrity 44/44, Enterprise reasoning 7/7,
Enterprise memory 16/16, and promotion 21/21. The actual retained cross-release test
also independently reproduces **194 baseline Evidence rows versus 102 repaired**
after TEL W5 then W6, without stopping at the earlier citation failure.

Pre-existing failures are unchanged:

| Module | Failures | Boundary |
| --- | --- | --- |
| `test_tel001_blueprint_import_regression.py` | 4 | Pilot review and existing factual/aspect/dossier/association expectations. |
| `test_tel001_enterprise_factual_presentation.py` | 1 | Existing factual route presentation. |
| `test_flora_banking_industry_reinvention_increment42.py` | 6 | Banking causal narrative, mapping, supplier/heatmap/opportunity presentation and retained rendering artifact expectations. |
| `test_flora_blueprint_import_executive_review.py` | 2 | Existing review copy/context-link expectations. |
| `test_flora_blueprint_import_restage.py` | 2 | Existing restage action and stale/non-atomic review expectations. |
| `test_flora_blueprint_import_interface.py` | 2 | Existing review-count markup and deployment panel copy. |

These failures were retained and reported; no assertions were weakened to make
unrelated presentation suites green. Valid final comparison output roots were
`/workspace/work/factory-repair-evidence/verified-before` and `verified-after`.


The existing promotion test that requested an update to nonexistent
`EVID-existing` now seeds an actual previous Evidence record. The corrected
fixture is used identically on both baseline and repaired code; a new regression
explicitly rejects missing reuse/update targets. Other existing tests are unchanged.

Commands:

```bash
# Set these to the actual retained files; absent files explicitly skip their tests.
export FLORA_AUDIT_TEL_W6=/path/to/retained/TEL-W6.zip
export FLORA_AUDIT_BNK_W1=/path/to/retained/BNK-W1.zip
python docs/flora-runtime/factory-repair-01/run_regressions.py --output /tmp/flora-repair-01-after
# Focused Repair 01 tests:
python -m pytest -q tests/test_flora_factory_evidence_release_repair.py
```

For the baseline comparison, use a detached worktree at the SHA above, copy the
new regression file and corrected existing promotion test into that worktree,
and run the same harness with a different output root. Each module runs in a
separate process and temporary FLORA_DATA_DIR / FLORA_PILOT_DIR. JSON summaries,
JUnit XML and complete failure logs are produced. Optional external-package tests
pin hashes and skip explicitly when unavailable. Do not run the harness against
production storage. The local interpreter was `/workspace/cios-venv/bin/python`.

A preliminary comparison harness run failed before test setup because its pytest
base directory parent was absent. The harness was corrected and the complete
comparison rerun in fresh roots; those setup errors are not counted as product
defects or passing validation.

## Remaining limitations and next actions

- **Deployment NOT TESTED for this repair.** The PR is unmerged and no deployment
  was requested or performed. Local route/service tests do not prove deployed
  behavior at `https://flora-current.onrender.com`.
- **Single-writer file compensation remains.** Normal errors restore canonical,
  model, ledger and lifecycle files. A hard interruption can leave canonical
  writes/backups needing operator recovery. Lifecycle reads retain the previous
  current release until a successful receipt; retries fail closed with recovery
  diagnostics. This repair does not claim database transactions or automatic
  crash recovery.
- **Legacy releases remain unchanged.** Scope-less legacy Evidence requires an
  explicit reviewed mapping. Already accepted or terminal identities cannot be
  silently rewritten. Any production backfill or cleanup needs separate approval.
- **No new qualification authority.** Import lifecycle eligibility is distinct
  from date, claim-support and commercial-pressure qualification. Original
  incomplete dates/source content remain unchanged; strict downstream validators
  still decide reasoning eligibility. No pressure is converted into opportunity,
  procurement, funding or buying intent.
- **Partial package promotion remains partial.** Wrapper-to-model integration,
  Banking dossier defects, accepted-domain rendering, economic reasoning and
  Navigator work remain outside Repair 01. Source-search prose or missing support
  is not turned into Evidence or a fact; existing Enterprise partial imports retain
  lineage and projection diagnostics.
- **Evidence-only reconciliation.** Other record classes retain their existing
  identity/update rules. This repair does not certify semantic deduplication or
  scoped identity for Unknowns, relationships or domain wrappers; prior package
  bytes remain the historical source for those unchanged boundaries.
- **Conservative source reconciliation.** Explicit contradictory records block
  promotion; unspecified semantic differences stay unresolved. Cross-source
  semantic deduplication and automated contradiction reasoning are not introduced.

The next action is review of this bounded PR and its evidence, followed by the
owner's merge/deployment decision. Repair 01 stops here; later integration and
product work have not begun.
