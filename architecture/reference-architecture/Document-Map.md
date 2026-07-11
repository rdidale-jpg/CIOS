# CIOS Architecture Document Map

**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-11

This map helps readers find the architecture paper that owns a concept. The Reference Architecture is the entry point; the documents below remain the primary homes for detailed standards and models.

## Living Context and Doctrine

| Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- |
| [CIOS AI Context](../../CIOS-AI.md) | Defines AI assistant and Codex working rules for CIOS. | Present | repo root | Required starting point for AI-assisted work. |
| [CIOS Design Doctrine](CIOS-Design-Doctrine.md) | Captures design philosophy and reasoning style. | Present | `architecture/reference-architecture/` | Explains why CIOS is evidence-first, observation-led and model-centred. |
| [CIOS Chief Architect Handbook](../handbook/CIOS-Chief-Architect-Handbook.md) | Defines how the Chief Architect thinks, decides, challenges, collaborates, implements, reviews and learns. | Editorial Draft | `architecture/handbook/` | Operating companion that teaches stewardship and application of CIOS architecture without replacing detailed model authority. |
| [AI Session Handoff](AI-Session-Handoff.md) | Provides a short briefing and ready-to-copy prompt for new AI sessions. | Present | `architecture/reference-architecture/` | Makes project memory portable across sessions. |

## Architecture Decision Records

| ID | Title | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- | --- |
| ADR index | [Architecture Decision Records](../decisions/README.md) | Index of major architecture decisions. | Present | `architecture/decisions/` | Preserves why important choices were made. |
| ADR-001 | [Observations as Atomic Intelligence Unit](../decisions/ADR-001-Observations-as-Atomic-Intelligence-Unit.md) | Treats Observations as reusable intelligence atoms. | Accepted | `architecture/decisions/` | Reinforces EI-012 and Observation doctrine. |
| ADR-002 | [Enterprise Model as Durable Memory](../decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md) | Treats the Enterprise Model / Commercial Digital Twin as durable memory. | Accepted | `architecture/decisions/` | Reinforces EI-001 and report-as-view doctrine. |
| ADR-003 | [CIRM and EI Separation](../decisions/ADR-003-CIRM-and-EI-Separation.md) | Separates reasoning process from enterprise knowledge model. | Accepted | `architecture/decisions/` | Clarifies CIRM, Enterprise Intelligence and Flora responsibilities. |
| ADR-004 | [Human-Supplied Knowledge Must Be Labelled](../decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md) | Requires labelled, dated human-supplied knowledge. | Accepted | `architecture/decisions/` | Supports governance and provenance clarity. |
| ADR-005 | [No Recommendation Without Inspectable Lineage](../decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md) | Requires inspectable lineage for strong recommendations. | Accepted | `architecture/decisions/` | Enforces trust, explainability and evidence lineage. |
| ADR-010 | [Structured-Source-First, AI-Assisted Evidence Acquisition](../decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md) | Selects the governed acquisition hierarchy and treats provider output as candidate data. | Accepted | `architecture/decisions/` | Governs Financial Intelligence source acquisition and provider boundaries. |
| ADR-006 | [Signal Architecture](../decisions/ADR-006-Signal-Architecture.md) | Migrated placeholder for future signal architecture review. | Proposed | `architecture/decisions/` | Not authoritative until accepted. |
| ADR-007 | [Transformation Thesis](../decisions/ADR-007-Transformation-Thesis.md) | Migrated placeholder for future transformation thesis review. | Proposed | `architecture/decisions/` | Not authoritative until accepted. |
| ADR-008 | [Recommendation Engine](../decisions/ADR-008-Recommendation-Engine.md) | Migrated placeholder for future recommendation engine review. | Proposed | `architecture/decisions/` | Not authoritative until accepted. |

## Founding Papers

| ID | Title | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- | --- |
| FP-001 | CIOS Vision | Defines the founding vision for CIOS. | Present | `architecture/founding-papers/` | Provides the strategic origin and purpose of CIOS. |
| FP-002 | Strategic Signal Standard | Earlier signal standard retained as founding context. | Present | `architecture/founding-papers/` | Historical/parallel signal language; FP-007 is the CIRM Volume II standard. |
| FP-003 | Flora Intelligence Architecture | Defines Flora as the first operational intelligence architecture. | Present | `architecture/founding-papers/` | Anchors Flora runtime role in CIRM. |
| FP-004 | Evidence Acquisition Standard | Defines evidence acquisition, acceptance and curation rules. | Present | `architecture/founding-papers/` | Owns Source and Evidence Layer standards. |
| FP-005 | Enterprise Intelligence Collection Framework | Defines enterprise evidence blueprints and collection priorities. | Present | `architecture/founding-papers/` | Connects governed collection to Enterprise Intelligence needs. |
| FP-006 | Source Quality Standard | Defines source tiering, quality, yield and lifecycle actions. | Present | `architecture/founding-papers/` | Governs source trust, decay and replacement. |
| FP-007 | Strategic Signal Standard | Defines Strategic Signals as bridges from evidence to commercial reasoning. | Present | `architecture/founding-papers/` | Owns Signal terminology in CIRM Volume II. |
| FP-008 | Commercial Conviction Model | Defines conviction needed to justify commercial action. | Present | `architecture/founding-papers/` | Owns commercial conviction and recommendation thresholds. |
| FP-009 | Hypothesis Validation Standard | Defines hypothesis lifecycle and validation rules. | Present | `architecture/founding-papers/` | Owns hypothesis testing and learning from rejection. |

## Enterprise Intelligence

| ID | Title | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- | --- |
| EI-001 | Enterprise Model Specification | Defines the durable Enterprise Model and Financial Metric Data Contract. | Present | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/` | Owns Commercial Digital Twin structure and canonical financial data. |
| EI-002 | Enterprise Knowledge Graph | Defines graph entities, edges and relationship intelligence. | Present | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/` | Owns Knowledge Graph Layer. |
| EI-003 | Enterprise Behaviour Model | Defines enterprise behaviour patterns. | Present | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/` | Supports Behaviour and Dynamics Layer. |
| EI-004 | Commercial Reasoning Framework | Defines commercial reasoning over enterprise knowledge. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Connects Enterprise Intelligence to CIRM reasoning. |
| EI-005 | Transformation Prediction Model | Defines how CIOS predicts transformation. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Owns Transformation Prediction concepts. |
| EI-006 | Opportunity Prediction Engine | Defines commercial opportunity prediction. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Owns Opportunity Outlook and accessibility logic. |
| EI-007 | Executive Intelligence Model | Defines executive actors, ownership and influence. | Present | `architecture/enterprise-intelligence/volume-3-human-intelligence/` | Owns Executive Intelligence Layer. |
| EI-008 | Enterprise Weather Model | Defines current conditions affecting enterprise change. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Enterprise Weather. |
| EI-009 | Transformation Pressure Model | Defines internal and external pressure. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Transformation Pressure. |
| EI-010 | Enterprise Momentum Model | Defines direction and velocity of change. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Enterprise Momentum. |
| EI-011 | Enterprise Economics Model | Defines enterprise economics and financial pressure. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns economics in the Commercial Digital Twin. |
| EI-012 | Enterprise Observation Model | Defines Observations as intelligence atoms and owns Observation lifecycle state. | Present | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/` | Owns Observation Doctrine and state-semantics separation. |
| EI-013 | Enterprise Learning Model | Future paper for outcome learning and model improvement. | Future | `architecture/enterprise-intelligence/` | Will own Learning and Feedback Layer. |
| EI-014 | Commercial Conversation Model | Future paper for commercial conversation and action interface. | Future | `architecture/enterprise-intelligence/` | Will own conversation-led recommendations. |
| EI-015 | Enterprise Question Model | Future paper for questions as architecture objects. | Future | `architecture/enterprise-intelligence/` | Will own structured unknowns and question generation. |
| EI-016 | Enterprise Curiosity Engine | Future paper for curiosity-driven collection and reasoning. | Future | `architecture/enterprise-intelligence/` | Will own targeted learning from unknowns and contradictions. |

## Runtime Architecture

| Area | Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- | --- |
| Flora | Flora v0.1 | Describes Flora application concept. | Present | `docs/Applications/` | Product surface for first CIOS runtime. |
| Flora | Flora Live Evidence v0.1 | Describes live evidence capability. | Present | `docs/Applications/` | Implements parts of Source and Evidence Layer. |
| Flora | Flora Pilot Workspace v0.3 | Describes pilot workspace experience. | Present | `docs/Applications/` | Runtime surface for evidence and research workflows. |
| Flora | Flora Case Files | Describes case file organisation. | Present | `docs/Applications/` | Workspace/product view over Evidence, Observations, Enterprise Model state and reasoning. |
| Flora | [Flora Financial Intelligence Runtime Specification v0.1](../../docs/Architecture/Flora_Financial_Intelligence_Runtime_Specification_v0.1.md) | Defines operational Financial Intelligence behaviour for governed financial sources, candidate facts, Observations and Enterprise Model projection. | Working Draft | `docs/Architecture/` | Runtime capability over Source, Evidence, Observation and Enterprise Model layers; does not own EI-001 or EI-012 semantics. |
| Flora | Flora Publisher v0.1 | Describes briefing/report generation. | Present | `docs/Applications/` | Publisher role for generated executive outputs. |
| Flora | Flora Runtime Alignment Audit | Audits runtime alignment. | Present | `docs/Architecture/` | Compliance evidence for Flora vs architecture. |
| Flora | Flora Product Maturity Review | Reviews Flora product maturity. | Present | `docs/Architecture/` | Connects runtime maturity to architecture maturity. |
| CIRM | CIRM Runtime Compliance | Defines runtime compliance expectations. | Present | `docs/Architecture/` | Future PR compliance mechanism input. |
| Observatory | Enterprise Transformation Observatory | Defines Observatory design. | Present | `architecture/design/` | Cross-enterprise market and pattern view. |
| Observatory | Observatory Roadmap | Describes Observatory capability evolution. | Present | `architecture/roadmap/` | Roadmap input for cross-enterprise intelligence. |
| Collection | Evidence Collection Architecture | Combined FP-004, FP-005 and FP-006. | Present | `architecture/founding-papers/` | Governs collection planning, source quality and evidence acceptance. |
| Newton | Newton Roadmap | Describes Newton capability evolution. | Present | `architecture/roadmap/` | Roadmap input for commercial reasoning and opportunity shaping. |
| Flora | Flora Roadmap | Describes Flora capability evolution. | Present | `architecture/roadmap/` | Roadmap input for runtime alignment. |
| Runtime compliance | Future Architecture Compliance Checklist | Future PR checklist derived from Reference Architecture. | Future | `docs/Architecture/` | Will make architecture compliance inspectable for significant runtime PRs. |

## Reading order

1. Start with [CIOS AI Context](../../CIOS-AI.md).
2. Read [CIOS Reference Architecture v1.0](CIOS-Reference-Architecture-v1.0.md).
3. Read [CIOS Design Doctrine](CIOS-Design-Doctrine.md).
4. Read the [CIOS Chief Architect Handbook](../handbook/CIOS-Chief-Architect-Handbook.md) for judgement and working practice.
5. Use the [Glossary](Glossary.md) for terms.
6. Read [Architecture Principles](Architecture-Principles.md).
7. Read Founding Papers FP-003 to FP-009 to understand CIRM.
8. Read Enterprise Intelligence papers EI-001 to EI-012 to understand the Commercial Digital Twin; EI-001 owns financial metric data and EI-012 owns Observation lifecycle.
9. For Financial Intelligence, read ADR-010 and the Flora Financial Intelligence Runtime Specification.
10. Read relevant [ADRs](../decisions/README.md).
11. Read runtime architecture documents before changing Flora, Newton, Observatory or Publisher behaviour.



## Progressive Assurance additions

| ID | Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- | --- |
| ADR-009 | [Progressive Assurance for Commercial Digital Twins](../decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md) | Establishes Initial Decision Twin and Assured Release modes, bounded Researcher autonomy and proportionate assurance. | Accepted | `architecture/decisions/` | Governs cross-cutting Twin production and promotion. |
| MOD-CDT-05 | [MOD v1.3 Owner Acceptance Decision](../../docs/MOD-CDT-05-Owner-Acceptance-Decision-v1.3.md) | Accepts the MOD v1.3 intelligence state with explicit commercial and process constraints. | Accepted | `docs/decisions/` | Records learning evidence for ADR-009; does not own architecture. |
| FLORA-TP-001 | [Progressive Assurance Test Plan](../../docs/FLORA-TP-001-Progressive-Assurance-Test-Plan-v0.1.md) | Tests ingestion, incremental refresh, autonomous Initial Decision Twin creation and promotion. | Working Draft | `docs/testing/` | Runtime validation evidence for ADR-009 and FP-003. |

## Architecture v2.0 Knowledge Pack Foundations

**Authority chain:** Accepted ADR → owning Founding Paper or EI paper → normative specification → runtime implementation contract.

| ID | Document | Purpose | Status | Folder | Authority relationship |
| --- | --- | --- | --- | --- | --- |
| ADR-016 | [Knowledge Packs as the Standard Exchange Mechanism](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) | Establishes Knowledge Pack as the standard exchange mechanism without making package acceptance canonical fact. | Accepted | `architecture/decisions/` | Starts the v2.0 authority chain. |
| FP-010 | [Knowledge Pack Architecture](../founding-papers/FP-010-Knowledge-Pack-Architecture.md) | Owns the conceptual Knowledge Pack architecture. | Accepted Foundation | `architecture/founding-papers/` | Owning Founding Paper for Knowledge Pack concepts. |
| FP-011 | [Knowledge Exchange Architecture](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) | Owns Knowledge Exchange Architecture and the Knowledge Supply Chain. | Accepted Foundation | `architecture/founding-papers/` | Owning Founding Paper for exchange flow and repository boundaries. |
| EI-013 | [Knowledge Asset Exchange Model](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md) | Owns exchanged Knowledge Asset semantics. | Accepted Foundation | `architecture/enterprise-intelligence/` | EI owner for portable asset semantics. |
| KP-SPEC-001 | [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md) | Owns the package contract. | Normative Specification | `architecture/specifications/knowledge-packs/` | Normative specification under FP-010, FP-011 and EI-013. |
| TPM-SPEC-001 | [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) | Owns presentation payload semantics. | Normative Specification | `architecture/specifications/presentation-models/` | Normative specification for accepted presentation payloads. |
| ITL-SPEC-001 | [Industry Twin Lifecycle Specification v1.0](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) | Owns Industry Twin maintenance and cadence. | Normative Specification | `architecture/specifications/industry-twins/` | Normative specification for Industry Twin lifecycle. |
| V2-REGISTER | [Architecture v2.0 Documentation Update Register](../programmes/cios-architecture-v2/Architecture-v2.0-Documentation-Update-Register.md) | Registers Phase 1 Architecture v2.0 additions. | Phase 1 Register | `architecture/programmes/cios-architecture-v2/` | Programme governance record. |

### Architecture v2.0 authority allocation

- FP-010 owns the conceptual Knowledge Pack architecture.
- FP-011 owns Knowledge Exchange Architecture.
- EI-013 owns exchanged Knowledge Asset semantics.
- Knowledge Pack Specification v1.0 owns the package contract.
- Twin Presentation Model Specification v1.0 owns presentation payload semantics.
- Industry Twin Lifecycle Specification v1.0 owns Industry maintenance and cadence.

## Architecture v2.0 reconciliation notes

- The Reference Architecture now defines the four Architecture v2.0 pillars: Enterprise Intelligence, Commercial Digital Twins, Presentation Intelligence and Knowledge Exchange Architecture.
- EI-001, EI-002, EI-003 and EI-012 remain the authority for canonical Enterprise Model, graph, behaviour and Observation acceptance. Knowledge Pack acceptance does not bypass those processes.
- FP-009 continues to govern hypothesis validation and recommendation lineage for hypotheses or recommendations carried inside Knowledge Packs.
- Flora runtime implementation remains out of scope for this documentation update; later runtime contracts must follow ADR-016, FP-010, FP-011, EI-013 and the v1.0 specifications.
