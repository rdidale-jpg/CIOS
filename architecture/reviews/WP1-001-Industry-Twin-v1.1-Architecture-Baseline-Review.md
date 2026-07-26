# WP1-001 — Industry Twin v1.1 Architecture Baseline Review and Canonical Gap Analysis

**Mission:** WP1-001  
**Status:** Assessment complete — no architecture acceptance decision  
**Review date:** 2026-07-26  
**Scope:** Repository architecture, specifications, programme state, packages, runtime and tests  
**Change boundary:** Assessment only; no runtime, schema, profile, accepted ADR or canonical architecture behaviour is changed by this report.

## 1. Executive decision

The repository does **not** yet contain an accepted, end-to-end Industry Twin v1.1 release contract. It does contain much of the required doctrine, but under several owners and at materially different authority levels:

* accepted ADRs establish atomic Observations, durable Enterprise Models, inspectable recommendation lineage, progressive assurance, governed import and Knowledge Packs as non-canonical exchange;
* accepted Enterprise Intelligence authorities own the Enterprise Model, graph, behaviour, commercial reasoning and Observation semantics;
* `IT-001` exists, contrary to some older guidance which describes it as absent, but it is explicitly **Review / Proposed** and documentation-only;
* the Industry Twin Lifecycle and Knowledge Pack specifications are **Draft Normative**, not accepted architecture;
* the `twin-release-manifest` schema is a useful derived contract but is not a substitute for an accepted Industry Twin owner;
* Flora has a strong, tested governed blueprint-import lifecycle and a broad banking demonstration, but it does not prove a general Industry Twin v1.1 build, autonomous research-completion or release lifecycle;
* current programme state is focused on the Chief Architect pack and evidence-bounded enterprise/commercial twins, not delivery of Industry Twin v1.1.

The smallest governed route is therefore to **extend and reconcile existing owners**, first through an acceptance-ready amendment to `IT-001` coordinated with the existing Draft Knowledge Pack and lifecycle owners. No ITS-001–ITS-010 family is justified. Derived schema, package, Researcher and Flora changes must wait for the canonical decision.

### Assessment rules

This review applies the requested evidence order: accepted ADR/reference architecture; Founding Papers and Enterprise Intelligence authorities; normative specifications at their declared status; code and tests; `CURRENT-PROGRAMME-STATE`; roadmaps; then examples/generated artefacts. “Architectural intent”, “runtime” and “programme state” columns below are deliberately independent. A document does not prove runtime, a test fixture does not establish doctrine, and a package does not become memory merely by being valid.

Runtime labels use the definitions in `docs/flora-runtime/wp-011/Flora-Runtime-Capability-Baseline.md`: **Operational**, **Implemented**, **Partially Implemented**, **Prototype**, **Stub**, **Planned**, and **Unknown**. “Operational” is used only where an integrated route is evidenced; it does not imply production scale or generality.

## 2. Evidence baseline and repository areas inspected

The review inspected:

* `architecture/reference-architecture/`, its Document Map and Authority Registry;
* accepted and status-conflicted ADRs, particularly ADR-001, ADR-002, ADR-005, ADR-009, ADR-010, ADR-012, ADR-014, ADR-016 and ADR-024;
* FP-004, FP-006, FP-009, FP-010, FP-011 and FP-012;
* EI-001, EI-002, EI-003, EI-004, EI-006, EI-012, EI-013 and EIF-001;
* `IT-001`, Industry Twin Lifecycle v1.0, OT-001, Market Participant and Twin Presentation specifications, Knowledge Pack Specification v1.0, FEIR-001, EIRP-001 and the Enterprise Knowledge Production Protocol;
* the Chief Architect pack manifest, source map and current programme state, plus the Researcher pack guidance, readiness gate and workspace protocol;
* banking Industry/Enterprise assets, candidate UK Government handover material, manifests, package fixtures and schemas;
* Flora blueprint import, registry, archive, validation, review, restage, promotion, projection and maturity code; banking, enterprise-intelligence, financial-intelligence and presentation routes;
* package builders/validators and relevant unit/integration tests;
* the existing Industry Twin documentation audit, inventory, lifecycle map, gap analysis and banking closure evidence.

## 3. Architecture Gap Matrix

Abbreviations: **A** accepted; **R** Review; **DN** Draft Normative; **PF** Proposed Foundation; **PS** programme-state evidence. Priorities are P0 (baseline-blocking), P1 (next), P2 (later).

| # | Target capability | Existing canonical owner and authority/status | Existing architectural intent | Implemented runtime capability | Programme-state relevance | Gap | Action | Recommended canonical change | Derived impact (only after acceptance) | Priority | Evidence paths | Uncertainty / contradiction |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Canonical Industry Twin release contract | IT-001 (R/Proposed); ADR-016 (A); Knowledge Pack Spec (DN); Lifecycle Spec (DN) | IT-001 defines the durable industry object; pack/lifecycle owners define exchange and cadence. | **Partially Implemented:** generic blueprint packages can be imported; no v1.1 Industry release contract is enforced. | PS names enterprise/commercial twin focus, not Industry v1.1. | No accepted composition of object, release and lifecycle obligations. | **Extend** | Amend IT-001 to normatively reference the existing pack and lifecycle owners and define the minimum release boundary; seek acceptance through existing governance. | Later align manifest/profile, validator and compatibility tests. | P0 | `architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md` §§1,6,8; `architecture/decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md` Decision; `architecture/specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md` §§4–8 | IT-001 exists but is Review and excluded from production profiles; lifecycle and pack specs are drafts. |
| 2 | Consistent, self-describing package structure | Knowledge Pack Spec (DN), FP-010 (PF), ADR-016 (A) | Manifest-driven logical structure; physical layout intentionally not mandated. | **Implemented** for specific Chief Architect/Researcher builders and blueprint packages, not one Industry layout. | WP-012 is hardening one pack, not defining all Industry packs. | Target asks consistency while owner explicitly permits logical/physical flexibility. | **Clarify** | In Knowledge Pack Spec, define an Industry Twin release profile using the existing logical model, without changing base pack architecture. | Profile/builder/fixture validation later; no base schema redesign. | P0 | `architecture/specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md` §§4–5; `tools/knowledge-packs/build_researcher_pack.py`; `tests/knowledge_packs/test_researcher_pack.py` | Banking uses `MANIFEST.yaml`; release schema uses a different richer contract. Physical-layout mandate would contradict technology-neutral intent. |
| 3 | Immutable and versioned releases | Knowledge Pack Spec (DN), ADR-016 (A) | Explicit immutable, reproducible and versioned principles; checksum/signature where available. | **Implemented** in deterministic pack builds/checksums and preserved import archive; not universally enforced for Industry releases. | Chief Architect pack work explicitly checks manifest checksums. | Doctrine exists; Industry binding and enforcement proof are absent. | **Preserve** | Preserve base semantics; reference them from the IT-001 release contract and define release replacement/supersession acceptance. | Industry builder/validator checksum and mutation-regression tests. | P0 | `architecture/specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md` §2; `cios/applications/flora/blueprint_import/archive.py`; `tests/knowledge_packs/test_chief_architect_pack.py` | Runtime preservation is file-backed/pilot scope, not proof of enterprise-grade immutability. |
| 4 | Backward compatibility with `industry-twin-v1` | No accepted explicit owner; closest are IT-001 (R), Knowledge Pack Spec (DN), banking package precedent | Versioning and supersession exist generally. | **Unknown:** no repository-wide compatibility contract or v1→v1.1 conformance suite found. | PS is silent. | “industry-twin-v1” is not evidenced as one authoritative machine contract; existing packages vary. | **Clarify** | IT-001 amendment must inventory and name protected v1 surfaces (identifiers, required paths/fields and import behaviour), with additive-only v1.1 rules or an explicit adapter. | Golden v1 fixtures, compatibility validator tests and migration report; do not normalize fixtures. | P0 | `enterprise-knowledge/banking/MANIFEST.yaml`; `tests/fixtures/industry_twin_packages/README.md`; `architecture/specifications/knowledge-packs/twin-release-manifest.schema.json` | Baseline label is ambiguous; compatibility cannot be honestly claimed until the protected surface is agreed. |
| 5 | Explicit governed-object inventory | EI-001/EI-002/EI-012 (A); IT-001 (R); manifest owner (DN) | IT-001 lists required industry objects; Knowledge Packs enumerate assets and lineage. | **Partially Implemented:** import review counts object classes and projections; packages do not share a complete inventory vocabulary. | PS prioritises pack source-map resolution, not Industry inventory. | No accepted Industry object inventory with per-object status/version/owner. | **Extend** | Add a release inventory obligation to IT-001, reusing EI object identities and Knowledge Pack asset metadata. | Manifest entries and validators later; preserve source IDs. | P0 | IT-001 §4; Knowledge Pack Spec §§5,7; `cios/applications/flora/blueprint_import/review_plan.py` | “Governed object” versus “included asset” needs reconciliation, not silent equivalence. |
| 6 | Tiered Enterprise dossier depth | EI-001 (A), EIF-001 (accepted/reference standard), IT-001 (R) | Enterprise Model/foundation semantics exist; Industry Twin has Enterprise Population. | **Partially Implemented:** banking Enterprise Twins exist at uneven depth; factual twin and canvas support bounded slices. | Banking lessons explicitly identify unequal enterprise depth. | No accepted dossier tiers or minimum evidence per tier. | **Extend** | Define tier purpose and minimum dimensions in EI-001/EIF-001; IT-001 should reference, not redefine, Enterprise depth. | Research templates/readiness calculations and fixtures later. | P0 | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md`; `architecture/reference-architecture/standards/EIF-001-Enterprise-Intelligence-Foundation-Model.md`; `docs/product/UK-Banking-Industry-Twin-v1-Closure.md` | “Dossier” is target terminology without an accepted repository definition. |
| 7 | Financial Intelligence requirements | EI-011/ADR-011 and financial runtime specification (status must be retained); EI-001 for Enterprise state | Financial evidence is candidate, governed and source-bounded. | **Partially Implemented / Operational for configured BT slices:** acquisition, extraction, RAPID and diagnostics exist, provider dependent. | PS does not declare Industry-level financial completion. | No Industry release minimum, temporal depth or enterprise-tier mapping. | **Extend** | Add minimum Financial Intelligence dimensions to the Enterprise depth owner; reference them from IT-001 release readiness. | Research collection, package declarations and tests after authority reconciliation. | P0 | `docs/Architecture/Flora_Financial_Intelligence_Runtime_Specification_v0.1.md`; `cios/applications/flora/financial_intelligence/`; WP-011 capability catalogue | Runtime breadth must not promote the v0.1 runtime spec into accepted canonical authority. |
| 8 | Annual-report and primary-evidence analysis | ADR-010 (A); FP-004/FP-006 (Draft); EI-012 (A) | Structured-source-first acquisition, provenance and Observation creation are established. | **Partially Implemented:** PDF/page parsing and official-source acquisition exist for configured financial paths; not general dossier coverage. | Existing audit flags source completeness and practical guidance gaps. | No release threshold for report periods, primary-source coverage or analysis deficiency. | **Extend** | Extend existing Researcher operating/readiness guidance, bounded by ADR-010/EI-012; IT-001 should require declared coverage, not acquisition mechanics. | Coverage manifest/checks, researcher prompts and fixtures later. | P0 | `architecture/decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md`; `cios/applications/flora/financial_intelligence/document_review.py`; `docs/governance/Industry-Twin-Documentation-Audit.md` | FP-004/FP-006 remain draft; absence of a source is a deficiency, not licence to infer. |
| 9 | Governed Evidence objects | FP-004 (Draft), EI-012 (A for Observations), EI-002 (A graph), ADR-010 (A) | Evidence precedes Observations and retains authority, provenance, confidence and freshness. | **Implemented** in several runtime models/import paths; semantics differ across modules. | PS claims bounded evidence assembly and validation. | Evidence’s single canonical object owner is ambiguous; EI-012 primarily owns Observation. | **Clarify** | Reconcile Evidence ownership in the Authority Registry/Document Map, preserving FP-004 draft status; IT-001 references the resolved owner. | Converge DTO mappings later, not in this mission. | P0 | `architecture/founding-papers/FP-004-Evidence-Acquisition-Standard.md`; EI-012; `cios/applications/flora/blueprint_import/models.py`; `cios/applications/flora/memory/models.py` | Multiple Evidence representations exist; no inference that one is universally canonical. |
| 10 | Structured reasoning lineage: Evidence → Observation → Strategic Signal → Hypothesis → Commercial Thesis → Recommendation | EI-004 (A per programme baseline), EI-012 (A), FP-009 (accepted in registry but file says Draft), ADR-005 (A), EIRP-001 | Inspectable lineage and bounded reasoning are explicit, but terminology includes Signal/Insight/Theme/Thesis variants. | **Partially Implemented / Operational in bounded enterprise reasoning:** briefs validate cited evidence; observatory builds signals/theses; not one persisted general chain. | PS evidences enterprise brief pipeline and says opportunity/observatory remain separate from final authority. | Chain vocabulary and cross-module identifiers are not one accepted contract. | **Clarify** | EI-004 should reconcile canonical stages and mappings; FP-009 retains hypothesis lifecycle; IT-001 only declares required lineage endpoints. | Commercial-reasoning schema and runtime mappings/tests only after canonical clarification. | P0 | `architecture/enterprise-intelligence/volume-2-commercial-intelligence/EI-004-Commercial-Reasoning-Framework.md`; FP-009 “Inspectable Reasoning Lineage”; `enterprise-knowledge/schemas/commercial-reasoning.schema.json`; `cios/applications/flora/enterprise_intelligence/` | FP-009 file status Draft conflicts with registry/programme description; requested chain omits existing “Insight/Theme” stages. |
| 11 | Explicit Unknowns and Contradictions | EI-012 (A), ADR-014 status-conflicted, FP-010/ADR-016 | First-class, never silently resolved; pack and reasoning validation must retain them. | **Implemented** across import, memory, reasoning and presentation paths. | PS explicitly requires them in evidence-limited briefs. | General principle is strong; release inventory/coverage declaration is not uniformly enforced. | **Preserve** | Reference EI-012 semantics unchanged in IT-001 release readiness and Knowledge Pack profile. | Add omission/round-trip tests later. | P0 | EI-012; ADR-016 Decision/Consequences; `cios/applications/flora/blueprint_import/review_plan.py`; `tests/test_flora_blueprint_import_validation.py` | Presence does not prove quality or closure; unresolved items must remain release-visible. |
| 12 | Opportunity Twin completeness | EI-006 owner; OT-001 (R) explicitly subordinate | Opportunity contents include evidence, uncertainty, positioning and recommendation lineage. | **Partially Implemented:** deterministic banking opportunity pipeline and maturity assessment; no general Opportunity Twin runtime. | WP-011 says banking-focused, not general. | OT-001 remains Review; no accepted completeness gate. | **Extend** | Extend EI-006 and progress OT-001 through review; IT-001 references Opportunity release links without owning their shape. | Opportunity package/profile/maturity tests later. | P1 | `architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md` Authority boundary; `cios/applications/flora/enterprise_intelligence/opportunity_pipeline.py`; `cios/applications/flora/blueprint_import/maturity.py` | Read-time maturity is not canonical acceptance or persisted lifecycle state. |
| 13 | Graph integrity and identifier lineage | EI-002 (A), ADR-005 (A), Knowledge Pack Spec (DN) | Stable entities/relationships and resolvable lineage are required. | **Partially Implemented:** import review reports supplied/derived IDs, collisions and failures; bounded projection lineage exists. | PS claims inspectable brief lineage, not whole-Industry graph integrity. | No v1.1 graph closure, dangling-edge and namespace acceptance criteria. | **Extend** | EI-002 defines release graph integrity; IT-001 references it; pack validation reports deficiencies without fabricating links. | Validator graph checks and golden tests. | P0 | EI-002; Knowledge Pack Spec §8; `cios/applications/flora/blueprint_import/review_plan.py`; `tests/test_mod_twin_spine_mapping.py` | Derived identifiers can exist at import; policy for preserving v1 lineage needs explicit decision. |
| 14 | Flora-addressable presentation and drill-down | Twin Presentation Model Spec (DN), FEIR-001, ADR-016 | Optional presentation payloads preserve evidence and are non-canonical. | **Operational for bounded banking/Lloyds/canvas routes; Partially Implemented generally.** | Flora is current product focus. | No general Industry v1.1 presentation/drill-down conformance. | **Extend** | Extend existing Twin Presentation Model profile for Industry navigation only after IT contract; do not put view semantics in IT-001. | Flora route/projection/accessibility tests later. | P1 | `architecture/specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md`; `cios/applications/flora/banking_portfolio.py`; `cios/applications/flora/runtime/increment1_views.py` | TPM-001 does not exist by that identifier; the titled Draft specification does. |
| 15 | Explicit Flora import payload or collection mapping | ADR-012 (A), Flora blueprint import runtime spec v0.1, Knowledge Pack Spec (DN) | Import is a governed boundary; package validity is not canonical acceptance. | **Operational** blueprint archive→validate→stage→review→restage→plan→promote workflow. | WP-011 identifies this as strong implementation. | Industry v1.1 payload/collection mapping is not declared; generic import does not prove it. | **Extend** | Define an Industry mapping appendix/profile under the existing import contract after canonical v1.1 fields stabilize. | Adapter, mapping deficiency report and end-to-end v1 fixture tests. | P0 | ADR-012; `cios/applications/flora/blueprint_import/package_contracts.py`, `industry_delta_adapter.py`, `promotion.py`; `tests/test_flora_governed_import_workflow.py` | “Promotion” in current runtime concerns mapped canonical outputs; it must not imply pack contents are canonical en masse. |
| 16 | Independent validation and deficiency reporting | Knowledge Pack Spec (DN), ADR-009 (A), owner review boundary in import | Validation requirements include links, lineage, duplicates, scope and canonical boundary. | **Implemented / Operational for supported package types:** deterministic validation and review reports exist; independence is procedural, not assured by separate actor. | WP-012 validation hardening is active. | No Industry v1.1 deficiency taxonomy, validator independence rule or conformance suite. | **Extend** | Knowledge Pack Industry profile defines deterministic deficiencies and reviewer separation proportional to assurance tier. | Validator result schema and negative fixtures later. | P0 | Knowledge Pack Spec §8; `cios/applications/flora/blueprint_import/validator.py`, `review.py`; `tests/test_flora_blueprint_import_validation.py` | Automated validation is not necessarily “independent”; human/organisational independence is unevidenced. |
| 17 | Multi-dimensional completeness assessment | ADR-009 (A); EIF-001; existing readiness guidance | Progressive assurance and decision-relative completeness are intended. | **Partially Implemented:** `assess_maturity` separates package, twin and decision completeness with dimensions/caps/penalties at read time. | Existing governance audit says accepted Industry minimum is absent. | Runtime heuristic lacks accepted owner, persisted history and calibrated thresholds. | **Extend** | Establish dimensions and gate semantics in ADR-009’s existing assurance framework/EIF-001; IT-001 references Industry thresholds. | Calibrated profiles, history and regression tests later. | P0 | `cios/applications/flora/blueprint_import/maturity.py`; `tests/test_flora_governed_twin_increment.py`; `docs/governance/Industry-Twin-Documentation-Audit.md` | Do not reverse-promote current weights into architecture. |
| 18 | Autonomous research completion and evidence-exhaustion behaviour | ADR-009 broad; Enterprise Knowledge Production Protocol (DN); Researcher RG-001/readiness guidance | Research is candidate work with readiness/handover controls. | **Planned / Unknown:** no general autonomous loop proving evidence exhaustion, stop rationale and safe escalation found. | PS does not claim it. | No accepted evidence-exhaustion definition, bounded autonomy policy or executable proof. | **Extend** | Extend the existing production protocol and Researcher operating guidance with bounded stop conditions, source-family exhaustion, unresolved deficiency and human escalation; IT-001 consumes the readiness result. | Researcher workflow/checkpoint tests later; no Flora implementation in this review. | P1 | `architecture/specifications/enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md`; `knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md`; `Industry-Twin-Readiness-Gate.md` | “Autonomous” authority and acceptable exhaustion are not established; missing evidence cannot be inferred away. |
| 19 | Separation of research checkpoints from release artefacts | Enterprise Knowledge Production Protocol (DN), Knowledge Pack Spec (DN), RG-002 | Research is candidate; packs are reproducible releases, not memory. | **Partially Implemented:** mission workspaces and release builders are distinct, but conventions vary. | PS distinguishes roadmap/pack acceptance from current state. | No explicit Industry checkpoint→candidate→accepted asset→release transition contract. | **Clarify** | Clarify transition and prohibited checkpoint content in the production protocol and Industry release profile. | Builder exclusions, workspace lint and leakage tests later. | P1 | Knowledge Pack Spec §1.1; `knowledge-packs/researcher/operating-guidance/RG-002-Research-Mission-Workspace-Standard.md`; `knowledge-packs/researcher/missions/` | Existing mission material inside a pack may blur working/release boundaries. |
| 20 | Promotion readiness and release lifecycle governance | ADR-012/ADR-016 (A), ADR-009 (A), Lifecycle Spec (DN) | Validation, acceptance, promotion and refresh are separated conceptually. | **Operational** for blueprint import lifecycle; **Planned/Partial** for general Industry refresh/release lifecycle. | PS focuses pack readiness; Industry lifecycle is not active programme objective. | No accepted state machine joining research readiness, release, import review, promotion, supersession and retirement. | **Extend** | Extend the existing Industry Lifecycle Spec and bind it through IT-001; preserve canonical-acceptance boundary and explicit owner decisions. | State-transition metadata, Flora adapter and lifecycle tests later. | P0 | Industry Lifecycle Spec §§Purpose/Lifecycle; ADR-012; `cios/applications/flora/blueprint_import/lifecycle.py`, `promotion.py`; `tests/test_flora_blueprint_import_promotion.py` | Current promotion workflow cannot be assumed to satisfy an unaccepted Industry lifecycle. |

## 4. Canonical Ownership Map

“Owner” below means the best repository-evidenced architecture owner, not the document author. Ambiguity is intentionally retained.

| Concern | Current owner / authority | Ownership decision for v1.1 | Ambiguity to preserve |
|---|---|---|---|
| Industry Twin | `IT-001` is the only direct object owner, but is Review/Proposed and documentation-only; Draft Lifecycle Spec owns cadence | Progress IT-001 rather than create another specification | No accepted canonical Industry object owner yet |
| Enterprise Twin / Enterprise dossier | EI-001 (Accepted) owns durable Enterprise Model; ADR-002 establishes durable memory; EIF-001 owns foundation completeness | Extend EI-001/EIF-001 for dossier tiers; Industry references it | “Enterprise Twin”, “Commercial Digital Twin” and “dossier” are not proven fully synonymous |
| Market Participant | Draft Market Participant Twin Specification under ADR-016/FP-010/FP-011/EI-013/EI-002 | Preserve draft owner and mature it separately | No accepted runtime/canonical owner; participant may also be an EI-002 entity |
| Opportunity Twin | EI-006 is owner; OT-001 Review is explicitly subordinate | Extend EI-006/OT-001; IT-001 links only | No accepted completeness contract |
| Evidence | FP-004 is closest conceptual standard (Draft); ADR-010 controls acquisition; EI-012 owns Observation, not clearly all Evidence | Reconcile in Authority Registry before deriving a release object | Multiple runtime Evidence DTOs and no single accepted object owner |
| Observation | EI-012 (Accepted) and ADR-001 (Accepted) | Preserve | None material |
| Commercial reasoning | EI-004 (accepted baseline), FP-009 for hypotheses, ADR-005 for recommendation lineage; EIRP-001 for pipeline | Clarify stage vocabulary in EI-004; preserve specialist owners | FP-009 metadata says Draft while registry/programme baseline treats it as accepted |
| Financial Intelligence | EI-011/ADR-011 are referenced owners; v0.1 runtime specification and implementation provide lower-authority evidence | Confirm authority status, then extend Enterprise-depth requirements | Status/authority must not be inferred from working runtime specification |
| Knowledge Pack release | ADR-016 (Accepted) → FP-010 (Proposed Foundation)/FP-011 → Knowledge Pack Spec (Draft Normative), EI-013 semantics | Preserve chain; extend an Industry profile only | Accepted ADR names subordinate documents whose own statuses are not accepted |
| Package validation | Knowledge Pack Spec §8 (Draft Normative); runtime blueprint validator implements supported contracts | Extend existing validation owner/profile | Architectural validation versus Flora implementation responsibility is split |
| Flora import and promotion | ADR-012 (Accepted) governs boundary; Flora import runtime specification/implementation operationalise it | Extend mapping only after v1.1 contract | Runtime “promotion” scope is narrower than wholesale pack acceptance |
| Presentation and drill-down | Twin Presentation Model Specification (Draft Normative) and FEIR-001 presentation layer | Extend existing presentation owner | No `TPM-001` identifier exists; do not invent it |
| Autonomous knowledge production | Enterprise Knowledge Production Protocol (Draft Normative) plus Researcher RG-001/RG-002 operating guidance | Extend those existing owners with bounded exhaustion/stop semantics | No accepted sovereign autonomous-agent owner or operational proof |
| Quality gates and completion assessment | ADR-009 (Accepted) progressive assurance; EIF-001 foundation; Researcher readiness guidance; package validation | Compose decision-relative gates under existing owners | Runtime maturity weights are implementation evidence, not canonical thresholds |

## 5. Runtime Capability Assessment

| Capability | Status | What repository evidence proves | What it does not prove |
|---|---|---|---|
| Flora web runtime and product routes | **Operational** | Registered health, banking, object, import, canvas and intelligence routes in `cios/applications/flora/web/app.py`, as catalogued by WP-011 | Production-scale hosting, general Industry v1.1 conformance |
| Banking Industry/Enterprise experience | **Operational** for supported banking journey | Banking portfolio, enterprise, comparison, evidence, opportunity and financial views are routed and tested | Uniform Enterprise dossier depth or a portable v1.1 release |
| Governed blueprint import | **Operational** | Archive, validate, stage, review, restage, dry-run plan and promotion modules plus lifecycle tests | That every Industry package shape is supported or contents become canonical automatically |
| Package builders (Chief Architect/Researcher) | **Implemented** | Deterministic builds, manifests, checksums and tests | A generic Industry Twin release builder |
| Knowledge Pack base validation | **Implemented** for pack-specific builders; **Partially Implemented** generally | Manifest/source-map/checksum tests and blueprint validation | Full Draft Knowledge Pack Spec conformance across all pack types |
| Industry Twin object runtime | **Partially Implemented** | Import projections and banking knowledge support industry entities, pressures, enterprises, participants and opportunities | Accepted IT-001 semantics or general lifecycle persistence |
| Enterprise Model memory | **Implemented** | Stable Observation/model/unknown structures and repositories | Complete dossiers for all enterprises |
| Evidence and Observation handling | **Implemented** | Models, import mappings, live collection and bounded evidence packages exist | One universally reconciled Evidence object model |
| Enterprise Intelligence reasoning | **Operational with deterministic fallback** | Retrieval, evidence package, provider abstraction, validation/audit and safe fallback | Autonomous open-world research or canonical memory writes |
| Full requested reasoning lineage | **Partially Implemented** | Enterprise reasoning and observatory each implement substantial stages | One interoperable Evidence→Recommendation chain with stable IDs across modules |
| Financial Intelligence | **Partially Implemented / Operational for configured BT paths** | Official-source acquisition, page parsing, candidate extraction, provider adapters, validation and tests | Generic annual-report coverage for every Industry participant or provider independence |
| Opportunity pipeline | **Partially Implemented / Operational for banking demo** | Deterministic opportunities, horizons and web routes | General OT-001 runtime or accepted completion criteria |
| Market Participant Twin | **Planned** | Draft specifications and templates exist | Clear Flora runtime module or accepted owner |
| Graph/ID integrity reporting | **Implemented** in import review | Supplied/derived ID counts, collisions/failures, class inventory and relationship mapping are reported | Whole-release graph closure against an accepted v1.1 namespace policy |
| Multi-dimensional maturity | **Implemented** as deterministic read-time assessment; **Partially Implemented** as governance | Dimensions, caps, penalties, gaps and next evidence are tested | Canonical thresholds, calibration, historical persistence or release approval |
| Presentation/drill-down | **Operational** for bounded banking, Lloyds and canvas experiences | Routed projections expose lineage, evidence, unknowns and contradictions | A generic self-describing Industry presentation payload |
| Autonomous research completion/evidence exhaustion | **Planned / Unknown** | Guidance and readiness artefacts describe research and handover | Executable autonomous loop, accepted exhaustion rule or test proof |
| Research checkpoint/release separation | **Partially Implemented** | Workspace protocol and release builders are conceptually distinct | Consistent enforcement across existing mission/package trees |
| Industry release promotion lifecycle | **Partially Implemented** | Blueprint lifecycle supports governed review/promotion; Draft Industry lifecycle describes refresh | Joined accepted research→release→import→promotion→supersession lifecycle |

## 6. Proposed v1.1 Change Plan

These are proposed follow-on changes, not changes made by WP1-001. Each increment is independently reviewable and stops before derived implementation where its authority dependency is unresolved.

### C1 — Reconcile the authority and compatibility baseline (P0)

* **Canonical owner:** Architecture Authority Registry/Document Map, with IT-001 as candidate Industry owner.
* **Intent/exact scope:** Record the actual statuses of IT-001, FP-009, ADR-014, ADR-024, FP-010, the Lifecycle Spec and Knowledge Pack Spec; define what repository artefacts constitute protected `industry-twin-v1` inputs. No renames and no status promotion by implication.
* **Reason:** A v1.1 contract cannot be reviewed against an ambiguous v1 or internally contradictory authority metadata.
* **Compatibility:** Documentation-only inventory; preserves every existing package.
* **Flora / Researcher / package / tests:** No behaviour change; add link/status integrity checks only if separately approved.
* **Commercial outcome:** Prevents teams investing against the wrong doctrine or breaking demonstrable banking assets.
* **Dependencies:** Owner decisions on status conflicts.
* **Acceptance:** One authority table resolves each identifier/path/status; a named list of v1 compatibility fixtures/surfaces exists; unknowns remain explicit.

### C2 — Make IT-001 acceptance-ready as the minimum Industry release contract (P0)

* **Canonical owner:** IT-001, bounded by EI-001/EI-002/EI-012/EI-004, ADR-009, ADR-016 and existing pack/lifecycle owners.
* **Intent/exact scope:** Add release composition, governed-object inventory, required lineage endpoints, declared deficiencies, Enterprise-depth references, opportunity links, lifecycle-state references and compatibility policy. Do not duplicate Evidence, Enterprise, Opportunity, pack or presentation semantics.
* **Reason:** It is the only suitable direct owner; creating ITS documents would compete with it.
* **Compatibility:** Additive by default; any non-additive issue must use an explicit v1 adapter/deprecation decision.
* **Flora impact:** None until acceptance; later mapping consumes the contract.
* **Researcher impact:** A clear release target, not new acquisition doctrine.
* **Package/schema impact:** None in this increment.
* **Test impact:** Documentation reference/status validation; no runtime test changes.
* **Commercial outcome:** Establishes a reviewable, repeatable Industry intelligence product boundary.
* **Dependencies:** C1.
* **Acceptance:** Every one of the 20 target capabilities is owned or explicitly delegated; no new spec family; authority reviewers approve the composition.

### C3 — Establish decision-relative completeness and Enterprise dossier tiers (P0)

* **Canonical owner:** ADR-009/EIF-001 for assurance; EI-001 for Enterprise depth; IT-001 for Industry release use.
* **Intent/exact scope:** Define tier purposes, mandatory dimensions, primary/annual-report and Financial Intelligence coverage declarations, material-gap rules, and release-blocking versus warning deficiencies. Reuse Unknown/Contradiction semantics.
* **Reason:** Banking evidence shows uneven depth; current runtime maturity weights are not authority.
* **Compatibility:** Existing v1 assets remain valid at a declared legacy/unassessed tier; no normalization.
* **Flora impact:** Future display/assessment only.
* **Researcher impact:** Bounded evidence targets and honest stop/escalation conditions.
* **Package/schema impact:** Future declarations only after acceptance.
* **Test impact:** Canonical examples and calibration cases, then deterministic gate tests.
* **Commercial outcome:** Comparable dossiers and defensible prioritisation without endless research.
* **Dependencies:** C2 and confirmed Financial Intelligence owner.
* **Acceptance:** Tiers are decision-relative, missing evidence scores as missing, and release readiness cannot conceal Unknowns/Contradictions.

### C4 — Clarify canonical commercial-reasoning lineage (P0)

* **Canonical owner:** EI-004; FP-009 owns hypothesis validation; EI-012 Evidence/Observation boundary; ADR-005 recommendation eligibility.
* **Intent/exact scope:** Reconcile Signal, Insight, Theme, Hypothesis and Thesis terms; define stable ID/edge expectations and permitted omissions/aliases.
* **Reason:** Requested v1.1 chain and current CIRM/runtime chains differ.
* **Compatibility:** Map legacy stages; never rewrite or fabricate old lineage.
* **Flora impact:** Future adapter mapping across enterprise reasoning and observatory.
* **Researcher impact:** Unambiguous reasoning artefacts and falsification trail.
* **Package/schema impact:** Future commercial reasoning mapping, not immediate schema modification.
* **Test impact:** Golden complete, partial, contradictory and legacy chains.
* **Commercial outcome:** Recommendations become inspectable and reusable across accounts.
* **Dependencies:** C1 status reconciliation.
* **Acceptance:** Every recommendation resolves to its available governed ancestry; gaps are explicit deficiencies, not inferred links.

### C5 — Extend existing research production/readiness guidance (P1)

* **Canonical owner:** Enterprise Knowledge Production Protocol and RG-001/readiness gate, constrained by ADR-010, EI-012 and ADR-009.
* **Intent/exact scope:** Define source-family coverage, annual-report periods, supplier/contract/procurement fields, checkpoint artefacts, evidence-exhaustion rationale, safe stop/escalation and candidate-to-release handover.
* **Reason:** The prior governance audit already identifies this as the operating gap.
* **Compatibility:** Existing missions remain historical; no silent rewriting.
* **Flora impact:** None.
* **Researcher impact:** Material but bounded operating change; no claim of sovereign autonomy.
* **Package/schema impact:** Checkpoints are explicitly excluded from release unless governed as assets.
* **Test impact:** Pack inclusion/exclusion and readiness scenario tests.
* **Commercial outcome:** Faster, consistent research with visible residual risk.
* **Dependencies:** C2–C3.
* **Acceptance:** A researcher can start, stop, declare exhaustion, escalate and hand over without undocumented context.

### C6 — Define the derived Industry release profile and independent validation report (P1)

* **Canonical owner:** Knowledge Pack Specification and existing Industry Lifecycle Specification, referencing accepted IT-001.
* **Intent/exact scope:** Bind logical structure, manifest inventory, checksums, validation state, supersession, deficiencies and reviewer separation; preserve base pack technology neutrality.
* **Reason:** Self-description and consistent validation belong to existing pack/lifecycle owners.
* **Compatibility:** Validate v1 fixtures unchanged; use additive v1.1 fields or explicit adapter.
* **Flora impact:** Defines input, not implementation.
* **Researcher impact:** Defines release output, not working workspace.
* **Package/schema impact:** This is the first increment allowed to propose derived profile/schema changes.
* **Test impact:** Positive/negative fixtures, checksum, dangling-link, missing-lineage and v1 compatibility tests.
* **Commercial outcome:** Portable, independently reviewable intelligence releases.
* **Dependencies:** C2–C5 accepted.
* **Acceptance:** Two independent validators produce the same deterministic findings; validity never implies canonical promotion.

### C7 — Map the accepted profile into Flora import/presentation (P2)

* **Canonical owner:** ADR-012 import boundary, FEIR-001 and Twin Presentation Model Specification; implementation in existing blueprint-import modules.
* **Intent/exact scope:** Add an Industry collection/payload adapter, graph/ID deficiency reporting, drill-down projection and lifecycle-state handling; no redesign of Flora.
* **Reason:** Reuse the proven import lifecycle only after semantics stabilise.
* **Compatibility:** Golden v1 packages continue through existing route; v1.1 is additive/adapter-backed.
* **Flora impact:** Bounded extension to mapping and views.
* **Researcher impact:** Validation feedback only.
* **Package/schema impact:** Consume, do not redefine, the accepted profile.
* **Test impact:** End-to-end archive→validate→review→promote tests with v1, v1.1, deficient and contradictory fixtures.
* **Commercial outcome:** Industry intelligence becomes safely explorable and actionable in Flora.
* **Dependencies:** C6.
* **Acceptance:** Source IDs and lineage round-trip; unsupported content is quarantined/reported; promotion requires explicit owner approval.

## 7. Governance Findings

### 7.1 Identifier and status conflicts

1. **ADR-014 and ADR-024 each declare Draft in front matter and Accepted in an internal `## Status` section.** The accepted/reference authority order cannot be applied reliably until metadata is reconciled. This report uses their architectural intent but does not silently promote them.
2. **FP-009 says Draft in the file**, while the Industry documentation inventory and current programme baseline treat it as accepted/active authority. Its content is useful, but the authority conflict remains.
3. **FP-010 collision history is recorded by the existing audit.** The current tree contains `FP-010-Knowledge-Pack-Architecture.md`; FP-012 states Enterprise Reinvention Intelligence was renumbered, while older audit text records two FP-010 uses. Historical references may still resolve to the wrong concept.
4. **IT-001 and OT-001 exist but are Review-only.** Discussions or paths do not make them accepted. Conversely, older guidance that says IT-001 is absent is stale.
5. **No `TPM-001` or `EKP-001` document identifier was found.** There is a Draft `Twin Presentation Model Specification v1.0` and an `Enterprise Knowledge Production Protocol v1.0`; neither may be relabelled by inference.

### 7.2 Ownership and supersession

* Industry object semantics, lifecycle and release container are split across IT-001, the Lifecycle Spec and Knowledge Pack chain. This is a legitimate separation, but their statuses do not yet form an accepted release contract.
* Evidence acquisition has an accepted ADR and Draft standards, while Observation has a clear accepted owner. A canonical governed Evidence object owner remains ambiguous.
* Knowledge Pack validation is architecture in a Draft specification and operational behaviour in Flora/build tools. Passing the latter cannot promote the former.
* “Enterprise dossier” tiering and “industry-twin-v1” compatibility have no unambiguous canonical owners/surfaces.
* ADR-016’s `Supersedes` statement refers to an “earlier unmerged architecture update pack” rather than a stable document identifier, weakening auditable supersession.

### 7.3 Broken/stale references and packaged baseline divergence

* The existing Industry audit records a canonical Research Agent Guide referencing absent specifications and concludes a Researcher could not build a high-quality Industry Twin without undocumented context. Newer IT-001/readiness files reduce discoverability gaps but do not erase their Review/Draft status.
* The packaged Chief Architect baseline is internally explicit that packs are bounded evidence, not canonical memory. Its source map and current state may be newer than some architecture metadata; packaging does not resolve those conflicts.
* Current programme state says FP-009 and FP-012 “govern” relevant reasoning, despite their file statuses being Draft and Review respectively. It also calls ADR-014/ADR-024 runtime authorities despite contradictory Draft/Accepted headers.
* The current programme objective is WP-012 pack assurance. Roadmaps and completion reports suggesting broader capability are planning/derived evidence only.

### 7.4 Architecture/runtime divergence

* Flora’s blueprint import is more mature than the Draft Industry release architecture it would need to consume.
* Runtime `assess_maturity` provides multi-dimensional scores but no accepted document owns its exact dimensions, weights or thresholds.
* Banking offers the strongest Industry demonstration, but it contains hard-coded/domain-specific precedent and uneven Enterprise research depth; it is not a domain-neutral canonical contract.
* Financial Intelligence is substantially implemented for configured slices, but generic Industry release requirements and authority are incomplete.
* Market Participant semantics are documented in Draft form with no clear general runtime.
* Autonomous evidence-exhaustion is not evidenced in code/tests; readiness prose must not be described as implementation.

### 7.5 Missing evidence

No reliable repository evidence was found for:

* a single accepted `industry-twin-v1` machine contract or enumerated compatibility surface;
* accepted Industry dossier tiers and completeness thresholds;
* an accepted full reasoning-stage vocabulary matching the requested chain;
* organisationally independent Industry release validation;
* a general autonomous research loop with evidenced exhaustion and safe stop behaviour;
* a joined, accepted research-checkpoint→release→Flora-promotion lifecycle;
* production-scale immutability, signatures, storage durability or IAM for Industry releases;
* a generalized Market Participant Twin runtime.

These are reported as Unknown/Planned gaps, not resolved by inference.

## 8. Recommended next Codex mission

> **Mission: Reconcile the Industry Twin authority and v1 compatibility baseline (documentation-only).** Inspect the Architecture Authority Registry, Document Map, IT-001, ADR-016, FP-009/FP-010, Knowledge Pack and Industry Lifecycle specifications, banking `MANIFEST.yaml`, release-manifest schema and all `industry_twin_packages` fixtures. Produce a single amendment to the existing authority registry or established governance report (no new specification) that records each owner’s exact repository status, identifies the protected `industry-twin-v1` compatibility surfaces and fixtures, lists unresolved owner decisions, and supplies acceptance criteria for an IT-001 amendment. Do not alter accepted ADRs, runtime, schemas, profiles, packages or programme state; do not create ITS-001–ITS-010. Run link/status checks and the existing test suite.

This is the smallest highest-value increment because every semantic, package and Flora change otherwise risks binding to an unagreed baseline.

## 9. Acceptance conclusion

All 20 target capabilities have been assessed with owner, authority, architectural intent, runtime evidence, programme-state relevance, gap, action, change impact, priority and uncertainty. The plan extends existing owners before derived artefacts, preserves backward-compatibility ambiguity until evidenced, and keeps Unknowns and Contradictions explicit. WP1-001 changes documentation only and makes no claim that the proposed v1.1 baseline is accepted or implemented.
