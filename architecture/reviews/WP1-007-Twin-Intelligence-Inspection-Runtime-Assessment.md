# WP1-007 — Twin Intelligence Inspection Runtime Assessment

**Status:** Assessment complete — implementation not started  
**Date:** 2026-07-27  
**Decision requested:** Evolve the existing Enterprise Canvas, Model Explorer and Executive Intelligence Brief into the common inspection experience; do not create a parallel runtime.  
**Assessment scope:** Repository runtime code and accepted architecture, with proposed and dormant architecture distinguished from executable capability.

## 1. Executive conclusion

Flora **already possesses the foundations of a governed Twin Intelligence Inspection Runtime**, but they are distributed across several product surfaces. The strongest reusable foundation is the Enterprise Canvas and its Model Explorer drill-down: it reads governed Twin state, presents an executive-first view, exposes uncertainty and freshness, and reaches claim-level Evidence and lineage. The Enterprise Intelligence Runtime already generates a bounded, validated Executive Intelligence Brief over the same governed state. Blueprint Import already provides unusually complete package, maturity, review, promotion and audit inspection.

The missing capability is therefore not another runtime. It is a **common presentation contract and route policy** that lets an accepted inspectable Twin use those capabilities consistently. Import inspection, Enterprise Canvas inspection, Explore, banking dashboards and financial-review screens currently assemble similar concepts independently.

The smallest commercially valuable increment is to make the existing Enterprise Canvas route the post-promotion destination for supported Enterprise Twins and add a shared, metadata-driven section navigation around its existing Executive Intelligence Brief, Canvas and lineage sections. It should initially support Enterprise Twins only. Industry and other governed types should join only when their existing canonical read models can satisfy the same presentation contract.

This conclusion preserves:

- canonical memory ownership outside the UI;
- ADR-012's staging and explicit-promotion boundary;
- ADR-013's Enterprise Canvas as the primary Living Twin navigation model;
- ADR-014's separation of governed fact from transient interpretation;
- the distinction between implemented runtime and future architectural intent.

## 2. Method and classification

The assessment traced HTTP dispatch, rendered views, domain/read services, persistence and the relevant ADRs. Capability is classified as:

- **Implemented:** reachable executable behavior with a runtime route and backing data/service.
- **Partial:** executable behavior with restricted type, fixture, tenant, object or depth coverage.
- **Dormant:** executable helper or model that is not part of the primary reachable journey.
- **Intent only:** documented architecture without a general implemented runtime.
- **Duplicated:** substantially the same user concern rendered by separate presentation code.

Static repository evidence cannot prove production deployment, provider availability, data population or authorization configuration. “Implemented” here means implemented in this repository, not demonstrated in every deployed environment.

## 3. Runtime capability assessment

### 3.1 Capability map

| Concern | Runtime location | State | Assessment and reuse decision |
|---|---|---:|---|
| Twin registry / entry | `/digital-twins`; `digital_twins_landing_page()` | Implemented, narrow | Governed list plus a BT special case. Reuse as discovery; do not make it another inspection shell. |
| Governed Twin detail | `/digital-twins/{enterprise_id}/canvas` | Implemented for Enterprise Twins | The best common-shell foundation. It renders a governed read model rather than owning Twin truth. |
| Executive overview | Enterprise Canvas overview | Implemented | Summary, Twin version, cut-off, assurance status, confidence, change, pressures, stakeholders, commercial relevance and next moves already form an inspection opening. |
| Executive Intelligence Brief | `/digital-twins/{enterprise_id}/executive-intelligence-brief` and generation action | Implemented, availability-dependent | Bounded retrieval, evidence package, structured brief, validation and safe fallback exist. Reuse as the optional first section, never as canonical fact. |
| Model / entity inspection | Canvas tile detail | Implemented | Core facts, state, pressure, response, unresolved matters, stakeholders, projections, freshness and next posture are already inspectable. |
| Evidence and research lineage | Canvas tile lineage; `/evidence/{id}`; object context/lineage routes | Implemented, fragmented | Observation → Evidence → Source → package location is implemented in Canvas lineage. Consolidate links and labels, not data ownership. |
| Unknowns / Contradictions | Canvas overview, tile markers and lineage; Brief | Implemented | Preserved as uncertainty, not coerced into facts. This is common-shell material. |
| Confidence / freshness | Canvas cards, tile detail and lineage | Implemented, inconsistent aggregation | Item-level qualifications and dates exist; overview confidence is qualitative. Reuse values and add only a common presentation vocabulary. |
| Relationships / dependencies | Canvas tiles and lineage references | Partial | Operating-model handoffs and dependencies are textual; nested-Twin markers exist. A universal relationship list or interactive graph is not implemented. |
| Graph exploration | Core and graph models; architectural EI graph | Partial / dormant for UI | Graph records support nodes, edges and influence structures, but the primary Flora UI has no general interactive graph explorer. Do not claim graph navigation or build a duplicate graph solely for inspection. |
| Timeline / history | Banking event, analyst and financial-history routes; import staging and lifecycle histories | Implemented in silos | Useful type-specific views exist, but no general Twin timeline projection exists. Treat timeline as conditional. |
| Change history | Import ledger/lifecycle, feedback audit, factual-memory and specialist histories | Partial | Audit trails exist in their owning workflows. There is no single cross-source Twin change-history read model. Link to owner views before aggregating. |
| Package inspection | `/blueprint-import/{run}/inspect` and associated package views | Implemented | Validation, inventory, mapping, maturity, provenance and affected-Twin inspection are strong. Keep package/run identity distinct from Twin identity. |
| Review and promotion | Blueprint review/promote; financial claim review/apply | Implemented, duplicated workflows | Both correctly gate canonical mutation, but present review decisions independently. They are governed workflows, not general Twin sections. |
| Completeness / maturity | Blueprint import maturity assessment | Implemented for candidate/import context | Type-weighted package, overall and decision completeness exist. They must not be silently relabelled as canonical Twin health after promotion. |
| Evidence coverage / density | Counts and lineage availability across Canvas/import/snapshots | Partial | Counts exist, but no accepted universal evidence-density metric or denominator is implemented. Avoid inventing a score. |
| Existing dashboards | Flora home, Banking portfolio, Live evidence, financial intelligence, digital Twins | Implemented, overlapping | These are task- and domain-specific entry points. They should deep-link into the common inspection route rather than reproduce Twin detail. |
| Navigation | Home modes, Explore/Focus/Shape/Governance, Digital Twins, redirects | Implemented, overlapping | Legacy Twin detail and registry aliases already redirect, showing an existing consolidation policy. Section-level Twin navigation remains absent. |

### 3.2 Existing common-shell foundation

The Enterprise Canvas already implements ADR-013's four levels of disclosure:

1. enterprise overview;
2. area/tile understanding;
3. pressures, mechanisms and commercial interpretation;
4. Evidence, Observations, sources, uncertainty and original-package lineage.

It is explicitly a read model. Its tiles are views, not new canonical objects. Its feedback path creates candidate human knowledge and preserves canonical state until review. These properties make it safer to generalize than either package inspection (whose subject is an Import Run) or a banking dashboard (whose subject is a portfolio/use case).

The Executive Intelligence Brief complements rather than replaces the Canvas. Its generated interpretation is transient, validated and evidence-bounded; failure returns an unavailable state with a path back to Model Explorer. The correct opening policy is therefore:

`existing accepted brief/presentation → validated generated brief when requested/available → deterministic governed overview fallback`

It is not safe to require generation merely to inspect a Twin.

## 4. Existing inspection section map

| Proposed standard section | Already exists? | Existing source | Common or conditional? | Required treatment |
|---|---:|---|---|---|
| Executive Summary | Yes | Executive Brief and Canvas hero/overview | Common | Prefer validated Brief; fall back to governed deterministic overview. |
| Commercial Summary | Yes, under other labels | Brief commercial relevance; Canvas Commercial Relevance; Shape output | Common where supported | Reuse projection/interpretation labels and `what not to claim`; do not make it fact. |
| Completeness | Yes for import; not general | Import maturity and validation | Conditional initially | Show imported package/candidate measures with their scope. Do not imply universal Twin completeness. |
| Confidence | Yes | Projections, pressures, lineage Evidence | Common | Present item-level qualification; summary must say mixed/unknown rather than average incompatible values. |
| Evidence | Yes | Canvas lineage, Evidence routes, Live Evidence | Common | Route material claims to the canonical lineage inspection. |
| Unknowns | Yes | Canvas, Brief, package review | Common | Preserve identifiers, impact and resolution need where available. |
| Contradictions | Yes | Canvas, Brief, package review | Common | Preserve both positions and review state; never auto-resolve in presentation. |
| Relationships | Partial | Canvas operating model and lineage links | Common when data exists | Render existing governed links; no UI-local relationship ontology. |
| Timeline | Specialist only | Banking event/analyst/financial history | Conditional | Register type-specific timeline providers; otherwise omit with no empty promise. |
| Research lineage | Yes | Canvas lineage to source/package; object context package | Common | Use the existing lineage chain and package location. |
| Change history | Partial | Import/staging ledger, feedback audit, specialist histories | Conditional | Link owner histories now; aggregate only after a canonical read contract exists. |
| Supporting intelligence | Yes | Brief pressures/portfolio/stakeholders; Canvas sections | Common, metadata-selected | Treat as projections/derived intelligence with lineage and status. |
| Cross-Twin dependencies | Partial | Nested-Twin marker, relationships, linked IDs | Conditional | Link only resolvable governed Twin identities; no inferred hierarchy. |

No new architectural concept is needed for these section names. What is missing is a `TwinInspectionPresentation` contract that describes which existing read projections are available and how to navigate them. It must contain references and presentation metadata, not duplicate domain records.

## 5. Explore capability assessment

### 5.1 What Explore currently does

`/explore` is a governed Banking exploration experience over the banking pipeline. It presents industry change, observations, mechanisms, hypotheses, “why now,” Evidence links, Unknowns and Contradictions. `/focus` then compares enterprise relevance, and `/shape` produces an evidence-aware engagement view. This is a coherent reasoning journey, not a generic object browser.

Explore therefore contributes reusable **industry-level derived views and navigation context**, but it is not currently a universal Twin explorer. Its object links resolve through the general Evidence detail surface rather than a general Industry Twin inspection route. The repository also contains broad architectural and knowledge assets for Industry Twins, but file presence is not equivalent to a reachable runtime.

### 5.2 Cross-Twin navigation finding

The desired Industry → Enterprise → Supplier → Capability → Opportunity journey is **not implemented as a complete governed runtime chain**. Existing building blocks are:

- Explore-to-Focus navigation from industry reasoning to enterprise comparison;
- governed relationship and graph data structures;
- Canvas operating-model links and nested-Twin indicators;
- banking enterprise opportunity routes;
- lineage-linked object IDs.

These justify a single “Related Twins”/relationships projection when the target has a governed identity and inspectable route. They do not justify a second hierarchical navigator or claims that every example level is a Twin. Until resolvable governed links exist, the UI should retain the current domain navigation and avoid synthesizing the chain.

## 6. Twin taxonomy assessment

The following table describes current **runtime support**, not every term used in design documents or knowledge assets.

| Requested taxonomy | Current standing | Inspection implication |
|---|---|---|
| Industry Twins | Architecturally specified governed Twin; package maturity profile exists; runtime Explore is a banking projection | Do not call Explore itself the Twin. Add common inspection only after an Industry Twin read adapter supplies identity, sections and lineage. |
| Enterprise Twins | Independent governed Twin / durable Enterprise Model with implemented Canvas | Supported first-class inspection target now. |
| Market Participants | Specified governed Twin type and import maturity profile; no general detail route | Unsupported by common runtime today; do not equate every participant with Enterprise Twin. |
| Suppliers | Relationship/participant role or projection in current runtime, not proven as an independent universal Twin type | Inspect as linked governed object or participant projection unless owning architecture provides a Twin identity. |
| Capabilities | Governed object/model element and Canvas lens/tile material | Inspect within owning Twin or linked object; do not invent Capability Twin. |
| Opportunities | Governed commercial objects; Opportunity Twin is architecturally specified and has an import maturity profile; banking routes are specialist projections | Keep object and Twin distinctions explicit. A common adapter is future work, not assumed. |
| Products | Offerings/products are governed content/projections in provider and commercial models | No evidence of a general independent Product Twin runtime. |
| Technologies | Enterprise model content/lens and linked objects | No evidence of a general independent Technology Twin runtime. |

Other repository types (for example Infrastructure Twin and Provider Offer Twin) reinforce why the shell must be adapter-driven rather than backed by a hard-coded universal taxonomy. No new Twin types are recommended by this assessment.

## 7. Inspection consistency model

### 7.1 Common sections

Every inspectable Twin should expose, when backed by governed data:

- identity, type, version/status and canonical owner;
- Executive Summary with interpretation status;
- confidence and temporal scope;
- Evidence and lineage;
- Unknowns and Contradictions;
- governed relationships and related inspectable Twins;
- change/audit entry point;
- supporting derived intelligence with projection labels.

“Unavailable,” “not supplied” and “not applicable” must remain distinct. Empty sections should normally be omitted, while governance-critical absence (for example missing lineage for a material claim) should be explicit.

### 7.2 Twin-specific sections

- **Industry:** mechanisms, value chains, jurisdictions/control bodies, participant landscape, industry pressures.
- **Enterprise:** operating model, material pressures, change portfolio, stakeholders, commercial relevance.
- **Market Participant:** offerings/capabilities, markets/customers, delivery evidence, partnerships and constraints.
- **Opportunity:** buyer pressure, target outcome, addressability, procurement, dependencies, delivery/competition and next action.
- **Import candidate:** validation, mapping, proposed effects, exclusions/quarantine, decision completeness and promotion readiness.

These are projections selected by type metadata. They are not additions to the canonical object model.

### 7.3 Minimal section metadata

The presentation contract needs only:

- stable section key and human label;
- order and executive/detail/governance grouping;
- source read-projection/provider;
- truth class (`canonical`, `evidence`, `observation`, `projection`, `generated interpretation`, `candidate`);
- availability and reason when governance-critical;
- lineage target;
- authorization requirement;
- freshness/effective-date fields already supplied by the source;
- optional related-Twin route resolved from canonical identity.

It must not store copied Evidence, calculate domain scores, create relationships or decide canonical type.

## 8. Completeness assessment

### 8.1 Existing measures

Blueprint Import implements deterministic, explainable type-specific maturity dimensions for Industry, Enterprise, Market Participant, Opportunity and Control Body candidates. It exposes:

- package completeness;
- overall maturity;
- decision completeness;
- weighted dimension results;
- caps and penalties;
- critical/material gaps;
- stale Evidence;
- unresolved Unknown and Contradiction counts;
- next Evidence need.

Canvas implements source cut-off, last refresh, assurance/acceptance state, lineage availability, qualitative confidence and item freshness. Specialist snapshots expose counts. Evidence confidence is often a qualification, not a scalar.

### 8.2 What does not yet exist

There is no accepted universal runtime definition for:

- post-promotion Twin completeness;
- evidence density and its denominator;
- cross-type coverage;
- research maturity versus commercial maturity;
- aggregation of heterogeneous confidence;
- one freshness score across mixed Evidence.

### 8.3 Smallest additions

Do not add a new composite score. Add a shared **Completeness presentation** that can display named measures from their owner with `measure`, `scope`, `as_of`, `method/version`, `value/status`, `gaps`, and `lineage`. Initially it should show:

1. Progressive Assurance / acceptance status from governed Twin metadata;
2. source cut-off and last refresh;
3. lineage coverage as honest counts (`material statements with lineage / material statements rendered`) where the existing read model can supply both;
4. unresolved Unknowns, Contradictions and stale-Evidence counts;
5. import package/candidate maturity only when explicitly scoped and linked to that import/version.

Research and commercial maturity remain separate labels until their owners approve definitions.

## 9. Duplication and overlap assessment

| Duplication | Evidence | Consolidation direction |
|---|---|---|
| Executive narratives | Canvas deterministic overview, generated Brief, Explore, Shape, Banking briefing and digital-Twin BT page each render summaries | Use Brief/Canvas opening policy; specialist pages link to it and retain only use-case-specific analysis. |
| Evidence cards and lineage | Canvas lineage, generic Evidence detail, Explore chips, Brief `<details>`, Live Evidence and financial review each render references differently | Standardize a lineage link/panel contract; keep Evidence data with its owner. |
| Unknown/Contradiction cards | Explore, Canvas, Brief and import review each format uncertainty | Share presentation vocabulary/component; preserve workflow-specific decisions. |
| Confidence/freshness labels | Canvas tiles, package maturity, financial claims and banking views use separate wording | Normalize display semantics, not source scales. Always show scope/method. |
| Twin detail routes | Canvas, BT special page, `/flora/object/*`, Banking enterprise pages and legacy redirects overlap | Canonicalize accepted Twin inspection on `/digital-twins/{id}/canvas` (or a later type-neutral alias that redirects without duplicating logic). |
| Review workflows | Package candidate review and financial claim review have separate tables/actions | Keep distinct command handlers; share visual decision primitives only after contract alignment. |
| History/timelines | Import staging history, banking event/analyst/financial history, feedback audit | Expose as conditional owner-provided sections; do not merge into an ungoverned event stream. |
| Navigation | Product mode nav, Digital Twins registry, Banking portfolio and legacy aliases compete as entry points | Keep task entry points, but resolve every governed Twin link to one inspection destination. |

Some apparent duplication is legitimate separation: an Import Run is not a Twin, a review command is not inspection, and a generated executive interpretation is not canonical memory.

## 10. Gap analysis

### Blocking gaps for a universal experience

1. No type-neutral inspection presentation contract or section registry.
2. Enterprise Canvas service is enterprise-specific; other governed types lack runtime adapters.
3. No canonical route-resolution service from governed object/Twin identity to inspection destination.
4. Relationships cannot yet guarantee target type, authorization and routable governed identity.
5. General timeline and change-history read contracts do not exist.
6. Completeness semantics are import-scoped and cannot be generalized silently.
7. Presentation helpers are embedded in several Python HTML renderers rather than shared components.

### Non-blocking gaps

- No interactive graph explorer. Existing linked relationships are enough for the first increment.
- No universal generated brief for every type. Deterministic governed overview is a safe fallback.
- No universal evidence-density score. Honest scoped measures are commercially sufficient.
- No new taxonomy. Existing owner-provided type metadata is sufficient.

## 11. Proposed unified architecture

```text
Product entry points
(Explore, Focus, registry, import completion, dashboards)
                         |
                         v
Governed identity + authorization-aware route resolver
                         |
                         v
Twin Inspection Shell (Flora presentation/orchestration only)
  - header, shared section navigation, truth/status labels
  - Executive Brief -> governed overview fallback
  - section availability from metadata
  - no canonical data, scoring or relationship ownership
                         |
          +--------------+----------------+
          |              |                |
          v              v                v
 Existing read adapters  Existing lineage Existing workflow links
 Enterprise Canvas       Evidence/Source   import review/promotion
 Explore projections     package location feedback/change histories
 future owner-approved
 type adapters
                         |
                         v
 Canonical governed memory and owning services remain unchanged
```

### Architectural rules

1. **One shell, multiple owned projections.** The shell orchestrates existing read capabilities; it does not normalize them into a second knowledge store.
2. **Identity precedes routing.** Only an owner-recognized governed Twin identity receives a Twin route.
3. **Inspection is read-first.** Review, promotion, feedback and refresh remain explicit linked commands with authorization and audit.
4. **Truth class is visible.** Canonical state, Evidence, Observation, projection, generated interpretation and candidate state cannot share an unlabeled card.
5. **Executive-first, lineage-near.** Start with the Brief/overview and keep material claims within purposeful reach of lineage.
6. **Conditional sections.** A section appears only when an owned provider supports it; type-specific absence does not create placeholder facts.
7. **No duplicate graph/navigation model.** Related-Twin navigation is a projection of governed relationships with authorization-aware targets.
8. **Import context survives promotion.** Package inspection remains available as research lineage, while the promoted Twin opens in the common shell.

## 12. Canonical owner recommendation

**Recommended experience owner:** the existing Flora Enterprise Canvas / workspace presentation boundary governed by **ADR-013 (Owner: Rob / CIOS)**, extended as a presentation contract through the normal architecture decision workflow.

This is ownership of inspection composition and navigation only. Canonical ownership remains unchanged:

- Twin/Enterprise Model state with its owning CIOS model and memory services;
- Evidence, Observations, Unknowns, Contradictions and relationships with their existing owning models/services;
- import lineage, staging, review and promotion with the Blueprint Import boundary under ADR-012;
- generated executive interpretation with the Enterprise Intelligence Runtime boundary under ADR-014;
- type taxonomy with the relevant accepted Twin specification, never the shell.

ADR-025 is proposed, not accepted, so it is useful direction but not authority for overriding ADR-012/013/014. A small ADR-013 amendment or accepted presentation-contract specification is preferable to declaring a new “Twin Inspection Runtime” domain.

## 13. Recommended roadmap

### Increment 1 — unify the supported Enterprise Twin journey

1. Approve a minimal `TwinInspectionPresentation` read contract and truth/availability vocabulary.
2. Wrap existing Enterprise Canvas sections with shared in-page navigation and stable section keys; do not rewrite their data logic.
3. Use the existing validated Executive Intelligence Brief as the first section when available and the Canvas overview as fallback.
4. Redirect post-promotion “Open Twin” and registry/detail links for supported Enterprise Twins to the Canvas.
5. Add scoped completeness/freshness/uncertainty presentation from existing values.
6. Preserve package inspection as a Research Lineage link, not as the promoted Twin's main page.

**Acceptance:** one supported imported/promoted Enterprise Twin can move from package inspection → review → promotion → common executive inspection → claim lineage without a parallel store, type or scoring model.

### Increment 2 — presentation reuse and related-Twin links

1. Extract shared uncertainty, confidence/freshness, Evidence-link and section-navigation renderers.
2. Introduce authorization-aware route resolution for existing governed identities.
3. Render resolvable governed relationships as Related Twins; leave non-Twin objects as linked objects.
4. Point Banking/Focus dashboards at canonical inspection routes while retaining portfolio-specific context.

### Increment 3 — owner-approved type adapters

1. Add an Industry Twin adapter over an accepted Industry read model; reuse Explore projections without making Explore canonical.
2. Add Market Participant and Opportunity adapters only after their owning specifications and runtime identities can meet the contract.
3. Register specialist timelines/change histories as optional providers.

### Deferred pending architecture/data contracts

- universal graph visualization;
- universal completeness, commercial-maturity or evidence-density scoring;
- synthesized cross-Twin hierarchy;
- independent Supplier, Capability, Product or Technology Twin types;
- persistence of generated briefs without governed approval.

## 14. Smallest implementation increment

The smallest commercially valuable increment is **route-and-presentation convergence for one promoted Enterprise Twin**, not a new runtime:

- destination: existing Enterprise Canvas;
- opening: existing Executive Intelligence Brief if valid, otherwise current overview;
- navigation: Overview, Commercial Relevance, Completeness, Evidence & Lineage, Unknowns & Contradictions, Relationships and Change/Package History, with unsupported sections omitted or linked to owner views;
- measures: current assurance status, cut-off, refresh, lineage counts and uncertainty counts, all scoped;
- cross-navigation: only existing governed links;
- mutation: none in inspection; existing review/promotion/feedback commands remain separate.

This increment demonstrates the universal-experience direction using existing capability, creates immediate post-promotion value, and avoids premature generalization. Only after it is accepted should implementation extend to an Industry Twin adapter.

## 15. Assessment gate

This document completes the WP1-007 assessment and capability map. No runtime implementation is included. Implementation may begin only after the recommended ownership and Increment 1 scope are accepted through the repository's architecture workflow.
