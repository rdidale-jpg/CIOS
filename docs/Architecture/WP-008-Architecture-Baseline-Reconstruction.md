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
| ADR-003 | Governed UK Banking Theme Taxonomy | `architecture/decisions/UK-Banking-Theme-Taxonomy-Decision.md` | not explicit | ADR | repository-current | UK banking theme taxonomy; duplicate ADR ID requires review. |
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
| ADR-015 | Observation Identity and Minimal Model Projection | `architecture/decisions/Historical-Observation-Identity-and-Minimal-Model-Projection-Draft.md` | not explicit | ADR | repository-current | Observation identity. |
| ADR-015 | Runtime Mission Context Architecture | `architecture/decisions/ADR-015-Runtime-Mission-Context.md` | Accepted | ADR | repository-current | Runtime mission context; duplicate ADR ID requires review. |
| ADR-016 | Knowledge Packs as the Standard Exchange Mechanism | `architecture/decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md` | Accepted | ADR | repository-current | Knowledge Packs as exchange mechanism. |
| ADR-023 | Enterprise Understanding as the Primary Governed Asset | `architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md` | Proposed | ADR | repository-current | Enterprise understanding. |
| ADR-024 | Hybrid Enterprise Intelligence Runtime | `architecture/decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md` | not explicit | ADR | repository-current | Hybrid EI runtime. |
| ADR-025 | Flora as the Enterprise Intelligence Workspace | `architecture/decisions/ADR-025-Flora-as-the-Enterprise-Intelligence-Workspace.md` | Proposed | ADR | repository-current | Flora workspace role. |

### Standards, specifications, profiles and missions

| ID | Title | Path | Status | Type | Version | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| AP-001 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md` | Accepted | Process standard | repository-current | Registry-backed compilation profiles and non-promotion rules. |
| AP-001 v1.1 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard-v1.1-Historical-Copy.md` | Accepted | Process standard | v1.1 | Later AP-001 file; relationship to base AP-001 requires review. |
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

Mission architecture exists in two places: runtime mission context is governed by `architecture/decisions/ADR-015-Runtime-Mission-Context.md`, while researcher pack mission execution is governed by `knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md`, `knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md`, and `knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md`. The source map explicitly groups researcher mission governance as RKI-001, RG-001 and MISSION-UKCG-001.

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
| Duplicate ADR-003 identifiers | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md` and `architecture/decisions/UK-Banking-Theme-Taxonomy-Decision.md` | Review Required | ADR index / Document Map / Authority Registry |
| Duplicate ADR-015 identifiers | `architecture/decisions/Historical-Observation-Identity-and-Minimal-Model-Projection-Draft.md` and `architecture/decisions/ADR-015-Runtime-Mission-Context.md` | Review Required | ADR index / Document Map / Authority Registry |
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

---

# WP-008 Extension — Architecture Semantic Boundary Review

## Evidence labelling used in this extension

- **Explicit** — directly stated in an authoritative or owning document.
- **Implied** — strongly supported across documents but not directly defined.
- **Conflicting** — authoritative sources disagree or duplicate authority creates ambiguity.
- **Unknown** — insufficient repository evidence.
- **Implementation-only** — present in code, tests or runtime but not canonically defined.

## A. Semantic Boundary Matrix

| Concept | Explicit definition | Semantic owner | Runtime owner | Related concepts | Boundary | Evidence status |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence | Attributable proof that supports Observations; EI-012 states evidence supports Observations and the canonical chain begins with Evidence. | FP-004 for acquisition; EI-012 for observation linkage. | Flora evidence package/retrieval services under FEIR/EIRP; code schemas/tests validate lineage. | Source, Observation, Recommendation, Unknown, Contradiction. | Evidence is not intelligence conclusion or recommendation. | Explicit |
| Observation | Structured statement about meaningful enterprise change, condition, relationship, absence or contradiction, supported by evidence. | EI-012; ADR-001 for atomic intelligence unit. | Observation repositories and Flora runtime projections. | Evidence, Signal, Hypothesis, Enterprise Model, Recommendation. | Observation is durable intelligence atom; not raw document, report or generated prose. | Explicit |
| Enterprise Model | Canonical enterprise object and durable CIOS memory for each monitored organisation. | EI-001; ADR-002. | Flora memory repository and read models. | Enterprise Twin, Knowledge Graph, Behaviour, Observations. | Durable model state; reports/briefs/opportunity predictions are views or reasoning products. | Explicit |
| Enterprise Knowledge Graph | Graph connecting the Commercial Digital Twin; represents enterprises, executives, suppliers, contracts, programmes, technologies, pressures, hypotheses and recommendations as evidence-lined relationships. | EI-002. | Runtime graph projection in Flora/EIRP. | Enterprise Model, Supplier, Contract, Capability, Opportunity. | Relationship structure, not presentation; inferred links need explanation. | Explicit |
| Behaviour | Enterprise behaviour semantics derive from EI-003 and graph/model state. | EI-003. | Reasoning services and presentation components. | Mechanisms, Patterns, Enterprise Model, Opportunity. | Behaviour describes how the enterprise repeatedly acts; not a supplier capability model. | Explicit/Implied |
| Mission | Bounded objective for one runtime execution with outcome, scope, acceptance criteria, deliverables and constraints. | ADR-015 Runtime Mission Context; researcher mission files for mission-specific content. | AI-agent runtime context; Researcher GPT instructions; Flora future runtime. | Research Policy, Capability Profile, Knowledge Pack mission file. | Runtime configuration; does not redefine canonical terms or durable model doctrine. | Explicit |
| Commercial Capability | Capability appears as supplier/participant state in MPT-001 and as graph supplier attributes in EI-002; solution positioning consumes proof points and evidence demands. | MPT-001 for participant capability claims; EI-014/OPI-001 for positioning; EI-002 for graph relationship projection. | Runtime graph projections and positioning/recommendation services. | Supplier, Participant, Offering, Delivery Evidence, Provider Fit. | Durable where stored in Market Participant Twin/EKG; account-relative fit belongs in APPA-001 or positioning, not generic participant strength. | Explicit/Implied |
| Opportunity | Commercially significant transformation opportunity discovered after Enterprise Twin foundation and prioritised before OT-001. | EI-006 owns opportunity prediction; EOD-001 owns discovery method; OT-001 owns Review object shape. | EIRP/Flora candidate intelligence and opportunity runtime views. | Signal, Hypothesis, Thesis, Provider Fit, Recommendation. | Opportunity is not a procurement alone; procurements are evidence of change. | Explicit |
| Recommendation | Proposed action requiring inspectable lineage. | ADR-005 and ADR-008; EIRP recommendation policy operationalises. | Recommendation Policy Service in EIRP/Flora. | Evidence, Observation, Signal, Hypothesis, Commercial Assessment. | Cannot be emitted from raw documents without lineage; weak lineage downgrades to learning/evidence demand. | Explicit |
| Enterprise Twin | Durable governed memory explaining one enterprise's evidence, state, mechanisms, pressures, behaviours, Unknowns and Contradictions. | EI-001/EI-002/EI-003/EI-012; IT-001 uses this definition in hierarchy. | Flora twin/workspace read models; enterprise memory repositories. | Industry Twin, Opportunity Twin, Commercial Digital Twin. | Represents a monitored enterprise. Repository evidence does not limit it to “target” enterprises only. | Explicit/Implied |
| Market Participant Twin | Governed, evidence-aware twin for an organisation or actor participating in a market around an Enterprise Twin, Industry Twin, Opportunity Twin or account context. | MPT-001, with EI-013/EI-002 semantic authorities. | Market Participant Knowledge Pack/presentation; runtime graph projection. | Supplier, Competitor, Partner, Adviser, Systems Integrator, Technology Vendor. | Participant state is durable; account-relative strength/fit is outside generic twin state. | Explicit |
| Opportunity Twin | Governed, evidence-aware model of a commercial opportunity; Review material under EI-006. | EI-006; OT-001 Review specification. | Documentation-only currently; candidate opportunity runtime views are implementation/runtime-specific. | EOD-001, RTP-001, OPI-001, Recommendation. | Makes opportunity state inspectable; does not change Enterprise Model, Observation Model or Knowledge Graph. | Explicit with Review boundary |
| Industry Twin | Durable Enterprise Intelligence object accumulating cross-enterprise learning about an industry. | IT-001 Review specification; EI owners retained for underlying semantics. | Documentation-only; Knowledge Pack mission produces industry twin research. | Enterprise Twins, Patterns, Opportunity Themes, Opportunity Twins. | Synthesises; never overwrites Enterprise Twins; cannot select suppliers or create provider fit. | Explicit with Review boundary |
| Commercial Digital Twin | EI-001 defines it as commercially relevant model of a monitored enterprise; EIRP says living Commercial Digital Twins are durable core asset; RG-001 uses the term for researcher method. | EI-001 for enterprise CDT semantics; blueprint/import specs for governed blueprint format; ADR-009 for progressive assurance. | Flora blueprint import, canvas and twin views. | Enterprise Model, Enterprise Twin, Presentation Model, Knowledge Pack. | Term is both an enterprise model/twin concept and used in blueprint/research packaging contexts; current architecture does not prove a separate non-enterprise twin type. | Conflicting/Implied |

## B. Twin Taxonomy Matrix

| Twin type | Subject | Purpose | Inputs | Durable state | Outputs | Owner | Relationship to other twins |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Enterprise Twin | One monitored organisation/enterprise. | Preserve enterprise-specific evidence, state, mechanisms, pressures, behaviours, Unknowns and Contradictions for reasoning. | Evidence, Observations, Enterprise Model attributes, Knowledge Graph relationships, Behaviour assessments. | Enterprise Model plus graph/behaviour/observation memory. | Signals, hypotheses, opportunity portfolio, reports/views, learning updates. | EI-001/EI-002/EI-003/EI-012; ADR-002. | Feeds Industry Twin synthesis; source for EOD-001 opportunity discovery; may be context around Market Participant Twins. |
| Industry Twin | An industry across multiple enterprises. | Accumulate cross-enterprise learning about industry structures, behaviours, mechanisms, pressures, patterns and commercial dynamics. | Enterprise Twins, observations, mechanisms, patterns, evidence and comparison method. | Industry-level claims with lineage, participating enterprises, Unknowns, Contradictions and validation state. | Industry opportunity themes, questions, evidence demands and contextual reasoning. | IT-001 Review. | Synthesises Enterprise Twins but never overwrites them; can contextualise Opportunity Twins but not produce provider fit. |
| Market Participant Twin | Organisation/actor participating in a market around an enterprise, industry, opportunity or account. | Preserve participant identity, type, capabilities, offerings, relationships, account presence, delivery evidence, strengths, weaknesses, Unknowns and Contradictions. | Evidence, Observations, human-supplied labels, market/account context, relationship data. | Participant sections including capabilities, offerings, delivery evidence, alliances, procurement routes and claim classifications. | Participant Knowledge Pack, presentation model, graph projection, account-relative assessment inputs. | MPT-001 with EI-013/EI-002 semantic authorities. | May represent supplier, competitor, partner, adviser, SI, vendor or challenger; connects to Enterprise/Opportunity through EI-002 and APPA-001. |
| Opportunity Twin | One selected commercial opportunity in enterprise-specific context. | Make opportunity state inspectable for need, pressure, timing, decision route, participant relationships, evidence, hypotheses and recommendations. | Enterprise Twin/EOD output, research sprint output, RTP-001 handover, OPI candidate positioning objects, Observations. | Opportunity identity, need, pressure, scope, confidence, freshness, Unknowns, Contradictions, lineage. | Positioning objects, decision envelope, recommendation lineage, next learning actions. | EI-006; OT-001 Review. | Created after opportunity prioritisation; may include participant relationships and OPI positioning but does not itself validate supplier claims. |
| Commercial Digital Twin | Commercially relevant model of a monitored enterprise; also used as governed blueprint/research term. | Support commercial decision questions about enterprise identity, economics, operation/change, behaviour and opportunity emergence. | Enterprise Model, graph, observations, behaviour, pressures, hypotheses and opportunity signals; blueprint imports where governed. | Living enterprise model/twin state where accepted; blueprint candidate state before acceptance. | Flora canvas/views, executive intelligence, opportunity outlook, knowledge packs. | EI-001 for semantic definition; blueprint contract/import specs and ADR-009 for governed maturity/import. | Overlaps strongly with Enterprise Twin. Distinctness is unresolved: explicit EI-001 ties it to monitored enterprise, while other docs use CDT as guide/blueprint umbrella. |
| Presentation Twin/Presentation Model | Audience-specific rendering of a twin, not a separate canonical subject. | Present governed twin content for declared audience/purpose. | Accepted twin data plus presentation rules. | Optional governed rendering payload, not canonical fact promotion. | UI/report/card/brief. | TPM-001. | May attach to Market Participant Twin or other twins; acceptance does not upgrade claims. |

### Direct answers — Twin Taxonomy

- **Does an Enterprise Twin represent only target enterprises, or any enterprise?** **Implied: any monitored enterprise.** EI-001 says each monitored organisation; EOD targets “given an enterprise”. The repository uses “target enterprise” in opportunity context, but no owning definition limits Enterprise Twin to targets only.
- **Does a Market Participant Twin represent suppliers, partners and competitors?** **Explicit: yes.** MPT-001 lists supplier, competitor, partner, adviser, systems integrator, technology vendor and specialist challenger.
- **Is a Commercial Digital Twin distinct, umbrella, blueprint format, or maturity state?** **Conflicting/Implied.** EI-001 explicitly defines it as the commercially relevant model of a monitored enterprise. Blueprint/import and progressive assurance material use Commercial Digital Twin as governed blueprint/maturity language. Evidence does not establish a separate non-enterprise twin type.
- **Can the same organisation have both an Enterprise Twin and a Market Participant Twin?** **Implied: yes.** One organisation may be a monitored enterprise and also participate as supplier/partner/competitor around another account. No document forbids dual modelling, but no explicit lifecycle rule defines identity reconciliation.
- **Where is the buyer-versus-supplier distinction encoded?** **Explicit in EI-002 and EOD/MPT.** EI-002 has Supplier, Contract and Procurement entities with buyer/supplier attributes; EOD captures buyer and known/likely suppliers; MPT encodes participant_type. There is no single buyer/supplier doctrine document beyond these model locations.
- **Is an Opportunity Twin produced from relationships between other twins?** **Implied.** EOD starts from Enterprise Twin; OT contains participant relationships; Industry Twins identify themes but cannot assert an individual opportunity. The relationship is not defined as a graph algorithm that produces OT from twin-to-twin relationships.

## C. Opportunity Formation Trace

1. **Observable reality and sources appear.** Source material is collected under evidence acquisition/source-quality doctrine. Classification: **Explicit**.
2. **Evidence is captured.** Evidence records attributable proof; raw evidence is not itself a conclusion. Classification: **Explicit**.
3. **Observations are created.** EI-012 defines Observations as evidence-backed durable intelligence atoms for change, condition, event, relationship, absence or contradiction. Classification: **Explicit**.
4. **Enterprise Model and Knowledge Graph update.** EI-001 states Observations update the model; EI-002 connects enterprises, executives, suppliers, contracts, programmes, technologies, pressures, hypotheses and recommendations. Classification: **Explicit**.
5. **Signals emerge.** EI-012 places Strategic Signal after Observation; FP-002/FP-007 duplicate strategic signal standards create title ambiguity. Classification: **Explicit with Conflicting identifier/title context**.
6. **Hypotheses form and are validated.** FP-009 owns hypothesis validation; EI-012 chain proceeds Signal → Hypothesis; hypotheses require supporting/contradicting evidence and unknowns. Classification: **Explicit**.
7. **Commercial thesis/conviction forms.** EI-004 and FP-008 govern commercial reasoning/conviction; EI-012 chain places Commercial Thesis before Recommendation. Classification: **Explicit**.
8. **Enterprise foundation precedes discovery.** EOD-001 states EOD begins after EIF-001 has produced the initial Enterprise Twin. Classification: **Explicit**.
9. **Opportunity discovery is enterprise-first and provider-neutral.** EOD says research the enterprise, not procurement, and keep Provider Fit separate from public research. Classification: **Explicit**.
10. **Opportunity portfolio and prioritisation are produced.** EOD required outputs include Enterprise Change Portfolio, Programme Landscape, Procurement Landscape, Opportunity Landscape, Emerging Opportunities, Opportunity Prioritisation and Decision Envelope. Classification: **Explicit**.
11. **Opportunity Twin begins after prioritisation.** EOD lifecycle orders Opportunity Prioritisation before OT-001 Opportunity Twin. Classification: **Explicit**.
12. **Research Sprint and RTP-001 handover carry selected opportunity evidence.** OT-001 consumes RTP-001 handover, preserving evidence lineage, opportunity scope, Unknowns, Contradictions, caveats and decision envelope. Classification: **Explicit**.
13. **OPI-001 positioning contributes candidate objects.** OPI creates candidate positioning statement, buyer/stakeholder frame, problem narrative, value hypothesis, proof points, evidence demands and next learning action. Classification: **Explicit Review**.
14. **Provider fit enters after public research.** EOD puts Provider Fit outside public research after Decision Envelope and before Executive Pursuit; MPT says participant strength is account-relative and APPA owns account-relative claims. Classification: **Explicit**.
15. **Recommendations require inspectable lineage.** ADR-005/EIRP require Evidence → Observation → Mechanism/Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation. Classification: **Explicit**.
16. **Human judgement enters at selection, validation, review and strong action approval.** EOD prioritisation/research selection is judgemental; EIRP requires human review for accepting candidate Observations, lifecycle changes, contradiction resolution, strong Recommendations and write-back. Classification: **Explicit/Implied**.
17. **Learning updates originating twins only through governance.** EOD lifecycle ends with Learning → Enterprise Twin evolves; EIRP says write-back requires validation, review, change proposal, governance, acceptance and re-ingestion. Classification: **Explicit**.

### Direct answers — Opportunity Formation

- **Does opportunity discovery begin from target-enterprise pain independently of suppliers?** **Explicit: yes for discovery.** EOD starts from Enterprise Twin, programmes, pressures and opportunities, not procurements or providers; supplier facts may be captured where evidenced but Provider Fit is separate.
- **At what point does supplier/provider fit enter?** **Explicit: after Decision Envelope/public research, before Executive Pursuit.** Supplier relationships may be evidence in programme/procurement landscape earlier, but provider-specific fit claims are excluded until later.
- **Is Opportunity Intelligence durable model, reasoning process, or both?** **Both, with boundary.** EI-006/EOD define reasoning/discovery; OT-001 defines a Review durable inspectable Opportunity Twin shape. Runtime candidate views are not canonical by themselves.
- **Which document owns demand-side need meets supply-side capability?** **Conflicting/Distributed.** EOD owns demand-side opportunity discovery and explicitly excludes provider fit; MPT/APPA own participant/account-relative strength; OPI/EI-014 own positioning; RTP owns handover. No single accepted document owns the full bridge.

## D. Mission Context Trace

1. **Mission definition.** ADR-015 defines Mission as bounded objective for one runtime execution. MISSION-UKCG-001 is a concrete industry-twin mission file in the Researcher pack. Classification: **Explicit**.
2. **Research policy and capability profile.** ADR-015 separates Research Policy and Capability Profile from Mission and says they assemble into Runtime Context. Classification: **Explicit**.
3. **Researcher execution guidance.** Researcher GPT Instructions provide behavioural kernel; RG-001 provides detailed method and route from mission intake through handover. Classification: **Explicit**.
4. **Domain ontology/source strategy.** Mission file and source map provide mission-specific scope/source expectations; Knowledge Pack manifest packages them. Classification: **Explicit**.
5. **Knowledge Pack generation.** Manifest enumerates documents; build script validates checksums and copies only listed files. Classification: **Explicit**.
6. **Flora runtime.** FEIR/EIRP consume governed context and runtime mission context as configuration; ADR-015 says runtime context configures execution but does not replace Source/Evidence/Observation/Knowledge/Reasoning/Presentation/Knowledge Pack/Flora architectures. Classification: **Explicit/Implied**.
7. **Resulting enterprise state.** ADR-015 says Runtime Context is not durable knowledge and cannot silently write doctrine or model state; Observation/model updates must follow owning process. Classification: **Explicit**.

### Direct answers — Mission Architecture

- **Is a Mission Pack already defined under another name?** **Unknown.** The repository defines Knowledge Packs and mission files inside the Researcher Knowledge Pack, but no explicit “Mission Pack” specification was found.
- **Is the current mission file executable configuration, human guidance, or both?** **Implied: both-adjacent but primarily human/agent guidance packaged as Knowledge Pack content.** ADR-015 defines executable runtime inputs; MISSION-UKCG-001 is a mission document included by manifest, not a separate machine schema.
- **What mission information is available at runtime?** **Explicit:** mission objective, scope, acceptance criteria, deliverables, constraints, completion expectations when declared/inherited; plus policy, capability, repository authority, workspace state and human constraints in Runtime Context.
- **Does mission context influence observation creation, confidence, twin structure or presentation?** **Explicit boundary:** it may guide whether Observation/model update is in scope, research depth and source posture; it cannot change Observation semantics, Evidence doctrine, Enterprise Model meaning or Knowledge Graph ownership. Influence on presentation is implied through output channels/profile, not canonically specified as twin structure mutation.
- **Where should mission provenance be retained?** **Explicit/Implied:** ADR-015 permits future persistence of runtime execution metadata for audit but says persistence does not make runtime configuration durable EI memory. EIRP lineage/audit metadata is the runtime location; canonical twin updates must retain source/observation lineage, not mission rules as doctrine.

## E. Ownership Layers Matrix

| Concept | Doctrine owner | Semantic owner | Schema owner | Runtime implementation owner | Knowledge Pack packaging owner | Presentation owner |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence | FP-004, ADR-010, DD-001 | EI-012 linkage | schemas/core/runtime package schemas | Flora retrieval/evidence package code | Knowledge Pack manifest/source map for packaged guidance | Flora/TPM when rendered |
| Observation | ADR-001, EI-012 doctrine | EI-012 | observation schemas/models | ObservationRepository, ObservationMemoryService, EIRP Observation Analyst | Researcher templates/source-map observations entry | Flora views, FA-001 workspace |
| Enterprise Model | ADR-002 | EI-001 | enterprise model schemas/models | EnterpriseModelRepository, Flora canvas/read models | Researcher pack EI-001 copy | Enterprise Canvas/TPM/Flora |
| Knowledge Graph | DD-001/RA | EI-002 | relationship/graph schemas where present | Runtime Knowledge Graph Projection | Researcher pack EI-002 copy/source-map | Flora relationship views |
| Behaviour | EI-003 doctrine | EI-003 | behaviour model schemas where present | Reasoning/runtime behaviour assessment | Researcher pack behaviour guidance | Flora explain/presentation |
| Mission | ADR-015 | ADR-015 plus concrete mission docs | no canonical Mission Pack schema found | AI-agent runtime context; future Flora-native missions | Researcher manifest packages MISSION-UKCG-001 | Completion reports/Flora outputs |
| Commercial Capability | MPT-001/EI-004/EI-014 | MPT-001 for participant claims; EI-014/OPI for positioning | participant/assessment schemas unknown | Runtime graph/projection and provider/account assessment if implemented | Market Participant Knowledge Pack; Researcher supplier checklist | TPM/participant presentation |
| Opportunity | EI-006/EOD doctrine | EI-006, EOD-001, OT-001 Review | opportunity twin schema unknown | EIRP candidate intelligence/opportunity views | RTP/OPI/OT docs not production pack unless listed | Opportunity cards/briefs |
| Recommendation | ADR-005 | ADR-005/ADR-008/EI-004 | recommendation schemas/core models | Recommendation Policy Service/EIRP/Flora | Researcher guidance where packaged | Flora executive brief/action views |
| Enterprise Twin | EI doctrine | EI-001/EI-002/EI-003/EI-012 | enterprise model/blueprint schemas | Flora memory/canvas/workspace | Enterprise Knowledge/Researcher pack outputs | Enterprise Canvas/TPM |
| Market Participant Twin | MPT-001 | MPT-001 with EI-013/EI-002 | participant twin schema not confirmed | Implementation unknown except runtime graph projections/tests with supplier context | Market Participant Knowledge Pack | TPM participant presentation |
| Opportunity Twin | EI-006/OT-001 Review | OT-001 under EI-006 | opportunity twin schema not confirmed | Documentation-only; candidate runtime views | Knowledge packs if manifest includes later | Opportunity presentation objects |
| Commercial Digital Twin | EI-001/ADR-009/FP-003 | EI-001 for enterprise CDT; blueprint specs for import | blueprint import schemas | Flora blueprint import/canvas | Researcher Knowledge Pack and enterprise knowledge packages | Flora CDT views/TPM |

## F. Commercial Capability Model Findings

| Question | Evidence found | Classification | Current answer |
| --- | --- | --- | --- |
| Is there already a durable supplier capability model? | MPT-001 requires capabilities, offerings, delivery evidence, alliances, procurement routes and evidence-governed strengths/weaknesses; EI-002 has Supplier attributes including capabilities, frameworks and incumbent positions. | Explicit/Implied | Yes, but under Market Participant Twin/EKG rather than a standalone accepted “Supplier Capability Model”. MPT is Draft Normative; EI-002 is Draft. |
| Is provider fit modelled independently of an opportunity? | EOD excludes Provider Fit from public research; MPT says participant strength is account-relative and belongs in APPA or governed interpretation. | Explicit | Generic capability is independent participant state; provider fit is account/opportunity-relative, not absolute. |
| Where are supplier evidence, credentials and delivery history stored? | MPT sections include delivery evidence, account presence, alliances, procurement routes and evidence lineage; EI-002 Supplier/Contract/Framework nodes store supplier, capabilities, frameworks, incumbent positions and source links. | Explicit | Market Participant Twin and Enterprise Knowledge Graph; delivery history through contracts/case studies/outcomes/references where evidenced. |
| Can capability be compared across providers? | MPT controls claim classification and fields; APPA implies account-participant assessment; EI-002 makes graph queryable. | Implied | Comparable when normalised by taxonomy/evidence status/account context, but no accepted cross-provider comparison algorithm found. |
| Is commercial capability part of the Enterprise Knowledge Graph? | EI-002 Supplier attributes include capabilities and Contract capability; MPT graph projection includes HAS_STRENGTH/HAS_WEAKNESS Capability. | Explicit | Yes as graph attributes/relationships, while participant twin stores richer participant claim state. |
| How are claims validated? | MPT requires evidence-backed/inferred/human-supplied/unknown/contradictory classification; marketing claims alone cannot establish strength. | Explicit | By evidence/observation lineage, corroboration, freshness, contradiction state and validation questions. |
| How are contradictions/unknowns represented? | MPT says Unknowns and Contradictions are first-class model objects; EI-012 and doctrine preserve them. | Explicit | As first-class model state with affected claim/relationship, why it matters, evidence needed, owner/action, confidence impact and review trigger. |

## G. Architecture Authority Resolution

| Authority issue | Repository evidence | Classification | Current effective answer |
| --- | --- | --- | --- |
| Handbook vs Accepted ADR | FA-001 states where it conflicts with Accepted ADR or owning architecture paper, the Accepted ADR or owning paper prevails; ADRs are enduring decisions constraining implementation. | Explicit/Implied | Accepted ADR prevails over Handbook guidance when conflict exists. |
| Reference Architecture summary vs owning EI paper | FA-001 says owning architecture papers prevail; Document Map/Authority Registry treat RA as navigation/governance, not semantic replacement. | Explicit/Implied | Owning EI paper prevails for semantic detail; RA summary should be reconciled. |
| Tests establishing architecture | Tests validate profile/compiler/runtime behaviour; AP-001 says compilation/profile mechanics do not promote authority. | Explicit/Implied | Tests can validate/enforce architecture but do not establish canonical architecture by themselves. |
| Knowledge Pack manifest promoting review doc | Manifest packages files and build validates checksums; AP-001/ADR-016 packaging does not create canonical ownership. | Explicit | No. A manifest can include/copy a review document but cannot promote it into accepted authority. |
| Duplicate ADR identifiers | ADR-003 and ADR-015 duplicates found in architecture catalogue. | Conflicting | Effective authority is ambiguous for identifier-based automation; Chief Architect decision required. |
| Which AP-001 file automation uses | Tests and registry references must be checked by path; both AP-001 base and v1.1 exist and are Accepted. | Conflicting | Unknown without inspecting automation resolution; existing report flags review required. |

## H. Executable Architecture Enforcement Trace

| Enforcement point | Architecture source | Implementation file(s) | Test file(s) | Status | Divergence |
| --- | --- | --- | --- | --- | --- |
| Observation identity/minimal projection | ADR-015 Observation Identity duplicate; EI-012 | Blueprint import/memory models | `tests/test_flora_blueprint_import_validation.py`, `tests/test_flora_blueprint_import_restage.py`, `tests/test_memory_models.py` | Enforced in tests | ADR-015 duplicate ID creates authority ambiguity. |
| Evidence lineage | EI-012, ADR-010, ADR-005 | Flora memory/reasoning/package builders | `tests/test_reasoning_models.py`, `tests/test_flora_runtime_alignment.py`, `tests/test_flora_increment22_evidence_trust.py` | Partially enforced | Runtime enforcement exists but not every architecture path has schema evidence. |
| Human-supplied knowledge labels | ADR-004, EI-001, MPT-001 | Runtime package/candidate models | Runtime alignment/blueprint tests | Partially enforced | Strong doctrine; exact complete schema coverage unknown. |
| Unknowns and Contradictions | EI-012, MPT-001, DD-001 | Runtime explain and package objects | Flora explain/runtime tests | Partially enforced | First-class in doctrine; coverage by twin type validation unknown. |
| Recommendation lineage | ADR-005, EIRP | Recommendation policy/runtime reasoning | `tests/test_reasoning_models.py`, executive guardrail tests | Enforced conceptually | ADR-008 remains Proposed; runtime may enforce subset. |
| Knowledge Pack profile membership | AP-001/AP-002/RP-001/ADR-016 | `tools/knowledge-packs/build_researcher_pack.py` | `tests/knowledge_packs/test_researcher_pack.py` | Enforced | Cannot promote authority; validates manifest/checksums/membership. |
| Mission context | ADR-015 Runtime Mission Context | Researcher instructions/mission files; future Flora runtime | Knowledge pack tests where mission packaged | Weak/partial | Accepted ADR exists; canonical runtime schema/persistence implementation not confirmed. |
| Twin type validation | EI-001, IT-001, MPT-001, OT-001, TPM-001 | Blueprint import/canvas; participant/opportunity schemas not confirmed | Blueprint/twin pilot tests | Partial/unknown | Enterprise/CDT import has tests; MPT/OT are mostly documentation-only/review without confirmed runtime validators. |

## I. Unresolved Questions Register

| Question | Documents searched | Evidence found | Classification | Architectural consequence | Chief Architect decision required |
| --- | --- | --- | --- | --- | --- |
| Is Commercial Digital Twin a distinct twin type or enterprise twin synonym? | EI-001, FP-003, ADR-009, blueprint import docs, RG-001, EIRP | EI-001 defines CDT as monitored enterprise model; other docs use CDT as blueprint/research/maturity term. | Conflicting/Implied | Tooling and taxonomy may conflate enterprise semantic model with blueprint/package/maturity state. | Decide whether CDT term remains enterprise-specific, umbrella, blueprint format, or maturity state. |
| Can one organisation be both Enterprise Twin and Market Participant Twin with shared identity? | EI-001, EI-002, MPT-001 | Nothing forbids; MPT can represent any participant, EI-001 any monitored organisation. | Implied/Unknown | Duplicate identity risk across graph/twin stores. | Define identity reconciliation if needed. |
| Which accepted document owns demand-side need meets supply-side capability? | EOD-001, OT-001, RTP-001, OPI-001, MPT-001, APPA-001, EI-014 | Ownership distributed and several docs are Review/Draft. | Conflicting/Unknown | Provider fit boundary remains distributed; implementation may vary. | Assign or confirm bridge ownership without inventing new architecture. |
| Is there an accepted durable supplier capability schema? | EI-002, MPT-001, APPA-001, schemas, tests | Capability appears in EI-002/MPT; no standalone accepted schema found. | Unknown/Implementation-only | Capability comparison may lack canonical validation contract. | Decide whether existing MPT/EKG ownership is sufficient. |
| When exactly is Opportunity Twin persisted? | EOD-001, OT-001, EIRP, runtime tests | Lifecycle places OT after prioritisation; OT is Review documentation-only. | Explicit/Unknown runtime | Runtime may have candidate opportunity views without canonical OT persistence. | Define persistence gate when OT moves beyond Review. |
| Is Mission Pack an existing concept? | ADR-015, RG-001, RP-001, MISSION-UKCG-001, manifest/source-map | Knowledge Pack contains missions; no Mission Pack spec. | Unknown | Avoid creating pack type accidentally. | Decide only if mission packaging needs formalisation. |
| Which AP-001 is authoritative for automation? | AP-001 base, AP-001 v1.1, Authority Registry, tests/build scripts | Two Accepted AP-001 files exist. | Conflicting | Profile compilation can depend on path-specific behaviour. | Resolve duplicate/supersession path. |
| Duplicate ADR identifiers and authority order | ADR catalogue, Document Map, Authority Registry | ADR-003 and ADR-015 duplicates. | Conflicting | Identifier-based reference may bind wrong document. | Resolve duplicate identifiers or define disambiguation rule. |
| Are MPT and OT production runtime objects? | MPT-001, OT-001, FEIR/EIRP, tests | MPT draft normative; OT Review documentation-only; runtime graph mentions participants/capabilities/opportunities. | Unknown/Implementation-only | Runtime may expose concepts before canonical validators exist. | Decide implementation acceptance boundary. |

## J. Evidence Source Index for Extension

| Evidence topic | Exact repository evidence referenced | Label |
| --- | --- | --- |
| Enterprise Model/CDT | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md` states the purpose is to define the canonical enterprise object for each monitored organisation; it also says the Enterprise Model is durable CIOS memory and that reports, briefs, hypotheses, recommendations and opportunity predictions are views or reasoning products. | Explicit |
| Commercial Digital Twin as enterprise model | EI-001 states: “The Commercial Digital Twin is the commercially relevant model of a monitored enterprise.” | Explicit |
| Knowledge Graph supplier/capability storage | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md` defines a graph of enterprises, executives, suppliers, contracts, programmes, technologies, pressures, hypotheses and recommendations; Supplier attributes include capabilities, frameworks, strategic partner status and incumbent positions. | Explicit |
| Observation definition and lifecycle | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md` states Evidence supports Observations; Observations update the Enterprise Model; and the core chain is Evidence → Observation → Strategic Signal → Hypothesis → Commercial Thesis → Recommendation. | Explicit |
| Market Participant Twin subject | `architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md` defines a Market Participant Twin as a governed, evidence-aware twin for an organisation or actor participating in a market around an Enterprise Twin, Industry Twin, Opportunity Twin or account context. | Explicit |
| Market Participant covered roles | MPT-001 explicitly lists supplier, competitor, partner, adviser, systems integrator, technology vendor and specialist challenger. | Explicit |
| Market Participant capability/delivery model | MPT-001 participant intelligence sections include Capabilities, Offerings, Relationships, Account presence, Incumbent positions, Delivery evidence, Alliances, Procurement routes, Unknowns, Contradictions, Evidence lineage and Observation lineage. | Explicit |
| Provider fit/account relativity | MPT-001 states participant strength is not absolute and must be interpreted relative to account, enterprise pressure, decision ownership, access route, procurement route, incumbent context, delivery requirement and alternatives. | Explicit |
| Industry Twin definition | `architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md` defines Industry Twin as the durable Enterprise Intelligence object that accumulates cross-enterprise learning about an industry. | Explicit Review |
| Industry/Enterprise boundary | IT-001 states Enterprise Twins are authoritative; Industry Twins synthesise; Industry Twins never overwrite Enterprise Twins. | Explicit Review |
| Industry/Opportunity boundary | IT-001 states Industry Twins identify opportunity themes; Opportunity Twins explain individual opportunities; Industry Twins must not select suppliers or create Provider Fit. | Explicit Review |
| Opportunity Twin definition | `architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md` defines Opportunity Twin as a governed, evidence-aware model of a commercial opportunity and says ownership remains beneath EI-006. | Explicit Review |
| Opportunity Twin contents | OT-001 contents include enterprise context, affected capabilities, need, pressure, timing, decision route, stakeholders, participant relationships, evidence, Observations, Unknowns, Contradictions, positioning objects, RTP handover, hypotheses, recommendation lineage and next learning actions. | Explicit Review |
| Opportunity discovery lifecycle | `architecture/reference-architecture/standards/EOD-001-Enterprise-Opportunity-Discovery-Standard.md` states EOD begins after EIF-001 has produced the initial Enterprise Twin and gives lifecycle steps from Enterprise through Enterprise Twin, discovery, prioritisation, OT-001, Research Sprint, RTP, OPI, Decision Envelope, Provider Fit, Executive Pursuit, Learning and Enterprise Twin evolution. | Explicit Review |
| Provider-neutral discovery | EOD-001 principles say research the enterprise, not the procurement, and keep Provider Fit separate from public research. | Explicit Review |
| OPI positioning outputs | `architecture/reference-architecture/standards/OPI-001-Opportunity-Positioning-Intelligence.md` creates candidate positioning objects for an Opportunity Twin, including positioning statement, buyer/stakeholder frame, problem narrative, value hypothesis, differentiated angle, proof points, evidence demands, objections, risks, Unknowns, Contradictions and next learning action. | Explicit Review |
| Mission/runtime context | `architecture/decisions/ADR-015-Runtime-Mission-Context.md` defines Mission, Research Policy and Capability Profile as independent runtime inputs assembled into Runtime Context; Runtime Context is transient configuration and not durable knowledge. | Explicit Accepted ADR |
| Mission boundaries | ADR-015 says runtime context can guide execution but must not silently write doctrine, promote candidate intelligence into canonical fact, or alter Evidence, Observation, Enterprise Model or Knowledge Graph meanings. | Explicit Accepted ADR |
| Runtime reasoning/lineage | `architecture/specifications/flora/EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md` requires recommendation eligibility to enforce Evidence → Observation → Mechanism/Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation and says canonical semantics remain owned by governing documents. | Explicit Proposed runtime contract |
| Authority precedence | `architecture/reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md` says where it conflicts with an Accepted ADR or owning architecture paper, the Accepted ADR or owning paper prevails. | Explicit |
| Researcher route | `knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md` gives the operating route from Mission intake through Industry scope, source map, evidence governance, Observation creation, Enterprise Model population, Knowledge Graph connection, Behaviour assessment, Hypothesis formation/validation, readiness gate and architecture handover. | Explicit |
| Knowledge Pack packaging | `knowledge-packs/researcher/manifest.yaml`, `knowledge-packs/researcher/source-map.yaml` and `tools/knowledge-packs/build_researcher_pack.py` are the packaging and validation mechanism; packaging does not alter source authority. | Explicit/Implied |
