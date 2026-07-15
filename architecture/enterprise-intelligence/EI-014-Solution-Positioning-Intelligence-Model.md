# EI-014 — Solution Positioning Intelligence Model

**Document class:** Enterprise Intelligence model  
**Status:** Review  
**Authority:** Proposed Enterprise Intelligence Model  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-15  
**Production behaviour:** Documentation-only architecture. Does not introduce runtime behaviour, generate proposals, change production Researcher packs, change production Assurance packs or assume Provider Fit.  
**Release-profile membership:** none — excluded from production Researcher and Assurance profiles

## 1. Purpose

EI-014 defines the canonical Enterprise Intelligence model that transforms an evidence-governed Opportunity Twin into Solution Positioning Intelligence suitable for executive engagement, solution strategy, bid development and commercial narrative.

EI-014 fills the architectural gap between Opportunity Intelligence and executive positioning. Current architecture can produce Enterprise Foundation, Enterprise Change Mechanisms, Opportunity Discovery and Opportunity Twins. EI-014 defines how a selected Opportunity Twin becomes governed positioning intelligence without becoming proposal text, supplier selection or runtime behaviour.

EI-014 does not generate proposals. It generates governed positioning intelligence.

## 2. Architectural position

EI-014 sits immediately after OT-001 in the Enterprise Intelligence reasoning chain:

```text
Enterprise Foundation (EIF)
  ↓
Enterprise Change Mechanisms
  ↓
Enterprise Opportunity Discovery (EOD)
  ↓
Opportunity Twin (OT)
  ↓
Solution Positioning Intelligence (EI-014)
  ↓
Executive Narrative
  ↓
Bid Strategy
```

This position matters because executive positioning must be derived from durable enterprise memory, evidence-backed observations, Knowledge Graph relationships, hypothesis-led reasoning and the selected Opportunity Twin. It must not be invented directly for a pursuit or inferred from provider capability.

## 3. Definition

Solution Positioning Intelligence is the governed interpretation of how evidence-backed enterprise transformation requirements map to coherent solution capability choices and executive narratives.

It identifies:

- executive problems;
- desired business outcomes;
- transformation success measures;
- solution capability themes;
- positioning messages;
- candidate solution architectures;
- executive narratives.

These outputs are durable intelligence objects. They are not proposal copy, bid responses, supplier recommendations or marketing collateral.

## 4. Core principles

1. **Positioning is not selling.** Positioning is the evidence-governed interpretation of how enterprise transformation requirements map to coherent solution capabilities.
2. **Recommendations remain evidence-backed.** Every material positioning assertion must carry lineage to Opportunity Twin evidence, Enterprise Model state, Observations, graph relationships or validated hypotheses.
3. **Unknowns remain explicit.** EI-014 records missing evidence, unvalidated assumptions and unresolved executive questions rather than hiding them inside persuasive language.
4. **Provider capability remains outside EI-014.** EI-014 can describe capabilities an enterprise may need. It must not evaluate suppliers, recommend providers or assume Provider Fit.
5. **Capabilities are not products.** EI-014 works at the level of enterprise and solution capabilities, not named offerings, delivery promises or implementation designs.
6. **Narrative is an intelligence view.** Executive Narrative objects summarise reasoning for executive engagement; they do not become generated proposal sections.

## 5. Canonical positioning objects

### 5.1 Executive Problem

The Executive Problem is the business problem the executive is actually trying to solve.

Required fields:

| Field | Definition |
| --- | --- |
| `description` | Concise statement of the executive problem, separated from symptoms and procurement language. |
| `drivers` | Enterprise pressures, change mechanisms, constraints or external forces causing the problem. |
| `affected_executives` | Executive roles or decision owners affected by the problem. |
| `evidence` | Evidence, Observations, graph relationships and Opportunity Twin references supporting the problem statement. |
| `confidence` | Confidence level and rationale. |
| `unknowns` | Missing evidence, unresolved questions and assumptions requiring validation. |

### 5.2 Executive Outcomes

Executive Outcomes are the desired enterprise outcomes implied by the Opportunity Twin and executive problem.

Examples include lower operating cost, reduced delivery risk, improved resilience and improved customer experience.

Required fields:

| Field | Definition |
| --- | --- |
| `outcome` | Business outcome sought by the enterprise. |
| `evidence` | Evidence or reasoning lineage showing why this outcome matters. |
| `success_indicators` | Measures or observable indicators that would show progress or success. |
| `dependencies` | Enterprise, governance, delivery, data, technology or stakeholder dependencies. |

### 5.3 Positioning Theme

A Positioning Theme is a reusable strategic message that connects enterprise need to a coherent solution capability direction.

Examples include:

- Deliver Transformation with Confidence;
- Accelerate Customer Migration;
- Modernise Operational Assurance.

Required fields:

| Field | Definition |
| --- | --- |
| `rationale` | Why the theme fits the Opportunity Twin and executive problem. |
| `evidence` | Evidence, Observations, hypotheses or graph relationships supporting the theme. |
| `related_mechanisms` | Enterprise Change Mechanisms or transformation pressures related to the theme. |
| `related_opportunity_twins` | Opportunity Twins that the theme helps interpret or connect. |

### 5.4 Solution Capability

A Solution Capability is a non-product capability that may be required to address the executive problem.

Examples include Programme Intelligence, Enterprise Integration, Data Governance, AI Operations, Service Management and Executive Reporting.

Required fields:

| Field | Definition |
| --- | --- |
| `purpose` | What the capability enables for the enterprise. |
| `executive_value` | Why the capability matters to executive outcomes and decision makers. |
| `dependencies` | Other capabilities, enterprise prerequisites or evidence conditions needed for the capability to be credible. |
| `enabling_capabilities` | Supporting capabilities that make the capability viable. |

### 5.5 Candidate Solution Architecture

A Candidate Solution Architecture is a high-level capability grouping. It is not an implementation architecture, delivery plan or product stack.

Required fields:

| Field | Definition |
| --- | --- |
| `description` | Summary of the candidate capability grouping. |
| `capabilities` | Solution Capabilities included in the grouping. |
| `executive_outcomes_supported` | Executive Outcomes the grouping is intended to support. |
| `strengths` | Evidence-backed advantages of this grouping for the opportunity context. |
| `limitations` | Constraints, risks, gaps or contexts where the grouping may be insufficient. |
| `assumptions` | Assumptions requiring validation before use in bid strategy or engagement. |

### 5.6 Executive Narrative

The Executive Narrative is the one-page intelligence story explaining:

- why change;
- why now;
- why this approach;
- why success is achievable.

It must remain evidence-backed, concise and transparent about confidence and Unknowns. It is not marketing collateral and must not claim supplier-specific ability.

### 5.7 Decision Envelope Alignment

Decision Envelope Alignment explains how the proposed capability architecture aligns with:

- executive decisions;
- governance;
- business priorities;
- transformation constraints.

It should show which executive decision each capability theme supports, what governance route may be needed, which business priorities are addressed and which constraints remain material.

### 5.8 Unknown Register

The Unknown Register records:

- unanswered questions;
- missing evidence;
- assumptions requiring validation.

Unknowns remain first-class positioning objects. They prevent unsupported assertions from becoming executive narrative, bid strategy or provider assumptions.

## 6. Relationship to existing architecture

EI-014 consumes outputs from existing architecture but does not replace them.

| Architecture | EI-014 relationship |
| --- | --- |
| EIF-001 | Consumes Enterprise Foundation and Enterprise Change Mechanisms as context for why an opportunity matters. EI-014 does not perform Foundation work. |
| EOD-001 | Consumes opportunity portfolio reasoning and selected opportunity context. EI-014 does not discover or prioritise opportunities. |
| OT-001 | Uses the Opportunity Twin as the immediate input. EI-014 starts after OT-001 and must preserve OT evidence, Unknowns, contradictions and confidence. |
| EI-001 | Preserves Enterprise Models as durable memory. EI-014 adds positioning objects as derived intelligence, not as report-only text. |
| EI-002 | Uses Knowledge Graph relationships among executives, capabilities, pressures, evidence and opportunities. EI-014 does not redefine graph semantics. |
| EI-003 | Uses behaviour and transformation interpretation to frame executive problems and capability themes. EI-014 does not redefine enterprise behaviour. |
| EI-012 | Preserves Observations as intelligence atoms. EI-014 positioning claims must trace to evidence-backed Observations or explicit assumptions. |
| FP-009 | Uses hypothesis-led reasoning to keep positioning testable and falsifiable. EI-014 does not convert unvalidated hypotheses into facts. |

The progression is therefore preserved: Enterprise Models provide durable memory; Observations provide intelligence atoms; Knowledge Graph relationships preserve context; hypothesis-led reasoning tests interpretation; EI-014 turns the selected Opportunity Twin into governed positioning intelligence.

## 7. CSM worked example — MOD CSM Opportunity Twin

This example illustrates reasoning only. It contains no supplier-specific content, no Provider Fit and no proposal.

```text
Executive Problem
  ↓
Executive Outcomes
  ↓
Positioning Themes
  ↓
Solution Capabilities
  ↓
Executive Narrative
```

### 7.1 Executive Problem

A defence enterprise responsible for CSM needs to sustain and modernise a complex service environment while reducing delivery risk, preserving operational continuity and giving senior accountable leaders confidence that transformation can be governed across organisational, supplier and technical boundaries.

Evidence lineage would come from the MOD CSM Opportunity Twin, relevant enterprise mechanisms, public-domain programme evidence, Observations and Unknowns recorded during validation.

Unknowns include the precise decision route, current operating pain points, detailed governance constraints, integration scope and success measures that are not yet evidenced.

### 7.2 Executive Outcomes

Candidate Executive Outcomes include:

- reduced transformation delivery risk;
- improved assurance over programme progress and dependencies;
- improved operational resilience during change;
- clearer executive visibility of risk, performance and decisions;
- more coherent migration from current service state to target operating outcomes.

Success indicators may include fewer unmanaged dependencies, clearer executive decision points, stronger service continuity evidence, measurable transition readiness and inspectable issue-to-decision lineage.

### 7.3 Positioning Themes

Candidate Positioning Themes include:

- **Deliver Transformation with Confidence** — emphasises assurance, governance and evidence-backed delivery control;
- **Modernise Operational Assurance** — connects service continuity, risk visibility and governance to transformation success;
- **Create Executive Line of Sight** — links programme intelligence to senior decision confidence.

### 7.4 Solution Capabilities

Candidate Solution Capabilities include:

- Programme Intelligence;
- Enterprise Integration;
- Data Governance;
- Service Management;
- Executive Reporting;
- Operational Assurance.

These capabilities are not products and do not imply any supplier. They describe the capability shape that may be needed for the executive outcomes.

### 7.5 Executive Narrative

The executive story is that CSM change is not only a technology or service transition problem. It is an enterprise assurance problem: senior leaders need confidence that operational continuity, risk, dependencies and transformation progress can be governed together. A capability architecture centred on Programme Intelligence, Service Management, Data Governance, Enterprise Integration and Executive Reporting would support a more inspectable route from current complexity to governed transformation outcomes, while preserving Unknowns that require validation before bid strategy.

## 8. Vodafone worked example — VodafoneThree Opportunity Twin

This example illustrates reasoning only. It contains no supplier-specific content, no Provider Fit and no proposal.

```text
Executive Problem
  ↓
Executive Outcomes
  ↓
Positioning Themes
  ↓
Solution Capabilities
  ↓
Executive Narrative
```

### 8.1 Executive Problem

A newly combined telecommunications enterprise needs to realise merger and transformation value while managing customer migration, operational integration, resilience, regulatory scrutiny and executive confidence across a complex multi-year change agenda.

Evidence lineage would come from the selected VodafoneThree Opportunity Twin, Enterprise Foundation, Enterprise Change Mechanisms, public-domain merger and transformation evidence, Observations and recorded Unknowns.

Unknowns include confirmed integration priorities, customer migration sequencing, governance cadence, operational bottlenecks, current assurance tooling and detailed success measures.

### 8.2 Executive Outcomes

Candidate Executive Outcomes include:

- accelerated but controlled customer migration;
- lower integration and operating risk;
- improved customer experience during change;
- improved resilience across combined operations;
- clearer executive visibility of synergy delivery, risk and constraints.

Success indicators may include migration readiness, service stability during transition, reduction in duplicated processes, improved issue resolution visibility and evidence of benefits realisation governance.

### 8.3 Positioning Themes

Candidate Positioning Themes include:

- **Accelerate Customer Migration** — connects transformation pace with customer and operational confidence;
- **Integrate Operations Without Losing Control** — frames integration as an assurance and operating-model challenge;
- **Make Synergy Delivery Inspectable** — links executive governance to benefits realisation and risk transparency.

### 8.4 Solution Capabilities

Candidate Solution Capabilities include:

- Programme Intelligence;
- Enterprise Integration;
- Data Governance;
- AI Operations;
- Service Management;
- Executive Reporting;
- Customer Migration Assurance.

These are capability requirements, not products, suppliers or implementation commitments.

### 8.5 Executive Narrative

The executive story is that VodafoneThree transformation value depends on making integration, customer migration and operational resilience governable at executive level. The opportunity is to treat migration and integration as an evidence-led transformation system, not a set of disconnected workstreams. A capability architecture centred on Programme Intelligence, Enterprise Integration, Data Governance, AI Operations, Service Management and Executive Reporting would support a more controlled route to customer, operational and synergy outcomes, while preserving Unknowns that require validation before engagement or bid strategy.

## 9. Flora relationship

Flora should eventually treat the following as governed Commercial Digital Twin objects:

- Executive Problems;
- Executive Outcomes;
- Positioning Themes;
- Solution Capabilities;
- Executive Narratives.

These objects should remain evidence-backed and carry lineage, confidence and freshness. Flora should expose them as Commercial Digital Twin intelligence state, not as generated proposal content. Runtime implementation, user interaction and promotion rules are outside EI-014 and require separate architecture authority before delivery.

## 10. Constraints

EI-014 must not:

- generate proposals;
- recommend suppliers;
- evaluate Provider Fit;
- produce bid responses;
- create marketing collateral;
- introduce runtime behaviour;
- promote EI-014 or other Review material into production profiles.

## 11. Acceptance criteria

EI-014 is acceptable when it:

- defines Solution Positioning Intelligence;
- bridges Opportunity Twins to executive positioning;
- preserves evidence lineage;
- preserves Unknowns;
- avoids Provider Fit;
- remains architecture-only;
- improves Commercial Digital Twin completeness.
