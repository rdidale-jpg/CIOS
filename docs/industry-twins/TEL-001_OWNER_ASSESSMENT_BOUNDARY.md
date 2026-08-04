# Imported Industry Twin owner-assessment boundary

## Decision

Manual Import Twin stages immutable **candidate intelligence**. It does not invoke
the canonical assessment owners and it does not promote candidates. IT-001,
EI-001/EIF-001, EI-004/FP-009, and the named reinvention owners assess governed
objects after the governance decision. Therefore candidate pages must say
**“Intelligence supplied; owner assessment pending governance”** and must not
translate the missing owner result into a request to research fields already
present.

A package may supply an assessment object. Such a record is staged and projected
as an owner-shaped candidate output, but remains subject to the same acceptance
and promotion controls. The importer neither endorses its conclusions nor turns
it into a high-fidelity completeness result.

## Lifecycle and owner inventory

| Family | Candidate / owner input | Canonical assessment owner and model | Execution and persistence | Projection disposition |
|---|---|---|---|---|
| Industry Overview | `industry_twin`, evidence, Unknowns and Contradictions | IT-001; High-Fidelity Completeness Contract / Industry Fidelity | Deferred until governance; canonical IT-001 assessment store, not candidate staging | Present intelligence, assessment pending |
| Enterprise Dossier | `enterprise_twin` and linked records | EI-001 / EIF-001; Enterprise Intelligence Density | Deferred until governance; Enterprise Intelligence owner output | Present intelligence, assessment pending |
| Market Participant | `market_participant_twin` and relationships | IT-001 delegated participant owner; Market Participant Intelligence Density | Delegation remains unresolved and cannot be bypassed; deferred | Present intelligence, assessment pending |
| Transformation Programme | `transformation_programme`, enterprise and evidence links | EI-001 / EIF-001 Change Landscape / EI-002 | Deferred until governance; enterprise-owner output | Present intelligence, assessment pending |
| Opportunity | `opportunity_hypothesis`, customer, problem, timing and evidence | EI-004 / FP-009; Opportunity Completeness | Deferred until governance; opportunity-owner output | Present intelligence, assessment pending |
| Reinvention Assessment | `ai_reinvention_assessment` with mechanism, functions, timing, consequence and evidence | EI-001 / EIF-001 / EI-003 / FP-012; Temporal Fidelity | Package-supplied owner-shaped candidate is persisted in candidate staging; canonical persistence still requires governance | Supplied owner assessment, pending governance |

`owner-projection-v1` could discover the typed objects because it reads the shared
candidate semantic projection. It could not discover completeness assessments
because it only reads `high_fidelity_completeness_assessment`, which this package
does not declare. This is an intentional store/lifecycle boundary, not evidence
that the typed source collections are absent.

## Reinvention Assessment reconciliation

The manifest declares seven rows in
`record_sets/reinvention_assessments_wave5.ndjson`. The existing profile adapter
maps all seven to `ai_reinvention_assessment`; validation accepts all seven;
candidate staging persists all seven; Explore Twin selects all seven through the
`reinvention-assessments` collection; and the Reinvention projection reports the
supplied candidate-owner state.

| Source row | Adapter class | Validation / persistence | Collection and projection |
|---|---|---|---|
| RA-ENT-CITYFIBRE | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-ENT-TALKTALK | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-ENT-VODAFONETHREE | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-ENT-VMO2 | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-ENT-OPENREACH | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-ENT-BT | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |
| RA-IND-UK-TELECOMS | `ai_reinvention_assessment` | Accepted candidate | Included / supplied, pending governance |

## Opportunity identity root cause

The source uses `opportunity_title`; the adapter correctly exposes canonical
`title`, but generic semantic assembly previously considered only `subject`,
`enterprise_name`, and `organisation_name`. It consequently installed the
synthetic fallback “Twin scope”. Semantic assembly now uses the canonical
opportunity title/name fields before that fallback.

## Residual reconciliation

The reported 514 was **507 true residual records plus seven Reinvention
Assessments that were formerly absent from their typed collection**. After the
existing adapter path is honoured, the seven assessments are canonical typed
candidate content and must not remain residual. The 507 true residuals comprise:

* 95 accepted monitoring triggers in `monitoring_trigger_register_wave5.ndjson`;
* 412 lineage-only/ignored rows: opportunity scorecard 187; analyst estimates
  34; eleven 17-row registers (buyer intelligence, procurement, qualified
  opportunities, identity resolution, horizon reclassification, residual
  opportunities, and Wave 4–5 change log account for the applicable rows);
  corrected opportunity IDs 12; corrected horizon pipeline 12; pipeline totals
  9; named open pipeline 8; overlap 7; shaping 7; awards 5; unclassified 5;
  strategic hypotheses 3; and four single-row control/exception records.

These are retained for advanced inspection and lineage. They are not promoted
to executive content merely to eliminate a residual count.

## Before and after

Before, Research Gaps treated every absent owner result as broadly missing
source research, and diagnostics said “No owner-produced assessment supplied”.
After, fields are classified as source absent, source invalid, source present but
unassessed, owner-assessed deficiency, or genuine Unknown. Only absent, invalid,
and genuine-Unknown fields enter the research requirement. Candidate diagnostics
show the governance-pending state, while the seven package-supplied Reinvention
Assessments show their distinct supplied-candidate state. No score, local
completeness heuristic, promotion, package mutation, or TEL-001 branch is added.
