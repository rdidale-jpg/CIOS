# CIOS Enterprise Intelligence Experience Standard v0.1

**Status:** Approved cross-product working standard  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09  
**Authority:** CIOS Reference Architecture, CIOS Design Doctrine, Chief Architect Handbook, ADR-002, ADR-004, ADR-005, ADR-013  
**Applies to:** Flora and future CIOS product surfaces

## 1. Purpose

This standard defines how CIOS presents complex Enterprise Intelligence so that a user can understand, challenge and act without the interface hiding uncertainty, lineage or model boundaries.

The goal is not to display every object.

The goal is:

> Make the enterprise understandable first, then make the intelligence inspectable.

## 2. Experience outcomes

A CIOS experience should help the user answer:

1. What is this enterprise trying to achieve?
2. How is it organised and controlled?
3. What changed?
4. Where are the material pains and pressures?
5. What is the enterprise already doing?
6. Is that response working?
7. What remains unresolved?
8. Who cares and why?
9. What should be validated or done next?
10. Why does CIOS believe this?

## 3. Core principles

### 3.1 Enterprise before artefact

The default experience is organised around the enterprise, not reports, uploads or tables.

Documents remain important lineage and reading assets. They are not the primary model of the enterprise.

### 3.2 Meaning before machinery

State the human conclusion before exposing the analytical taxonomy that produced it.

Use plain language at the first two levels. IDs, classes, confidence mechanics and source registers appear through progressive disclosure.

### 3.3 Model before view

A surface renders governed state. It does not become a competing memory store.

The view may be replaced without losing the underlying intelligence.

### 3.4 Progressive disclosure

Use four levels:

- Level 1 — enterprise orientation;
- Level 2 — area or domain understanding;
- Level 3 — mechanism, programme or pain understanding;
- Level 4 — intelligence and lineage inspection.

### 3.5 Explain before compressing

Concise statements are valuable only when the reader has enough context to understand them.

Every material conclusion should make clear:

- what must be known first;
- how the mechanism works;
- why it matters;
- who experiences the consequence;
- what action follows.

### 3.6 Uncertainty is visible, not buried

Unknowns, Contradictions, stale Evidence, inference and human knowledge must be visible at the point where they affect judgement.

A clean screen must not imply certainty that the model does not possess.

### 3.7 Time is part of the meaning

Display effective date, source cut-off, freshness, material change and upcoming accountability events.

Avoid a single “last updated” label where underlying intelligence has mixed freshness.

### 3.8 Lineage is a user journey

A user should be able to navigate from a judgement to its support.

Lineage is not merely a database field or a link hidden in an audit screen.

### 3.9 Action is proportionate to conviction

Interfaces must not imply Pursue, buy, replace or sell when the supported posture is Learn, Validate, Map, Monitor or Defer.

### 3.10 User input becomes governed candidate knowledge

Feedback, account knowledge and corrections must be labelled and staged. They do not silently overwrite Evidence-backed state.

### 3.11 Simplicity does not mean one score

Do not collapse pressure, urgency, confidence, access, fit or response adequacy into one unexplained indicator.

Simple surfaces may summarise several dimensions if each remains inspectable.

### 3.12 Accessibility is architectural

Accessibility is not a finishing task. It affects navigation, semantics, state communication and trust.

## 4. View hierarchy

### 4.1 Enterprise Overview

Must show:

- enterprise identity and purpose;
- Twin version and effective boundary;
- governing thesis or orientation;
- top-level enterprise structure;
- principal current pressures;
- material recent change;
- current maturity and limitations.

### 4.2 Area View

Must answer:

- what this area does;
- who is accountable;
- what outcomes it affects;
- core facts;
- what is changing;
- principal pains;
- current responses;
- what remains unresolved;
- Unknowns and Contradictions;
- next action.

### 4.3 Mechanism View

Used for pain, programme, value stream, outcome chain or transformation.

Must show:

- mechanism in plain English;
- causes and handoffs;
- actors and decision rights;
- systems and data;
- current controls or response;
- failure modes;
- consequences;
- solution principles;
- proof measures;
- falsification;
- lineage.

### 4.4 Intelligence Inspection

Must show:

- truth class;
- supporting and contrary Evidence;
- Observations;
- source details and exact location;
- effective dates;
- confidence and freshness;
- Unknowns and Contradictions;
- human knowledge;
- original package location;
- relevant decisions and history.

## 5. Content hierarchy

For each material item, present in this order where applicable:

1. plain-English judgement;
2. why it matters;
3. who cares;
4. what is already happening;
5. what remains unresolved;
6. what to ask or do next;
7. supporting detail;
8. lineage and analytical classification.

Do not force the user to infer the conclusion from a table.

## 6. Representation of pains and pressures

A pain card or view should include:

- plain-English statement;
- affected outcome;
- current or future state;
- consequence;
- current response;
- evidence of effectiveness;
- what remains unresolved;
- accountable roles;
- next validation question;
- supporting lineage.

Detailed classification may include:

- pressure, symptom, driver or causal mechanism;
- active, emerging, latent or contingent;
- recognised, contested or unrecognised;
- trajectory;
- Burning Platform or Transformation Pressure;
- enterprise significance;
- commercial accessibility.

The detailed classification should not dominate the first explanation.

## 7. Representation of current responses

Always distinguish:

- announced;
- approved;
- funded;
- contracted;
- mobilised;
- piloted;
- deployed;
- adopted;
- operationally supported;
- benefits evidenced;
- scaled.

The interface must not equate programme existence with effectiveness.

## 8. Evidence and lineage experience

### 8.1 Lineage summary

A material judgement should show a short explanation such as:

- supported by 4 Observations from 3 Sources;
- 1 material Contradiction;
- last material Evidence 42 days ago;
- 2 unresolved Unknowns.

### 8.2 Lineage detail

The user can inspect:

- the exact claim;
- support chain;
- contrary chain;
- source quality;
- source date;
- package location;
- acceptance history.

### 8.3 Broken or incomplete lineage

Display:

- what link is missing;
- how that limits the judgement;
- what Evidence would close the gap.

Never fabricate a complete chain.

## 9. Unknowns and Contradictions

### Unknown marker

Communicate:

- what is unknown;
- why it matters;
- what decision it blocks;
- who may know;
- next collection action.

### Contradiction marker

Communicate:

- the competing claims;
- support for each;
- why both are retained;
- current impact;
- resolution path.

Unknown and Contradiction state must not be represented by colour alone.

## 10. Human-supplied knowledge

Display:

- human-supplied label;
- contributor identity or governed role;
- date;
- scope;
- effect on reasoning;
- validation need.

The experience should make human knowledge useful without presenting it as independent Evidence.

## 11. Time and change

Every major surface should expose:

- Twin effective date;
- source cut-off;
- latest material Observation;
- stale areas;
- change since prior version;
- next accountability event;
- refresh triggers.

A “what changed?” view should distinguish:

- new Evidence;
- new Observation;
- changed Enterprise Model state;
- changed analytical projection;
- publication-only change.

## 12. User actions

Supported action types should be explicit:

- inspect;
- confirm;
- challenge;
- add human knowledge;
- create Unknown;
- flag Contradiction;
- request Evidence;
- monitor;
- validate;
- map;
- open nested Twin;
- propose refresh.

Each action must state whether it changes canonical state, creates candidate knowledge or creates a work item.

## 13. Language standard

### Use

- what MOD has done so far;
- whether it is working;
- what remains unresolved;
- why this matters;
- who must defend or prove the outcome;
- what evidence would change the view.

### Avoid at the first two levels unless explained

- residual pain;
- response-state evidence;
- provider-neutral solution pattern;
- causal maturity;
- analytical disposition;
- supported-service transfer;
- commercial accessibility;
- benefit-to-resource-to-mission lineage.

Technical precision may remain in deeper views and standards.

## 14. Tables and visualisations

A visual must answer a decision question.

For executive-level views:

- state the conclusion before the visual;
- give the visual a message-led title;
- provide a plain-English interpretation;
- do not use a table where prose communicates the point faster;
- do not place the only important judgement inside a table;
- avoid dense IDs and multi-column registers.

## 15. Empty, partial and failure states

### Empty

Explain what has not yet been modelled and the next useful action.

### Partial

State which records or domains are imported and which remain unresolved.

### Stale

State what is old, why it matters and what refresh is needed.

### Contradicted

Show competing claims without forcing false resolution.

### Failed import

Separate package failure from enterprise condition.

### Access restricted

State that intelligence exists but cannot be shown; do not imply absence.

## 16. Accessibility

Minimum requirements:

- WCAG 2.2 AA target;
- keyboard operation;
- visible focus;
- semantic headings and landmarks;
- accessible names for tiles, states and actions;
- sufficient contrast;
- no information conveyed solely by colour;
- readable zoom and responsive reflow;
- textual alternatives for diagrams;
- status announcements for asynchronous operations;
- reduced-motion support;
- no hover-only critical content.

## 17. Comprehension tests

A new informed user should, within five minutes, be able to explain:

- what the enterprise does;
- how it is broadly organised;
- how outcomes are created;
- the principal pressures;
- what the enterprise is doing;
- what remains unresolved;
- where uncertainty exists;
- how to inspect the Evidence.

For every major view ask:

- What must the user already know?
- Has the interface supplied it?
- Is the conclusion visible before the analytical detail?
- Can the user explain the point without CIOS terminology?
- Is the next action proportionate and clear?

## 18. Trust tests

The experience fails if:

- a report or tile becomes hidden canonical memory;
- inference appears as fact;
- human knowledge appears as Evidence;
- an Unknown appears as a negative fact;
- one score hides distinct dimensions;
- programme existence appears as proof of benefit;
- stale data appears current;
- lineage is technically present but practically unreachable;
- a commercial action outruns conviction.

## 19. Product metrics

Useful measures include:

- time to first correct enterprise explanation;
- successful tile-to-lineage navigation;
- percentage of material judgements with complete lineage;
- Unknowns resolved through user action;
- challenged facts converted into governed updates;
- repeated access to nested mechanisms;
- comprehension-test pass rate;
- accessibility defects;
- incorrect inference or overclaim reports.

Do not optimise only for clicks, dwell time or report downloads.

## 20. Standard conformance

A product surface conforms when:

- it renders governed state;
- its primary concepts exist outside the view;
- time and uncertainty are visible;
- material claims are inspectable;
- user feedback is governed;
- accessibility tests pass;
- plain-language comprehension tests pass;
- commercial boundaries remain clear.
