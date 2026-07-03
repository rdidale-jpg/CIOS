# CIOS Architecture Document Map

**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

This map helps readers find the architecture paper that owns a concept. The Reference Architecture is the entry point; the documents below remain the primary homes for detailed standards and models.

## Living Context and Doctrine

| Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- |
| [CIOS AI Context](../../CIOS-AI.md) | Defines AI assistant and Codex working rules for CIOS. | Present | repo root | Required starting point for AI-assisted work. |
| [CIOS Design Doctrine](CIOS-Design-Doctrine.md) | Captures design philosophy and reasoning style. | Present | `architecture/reference-architecture/` | Explains why CIOS is evidence-first, observation-led and model-centred. |
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
| EI-001 | Enterprise Model Specification | Defines the durable Enterprise Model. | Present | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/` | Owns Commercial Digital Twin structure. |
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
| EI-012 | Enterprise Observation Model | Defines Observations as intelligence atoms. | Present | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/` | Owns Observation Doctrine. |
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
| Flora | Flora Case Files | Describes case file organisation. | Present | `docs/Applications/` | Report/view layer over evidence and model state. |
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
3. Use the [Glossary](Glossary.md) for terms.
4. Read [Architecture Principles](Architecture-Principles.md) and [CIOS Design Doctrine](CIOS-Design-Doctrine.md).
5. Read Founding Papers FP-003 to FP-009 to understand CIRM.
6. Read Enterprise Intelligence papers EI-001 to EI-012 to understand the Commercial Digital Twin.
7. Read relevant [ADRs](../decisions/README.md).
8. Read runtime architecture documents before changing Flora, Newton, Observatory or Publisher behaviour.
