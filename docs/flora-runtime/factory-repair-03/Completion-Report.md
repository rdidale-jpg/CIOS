# Industry Twin Factory Repair 03 — completion report

Baseline: `cf7942fabb5f456f827c08f88e0d189a46ebc69f`, main after merged PR #535,
including #530–#535. Remote main was checked again before publication. The
[pre-change journey assessment](User-Journey-Assessment.md) records the defects and
minimum intervention. This increment changes existing presentation, read adapters
and review summaries. It adds no canonical store, model owner, framework,
scheduler, research, economic engine or Navigator.

## Corrected boundaries

| Defect | Existing boundary and correction | Evidence | Limit / consequence |
| --- | --- | --- | --- |
| F06 — BNK associations | `semantic_twin.ASSOCIATION_DIRECTIONS`, `query_subject_associations`, `opportunity_enterprise_names`: exact `Owner owns Programme` and `Enterprise has Opportunity Hypothesis` vocabulary with typed, resolved, directional endpoints; existing TEL vocabulary retained. Dossier cards expose source record, source file/location, relationship ID/direction/status and candidate label. | New regression module: BNK, reversed edge, unrelated enterprise and actual retained package cases. Barclays has the supplied Copilot and security programme edges plus the supplied AI/cyber hypothesis. | Source associations do not create canonical Programme, Opportunity, Procurement or Watchpoint objects. Source timing in the existing Watchpoints view is explicitly labelled; no new object is generated. Unresolved endpoints remain unresolved. |
| F07 — financial context | `canonical_factual_projection` consumes preserved `financial_position` through the existing financial dimension and `latest_reporting` Evidence refs. Existing raw payload is retained by the Researcher adapter. Dossier financial context is labelled source narrative / candidate interpretation, not verified canonical financial facts. | Regression checks economic narrative and EV lineage; actual Barclays dossier shows its supplied economic model/current signal/reporting references. Empty other-enterprise dimension remains absent. | No numeric extraction, calculation or canonical model mutation. Shared Researcher profile and package versions remain unchanged. Unsupported Enterprise Economics is still not implemented. |
| F08 — report identity | Existing canonical alias owner `live/source_registry` explicitly maps Barclays / Barclays PLC to `barclays-plc`. Key-report subject matching applies owned aliases and rejects multiple dossier matches; producer-supplied aliases remain literal. Report qualification uses explicit primary subject, never publisher/title inference. | Barclays annual report `EV-BARCLAYS-AR2025`; missing, unknown, competitor, group, duplicate-alias and explicit producer-alias tests. | A shared report retains its primary parent subject. Child and competitor dossiers cannot adopt it as their own company report. Unresolved identities remain visible; this does not claim that a stored PDF was downloaded or its findings verified. |
| F09 — honest outcome | `review_plan.review_effect_counts` partitions staged accepted rows using existing persistence classes and planned effects. Review counts exclude non-persistable wrapper proposals from canonical Creates. Completion reads the approved plan and approval record and separates staging, owner approval, canonical execution, skipped/deferred classes, model projection and complete acceptance. | Corrected existing count regression, partition and blocking-mapping tests, actual package review/approval/subset-promotion cases. | A balanced partition does not remove conflict/unresolved gates. `succeeded` establishes execution of the approved subset only. Complete Industry Twin acceptance remains **Not established**. Missing approvals or plans are not invented. |
| F11 — navigation / false context | Industry completion opens `/blueprint-import/<run>/intelligence` and skips Enterprise Canvas access repair. Legitimate separately applied Enterprise Model links and Enterprise imports remain intact. Generic Canvas strategy/lens text does not name MOD. Receipt time is no longer material-change time; missing model state is candidate-only. | Industry/Enterprise completion, generic and MOD Canvas tests; retained package route checks and local browser navigation. | Existing MOD-specific reasoning remains guarded by actual MOD identity. Material change is Unknown unless supplied by the model owner. No model is invented for an Industry package identity. |

Read-model versions and the existing mapping version were incremented so existing
cached diagnostics can identify stale output; no restage or migration of production
intelligence was performed. Directory rendering requests only the relevant existing
research-requirement assessment and reuses it within that response. A regression
checks equality with the original filtered assessment. No caching layer was added.

## Ownership and assurance

The original ZIP is immutable input; staging repositories retain source/candidate
objects. Existing canonical promotion owns the persistable subset and requires its
existing plan approval. Repair 02 continues to own Observation-to-Enterprise Model
handoff. Industry dossiers are import-scoped views, not new durable models or
qualified Material Pressures. The dossier Opportunities anchor also now targets the actual Commercial Opportunities section, covered by retained tests and browser capture. The completion banner and class table make that
boundary explicit. Approval checks, promotion services, Evidence identity and
model repositories are reused without weakening their permission or acceptance
rules.

Accepted authorities remain unchanged: [ADR-002](../../../architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md),
[ADR-009](../../../architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md),
[ADR-012](../../../architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md),
[ADR-014](../../../architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md),
[ADR-024](../../../architecture/decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md),
[ADR-026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md).

## Retained package and regression evidence

See `Retained-Package-Evidence.json`, `Regression-Comparison.json` and
[rendered views / browser checks](rendered/README.md). Original TEL W5, TEL W6 and
BNK W1 bytes were hashed before and after isolated import/review/approval/subset
promotion. Identity decisions and approvals are explicit **isolated test fixtures**;
these results do not assert real-world owner acceptance or production data state.
No source ZIP or production intelligence was modified. External W6/BNK archives
are not republished in this PR.

The repeatable test module is `tests/test_flora_factory_presentation_repair.py`.
`run_regressions.py` uses a separate temporary data root and pytest base directory
per module. External artifacts are supplied through `FLORA_AUDIT_TEL_W6` and
`FLORA_AUDIT_BNK_W1`; missing archives yield explicit skips and available archives
must match the pinned hashes. `FLORA_REPAIR03_EVIDENCE` optionally exports actual
handler HTML, diagnostics and timings. The same new tests and corrected F09
assertion run against pinned main for the before comparison; the baseline source
implementation is unchanged.

| Isolated package | Staged accepted | Persistable staged | Non-persistable | Deferred canonical | Created / approved | Skipped | Ignored source rows | Model projection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TEL W5 | 648 | 441 | 207 | 308 | 133 / 133 | 515 | 412 | not_applicable |
| TEL W6 | 678 | 470 | 208 | 327 | 143 / 143 | 535 | 412 | not_applicable |
| BNK W1 | 584 | 530 | 54 | 430 | 100 / 100 | 484 | 229 | not_applicable |

For these fresh imports, accepted staged = created + skipped, and skipped =
non-persistable + deferred canonical. Support metadata and updated records are
zero. Ignored source rows are outside accepted staging; existing receipts include
them in `records_blocked`. They are disclosed separately and are not counted again
as skipped accepted candidates. Each package has zero failed execution records.
None establishes complete Industry Twin acceptance.

Local handler timings after the scoped-assessment change: overview 0.09–0.20s,
dossier 0.15–0.34s, directory 2.98–4.82s, programme aspect 0.63–0.80s, Evidence
0.59–2.55s in the recorded final-fixture run. Financial context is the same dossier
route, not a new service. Earlier same-worktree measurements before the scoped
assessment were 33.95–45.55s for the directory. These are single local samples under
concurrent test load, not production benchmarks or controlled statistical claims.
Browser navigation separately measured 3.92s/4.39s for BNK/TEL directory and
0.31s/0.45s for dossier. No new cache was introduced.

| Check | Pinned main | Repair 03 |
| --- | --- | --- |
| Distinct cases across 36 relevant modules, including final focused/contract reruns | 484 passed / 37 failed | 500 passed / 21 failed |
| New Repair 03 module, all retained packages supplied | 8 passed / 15 failed | 23 passed |
| Final focused module group after anchor correction | Baseline cases included above | 63 passed |
| Shared profile + portable import contract | Baseline cases included above | 17 passed |
| Existing Repair 01 Evidence identity / release suite | 41 passed | 41 passed |
| Existing Repair 02 Researcher-to-model suite | 32 passed | 32 passed |

The exact-ID comparison shows **16 corrected failures, 21 remaining pre-existing
failures and zero new failing test IDs**; both sides contain the same 521 cases,
with no missing IDs or skips. Fifteen fixes are exposed by the new module; one is
the existing F09 count assertion corrected to separate staged and canonical
acceptance. The baseline implementation is unchanged; that assertion is
intentionally stricter, not a weakening of a failing expectation.

The 21 inherited failures comprise TEL package/presentation expectations (5),
legacy BNK reinvention expectations/artifact availability (6), executive review (2),
restage (2), import interface (2), Enterprise Canvas/landing expectations (3) and
TMS diagnostics (1). Exact test IDs and before/after failure messages are retained
in `Regression-Comparison.json`. Examples include an old v2 factual-projection
expectation against baseline v5, missing landing/review labels and the MOD brief
availability gate. This increment does not claim to resolve them or to certify
all existing product behavior.

Both broad runner invocations exit 1 because of explicit failures; final focused
and contract commands exit 0. The baseline-only final new-module rerun exits 1
(15 failed / 8 passed), reproducing the same defects. Final Python compilation
and diff whitespace checks pass. During development a temporary shared-profile
edit caused checksum/version failures; the edit was removed and unchanged-profile
checks reran successfully. The browser-discovered missing Opportunities anchor
was corrected and the final focused tests rerun. See [commands and environment](Test-Commands.md).


## Remaining limitations and smallest follow-up

1. Complete Industry Twin acceptance has no supplied owner-level result. Non-persistable
   domain wrappers and deferred canonical candidates remain candidate intelligence;
   this increment discloses that boundary rather than automatically promoting them.
2. Existing BNK overview still offers legacy Telecoms/Media/Sport filters. The All
   Twin route and enterprise directory work, but these inherited domain filters
   need a separately reviewed contextual presentation repair. No new banking
   research or guessed industry taxonomy was introduced.
3. Financial content is narrative context, not a financial facts service or economic
   exposure model. Report subject resolution does not establish verified report
   findings or downloaded document contents. Unmapped/unsupported dimensions and
   absent identity remain explicit.
4. Existing inherited test failures are listed separately in the comparison. They
   are not evidence that the whole repository or product is green. This was a
   focused integration corpus, not every repository test.
5. Browser validation uses local existing routes over isolated retained-package
   storage, with explicit development test headers. Completion HTML is the actual
   saved approval POST response; its destination is then followed locally. No
   production upload, approval, promotion, migration, deployment or real owner
   acceptance was performed. New deployed behavior is **NOT TESTED** until this
   PR is reviewed, merged and deployed through the normal process.

Review these minimal corrections first; then address contextual filters and the
separately documented baseline failures. Any broader model acceptance capability,
continuous intelligence, economic reasoning or Navigator work needs a separate
approved increment. Work stops after Repair 03 publication.
