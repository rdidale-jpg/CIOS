# OT-001 — Opportunity Twin Specification

**Status:** Review  
**Authority:** Proposed subordinate model specification  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-14  
**Production behaviour:** Documentation-only architecture specification. Does not change runtime behaviour, the Enterprise Model, the Observation Model, EI-006, ADR-008, EI-013, production Researcher packs or Flora implementation contracts.

## 0. Opportunity ownership review

### Sources inspected

This specification was created after reviewing the Architecture Authority Registry, Document Map, EI-001, EI-002, EI-004, EI-005, EI-006, FP-008, EOD-001, the Enterprise Intelligence Opportunity Lifecycle diagram and accepted ADRs governing durable memory, reasoning lineage, human-supplied knowledge, canonical acceptance, packaging and enterprise understanding. `OPI-001` and `RTP-001` were requested inputs but no matching documents were present in the repository at the time of review; their expected responsibilities are therefore recorded as Unknowns rather than assumed authority.

### Ownership decision

EI-006 owns opportunity prediction, Opportunity Outlook and commercial accessibility logic at the Enterprise Intelligence paper level. OT-001 does not replace EI-006 and does not create a new EI paper. OT-001 is a subordinate Review specification under EI-006 that defines the durable Opportunity Twin object needed to preserve governed opportunity memory over time.

| Concept | Current owner | OT-001 position |
|---|---|---|
| Opportunity | EI-006, supported by EOD-001 | Defines a precise subordinate object definition for Review. |
| Opportunity Outlook | EI-006 | A current generated view over Opportunity Twin state, not a competing durable object. |
| Commercial Conviction | FP-008 | Referenced for readiness judgement and recommendation thresholds. |
| Commercial Outcome | FP-008 now; future learning owner remains open where EI-013 is exchange-focused | Recorded as outcome and learning events linked to the Twin. |
| Provider Fit | FP-008 / EI-006 conceptually, outside public research per EOD-001 and lifecycle diagram | A separate overlay reference, never merged into public-domain truth. |
| Opportunity lifecycle | EOD-001 and Enterprise Intelligence Opportunity Lifecycle | OT-001 defines object states without implying confidence. |

### Conflicts and Unknowns

- `OPI-001` and `RTP-001` are referenced by mission scope but absent from the repository; this specification treats Opportunity Positioning and Research-to-Positioning Handover as interfaces pending document reconciliation.
- EI-006 currently lists Provider Fit as an input theme, while EOD-001 states Provider Fit is outside public-domain research. OT-001 reconciles this by allowing a Provider Fit reference or overlay, not a public Researcher conclusion.
- EI-013 is occupied by Knowledge Asset Exchange Model and must not be reused for Opportunity Twin ownership.

## 1. Purpose

The Opportunity Twin exists to preserve durable, evidence-governed memory about a commercially meaningful enterprise-change opportunity. It solves the problem where CIOS can research a procurement, programme or report and then lose the broader opportunity system that explains why the opportunity exists, what it depends on, how it may be accessed, how positioning evolved and what was learned.

The CSM lesson is that the visible procurement was not the whole opportunity. Multiple phases, partners and procurements formed one connected opportunity system. Durable opportunity memory was required across research, positioning and pursuit so CIOS could avoid anchoring on a single notice and could retain evidence, hypotheses, positioning and learning as the opportunity changed.

**Opportunity definition:** An Opportunity is a commercially meaningful enterprise-change situation in which an enterprise need, transformation pressure, actor system, buying pathway and possible commercial action can be reasoned about from governed evidence, Unknowns and hypotheses.

**Opportunity Twin definition:** A durable, evidence-governed model of a commercially meaningful enterprise-change opportunity, its origins, actors, dependencies, buying pathways, positioning, decision boundaries and learning history.

## 2. Architectural position

```text
Enterprise Twin
→ Opportunity Discovery
→ Opportunity Portfolio
→ Opportunity Prioritisation
→ Opportunity Twin
→ Opportunity Positioning
→ Provider Fit
→ Executive Pursuit
→ Outcome
→ Learning
```

The Opportunity Twin reads enterprise memory from the Enterprise Twin but does not duplicate enterprise memory. Enterprise facts, Observations, executive records, programme records and graph relationships remain governed by their owning models. The Opportunity Twin stores opportunity-specific composition, interpretation, hypotheses, Decision Envelopes, positioning candidates, accessibility reasoning and learning links that bind those enterprise facts into a commercial opportunity history.

## 3. Opportunity identity

Stable identity fields are:

| Field | Description |
|---|---|
| Opportunity ID | Stable identifier, unique within CIOS and not reused after retirement. |
| Title | Human-readable title. |
| Enterprise | Linked enterprise identifier. |
| Business unit or monitored scope | Business unit, geography, capability, account scope or monitored perimeter. |
| Programme or transformation theme | Primary programme, theme or transformation driver. |
| Aliases | Procurement names, internal names, programme aliases and historical labels. |
| Opportunity type | Emerging, programme-linked, procurement-linked, renewal, transformation, partner, platform, advisory or other governed type. |
| Effective date | Date from which the opportunity identity is considered active. |
| Owner | Accountable CIOS owner or steward. |
| Lifecycle state | Current lifecycle state from section 5. |
| Evidence boundary | Public, human-supplied, private-provider, mixed or restricted. |
| Confidence | Evidence confidence for claims, not automatic lifecycle confidence. |
| Freshness | Date and review status for current state. |

## 4. Opportunity composition

An Opportunity Twin may link to enterprises, business units, programmes, procurements, contracts, frameworks, platforms, suppliers, executives, outcomes, pressures, risks, Observations, Signals, hypotheses, theses, Positioning Options, Evidence Demands and Decision Envelopes.

An Opportunity is not the same as a procurement. One Opportunity may relate to several programmes and procurements. One procurement may support only part of an Opportunity. An Opportunity can exist before procurement when evidence supports enterprise need, pressure, ownership or likely buying conditions. CRM pipeline records are execution artefacts and are not the canonical Opportunity Twin.

## 5. Opportunity lifecycle

Permitted lifecycle states are:

- Detected;
- Emerging;
- Validating;
- Researchable;
- Prioritised;
- Shaping;
- Positioned;
- Provider-Fit Review;
- Pursuit Candidate;
- Pursuing;
- Deferred;
- Rejected;
- Awarded;
- Lost;
- Realising;
- Closed;
- Archived.

Lifecycle state must never imply evidence confidence automatically. A `Pursuing` opportunity may have unresolved Unknowns. A `Detected` opportunity may have high-confidence evidence for a narrow claim. A `Rejected` opportunity may remain useful as learning.

## 6. Evidence and reasoning

Every material Opportunity Twin claim must preserve this lineage:

```text
Source
→ Evidence
→ Observation
→ Signal
→ Hypothesis
→ Commercial Thesis
→ Opportunity state
→ Positioning
→ Recommendation
```

The Twin must preserve Unknowns, Contradictions, human-supplied knowledge labels, Confidence, Freshness, falsification conditions and review triggers. Strong recommendations require inspectable lineage; otherwise the appropriate output is an Evidence Demand, caveated Decision Envelope or learning action.

## 7. Need, accessibility and Provider Fit

The Twin keeps three judgements distinct:

| Judgement | Question | Boundary |
|---|---|---|
| Enterprise Need | Does the enterprise need to change? | Public and enterprise evidence may support this. |
| Commercial Accessibility | Is the opportunity commercially reachable? | Uses procurement routes, timing, frameworks, openness, incumbent position and route-to-market evidence. |
| Provider Fit | Can a particular provider credibly win and deliver? | Separate provider overlay using private capability, references, relationships, capacity, partner strategy, constraints, appetite and commercial position. |

These must not be combined into one unexplained score.

## 8. Opportunity Outlook and adjacent objects

| Object | Boundary |
|---|---|
| Opportunity Twin | Durable governed opportunity memory and current state. |
| Opportunity Outlook | Current view generated from Opportunity Twin state and EI-006 logic. |
| Opportunity Positioning Brief | Transient view of candidate positioning and narratives. |
| CRM opportunity | Sales execution record; not canonical CIOS opportunity memory. |
| Procurement | Buying event or route; subordinate evidence or component. |
| Recommendation | Action statement requiring lineage and Decision Envelope support. |
| Commercial Outcome | Result or consequence of action, pursuit, award, loss, deferral or delivery. |

Reports and briefs are views over the Opportunity Twin.

## 9. Opportunity Portfolio

Multiple Opportunity Twins within an enterprise sit in an Opportunity Portfolio. The portfolio supports prioritisation, sequencing, dependencies, overlaps, shared evidence, competing opportunities, opportunity retirement and continuity across research refreshes. Shared evidence is linked rather than copied, allowing one Observation to inform several Twins while preserving each Twin's distinct hypotheses and decisions.

## 10. Positioning relationship

OPI-001 is absent from the repository, so this section proposes an interface pending reconciliation. Opportunity Positioning reads from the Opportunity Twin and contributes candidate positioning objects back to it, including strategic theses, executive narratives, transformation frictions, white-space candidates, conversation plays, proof requirements, commercial risks and stop conditions. These remain governed candidate objects until accepted through the relevant review path.

## 11. Provider Fit relationship

Provider Fit remains a separate overlay containing provider capabilities, references, relationships, delivery capacity, partner strategy, constraints, appetite and commercial position. Public Researcher outputs must not create final Provider Fit conclusions. The Opportunity Twin may store a Provider Fit reference, summary status or Evidence Demand, but provider-private facts stay outside public-domain opportunity truth.

## 12. Decision Envelope

Every Opportunity Twin must carry a current Decision Envelope with one of:

- Supported;
- Supported with Caveats;
- Not Supported.

The Decision Envelope records decisions supported, decisions blocked, Evidence Demands, Unknowns, Contradictions and expiry or review trigger. It bounds what CIOS may safely do with the current state.

## 13. Learning and outcomes

Outcomes update the Opportunity Twin through customer conversations, new evidence, bid decisions, procurement events, awards, losses, delivery outcomes, rejected hypotheses and lessons learned. The Twin separates enterprise learning, opportunity learning, architecture learning and provider learning so that private provider experience does not silently rewrite public enterprise truth and architecture lessons do not become enterprise facts.

## 14. Flora relationship

Flora should maintain accepted Opportunity Twin state and generate transient views such as Opportunity Brief, Positioning Brief, Executive Meeting Brief, Pursuit Summary, Decision Envelope and Evidence Demand Register. Reports remain views. Flora must preserve lineage, freshness and canonical acceptance boundaries before promoting candidate material into accepted state.

## 15. Required Opportunity Twin field model

| Area | Fields |
|---|---|
| Identity | opportunity_id, title, aliases, opportunity_type, effective_date, owner, status, evidence_boundary. |
| Enterprise relationship | enterprise_id, business_unit_scope, enterprise_twin_links, knowledge_graph_links. |
| Opportunity thesis | commercial_thesis, transformation_thesis_links, hypothesis_ids, falsification_conditions. |
| Enterprise outcomes | target_outcomes, executive_outcomes, public_outcome_evidence. |
| Executive owners | named_executives, accountable_roles, sponsor_confidence, relationship_evidence. |
| Transformation pressures | cost, resilience, regulation, service, technology_debt, workforce, policy, market or sector pressures. |
| Programmes | related_programmes, phase_links, dependencies, status, confidence, freshness. |
| Procurements | related_procurements, routes, notices, frameworks, lots, values, timing, status. |
| Suppliers | incumbents, partners, likely competitors, supplier_roles, evidence boundary. |
| Commercial accessibility | access_routes, route_confidence, procurement_readiness, incumbent_lock, timing_window, accessibility_unknowns. |
| Transformation frictions | blockers, operating constraints, delivery risks, adoption issues, governance issues. |
| Hypotheses | active, supported, weakened, rejected and deferred hypotheses. |
| Positioning | candidate_positioning_options, narratives, proof_requirements, risks, stop_conditions. |
| Provider Fit reference | provider_fit_overlay_id, fit_status, fit_unknowns, provider-private boundary marker. |
| Evidence | source_ids, evidence_ids, evidence_quality, evidence_coverage, lineage. |
| Observations | observation_ids, signal_ids, human_supplied_labels. |
| Unknowns | unknown_id, question, impact, owner, review_date, blocking_status. |
| Contradictions | contradiction_id, conflicting_claims, severity, resolution_plan. |
| Confidence | claim_confidence, reasoning_confidence, confidence_rationale. |
| Freshness | last_evidence_date, last_review_date, decay_rule, review_trigger. |
| Decision Envelope | support_state, supported_decisions, blocked_decisions, evidence_demands, expiry. |
| Lifecycle | lifecycle_state, state_history, state_change_reason. |
| Outcomes | conversation_events, bid_decisions, procurement_events, awards, losses, delivery_outcomes. |
| Learning | enterprise_learning, opportunity_learning, architecture_learning, provider_learning. |
| Provenance | created_by, created_at, updated_by, updated_at, acceptance_record, source_boundary. |

## 16. CSM worked example

A CSM Opportunity Twin would represent one connected opportunity system rather than treating SIDP or any single visible procurement as the opportunity. It would link Phase 1, Phase 2, Phase 2b, Transformation Partner, ERP/System Implementation Delivery Partner, Oracle Fusion, MOD responsibilities and supplier responsibilities as related components where evidenced.

The Twin would record positioning theses such as whether the opportunity is primarily ERP implementation, transformation assurance, delivery recovery, partner orchestration or MOD-side capability enablement. It would carry Evidence Demands for phase boundaries, responsibility split, procurement scope, incumbent commitments, decision ownership, timing and MOD versus supplier accountability. Provider Fit would remain a separate overlay because whether a specific provider can win or deliver depends on private capability, relationships, references, appetite and partner strategy.

CSM-specific structures are examples only and are not universal architecture.

## 17. Validation tests

| Scenario | Expected representation | Result |
|---|---|---|
| MOD CSM | One Opportunity Twin spanning several phases, programmes, procurements, suppliers, theses and Evidence Demands. | Supported. |
| Hypothetical communications opportunity | An opportunity may exist before procurement when churn, network modernisation, service pressure or platform consolidation evidence supports need; accessibility may remain weak until route evidence appears. | Supported with Caveats. |
| Hypothetical energy or utilities opportunity | Strong grid, resilience or regulatory need can be represented while Provider Fit remains weak or unknown; deferral is allowed when access is closed or incumbents dominate. | Supported with Caveats. |
| Multi-procurement opportunity | Several procurements link to one opportunity without becoming the opportunity identity. | Supported. |
| Weak accessibility | Enterprise Need remains separate from Commercial Accessibility and Decision Envelope can block pursuit. | Supported. |
| Deferred or rejected opportunity | Lifecycle can become Deferred or Rejected while preserving evidence, hypotheses and lessons. | Supported. |
| Opportunity changes over time | State history, freshness, Evidence Demands, outcomes and learning preserve evolution. | Supported. |

## 18. Completion report

- Opportunity has one clear definition in section 1.
- Opportunity Twin ownership is reconciled with EI-006 as a subordinate Review specification.
- Procurement is subordinate to opportunity.
- Enterprise Need, Commercial Accessibility and Provider Fit remain separate.
- Durable memory is supported by identity, lineage, lifecycle, outcomes and learning fields.
- Transient reports remain views.
- CSM can be represented cleanly without universalising CSM-specific detail.
- Future enterprise Twins across sectors are supported through portfolio, relationship and evidence-bound field design.
- Conflicts and Unknowns are explicitly recorded in section 0.
