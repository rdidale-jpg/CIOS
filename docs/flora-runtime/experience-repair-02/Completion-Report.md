# Flora Experience Reconciliation Repair 02 — completion report

Implemented a shared, read-only discovery projection on Home, Intelligence and
Digital Twins. Curated Banking, imported Industry workspaces and authorised
existing Enterprise Canvas views now appear with separate authority, identity,
status, current-release state, availability and destination. The shadowed Banking
inspection alias is repaired. This completes the bounded local implementation;
publication/CI status is reported separately with the PR.

Baseline main was verified before implementation and rechecked before publication:
`acaf99cd26c5faf7719cf0fbda48edef6bc97c59`, including merged #530–#537.
The preimplementation [Discovery Contract](Discovery-Contract.md) records the
ownership assessment and route defect. This increment addresses audit F02/F03
(fragmented discovery) and F07 (shadowed alias), without treating presentation
convergence as canonical convergence.

## Changes and preserved boundaries

- [digital_twins.py](../../../cios/applications/flora/digital_twins.py): minimal
  immutable in-memory projection and shared existing-card renderer. Reuses
  BlueprintPackageRegistry, explicit governed identity projection, candidate
  summary, review acknowledgement, receipt-backed lifecycle, Enterprise Model
  repository and existing Canvas ACL/visibility. The old Canvas-list API remains
  available for compatibility. No directory indexing, identity store or new
  lifecycle enum is introduced.
- [web/app.py](../../../cios/applications/flora/web/app.py): all three entry
  routes consume the same projection; existing permission-filtered import metrics
  consume the same snapshot. Banking inspection alias is dispatched before the
  Banking catch-all, using the existing Industry inspection adapter.
- [blueprint_import/views.py](../../../cios/applications/flora/blueprint_import/views.py):
  Industry intake breadcrumb targets its actual workspace rather than treating
  an Industry identity as an Enterprise Canvas. Enterprise imports retain their
  existing destination.
- [executive_workspace.py](../../../cios/applications/flora/blueprint_import/executive_workspace.py)
  and [banking_portfolio.py](../../../cios/applications/flora/banking_portfolio.py):
  return navigation to the shared Intelligence entry point.

Permission checks run before discovery item names, identifiers, counts and URLs
are constructed. Explicit workspace-bound records must match the active workspace
as well as existing owner ACLs, including under wildcard enterprise grants.
Anonymous readers see public curated context only. Empty results do not reveal
whether protected intelligence exists. Unreadable owner state is generic
Unavailable; a mismatched model payload is withheld without a cross-identity URL.

Import receipt, source package, import run, governed Twin, primary subject,
presentation context and canonical Enterprise identities remain separately
labelled. No fuzzy name/ZIP matching or automatic Canvas registration occurs.
Received/reviewed packages remain Candidate/Under review. Owner promotion is
labelled Partially promoted, never complete Industry acceptance. Historical
releases remain inspectable, current No. Model-backed explicitly does not assert
complete Commercial Digital Twin assurance. Source Unknowns/Contradictions and
Evidence stay in existing workspaces; open model Unknowns are also shown.

Meaningful update is Unknown unless an explicit current model attribute supplies
it. Receipt/access timestamps are not substitutes. Future/retired attribute dates
are excluded; lifecycle/review events, model observations and curated snapshot
are separately labelled. No save, promotion, access repair or side-effecting
Canvas service method is called during discovery.

## Acceptance and tests

[Acceptance Matrix](Acceptance-Matrix.md) maps request cases A–M to regressions,
retained package tests and browser evidence. New regressions are in
[test_flora_experience_discovery_repair.py](../../../tests/test_flora_experience_discovery_repair.py).
All original tests remain unchanged.

| Exact-case comparison across 26 relevant modules | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Pinned main, including the 27 added regression cases | 387 | 49 | 0 |
| Repair 02 | 414 | 22 | 0 |

All 27 added cases fail against pinned main and pass after the repair. There are
no newly failing original cases. [Regression-Comparison.json](Regression-Comparison.json)
contains exact case IDs and both inherited failure messages; it compares the same
436 case IDs, with final reruns replacing preliminary results by exact ID.
The existing corpus alone remains 387 passed / 22 failed. The inherited failures
are Banking portfolio increment 3 (7), executive navigation 44 (4), visual 45 (1),
visual 451 (1), reinvention 42 (6), and Enterprise Canvas (3). These include older
presentation/assurance expectations and were not altered to obtain a green run.

Focused final command: `python -m pytest -q tests/test_flora_experience_discovery_repair.py tests/test_flora_experience_assurance_repair.py tests/test_flora_enterprise_canvas.py --basetemp=<isolated-final-root> --junitxml=<final-focused.xml>`:
**70 passed, 3 inherited Canvas failures**, 89.66 seconds. Broad runs use
[run_regressions.py](run_regressions.py), one isolated root per module. Factory
Repairs 01/02/03 pass 41/32/23 cases respectively; Experience Repair 01 passes 31.
Existing integrity and Material Pressure suites pass 44 and 51 cases respectively.

Actual retained BNK W1, TEL W5 and TEL W6 pass the existing Factory journeys and
the generic discovery checks, with hash-pinned original bytes. The BNK historical
state is an explicitly synthetic owner lifecycle transition over retained source
content; no actual successor package acceptance is claimed. Model/Canvas,
ambiguous identity and permission-negative records are synthetic fixtures.

## Browser evidence

Local Chromium: desktop 1440×1050 and iPad portrait 1024×1366 with touch/mobile
emulation. Pinned-main comparison uses identical isolated fixture bytes.
[Browser-Results.json](Browser-Results.json) records routes, audiences, viewports
and visible checks: before **20 observations / 148 checks, 20 observations fail**;
after **36 observations / 200 checks, all pass**. This is not a claim that all
148 baseline checks failed; each baseline observation fails one or more checks.

Visible checks cover authority/status, distinct typed entries, actual links,
owner/wrong-workspace/anonymous views, empty and historical state, alias parity,
no horizontal overflow, dossier/Evidence clicks and existing Canvas clicks.
All four entire fixture-store fingerprints are byte-identical before and after
browser journeys. The browser harness redirects the pre-existing Banking derived
pipeline output outside owner stores. This is test isolation, not a runtime
behaviour change.

Representative screenshots:
[before iPad](screenshots/before-ipad-directory.png),
[desktop Home](screenshots/desktop-home.png),
[iPad discovery](screenshots/ipad-discovery.png),
[historical release](screenshots/ipad-historical.png),
[wrong workspace](screenshots/ipad-wrong-workspace.png),
[dossier](screenshots/ipad-dossier.png),
[Evidence](screenshots/ipad-evidence.png).
Reproduction instructions are in [Testing.md](Testing.md). Raw XML, complete
screenshots, local route text and isolated roots are retained in the execution
workspace under `/workspace/work/flora-experience-repair-02-evidence`; package
archives and owner stores are not added to this change.

## Remaining limitations

- Discovery enumerates existing authorised Canvas access records. Persisted models
  without such records are intentionally not indexed or automatically registered.
  An authorised existing Canvas with no persisted model says Unavailable; its
  existing incomplete Canvas view remains accessible.
- Legacy unscoped access records retain existing owner checks; no workspace is
  inferred or migrated. Broader destination authorisation mechanisms are reused;
  this change does not claim a system-wide authorisation redesign.
- Import intelligence effective dates remain Unknown when the owner does not
  supply them. Partial promotion, existing model presence and receipt success do
  not prove full Twin assurance. Identity ambiguity is exposed, not resolved by
  guessing. Source and model Unknowns retain their owners.
- The 22 inherited test failures remain. No claim of an entirely green repository
  or full production Industry Twin acceptance is made.
- Deployment verification: **NOT TESTED**. The managed environment's network
  proxy rejects access to the Render origin; no deployment was performed.
  Physical iPad and Safari were not tested; Chromium viewport emulation was.
- No accepted ADR, canonical intelligence, production data, identity authority,
  canonical Banking adapter, scheduler, economic engine, opportunity/procurement
  workflow or four-slide Navigator was changed. No migration or backfill ran.
  ADR-014/024's pre-existing header/body status ambiguity remains documented.

Stop after Repair 02. No subsequent increment has been started.
