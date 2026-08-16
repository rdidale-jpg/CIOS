# CIOS Material Pressure Qualification Architecture Reconciliation

**Assessment date:** 2026-08-16
**Scope:** architecture only; no runtime or TEL-001 change
**Decision:** amend EI-001 first and advance it through normal governance

## AUTHORITY REVIEW

The complete current Chief Architect Knowledge Pack manifest and source map were
reviewed. The records relevant to this decision are below; pack records concerned
only with packaging, operating procedure, templates or roadmap context do not define
any of the requested semantic concepts.

### Accepted sources

| Document | Status | Canonical concept | Relevant rule | Can govern runtime today? |
|---|---|---|---|---|
| ADR-014 — Evidence-Governed Enterprise Intelligence Reasoning Runtime | Accepted decision (despite the legacy `Draft` header, its accepted amendment and current pack classify it as accepted) | Bounded runtime interpretation | Evidence package, applicability, lineage, labelled inference, Unknown/Contradiction preservation, safe failure; pressure assessment may be transient but cannot silently become fact | YES |
| ADR-024 — Hybrid Enterprise Intelligence Runtime | Accepted as recorded by its acceptance decision and current pack (legacy header says `Draft`) | Hybrid reasoning boundary | Deterministic identity, lineage, lifecycle, confidence, contradiction and recommendation controls; GPT interprets but cannot assign authority | YES |
| WP-011 — Flora Runtime Capability Baseline | Accepted implementation evidence baseline | Implemented capability, not domain semantics | Distinguishes demonstrated runtime from planned architecture | YES, only as evidence of what exists |

Neither accepted ADR supplies Material Pressure qualification semantics.

### Review sources

| Document | Status | Canonical concept | Relevant rule | Can govern runtime today? |
|---|---|---|---|---|
| EIF-001 — Enterprise Intelligence Foundation Model | Review | Enterprise foundation construction | Separates sourced Fact, Observation, Interpretation, Unknown, Evidence Demand and Enterprise consequence; keeps commercial implication derived | NO |
| FP-012 — Enterprise Reinvention Intelligence | Review | Enterprise reinvention rationale | Connects change, constraints and enterprise consequence to later commercial reasoning without replacing canonical EI owners | NO |

### Draft sources

| Document | Status | Canonical concept | Relevant rule | Can govern runtime today? |
|---|---|---|---|---|
| EI-001 — Enterprise Model Specification | Draft | Durable Enterprise Model, Transformation Pressure, facts, change, programme, procurement, risk context, opportunity outlook | Existing pressure definition is “force accumulating on the enterprise to change”; the new canonical annex supplies qualification, identity, materiality, consequence, lineage and boundaries | NO, until accepted |
| EI-002 — Enterprise Knowledge Graph | Draft | Durable graph identity and relationships | Keeps Evidence, Observation, Enterprise attributes and relationships addressable with lineage rather than collapsed into prose | NO |
| EI-003 — Enterprise Behaviour Model | Draft | Repeatable enterprise behaviour | Behaviour is an evidenced predictive tendency, not a pressure; behaviour may affect response and commercial interpretation but cannot prove pressure existence | NO |
| EI-004 — Commercial Reasoning Framework | Draft | Commercial interpretation | Derives commercial significance, opportunity hypothesis and action over governed enterprise understanding; does not own durable enterprise truth | NO |
| EI-012 — Enterprise Observation Model | Draft | Atomic Observation, Evidence Demand, Unknown and Contradiction | Evidence supports non-speculative Observations; repeated Evidence strengthens one Observation; interpretation, hypothesis and recommendation remain separate | NO |
| FP-009 — Hypothesis Validation Standard | Draft | Hypothesis validation | Requires testability, competing explanations, Evidence Demands, Unknowns, Contradictions and lineage before stronger commercial judgement | NO |

### Proposed sources

| Document | Status | Canonical concept | Relevant rule | Can govern runtime today? |
|---|---|---|---|---|
| FEIR-001 — Flora Enterprise Intelligence Runtime Architecture | Proposed | Flora runtime separation | Durable knowledge is distinct from derived runtime assessment and transient presentation; workers cannot promote authority | NO |
| EIRP-001 — Enterprise Intelligence Reasoning Pipeline | Proposed | Stage contracts for Observation, enterprise context, challenge, commercial assessment and presentation | Enterprise specificity and lineage are validated; Unknown/Contradiction propagate; commercial significance is a derived Commercial Assessment field | NO |

## EXISTING ARCHITECTURE

**Existing Pressure concept:** EI-001 Transformation Pressure is the applicable
existing concept (option A: defined but not accepted), but its prior prose lacks a
deterministic qualification contract. “Material Pressure” is reconciled as its
qualified durable representation, not a new subsystem.

**Existing Observation concept:** EI-012 owns the atomic, evidence-backed,
non-speculative statement about an enterprise change, condition, event, relationship,
absence or contradiction. An Observation is eligible input, not automatically a
Pressure.

**Existing Behaviour concept:** EI-003 owns slow-moving, repeated tendencies in how
an enterprise responds. Behaviour may explain likely response but cannot establish
the existence or materiality of a condition.

**Existing Commercial Reasoning concept:** EI-004 owns seller-specific significance,
timing, fit, conviction and action derived over enterprise truth.

**Existing Opportunity boundary:** Opportunity is a separate, time-bound commercial
hypothesis/object. A Pressure can support it but cannot create or qualify it.

**Existing Watchpoint boundary:** Existing monitoring-trigger semantics concern a
condition/evidence change to watch and a reassessment action. A Watchpoint may
reference a Pressure; the Pressure is not itself the monitoring instruction.

## CANONICAL OWNER

**Recommended owner:** EI-001 Enterprise Model Specification.

**Why:** Material Pressure is durable enterprise understanding derived from governed
Observations and facts. EI-001 already owns the Enterprise Model and Transformation
Pressure, while EI-012 owns its input primitive and EI-004 owns downstream commercial
meaning. The reconciliation evolves an existing object exactly at that boundary.

**Alternative owners considered:** EI-012 Observation; EI-003 Behaviour; EI-004
Commercial Reasoning; FEIR/EIRP runtime; dossier/presentation; a new ADR or subsystem.

**Why rejected:** Pressure is an interpretation over Observations, not an atomic fact;
it is a current enterprise condition, not a repeatable response tendency; its
existence must not depend on seller-specific reasoning; runtime and presentation map
canonical semantics rather than own them. No cross-cutting decision beyond EI-001's
existing ownership warrants an ADR.

## MATERIAL PRESSURE DEFINITION

A Material Pressure is an evidence-grounded condition, change or accumulating force
applicable to one identified enterprise that constrains, impairs or makes a material
response necessary, with at least one supported material enterprise consequence. It
is a governed interpretation in durable Enterprise understanding. It is not merely an
Observation, Fact, Risk label, generic Challenge, Programme, Strategic Priority,
Financial Metric, Opportunity, Procurement or Watchpoint.

## QUALIFICATION CONTRACT

**Eligible input:** One or more governed, non-rejected Observations or accepted
factual objects with attributable Evidence. Properly labelled human input is allowed;
candidate input cannot create an accepted Pressure.

**Enterprise applicability:** Canonical Enterprise ID and group/subsidiary/business-
unit scope must match. An industry or competitor condition needs a governed
relationship showing its application to that Enterprise; membership alone fails.

**Pressure condition:** Evidence must show constraint or impairment to performance,
resources, obligations or choices, or necessity for a response. A value, event,
priority, response or keyword is insufficient.

**Materiality:** No numeric score. At least one non-trivial, evidence-supported
strategic, financial, operational, regulatory/obligation, programme/change-delivery
or investment/capital-allocation consequence, with scope and direction, is required.

**Enterprise consequence:** YES, required. It states the affected Enterprise outcome,
obligation, resource, operating condition or committed change. Exact severity,
timing, owner and response may remain Unknown; a wholly unsupported consequence may
not be inferred.

**Evidence requirement:** Attributable Evidence plus governed Observation/fact owner,
applicability path, consequence and a recorded gate-by-gate qualification decision.

**Uncertainty:** Unknown existence or materiality blocks. Once those pass, severity,
timing, direction detail, ownership and response may each be Unknown and visible.

**Contradiction:** Preserve all conflicting Evidence. Conflict preventing existence,
materiality or directional pressure semantics yields UNRESOLVED. Conflict only about
severity, timing, consequence detail, owner or response bounds confidence, marks the
field Contradiction/Unknown and creates an Evidence Demand; it does not erase a
separately proven Pressure.

**Rejection:** Reject or explicitly leave unresolved for ineligible/insufficient
Evidence, wrong/unresolved Enterprise, keyword match, generic market assumption,
fact without pressure semantics, no supported material consequence, unsupported
inference, blocking Contradiction or duplicate representation. Never silently
promote.

## IDENTITY / SINGULARITY

Identity is the tuple of canonical Enterprise and scope, affected enterprise
outcome/obligation/resource, constraining mechanism/condition and materially
continuous interval—not wording or Evidence ID. A match attaches Evidence to one
Pressure; a distinct mechanism/outcome is distinct. Missing scope, mechanism, outcome
or temporal continuity produces unresolved identity, possible-match links and an
Evidence Demand, with neither merge nor duplicate qualification.

## LIFECYCLE

No new lifecycle enumeration is necessary. Dated Evidence, freshness and direction
show whether the condition is emerging, continuing, weakening or no longer current.
Evidence strengthens, weakens, contradicts, retires or supersedes; historical
Pressure remains explainable. Explicit states should be added only after a consumer
proves evidence-derived lifecycle inadequate.

## COMMERCIAL REASONING BOUNDARY

**Material Pressure contains:** Enterprise proposition/scope,
mechanism/condition, material enterprise consequence, uncertainty, contradiction,
freshness and qualification/evidence lineage.

**Commercial reasoning derives:** Commercial Significance, seller relevance,
provider fit, accessibility, pursuit timing, conviction and recommended action.

**Opportunity relationship:** MATERIAL PRESSURE ≠ OPPORTUNITY. It may support a
Signal, Hypothesis, Commercial Assessment or Opportunity thesis; no automatic
creation or qualification.

**Procurement relationship:** MATERIAL PRESSURE ≠ PROCUREMENT. Procurement is a
separately evidenced activity that may indicate response/timing; qualification cannot
create it.

**Watchpoint relationship:** A separately governed Watchpoint may reference the
Pressure and specify what change to monitor and what review to trigger. Monitoring a
Pressure does not reclassify it.

## EVIDENCE LINEAGE

Every Pressure must retain stable Pressure ID; Enterprise/scope ID; proposition;
supporting and contradicting Evidence IDs; governing Observation/factual-object IDs
and owner; applicability relationship path; supported consequence/domain;
truth/confidence/freshness; Unknown/Contradiction references; and decision contract
version, gate results, authority, timestamp and rationale. This is the inspectable
answer to “Why does Flora believe this pressure exists?”

## TEL-001 CONCEPTUAL VALIDATION

These are contract tests, not accepted pressure records or runtime output changes.

**BT Group:** Candidate: high capex/net debt combined with transition toward cash
generation. Evidence: `EV-BT-FY26`, `EV-BT-Q1FY27` and dossier facts. Would qualify:
YES, if those governed facts support constrained capital allocation/cash generation at
BT Group scope. Why: pressure semantics and financial/investment consequence can be
direct. Missing requirement: runtime must validate exact fact status, scope and
lineage rather than trust dossier wording.

**CityFibre:** Candidate: debt/financing and consolidation economics with take-up
monetisation. Evidence: `EV-CITYFIBRE-FY25` and the dossier's CityFibre-scoped facts.
Would qualify: YES, if evidence establishes financing/cash or investment consequence.
Why: enterprise-specific financial constraint can be material. Missing requirement:
validate consequence and continuity; the generic altnet financing environment alone
would fail.

**Openreach:** Candidate: Ofcom access regulation plus FTTP take-up versus build cost.
Evidence: `EV-OR-FTTP26`, `EV-BT-CMA-NEXFIBRE-RESPONSE26`. Would qualify: YES, if
Openreach scope and an evidenced pricing, investment or delivery consequence are
linked. Why: obligation/constraint and consequence can both be direct. Missing
requirement: retain Openreach-versus-BT Group scope and do not infer from regulation
alone.

**TalkTalk:** Candidate: debt/refinancing. Evidence: `EV-TALKTALK-CH-2025`,
`EV-TALKTALK-FT-FUNDING26`. Would qualify: UNRESOLVED. Why: dossier also records
current financial opacity and secondary-reporting supplier risk. Missing requirement:
governed current evidence establishing existence, material consequence, timing and
resolving any material contradiction.

**Virgin Media O2:** Candidate: customer-service quality/complaints affecting Consumer
fixed/customer operations. Evidence: `EV-VMO2-Q4FY25-PDF` and dossier facts. Would
qualify: UNRESOLVED. Why: complaints are evidence candidates, but material operational
or regulatory consequence and correct business-unit/group scope must be established.
Missing requirement: supported consequence and applicability path.

**VodafoneThree:** Candidate: merger integration complexity and regulatory remedy/
wholesale obligations. Evidence: `EV-VT-OWN-COMPLETE26`, `EV-VT-WRO25`,
`EV-CMA-VT-CLOSE25`. Would qualify: YES for a regulatory/integration Pressure only if
the evidence links obligations to material integration, investment or operating
consequence. Why: named obligations and integration scope can establish constraint.
Missing requirement: exact consequence and whether integration and remedy are one
mechanism/outcome or separate Pressure identities.

## BT WORKED EXAMPLES

**Candidate:** Cost base / cost-transformation target. **Qualifies:** YES, only where
accepted BT Evidence shows the cost condition constrains margin/cash or necessitates
material simplification. **Reason:** a cost number alone is a Fact; constraint plus
consequence makes it a Pressure.

**Candidate:** Legacy estate. **Qualifies:** UNRESOLVED. **Reason:** inventory age or
“legacy” wording alone is a Fact/label; it needs evidenced operational, financial,
regulatory or programme consequence.

**Candidate:** Capex. **Qualifies:** NO as a standalone metric. **Reason:** capex is a
Financial Metric; high capex plus evidence that it constrains cash/capital allocation
may qualify as a distinct Pressure.

**Candidate:** Debt financing costs. **Qualifies:** UNRESOLVED. **Reason:** TEL-001's
high net-debt wording does not by itself prove financing-cost direction or material
consequence; a governed cost/debt consequence is required.

**Candidate:** Competitive broadband/mobile pricing. **Qualifies:** UNRESOLVED at BT
Group scope. **Reason:** competition is external context; Consumer-specific evidence
must link it to churn, ARPU, margin or a necessary response.

**Candidate:** Regulated Openreach pricing. **Qualifies:** YES at resolved Openreach
scope when evidence establishes an obligation constraining pricing and a material
revenue/investment consequence. **Reason:** this is more than the Fact that regulation
exists.

**Candidate:** PSTN/copper migration. **Qualifies:** UNRESOLVED. **Reason:** migration
is a Programme/change response; it becomes evidence of Pressure only if obligation,
legacy constraint or execution consequence is separately supported.

**Candidate:** Enterprise complexity. **Qualifies:** UNRESOLVED. **Reason:** a generic
Challenge label needs an evidenced mechanism and consequence in BT Business or Group
scope.

## FALSIFICATION

**Financial metric:** PASS — rejected without supported pressure semantics and
consequence.
**Generic telecom challenge:** PASS — rejected without Enterprise applicability.
**Competitor condition:** PASS — rejected without a governed applicability path.
**Strategic priority:** PASS — a chosen outcome/response is not a constraining force.
**Opportunity:** PASS — separate downstream hypothesis/object; cannot self-prove.
**Programme:** PASS — treated as response/change unless it separately evidences
constraint and consequence.
**Procurement:** PASS — separate commercial activity; never generated by Pressure.
**Weak observation:** PASS — insufficient Evidence/material consequence is rejected.

## GOVERNANCE ACTION

**A / B / C:** B — amend the existing canonical EI-001 source and advance it through
normal governance. Accepted architecture constrains reasoning but is not sufficient,
so A is false; this is an elaboration of EI-001's existing ownership, so C is
unnecessary.

**Canonical source to change:** EI-001 Enterprise Model Specification, first.

**Required change:** Accept the Material Pressure qualification annex added beside
Transformation Pressure, including gates, identity, uncertainty, contradiction,
lineage, rejection and commercial/monitoring boundaries.

**Derived artefacts requiring reconciliation:** after acceptance only: EI-012 mapping
from Observation; EI-002 graph/schema mapping; EI-004 commercial-input mapping;
FEIR-001 and EIRP-001 runtime contracts; Knowledge Pack manifest/checksum/release;
Flora import/reasoning/projection specifications and acceptance tests. TEL-001 data
and dossier content do not require alteration.

## CHANGE IMPACT

**Runtime changed:** NO
**TEL-001 changed:** NO
**Fresh import required:** NO
**New ontology introduced:** NO
**New governance artefact required:** NO

## IMPLEMENTATION READINESS

**NO.** The proposed contract is semantically precise enough to implement without
inventing decisions, but EI-001 is still Draft. Runtime work must wait until the
canonical change is accepted and subordinate runtime specifications are reconciled.

## RECOMMENDED IMPLEMENTATION SPRINT

**Name:** Flora Material Pressure Qualification — Governed Runtime Increment.
**Objective:** after EI-001 acceptance, map eligible governed enterprise intelligence
through the accepted gates without changing source truth.
**Canonical owner:** EI-001 Enterprise Model Specification.
**Smallest runtime increment:** candidate evaluation, explicit gate results,
unresolved/rejected outcomes, identity deduplication and inspectable lineage before
any projection change.
**Acceptance principle:** no Material Pressure without accepted Enterprise
applicability, pressure semantics, material consequence and complete qualification
lineage; no automatic Opportunity or Procurement.

## DECISION

**ARCHITECTURE READY FOR GOVERNANCE**
