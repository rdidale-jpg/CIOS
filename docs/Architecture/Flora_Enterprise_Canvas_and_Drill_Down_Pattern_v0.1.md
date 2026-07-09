# Flora Enterprise Canvas and Drill-Down Pattern v0.1

**Status:** Approved design baseline for Flora Sprint 1  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09  
**Authority:** ADR-013 and CIOS Enterprise Intelligence Experience Standard v0.1

## 1. Purpose

This pattern defines the first user experience for a Blueprint imported into Flora.

It turns the accepted MOD Commercial Digital Twin into a navigable enterprise experience using:

- an Enterprise Canvas;
- Intelligence Tiles;
- an Intelligence Detail Panel;
- progressive drill-down;
- lineage inspection;
- governed feedback.

The pattern is enterprise-neutral. MOD is the pilot.

## 2. Target user outcome

A strategic commercial professional should be able to open Flora and understand:

- what the enterprise exists to do;
- how it is broadly organised;
- where the major pressures and pains sit;
- what is changing;
- what the enterprise is already doing;
- what remains unresolved;
- which roles care;
- what to inspect or ask next;
- why Flora believes the judgement.

The user should not need to open a workbook or read the full Blueprint first.

## 3. Primary layout

```text
┌──────────────────────────────────────────────────────────────────┐
│ Enterprise header                                                │
│ Name | purpose | Twin version | effective date | maturity        │
│ Governing thesis | material change | refresh trigger             │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ Lens switcher: Organisation | Pain | Transformation | ...        │
│ Search | filters | freshness | attention                         │
└──────────────────────────────────────────────────────────────────┘
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ Intelligence Tile  │ │ Intelligence Tile  │ │ Intelligence Tile  │
└────────────────────┘ └────────────────────┘ └────────────────────┘
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ Intelligence Tile  │ │ Intelligence Tile  │ │ Intelligence Tile  │
└────────────────────┘ └────────────────────┘ └────────────────────┘
```

Clicking or activating a tile opens a detail route or panel.

## 4. Enterprise header

Required elements:

- enterprise name;
- plain-English purpose;
- Twin version;
- effective date;
- source cut-off;
- maturity statement;
- package import state;
- latest material change;
- material refresh trigger;
- visible limitation where import is partial.

Optional:

- parent or nested-Twin path;
- governing thesis;
- total attention items.

Do not display one synthetic “health score”.

## 5. Organisation Lens

Sprint 1 implements the Organisation Lens.

For the MOD pilot, use six to ten top-level tiles derived from governed state, for example:

- Strategic Direction and Departmental Leadership;
- Finance, Affordability and Assurance;
- Military Commands and Force Generation;
- Acquisition and Capability Delivery;
- Digital, Data and Operational AI;
- Corporate Services and Defence Business Services;
- Workforce and Skills;
- Suppliers and Industrial Base.

The exact tile set must be traceable to package entities, domains or accepted projections. It must not be invented solely for visual balance.

## 6. Intelligence Tile

### 6.1 Tile anatomy

A tile may show:

- name;
- one-sentence role;
- accountable role where known;
- current state label;
- principal pain or pressure in plain English;
- material change;
- attention markers;
- nested-Twin marker;
- last relevant refresh.

### 6.2 Tile states

Supported visual states:

- stable;
- changing;
- under pressure;
- evidence incomplete;
- contradicted;
- stale;
- partial import.

These are presentation summaries. They must link to the governed dimensions used to derive them.

### 6.3 Attention markers

Examples:

- Unknown;
- Contradiction;
- stale Evidence;
- upcoming accountability event;
- bounded Burning Platform;
- high Transformation Pressure;
- incomplete import mapping.

Markers use icon, text and accessible label; never colour alone.

### 6.4 Tile selection

A selected tile must have:

- visible focus and selected state;
- URL-addressable identity where practical;
- keyboard activation;
- accessible name that includes tile role and state;
- deterministic content from the same Twin version.

## 7. Intelligence Detail Panel

The panel opens with the executive explanation, not internal records.

### Section 1 — What this area does

- purpose;
- responsibilities;
- outcomes;
- material dependencies.

### Section 2 — Core facts

Use up to six facts initially:

- scale;
- budget/resource pool;
- workforce;
- major programmes;
- key systems;
- supplier or accountability context.

Each fact shows date and truth class on inspection.

### Section 3 — What is changing

Show:

- latest material Observations;
- direction or trajectory;
- upcoming accountability event;
- last refresh.

### Section 4 — Key pains and pressures

For each displayed pain:

- issue in plain English;
- why it matters;
- affected outcome;
- current response;
- whether effectiveness is proven;
- what remains unresolved.

Default maximum: three. Offer “view all”.

### Section 5 — Stakeholders and hot buttons

Show:

- accountable roles;
- affected roles;
- what each must defend, decide or prove;
- one useful executive question.

### Section 6 — Unknowns and Contradictions

Show the material items that limit confidence.

### Section 7 — Next action

Use one or more bounded postures:

- Learn;
- Validate;
- Map;
- Monitor;
- Request Evidence;
- Open nested Twin.

Do not show Pursue without an authorised Provider Fit Overlay.

### Section 8 — Inspect lineage

Provide a lineage summary and entry point.

## 8. Pain detail

Opening a pain creates a Level 3 mechanism view.

Required structure:

1. pain in one sentence;
2. why it matters now;
3. enterprise consequence;
4. affected areas and stakeholders;
5. causal mechanism;
6. current response;
7. response delivery state;
8. evidence of effectiveness;
9. what remains unresolved;
10. strongest contrary Evidence;
11. solution principles;
12. practical solution patterns;
13. proof measures;
14. evidence that would change the view;
15. lineage.

Internal Pain Point IDs remain visible in the inspection area, not the headline.

## 9. Current-response representation

Use a simple response timeline or ladder:

`recognised → proposed → approved → funded → contracted → mobilised → piloted → deployed → adopted → supported → benefits evidenced → scaled`

Show:

- current known state;
- supporting Evidence;
- missing transition;
- current effectiveness assessment;
- secondary pain where known.

Do not show a later state without supporting evidence.

## 10. Lineage View

### 10.1 Default summary

Example:

> Supported by 6 Observations from 4 Sources. One material Contradiction remains. Latest supporting Evidence: 18 June 2026.

### 10.2 Expanded chain

```text
Displayed judgement
  ↓
Analytical Projection or Hypothesis
  ↓
Observation(s)
  ↓
Evidence item(s)
  ↓
Source
  ↓
Original package file and location
```

Each node shows:

- ID;
- title or statement;
- truth class;
- date;
- confidence/freshness where applicable;
- package mapping;
- open action.

### 10.3 Incomplete chain

The UI states:

- missing link;
- consequence;
- recommended Evidence request.

### 10.4 PR7 implementation note

The first implemented lineage inspection uses the existing tile detail **Inspect evidence** entry point and routes to `/digital-twins/{enterprise_id}/canvas/tiles/{tile_id}/lineage`. The route is read-only, server-side access controlled and presents the lineage chain as accessible headings and ordered lists rather than a graph. Missing Observations, Evidence, Source details or imported package locations are displayed as incomplete lineage, not application errors.

## 11. Lens architecture

The shared Canvas shell supports later lenses.

### Organisation

Formal and practical enterprise structure.

### Outcomes and capabilities

How enterprise resources become service, public value or mission effect.

### Transformation

Programmes, initiatives and current responses.

### Pain and pressure

Current heat, future exposure and unresolved mechanisms.

### Stakeholders

Ownership, influence, affected parties and hot buttons.

### Technology and data

Platforms, data, integrations and control.

### Suppliers and ecosystem

Suppliers, partners, dependencies, rights and route constraints.

### Time and change

Material change, freshness, accountability events and refresh triggers.

Only Organisation is required for Sprint 1. The route and read-model design must not block later lenses.

## 12. Search and filters

Sprint 1 search should cover:

- tile names;
- roles;
- programmes;
- pains;
- stakeholders;
- external stable IDs.

Filters:

- current pressure;
- emerging pressure;
- Unknown;
- Contradiction;
- stale;
- bounded Burning Platform;
- partial import.

Search results must identify whether an item is canonical state, analytical projection or publication.

## 13. Feedback and learning

Available actions:

- challenge displayed statement;
- add labelled human knowledge;
- identify missing context;
- create Evidence request;
- flag possible Contradiction;
- request refresh;
- request nested Twin.

Submission captures:

- user;
- timestamp;
- affected object/projection;
- statement;
- contribution type;
- scope;
- desired action.

It creates candidate knowledge or a work item. No immediate canonical overwrite.

## 14. Empty and partial states

### No tiles mapped

> Flora has received the package, but no organisation mappings are accepted yet.

Actions: inspect import, resolve mapping.

### Tile with no pains

Do not say “no pain”.

Say:

> No material pain is currently mapped to this area in the accepted Twin.

### Partial package

Show:

- imported classes;
- unsupported classes;
- unresolved mappings;
- effect on the Canvas.

### Restricted content

Show access restriction rather than absence.

## 15. Responsive behaviour

Desktop:

- grid Canvas;
- side panel or routed detail;
- persistent filters.

Tablet:

- two-column or single-column grid;
- routed or full-height panel.

Mobile:

- ordered tile list;
- detail as new route;
- preserve semantic hierarchy;
- no horizontal dependency for understanding.

## 16. Accessibility

- Tiles are buttons or links with semantic names.
- Grid order matches reading order.
- State is written in text.
- Keyboard can move, open and close.
- Focus returns to the originating tile.
- Panel has labelled heading and close control.
- Lineage graph has an equivalent ordered list.
- Tooltips are not the only source of information.
- Charts have text summaries.
- Reduced motion is respected.
- Touch targets meet accessible size guidance.

## 17. MOD pilot mapping

The pilot should demonstrate:

### Finance, Affordability and Assurance

Pain headline:

> MOD must prove that planned efficiencies become usable money, time or capacity without weakening Defence outcomes.

### Acquisition and Capability Delivery

Pain headline:

> A formal milestone can be valid while the capability remains restricted, difficult to support or unable to deliver its intended effect.

### Digital, Data and Operational AI

Pain headline:

> A successful AI sprint may not create lasting value unless a receiving organisation owns, funds, monitors and supports the live service.

### Corporate Services

Pain headline:

> A central transformation can report successful delivery while local users inherit more checking, correction and exception handling.

These statements are imported projections and must link to the accepted MOD Twin.

## 18. Sprint 1 scope

### Include

- Enterprise header;
- Organisation Lens;
- six to ten MOD tiles;
- detail panel;
- core facts;
- top pains and pressure;
- current responses;
- unresolved state;
- Unknown and Contradiction indicators;
- lineage summary and detail;
- effective date and freshness;
- search and filters;
- nested-Twin placeholder;
- governed feedback.

### Exclude

- automatic graph layout;
- user-built dashboards;
- personalisation;
- AI-generated screen layouts;
- one-score health ratings;
- Provider Fit;
- pursuit scoring;
- CSM bid workspace;
- cross-enterprise comparison;
- all 51 workbook sheets as direct UI pages.

## 19. Acceptance criteria

The pattern passes when:

1. A cold user can explain MOD's broad structure and three main pressures within five minutes.
2. Each tile is derived from governed state or a registered projection.
3. One click or activation opens role, facts, pains, responses and uncertainty.
4. A displayed judgement reaches source/package lineage in no more than three purposeful interactions.
5. Unknowns and Contradictions are not hidden.
6. No tile or panel creates canonical state directly.
7. Search distinguishes canonical objects, projections and publications.
8. Feedback creates candidate knowledge.
9. The interface works by keyboard and without colour.
10. Partial import and stale states are intelligible.
11. No Provider Fit or pursuit implication appears.
12. User testing records comprehension failures and resulting changes.

## 20. Design handoff checklist

Before implementation:

- confirm tile set and mappings;
- confirm read-model source for each field;
- confirm derivation rule for summary states;
- confirm lineage endpoint;
- confirm feedback workflow;
- confirm access model;
- confirm empty and error states;
- confirm responsive wireframes;
- confirm accessibility annotations;
- confirm analytics events;
- confirm all text uses approved terms.

## 21. Review triggers

Review after:

- first cold-reader test;
- first imported non-MOD enterprise;
- first nested-Twin implementation;
- evidence that tile summaries obscure material distinctions;
- accessibility audit;
- user feedback showing document navigation is still required for basic understanding.

## Sprint 1 PR5 implementation note — Enterprise Canvas read-model foundation

Flora now provides a bounded, read-only Enterprise Canvas service under `cios/applications/flora/enterprise_canvas/`. The first supported lens is the organisation lens. It assembles an enterprise header and deterministic top-level tiles from existing Enterprise Model attributes, Unknown records, Evidence references and Blueprint-import analytical projection candidates.

The Canvas DTOs intentionally prioritise plain-language display fields such as `plain_english_role`, `what_has_been_done_so_far` and `what_remains_unresolved`. Internal references remain available for inspection and lineage, but they are not the primary display language.

Analytical projection candidates such as Pain Points, Burning Platforms, Transformation Pressures, current responses, response-effectiveness views and residual-pain views remain projections. The Canvas may display them with projection type, package or Twin version, effective date, confidence or qualification, status and lineage, but it does not promote them into canonical Enterprise Model object types.

Freshness and uncertainty are represented separately in the header and tiles: effective date, source cut-off, last refreshed date, stale-evidence indicator, Unknown indicator, Contradiction indicator, human-supplied provenance via canonical attributes, and accepted Evidence-backed state remain distinct fields.

Lineage references are preserved from displayed judgement to canonical attribute or analytical projection, Observation IDs, Evidence IDs, Source IDs where known, package reference, import run and package location. The visual lineage explorer and full drill-down panel remain deferred.

## Sprint 1 PR6 implementation note — organisation experience

Flora now exposes the first visible Enterprise Canvas organisation experience at `/digital-twins/{enterprise_id}/canvas`, with tile detail at `/digital-twins/{enterprise_id}/canvas/tiles/{tile_view_id}`. The page is a read-only rendering of the PR5 `EnterpriseCanvasService` DTO: it does not create a new source of truth, does not add canonical writes and does not recalculate organisation intelligence in the view layer.

The implemented organisation lens renders the enterprise header, deterministic read-model tile ordering, separate Unknown, Contradiction, stale-evidence and nested-Twin markers, and a plain-language detail panel with an Inspect evidence entry point. Full lineage exploration, additional lenses, feedback capture and editable Canvas workflows remain deferred.

## 13. Governed Canvas feedback implementation note

Canvas tile detail and lineage inspection views may expose a bounded feedback entry point for authorised users. The control must state that the contribution is stored as candidate human knowledge and does not change the governed Twin until reviewed and accepted.

Supported feedback actions are confirmation, challenge, correction suggestion, context addition, labelled Human-Supplied Knowledge, Unknown candidate, Contradiction candidate, Evidence request and refresh suggestion. Submitted feedback remains workflow state with its own lifecycle and audit history; it is not Evidence, an Observation, an Enterprise Model mutation or a pain-priority change.

Restricted and account-confidential feedback must be filtered server-side using the current enterprise and product-session access patterns. Corrections must supersede earlier feedback by appending a new record or event rather than silently editing the original statement.
