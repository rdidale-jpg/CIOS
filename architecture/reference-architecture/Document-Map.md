# CIOS Architecture Document Map

**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-17

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
| AP-001 | [Architecture Compilation Standard](standards/AP-001-Architecture-Compilation-Standard.md) | Defines registry-backed compilation profiles and non-promotion rules for architecture packs. | Accepted | `architecture/reference-architecture/standards/` | Uses the Authority Registry as the foundation for architecture compilation without changing runtime behaviour. |
| AP-002 | [Architecture Metadata Standard](standards/AP-002-Architecture-Metadata-Standard.md) | Defines implementation-neutral metadata semantics for canonical architecture documents. | Accepted | `architecture/reference-architecture/standards/` | Aligns canonical document metadata with the Authority Registry so compilers can determine profile membership without prose. |
| RP-001 | [Enterprise Blueprint Researcher Profile](profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md) | Defines the official Researcher role and registry-backed Researcher-pack membership. | Accepted | `architecture/reference-architecture/profiles/` | Builds on AP-001, AP-002 and the Authority Registry so the compiler can generate a non-empty Researcher profile. |
| RP-002 | [Enterprise Intelligence Assurance Profile](profiles/RP-002-Enterprise-Intelligence-Assurance-Profile.md) | Defines the official Enterprise Intelligence Assurance role and registry-backed Assurance-pack membership. | Accepted | `architecture/reference-architecture/profiles/` | Builds on AP-001, AP-002, RP-001 and the Authority Registry so the compiler can generate a non-empty Assurance profile without promoting source documents. |
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
| FP-010 | [Enterprise Reinvention Intelligence](../founding-papers/FP-010-Enterprise-Reinvention-Intelligence.md) | Establishes the Review founding rationale linking EGM, CIOS, Flora, specialist Intelligence Companions, Commercial Asset Generation and continuous learning. | Review | `architecture/founding-papers/` | Documentation-only, non-runtime and excluded from production profiles; does not alter accepted ADR or owning-paper decisions. |
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
| EIF-001 | [Enterprise Intelligence Foundation Model](standards/EIF-001-Enterprise-Intelligence-Foundation-Model.md) | Defines the Review method for constructing the initial Enterprise Twin from public-domain evidence before Opportunity Discovery, including Enterprise Change Mechanisms, Enterprise Tensions and Executive Questions. | Review | `architecture/reference-architecture/standards/` | Documentation-only Review input to EOD-001; mechanisms and executive questions govern the bridge into EOD-001 while preserving EI-001, EI-002, EI-003, EI-012, canonical models and production packs. |
| EOD-001 | [Enterprise Opportunity Discovery Standard](standards/EOD-001-Enterprise-Opportunity-Discovery-Standard.md) | Defines the Review method for enterprise-first opportunity portfolio discovery after EIF-001. | Review | `architecture/reference-architecture/standards/` | Documentation-only Review input to OT-001, RTP-001 and OPI-001 validation; not Accepted and not production profile material. |
| EI-004 | Commercial Reasoning Framework | Defines commercial reasoning over enterprise knowledge. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Connects Enterprise Intelligence to CIRM reasoning. |
| EI-005 | Transformation Prediction Model | Defines how CIOS predicts transformation. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Owns Transformation Prediction concepts. |
| EI-006 | Opportunity Prediction Engine | Defines commercial opportunity prediction. | Present | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/` | Owns Opportunity Outlook and accessibility logic. |
| OT-001 | [Opportunity Twin Specification](../specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md) | Defines the Review Opportunity Twin interface, including explicit OPI-001 and RTP-001 relationships. | Review | `architecture/specifications/opportunity-twins/` | Documentation-only Review specification beneath EI-006; not Accepted and not production profile material. |
| EI-014 | [Solution Positioning Intelligence Model](../enterprise-intelligence/EI-014-Solution-Positioning-Intelligence-Model.md) | Defines the Review Enterprise Intelligence model that turns a governed Opportunity Twin into evidence-backed executive positioning intelligence. | Review | `architecture/enterprise-intelligence/` | Documentation-only Review model immediately after OT-001; generates governed positioning intelligence, not proposals, Provider Fit, supplier recommendations or runtime behaviour. |
| EI-015 | [Enterprise Intelligence Pattern Model](../enterprise-intelligence/EI-015-Enterprise-Intelligence-Pattern-Model.md) | Documents the Review model for evidence-governed, cross-enterprise Enterprise Intelligence Patterns. | Review | `architecture/enterprise-intelligence/` | Documentation-only comparative reasoning model; patterns emerge from mechanisms across multiple Enterprise Twins, do not create opportunities or Solution Patterns, and have no production-profile membership. |
| EI-017 | [Enterprise Mechanism Model](../enterprise-intelligence/EI-017-Enterprise-Mechanism-Model.md) | Defines the Review model for evidence-governed, reusable causal explanations of enterprise outcomes. | Review | `architecture/enterprise-intelligence/` | Documentation-only causal-explanation model; preserves Observation primacy, evidence lineage, Unknowns and Contradictions; excluded from all production profiles. |
| IT-001 | [Industry Twin Specification](../specifications/industry-twins/IT-001-Industry-Twin-Specification.md) | Defines the Review Industry Twin as a governed, comparative model of cross-enterprise industry intelligence and Pattern Variant consumption. | Review | `architecture/specifications/industry-twins/` | Documentation-only Review specification; Industry Twins synthesise authoritative Enterprise Twins, consume independently governed Patterns, preserve evidence discipline and have no production-profile membership. |
| OPI-001 | [Opportunity Positioning Intelligence](standards/OPI-001-Opportunity-Positioning-Intelligence.md) | Defines the Review method for candidate positioning objects contributed to Opportunity Twins. | Review | `architecture/reference-architecture/standards/` | Explicit Review input to OT-001; not Accepted and not production profile material. |
| RTP-001 | [Research-to-Positioning Input Contract](../enterprise-intelligence/contracts/RTP-001-Research-to-Positioning-Input-Contract.md) | Defines the Review governed handover from Research to Positioning. | Review | `architecture/enterprise-intelligence/contracts/` | Explicit Review handover into OT-001 and OPI-001; not Accepted and not production profile material. |
| VAL-ROADMAP-001 | [CIOS Validation Roadmap v1.0](../validation/CIOS-Validation-Roadmap-v1.0.md) | Establishes the Review validation programme for Commercial Digital Twin artefacts before any promotion is considered. | Review | `architecture/validation/` | Programme governance roadmap only; records MOD as completed evidence and VodafoneThree, National Grid and United Utilities as planned validation enterprises without promoting Review artefacts. |
| EI-007 | Executive Intelligence Model | Defines executive actors, ownership and influence. | Present | `architecture/enterprise-intelligence/volume-3-human-intelligence/` | Owns Executive Intelligence Layer. |
| EI-008 | Enterprise Weather Model | Defines current conditions affecting enterprise change. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Enterprise Weather. |
| EI-009 | Transformation Pressure Model | Defines internal and external pressure. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Transformation Pressure. |
| EI-010 | Enterprise Momentum Model | Defines direction and velocity of change. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns Enterprise Momentum. |
| EI-011 | Enterprise Economics Model | Defines enterprise economics and financial pressure. | Present | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/` | Owns economics in the Commercial Digital Twin. |
| EI-012 | Enterprise Observation Model | Defines Observations as intelligence atoms and owns Observation lifecycle state. | Present | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/` | Owns Observation Doctrine and state-semantics separation. |
| EI-013 | Enterprise Learning Model | Future paper for outcome learning and model improvement. | Future | `architecture/enterprise-intelligence/` | Will own Learning and Feedback Layer. |
| EI-016 | Enterprise Curiosity Engine | Future paper for curiosity-driven collection and reasoning. | Future | `architecture/enterprise-intelligence/` | Will own targeted learning from unknowns and contradictions. |

## Enterprise Knowledge

| Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- |
| [Banking Reinvention Hypotheses v0.1](../../enterprise-knowledge/banking/reinvention/Banking-Reinvention-Hypotheses-v0.1.md) | Governs candidate, evidence-derived Banking-domain Reinvention Hypotheses. | Candidate | `enterprise-knowledge/banking/reinvention/` | Industry-specific Enterprise Knowledge; not an architecture specification, Accepted ADR, Enterprise Reinvention Blueprint or cross-industry methodology. Methodology ownership resolved to EGM-001; section-level references preserved to the Universal Enterprise Reinvention Model and Industry Blueprint Method; no duplicate Enterprise Reinvention Blueprint asset created. |

## Founder Knowledge (Non-Architecture)

| Document | Purpose | Status | Folder | Relationship to Reference Architecture |
| --- | --- | --- | --- | --- |
| [Founder Knowledge README](../../knowledge/founder/README.md) | Entry point for preserved Founder Knowledge. | Review | `knowledge/founder/` | Discoverability only; not public evidence, architecture authority or production-profile material. |
| [FDK-001 — Founder Knowledge Register](../../knowledge/founder/FDK-001-Founder-Knowledge-Register.md) | Governs Founder Knowledge preservation and recovery. | Review | `knowledge/founder/` | Governance only; does not override Accepted ADRs or owning architecture papers. |
| [EGM-001 — Enterprise Growth Method](../../knowledge/founder/recovered-methods/EGM-001-Enterprise-Growth-Method.md) | Preserves the recovered Enterprise Growth Method. | Review | `knowledge/founder/recovered-methods/` | Founder Design Knowledge; no architecture authority and no production-profile membership. |

## Operational Intelligence Commissions

| ID | Title | Purpose | Status | Folder | Relationship to Architecture |
| --- | --- | --- | --- | --- | --- |
| IC-001 | [Enterprise Foundation Intelligence Commission](../../operations/intelligence-commissions/IC-001-Enterprise-Foundation-Intelligence-Commission.md) | Defines the reusable operational commission and enterprise-configuration model for executing EIF-001 Enterprise Foundation research. | Review | `operations/intelligence-commissions/` | Consumes EIF-001 and related architecture without redefining it; documentation-only and excluded from production Researcher and Assurance packs pending validation across multiple enterprises. |

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
9. Read EIF-001 before EOD-001 when constructing a new Enterprise Twin from public-domain evidence.
10. Read the CIOS Validation Roadmap before proposing Accepted promotion for EIF-001, EOD-001, OT-001, RTP-001 or OPI-001.
11. For Financial Intelligence, read ADR-010 and the Flora Financial Intelligence Runtime Specification.
12. Read relevant [ADRs](../decisions/README.md).
13. Read runtime architecture documents before changing Flora, Newton, Observatory or Publisher behaviour.



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
| EKPP-001 | [Enterprise Knowledge Production Protocol v1.0](../specifications/enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md) | Owns the standard operating model for creating, reviewing, governing and publishing Enterprise Knowledge. | Accepted Normative Protocol | `architecture/specifications/enterprise-knowledge/` | Complements accepted doctrine, Reference Architecture, Enterprise Knowledge Architecture, Knowledge Pack Specification and Accepted ADRs without changing their precedence. |
| TPM-SPEC-001 | [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) | Owns presentation payload semantics. | Normative Specification | `architecture/specifications/presentation-models/` | Normative specification for accepted presentation payloads. |
| ITL-SPEC-001 | [Industry Twin Lifecycle Specification v1.0](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) | Owns Industry Twin maintenance and cadence. | Normative Specification | `architecture/specifications/industry-twins/` | Normative specification for Industry Twin lifecycle. |
| MPT-SPEC-001 | [Market Participant Twin Specification v1.0](../specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md) | Owns Market Participant Twin structure, evidence-governed strengths and weaknesses, account presence and participant Knowledge Pack profile. | Normative Specification | `architecture/specifications/market-participants/` | Normative specification under FP-010, FP-011, EI-013 and EI-002. |
| APPA-SPEC-001 | [Account-Participant Position Assessment Specification v1.0](../specifications/market-participants/Account-Participant-Position-Assessment-Specification-v1.0.md) | Owns account-relative participant fit assessment, supported postures, commercial questions, recommendation lineage and assessment Knowledge Pack profile. | Normative Specification | `architecture/specifications/market-participants/` | Normative specification under FP-010, FP-011, FP-009, EI-013 and EI-002. |
| V2-REGISTER | [Architecture v2.0 Documentation Update Register](../programmes/cios-architecture-v2/Architecture-v2.0-Documentation-Update-Register.md) | Registers Phase 1 Architecture v2.0 additions. | Phase 1 Register | `architecture/programmes/cios-architecture-v2/` | Programme governance record. |

### Architecture v2.0 authority allocation

- FP-010 owns the conceptual Knowledge Pack architecture.
- FP-011 owns Knowledge Exchange Architecture.
- EI-013 owns exchanged Knowledge Asset semantics.
- Knowledge Pack Specification v1.0 owns the package contract.
- Enterprise Knowledge Production Protocol v1.0 owns the Enterprise Knowledge production operating model beneath the accepted precedence chain.
- Twin Presentation Model Specification v1.0 owns presentation payload semantics.
- Industry Twin Lifecycle Specification v1.0 owns Industry maintenance and cadence.

## Architecture v2.0 reconciliation notes

- The Reference Architecture now defines the four Architecture v2.0 pillars: Enterprise Intelligence, Commercial Digital Twins, Presentation Intelligence and Knowledge Exchange Architecture.
- EI-001, EI-002, EI-003 and EI-012 remain the authority for canonical Enterprise Model, graph, behaviour and Observation acceptance. Knowledge Pack acceptance does not bypass those processes.
- FP-009 continues to govern hypothesis validation and recommendation lineage for hypotheses or recommendations carried inside Knowledge Packs.
- Flora runtime implementation remains out of scope for this documentation update; later runtime contracts must follow ADR-016, FP-010, FP-011, EI-013 and the v1.0 specifications.

## Architecture v2.0 accepted authority chains

The Architecture v2 document chain is: **Accepted ADR → owning paper → normative specification → runtime contract → implementation documentation**. Runtime contracts and implementation documentation are intentionally marked as Phase 3 where not yet created.

| Accepted ADR | Owning paper | Normative specification | Runtime contract | Implementation documentation |
| --- | --- | --- | --- | --- |
| [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) | [FP-010](../founding-papers/FP-010-Knowledge-Pack-Architecture.md), [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md), [EI-013](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md) | [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md) | Phase 3: Flora Knowledge Pack Import/Export Runtime Contract | Phase 3: Flora Knowledge Repository implementation docs |
| [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) | [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) | Phase 3: Flora Presentation Model Rendering Contract | Phase 3: Presentation renderer implementation docs |
| [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) | [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) | [Industry Twin Lifecycle Specification v1.0](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) | Phase 3: Industry Change Queue Runtime Contract | Phase 3: Industry Twin maintenance implementation docs |

## Architecture v2.0 document ownership register

| Document | Owner |
| --- | --- |
| [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md) | CIOS Architecture Decision Register |
| [FP-010](../founding-papers/FP-010-Knowledge-Pack-Architecture.md) | Knowledge Pack Architecture owner |
| [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md) | Knowledge Exchange Architecture owner |
| [EI-013](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md) | Enterprise Intelligence owner |
| [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md) | Knowledge Pack specification owner |
| [Enterprise Knowledge Production Protocol v1.0](../specifications/enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md) | Chief Architect / Enterprise Knowledge production owner |
| [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) | Presentation Intelligence specification owner |
| [Industry Twin Lifecycle Specification v1.0](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) | Industry Twin lifecycle owner |
| [Market Participant Twin Specification v1.0](../specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md) | Market Participant Twin specification owner |
| [Account-Participant Position Assessment Specification v1.0](../specifications/market-participants/Account-Participant-Position-Assessment-Specification-v1.0.md) | Account-relative assessment specification owner |
| [Architecture v2.0 Documentation Update Register](../programmes/cios-architecture-v2/Architecture-v2.0-Documentation-Update-Register.md) | Architecture v2 programme owner |

## Phase 3 Enterprise Intelligence extension ownership

| Area | Owning document | Owned sections or concepts | Notes |
| --- | --- | --- | --- |
| Supported Twin types and shared Twin governance | [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) | Enterprise, Industry, Market Participant, Opportunity and Relational Twin support; shared governance; incremental release rule | Presentation Models and Knowledge Packs remain non-canonical views or exchange assets unless separately accepted by the owning Twin process. |
| Cross-Twin and pack graph relationships | [EI-002](../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md) | Cross-Twin edge patterns, inferred edge governance and Pack-to-Twin relationships | Cross-Twin propagation is proposal-based and evidence-linked. |
| Industry and participant behaviour | [EI-003](../enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md) | Participant Behaviour and Industry behaviour dimensions | Behaviour is derived from repeated Observations and does not override direct account evidence. |
| Industry and Participant Observations | [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) | Industry Observation categories, Participant Observation categories, cross-Twin impact proposal fields and incremental release rule | Cross-Twin impact is a proposal, not an automatic update. |
| Cross-Twin hypothesis validation | [FP-009](../founding-papers/FP-009-Hypothesis-Validation-Standard.md) | Participant, Industry, Account–Participant fit, Opportunity and cross-Twin recommendation validation rules | Strong recommendations require lineage across relevant Twins. |

## Knowledge Pack profile governance

| Area | Document | Purpose | Status | Location | Notes |
| --- | --- | --- | --- | --- | --- |
| Knowledge Pack role profiles | [Researcher and Reviewer Knowledge-Pack Profile Audit](../specifications/knowledge-packs/Researcher-Reviewer-Knowledge-Pack-Profile-Audit.md) | Audits generated role-pack profiles, explains the 93-file Researcher and 68-file Reviewer counts, and records exclusion rules for draft, historical, duplicate, sprint, experiment and generated files. | Governance audit | `architecture/specifications/knowledge-packs/` | Use before approving generated Researcher or Reviewer pack manifests. |
