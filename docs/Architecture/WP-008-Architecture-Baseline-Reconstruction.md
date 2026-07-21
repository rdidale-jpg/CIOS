# WP-008 — Architecture Baseline Reconstruction

**Status:** Analysis complete  
**Document type:** Architecture baseline report  
**Version:** 0.1.0  
**Date:** 2026-07-21  
**Owner:** CIOS Architecture Engineer  

## Executive Summary

This report reconstructs the current CIOS architecture without redesigning, renaming, renumbering, merging, or superseding any architectural concept. The repository already defines CIOS as an Enterprise Intelligence platform whose flow is evidence-backed and observation-led: Observable Reality → Sources → Evidence → Observations → Enterprise Models → Commercial Digital Twins → Presentation Models → Knowledge Packs → Flora → Executive action and learning.

The current architecture is intentionally layered rather than monolithic. The Reference Architecture is the navigation and governance entry point; Founding Papers establish doctrine; Enterprise Intelligence papers own durable models; ADRs govern accepted decisions; runtime and Flora specifications bind architecture to product behaviour; Knowledge Pack specifications and manifests govern exchange; enterprise-knowledge folders hold packaged domain/twin knowledge; tests and validators provide executable controls.

No architectural change is proposed here. All findings are classified only as Preserve, Extend, Refactor, Supersede, or Review Required.

## Repository Structure

| Area | Architectural role | Primary paths |
| --- | --- | --- |
| Reference Architecture | Entry point, map, glossary, principles, authority registry, maturity model, metadata and compilation standards | `architecture/reference-architecture/` |
| Founding Papers | Foundational doctrine and platform intent | `architecture/founding-papers/` |
| Enterprise Intelligence | Enterprise, graph, behaviour, commercial, observation, mechanism and knowledge-asset models | `architecture/enterprise-intelligence/` |
| ADRs | Accepted/proposed architectural decisions and decision workflow | `architecture/decisions/`, `architecture/adr/` |
| Runtime / Flora specs | Product, runtime, reasoning pipeline and import architecture | `architecture/specifications/flora/`, `docs/Architecture/`, `cios/applications/flora/` |
| Knowledge Packs | Researcher pack content, manifest, source map, build and validation process | `knowledge-packs/researcher/`, `tools/knowledge-packs/` |
| Enterprise Knowledge | Domain, industry, enterprise, infrastructure, provider-offer and governance knowledge | `enterprise-knowledge/` |
| Science / CBOK | Scientific governance, evidence hierarchy, commercial body of knowledge standards/templates | `docs/Science/`, `docs/CBOK/` |
| Tests / schemas / fixtures | Executable validation of models, profiles, runtime and pack rules | `tests/`, `schemas/`, `fixtures/` |
| Workflows | CI and build validation | `.github/workflows/` |

## Architectural Layers

1. **Doctrine and authority:** CIOS vision, design doctrine, architecture principles, reference architecture, document map, authority registry, Chief Architect handbook, CIOS-AI guidance.
2. **Decision layer:** accepted and proposed ADRs, including observation, enterprise model, lineage, human-labelling, blueprint import, enterprise canvas, runtime and knowledge-pack decisions.
3. **Enterprise Intelligence model layer:** EI-001 through EI-017 and contracts such as EU-001 and RTP-001.
4. **Twin and opportunity layer:** industry twins, enterprise twins, market-participant twins, opportunity twins, commercial digital twin blueprint contract and presentation models.
5. **Runtime and product layer:** Flora runtime, Flora v2 experience, FEIR-001, EIRP-001, governed blueprint import, live evidence, canvas and workspace code.
6. **Knowledge exchange layer:** FP-010, FP-011, ADR-016, EKP-001, Knowledge Pack Specification, researcher profile, manifest and source map.
7. **Validation layer:** schemas, tests, fixtures, build scripts, pack checksums, science registries and governance reports.

## Document Catalogue

### Canonical architecture authority and navigation

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| RA entry | CIOS Reference Architecture v1.0 | `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md` | Draft | Reference architecture | v1.0 | Top-level navigation, philosophy, taxonomy and governance document. |
| Document Map | CIOS Architecture Document Map | `architecture/reference-architecture/Document-Map.md` | Draft | Document map | repository-current | Maps concept homes and relationships to the Reference Architecture. |
| Authority Registry | CIOS Architecture Authority Registry | `architecture/reference-architecture/Architecture-Authority-Registry.md` | Draft | Governance registry | repository-current | Records authority status and release-profile membership. |
| DD-001 | CIOS Design Doctrine | `architecture/reference-architecture/CIOS-Design-Doctrine.md` | Living doctrine / Accepted in registry | Doctrine | repository-current | Governs evidence-first, observation-led, model-centred design style. |
| Principles | CIOS Architecture Principles | `architecture/reference-architecture/Architecture-Principles.md` | Draft | Principles | repository-current | Defines architectural principles for CIOS. |
| Glossary | CIOS Reference Architecture Glossary | `architecture/reference-architecture/Glossary.md` | Draft | Glossary | repository-current | Canonical terminology reference. |
| Handbook | CIOS Chief Architect Handbook | `architecture/handbook/CIOS-Chief-Architect-Handbook.md` | Living handbook | Handbook | repository-current | Stewardship, review and architectural operating guidance. |
| CIOS-AI | CIOS AI Context | `CIOS-AI.md` | Present | AI guidance | repository-current | AI assistant and Codex working rules. |

### Founding Papers

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| FP-001 | CIOS Vision | `architecture/founding-papers/FP-001-CIOS-Vision.md` | draft | Founding Paper | repository-current | Platform purpose and vision. |
| FP-002 | Strategic Signal Standard | `architecture/founding-papers/FP-002-Strategic-Signal-Standard.md` | draft | Founding Paper | repository-current | Strategic signal semantics. |
| FP-003 | Flora Intelligence Architecture | `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md` | draft | Founding Paper | repository-current | Flora intelligence architecture. |
| FP-004 | Evidence Acquisition Standard | `architecture/founding-papers/FP-004-Evidence-Acquisition-Standard.md` | draft | Founding Paper | repository-current | Evidence acquisition standard. |
| FP-005 | Enterprise Intelligence Collection Framework | `architecture/founding-papers/FP-005-Enterprise-Intelligence-Collection-Framework.md` | draft | Founding Paper | repository-current | Enterprise Intelligence collection framework. |
| FP-006 | Source Quality Standard | `architecture/founding-papers/FP-006-Source-Quality-Standard.md` | draft | Founding Paper | repository-current | Source quality standard. |
| FP-007 | Strategic Signal Standard | `architecture/founding-papers/FP-007-Strategic-Signal-Standard.md` | Draft | Founding Paper | repository-current | Later strategic signal standard; duplicate title with FP-002 requires review. |
| FP-008 | Commercial Conviction Model | `architecture/founding-papers/FP-008-Commercial-Conviction-Model.md` | Draft | Founding Paper | repository-current | Commercial conviction. |
| FP-009 | Hypothesis Validation Standard | `architecture/founding-papers/FP-009-Hypothesis-Validation-Standard.md` | Draft | Founding Paper | repository-current | Hypothesis validation. |
| FP-010 | Knowledge Pack Architecture | `architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md` | Proposed Foundation | Founding Paper | repository-current | Knowledge Pack architecture. |
| FP-011 | Knowledge Exchange Architecture | `architecture/founding-papers/FP-011-Knowledge-Exchange-Architecture.md` | Proposed Foundation | Founding Paper | repository-current | Knowledge exchange architecture. |
| FP-012 | Enterprise Reinvention Intelligence | `architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md` | Review | Founding Paper | repository-current | Enterprise reinvention intelligence. |

### Enterprise Intelligence specifications and contracts

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| EI-001 | Enterprise Model Specification | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md` | Draft | EI specification | repository-current | Canonical Enterprise Model. |
| EI-002 | Enterprise Knowledge Graph | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md` | Draft | EI specification | repository-current | Enterprise Knowledge Graph. |
| EI-003 | Enterprise Behaviour Model | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md` | Draft | EI specification | repository-current | Enterprise behaviour semantics. |
| EI-004 | Commercial Reasoning Framework | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/EI-004-Commercial-Reasoning-Framework.md` | Draft | EI specification | repository-current | Commercial reasoning. |
| EI-005 | Transformation Prediction Model | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/EI-005-Transformation-Prediction-Model.md` | Draft | EI specification | repository-current | Transformation prediction. |
| EI-006 | Opportunity Prediction Engine | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/EI-006-Opportunity-Prediction-Engine.md` | Draft | EI specification | repository-current | Opportunity prediction. |
| EI-007 | Executive Intelligence Model | `architecture/enterprise-intelligence/volume-3-human-intelligence/EI-007-Executive-Intelligence-Model.md` | Draft | EI specification | repository-current | Executive intelligence. |
| EI-008 | Enterprise Weather Model | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/EI-008-Enterprise-Weather-Model.md` | Draft | EI specification | repository-current | Enterprise weather. |
| EI-009 | Transformation Pressure Model | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/EI-009-Transformation-Pressure-Model.md` | Draft | EI specification | repository-current | Transformation pressure. |
| EI-010 | Enterprise Momentum Model | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/EI-010-Enterprise-Momentum-Model.md` | Draft | EI specification | repository-current | Enterprise momentum. |
| EI-011 | Enterprise Economics Model | `architecture/enterprise-intelligence/volume-4-enterprise-dynamics/EI-011-Enterprise-Economics-Model.md` | Draft | EI specification | repository-current | Enterprise economics. |
| EI-012 | Enterprise Observation Model | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md` | Draft | EI specification | repository-current | Observation lifecycle and evidence linkage. |
| EI-013 | Knowledge Asset Exchange Model | `architecture/enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md` | Proposed Foundation | EI specification | repository-current | Knowledge asset exchange. |
| EI-014 | Solution Positioning Intelligence Model | `architecture/enterprise-intelligence/EI-014-Solution-Positioning-Intelligence-Model.md` | Review | EI specification | repository-current | Solution positioning. |
| EI-015 | Enterprise Intelligence Pattern Model | `architecture/enterprise-intelligence/EI-015-Enterprise-Intelligence-Pattern-Model.md` | Review | EI specification | repository-current | EI patterns. |
| EI-017 | Enterprise Mechanism Model | `architecture/enterprise-intelligence/EI-017-Enterprise-Mechanism-Model.md` | Review | EI specification | repository-current | Enterprise mechanisms. |
| EU-001 | Enterprise Understanding Contract | `architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md` | Review | Contract | repository-current | Enterprise understanding input/review contract. |
| RTP-001 | Research-to-Positioning Input Contract | `architecture/enterprise-intelligence/contracts/RTP-001-Research-to-Positioning-Input-Contract.md` | Review | Contract | repository-current | Research-to-positioning handoff. |

### ADRs

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| ADR-001 | Observations as Atomic Intelligence Unit | `architecture/decisions/ADR-001-Observations-as-Atomic-Intelligence-Unit.md` | Accepted | ADR | repository-current | Observation as atomic intelligence unit. |
| ADR-002 | Enterprise Model as Durable Memory | `architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md` | Accepted | ADR | repository-current | Enterprise Model durable memory. |
| ADR-003 | CIRM and EI Separation | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md` | Accepted | ADR | repository-current | Separates CIRM and EI. |
| ADR-003 | Governed UK Banking Theme Taxonomy | `architecture/decisions/ADR-003-uk-banking-theme-taxonomy.md` | not explicit | ADR | repository-current | UK banking theme taxonomy; duplicate ADR ID requires review. |
| ADR-004 | Human-Supplied Knowledge Must Be Labelled | `architecture/decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md` | Accepted | ADR | repository-current | Human-supplied knowledge labelling. |
| ADR-005 | No Recommendation Without Inspectable Lineage | `architecture/decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md` | Accepted | ADR | repository-current | Recommendation lineage. |
| ADR-006 | Signal Architecture | `architecture/decisions/ADR-006-Signal-Architecture.md` | Proposed | ADR | repository-current | Signal architecture. |
| ADR-007 | Transformation Thesis | `architecture/decisions/ADR-007-Transformation-Thesis.md` | Proposed | ADR | repository-current | Transformation thesis. |
| ADR-008 | Recommendation Engine | `architecture/decisions/ADR-008-Recommendation-Engine.md` | Proposed | ADR | repository-current | Recommendation engine. |
| ADR-009 | Progressive Assurance for Commercial Digital Twins | `architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md` | Accepted | ADR | repository-current | Progressive assurance. |
| ADR-010 | Structured-Source-First, AI-Assisted Evidence Acquisition | `architecture/decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md` | Accepted | ADR | repository-current | Structured-source-first evidence acquisition. |
| ADR-011 | Dual-Speed Financial Intelligence | `architecture/decisions/ADR-011-Dual-Speed-Financial-Intelligence.md` | Accepted | ADR | repository-current | Dual-speed financial intelligence. |
| ADR-012 | Governed Blueprint Package Import and Canonical Acceptance Boundary | `architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md` | Accepted | ADR | repository-current | Blueprint import acceptance boundary. |
| ADR-013 | Enterprise Canvas as the Primary Living Twin Navigation Model | `architecture/decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md` | Accepted | ADR | repository-current | Enterprise Canvas navigation. |
| ADR-014 | Evidence-Governed Enterprise Intelligence Reasoning Runtime | `architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md` | not explicit | ADR | repository-current | Reasoning runtime. |
| ADR-015 | Observation Identity and Minimal Model Projection | `architecture/decisions/ADR-015-Observation-Identity-and-Minimal-Model-Projection.md` | not explicit | ADR | repository-current | Observation identity. |
| ADR-015 | Runtime Mission Context Architecture | `architecture/adr/ADR-015-Runtime-Mission-Context.md` | Accepted | ADR | repository-current | Runtime mission context; duplicate ADR ID requires review. |
| ADR-016 | Knowledge Packs as the Standard Exchange Mechanism | `architecture/decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md` | Accepted | ADR | repository-current | Knowledge Packs as exchange mechanism. |
| ADR-023 | Enterprise Understanding as the Primary Governed Asset | `architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md` | Proposed | ADR | repository-current | Enterprise understanding. |
| ADR-024 | Hybrid Enterprise Intelligence Runtime | `architecture/decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md` | not explicit | ADR | repository-current | Hybrid EI runtime. |
| ADR-025 | Flora as the Enterprise Intelligence Workspace | `architecture/decisions/ADR-025-Flora-as-the-Enterprise-Intelligence-Workspace.md` | Proposed | ADR | repository-current | Flora workspace role. |

### Standards, specifications, profiles and missions

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| AP-001 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md` | Accepted | Process standard | repository-current | Registry-backed compilation profiles and non-promotion rules. |
| AP-001 v1.1 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard-v1.1.md` | Accepted | Process standard | v1.1 | Later AP-001 file; relationship to base AP-001 requires review. |
| AP-002 | Architecture Metadata Standard | `architecture/reference-architecture/standards/AP-002-Architecture-Metadata-Standard.md` | Accepted | Metadata standard | repository-current | Canonical architecture metadata semantics. |
| RP-001 | Enterprise Blueprint Researcher Profile | `architecture/reference-architecture/profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md` | Accepted | Role profile | repository-current | Researcher role and pack membership. |
| RP-002 | Enterprise Intelligence Assurance Profile | `architecture/reference-architecture/profiles/RP-002-Enterprise-Intelligence-Assurance-Profile.md` | Accepted | Role profile | repository-current | Assurance role and pack membership. |
| RA-001 | CIOS Enterprise Intelligence Meta Model | `architecture/reference-architecture/meta-model/RA-001-CIOS-Enterprise-Intelligence-Meta-Model.md` | Draft | Meta-model | repository-current | EI meta-model. |
| EIF-001 | Enterprise Intelligence Foundation Model | `architecture/reference-architecture/standards/EIF-001-Enterprise-Intelligence-Foundation-Model.md` | Review | Standard | repository-current | Enterprise Intelligence foundation before opportunity discovery. |
| EOD-001 | Enterprise Opportunity Discovery Standard | `architecture/reference-architecture/standards/EOD-001-Enterprise-Opportunity-Discovery-Standard.md` | Review | Standard | repository-current | Opportunity discovery from Enterprise Twin. |
| OPI-001 | Opportunity Positioning Intelligence | `architecture/reference-architecture/standards/OPI-001-Opportunity-Positioning-Intelligence.md` | Review | Standard | repository-current | Opportunity positioning. |
| IT-001 | Industry Twin Specification | `architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md` | Review | Twin specification | repository-current | Industry Twin. |
| OT-001 | Opportunity Twin Specification | `architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md` | Review | Twin specification | repository-current | Opportunity Twin. |
| EKP-001 | Enterprise Knowledge Production Protocol v1.0 | `architecture/specifications/enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md` | Accepted by index | Protocol | v1.0 | Enterprise knowledge production. |
| FEIR-001 | Flora Enterprise Intelligence Runtime Architecture v1.0 | `architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md` | Proposed | Runtime specification | v1.0 | Flora runtime architecture. |
| EIRP-001 | Enterprise Intelligence Reasoning Pipeline Specification | `architecture/specifications/flora/EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md` | Proposed | Pipeline specification | repository-current | Reasoning pipeline. |
| TPM-001 | Twin Presentation Model Specification v1.0 | `architecture/specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md` | Draft Normative Specification | Presentation specification | v1.0 | Presentation model. |
| MPT-001 | Market Participant Twin Specification v1.0 | `architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md` | Draft Normative Specification | Twin specification | v1.0 | Market participant twin. |
| APPA-001 | Account-Participant Position Assessment Specification v1.0 | `architecture/specifications/market-participants/Account-Participant-Position-Assessment-Specification-v1.0.md` | Draft Normative Specification | Assessment specification | v1.0 | Account-participant position assessment. |
| MISSION-UKCG-001 | UK Central Government Industry Twin Mission | `knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md` | current in pack manifest | Mission | repository-current | Researcher mission included in Knowledge Pack. |

## Canonical Concepts and Ownership Matrix

| Concept | Canonical owner | Supporting / governing documents | Classification |
| --- | --- | --- | --- |
| Evidence | EI-012 owns observation evidence linkage; FP-004 owns acquisition standard | ADR-010, source-map evidence entry, EKP-001 | Preserve |
| Observation | EI-012 | ADR-001, ADR-015 observation identity, source-map observations entry | Preserve |
| Enterprise | EI-001 | EIF-001, EU-001, enterprise-knowledge register | Preserve |
| Behaviour | EI-003 | EI-017, EI-002 graph relationships | Preserve |
| Enterprise Model | EI-001 | ADR-002, EIF-001, source-map enterprise_model entry | Preserve |
| Enterprise Knowledge Graph | EI-002 | source-map knowledge_graph entry | Preserve |
| Mission | RKI-001 / RG-001 / MISSION-UKCG-001 for researcher pack mission | ADR-015 Runtime Mission Context | Preserve |
| Runtime Context | ADR-015 Runtime Mission Context | FEIR-001, ADR-024 | Review Required because ADR-015 ID appears in two paths. |
| Research Policy | RG-001 and RP-001 | RKI-001, RKI-002, EKP-001 | Preserve |
| Commercial Capability | EI-004 / EI-014 | FP-008, OPI-001 | Preserve |
| Commercial Opportunity | EOD-001 / OT-001 / EI-006 | OPI-001, RTP-001 | Preserve |
| Commercial Thesis | ADR-007 | EI-004, FP-008, OPI-001 | Preserve |
| Recommendation | ADR-005 and ADR-008 | EI-004, EIRP-001 | Preserve; Review Required for ADR-008 proposed status. |
| Commercial Digital Twin | Commercial Digital Twin Blueprint Contract | FP-003, FP-012, ADR-009 | Preserve |
| Target Enterprise | EI-001 / EU-001 | EIF-001, Enterprise Twin docs | Preserve |
| Supplier | RG-001 checklist / market participant specs | Supplier-Contract-Procurement checklist, MPT-001 | Preserve |
| Partner | MPT-001 / EI-002 relationships | Enterprise Knowledge Graph | Preserve |
| Transformation | EI-005 / ADR-007 | FP-012, EI-009, EI-010 | Preserve |
| Enterprise Reinvention | FP-012 | banking reinvention package | Review Required because FP-012 is Review status. |
| Relationship | EI-002 | EI-012 projection fixtures and schemas | Preserve |
| Unknown | Reference Architecture doctrine / EI-012 | runtime schemas for unknown and safe-unavailable | Preserve |
| Contradiction | Reference Architecture doctrine / EI-012 | runtime schemas and fixtures | Preserve |
| Validation | FP-009 and validation roadmap | tests, schemas, governance reports | Preserve |
| Confidence | FP-009 / CBOK confidence docs | Science governance, provider-offer seeds | Preserve |
| Executive Briefing | EI-007 | Flora presentation/runtime documents | Preserve |
| Research Output | EKP-001 / RG-001 | templates and source map | Preserve |
| Knowledge Pack | FP-010 | ADR-016, Knowledge Pack Specification, manifest, build script | Preserve |
| Workflow | GitHub workflows and AP-001 | build script and tests | Preserve |
| Manifest | Knowledge Pack manifest | build_researcher_pack.py | Preserve |
| Source Map | Knowledge Pack source-map.yaml | manifest and pack spec | Preserve |

## Dependency Analysis

| Document / family | Depends on | Extends / implements | Notes |
| --- | --- | --- | --- |
| Reference Architecture | Founding Papers, ADR index, EI papers, Flora runtime | Navigates all architecture | Does not replace detailed authority. |
| Authority Registry | Reference Architecture, Document Map, accepted ADRs/EI/FP papers | Release-profile classification | Prevents review material from being treated as accepted authority. |
| AP-001 | Authority Registry, Reference Architecture, Document Map | Compilation process | Non-runtime, non-promotion standard. |
| AP-002 | Authority Registry, AP-001, Document Map | Metadata semantics | Enables profile membership determination. |
| RP-001 | AP-001, AP-002, Authority Registry | Researcher profile | Drives researcher pack membership. |
| RP-002 | AP-001, AP-002, RP-001 | Assurance profile | Drives assurance pack membership. |
| EI-001 | FP doctrine, ADR-002 | Enterprise Model | Foundation for twins and opportunity discovery. |
| EI-002 | EI-001 | Knowledge Graph | Defines relationships and graph structure. |
| EI-003 | EI-001 / EI-002 | Behaviour semantics | Behaviour sits on model and graph. |
| EI-012 | FP-004, ADR-001 | Observation lifecycle | Evidence-to-observation bridge. |
| EI-004 / EI-006 / EOD-001 / OT-001 / OPI-001 | EI-001, EI-002, EI-012 | Commercial and opportunity reasoning | Opportunity model depends on prior enterprise understanding. |
| FEIR-001 / EIRP-001 / ADR-024 | ADR-014, ADR-015, Flora specs | Runtime and reasoning implementation | Runtime remains governed by evidence and mission context. |
| FP-010 / FP-011 / ADR-016 / EKP-001 | EI owners, Authority Registry | Knowledge exchange and pack production | Knowledge Packs package authority; they do not create canonical ownership. |

## Workflow Analysis

The repository contains GitHub workflow configuration under `.github/workflows/`. Workflow inputs and outputs observed in the repository are validation-oriented: Python tests, architecture/profile tests, and Knowledge Pack build/validation are represented by test files and `tools/knowledge-packs/build_researcher_pack.py`. No workflow files were modified.

## Knowledge Pack Build Analysis

| Build concern | Current implementation |
| --- | --- |
| Included documents | `knowledge-packs/researcher/manifest.yaml` enumerates pack path, source path, document ID, title, version/last-updated, authority, status, required flag, inclusion reason, checksum and transform. |
| Excluded documents | Anything not enumerated in the manifest is not copied by the build script. |
| Manifest build | The manifest is source-controlled; the build script parses it and validates source existence and checksums. |
| Source map build | `knowledge-packs/researcher/source-map.yaml` is source-controlled and copied unchanged into the staged pack. |
| Template selection | Templates are selected by manifest entries whose pack paths are under `templates/`. |
| Mission selection | Missions are selected by manifest entries whose pack paths are under `missions/`; the current source map names `MISSION-UKCG-001`. |
| ZIP production | The build script stages listed files, generates `DOCUMENT-INDEX.md`, writes `checksums.sha256`, and creates `dist/CIOS-Researcher-Knowledge-Pack-v<VERSION>.zip`. |
| Validation | Required document IDs are checked; source existence and SHA-256 checksums are checked; EI/FP/ADR document IDs must appear near the top; core doctrine phrases must be present. |

## Mission Architecture

Mission architecture exists in two places: runtime mission context is governed by `architecture/adr/ADR-015-Runtime-Mission-Context.md`, while researcher pack mission execution is governed by `knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md`, `knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md`, and `knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md`. The source map explicitly groups researcher mission governance as RKI-001, RG-001 and MISSION-UKCG-001.

## Twin Architecture

Twin architecture is multi-form: Enterprise Twins rely on EI-001, EI-002, EI-003 and EI-012; Industry Twins are specified by IT-001 and industry lifecycle documents; Market Participant Twins are specified by market-participant specifications; Opportunity Twins are specified by OT-001; Commercial Digital Twins are governed by the Commercial Digital Twin Blueprint Contract, FP-003, FP-012 and ADR-009. Presentation is separate and governed by the Twin Presentation Model Specification.

## Commercial Architecture

Commercial architecture spans EI-004 Commercial Reasoning Framework, FP-008 Commercial Conviction Model, EI-006 Opportunity Prediction Engine, EOD-001, OPI-001, ADR-005, ADR-008 and EIRP-001. The doctrine preserves the distinction between fact, inference, hypothesis and recommendation.

## Opportunity Architecture

Opportunity architecture follows the Reference Architecture lifecycle: Enterprise → EIF-001 → Enterprise Twin → EOD-001 → Opportunity Portfolio → Opportunity Prioritisation → OT-001 → Research Sprint → RTP-001 → OPI-001 → Provider Fit → Executive Pursuit → Learning → evolved Enterprise Twin.

## Evidence Lineage

Evidence lineage is owned across FP-004, ADR-010, EI-012, ADR-001, ADR-015 observation identity, ADR-005 and runtime schemas. The lineage rule is that evidence proves change, observations remember change, and recommendations require inspectable lineage.

## Terminology Analysis

| Term | Owner / source | Observation |
| --- | --- | --- |
| Evidence | FP-004 / EI-012 | Used consistently as proof rather than intelligence. |
| Observation | EI-012 / ADR-001 | Atomic Enterprise Intelligence unit. |
| Enterprise Model | EI-001 / ADR-002 | Durable memory. |
| Knowledge Graph | EI-002 | Relationship structure. |
| Unknown / Contradiction | Reference Architecture / EI-012 / runtime schemas | First-class states. |
| Knowledge Pack | FP-010 / ADR-016 / Knowledge Pack Specification | Exchange mechanism, not ownership source. |
| Commercial Digital Twin | Blueprint Contract / FP-003 / ADR-009 | Governed twin state. |
| Flora | FP-003 / FEIR-001 / ADR-025 | Runtime/product workspace. |

## Cross Reference Matrix

| Source | References / packages / implements |
| --- | --- |
| Document Map | Reference Architecture, CIOS-AI, Design Doctrine, Handbook, ADRs, AP/RP standards, EI owners. |
| Authority Registry | Authority classification and release-profile membership for AP-001, AP-002, RP-001, RP-002, DD-001 and other canonical material. |
| Source map | Governance mappings for researcher mission, industry twin lifecycle, evidence, observations, enterprise model, knowledge graph, behaviour, hypotheses, readiness, architecture handover and pack configuration. |
| Manifest | Concrete packaged file list and checksums for researcher Knowledge Pack. |
| Build script | Implements manifest-driven staging, validation, index/checksum generation and ZIP output. |
| Tests | Validate architecture metadata/profile compiler, Knowledge Pack, models, runtime and Flora behaviours. |

## Architecture Consistency Review

| Finding | Evidence | Classification | Owning documents |
| --- | --- | --- | --- |
| Duplicate ADR-003 identifiers | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md` and `architecture/decisions/ADR-003-uk-banking-theme-taxonomy.md` | Review Required | ADR index / Document Map / Authority Registry |
| Duplicate ADR-015 identifiers | `architecture/decisions/ADR-015-Observation-Identity-and-Minimal-Model-Projection.md` and `architecture/adr/ADR-015-Runtime-Mission-Context.md` | Review Required | ADR index / Document Map / Authority Registry |
| AP-001 exists in base and v1.1 files | Two AP-001 standard files exist, both marked Accepted | Review Required | AP-001 / Authority Registry |
| FP-002 and FP-007 share the title Strategic Signal Standard | Two Founding Papers use same title | Review Required | Founding Papers / Document Map |
| Some ADR status metadata absent in extracted headers | ADR-014, ADR-015 observation and ADR-024 did not expose a simple `**Status:**` header in the scanned top matter | Review Required | ADR index / Authority Registry |
| Knowledge Pack excludes any source not listed in manifest | Build script only copies manifest documents | Preserve | FP-010 / ADR-016 / manifest / build script |
| Knowledge Pack is generated, not canonical ownership | Pack manifest copies source documents and records source paths | Preserve | FP-010 / ADR-016 / Knowledge Pack Specification |

## Architecture Preservation Assessment and Recommendations

| Recommendation | Classification | Owner references |
| --- | --- | --- |
| Preserve the Reference Architecture as the top-level navigation and governance entry point. | Preserve | Reference Architecture, Document Map, Authority Registry |
| Preserve EI-001, EI-002, EI-003 and EI-012 as the core Enterprise Intelligence ownership spine. | Preserve | EI-001, EI-002, EI-003, EI-012, ADR-001, ADR-002 |
| Preserve Knowledge Packs as packaging and exchange artifacts rather than canonical concept owners. | Preserve | FP-010, FP-011, ADR-016, Knowledge Pack Specification |
| Review duplicate ADR identifiers before future ADR authoring or automated compilation. | Review Required | ADR index, Document Map, Authority Registry |
| Review AP-001 base/v1.1 supersession relationship before depending on one file as canonical. | Review Required | AP-001, AP-001 v1.1, Authority Registry |
| Extend future architecture by changing the owning document first, then generated/profile/packaging surfaces second. | Extend | Authority Registry, AP-001, AP-002, RP-001, manifest, source map |
| Do not refactor terminology until Chief Architect review resolves duplicate IDs and strategic signal ownership. | Review Required | FP-002, FP-007, ADR index |

## Appendices

### Appendix A — Repository Inventory Method

Inventory used repository file enumeration with `rg --files`, targeted reads of the Reference Architecture, Document Map, Authority Registry, Knowledge Pack manifest, source map and build script, plus scripted header extraction for Markdown files under `architecture/`.

### Appendix B — Completion Artefacts Produced

This single report contains the Architecture Baseline Report, Repository Inventory, Canonical Ownership Matrix, Dependency Matrix, Knowledge Pack Build Analysis, Workflow Analysis, Cross Reference Matrix, Architecture Consistency Review, Architecture Preservation Assessment and Executive Summary requested by WP-008. It intentionally does not alter architecture workflows, manifests, source maps, templates, Knowledge Pack generation or canonical document identifiers.
