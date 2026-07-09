# ADR-013 — Enterprise Canvas as the Primary Living Twin Navigation Model

**Status:** Accepted  
**Decision date:** 2026-07-09  
**Owner:** Rob / CIOS  
**Decision class:** Product surface and cross-cutting experience architecture  
**Supersedes:** None  
**Related decisions:** ADR-002, ADR-004, ADR-005, ADR-012

## Context

Once a Commercial Digital Twin is maintained in Flora, its representation becomes a core part of the product’s value.

A document library, workbook viewer or generic dashboard would make the imported intelligence accessible but would not make a complex enterprise understandable. Users need to see how the enterprise is organised, what each part does, what is changing, where pain and pressure sit, what is already being done and what remains unresolved.

The interface must remain simple without hiding:

- Evidence and reasoning lineage;
- effective dates and freshness;
- Unknowns and Contradictions;
- the distinction between current fact, inference, analytical view and Recommendation;
- the distinction between enterprise significance and commercial accessibility.

A tile-based enterprise view is a useful entry point, but a tile must not become a new canonical intelligence object or an attractive substitute for durable state.

## Decision

### 1. Flora starts with the enterprise, not the document set

The primary navigation for a Living Commercial Digital Twin is an Enterprise Canvas.

The Canvas presents an understandable visual model of the enterprise and its material domains, units, programmes or capabilities. Imported files remain available for inspection but are not the default organising metaphor.

### 2. The Enterprise Canvas is a view

The Canvas and its Intelligence Tiles render existing governed state, including:

- Enterprise Model entities and attributes;
- organisational units;
- programmes;
- capabilities;
- relationships;
- nested Twins;
- versioned Analytical Projections.

An Intelligence Tile is not a canonical Enterprise Intelligence object.

### 3. Organisation is the default lens, not the only lens

Sprint 1 begins with an Organisation Lens.

The architecture supports further lenses over the same Twin:

- outcomes and capabilities;
- transformation;
- pain and pressure;
- stakeholders;
- technology and data;
- suppliers and ecosystem;
- time and change.

Changing lens must not create competing enterprise facts.

### 4. Progressive disclosure governs complexity

The experience uses four levels:

1. **Enterprise understanding** — Canvas and headline state.
2. **Area understanding** — Intelligence Detail Panel for a tile.
3. **Mechanism understanding** — pain, programme, value stream or causal flow.
4. **Intelligence inspection** — Observations, Evidence, source, confidence, Unknowns, Contradictions and original package location.

Users do not need Level 4 to understand Level 1, but material judgements must remain inspectable.

### 5. Every tile answers why the user should care

A tile should normally show:

- recognisable name;
- role or purpose;
- accountable role where known;
- current state;
- principal pain or pressure;
- material recent change;
- attention markers;
- nested-Twin availability.

It must not attempt to display every associated object or score.

### 6. Tile drill-down is decision-first

The first detail view explains:

1. what this area does;
2. core facts;
3. what is changing;
4. principal pains and pressures;
5. current responses;
6. what remains unresolved;
7. stakeholders and hot buttons;
8. Unknowns and Contradictions;
9. appropriate next action;
10. how to inspect lineage.

Internal IDs and taxonomies must not dominate the first two levels.

### 7. Time, uncertainty and provenance are visible

Material views must expose:

- Twin effective date;
- source cut-off;
- last refresh;
- mixed freshness where relevant;
- upcoming accountability events;
- Unknowns;
- Contradictions;
- human-supplied knowledge;
- stale or weak Evidence.

Colour alone must not carry these meanings.

### 8. Lineage is reachable without leaving the product

From a material displayed judgement, a user should be able to reach:

`displayed judgement → analytical projection or hypothesis → Observation → Evidence → Source → original package location`

in no more than three purposeful interactions for the Sprint 1 design.

### 9. The experience may improve the Twin but cannot silently overwrite it

Users may:

- confirm or challenge a fact;
- add labelled human knowledge;
- create an Unknown;
- request Evidence;
- flag a Contradiction;
- propose a refresh;
- open a nested Twin request.

These actions create governed candidate updates or work items. They do not directly overwrite Evidence-backed canonical state.

### 10. Avoid false simplicity

The Canvas must not collapse enterprise condition into one unexplained score.

Pain markers must distinguish, where available:

- current versus future;
- pressure, symptom or causal mechanism;
- current response;
- effectiveness;
- unresolved consequence;
- enterprise significance;
- commercial accessibility.

The first view uses plain language; deeper classification is progressively disclosed.

### 11. Accessibility and comprehension are acceptance criteria

The Canvas must:

- work without relying solely on colour or hover;
- support keyboard navigation;
- use readable text at supported sizes;
- provide semantic names and states;
- make focus and selection visible;
- preserve the reading order on smaller screens;
- provide textual equivalents for visual relationships.

A new informed user should be able to explain the enterprise, its main pressures and current responses after a short guided exploration.

## Decision rationale

The Canvas is differentiated not because it uses tiles, but because each tile is a doorway into maintained, time-aware and evidence-linked Enterprise Intelligence.

This preserves the CIOS principle:

> simple surface; strong model; progressive disclosure; inspectable depth.

## Alternatives considered

### Document library as the primary interface

Rejected. It organises artefacts rather than the enterprise.

### Static organisation chart

Rejected as the whole experience. It cannot represent cross-boundary programmes, pains, outcomes, suppliers or transformation.

### Knowledge graph as the default view

Deferred. Graphs are useful for mechanism inspection but can overwhelm first-time users and encourage layout complexity before comprehension is proven.

### Dashboard of scores and KPIs

Rejected as the primary navigation. It risks hiding lineage, blending distinct states and presenting missing evidence as measured condition.

### Fully generated AI interface

Deferred. A dynamic assistant may augment the experience, but governed and testable navigation must exist without relying on generated layout or unsupported summaries.

## Consequences

### Positive

- A complex Twin becomes understandable within minutes.
- Users navigate by enterprise meaning rather than file structure.
- The same durable state can support several lenses.
- Lineage and uncertainty remain available without overwhelming the first view.
- Nested programme Twins such as CSM have a natural entry point.
- User challenges can become governed learning.

### Costs and constraints

- A read model or projection layer is required.
- Tile composition rules must be deterministic and testable.
- Multiple lenses increase later design complexity.
- Accessibility requires deliberate implementation.
- Some package content will not be representable until canonical or projection mappings exist.

## Runtime implications

Flora Sprint 1 must implement a bounded slice:

- enterprise header and Twin status;
- Organisation Lens;
- six to ten top-level Intelligence Tiles for the MOD pilot;
- Intelligence Detail Panel;
- core facts;
- pain and pressure summary;
- current response and unresolved state;
- Unknown and Contradiction indicators;
- Evidence and lineage inspection;
- effective date and freshness;
- search and basic filtering;
- nested-Twin placeholder;
- governed feedback submission.

## Affected documents

- CIOS Reference Architecture v1.0
- CIOS Reference Architecture Glossary
- CIOS Architecture Document Map
- CIOS Enterprise Intelligence Experience Standard v0.1
- Flora Enterprise Canvas and Drill-Down Pattern v0.1
- Flora Governed Blueprint Import Runtime Specification v0.1

No new EI canonical object is introduced by this ADR.

## Validation

The decision is implemented correctly when:

- the default experience is organised around the enterprise rather than files;
- tiles render governed state;
- switching view does not create conflicting facts;
- a user can understand a tile before seeing internal IDs;
- Unknowns, Contradictions and freshness are visible;
- a material judgement can be traced to its Evidence and package location;
- feedback creates candidate knowledge rather than silent mutation;
- keyboard and non-colour interaction paths work;
- a five-minute comprehension test passes for an informed cold reader.

## Architecture debt and deferrals

- Additional lenses beyond Organisation are deferred.
- Automated graph layout is deferred.
- Configurable dashboards are deferred.
- Personalised role-based canvases are deferred.
- Opportunity and pursuit scoring are excluded.
- Full nested-Twin navigation is deferred to the CSM programme sprint.

## Review and supersession conditions

Revisit this decision when:

- users consistently prefer another primary navigation model;
- more than one enterprise type cannot be represented coherently;
- the Canvas begins inventing meaning not present in governed state;
- cross-enterprise Observatory navigation requires a different primary metaphor;
- accessibility or performance constraints make the current pattern unsuitable.
