# IC-001 — Enterprise Foundation Intelligence Commission

**Document class:** Operational Commission Standard
**Status:** Review
**Owner:** Rob / CIOS
**Last updated:** 2026-07-16
**Production behaviour:** Documentation-only operational template. It introduces no runtime behaviour, changes no architecture or canonical model, and is excluded from production Researcher and Assurance packs until it has been validated across multiple enterprises.
**Implements:** EIF-001 — Enterprise Intelligence Foundation Model

## 1. Purpose

IC-001 is the canonical, reusable operational commission for instructing a Researcher GPT to construct an Enterprise Foundation using approved CIOS architecture. It standardises execution; it does not alter architecture.

IC-001 is not enterprise-specific. A commission instance consists of this reusable template plus an Enterprise Configuration. The configuration supplies context; it does not change the commission, architecture or acceptance boundaries.

## 2. Architectural position

```text
Architecture
        ↓
Operational Commission
        ↓
Enterprise Configuration
        ↓
Researcher GPT
        ↓
Enterprise Foundation
```

- **Architecture defines capability.**
- **Intelligence Commissions define execution.**
- **Enterprise Configurations provide context.**

IC-001 consumes architecture. It does not redefine architecture, Enterprise Models, Opportunity Twins or EIF.

## 3. Scope and operating boundary

IC-001 commissions construction of an Enterprise Foundation from public-domain information. It is Foundation-only: it does not discover or select opportunities, create an Opportunity Twin, assess Provider Fit, recommend a provider, or treat a procurement as an opportunity.

All work remains public-domain unless the Mission Configuration explicitly instructs otherwise. Any non-public material must be clearly labelled with its authority, access constraint and handling boundary; it must not be presented as public evidence.

## 4. Required configuration model

An IC-001 instance must be accompanied by a complete Enterprise Configuration with the following fields.

### 4.1 Enterprise Configuration

| Field | Required content |
| --- | --- |
| Enterprise Name | The enterprise to be researched. |
| Industry | The enterprise's relevant industry or industries. |
| Geography | Relevant operating, regulatory and market geographies. |
| Enterprise Boundary | Included and excluded organisations, activities, periods and geographies. |
| Known Regulators | Regulators known at commission start. |
| Known Parent Organisations | Parent, holding or controlling organisations known at commission start. |
| Known Operating Entities | Material operating entities, divisions or subsidiaries known at commission start. |
| Known Public Information Sources | Known authoritative or useful public sources, without treating the list as exhaustive. |

### 4.2 Mission Configuration

| Field | Required content |
| --- | --- |
| Intelligence Objective | What the Foundation must enable a decision-maker to understand. |
| Validation Objective | What must be tested, corroborated or bounded before completion. |
| Applicable Architecture | Applicable authoritative and Review architecture references. |
| Applicable Pattern Library | Applicable reusable patterns, if any; absence must be explicit. |
| Public Information Constraints | Jurisdictional, source, time, language, access and use constraints. |
| Known Unknowns | Questions and gaps known before research begins. |

### 4.3 Runtime Configuration

| Field | Required content |
| --- | --- |
| Expected Deliverables | Deliverables requested in addition to the mandatory outputs, if any. |
| Completion Criteria | Instance-specific criteria that supplement, but do not weaken, section 9. |
| Output Format | Required formats, structure and destination for outputs. |
| Flora Import Required (Yes/No) | Whether a Flora Import Manifest must be prepared for the commission instance. |

Missing, ambiguous or conflicting configuration is an explicit Unknown or Contradiction. It must be recorded, not silently resolved.

## 5. Mandatory principles

Every Intelligence Commission must:

1. preserve Unknowns;
2. preserve Contradictions;
3. distinguish evidence from inference;
4. distinguish enterprise from opportunity;
5. distinguish opportunity from procurement;
6. distinguish public evidence from Provider Fit;
7. explain commercial significance;
8. preserve evidence lineage;
9. produce durable Enterprise Intelligence objects; and
10. remain public-domain unless explicitly instructed otherwise.

## 6. Standard workflow

The Researcher GPT must execute the following generic sequence. A step may iterate when new evidence requires revision, but it may not be omitted without an explicit recorded rationale.

1. Establish Enterprise Boundary.
2. Establish Information Boundary.
3. Gather Public Evidence.
4. Construct Enterprise Identity.
5. Construct Enterprise Purpose.
6. Construct Enterprise Value Model.
7. Construct Enterprise Operating Model.
8. Construct Enterprise Behaviour Model.
9. Construct Enterprise Technology & Data Capability Model.
10. Construct Enterprise Ecosystem.
11. Construct Enterprise Risk Landscape.
12. Construct Enterprise Change Landscape.
13. Identify Enterprise Change Mechanisms.
14. Identify Executive Tensions.
15. Generate Executive Questions.
16. Produce Enterprise Capability Heat Map.
17. Construct Transformation Narrative.
18. Construct Enterprise Timeline.
19. Produce Decision Envelope.
20. Produce Evidence Demand Register.
21. Produce Strategic Watch.
22. Produce Flora Import Manifest.
23. Produce Researcher Reflection.

At each step, material claims must identify their supporting public evidence, any inference made, confidence, unresolved Unknowns, Contradictions and commercial significance. The commission must add only durable Enterprise Intelligence objects within the boundaries of the applicable architecture; it must not make a report the canonical memory.

## 7. Mandatory outputs

The commission must produce the following output structure. Each output must be attributable to the Enterprise Configuration, identify its evidence lineage, and preserve relevant Unknowns and Contradictions.

| Output | Minimum purpose |
| --- | --- |
| Executive Brief | Decision-oriented summary of Foundation findings, material uncertainty and commercial significance. |
| Enterprise Identity | Bounded identity, ownership, entities, geography and relationships. |
| Enterprise Purpose | Mandate, purpose, strategic intent and stakeholder obligations. |
| Enterprise Value Model | How value, funding, costs, outcomes and constraints relate. |
| Enterprise Operating Model | Material capabilities, operating structure and delivery model. |
| Enterprise Behaviour Model | Evidence-backed behavioural patterns with confidence. |
| Technology Capability Model | Technology and data capabilities, dependencies and gaps within public evidence limits. |
| Enterprise Ecosystem | Ecosystem actors, dependencies, regulators and material relationships. |
| Enterprise Risk Landscape | Material enterprise risks, exposures, controls and uncertainties. |
| Enterprise Change Landscape | Current and emerging change pressures, initiatives and external forces. |
| Enterprise Change Mechanisms | Mechanisms by which change is initiated, governed, funded or delivered. |
| Executive Tensions | Material competing priorities, constraints or trade-offs. |
| Executive Questions | Decision-relevant questions generated from evidence, tensions and Unknowns. |
| Capability Heat Map | Evidence-backed view of capability strength, pressure, uncertainty and change relevance. |
| Transformation Narrative | Coherent, bounded account of transformation direction, drivers and implications. |
| Enterprise Timeline | Dated material events, commitments, changes and expected milestones. |
| Decision Envelope | What can and cannot responsibly be concluded, decided or pursued from the Foundation. |
| Evidence Demand Register | Prioritised evidence gaps, validation needs, owners where known and intended decision impact. |
| Strategic Watch | Signals, events and evidence demands that require continuing observation. |
| Flora Import Manifest | Traceable inventory of candidate objects and evidence for Flora import, including import status; required even when Flora import is not requested, in which case it records `not requested`. |
| Researcher Reflection | Self-assessment of coverage, confidence, limitations, changed assumptions and recommended next validation actions. |

## 8. Quality gates

All quality gates are mandatory. A failure blocks completion until remediated or explicitly recorded as an unmet completion criterion.

| Quality gate | Pass criteria | Fail criteria |
| --- | --- | --- |
| Evidence Quality | Every material claim has inspectable public evidence lineage, source identity and a clear evidence/inference distinction; material source limitations are explicit. | A material claim lacks lineage, relies on unlabelled non-public information, or presents inference as evidence. |
| Enterprise Boundary Quality | Included and excluded entities, activities, geographies and periods are explicit; material boundary ambiguity is an Unknown or Contradiction. | The researched enterprise cannot be distinguished from related entities, markets or excluded activity. |
| Behaviour Confidence | Behaviour findings cite supporting evidence, use bounded confidence and preserve credible alternatives. | Behaviour is asserted as fact without adequate evidence, confidence or alternatives. |
| Change Mechanism Quality | Each material mechanism identifies trigger, actors, governance or funding path where evidenced, expected effect and uncertainty. | Change is described only as an event or initiative, with no evidenced mechanism or uncertainty boundary. |
| Executive Utility | The Executive Brief, Questions, Tensions and Decision Envelope make the decision context, implications and Unknowns actionable. | Outputs are descriptive only, obscure uncertainty or do not support an executive decision conversation. |
| Commercial Utility | Commercial significance is explained without converting enterprise intelligence into opportunity, procurement, Provider Fit or recommendation. | Commercial claims conflate those categories or lack an evidence-backed significance statement. |
| Flora Import Completeness | The manifest inventories all eligible durable objects and linked evidence, records disposition, and explicitly records `not requested` when applicable. | The manifest is absent, incomplete, lacks lineage or fails to state its import disposition. |

## 9. Completion criteria

A commission completes only when:

1. the Mission Success Test passes against the Intelligence Objective and Validation Objective;
2. all mandatory outputs exist;
3. Unknowns are explicit;
4. the Decision Envelope is complete;
5. the Evidence Demand Register is complete;
6. the Flora Import Manifest is complete; and
7. the Researcher Reflection is complete.

Passing completion means the Foundation is sufficiently complete for its stated decision purpose, not that the enterprise is fully known or that all uncertainty has been eliminated.

## 10. Relationship to architecture

IC-001 cross-references, and does not duplicate, the following authorities:

| Authority | IC-001 relationship |
| --- | --- |
| EIF-001 | Defines the Enterprise Foundation method implemented by this commission. |
| EI-001 | Owns the Enterprise Model and durable Enterprise Intelligence boundaries. |
| EI-002 | Owns Enterprise Knowledge Graph entities and relationships. |
| EI-003 | Owns Enterprise Behaviour Model semantics and confidence handling. |
| EI-012 | Owns Observations, evidence lineage and lifecycle semantics. |
| FP-009 | Owns hypothesis validation and learning discipline. |
| OT-001 | Remains downstream; IC-001 does not construct an Opportunity Twin. |
| EI-014 | Remains downstream; IC-001 does not create solution positioning intelligence or Provider Fit. |

## 11. Relationship to Assurance

Assurance GPT validates:

- commission compliance;
- architectural compliance;
- evidence discipline; and
- operational completeness.

Assurance does not change Research conclusions. It may identify a non-compliance, missing evidence, unsupported inference, unclear boundary or incomplete output, but must preserve the Researcher's conclusion and record its assurance finding separately.

## 12. Extensibility

Future Intelligence Commissions inherit IC-001's operating philosophy: architecture-led capability, reusable execution, configuration-provided context, evidence discipline, durable objects and explicit uncertainty.

Planned commissions are:

- IC-002 — Enterprise Opportunity Discovery;
- IC-003 — Opportunity Twin;
- IC-004 — Enterprise Intelligence Pattern Extraction; and
- IC-005 — Solution Positioning Intelligence.

These commissions are not created or implied by IC-001.

## 13. Repository pattern and validation status

Operational commissions are held separately from architecture at:

```text
operations/
    intelligence-commissions/
        IC-001-Enterprise-Foundation-Intelligence-Commission.md
```

This establishes the operational-layer pattern without moving existing architecture. IC-001 remains Review material and must not be included in production Researcher or Assurance packs until validation across multiple enterprises has been completed through a separate accepted governance decision.
