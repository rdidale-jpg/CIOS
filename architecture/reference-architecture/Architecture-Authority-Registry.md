# CIOS Architecture Authority Registry

**Document class:** Architecture governance registry  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-14

## Purpose

This registry records architecture authority status and release-profile membership for review material that must not be mistaken for accepted architecture. It complements the Reference Architecture, Accepted ADR index and owning EI/FP papers; it does not supersede them.

## Status taxonomy

| Status | Meaning |
| --- | --- |
| Accepted | Approved architecture authority within its stated scope. |
| Draft | Work-in-progress architecture material; useful but not final authority. |
| Proposed | Submitted for decision; not accepted and not authoritative. |
| Review | Review material being evaluated; not accepted and not authoritative. |
| Superseded | Retained for history after a newer authority replaces it. |
| Rejected | Reviewed and not adopted. |

## Release-profile taxonomy

| Profile | Meaning |
| --- | --- |
| architecture-authority | Accepted or otherwise owner-designated authoritative architecture material. |
| researcher-pack | Material approved for production research-agent use. |
| reviewer-pack | Material approved for production reviewer use. |
| assurance-pack | Material approved for production Enterprise Intelligence assurance use. |
| none | No production release-profile membership. |


## Accepted architecture process standards

| ID | Title | Path | Status | Authority classification | Release-profile membership | Dependencies | Validation trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AP-001 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md` | Accepted | Architecture process standard governing compilation from the Authority Registry; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Architecture Authority Registry; Reference Architecture; Document Map | Registry-backed compilation check before any future architecture pack promotion |
| AP-002 | Architecture Metadata Standard | `architecture/reference-architecture/standards/AP-002-Architecture-Metadata-Standard.md` | Accepted | Architecture process standard governing canonical document metadata semantics; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Architecture Authority Registry; AP-001; Document Map | Registry-backed metadata compatibility check before compiler enforcement |
| RP-001 | Enterprise Blueprint Researcher Profile | `architecture/reference-architecture/profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md` | Accepted | Architecture role profile governing Enterprise Blueprint Researcher responsibilities and researcher-pack composition; documentation-only and non-runtime | architecture-authority; researcher-pack | Architecture Authority Registry; AP-001; AP-002; Document Map | Researcher-pack compilation must be non-empty and fully registry-traceable |
| RP-002 | Enterprise Intelligence Assurance Profile | `architecture/reference-architecture/profiles/RP-002-Enterprise-Intelligence-Assurance-Profile.md` | Accepted | Architecture role profile governing Enterprise Intelligence assurance responsibilities and assurance-pack composition; documentation-only and non-runtime | architecture-authority; assurance-pack | Architecture Authority Registry; AP-001; AP-002; RP-001; Document Map | Assurance-pack compilation must be non-empty, fully registry-traceable and preserve non-promotion boundaries |


## Accepted Researcher and Assurance architecture foundations

| ID | Title | Path | Status | Authority classification | Release-profile membership | Dependencies | Validation trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DD-001 | CIOS Design Doctrine | `architecture/reference-architecture/CIOS-Design-Doctrine.md` | Accepted | Accepted design doctrine governing CIOS reasoning style and evidence-first architectural intent; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; Architecture Principles | Doctrine alignment check before material Researcher-pack changes |
| RA-001 | CIOS Reference Architecture v1.0 | `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md` | Accepted | Accepted reference architecture entry point for CIOS architecture navigation and authority-chain discovery; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Document Map; Accepted ADR index; Founding Papers; Enterprise Intelligence papers | Reference architecture consistency check before material Researcher-pack changes |
| EI-001 | Enterprise Model Specification | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md` | Accepted | Accepted Enterprise Intelligence model specification defining durable enterprise memory and Commercial Digital Twin structure; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; ADR-002; EI-012 | Enterprise Blueprint research must preserve Enterprise Model memory boundaries |
| EI-012 | Enterprise Observation Model | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md` | Accepted | Accepted Enterprise Intelligence observation model defining Observations as atomic intelligence units; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; ADR-001; FP-004 | Enterprise Blueprint research must preserve Observation lifecycle and evidence lineage |
| EI-002 | Enterprise Knowledge Graph | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md` | Accepted | Accepted Enterprise Intelligence graph model defining entities, relationships and evidence-backed links; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; EI-001; EI-012 | Enterprise Blueprint research must preserve graph relationship provenance |
| EI-003 | Enterprise Behaviour Model | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md` | Accepted | Accepted Enterprise Intelligence behaviour model defining behavioural interpretation for Enterprise Blueprint reasoning; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; EI-001; EI-002 | Enterprise Blueprint research must separate behaviour patterns from unsupported recommendations |
| FP-009 | Hypothesis Validation Standard | `architecture/founding-papers/FP-009-Hypothesis-Validation-Standard.md` | Accepted | Accepted founding standard defining hypothesis lifecycle, validation and retirement; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; FP-004; EI-012 | Research findings must preserve hypothesis validation boundaries |
| GL-001 | CIOS Reference Architecture Glossary | `architecture/reference-architecture/Glossary.md` | Accepted | Accepted vocabulary authority for CIOS architecture terminology; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; Document Map | Terminology consistency check before material Researcher-pack changes |

## Relevant accepted architecture decision records

| ID | Title | Path | Status | Authority classification | Release-profile membership | Dependencies | Validation trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-001 | Observations as Atomic Intelligence Unit | `architecture/decisions/ADR-001-Observations-as-Atomic-Intelligence-Unit.md` | Accepted | Accepted ADR governing Observation granularity and reuse; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-012; Reference Architecture | Research outputs must model observations atomically |
| ADR-002 | Enterprise Model as Durable Memory | `architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md` | Accepted | Accepted ADR governing Enterprise Model memory boundaries; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; Reference Architecture | Research outputs must not treat reports as canonical memory |
| ADR-003 | CIRM and EI Separation | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md` | Accepted | Accepted ADR separating reasoning process from enterprise knowledge model; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; EI-001 | Research outputs must preserve CIRM and EI boundaries |
| ADR-004 | Human-Supplied Knowledge Must Be Labelled | `architecture/decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md` | Accepted | Accepted ADR governing labelling of human-supplied knowledge; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; EI-001 | Research outputs must label human-supplied knowledge |
| ADR-005 | No Recommendation Without Inspectable Lineage | `architecture/decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md` | Accepted | Accepted ADR requiring inspectable lineage for strong recommendations; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | Reference Architecture; EI-012 | Research outputs must preserve lineage before recommendations |
| ADR-009 | Progressive Assurance for Commercial Digital Twins | `architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md` | Accepted | Accepted ADR governing proportionate assurance and bounded Researcher autonomy; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; EI-012; FP-009 | Researcher autonomy must stay within progressive assurance boundaries |
| ADR-010 | Structured-Source-First, AI-Assisted Evidence Acquisition | `architecture/decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md` | Accepted | Accepted ADR governing source acquisition hierarchy and candidate-data treatment; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | FP-004; EI-012 | Research acquisition must prefer authoritative structured sources |
| ADR-011 | Dual-Speed Financial Intelligence | `architecture/decisions/ADR-011-Dual-Speed-Financial-Intelligence.md` | Accepted | Accepted ADR governing durable financial facts and slower interpretive reasoning; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; EI-012 | Financial research must separate facts from interpretation |
| ADR-012 | Governed Blueprint Package Import and Canonical Acceptance Boundary | `architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md` | Accepted | Accepted ADR governing blueprint package import and canonical acceptance boundaries; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; EI-012; ADR-009 | Blueprint research packages must not bypass canonical acceptance |
| ADR-013 | Enterprise Canvas as Primary Living Twin Navigation Model | `architecture/decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md` | Accepted | Accepted ADR governing Enterprise Canvas navigation of Twin state; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; EI-002; EI-012 | Research outputs must align with Enterprise Canvas navigation semantics |
| ADR-014 | Evidence-Governed Enterprise Intelligence Reasoning Runtime | `architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md` | Accepted | Accepted ADR governing evidence-governed Enterprise Intelligence reasoning runtime boundaries; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | EI-001; EI-012; FP-009 | Research outputs must preserve evidence-governed reasoning boundaries |
| ADR-016 | Knowledge Packs as the Standard Exchange Mechanism | `architecture/decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md` | Accepted | Accepted ADR governing Knowledge Packs as exchange rather than canonical acceptance; documentation-only and non-runtime | architecture-authority; researcher-pack; assurance-pack | FP-010; FP-011; EI-013 | Researcher-pack use must distinguish exchange from canonical acceptance |


## Researcher-pack and Assurance-pack inclusion rationale

| Document group | Included documents | Why this belongs in the Researcher and Assurance profiles |
| --- | --- | --- |
| Governance controls | AP-001; AP-002; RP-001; RP-002 | Preserves registry-backed compilation, metadata compatibility, non-promotion rules and the Researcher and Assurance role boundaries. |
| Design Doctrine | DD-001 | Gives Researchers and Assurance reviewers the accepted CIOS reasoning style: evidence-first, observation-led and model-centred rather than report-led. |
| Reference Architecture | RA-001 | Provides the accepted navigation entry point and authority chain needed to locate owning papers without inferring authority from folders or prose. |
| Enterprise Model Specification | EI-001 | Defines the durable Enterprise Model / Commercial Digital Twin memory boundary that Enterprise Blueprint Research populates and must not bypass. |
| Enterprise Observation Model | EI-012 | Defines Observations as atomic, evidence-backed intelligence units and protects evidence lineage during research. |
| Enterprise Knowledge Graph | EI-002 | Defines the relationship model needed to connect enterprises, actors, pressures, evidence, hypotheses and recommendations. |
| Enterprise Behaviour Model | EI-003 | Provides the accepted behavioural interpretation layer needed to turn evidence into bounded Enterprise Blueprint research findings. |
| Hypothesis Validation Standard | FP-009 | Defines hypothesis lifecycle, strengthening, weakening, rejection and retirement so research remains testable. |
| Relevant accepted ADRs | ADR-001; ADR-002; ADR-003; ADR-004; ADR-005; ADR-009; ADR-010; ADR-011; ADR-012; ADR-013; ADR-014; ADR-016 | Captures accepted decisions directly governing observations, durable memory, CIRM/EI separation, human knowledge labelling, lineage, assurance, acquisition, financial intelligence, blueprint import, canvas navigation, evidence-governed reasoning and knowledge-pack exchange. |
| Glossary | GL-001 | Provides canonical vocabulary so compiled Researcher and Assurance output uses CIOS terms consistently. |

## Review-material registry entries

| ID | Title | Path | Status | Authority classification | Release-profile membership | Dependencies | Validation trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EU-001 | Enterprise Understanding Contract | `architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md` | Review | Proposed operational contract / review material; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack` | Reference Architecture; EI-001; EI-002; EI-003; EI-012; FP-009; ADR-009; Commercial Digital Twin Blueprint Contract | MOD and one materially different enterprise |
| OT-001 | Opportunity Twin Specification | `architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md` | Review | Proposed method / proposed operational contract; documentation-only; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack` | EI-006; EI-012; FP-009; OPI-001; RTP-001 | Wider validation across materially different enterprises and opportunity types |
| OPI-001 | Opportunity Positioning Intelligence | `architecture/reference-architecture/standards/OPI-001-Opportunity-Positioning-Intelligence.md` | Review | Proposed method / proposed operational contract; documentation-only; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack` | OT-001; RTP-001; EI-006; FP-009 | Wider validation across materially different enterprises and positioning use cases |
| RTP-001 | Research-to-Positioning Input Contract | `architecture/enterprise-intelligence/contracts/RTP-001-Research-to-Positioning-Input-Contract.md` | Review | Proposed method / proposed operational contract; documentation-only; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack` | OT-001; OPI-001; EI-006; EI-012; FP-009 | Wider validation across materially different research-to-positioning handovers |
| ADR-023 | Enterprise Understanding as the Primary Governed Asset | `architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md` | Proposed | Proposed ADR; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack` | Reference Architecture; EI-001; EI-002; EI-003; EI-012; FP-009; ADR-009; Commercial Digital Twin Blueprint Contract; EU-001 | MOD and one materially different enterprise |

## Production profile note

EU-001, OT-001, OPI-001, RTP-001 and ADR-023 remain excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack`; they are also excluded from `assurance-pack`.

EU-001, OT-001, OPI-001, RTP-001 and ADR-023 are intentionally absent from the current `FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json` export profile. They must not be added to production Researcher, Assurance or Reviewer packs until a separate accepted architecture decision approves that change. The approved Researcher-pack membership is limited to accepted registry rows with explicit `researcher-pack` membership. As of 2026-07-12, this includes AP-001, AP-002, RP-001, accepted Researcher architecture foundations, relevant accepted ADRs and the Glossary listed above.
