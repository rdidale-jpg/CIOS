# Increment 03 completion report

Implemented for review on baseline **096c9832df3b67a0970a3a0e1681133110b075a1**,
verified against GitHub main before implementation and again before publication.
PR #530 and PR #531 are merged in that baseline. This report describes tested
branch behavior, not a production deployment. The accompanying PR is open and
unmerged when delivered.

## Contract conformance and ownership

The pre-code assessment and canonical ownership design are in
[Contract-and-Ownership.md](Contract-and-Ownership.md). Accepted authorities remain
[ADR-026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md)
and ADR-002/009/014/024. EI-001, EI-012 and EI-004 remain Draft; their intended
ownership/reasoning models are not treated as proof of implemented runtime.
No accepted ADR was edited.

| Boundary | Implementation and proof | Limitation / consequence |
| --- | --- | --- |
| Governed input | `blueprint_import/material_pressure.py::qualify_candidates` resolves canonical Observations/facts and Evidence; rejects unavailable, rejected, quarantined, retired, expired, future and superseded support. Tests `missing_evidence`, `ineligible_*`, `superseded_observation_relation`. | Legacy source labels alone do not authorize a pressure. Staged Twin candidates now fail gate 1 explicitly. |
| Enterprise applicability | Canonical enterprise identities on source, supporting Observations and Evidence must match. Tests `industry_or_other_enterprise_evidence`. | Direct scoped applicability only; no implicit industry, group or subsidiary propagation. |
| Pressure semantics | Accepted descriptor binds condition/mechanism to direct Evidence clauses; a causal explanation is required. Tests `caller_cannot_assert_semantics`, `numeric_metric_alone`, `governed_negative_gate`. | Conservative validation needs governed annotation and direct source clauses; does not perform autonomous entailment. |
| Stable identity | Enterprise + governed concept + domain + scope + time; supported semantic rationale, explicit ambiguity/distinction/replacement handling. Tests `paraphrases`, `distinct_supported_conditions`, `uncertain_equivalence`, `source_identity_mutation`. | Semantic concept governance is required; unknown equivalence stays unresolved. No fuzzy or keyword identity generator. |
| Materiality | Supported Enterprise consequence in an ADR-026 domain and supported impact rationale. Tests `numeric_metric_alone`, `caller_cannot_assert_semantics`, `rejected_assessment`. | No financial magnitude or commercial opportunity is inferred. Exact clause checks can reject valid paraphrased rationales until governed interpretation supplies the source basis. |
| Assurance | Canonical Unknowns/conflicts, supporting/counter Evidence, current/historical lineage, confidence and dates. Tests `core_same_period`, `non_core_contradiction`, `unknowns`, `unresolvable_counter_evidence`, `caller_cannot_omit_canonical_*`. | Existing Observation contradictions are conservatively core unless explicitly classified through the canonical contradiction record. |
| Durable owner | `memory/models.py::MaterialPressure`, `EnterpriseModel`; `memory/service.py::assess_material_pressure`; unchanged `EnterpriseModelRepository` storage. Tests persistence reconstruction, weakening, strengthening, resolution, supersession, replay and old JSON. | Rejected first assessments are diagnostic rows, not pressure truth. No migration/backfill. |
| Governed updates | Existing accepted `apply_observation` path; explicit annotation only creates candidates. Existing import compensation includes model snapshots. Tests approved import and forced pressure-save rollback. | Direct canonical fact assessment is explicit. No Evidence-only scheduler or bulk maintenance service. |
| Read boundaries | `enterprise_intelligence/retrieval.py`, `memory/views.py`, existing Executive quality diagnostic. Tests bounded qualified/conflict retrieval, current Evidence revalidation, historical exclusion and Memory panel. | Existing pages only. Executive staged dossier prose cannot become qualified truth; no Navigator or new dashboard. |

All source paths above are under `cios/applications/flora/`; regression names are
in [test_flora_material_pressure_lifecycle.py](../../../tests/test_flora_material_pressure_lifecycle.py).
Each assessment retains six gate results and an explicit reason. Core conflicts
produce UNRESOLVED. Rejected assessments retain source facts and diagnostics.
Existing qualified objects that lose support remain historical objects marked
NOT_QUALIFIED or UNRESOLVED; no accepted intelligence is silently deleted.

## Minimal implementation changes

- Extend the existing qualifier with canonical reference resolution, source binding,
  semantic context, material consequence checks and uncertainty handling.
- Add optional pressure/history and diagnostic collections to the existing
  Enterprise Model snapshot. No new repository or canonical ledger.
- Reuse `ObservationMemoryService` after accepted application. Retain opt-in
  provenance from existing Evidence processing. Preserve original import approval
  and compensation behavior.
- Expose assurance through existing bounded retrieval and Enterprise Memory view;
  report staged Executive assessment failures honestly.
- Add 51 isolated regressions. Adapt the six legacy qualifier tests to actual
  canonical sources instead of invented reference strings. Replace the unsafe
  TEL-001 test expectation that staging alone qualifies every enterprise with a
  test proving no self-promotion; TEL-001 source fixtures are unchanged.

## Golden-path outcomes

All tests use synthetic enterprise/Evidence records under isolated temporary
roots. No real easyJet facts or canonical production data are created.

| Case | Demonstrated outcome / regression |
| --- | --- |
| A | Verified financial condition qualifies, persists and reloads; `verified_pressure_qualifies_and_survives_repository_reconstruction`. |
| B | Missing referenced Evidence fails even with caller flags true; `missing_evidence_fails_even_when_candidate_flags_are_true`. |
| C | Rejected/quarantined/retired source and rejected/quarantined/expired Evidence fail; parametrized `ineligible_*`. |
| D | Three specified paraphrases reconcile through the same governed concept, scope and time to one ID; `paraphrases_reconcile_via_governed_semantic_basis_not_words`. |
| E | Independently supported fuel and refinancing conditions retain distinct IDs; `distinct_supported_conditions_are_not_merged`. Ambiguous equivalence remains unresolved. |
| F | Corroboration adds Evidence to existing lineage; `corroboration_and_identical_replay_do_not_duplicate_pressure_history`. |
| G | Same-period opposing assertion makes prior pressure UNRESOLVED, keeps both Observations and history; `core_same_period_contradiction`. |
| H | Severity conflict retains qualification and counter-Evidence; `non_core_contradiction_is_linked_without_invalidating_core`. |
| I | New confidence 45 Evidence weakens prior 85 assessment; `lower_confidence_evidence_weakens_existing_pressure`. Separate strengthening test preserves the earlier confidence. |
| J | Explicit Evidence-backed resolution preserves condition history and resolution lineage; `resolution_retains_original_condition_history_and_lineage`. Reopening requires supported reconciliation through all gates. |
| K | Identical evidence replay leaves the entire model unchanged; corroboration/replay test plus superseded and older-source replay tests. |
| L | Industry-scoped Evidence without target applicability fails; `industry_or_other_enterprise_evidence` (industry parameter). |
| M | Other-enterprise Evidence fails; same parametrized test (enterprise parameter). |
| N | No pressure, opportunity, procurement or watchpoint ledger is created; `pressure_creation_never_creates_commercial_domain_objects`. There is no commercial-generation call in the implementation. |
| O | Approved import reaches the existing model and bounded retrieval; `approved_import_uses_same_owner_and_bounded_retrieval`. Forced pressure persistence failure rolls back canonical writes through existing compensation. Existing Inc01/02 suites remain green. |

Additional tests cover current-source revalidation without writes, historical
retrieval, different-period non-conflict, source identity mutation, canonical fact
input, missing counter-Evidence, explicit core/non-core Unknowns and omission
attacks against canonical uncertainty references.

## Before/after verification

[Regression-Results.json](Regression-Results.json) records module outcomes and
individual pre-existing failure identifiers. Environment: existing
`/workspace/cios-venv/bin/python`, Python pytest runner with repository on
`PYTHONPATH=.`. Every process sets `FLORA_DATA_DIR` and `FLORA_PILOT_DIR` to a fresh
scratch root; fixtures further isolate writes using pytest `tmp_path`. The
original checkout remained clean. No production service or database was used.

| Tests | Baseline main | Increment 03 |
| --- | --- | --- |
| 51 new regressions, identical test file against both versions | 50 failed, 1 passed | 51 passed |
| 14 relevant existing modules | 170 passed, 5 failed | 170 passed, same 5 failed |
| Final focused run: new + qualifier + Executive EI | Not a separate baseline run | 60 passed |

Baseline new-test failures include absent durable model fields/methods as well as
unsafe qualification behavior. They are not all independent production incidents.
The historical-context exclusion test already passes on main, where no durable
pressure state exists. The modified legacy fixtures and TEL test are intentional
contract corrections described above, not failures hidden from the comparison.
The affected qualifier/Executive modules were rerun with the final source patch.

Commands executed from isolated branch/baseline worktrees:

```bash
FLORA_DATA_DIR="$scratch" FLORA_PILOT_DIR="$scratch" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q tests/test_flora_material_pressure_lifecycle.py
FLORA_DATA_DIR="$scratch" FLORA_PILOT_DIR="$scratch" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q \
  tests/test_flora_material_pressure_lifecycle.py \
  tests/test_material_pressure_qualification.py \
  tests/test_tel001_executive_enterprise_intelligence.py
git diff --check
```

For the 14-module comparison, run `python -m pytest -q tests/<file>` separately
with a new scratch root for each module; exact filenames and results are in the
JSON. Baseline SHA and test file were held constant. `git diff --check` passes.
The full repository suite and live-provider/browser/deployment tests were not run.

The five pre-existing failures, reproduced on both sides, are:

1. `test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route`.
2. `test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`.
3. `test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model`.
4. `test_tel001_enterprise_factual_presentation.py::test_tel001_facts_survive_without_assessment_and_render_on_actual_routes` (deployment expected-change label).
5. `test_flora_intelligence_projection.py::test_legacy_records_cannot_infer_readiness_from_volume_or_weighted_maturity` (legacy insight inventory text).

These remain outside this increment. No new failures appear in the compared
modules. Remote CI status is separate from these local test results.

## Remaining limits and next boundary

Semantic equivalence is explainable through accepted annotations, rather than
inferred autonomously. Direct clause matching is deliberately conservative and
cannot prove every natural-language entailment or detect every latent compound
condition. This increment validates an explicitly governed singular interpretation;
it does not supply an automatic semantic annotator or concept taxonomy service.

No new UI produces descriptors. Existing accepted workflows can carry them in
provenance; old models require no migration but receive no automatic pressure
backfill. Missing temporal context stays unresolved. Historical pressure snapshots
are retained for inspection; historical retrieval fails closed when the latest
source is outside the cutoff rather than reconstructing a complete past pressure
state from history.

Evidence-only edits are revalidated on read and explicit owner assessment. They do
not schedule durable reassessment by themselves. Existing whole-model file writes
and import compensation remain the concurrency/transaction boundary; this work
does not add cross-process locking or database transactions. Relationship-based
industry/group applicability, autonomous concept reconciliation and comprehensive
historical reconstruction remain future work requiring separate authorization.

Accepted ADRs, commercial generation, Opportunity/Procurement/Watchpoint governance,
industry propagation, exposure economics, scheduling and Navigator generation are
unchanged. Stop after Increment 03; no later increment was begun.
