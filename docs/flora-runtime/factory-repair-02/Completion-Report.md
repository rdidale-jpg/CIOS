# Flora Industry Twin Factory Repair 02 — completion report

8 November 2026. Baseline main: `327fb506d46fda1ba981ed0aa1ff85a4c56486e5`
(merged #530–#534), independently verified through GitHub and `git fetch` /
`git ls-remote`. No production intelligence, accepted ADR, deployment, migration,
backfill, scheduler, canonical store or model owner was changed by this repair.

## A. Producer-to-model contract assessment

The [assessment recorded before implementation](Producer-to-Model-Assessment.md)
traces the F04/F05 boundaries. The retained Researcher packages provide six TEL
Enterprise Dossiers in each release and eleven Banking dossiers. They contain no
canonical typed Observations. Nested financial strings often combine facts,
comparators and interpretation; leadership names are not always asserted by their
retained source summaries. A dossier is not proof of canonical truth or ownership.

The minimal supported handoff is **an existing producer-written
Evidence.supported_claim, explicitly linked in a dossier's evidence list**, with
complete source/collection dates and an owner-confirmed target enterprise and
supported event/leadership attribute. The assertion is used verbatim. There is no
prose extraction, sentence splitting, numeric inference, new reasoning engine or
automatic classification of commercial hypotheses. Scalar dossier fields without
explicit supporting statements remain candidates, not manufactured Observations.

Authorities remain accepted ADR-002/009/012/014/024/026 under
`architecture/decisions/`. Existing `BlueprintManifest`, `CandidateImportRecord`,
`Observation`, `EnterpriseModelRepository`, mapping and review records are reused.
No accepted authority or producer profile schema was amended. The importer mapping
version advances to `mod-cdt-twin-spine-mapping-v1.3.5`, making older cached reviews
stale rather than reusing an unsafe graph plan.

## B. Minimal integration changes and owners

| Boundary | Existing owner/location | Change and evidence | Limit/consequence |
| --- | --- | --- | --- |
| Researcher claims -> review offers | `blueprint_import/researcher_profile_adapter.py: handoff_offers` | Enumerates explicit dossier Evidence links, preserving source text and deferral reasons; existing atomicity and Observation constructors validate offers. | Offers require owner review; they are not accepted facts. Unknown dates, explicit unverified/expired/contradictory sources, compound or speculative claims are deferred. |
| Explicit enterprise handoff | Same existing adapter, `stage_observation_handoff`; existing staging/mapping/review/ledger repositories | Owner must have package and target-enterprise promotion authority and give a rationale. The dossier is explicitly mapped to a canonical Enterprise ID. Fresh staged Evidence receives the confirmed enterprise owner; raw source_payload and ZIP bytes remain unchanged. A typed Observation is staged with a separate deferred review decision. | Only an active, unaccepted import. Accepted Evidence under another owner cannot be moved or copied by this adapter. Sources shared across enterprise owners cannot be silently reused under a new identity. |
| Canonical acceptance | `promotion.py`, existing CanonicalPromotionService and PR #531 projection | Approval/execution recheck the handoff source, dates, identity mapping, Evidence snapshot and complete staged-candidate fingerprint. All supporting IDs resolve through PR #534 approved mappings. Existing projection invokes ObservationMemoryService / EnterpriseModelRepository. | Selection and staging make no canonical write. A distinct Observation review and owner promotion are required. Partial staging failure cannot acquire an automatic Observation approval. |
| Replay/history | Existing stable Observation identity, repositories, Evidence release provenance and receipts | Package version alone does not change Observation identity. Identical release/replay retains one Observation and unchanged model confidence history. Reviewed changed source preserves prior Evidence and old Observation, including explicit supersession. | Different content requires an explicit Evidence update decision; no semantic deduplication or guessed supersession. |
| Canonical graph | `semantic_twin.py: canonical_relationship_endpoints`, `planning.py`, `promotion.py` | Candidate aliases resolve only to existing owned canonical objects or approved planned objects. Model owners can be endpoints after explicit Enterprise mapping and approved Observation projection. Inaccessible/unowned endpoints fail. Unresolved edges are deferred in plans and rechecked before writes. | A readable dossier/programme/opportunity/supplier wrapper is not a canonical endpoint. Raw candidate graph remains inspectable. Existing production edges are not migrated or cleaned up. |
| Operator and consumers | Existing `views.py` / `web/app.py`, bounded retrieval, Enterprise Canvas | Review has handoff and separate Observation decision actions, explicit selected-subset deferral and counts. Completion links applied target Enterprise Models. Existing bounded retrieval and Canvas detail consume accepted model state, separate from candidate Industry dossiers. | No new dashboard/Navigator or Banking presentation repair. The detail view is proved; complete Industry executive rendering is not claimed. |

Files above are under `cios/applications/flora/`.
`tests/test_flora_factory_researcher_model_repair.py` provides focused evidence for
each boundary, plus the existing import/memory/pressure/integrity suites.

Publication and collection dates are taken from the source as supplied. Source
publication is explicitly labelled as the observation/source date, without
inventing event-effective timing. Explicit effective date, source confidence,
uncertainty and wrapper Unknown/Contradiction context are retained in existing
Observation provenance. Future effective dates are not accepted as current support.
Historical retrieval uses the existing cut-off rules. Context links do not promote
Unknowns or treat every dossier contradiction as a contradiction of the selected fact.

## C. Retained package acceptance matrix

| Package | Enterprise wrappers | Linked claim candidates | Structurally reviewable | Structurally deferred | Reviewable but unselected | Approved Observations | Model attributes | Resolved Evidence refs | Retrieval Obs / Evidence | View-visible facts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TEL-W5 | 6 | 28 | 4 | 24 | 3 | 1 | 1 | 1 | 1 / 1 | 1 |
| TEL-W6 | 6 | 40 | 4 | 36 | 3 | 1 | 1 | 1 | 1 / 1 | 1 |
| BNK-W1 | 11 | 50 | 12 | 38 | 11 | 1 | 1 | 1 | 1 / 1 | 1 |

These are isolated, explicitly authorised test decisions, not production business
acceptance or independent verification of the underlying public sources. TEL uses
`EV-VT-OWN-COMPLETE26` linked from `ENT-VODAFONETHREE`; BNK uses
`EV-BARCLAYS-MICROSOFT-COPILOT-2025` linked from `ENT-BARCLAYS`. The exact original
supported_claim becomes the Observation. All other package records are explicitly
deferred in the selected-subset workflow and retained as candidates.

The canonical target is explicitly confirmed from the source dossier mapping.
Before promotion, canonical Evidence, Observations and target model attributes are
absent. After separate review and promotion, each selected fact has one canonical
Evidence reference, one Observation, one model attribute, bounded retrieval support,
and an existing model-backed Canvas detail view. No programme, opportunity,
procurement or Material Pressure is manufactured. Re-import/update history is tested
with isolated synthetic releases; the actual TEL W5/W6 selected source is unchanged.

Hashes (the original archives were not edited):

| Artifact | SHA-256 |
| --- | --- |
| TEL W5, repository corrected Flora import ZIP | `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07` |
| TEL W6, supplied targeted enrichment corrected ZIP | `c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb` |
| BNK W1, supplied manifest-compatible ZIP | `1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313` |

Counts are linked-claim occurrences, not independently verified facts or arbitrary
completeness percentages. Reviewable but unselected claims remain deferred by the
owner; structurally eligible does not mean accepted. NRG was not supplied or tested.

## D. Canonical graph reconciliation findings

| Package | Source relationships | Resolved canonical edges in selected subset | Deferred ungoverned source edges before subset selection |
| --- | --- | --- | --- |
| TEL-W5 | 308 | 0 | 308 |
| TEL-W6 | 327 | 0 | 327 |
| BNK-W1 | 430 | 0 | 430 |

Unresolved examples/classes are recorded in [retained-package diagnostics](Retained-Package-Evidence.json). Enterprise dossiers, opportunity hypotheses, programmes and market participants remain candidate endpoints until their existing owners establish canonical objects. No wrapper is promoted to close these edges.

The synthetic positive tests prove owned canonical Entity endpoints and explicit
Enterprise mapping to a planned model owner. The negative tests prove that missing,
wrong-access and domain-wrapper endpoints do not create canonical relationships.
The retained selected-subset path approves zero relationships. This demonstrates a
safe partial graph, not a complete Industry graph. Pre-existing accepted dangling
edges are untouched: any production repair/backfill requires separate approval.

## E. Before/after tests

| Selected tests | Baseline | Repaired |
| --- | --- | --- |
| 439 existing cases (30 modules, including Repair 01) | 419 passed / 20 failed | 419 passed / the same 20 failed |
| 32 Repair 02 cases | 2 passed / 30 failed | 32 passed |
| Combined | 421 passed / 50 failed | 451 passed / 20 pre-existing failures |

No new regressions, errors or skipped retained-package tests. The Repair 02 result
combines 31 full-module cases with the separately run legacy-lineage endpoint case
on both baseline and repair. The current focused promotion/model/handoff supplement
also passed 83 cases (the retained cases ran separately). Syntax compilation and
`git diff --check` passed. [Machine-readable results](Regression-Comparison.json)
contain exact per-module summaries and failing names. Expected baseline failures
reflect missing handoff/graph safeguards; they are not 30 distinct production defects.

Pre-existing failures: TEL package regression (4), TEL factual presentation (1),
Banking industry reinvention executive/presentation checks (6), executive review
copy/context checks (2), restage expectations (2), import interface expectations
(2), and Enterprise Canvas legacy expectations (3). They remain unchanged; no
Banking presentation or unrelated assertions were weakened.

Actual W5 followed by W6 additionally proves **one Observation, one Evidence row,
one model attribute, two Evidence release provenance entries, unchanged model and
confidence history, W5 superseded and W6 current**. Same-package UI replay is also
unchanged. This is a selected-fact path, not complete package acceptance.

The valid comparison roots are `/workspace/work/factory-repair-02-evidence/before`
and `after`; retained diagnostics/rendered HTML are in `final-retained`.

Identical new fixtures and actual package bytes are used against the pinned baseline
and repaired code, with one isolated process and temporary data root per module.
Two existing positive relationship fixtures now supply governed endpoints instead of
invented/missing endpoints; those corrected fixtures are copied identically into
the baseline checkout. Their citation/persistence assertions remain intact. New
negative tests separately assert deferral of dangling endpoints. No unrelated
Banking or presentation assertion was changed.

Reproduction (from each checkout using its test interpreter):

```bash
export FLORA_AUDIT_TEL_W6=/path/to/retained/TEL-W6.zip
export FLORA_AUDIT_BNK_W1=/path/to/retained/BNK-W1.zip
export FLORA_REPAIR02_EVIDENCE=/tmp/flora-repair-02-retained
python docs/flora-runtime/factory-repair-02/run_regressions.py --output /tmp/flora-repair-02-tests
python -m pytest -q tests/test_flora_factory_researcher_model_repair.py
```

For baseline, use a detached checkout at the SHA above and copy the new test module,
the two corrected positive test fixtures and the harness into it. Source code remains
at baseline. The harness records full logs, JUnit XML, commands and JSON summaries.
External retained packages are optional locally but hash-pinned; unavailable ones
skip explicitly. The reported acceptance run supplies all three actual packages.
The interpreter was `/workspace/cios-venv/bin/python`.

Local Chromium additionally rendered the accepted TEL Canvas detail and verified
Core facts plus source lineage. This rendered saved HTML from the actual view
handler, not the live deployment or an HTTP/browser import journey. The test venv
lacked Playwright; the existing system interpreter and `/usr/bin/chromium` were
used. Managed Chrome blocks file URLs, so the authorised, locally generated HTML
was rendered with `page.set_content`. No external research or browser policy change
was performed. Deployment and external provider execution remain NOT TESTED.

## Publication status

Implementation, isolated testing and local review artefacts are complete. GitHub PR
publication is pending explicit user authorization. Automatic approval review twice
rejected source-file publication: initially for unverified destination/authorization,
and then, after repository identity and push permission were verified, because a
trusted user message must explicitly authorize publishing the new changes to public
`rdidale-jpg/CIOS`. No PR or remote branch for Repair 02 was created. No alternate
publishing method was used to bypass the rejection. A local commit and patch make
the exact proposed change reviewable before that approval.

## F. Remaining limitations and minimum next actions

- This is a deliberately selected handoff, not wholesale dossier-to-model
  conversion. Compound financial strings, unsupported names, recommendations,
  supplier/procurement hypotheses and ambiguous dates still need a better producer
  handoff contract or additional evidence. No fact is inferred to fill those gaps.
- Owner mapping confirms enterprise identity for the selected import. It does not
  create/promote a dossier wrapper, legal-entity registry or new identity authority.
  Already promoted industry-owned Evidence is not reassigned or duplicated here.
- Selected-subset mode explicitly defers all other records. Operators must make
  additional review decisions to accept more than that subset. Complete Industry
  Twin acceptance, canonical graph completeness and Banking dossier usability are
  not established by one accepted fact per package.
- Staging is an inspectable review workspace, not a new transaction engine. A
  staging I/O failure can leave partial review artefacts; defaults keep derived
  Observations deferred, stale approval fingerprints fail, and canonical memory
  stays unchanged. Existing promotion compensation and manual crash-recovery
  limitations from Repair 01 remain.
- The current model-backed detail view displays the fact and existing governance,
  date and lineage labels. Broader executive narratives, all source context fields,
  commercial interpretation, provider briefs and production deployment are not
  certified by these tests.

Review this bounded PR and its evidence before any merge/deployment decision.
Production backfill, further producer-contract work or later product repairs require
separate approval. Work stops after Factory Repair 02: no Banking dossier repair,
monitoring, economics or Navigator development has begun.
