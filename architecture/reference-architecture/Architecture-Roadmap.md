# CIOS Architecture Roadmap

**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

This roadmap aligns implementation phases to the Reference Architecture. It is intentionally architecture-led: runtime work should cite the relevant papers before changing product behaviour.

## 1. Runtime alignment to Reference Architecture

- **Purpose:** Align Flora, Newton, Observatory and Publisher terminology with CIRM, Enterprise Intelligence and the Reference Architecture.
- **Major dependencies:** Reference Architecture v1.0, architecture README, Enterprise Intelligence README, CIRM runtime compliance material.
- **Architecture papers required:** FP-003 to FP-009, EI-001 to EI-012.
- **Expected product impact:** Consistent navigation, naming, traceability and PR compliance expectations.

## 2. Observation Engine

- **Purpose:** Create Observations from accepted evidence and make them the reusable atom of Enterprise Intelligence.
- **Major dependencies:** evidence acceptance, source quality scoring, Observation schema, freshness and decay policy.
- **Architecture papers required:** EI-012, FP-004, FP-005, FP-006.
- **Expected product impact:** Less repeated reasoning over raw evidence; stronger memory, lineage and contradiction handling.

## 3. Enterprise Model runtime

- **Purpose:** Persist durable Enterprise Models as maintained Commercial Digital Twins.
- **Major dependencies:** model data contract, Observation updates, entity identity, attribute provenance.
- **Architecture papers required:** EI-001, EI-003, EI-011, EI-012.
- **Expected product impact:** Executive views and reports become renders of durable enterprise memory.

## 4. Knowledge Graph runtime

- **Purpose:** Connect enterprise entities, relationships and temporal evidence-backed edges.
- **Major dependencies:** Enterprise Model runtime, entity resolution, relationship typing, contradiction model.
- **Architecture papers required:** EI-002, EI-007, EI-012.
- **Expected product impact:** Queryable relationship intelligence across executives, suppliers, contracts, technologies and transformation themes.

## 5. Source Discovery and Recovery

- **Purpose:** Improve source coverage, detect degraded sources and recover collection capability.
- **Major dependencies:** source yield scoring, source lifecycle tracking, collection diagnostics.
- **Architecture papers required:** FP-004, FP-005, FP-006, future Source Discovery and Recovery Architecture.
- **Expected product impact:** More resilient collection and clearer explanations for missing or weak evidence.

## 6. Procurement Intelligence

- **Purpose:** Model procurement activity, contract timing, incumbent blockers and commercial accessibility.
- **Major dependencies:** evidence sources for procurement, contract graph edges, opportunity prediction model.
- **Architecture papers required:** EI-006, EI-002, future Procurement Intelligence Architecture.
- **Expected product impact:** Better distinction between enterprise need and reachable commercial opportunity.

## 7. People and Executive Intelligence

- **Purpose:** Model leadership, governance, executive mandates, ownership and influence.
- **Major dependencies:** permissible people sources, executive freshness, relationship graph, human-supplied labelling.
- **Architecture papers required:** EI-007, EI-002, future People and Executive Intelligence Source Standard.
- **Expected product impact:** Stronger account planning, executive recommendations and relationship-aware opportunity shaping.

## 8. Enterprise Economics

- **Purpose:** Model financial pressure, cost structure, value drivers and economic constraints.
- **Major dependencies:** financial evidence, enterprise economics attributes, pressure and momentum models.
- **Architecture papers required:** EI-011, EI-009, EI-010.
- **Expected product impact:** Commercial reasoning reflects economic reality rather than isolated transformation signals.

## 9. Opportunity Prediction

- **Purpose:** Predict where commercially valuable action may exist and what must be learned next.
- **Major dependencies:** Enterprise Model runtime, Knowledge Graph runtime, Commercial Conviction, procurement and executive intelligence.
- **Architecture papers required:** EI-006, EI-005, FP-008, FP-009.
- **Expected product impact:** Opportunity outlooks with evidence lineage, timing, blockers, access paths and learning actions.

## 10. Commercial Conversation Engine

- **Purpose:** Convert intelligence into explainable commercial conversations, account plans and executive engagement paths.
- **Major dependencies:** executive intelligence, opportunity outlook, recommendations, human calibration workflow.
- **Architecture papers required:** future EI-014 Commercial Conversation Model, EI-007, EI-006, FP-008.
- **Expected product impact:** CIOS becomes a guided business development partner rather than only an intelligence surface.

## 11. Learning and Curiosity Engine

- **Purpose:** Learn from outcomes, unknowns, contradictions and failed hypotheses to improve future collection and reasoning.
- **Major dependencies:** outcome capture, feedback loops, hypothesis lifecycle, Observation Demand management.
- **Architecture papers required:** future EI-013, EI-015, EI-016, FP-009, EI-012.
- **Expected product impact:** CIOS improves with use, asks better questions and targets collection where uncertainty matters most.
