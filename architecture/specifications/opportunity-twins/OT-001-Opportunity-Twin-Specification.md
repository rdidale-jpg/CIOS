# OT-001 — Opportunity Twin Specification

**Document class:** Review specification
**Status:** Review
**Authority:** proposed method / proposed operational contract
**Owner:** Rob / CIOS
**Last updated:** 2026-07-14
**Production behaviour:** documentation-only
**Release-profile membership:** none — excluded from production Researcher and Assurance profiles

## Purpose

OT-001 defines the current Review version of the Opportunity Twin as a governed, evidence-aware model of a commercial opportunity. It makes opportunity state inspectable without changing runtime behaviour, production Researcher packs, production Assurance packs, the Enterprise Model, the Observation Model or the Knowledge Graph.

## Authority boundary

OT-001 remains Review material pending wider validation. It is not Accepted architecture and must not be treated as production Researcher or Assurance authority.

Ownership remains beneath **EI-006 — Opportunity Prediction Engine**. OT-001 specifies the Review interface and object shape for Opportunity Twin material under EI-006; it does not move or dilute EI-006 ownership.

## Opportunity Twin contents

An Opportunity Twin may contain:

- opportunity identity, aliases and scope;
- enterprise context and affected capabilities;
- opportunity need, pressure, timing and decision route;
- known stakeholders, sponsors, blockers and participant relationships;
- evidence, Observations, Unknowns and Contradictions;
- candidate positioning objects supplied by OPI-001;
- governed Research-to-Positioning handover material supplied under RTP-001;
- hypotheses, recommendation lineage and next learning actions;
- confidence, freshness and validation status for each material claim.

## Interface relationships

| Interface | Relationship | Status |
| --- | --- | --- |
| EI-006 | EI-006 owns Opportunity Prediction and remains the owning Enterprise Intelligence paper for Opportunity Twin logic. | Accepted owner / OT-001 Review specification |
| OPI-001 | OPI-001 contributes candidate positioning objects to the Opportunity Twin, including candidate opportunity narratives, value hypotheses, buyer-problem framing, differentiation angles, evidence demands and positioning Unknowns. | Explicit Review relationship |
| RTP-001 | RTP-001 defines the governed handover from Research to Positioning, including what evidence, Unknowns, Contradictions, caveats and decision envelope must be carried before positioning work consumes research outputs. | Explicit Review relationship |
| FP-009 | Opportunity hypotheses and recommendations remain subject to hypothesis validation and inspectable lineage. | Accepted dependency |
| EI-012 | Evidence-backed Observations, Unknowns and Contradictions retain EI-012 semantics. | Accepted dependency |

## Positioning-object contribution from OPI-001

OPI-001 may contribute candidate positioning objects to an Opportunity Twin only as Review material. Candidate positioning objects must remain labelled as candidate, must carry lineage or evidence demand, and must not be promoted to accepted opportunity truth without the owning validation path.

The candidate positioning object set may include:

- candidate opportunity positioning statement;
- target buyer or stakeholder frame;
- problem and pressure narrative;
- value hypothesis;
- differentiated angle or wedge;
- proof points and evidence gaps;
- objections, blockers and contradiction notes;
- next learning action.

## Research-to-Positioning handover from RTP-001

RTP-001 defines the governed handover from Research to Positioning. OT-001 consumes that handover as an explicit interface rather than an Unknown relationship.

The handover must preserve:

- source and evidence lineage;
- selected opportunity object and scope;
- material Unknowns and Contradictions;
- confidence, freshness and caveats;
- unsupported assumptions that must not be used as facts;
- decision envelope for whether positioning work may proceed;
- validation notes explaining why the material remains Review rather than Accepted.

## Review validation requirements

Before OT-001, OPI-001 or RTP-001 can be promoted beyond Review, they require validation across materially different enterprises and opportunity types. Until then, all three remain documentation-only Review material pending wider validation.
