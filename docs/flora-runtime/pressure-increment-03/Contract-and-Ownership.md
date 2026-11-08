# Increment 03 — ADR-026 assessment and ownership design

Baseline: `096c9832df3b67a0970a3a0e1681133110b075a1`, main including merged
PRs #530 and #531. Assessment recorded before implementation.

ADR-026 is Accepted and owns qualification; ADR-002 owns durable Enterprise
memory; ADR-009 preserves progressive assurance; ADR-014/024 own bounded
interpretation and validation. EI-001, EI-012 and EI-004 are Draft design material;
ADR-026 explicitly establishes EI-001's durable-pressure ownership without
accepting those documents wholesale. No accepted ADR will be changed.

## Current implementation and gaps

`blueprint_import/material_pressure.py` returns read-only assessments. It admits
caller-supplied Boolean gates and nonempty reference strings, hashes condition
wording, and has no canonical Evidence lookup or durable reconciliation. Semantic
Enterprise discovery reads financial condition/outlook fields from a staged Twin
wrapper, assumes applicability, and joins conditions. Executive quality uses the
assessment; no Enterprise Model pressure state is maintained.

| ADR-026 gate | Current proof | Required minimum extension |
| --- | --- | --- |
| Governed input | Type label and ID presence | Resolve canonical Observation/factual object; verify acceptance/lifecycle and bind the candidate to its governed descriptor |
| Applicability | Caller Boolean and enterprise string | Canonical enterprise identity and direct enterprise-scoped accepted Evidence; industry/other-enterprise context cannot silently apply |
| Pressure semantics | Nonempty condition and Boolean | Explicit accepted causal interpretation with inspectable condition/mechanism source support, rather than a metric or renderer label |
| Identity/singularity | Hash of literal condition | Governed condition concept + enterprise/domain/scope/time, supported by an explicit semantic rationale; uncertain competing concepts require reconciliation, never keyword/fuzzy merging |
| Materiality | Consequence-domain presence | Accepted consequence domain and supported nontrivial consequence/materiality explanation |
| Assurance | Nonempty Evidence tuple | Resolve actual source Evidence, Observations, Unknowns and contradictions; preserve supporting/counter-evidence, confidence and dates |

Temporal qualification, core/non-core distinction and changes to existing
pressure state are not implemented by the current helper. Import now projects
approved supported Observations through ObservationMemoryService; its existing
promotion compensation includes affected Enterprise Model files. This is the
safe integration point, not staging, rendering, or provider prose.

## Owner extension and update point

Extend the existing EnterpriseModel with pressure objects and a separately named
diagnostic assessment collection, in its existing JSON snapshot. No independent
pressure repository, canonical ledger, framework or scheduler is introduced.
Rejected first assessments are diagnostics only. Previously qualified objects
retain history when weakened, unresolved, resolved or superseded; those historical
objects do not imply current qualification.

Pressure consideration is opt-in: an accepted source can carry a structured
`material_pressure` descriptor in existing Observation provenance (or in an owned
canonical factual object). The descriptor supplies the condition, bounded concept,
mechanism, affected domain/scope/time, material consequence and explicit semantic
rationale. Each asserted basis must be backed by resolvable accepted source text.
The concept/rationale are governed semantic work, not a keyword-generated code.
Absent or uncertain semantic grounding remains an explicit reconciliation need.

ObservationMemoryService owns maintenance after canonical acceptance. Replays
must compare substantive assessment content before writing history. Existing
pressures can be reassessed when their supporting Observations change; unrelated
unannotated Observations must not create pressures. Import continues to rely on
existing review, approval, canonical acceptance and file compensation.

Resolution and supersession use explicit Evidence-backed relations and supplied
dates, not an invented lifecycle enumeration. Current qualification status,
observed/effective timing and history remain separate from commercial reasoning.
Existing bounded retrieval and model-backed views expose qualified/unresolved
state and diagnostics without creating Opportunities, Procurements or Watchpoints.

## Implemented bounded contract

The descriptor is an opt-in part of existing governed provenance, not a new
canonical import class or autonomous extraction service. Its required fields are
`condition`, `condition_concept`, `condition_basis`, `mechanism`, `affected_domain`,
`scope`, `time_context`, `consequence`, `consequence_domain`,
`materiality_rationale`, and `identity_rationale`; `effective_at` is retained when
provided. Condition basis, mechanism, consequence, materiality and semantic
rationale require direct clause support from resolved source Evidence. Causal and
impact checks reject plain metric-only annotations. An accepted descriptor supplies
semantic interpretation; the runtime does not invent a concept from word overlap.

Optional `observation_refs`, `unknown_refs` and `contradiction_refs` resolve through
existing owners. Source uncertainty cannot be omitted by an API caller. Core
uncertainty blocks qualification; the ADR's non-core fields may remain explicit.
An uncertain alternative concept for an existing same-scope/domain/time pressure
requires reconciliation. Explicit `distinct_from` can establish the governed
separation; supported `supersedes_pressure_id` + `supersession_basis` can establish
replacement. Mutation of the identity basis on an existing source is unresolved.

Resolution requires `resolves_pressure_id`, `resolved_at`,
`resolution_evidence_refs`, and directly supported `resolution_basis` referring to
an existing pressure. Requalification after resolution requires all gates plus
`reopens_pressure_id`, directly supported `requalification_basis`, and an effective
date at or after resolution. Ordinary historical replay cannot reopen a resolved
or superseded object. Supersession records both identities and effective timing.
These are explicit evidence relations, not a new mandatory lifecycle enumeration.

`EnterpriseModel.material_pressures` holds previously qualified objects and their
history. `EnterpriseModel.pressure_assessments` holds per-source diagnostics;
failed first assessments do not create pressure objects. Both use the existing
EnterpriseModelRepository JSON snapshot and existing import rollback. Additive
optional fields read old `flora-memory-v1` snapshots without migration. Source
publication/collection/acceptance/freshness details remain in their canonical
Evidence/Observation records, reachable through retained references rather than
copied into a competing source of authority.

Maintenance runs after accepted Observation application when explicitly annotated,
and reassesses existing pressures dependent on changed attributes. A canonical
fact can be assessed explicitly through the same owner method. Read models
revalidate the latest canonical source without writing. There is no bulk backfill,
Evidence-only background hook, industry propagation, new model, or new page.
