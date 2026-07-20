# Industry Twin Documentation Audit

**Status:** Audit complete  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-20  
**Document type:** Governance audit  
**Conclusion:** Requires targeted documentation remediation

## Executive decision

A Researcher **cannot yet build, validate and hand over a high-quality Industry Twin using only the current repository documentation without relying on undocumented context**. The repository contains strong architectural doctrine and several accepted controls, but Industry Twin operating guidance is split between accepted researcher-pack authorities, Review/Draft Industry Twin specifications, a canonical Research Agent Guide that references absent specifications, and Banking v1 closure artefacts.

## Authority hierarchy used

1. Accepted ADRs.
2. Owning architecture papers and Founding Papers.
3. Enterprise Intelligence papers.
4. CIOS Reference Architecture.
5. CIOS Chief Architect Handbook.
6. CIOS-AI guidance.
7. Design Doctrine and Architecture Principles.
8. Operational handbooks and knowledge packs.
9. Implementation and product documentation.

## Documents inspected

The audit inspected the files enumerated in [Industry Twin Documentation Inventory](Industry-Twin-Documentation-Inventory.md), including accepted ADRs, FP-004, FP-006, FP-009, both FP-010 files, FP-011, EI-001, EI-002, EI-003, EI-012, EI-013, EI-014, EI-015, EI-017, IT-001, the Industry Twin Lifecycle Specification, EKPP-001, Knowledge Pack Specification, RP-001, RP-002, CIOS-AI, the Reference Architecture, Design Doctrine, Chief Architect Handbook, Document Map, Architecture Authority Registry, Commercial Digital Twin Research Agent Guide, Enterprise Knowledge Architecture, Banking Industry Twin, Banking closure and validation artefacts, Banking research migration and completion reports, and Flora/Banking evaluation and backlog documents.

## FP-010 Assessment

### Exact FP-010s found

Two documents currently use the FP-010 identifier:

1. `architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md` — **FP-010 — Knowledge Pack Architecture**, status **Proposed Foundation**, owner **Rob / CIOS**, owning ADR **ADR-016**.
2. `architecture/founding-papers/FP-010-Enterprise-Reinvention-Intelligence.md` — **FP-010 — Enterprise Reinvention Intelligence**, status **Review**, owner **Rob / CIOS**, explicitly excluded from all production profiles.

### What FP-010 already governs

The accepted authority chain still treats **FP-010 — Knowledge Pack Architecture** as the conceptual owner for Knowledge Packs under ADR-016. It governs exchange containers, Knowledge Assets, presentation payloads, provenance, validation, Unknowns, Contradictions and recommendations. It deliberately separates package validity from canonical knowledge acceptance.

The newer **FP-010 — Enterprise Reinvention Intelligence** governs no production behaviour. It is a founding rationale explaining the relationship between EGM methodology, CIOS architecture, Flora runtime, specialist companions, Commercial Asset Generation and continuous learning. It says it does not replace EGM-001, Enterprise Intelligence papers, accepted ADRs or the Reference Architecture.

### What was incorrectly being proposed as new

A separate reinvention/research doctrine would duplicate material already distributed across FP-004, FP-006, FP-009, EI-001, EI-002, EI-003, EI-012, ADR-001, ADR-002, ADR-004, ADR-005, ADR-009, ADR-010, ADR-012, ADR-016, EKPP-001 and IT-001. A new Research Standard is not justified by the evidence gathered in this audit.

### Is FP-010 still the correct owning document?

For Knowledge Packs, **yes**, but its status and identifier collision need reconciliation. For Enterprise Reinvention Intelligence, **no** as an operating owner: it should remain a Review rationale unless promoted by a separate decision.

### Does FP-010 need amendment?

**Targeted substantive update.** The Knowledge Pack FP-010 needs metadata/status reconciliation with ADR-016 and the Authority Registry. The Enterprise Reinvention FP-010 needs either a new identifier or an explicit supersession/renumbering decision to remove the FP-010 collision. This is not a reason to create FP-011 replacement doctrine because FP-011 already exists as Knowledge Exchange Architecture.

### Missing, stale or broken references

The Commercial Digital Twin Research Agent Guide links to `../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md`, but the actual file is `architecture/specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md`; from `architecture/research/` the relative link should be `../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md`, which exists. The same guide references `../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md`, which exists. It also references Knowledge Pack architecture and Knowledge Exchange architecture that exist. The larger issue is not broken paths in that guide but status mismatch: it presents Review/Draft lifecycle material as aligned guidance while the Authority Registry excludes IT-001 and the lifecycle spec from production packs.

## Gold standard assessment

**Decision:** Partially — strong architecture, incomplete operating guidance.

| Dimension | Rating | Evidence summary |
| --- | --- | --- |
| Research scope | Partial | Industry and enterprise scope are described in IT-001, EKPP-001, EI-001 and Banking artefacts, but supplier, contract, procurement and programme coverage are not consolidated into Researcher-visible accepted guidance. |
| Research quality | Substantive | FP-004, FP-006, ADR-010 and EI-012 define source/evidence/Observation quality, but FP-004 and FP-006 remain draft and are not in the accepted Researcher pack. |
| Research completeness | Weak | ADR-009 defines progressive assurance and Banking closure records pilot acceptance, but minimum viable Industry Twin completeness thresholds are unresolved Known Unknowns in IT-001. |
| Connected intelligence | Partial | Doctrine supports Source → Evidence → Observation → Signal/Behaviour → Hypothesis → Opportunity → Recommendation, but pressure → programme → supplier → contract → procurement trigger → buyer → timing → addressable opportunity is not fully owned. |
| Research operation | Weak | RP-001 defines the role but the official Researcher pack is intentionally narrow; the Research Agent Guide is helpful but not registry-approved. |
| Industry acceptance | Partial | Banking v1 closure provides a precedent and ADR-009 provides assurance mode, but generic Industry Twin acceptance criteria are not accepted and discoverable. |

## Industry Twin lifecycle coverage

The full lifecycle is mapped in [Industry Twin Lifecycle Documentation Map](Industry-Twin-Lifecycle-Documentation-Map.md). The highest-risk stages are source mapping, supplier/contract/procurement intelligence, research completeness, Researcher-to-architecture handover, Codex implementation handover, generic Industry Twin acceptance, and refresh/decay.

## Researcher knowledge-pack assessment

The Researcher currently knows the accepted role, profile membership rules, design doctrine, Reference Architecture navigation, Enterprise Model, Observation, Knowledge Graph, Enterprise Behaviour, accepted hypothesis validation, accepted ADRs and glossary only if operating from the registry-defined `researcher-pack`. The Researcher does **not** receive IT-001, the Industry Twin Lifecycle Specification, EKPP-001, FP-004, FP-006, the Commercial Digital Twin Research Agent Guide or Banking lessons through the production profile. See [Researcher Knowledge Pack Audit](Researcher-Knowledge-Pack-Audit.md).

## Banking lessons traced

Banking v1 demonstrates that future Industry Twins need deeper historical coverage, stronger supplier intelligence, explicit contract/procurement timing, valuation comparables, equal enterprise research depth, less generic AI-native description, analyst/scrutiny coverage, research-completeness gates, clearer research-gap versus product-defect separation, avoidance of hard-coded Banking assumptions, and stronger human commercial validation. Existing doctrine covers the evidence/lineage/unknown principle, but operating guidance does not yet force these Banking lessons into the Researcher workflow.

## Conflicts and duplication

| Issue | Type | Documents | Required treatment |
| --- | --- | --- | --- |
| FP-010 identifier collision | Authoritative/editorial conflict | FP-010 Knowledge Pack Architecture; FP-010 Enterprise Reinvention Intelligence; ADR-016; Authority Registry | Preserve ADR-016; reconcile the Review FP-010 identifier. |
| Research guide depends on non-production material | Discoverability/authority conflict | Commercial Digital Twin Research Agent Guide; Authority Registry; RP-001 | Either register a revised guide or make its non-production status explicit. |
| Industry Twin lifecycle ownership is Draft/Review | Missing accepted guidance | IT-001; Industry Twin Lifecycle Specification; EKPP-001 | Targeted acceptance/remediation before Public Sector research. |
| Old CIRM chain versus Observation-led doctrine | Ambiguity | FP-004/FP-006; Design Doctrine; EI-012 | Update source/evidence papers to align chain language without changing doctrine. |
| Banking closure cites Review specs as relevant architecture | Editorial conflict | UK Banking closure; Authority Registry | Add caveat in future closure template that Review specs were design inputs, not accepted authority. |

## Genuine documentation gaps

The gap analysis records the full set. P0 gaps are:

- P0-G01: No accepted, Researcher-visible Industry Twin operating route from selection through handover.
- P0-G02: No accepted minimum research completeness/readiness gate for an Industry Twin.
- P0-G03: Supplier, contract and procurement timing requirements are not consolidated in Researcher-visible guidance.
- P0-G04: Banking lessons are not converted into a next-industry research checklist.
- P0-G05: FP-010 identifier/status conflict creates authority confusion.

## Proposed documentation architecture

No speculative new standard is recommended now. The proposed architecture is:

- **Foundational doctrine:** CIOS-AI, Design Doctrine, Reference Architecture, Architecture Principles, Chief Architect Handbook.
- **Accepted architecture controls:** ADRs, EI-001, EI-002, EI-003, EI-012, FP-009, AP-001, AP-002, RP-001, RP-002, Glossary.
- **Production protocol:** amend EKPP-001 or add accepted appendix for Industry Twin production lifecycle and handover.
- **Industry model:** amend/promote IT-001 only after resolving Known Unknowns needed for Public Sector research.
- **Research operating guidance:** revise and register the Commercial Digital Twin Research Agent Guide or create a narrow accepted Researcher Handbook only if the Authority Registry cannot responsibly include the revised guide.
- **Acceptance standard:** add a generic Industry Twin acceptance section to EKPP-001 or ADR-009 rather than creating a separate standard.
- **Closure artefacts:** use Banking v1 closure as precedent, not doctrine.

## Review outcomes

### Architecture Reviewer

**Outcome:** Approved with conditions.

Conditions: resolve FP-010 identifier collision; do not promote Review material by prose; define accepted ownership for Industry Twin lifecycle/readiness before Public Sector research; keep IT-001 as model owner and EKPP/ADR-009 as process/acceptance owner.

### Research Operations Reviewer

**Outcome:** Approved with conditions.

Conditions: make Researcher operating guidance discoverable in the production profile; add supplier/contract/procurement timing checklist; add Banking lessons checklist; define stop/readiness/handover criteria before Public Sector research begins.

## Chief Architect decision record

| Decision | Outcome |
| --- | --- |
| Gold standard status | Partially — strong architecture, incomplete operating guidance |
| FP-010 update status | Targeted substantive update |
| Researcher knowledge-pack update status | Targeted operating-guidance update |
| New-document requirement | No |
| Public Sector research readiness | Yes, after P0 documentation changes |
| Overall readiness conclusion | Requires targeted documentation remediation |
