# EOD-001 — Enterprise Opportunity Discovery Standard

**Document class:** Reference architecture standard  
**Status:** Review  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-14  
**Production behaviour:** Documentation-only architecture standard. Does not change runtime behaviour, production Researcher packs, Enterprise Model, Observation Model, Knowledge Graph, AP-001 or AP-002.  
**Relationship:** EOD precedes EIRS.

## Purpose

Define how CIOS discovers opportunities before researching them.

EOD-001 establishes an enterprise-first discovery method so future Research Sprints no longer assume that the opportunity is already known.

## Mission

Given an enterprise, identify all commercially significant transformation opportunities.

Do not begin with a known procurement. Research the enterprise first, then identify the opportunity portfolio, then select and validate the research object.

## Principles

1. Research the enterprise, not the procurement.
2. Procurements are evidence of change, not the definition of opportunity.
3. Preserve Unknowns.
4. Preserve Contradictions.
5. Do not infer future procurements without evidence.
6. Separate evidence, interpretation, projection and commercial judgement.
7. Maintain public-domain boundaries.
8. Keep Provider Fit separate from public research.

## Required outputs

### 1. Enterprise Change Portfolio

Identify all significant enterprise change initiatives supported by public-domain evidence.

For each initiative capture:

- name or working title;
- enterprise owner or sponsor where evidenced;
- stated purpose;
- business driver;
- impacted functions, capabilities or populations;
- public evidence references;
- confidence;
- freshness;
- unknowns and contradictions.

### 2. Programme Landscape

Identify every significant programme related to enterprise transformation.

For each programme include:

- purpose;
- status;
- dependencies;
- intended outcomes;
- related procurements;
- related platforms;
- known or likely suppliers where evidenced;
- evidence confidence;
- freshness;
- unknowns and contradictions.

### 3. Procurement Landscape

Identify every publicly evidenced procurement related to enterprise transformation.

For every procurement capture:

- title;
- aliases;
- reference;
- status;
- value;
- route;
- buyer;
- relationship to programme, platform, supplier or opportunity;
- confidence;
- freshness;
- unknowns and contradictions.

### 4. Opportunity Landscape

For every opportunity assess:

- Enterprise Importance;
- Commercial Accessibility;
- Evidence Confidence;
- Maturity;
- Transformation Dependency;
- Decision Urgency;
- Unknowns;
- contradictions;
- rationale for assessment.

### 5. Programme Relationship Map

Produce relationships between:

- programmes;
- procurements;
- platforms;
- suppliers;
- dependencies;
- enterprise outcomes;
- emerging opportunities.

The relationship map must distinguish evidenced relationships from inferred relationships and must preserve contradictions.

### 6. Emerging Opportunities

Identify opportunities that are expected but not yet publicly procured only when supported by evidence.

For each emerging opportunity state:

- evidence basis;
- why the opportunity is expected;
- what is not yet evidenced;
- what would falsify or weaken the expectation;
- confidence;
- freshness;
- caveats.

Do not infer future procurements merely because a programme exists.

### 7. Opportunity Prioritisation

Recommend which opportunities deserve full Research Sprints and explain why.

Prioritisation should consider:

- enterprise importance;
- commercial accessibility;
- evidence confidence;
- maturity;
- transformation dependency;
- decision urgency;
- potential strategic value;
- unresolved evidence demand;
- risk of false anchoring.

### 8. Decision Envelope

State one of:

- **Supported** — public-domain evidence supports the opportunity selection for a full Research Sprint.
- **Supported with Caveats** — the opportunity appears researchable, but material unknowns, contradictions, dependencies or freshness issues must be carried into Research Object Validation.
- **Not Supported** — the evidence does not support selection, or selection would require unsupported inference.

### 9. Evidence Demand Register

Prioritise missing evidence.

For each evidence demand capture:

- question;
- why it matters;
- target evidence type;
- likely source class;
- priority;
- impact if unresolved;
- whether unresolved evidence blocks opportunity selection or can be carried as a caveat.

## EOD lifecycle position

EOD precedes EIRS.

The enterprise intelligence lifecycle is:

1. Enterprise.
2. Enterprise Opportunity Discovery.
3. Opportunity Selection.
4. Research Object Validation.
5. Enterprise Understanding.
6. Research-to-Positioning Handover.
7. Opportunity Positioning.
8. Positioning Insight Deepening.
9. Decision Envelope.
10. Provider Fit outside public research.
11. Executive Pursuit.
12. Learning.

## Boundary with EIRS

EOD identifies and prioritises opportunity candidates. EIRS researches a selected and validated opportunity.

EOD must not produce provider-specific fit claims. Provider Fit requires private account knowledge, delivery capability context or supplier-specific qualification and is outside public-domain research.

## CSM validation demonstration

Applied to the completed CSM sprint, EOD would have required enterprise-first mapping before any procurement anchor was selected. That mapping would have searched for CSM transformation initiatives, programmes, procurements, platform dependencies and supplier relationships.

The Enterprise Change Portfolio and Programme Landscape would have identified multiple candidate transformation objects, including Transformation Partner, Implementation Partner, Phase 2, Phase 2b, Oracle and related procurements, without requiring Rob to already know about SIDP.

The Procurement Landscape would then have treated SIDP and related procurements as evidence within a broader programme relationship map, not as the definition of the opportunity. Opportunity Selection would have compared the candidate opportunities before Research Object Validation chose the object for a full Research Sprint.

This remains a Review validation demonstration, not Accepted evidence that the method generalises across all enterprises.
