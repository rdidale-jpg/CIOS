# Increment 04 completion report

Baseline: **ec0bd875ab2a780ff1551dcb2a239aa8a76eb402**, latest GitHub main,
including merged PRs #530, #531 and #532. Verified before implementation and again
before publication. Results below concern the review branch, not deployment.
The accompanying PR is delivered open and unmerged.

## Architecture gate and ownership

Phase A concluded that this bounded implementation fits existing owners; a new
accepted architectural decision is unnecessary for transient interpretation.
[Architecture-and-Ownership.md](Architecture-and-Ownership.md) records the
pre-code review, canonical boundary map, authority/status discrepancies, source
contracts and implementation limits. No accepted ADR was modified. The proposed
broader hybrid operating direction has not been promoted into accepted architecture.

Canonical Evidence remains in EvidenceRepository. Enterprise applicability and
consequence remain supported by canonical enterprise Observations and their own
Evidence. Existing promoted entity/relationship rows identify candidates via the
existing semantic relationship resolver. Industry/sector membership never proves
exposure, a security incident at an enterprise, a material consequence or commercial
intent. IT-001 remains Review; this work does not create an Industry Twin owner.

The new result is a transient `derived_runtime_assessment` in the existing
Enterprise Intelligence boundary. It has stable identity, qualification, explanation,
Evidence roles, uncertainty, evidence demands and exact existing model/pressure
dependencies. It is not a new canonical object, durable memory or change-event
repository. No Model update is performed, including after a successful ADR-026
qualification preview.

## Implemented changes and traceability

All runtime paths below are under `cios/applications/flora/`.

| Change | Existing service reused / code | Regression evidence | Limit / next boundary |
| --- | --- | --- | --- |
| Governed external context | `enterprise_intelligence/change_interpretation.py::assess`; EvidenceRepository; shared ADR-026 acceptance/source-clause helpers | Missing, rejected, expired, future, unsupported, missing-descriptor and staged-only inputs fail | Source must already be accepted and explicitly annotated. No acquisition or canonical acceptance is added. |
| Candidate identification | `_candidates`; existing CanonicalJsonlRepository entity/relationship owners; `semantic_twin.resolve_relationships`; existing enterprise identity normalization | Resolvable Evidence-backed direct links succeed; missing endpoints, rejected relationship Evidence, indirect and name-only association fail; target access scope filters results | One-hop canonical links only; no transitive industry/group/supplier propagation or fuzzy alias graph. Caller supplies authorized enterprise scope; no new public endpoint bypasses existing route access checks. |
| Differentiated interpretation | `_support` and `assess` bind event/time, enterprise-specific basis, mechanism, mitigation and consequence to accepted enterprise Evidence | Aviation, Banking and cyber cases; wrong-enterprise/industry/unsupported support; confidence, dates, supersession and period disagreements | Deterministic validation of governed semantic annotations, not autonomous economic/semantic inference. Direct clause checks can reject valid paraphrased explanations. |
| Uncertainty and conflict | Existing Observation lifecycle, ContradictionRepository and Unknown owners; canonical conflicts can be found by supporting Evidence without duplicate annotation links | Opposing applicability, canonical consequence conflict, external conflict, missing counter-Evidence, unresolved/non-core Unknowns, resolved historical links | Open Unknowns on core support keep applicability incomplete. Conflicts are unresolved; no preferred source is silently selected. Canonical non-core contradiction distinctions are conservative in this interpreter. |
| Reassessment boundary | Existing Enterprise Model attributes/pressure lineage; existing ADR-026 `qualify_candidates` | Exact dependency targets and successful ADR-026 preview; full model snapshot unchanged; lost Evidence blocks preview | Targets and previews are requests/diagnostics, not writes or queued work. Actual pressure writes remain with accepted Observation application / `ObservationMemoryService.assess_material_pressure`. |
| Existing read models | `enterprise_intelligence/retrieval.py` adds requested-enterprise diagnostics to `EvidencePackageV1.enterprise_context`; `memory/views.py` appends an optional panel | Requested-enterprise isolation, qualification/lineage/demand rendering, no external Observation selected | No new route, page, dashboard, store or Navigator. External context remains labelled context, outside canonical enterprise Observation items. |
| Replay and boundaries | Read-only result with stable event-Evidence/enterprise/time ID; no repository save calls | Identical replay equal; complete canonical file snapshot unchanged; no new event/commercial store or source Observation | No durable assessment history is introduced. Existing reasoning audit may retain an Evidence package when the existing runtime is explicitly invoked. |

Only three runtime files are added/changed: the bounded interpreter, its existing
retrieval integration, and the existing Enterprise Memory view. No accepted
validator, canonical repository, importer or schema was changed. No agent
framework, scheduler, domain calculations, opportunity engine or backfill was added.

## Cross-industry golden path

[Test source](../../../tests/test_flora_external_change_interpretation.py) contains
42 isolated cases, including parameter variants. All input enterprises, sources,
relationships and claims are synthetic. Tests use temporary data roots and never
create real easyJet intelligence or alter canonical production data.

| Requirement | Demonstrated result and test |
| --- | --- |
| A — Aviation | A 15% jet-fuel benchmark development identifies two airlines through governed links. One has evidenced unhedged exposure, partial mitigation and constrained operating margin; the other has evidenced broad hedging and no established consequence. Results differ: APPLICABLE_WITH_EVIDENCED_CONSEQUENCE vs POTENTIALLY_APPLICABLE with an evidence demand. No net financial impact calculation. `aviation_distinguishes_exposure_mitigation_and_consequence`. |
| B — Banking | The same runtime contract distinguishes deposit repricing/funding flexibility from delayed fixed-asset repricing. No banking formula or rule exists in generic code. `banking_uses_same_contract_without_sector_calculations`. |
| C — Cyber/hybrid | Sector-related enterprises remain candidates with explicit exposure/consequence demands. Sector incident Evidence does not assert an enterprise incident. `sector_security_incident_does_not_imply_enterprise_incident`. |
| D — Unaffected | An unrelated enterprise is excluded. Every canonical file is byte-for-byte unchanged after interpretation. Explicitly evidenced non-applicability is distinct from missing evidence. `unrelated_enterprise_and_all_canonical_state_remain_unchanged`, `explicit_evidenced_non_applicability`. |
| E — Contradiction | Opposing same-period applicability claims, canonical consequence conflict and external context conflict return UNRESOLVED with both lineage paths/demands. Canonical conflicts are detected without redundant annotation references. Missing counter-Evidence is explicit. Relevant `opposing_same_period_*`, `canonical_consequence_conflict`, `external_canonical_conflict`, `existing_canonical_conflict_*` tests. |
| F — Replay | Repeated identical Evidence returns the same assessment IDs/content, with no duplicate result or canonical change. `replay_has_stable_assessment_id_and_no_duplicate_result`. |
| G — Pressure | Only separately supported enterprise consequence and accepted enterprise source can enter the read-only ADR-026 preview. All six gates are checked; the existing pressure remains unchanged. Removing source support blocks preview. `pressure_preview_reuses_adr026_and_never_mutates_model`. |
| H — Commercial | No Opportunity, Procurement, Programme, Watchpoint, contract value or buying intent is generated. External Evidence creates no enterprise Observation or pressure. Entire canonical snapshots are unchanged. `read_only_interpretation_creates_no_new_commercial_or_event_store`, `external_only_event_never_creates_observation_or_pressure`. |

The approved import test exercises actual package validation, review, planning,
approval and canonical promotion before interpretation. It reaches the same
read-model boundary without a special import class or bypass. Temporal and
lifecycle tests reject unsupported current support while retaining source records.

## Before/after results and commands

[Regression-Results.json](Regression-Results.json) records the exact existing
module outcomes and pre-existing failure identifiers. The original checkout
remained clean. No live provider, real research collection, production service,
production database or migration was used.

| Verification | Main baseline | Increment 04 branch |
| --- | --- | --- |
| Same 42 new tests | 42 failed | 42 passed |
| 18 relevant existing modules | 245 passed, 13 failed | 245 passed, same 13 failed |
| Final focused new + Material Pressure + Evidence applicability + import reconciliation | Not run as a separate combined baseline command | 132 passed |
| Whitespace/diff check | — | `git diff --check` passes |

The new tests fail on baseline because the capability is absent (including missing
module/read-model fields); they do not represent 42 separate historical assurance
incidents. Existing tests were not rewritten to mask behavior. The five failures
already documented in Increment 03 remain, plus eight failures exposed by broader
Industry/relationship coverage. No new failures appear in the compared modules. No unrelated fixes are included.

The 13 baseline failures comprise three Canvas route/text assertions, one runtime
proof expected-change label, one legacy inventory assertion, two TEL-001 dimension/
diagnostics assertions, and six Banking reinvention presentation/narrative/
reconciliation/artifact assertions. Full test identifiers are retained in the JSON.
The TEL-001 relationship/rendering module takes approximately five minutes on both
sides; it is executed to completion, not silently skipped or treated as a timeout.

Commands use the existing `/workspace/cios-venv/bin/python` environment and
`PYTHONPATH=.`. Each module runs in a separate process with a new
`FLORA_DATA_DIR` / `FLORA_PILOT_DIR`; fixtures further isolate data with `tmp_path`.
The new tests are copied unchanged into a detached worktree of the exact baseline.

```bash
FLORA_DATA_DIR="$scratch" FLORA_PILOT_DIR="$scratch" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q tests/test_flora_external_change_interpretation.py
FLORA_DATA_DIR="$scratch" FLORA_PILOT_DIR="$scratch" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q \
  tests/test_flora_external_change_interpretation.py \
  tests/test_flora_material_pressure_lifecycle.py \
  tests/test_evidence_provenance_applicability.py \
  tests/test_flora_import_model_reconciliation.py
git diff --check
```

For each existing filename in the JSON, the comparison runs `python -m pytest -q
 tests/<filename>` separately with fresh scratch roots. The full repository suite,
browser/live-provider integration and deployment tests were not run. Remote CI is
separate from these local results; no deployment or CI success is asserted here.

## Remaining limitations and future model

[Future-Operating-Model.md](Future-Operating-Model.md) distinguishes reusable
implemented components from proposed monitoring, scheduled research, event-driven
reassessment, evidence-demand research, Industry/Enterprise Twin refresh,
commercial hypothesis reassessment, Navigator updates and human feedback.

Governed annotation supplies semantic meaning. This increment validates it against
source clauses and scope; it neither discovers every latent exposure mechanism nor
proves arbitrary natural-language entailment. Canonical typed enterprise identities
and exact relationship endpoints are required. A missing graph link is an evidence
demand, not proof that an enterprise is unaffected. No transitive propagation occurs.

Results are transient and read-only. There is no durable external-event history,
assessment ledger, automated research dispatch, automatic model/pressure update or
commercial hypothesis promotion. Existing accepted owner paths remain the only
write paths. Current-state data is revalidated at the requested cutoff; this does
not reconstruct a complete historical Industry or Enterprise Twin state.

The output bounds are 50 candidate enterprises per explicit batch and 20 external
assessments in an enterprise read model. File-backed owners are scanned; no indexing
or background cache was introduced. Reassessing broad portfolios or enabling
unattended orchestration is future work requiring authorization. This branch is
reviewable implementation, not proof of a continuous production intelligence loop.

Stop after Increment 04. No monitoring, scheduling, economic modelling, commercial
reassessment or Navigator generation was begun.
