# CIOS Reference Architecture Glossary

**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11

Use this glossary as the common vocabulary for CIOS architecture. Primary documents are linked where they currently exist.

| Term | Definition | Primary documents |
| --- | --- | --- |
| CIOS | Enterprise Intelligence platform that detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action. | [Reference Architecture](CIOS-Reference-Architecture-v1.0.md), [FP-001](../founding-papers/FP-001-CIOS-Vision.md) |
| CIRM | CIOS Intelligence Reference Model; the reasoning chain that converts observable enterprise reality into strategic commercial judgement. | [Reference Architecture](CIOS-Reference-Architecture-v1.0.md), [architecture README](../README.md) |
| Enterprise Intelligence | The architecture for what CIOS knows about an enterprise and how that knowledge is organised, refreshed and used. | [Enterprise Intelligence README](../enterprise-intelligence/README.md) |
| Commercial Digital Twin | Evidence-backed, time-aware, confidence-scored, contradiction-aware model of a monitored enterprise. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Enterprise Model | Durable enterprise memory containing identity, leadership, economics, operating model, technology, transformation and commercial context. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Enterprise Knowledge Graph | Graph structure connecting enterprise entities, relationships, attributes and evidence-backed edges. | [EI-002](../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md) |
| Evidence | Attributable proof that something was observed from a permissible source. Evidence proves; it does not by itself constitute intelligence. | [FP-004](../founding-papers/FP-004-Evidence-Acquisition-Standard.md) |
| Observation | Atomic, reusable unit of Enterprise Intelligence created from evidence and stored as durable memory. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Strategic Signal | Commercially meaningful interpretation of evidence-backed change, pressure or opportunity. | [FP-007](../founding-papers/FP-007-Strategic-Signal-Standard.md) |
| Pattern | Recurring relationship across Observations, Signals or enterprise behaviour that may explain change or predict future change. | [EI-003](../enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md) |
| Hypothesis | Testable proposition used to validate or challenge an interpretation of enterprise change. | [FP-009](../founding-papers/FP-009-Hypothesis-Validation-Standard.md) |
| Commercial Thesis | Coherent, evidence-backed judgement about what is happening in an enterprise and why it matters commercially. | [FP-009](../founding-papers/FP-009-Hypothesis-Validation-Standard.md) |
| Commercial Conviction | Structured confidence that evidence and reasoning justify a level of commercial action. | [FP-008](../founding-papers/FP-008-Commercial-Conviction-Model.md) |
| Recommendation | Proposed learning, engagement or action step grounded in inspectable evidence and reasoning lineage. | [FP-008](../founding-papers/FP-008-Commercial-Conviction-Model.md) |
| Transformation Pressure | Internal and external forces that make enterprise change more likely or necessary. | [EI-009](../enterprise-intelligence/volume-4-enterprise-dynamics/EI-009-Transformation-Pressure-Model.md) |
| Transformation Inevitability | Degree to which an enterprise appears structurally compelled to transform, independent of visible procurement readiness. | [EI-005](../enterprise-intelligence/volume-2-commercial-intelligence/EI-005-Transformation-Prediction-Model.md) |
| Enterprise Weather | Current enterprise conditions that affect timing, urgency, risk and receptivity to change. | [EI-008](../enterprise-intelligence/volume-4-enterprise-dynamics/EI-008-Enterprise-Weather-Model.md) |
| Enterprise Momentum | Direction and velocity of enterprise change over time. | [EI-010](../enterprise-intelligence/volume-4-enterprise-dynamics/EI-010-Enterprise-Momentum-Model.md) |
| Opportunity Outlook | Evidence-backed view of commercial potential, accessibility, timing, blockers and next best learning action. | [EI-006](../enterprise-intelligence/volume-2-commercial-intelligence/EI-006-Opportunity-Prediction-Engine.md) |
| Human-supplied Attribute | Attribute supplied by human expertise rather than direct evidence; it must be labelled and calibrated. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Inferred Attribute | Attribute derived from reasoning over evidence, Observations or graph relationships; it must remain distinguishable from fact. | [EI-002](../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md) |
| Evidence-backed Attribute | Attribute directly supported by one or more evidence items or Observations. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Contradiction | Two or more claims that cannot all be true at the same time; contradictions must be preserved, not silently overwritten. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Unknown | Explicitly modelled absence of knowledge that guides future collection or reasoning. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Decay | Reduction in confidence or usefulness as information becomes stale or unsupported by recent evidence. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Half-Life | Expected period after which an Observation or attribute materially loses confidence without refresh. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Observation Demand | A need for a specific Observation that would reduce uncertainty, validate a hypothesis or improve an Enterprise Model. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Curiosity Engine | Future capability that turns unknowns, contradictions and weak hypotheses into targeted questions and collection priorities. | [Reference Architecture](CIOS-Reference-Architecture-v1.0.md) |
| Executive Intelligence | Understanding of executive actors, roles, ownership, influence, mandates and relationship context. | [EI-007](../enterprise-intelligence/volume-3-human-intelligence/EI-007-Executive-Intelligence-Model.md) |
| Provider Candidate Fact | Structured provider output awaiting canonical validation and acceptance. | [ADR-010](../decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md) |
| Canonical Fact | Governed, domain-valid fact that satisfies the owning data contract and may support an Observation. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Financial Measurement State | Whether a financial value is actual, guidance, target, forecast or another owned domain state. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Accounting Basis | Reporting basis under which a financial metric is stated, such as statutory or adjusted. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Reported Scale | Magnitude unit attached to a reported financial number, such as units, thousands, millions or billions. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Normalised Financial Value | Reported amount converted into canonical base-unit representation while retaining original display value and scale. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) |
| Observation Lifecycle State | EI-012 state describing validation, corroboration, strengthening, weakening, contradiction, retirement or archival. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Temporal Relevance | Degree to which an Observation or attribute remains current and decision-relevant based on effective period, freshness and decay. | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) |
| Financial Intelligence | Governed capability that converts financial sources into Evidence-backed Observations and Enterprise Model state. | [Flora Financial Intelligence Runtime Specification](../../docs/Architecture/Flora_Financial_Intelligence_Runtime_Specification_v0.1.md) |


## Progressive Assurance terms

| Term | Definition | Primary documents |
| --- | --- | --- |

| Progressive Assurance | Assurance model in which governance depth increases with recommendation strength, audience and consequence while core lineage and uncertainty rules remain invariant. | [ADR-009](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md), [FP-003](../founding-papers/FP-003-Flora-Intelligence-Architecture.md) |
| Initial Decision Twin | Default operating mode that creates or refreshes governed, decision-useful Commercial Digital Twin state without requiring formal release packaging. | [ADR-009](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md) |
| Assured Release | Explicit promotion mode that adds deeper review, reconciliation, publication validation and owner acceptance for external or high-consequence use. | [ADR-009](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md) |
| Evidence Saturation | Decision-relative point at which additional collection is unlikely to change the immediate bounded judgement materially; residual gaps remain explicit as Unknowns, Contradictions or Evidence Demands. | [ADR-009](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md), [FP-003](../founding-papers/FP-003-Flora-Intelligence-Architecture.md) |
| Promotion Trigger | A condition requiring an Initial Decision Twin to move to Assured Release, such as external publication, provider-specific pursuit, sponsor outreach or material reliance. | [ADR-009](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md) |

## Architecture v2.0 Knowledge Exchange terms

| Term | Definition | Primary documents |
| --- | --- | --- |
| Knowledge Pack | Governed exchange container for Knowledge Assets, provenance, validation metadata, Unknowns, Contradictions, recommendations and optional payloads such as Twin Presentation Models. | [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md), [FP-010](../founding-papers/FP-010-Knowledge-Pack-Architecture.md) |
| Knowledge Asset | Inspectable unit of portable intelligence carried by a Knowledge Pack. | [EI-013](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md) |
| Knowledge Exchange Architecture | Architecture for creating, receiving, validating, storing, rendering and learning from Knowledge Packs. | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) |
| Knowledge Repository | Governed store for accepted Knowledge Packs and related validation metadata. | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) |
| Twin Presentation Model | Versioned interpretation payload for rendering, review and navigation over governed knowledge. | [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) |
| Enterprise Twin | Governed enterprise-level digital twin model. | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md), [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) |
| Industry Twin | Governed industry-level twin maintained through lifecycle and cadence rules. | [Industry Twin Lifecycle Specification v1.0](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) |
| Market Participant Twin | Governed twin for a market participant within an Industry Twin context. | [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) |
| Opportunity Twin | Governed twin focused on a commercial opportunity and its evidence, participants, timing and constraints. | [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) |
| Relational Twin | Governed twin representing relationships across enterprises, participants, opportunities or portfolio contexts. | [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) |
| Cross-Twin Intelligence | Intelligence derived by comparing or reasoning across multiple Twins while preserving lineage and canonical boundaries. | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) |
| Knowledge Supply Chain | End-to-end flow for authoring, packaging, validating, storing, rendering and promoting exchanged knowledge. | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) |
| Flora Knowledge Pack Validation | Future Flora responsibility for validating, versioning, storing, rendering and distributing accepted Knowledge Packs without silently promoting contents to canonical fact. | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md), [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md) |
