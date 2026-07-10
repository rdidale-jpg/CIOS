# FP-003 — Flora Intelligence Architecture

**Purpose:** Establish the durable intelligence philosophy and architecture for Flora as a CIOS founding capability.
**Status:** draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-10

## Relationship to the CIOS Intelligence Reference Model

The CIOS Intelligence Reference Model (CIRM) defines how CIOS converts observable enterprise reality into strategic commercial judgement. Its canonical pipeline is:

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Observation
→ Strategic Signal
→ Commercial Insight
→ Transformation Theme
→ Transformation Thesis / Hypothesis
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendation
→ Commercial Outcome
→ Continuous Learning
```

FP-003 governs the whole pipeline and establishes the architectural distinction between observation, reasoning, recommendation and learning.

## Transformation Pressure and Transformation Inevitability

**Transformation Pressure** is the internal and external forces that make change more likely or necessary. Internal pressure may include legacy technology, operating cost, service quality, cyber exposure, workforce constraints, fragmented data, delivery failure and technical debt. External pressure may include regulation, political direction, customer expectations, market disruption, competitive moves, supplier change, economic pressure and technology shifts.

**Transformation Inevitability** is the degree to which an enterprise appears structurally compelled to transform, regardless of whether procurement, budget or sponsor evidence is visible. Transformation inevitability is not the same as commercial opportunity: an enterprise may need to transform but still be inaccessible, already committed to another provider, internally constrained or commercially unattractive.

## Commercial Reasoning Loop

```text
Observe
→ Interpret
→ Challenge
→ Hypothesise
→ Test
→ Convict
→ Recommend
→ Learn
→ Observe
```

This loop describes Newton's desired behaviour. Flora should not only collect evidence and generate outputs; it should continually challenge, validate and improve its commercial judgement.

## Inspectable Reasoning Lineage

No recommendation may exist unless its reasoning chain can be inspected:

```text
Executive Recommendation
→ Commercial Conviction
→ Hypothesis / Transformation Thesis
→ Commercial Insight
→ Strategic Signal
→ Observation
→ Raw Evidence
→ Source
```

If any link is missing, the recommendation should be downgraded to a learning action or evidence demand.


## Progressive Assurance and autonomous Twin construction

ADR-009 separates governed Twin construction from formal release production.

### Default fast path

Flora defaults to **Initial Decision Twin** mode. The runtime should:

1. establish the monitored enterprise and decision boundary;
2. collect the highest-yield permissible Evidence;
3. create or update reusable Observations;
4. update only affected Enterprise Model and graph state;
5. form, challenge and bound Hypotheses;
6. identify the most consequential pressures and candidate reinvention seams;
7. propose proportionate learning or commercial actions;
8. run final integrity checks;
9. render the minimum output set.

This is not a reduced reasoning chain. It is a reduced administration and publication chain.

### Research saturation

Research may stop when:

- the leading decision is supported by sufficient independent Evidence;
- material counter-evidence has been considered;
- unresolved gaps are represented as Unknowns, Contradictions or Evidence Demands;
- another collection cycle is unlikely to alter the immediate recommendation materially.

Saturation is assessed against the decision, not against exhaustive source coverage or complete field population.

### Owner interaction

Owner input is conditional rather than a mandatory stage. Flora should request it when account knowledge, provider capability, relationship access or risk authority materially affects the decision. Absence of that input should be represented honestly and should not block an Initial Decision Twin.

### Validation timing

Integrity and publication validation should occur once near completion. Flora should not repeatedly interrupt reasoning for release administration. Machine checks should be silent unless they fail or change the decision boundary.

### Publisher boundary

Flora Publisher renders views over governed Twin state. It does not own Twin memory and must not make formal release packaging a prerequisite for research completion.

### Assured Release promotion

Promotion is explicit. It adds assurance for external publication or consequential action without rebuilding the Twin from scratch. The promoted release must preserve lineage to the Initial Decision Twin and identify what additional evidence, review and acceptance changed.


## Source note

This Markdown version preserves the content and intent of `CIOS_Research_Paper_001_Flora_Intelligence_Architecture_Draft_v0_1.docx` as a clean architecture founding paper for the repository. The uploaded DOCX was not present in the working tree, so this document consolidates the Flora intelligence architecture already represented by the repository's Flora documentation and implementation direction, and extends it into a durable founding paper for the CIOS intelligence model.

## Abstract

Flora is the CIOS intelligence application for identifying organisations where AI-enabled reinvention may be timely, valuable and commercially actionable. Flora should not behave as a generic news summariser, sales-prospecting list, CRM enrichment tool or opaque recommendation engine. Its purpose is to convert governed evidence into explainable commercial judgement: what appears to be changing, why it may matter, what is still unknown, and what action is justified.

The founding belief of Flora is that enterprises continuously emit observable signals before they formally create opportunities. They publish strategies, change leaders, reorganise divisions, invest in platforms, announce partnerships, expose capability gaps, respond to regulation, launch transformation programmes and reveal pressure through their operating behaviour. Commercial advantage comes from detecting, connecting and interpreting those signals before a formal opportunity exists.

CIOS exists to make that judgement systematic, governed, explainable and learnable.

## 1. The intelligence problem

Most enterprise commercial systems begin too late.

Traditional CRM records opportunities after they have been named, qualified or entered into a pipeline. Traditional BI reports information after it has been modelled, aggregated or requested. Traditional AI answers questions after a user has already framed the question. None of these categories is primarily designed to identify the early shape of enterprise transformation before the market has made it explicit.

The intelligence problem for CIOS is therefore not simply information retrieval. It is the disciplined conversion of observable enterprise reality into strategic commercial judgement.

Enterprises continuously emit signals through:

- public announcements, annual reports, investor materials and executive interviews;
- hiring patterns, technology partnerships, cloud migrations and product launches;
- regulatory pressure, security incidents, operating constraints and market shocks;
- organisational redesign, leadership change and transformation language;
- supplier behaviour, procurement posture and ecosystem participation.

These signals are individually incomplete. A single announcement rarely proves budget, urgency, sponsorship or buying intent. However, when governed evidence is normalised, connected and challenged over time, it can reveal transformation pressure, capability gaps and commercially relevant timing.

Flora's role is to help CIOS answer a durable question:

> What enterprise transformation appears to be forming, what evidence supports that judgement, what remains unknown, and what should we do next to learn or act?

## 2. Purpose of CIOS

CIOS is a commercial intelligence operating system for enterprise transformation judgement.

Its category distinction is explicit:

- **Traditional CRM records opportunities.**
- **Traditional BI reports information.**
- **Traditional AI answers questions.**
- **CIOS identifies enterprise transformation before formal opportunities exist.**

This distinction matters because CIOS is not merely a system of record, a dashboard layer or a chat interface. CIOS is intended to become a reasoning system that observes enterprise reality, maintains evidence lineage, forms transformation theses, exposes unknowns, recommends learning actions and improves through feedback.

Flora is the first applied expression of this category: a CIOS intelligence capability focused on finding, explaining and improving commercial judgement about AI-enabled reinvention.

## 3. Architecture thesis

Flora exists to reduce commercial uncertainty. It observes public and governed signals, relates them to transformation pressure, evaluates commercial fit, and produces recommendations that remain traceable to evidence, assumptions, contradictions and constraints.

The architecture is founded on five commitments:

1. **Evidence before opinion** — Flora should distinguish observed facts from hypotheses and recommendations.
2. **Explainability by design** — every score, priority and recommendation should expose its reasoning trail.
3. **Human accountability** — Flora supports executive judgement; it does not replace it.
4. **Governed intelligence** — Flora should prefer legitimate, source-specific and auditable evidence collection.
5. **Institutional learning** — user feedback and case history should improve future recommendations without erasing provenance.

These commitments are philosophical and architectural. They should guide product behaviour, data modelling, agent design, evaluation, user experience and engineering trade-offs.

## 4. How Flora thinks

Flora's cognitive architecture should convert observable enterprise reality into commercial outcomes through a governed reasoning chain:

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Observation
→ Strategic Signal
→ Commercial Insight
→ Transformation Theme
→ Transformation Thesis / Hypothesis
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendation
→ Commercial Outcome
→ Continuous Learning
```

Each stage has a distinct purpose:

1. **Observable Enterprise Reality** — the external facts, events, statements, decisions and conditions emitted by an organisation or its environment.
2. **Governed Source Collection** — the controlled acquisition of evidence from approved, explainable and source-specific locations.
3. **Raw Evidence** — a factual, attributable record of something observed.
4. **Evidence Quality Assessment** — assessment of evidence authority, specificity, freshness, relevance, independence and usefulness.
5. **Observation** — the required memory object created from accepted evidence before higher-order reasoning where an Observation can be created.
6. **Strategic Signals** — commercially meaningful interpretations of Observation-backed evidence that indicate potential enterprise change, pressure or opportunity.
6. **Commercial Insights** — reasoned patterns derived from multiple signals.
7. **Transformation Themes** — recurring categories of enterprise change such as AI transformation, cyber resilience, cloud modernisation, legacy replacement, operating-model change or cost transformation.
8. **Transformation Theses** — coherent, evidence-backed judgements about what may be happening in an enterprise and why it matters commercially.
9. **Hypothesis Validation** — testing discipline used to validate or challenge a transformation interpretation.
10. **Commercial Conviction** — structured judgement that sufficient evidence and reasoning exist to justify a level of commercial action.
11. **Executive Recommendations** — recommended next learning or engagement actions, grounded in the reasoning chain.
12. **Commercial Outcomes** — results of action, feedback or market development that can improve future judgement.
13. **Continuous Learning** — feedback loops that improve future evidence interpretation, thesis quality and recommendation discipline.

The chain is intentionally inspectable. Flora should never jump directly from evidence to recommendation without preserving the intermediate reasoning.

## 5. Intelligence object model

Flora should reason across a small number of durable intelligence objects:

- **Organisation** — the enterprise, public body or target account being assessed.
- **Signal** — an observed event, statement or artefact that may indicate change.
- **Evidence receipt** — the traceable record of where a signal came from and how it was interpreted.
- **Pressure profile** — the set of internal and external forces that may create transformation urgency.
- **Capability gap** — a plausible gap between current state and required future capability.
- **Commercial insight** — interpreted meaning produced by connecting signals, context and commercial logic.
- **Transformation thesis** — a testable belief about a material enterprise transformation that may be forming.
- **Commercial hypothesis** — a narrower testable belief about why engagement may be valuable.
- **Unknown** — a named missing fact, unresolved question, assumption or evidence gap.
- **Contradiction** — evidence that weakens, narrows or challenges a signal, insight or thesis.
- **Recommendation** — an action Flora suggests, with rationale, confidence and caveats.
- **Case file** — a workspace or product view that organises Evidence, Observations, Enterprise Model state, reasoning, unknowns and actions for an organisation; it is not an independent canonical memory store.

These objects should remain conceptually stable even as the implementation changes. Code may introduce different modules, services or storage mechanisms, but it should preserve the reasoning distinction between evidence, signal, insight, thesis, recommendation and outcome.

## 6. Signal architecture and strategic signal standard

Flora should treat signals as structured intelligence assets rather than free text. A signal should have at least:

- source identity;
- organisation;
- signal type;
- evidence tier;
- summary;
- observed date or publication date where available;
- interpretation;
- confidence;
- limitations;
- relationship to scoring, thesis or recommendation logic.

A mature CIOS strategic signal should additionally represent the following standard fields.

### Observation

The neutral statement of what was observed. The observation should avoid commercial overreach and should be separable from interpretation.

### Evidence

The source artefacts, receipts, timestamps, excerpts, metadata or references that support the observation. Evidence should be inspectable and governed.

### Commercial meaning

The interpreted significance of the observation for enterprise transformation, capability gaps, timing, potential value or executive relevance.

### Transformation dimensions

The dimensions of transformation the signal may relate to, such as operating model, AI maturity, cloud maturity, security posture, customer experience, data estate, cost pressure, regulatory response or executive agenda.

### Supports

The theses, insights, hypotheses or recommendations the signal strengthens.

### Does not support

The claims the signal does not justify. This field prevents evidence inflation. A signal may support transformation interest without proving budget, sponsor, procurement route or near-term buying intent.

### Evidence strength

The assessed reliability, specificity, recency and corroboration level of the evidence.

### Unknowns

The missing facts that prevent stronger judgement. Unknowns should be explicit, persistent and actionable.

### Commercial importance

The estimated importance of the signal to commercial prioritisation. Importance should consider value potential, urgency, executive relevance, differentiation and the cost of learning more.

Signals should not automatically become recommendations. They become useful only when combined with sector context, capability logic, executive ownership, commercial fit, contradictions and known evidence gaps.

## 7. Transformation thesis

A **Transformation Thesis** is a structured, testable argument that a material enterprise transformation may be forming, accelerating, weakening or becoming commercially actionable.

It is not a lead, opportunity, sales pitch or generic account summary. It is the bridge between strategic signals and executive engagement.

A transformation thesis should answer:

- What transformation appears to be underway or emerging?
- What enterprise pressures or ambitions seem to be driving it?
- What evidence supports this interpretation?
- What commercial value could be created if the thesis is true?
- What remains unknown or contradictory?
- What should be done next to validate, strengthen, challenge or act on the thesis?

### Building a thesis from signals and insights

A thesis is built by connecting multiple signals into a coherent commercial interpretation. The minimum reasoning path should be:

```text
Raw Evidence → Observation → Strategic Signal → Commercial Insight → Transformation Thesis → Hypothesis Validation → Commercial Conviction → Executive Recommendation
```

A single strong signal may create an early thesis candidate, but a durable thesis should normally require corroboration across different evidence types, time periods or transformation dimensions.

### Evidence thresholds

Thesis strength should increase when evidence is:

- recent;
- source-specific;
- directly attributable;
- corroborated by independent sources;
- connected to executive language or enterprise commitments;
- linked to observable operating or technology change;
- aligned with known pressure in the sector or regulatory environment.

A thesis should remain provisional when evidence is old, generic, indirect, single-source, speculative or disconnected from executive ownership.

### Confidence

Thesis confidence expresses how strongly the evidence supports the thesis. It should not be confused with commercial attractiveness or commercial conviction. A thesis may be well evidenced but commercially unattractive, or commercially attractive but weakly evidenced.

### Contradictions

Contradictions are evidence that weakens, narrows or falsifies a thesis. Flora should preserve contradictions rather than smoothing them away. A contradiction may show that transformation is delayed, ownership has shifted, budgets are constrained, a competing supplier is embedded, or the original interpretation was too broad.

### Unknowns

Unknowns are named missing facts that would materially improve judgement. Examples include sponsor identity, budget existence, procurement route, platform constraints, transformation owner, executive priority, partner landscape and timing.

### Lifecycle

A transformation thesis should remain aligned to the standard CIRM hypothesis lifecycle because theses are validated through testable hypotheses:

1. **Created** — early Strategic Signals suggest a possible transformation interpretation.
2. **Emerging** — multiple signals connect into an interpretable pattern, but coverage and corroboration are incomplete.
3. **Strengthening** — corroborated evidence increases confidence in the thesis and its supporting hypotheses.
4. **Validated** — evidence and commercial context are sufficient for the intended decision context, while assumptions remain visible.
5. **Weakening** — contradictions, ageing evidence or missing expected evidence materially weaken the thesis.
6. **Rejected** — evidence materially disproves the thesis or makes the explanation commercially unreliable.
7. **Retired** — evidence is stale, timing has passed, the thesis has been superseded or it is no longer useful for current reasoning.

### Executive engagement

A thesis supports executive engagement by turning scattered evidence into a disciplined point of view. It should help a human explain why a conversation is timely, what value may be at stake, what CIOS does and does not know, and what the next learning action should be.

## 8. Commercial conviction

CIOS should distinguish three related but different judgements.

### Evidence confidence

Evidence confidence measures how strongly the available evidence supports a signal, insight or thesis. It is about truth, reliability, specificity and corroboration.

### Commercial attractiveness

Commercial attractiveness measures whether the potential transformation appears valuable, strategically relevant and worth attention. It considers market size, urgency, fit, differentiation, value creation and relevance to CIOS capabilities.

### Commercial conviction

Commercial conviction measures whether the case is strong enough to justify a commercial action now. It combines evidence confidence and commercial attractiveness with practical route-to-action factors.

Conviction may remain low even when evidence confidence is high if sponsor, budget, procurement route, executive ownership, timing, partner landscape or internal access remain unknown. Conversely, conviction should not become high merely because an account is attractive. It must be supported by traceable evidence and explicit reasoning.

Commercial conviction should therefore be represented as a judgement with lineage, not as an unexplained score.

## 9. Unknowns as first-class objects

Unknowns, contradictions, missing evidence and assumptions must be explicitly represented. They should not be hidden inside prose, collapsed into a confidence score or omitted from recommendations.

CIOS treats unknowns as commercially valuable because they define the next best learning action. A named unknown can guide research, shape an executive question, prevent overclaiming, reduce wasted pursuit effort or reveal why an apparently attractive account should not yet be prioritised.

Flora should distinguish:

- **Unknowns** — important facts that are not yet known.
- **Contradictions** — evidence that weakens or challenges an interpretation.
- **Missing evidence** — evidence types that would be expected but are absent.
- **Assumptions** — beliefs temporarily used for reasoning that require validation.

Recommendations should include the unknowns they depend on and, where possible, actions that reduce those unknowns.

## 10. Challenge and falsification

Flora should try to disprove its own theses.

Commercial intelligence becomes more valuable when it actively searches for weakening evidence rather than only accumulating confirming evidence. A thesis that survives challenge is more useful than a thesis that has only been supported.

Challenge should include:

- looking for contradictory announcements, delays, budget constraints or strategic pivots;
- testing whether evidence supports a narrower claim than originally assumed;
- identifying alternative explanations for the same signals;
- checking whether signals are stale, generic, marketing-led or non-specific;
- separating transformation interest from buying intent;
- asking what evidence would cause the thesis to be downgraded or retired.

This function may eventually be performed by a specialist Challenge Agent, but the principle applies to the whole architecture.

## 11. Enterprise DNA

Enterprise DNA is retained as a historical and descriptive term for a view over relatively stable Enterprise Model attributes. It is not a second canonical memory store. The Enterprise Model / Commercial Digital Twin owns durable enterprise state; Enterprise DNA describes the structural characteristics within that model that shape how signals should be interpreted and how transformation may happen.

Flora should represent Enterprise DNA-like context through the Enterprise Model across at least these dimensions:

- **Business Model** — how the enterprise creates, delivers and captures value.
- **Technology Estate** — major platforms, legacy systems, data architecture and integration constraints.
- **Cloud Maturity** — cloud adoption, migration posture, operating model and platform dependency.
- **AI Maturity** — AI experimentation, production adoption, governance, skills and use-case maturity.
- **Security Posture** — cyber risk, resilience needs, regulatory exposure and trust requirements.
- **Operating Model** — organisational design, delivery model, process maturity and transformation capacity.
- **Executive Structure** — leadership roles, ownership patterns, sponsors and decision forums.
- **Commercial Behaviour** — buying patterns, partnership preferences, procurement posture and investment style.
- **Supplier Ecosystem** — strategic vendors, consultancies, cloud providers, system integrators and incumbent relationships.
- **Regulatory Environment** — legal, compliance, sector and jurisdictional pressures.
- **Transformation Readiness** — ability to absorb change, execute programmes and sustain adoption.
- **Innovation Appetite** — willingness to experiment, partner, modernise and adopt emerging capabilities.
- **Risk Appetite** — tolerance for operational, financial, reputational, security and delivery risk.

Enterprise DNA prevents Flora from interpreting every signal the same way. The same AI announcement may mean different things for a regulated bank, retailer, manufacturer, public body or technology platform company.

## 12. Temporal intelligence

Commercial intelligence is temporal. Signals age, strengthen, weaken and expire. Momentum changes. Transformation windows open and close.

Flora should reason about time explicitly:

- **Signals age** when their observed date moves further from the current decision point.
- **Signals strengthen** when later evidence corroborates or extends them.
- **Signals weaken** when no follow-up evidence appears, when priorities change or when contradictions emerge.
- **Signals expire** when the decision window has passed or the evidence no longer informs current judgement.
- **Momentum changes** when evidence frequency, executive language, funding, hiring or programme activity accelerates or slows.
- **Transformation windows open and close** as regulation, budget cycles, leadership transitions, incidents, platform migrations or competitive shocks change the cost and value of action.

Temporal intelligence should influence thesis lifecycle, commercial conviction and recommendation timing. A correct recommendation at the wrong time may still be commercially poor.

## 13. Commercial intelligence loop

CIOS should operate through a continuous commercial intelligence loop:

```text
Observe
→ Understand
→ Hypothesise
→ Challenge
→ Recommend
→ Act
→ Learn
→ Observe
```

The loop is not a linear sales process. It is an institutional learning cycle.

- **Observe** enterprise reality through governed sources.
- **Understand** evidence in context using Enterprise Model context and sector logic.
- **Hypothesise** about transformation pressure and commercial meaning.
- **Challenge** the hypothesis through contradiction, falsification and unknowns.
- **Recommend** the next action that is justified by the reasoning.
- **Act** through research, engagement, disqualification or further validation.
- **Learn** from outcomes, user feedback and changed evidence.
- **Observe** again with improved context.

Recommendations should often maximise learning before selling. The best next action may be to validate a sponsor, test an assumption, find contradictory evidence or wait for a stronger signal.

## 14. Intelligence agents

Future Flora capabilities may be expressed through specialist intelligence agents. These agents are architectural roles, not necessarily separate deployed services yet. A single codebase, workflow or model may perform multiple roles until the architecture justifies separation.

Potential agent roles include:

- **Research Agent** — collects or receives governed evidence from approved sources.
- **Evidence Agent** — records provenance, source quality, timestamps, limitations and evidence receipts.
- **Signal Agent** — classifies evidence into structured strategic signals.
- **Insight Agent** — connects Observation-backed signals with Enterprise Model context, sector context and capability logic.
- **Thesis Agent** — builds, updates and manages transformation theses.
- **Challenge Agent** — searches for contradictions, weakening evidence and alternative explanations.
- **Recommendation Agent** — proposes next actions with rationale, caveats and learning objectives.
- **Learning Agent** — incorporates feedback, outcomes and case history without erasing provenance.

Agent design should preserve inspectable reasoning lineage. Agents should not create opaque handoffs where evidence, assumptions or confidence disappear.

## 15. Reasoning flow

Flora's default reasoning flow should be:

1. Collect or load governed evidence.
2. Preserve evidence receipts and source context.
3. Convert accepted evidence into Observations.
4. Classify Observations into strategic signals.
5. Normalise signals into the strategic signal standard.
6. Assess transformation pressure and commercial relevance.
7. Identify capability themes and possible executive owners.
8. Compare evidence strength against unknowns and contradictions.
9. Generate or update transformation theses.
10. Challenge theses through falsification and alternative explanations.
11. Generate ranked opportunities, attention items or learning actions.
12. Explain why Flora believes each item matters.
13. State what Flora cannot yet know.
14. Recommend next actions that a human can validate.
15. Capture feedback and outcomes as governed learning and product-view updates over canonical memory.

## 16. Explainability requirements

Flora outputs should expose:

- the evidence used;
- the signal types contributing to a view;
- score or ranking rationale;
- confidence and uncertainty;
- assumptions;
- contradictions;
- missing evidence;
- unknowns;
- thesis lifecycle state;
- recommended validation steps.

Where evidence is seeded, simulated or limited to a pilot source set, Flora must label it visibly.

No recommendation should exist without inspectable reasoning lineage from evidence to signal, insight, thesis, commercial argument and recommended action.

## 17. Governance and constraints

Flora must avoid unsupported claims about private intent, budget, procurement, sponsorship or competitor engagement. Public evidence may justify hypotheses, but it does not prove internal decision-making.

Flora should avoid broad crawling and should respect source-specific access policies. Where live evidence is unavailable, deterministic seeded evidence may be used for local validation if clearly labelled.

Governance should also maintain the relationship between founding philosophy, architecture and implementation:

- **Founding Papers explain why CIOS thinks this way.**
- **Architecture docs explain how capabilities are designed.**
- **ADRs explain why major decisions were made.**
- **Code implements these ideas.**

This paper should therefore guide future engineering decisions without pretending to be the runtime specification for every current component.

## 18. Product surfaces

Flora may express the same intelligence architecture through multiple product surfaces:

- daily or weekly intelligence briefs;
- executive brief publications;
- portfolio radar views;
- living commercial case files;
- observatory views;
- thesis workbenches;
- unknowns and contradiction queues;
- teach-Flora feedback loops.

These surfaces should remain consistent with the same evidence, reasoning and governance model. A user should be able to move from a recommendation back to the evidence, Observation, signal, insight, thesis and unknowns that produced it.

## 19. Relationship to CIOS

Flora is not a standalone application in architectural terms. It is an applied expression of CIOS principles:

- commercial ontology;
- commercial knowledge graph concepts;
- commercial reasoning language;
- commercial decision engine;
- agent-supported analysis;
- learning and memory.

Flora should therefore create reusable knowledge assets rather than isolated outputs. Its evidence receipts, Observations, signals, Enterprise Model context, theses, contradictions, unknowns, recommendations and outcomes should become part of the wider CIOS intelligence substrate.

## 20. Laws of commercial intelligence

CIOS should preserve the following laws as durable design constraints:

1. **Evidence precedes judgement.**
2. **Judgement without traceability is opinion.**
3. **Commercial confidence grows through corroboration.**
4. **Recommendations should maximise learning before selling.**
5. **Unknowns have commercial value.**
6. **No recommendation should exist without inspectable reasoning lineage.**

These laws should be used to evaluate product features, agent behaviour, scoring models, user interfaces and future architecture proposals.

## 21. Future expansion

Future versions should expand:

- live governed evidence coverage;
- sector and capability playbooks;
- executive ownership models;
- recommendation validation workflows;
- formal thesis lifecycle management;
- contradiction and unknown management;
- temporal scoring and signal expiry;
- learning from user feedback;
- architecture-level traceability from founding papers to runtime behaviour.

## 22. Open questions

- Which signal categories should be promoted to formal CIOS standards?
- What minimum evidence threshold is required before Flora recommends action?
- How should human feedback alter confidence without compromising provenance?
- Which recommendations require ADR-level governance before implementation?
- Which thesis lifecycle transitions should be automated and which require human judgement?
- How should CIOS measure whether recommendations improve learning before selling?
- What evidence is sufficient to infer executive ownership without overclaiming?

## 23. Closing vision

CIOS exists to convert observable enterprise reality into strategic commercial judgement. Every feature, model and agent should make that judgement more accurate, more explainable and more valuable.

## Relationship to CIRM

This paper governs the overall intelligence architecture of CIRM. It explains how Flora connects the whole model from observable enterprise reality through evidence, signals, insights, theses, conviction, recommendations, outcomes and learning, with FP-004 to FP-009 defining the specialised controls within that chain.
