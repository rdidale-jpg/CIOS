# EI-012 — Enterprise Observation Model

**Purpose:** Define the Observation as the atomic unit of Enterprise Intelligence.
**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons. The Enterprise Observation Model defines the intelligence primitive that sits between Evidence Acquisition and Commercial Reasoning.

Evidence supports Observations. Observations update the Enterprise Model. Observations support Strategic Signals. Signals support Hypotheses. Hypotheses support Commercial Theses. Commercial Theses support Recommendations.

This creates the core intelligence chain:

```text
Evidence → Observation → Strategic Signal → Hypothesis → Commercial Thesis → Recommendation
```

## Purpose

CIOS should not reason directly over raw documents, scrape fragments or isolated snippets when a structured intelligence primitive can be created. Raw evidence is necessary, but it is not sufficient memory.

CIOS should reason over structured Observations that are:

- atomic;
- evidence-backed;
- time-aware;
- reusable;
- explainable;
- commercially relevant;
- independent of any single report.

The Observation is therefore the smallest reusable unit of Enterprise Intelligence: a durable statement about what changed, what condition exists, what relationship matters, what absence is notable or what contradiction has emerged.

# Observation Doctrine

> "The purpose of Enterprise Intelligence is to detect meaningful change.
>
> Evidence proves change.
>
> Observations remember change.
>
> The Enterprise Model accumulates change.
>
> Commercial reasoning explains change.
>
> Recommendations propose how to act on change."

CIOS does not exist to collect documents. CIOS exists to detect meaningful enterprise change and preserve that change as durable intelligence. Documents are carriers of evidence, not the intelligence product itself. They may be revised, removed, superseded, duplicated, syndicated, reformatted or forgotten; an Observation survives because it records the enterprise fact, condition, movement, absence or contradiction that the document made visible.

This doctrine makes Observations the enduring memory layer of Enterprise Intelligence:

- documents are transient evidence containers;
- evidence proves that something was stated, published, filed, awarded, appointed, reported or omitted;
- Observations convert evidence into durable enterprise memory;
- Enterprise Models accumulate Observations as structured state change;
- reports render selected Observations for a moment, audience or decision;
- Commercial Digital Twins become more useful as their Observation memory deepens.

A report is therefore never the source of truth. A report is a view over selected Observations, Signals, Hypotheses, Commercial Theses and Recommendations. If the report disappears, the Enterprise Model should still remember the Observations that mattered. If Flora is rewritten, the Observation doctrine should remain valid because it describes the intelligence philosophy rather than an implementation detail.

## Why observations exist

Evidence, Observation, Signal, Hypothesis and Recommendation answer different questions.

Evidence:
Annual report says “operating costs increased by 8%.”

Observation:
Operating cost pressure increased.

Signal:
Cost pressure may be creating a need for operating-model transformation.

Hypothesis:
Enterprise may pursue automation or service redesign to reduce operating cost.

Recommendation:
Validate the cost pressure and ownership with CFO / COO.

Observations prevent Flora from jumping from document snippets to commercial conclusions. They force the system to preserve a structured memory layer between evidence and reasoning, so that commercial judgement can be inspected, reused, challenged and improved.

## Observation pipeline

The canonical pipeline is:

```text
Source
→ Evidence
→ Observation
→ Strategic Signal
→ Pattern
→ Hypothesis
→ Commercial Thesis
→ Recommendation
```

- **Source:** The origin of potentially useful enterprise information, such as an annual report, procurement notice, regulatory filing, job advert, executive statement or trusted human input.
- **Evidence:** A collected, attributable record of what was published, stated, observed or supplied.
- **Observation:** A structured, evidence-backed statement describing a meaningful enterprise change, condition, relationship, absence or contradiction.
- **Strategic Signal:** A commercially meaningful interpretation indicating possible pressure, behaviour, risk, opportunity or timing.
- **Pattern:** A cluster of related observations and signals that suggests a recurring enterprise condition or trajectory.
- **Hypothesis:** A testable interpretation about what may be happening and why it matters commercially.
- **Commercial Thesis:** A reasoned commercial judgement about enterprise need, likely action, timing and relevance.
- **Recommendation:** A proposed next action, validation step or engagement move.

## Definition of an Observation

An Observation is a structured statement describing a meaningful change, condition, relationship, absence or contradiction about an enterprise, supported by one or more evidence objects.

Observation types include:

- Change
- Condition
- Event
- Relationship
- Absence
- Contradiction
- Trend
- Anomaly
- Confirmation
- Weakening

## Observation principles

Observations must be:

- **Atomic:** one observation should express one meaningful fact or change.
- **Evidence-backed:** every observation should reference evidence or be explicitly human-supplied.
- **Time-aware:** observations have observation date, evidence date and collection date.
- **Reusable:** the same observation can support multiple signals or hypotheses.
- **Explainable:** a human can inspect why the observation exists.
- **Non-duplicative:** repeated evidence should strengthen the same observation, not create noisy duplicates.
- **Commercially relevant:** observations should improve understanding of pressure, behaviour, opportunity, risk or timing.
- **Separate from narrative:** observations are not executive prose.

# The Laws of Observation

These laws govern how Observations are created, interpreted, reused and challenged. They are architectural constraints, not interface preferences.

## Law 1 — One Observation represents exactly one meaningful enterprise fact

**Purpose:** Keep Observations atomic so each one can be independently validated, contradicted, reused, aged and retired. Never combine unrelated changes.

**Commercial rationale:** Commercial reasoning becomes auditable only when each reasoning step can be traced to a single enterprise fact. Combining a CFO change, a cost programme and a cloud migration in one Observation makes it impossible to know which fact supports which conclusion.

**Example:** "New CIO appointed" is one Observation. "New CIO appointed and enterprise likely to modernise ERP" combines fact and speculation and must be split.

## Law 2 — Observations never speculate

**Purpose:** Preserve the boundary between what is known and what may be inferred. Speculation belongs in Hypotheses.

**Commercial rationale:** Separating observed fact from interpretation prevents premature conviction and lets competing hypotheses reuse the same evidence-backed memory.

**Example:** "Cloud migration programme announced" is an Observation. "Cloud migration will reduce supplier spend" is a Hypothesis.

## Law 3 — Observations never contain recommendations

**Purpose:** Keep action proposals separate from intelligence memory. Recommendations are separate reasoning objects.

**Commercial rationale:** An Observation may support several possible engagement moves; embedding a recommendation inside it makes the intelligence less reusable and harder to challenge.

**Example:** "Procurement notice issued for data platform services" is an Observation. "Contact the CIO this week" is a Recommendation.

## Law 4 — Every Observation must update the Enterprise Model

**Purpose:** Ensure Observations change durable enterprise state. If it changes nothing, it should not exist.

**Commercial rationale:** The Enterprise Model is the memory of the Commercial Digital Twin. Observations that do not update state create noise, cost and false analytical activity.

**Example:** A repeated syndicated copy of the same press release should strengthen source lineage on an existing Observation, not create a new one.

## Law 5 — Every Observation must have commercial relevance

**Purpose:** Reject facts that do not improve understanding of pressure, behaviour, timing, opportunity, risk, relationship or transformation.

**Commercial rationale:** Enterprise Intelligence is not trivia collection. Commercial relevance focuses collection and reasoning on intelligence that can improve decisions.

**Example:** "Annual report PDF file size changed" is normally noise. "Annual report introduces a new cost reduction target" is commercially relevant.

## Law 6 — Observations strengthen or weaken understanding

**Purpose:** Treat Observations as contributors to judgement, not guarantees of conclusions.

**Commercial rationale:** Enterprise reality is uncertain. Commercial conviction should grow through accumulating, corroborating and contradicting Observations rather than single-fact certainty.

**Example:** A hiring spike in data engineers strengthens the view that data capability is expanding; it does not prove an enterprise-wide AI transformation.

## Law 7 — Confidence belongs to Observations

**Purpose:** Assign belief to the derived Observation, not only to source evidence. Evidence quality informs confidence but does not determine commercial significance.

**Commercial rationale:** A reliable source can produce a low-significance Observation, and a single modest source can reveal a commercially important change requiring validation.

**Example:** A statutory filing may prove an address change with 100% confidence but little commercial value; a job advert for a transformation director may be lower-confidence but commercially important.

## Law 8 — Observations persist beyond documents

**Purpose:** Preserve enterprise memory after documents disappear, expire or become inaccessible. Documents disappear. Enterprise memory remains.

**Commercial rationale:** Commercial Digital Twins need continuity. Durable Observation memory lets CIOS reason across time rather than repeatedly rediscovering the same enterprise facts.

**Example:** A procurement notice may close after 30 days, but the Observation that a cloud migration procurement occurred remains relevant to supplier landscape and transformation history.

## Law 9 — Observations may support multiple Signals and Hypotheses

**Purpose:** Make Observations reusable across reasoning pathways.

**Commercial rationale:** The same enterprise fact can matter to cost, risk, relationship, timing and opportunity. Reuse increases intelligence leverage and avoids duplicative analysis.

**Example:** "New CIO appointed" may support signals about leadership change, technology strategy reset, supplier review and executive conversation timing.

## Law 10 — Contradictory Observations must coexist until resolved

**Purpose:** Preserve conflicting intelligence instead of overwriting it. Never overwrite conflicting intelligence.

**Commercial rationale:** Contradiction is often the first sign of ambiguity, transition or contested strategy. Keeping contradictions visible prevents false certainty.

**Example:** One source says ERP replacement is delayed while another says mobilisation has begun. Both Observations coexist until validated, dated, scoped or resolved.

# Observation Importance

Observation Importance measures enterprise impact: how materially the Observation changes understanding of the enterprise if true. It is separate from Confidence, Freshness, Quality and Commercial Value.

- **Confidence** measures belief that the Observation is true.
- **Freshness** measures temporal recency and current relevance.
- **Quality** measures evidence and construction strength.
- **Commercial Value** measures usefulness for commercial reasoning.
- **Importance** measures enterprise impact.

Importance levels are:

- **Critical:** materially changes strategic understanding, executive engagement, transformation pressure or opportunity outlook. Example: "ERP replacement programme approved."
- **Major:** significantly changes an important area of the Enterprise Model. Example: "New CIO appointed."
- **Moderate:** useful change in a relevant domain but not enterprise-defining alone. Example: "Cyber hiring increased."
- **Minor:** small but valid state update. Example: "Technology committee membership updated."
- **Context:** background that helps interpretation but rarely changes decisions alone. Example: "Annual report published."
- **Noise:** true or plausible information that does not improve enterprise understanding. Example: "Website banner image changed."

These dimensions are independent. A Critical Observation may begin with low Confidence and demand validation. A 100% confident Observation may have only Context importance. A fresh Observation may still be commercially irrelevant.

# Observation Commercial Value

Commercial Value answers: **"If true, how much better does this help us understand the enterprise?"**

Suggested dimensions are:

- **Commercial usefulness:** Does it improve understanding of need, timing, budget, route to market or buying motion?
- **Transformation usefulness:** Does it clarify transformation pressure, maturity, direction or blockers?
- **Relationship usefulness:** Does it reveal sponsors, influencers, incumbents, advisers or partnerships?
- **Opportunity usefulness:** Does it change opportunity probability, qualification, route or urgency?
- **Strategic usefulness:** Does it improve understanding of enterprise direction or competitive posture?
- **Executive usefulness:** Does it help create a better executive conversation?
- **Overall Commercial Value:** The combined usefulness of the Observation for commercial reasoning.

An Observation may be perfectly true but commercially insignificant.

Example:

- Observation: "Annual report published."
- Confidence: 100%.
- Commercial Value: Very Low.

Example:

- Observation: "New CIO appointed."
- Confidence: 95%.
- Commercial Value: Very High.

# Observation Actionability

Actionability records what, if anything, the system should do because the Observation exists. Every Observation should indicate whether it requires:

- No action
- Monitor
- Validate
- Collect evidence
- Generate questions
- Update Enterprise Model
- Recalculate Transformation Pressure
- Recalculate Opportunity Outlook
- Prepare Executive Conversation

Actionability differs from Commercial Value. Commercial Value describes how useful the Observation is for understanding the enterprise. Actionability describes the operational or reasoning response required now. A high-value Observation may require only monitoring if it is already validated; a moderate-value contradiction may require immediate evidence collection because it blocks a decision.

# Observation Demand

Observation Demand is the follow-on intelligence need created by an Observation. Some Observations automatically create demand for further Observations because they expose unknowns, likely consequences or missing context.

Example:

Observation: New CIO appointed.

Automatically generated evidence demand:

- Has strategy changed?
- Has supplier landscape changed?
- Has technology roadmap changed?
- Has AI strategy changed?
- Has procurement activity changed?
- Has executive committee changed?

Observation Demand becomes one of the inputs to the Curiosity Engine. It tells CIOS what it should want to know next because the Enterprise Model has changed.

# Observation Question Generation

Every Observation should generate investigative questions. Questions convert observed change into a structured search for missing context and should eventually feed EI-015 Enterprise Question Model.

## Cloud Migration example

Observation: Cloud migration announced.

Questions:

- Budget?
- Supplier?
- Timeline?
- Programme?
- Executive Sponsor?
- Business Units?
- Target Architecture?
- Legacy Replacement?

## ERP Replacement example

Observation: ERP replacement indicated.

Questions:

- Business Case?
- Programme Director?
- Delivery Partner?
- Funding?
- Change Requests?
- Customer Impact?

## Cyber Investment example

Observation: Cyber investment increased.

Questions:

- Trigger event?
- Regulatory driver?
- CISO sponsor?
- Current controls?
- Procurement route?
- Managed service partner?
- Board-level risk appetite?

## Observation categories

### Enterprise Strategy observations

Enterprise Strategy observations describe changes in declared direction, strategic priorities, portfolio choices or market positioning. They help CIOS understand where leadership says the enterprise is going and whether that direction creates transformation pressure or opportunity.

Examples:

- Strategy updated.
- AI becomes strategic priority.
- Cost reduction target increased.
- Market exit announced.
- Expansion announced.
- Business model repositioning detected.

### Financial observations

Financial observations describe changes in enterprise performance, economics, investment capacity, cost pressure or unit-level financial health. They help CIOS connect commercial reasoning to pressure, affordability, urgency and constraints.

Examples:

- Revenue slowed.
- Margin deteriorated.
- Operating costs increased.
- Debt rose.
- Capex increased.
- Capex reduced.
- Cash flow improved.
- Business unit underperformed.
- Cost reduction target announced.

### Executive observations

Executive observations describe leadership changes, sponsor signals, governance structures and public leadership emphasis. They help CIOS identify who may own change and whether executive attention is shifting.

Examples:

- New CIO appointed.
- CFO changed.
- COO departure announced.
- Board reshuffle occurred.
- Technology committee formed.
- Transformation sponsor changed.
- Executive publicly emphasised productivity / AI / cyber / cost.

### Technology observations

Technology observations describe platform choices, digital programmes, security posture, data capability, AI governance and technology modernisation. They help CIOS identify transformation state and likely technology pathways.

Examples:

- Oracle adopted.
- SAP programme extended.
- Cloud migration announced.
- Data platform expanded.
- AI governance introduced.
- Legacy retirement announced.
- Cyber investment increased.
- Zero Trust programme launched.

### Operating Model observations

Operating Model observations describe how work, accountability, service delivery and organisational structures are changing. They help CIOS detect transformation pressure that may not yet appear as procurement demand.

Examples:

- Shared services expanded.
- Contact centres consolidated.
- Field workforce restructured.
- Business unit merged.
- Operating model decentralised.
- Outsourcing increased.
- Insourcing announced.

### Commercial / Procurement observations

Commercial / Procurement observations describe visible buying activity, supplier movement, contract timing and commercial routes. They help CIOS connect enterprise need to accessible opportunity.

Examples:

- Procurement published.
- PIN issued.
- Framework used.
- Supplier replaced.
- Contract extended.
- Incumbent retained.
- Award notice published.
- Contract expiry approaching.
- Supplier spend increased.
- Supplier spend declined.

### People and workforce observations

People and workforce observations describe labour demand, workforce constraints, capability building, sentiment and employee relations. They help CIOS understand whether transformation is being pulled by skills, capacity, industrial relations or workforce redesign.

Examples:

- AI recruitment increased.
- Cyber hiring increased.
- Hiring freeze announced.
- Redundancy programme announced.
- Skills shortage evidenced.
- Graduate programme launched.
- Union pressure increased.
- Public workforce sentiment weakened.

### Competition observations

Competition observations describe peer movement, market comparison, challenger activity and relative performance. They help CIOS understand whether external market pressure is increasing transformation inevitability.

Examples:

- Competitor investment increased.
- Market share declined.
- AI-first entrant emerged.
- Strategic acquisition completed.
- Peer outperformed.
- Customer churn increased.
- Regulatory comparison worsened.

### Regulation observations

Regulation observations describe compliance obligations, enforcement, scrutiny and policy change. They help CIOS identify non-discretionary pressure and timing constraints.

Examples:

- Regulator investigation opened.
- Compliance deadline approaching.
- Fine issued.
- Audit criticism published.
- Licence condition updated.
- Consultation launched.
- Parliamentary scrutiny increased.

### Security observations

Security observations describe cyber events, security leadership, programmes, controls, guidance and regulatory pressure. They help CIOS identify resilience pressure and secure-by-design transformation needs.

Examples:

- Cyber incident occurred.
- CISO appointed.
- Security programme launched.
- Zero Trust adopted.
- NCSC guidance applies.
- Security investment increased.
- Regulatory cyber pressure increased.

### Relationship observations

Relationship observations describe meaningful links between people, suppliers, advisers, boards and partnerships. They help CIOS interpret access, influence, incumbent strength and ecosystem movement.

Examples:

- Executive previously worked with supplier.
- Supplier partnership announced.
- Board member connected to sector adviser.
- Incumbent relationship renewed.
- Strategic alliance expanded.

### Absence observations

Absence observations describe important missing evidence after a defined search. They are valuable because silence can itself change commercial interpretation, but they require careful confidence labelling and must avoid overclaiming.

Examples:

- No AI strategy found despite peer adoption.
- No procurement evidence found despite transformation pressure.
- No named sponsor identified.
- No budget evidence visible.
- No supplier evidence found for stated programme.

## Observation object

A standard Observation object should include:

- Observation ID
- Observation Type
- Category
- Statement
- Observed Entity
- Related Entities
- Observation Date
- Evidence Date
- Collection Date
- Evidence References
- Source Families
- Confidence
- Freshness
- Severity
- Novelty
- Materiality
- Commercial Relevance
- Observation Importance
- Commercial Value
- Actionability
- Observation Demand
- Generated Questions
- Observation Maturity
- Observation Half-Life
- Transformation Relevance
- Opportunity Relevance
- Affected Enterprise Model Attributes
- Supporting Strategic Signals
- Supporting Hypotheses
- Contradictory Observations
- Unknowns
- Generated By
- Human Validation State
- Lifecycle State
- Expiry / Review Date

## Observation quality

Observation quality should be assessed across these dimensions:

- Specificity
- Novelty
- Materiality
- Authority
- Corroboration
- Freshness
- Commercial usefulness
- Noise level
- Explainability
- Independence
- Absence significance

Suggested quality bands:

- **90–100:** high-specificity, material, evidence-backed observation.
- **75–89:** strong observation requiring limited corroboration.
- **60–74:** useful observation but incomplete or single-source.
- **40–59:** context observation only.
- **0–39:** reject or diagnostics only.

## Observation lifecycle

Observation lifecycle states are:

- Detected
- Validated
- Corroborated
- Strengthened
- Weakened
- Contradicted
- Retired
- Archived

Lifecycle transitions should preserve lineage and explain why the state changed:

- **Detected → Validated:** evidence quality passes threshold.
- **Validated → Corroborated:** independent evidence supports the observation.
- **Corroborated → Strengthened:** additional source families support the observation.
- **Strengthened → Weakened:** evidence ages or contradictions appear.
- **Any state → Contradicted:** reliable opposing evidence appears.
- **Any state → Retired:** the observation is no longer commercially relevant.
- **Retired → Archived:** the observation is preserved only for history.

## Observation relationships

One observation may:

- support multiple Strategic Signals;
- support multiple Hypotheses;
- contradict another Observation;
- strengthen Enterprise Behaviour;
- modify Transformation Pressure;
- modify Transformation Inevitability;
- modify Opportunity Outlook;
- trigger Enterprise Model updates;
- create Evidence Demand;
- generate a Collection Task.

These relationships make Observations reusable intelligence atoms rather than one-off report statements.

## Observation clustering

Observations become patterns when multiple related statements indicate a coherent enterprise movement.

Example:

Observation:
AI recruitment increased.

Observation:
Chief AI Officer appointed.

Observation:
Data platform investment announced.

Observation:
AI governance policy published.

Pattern:
AI capability expansion.

Strategic Signal:
Enterprise AI transformation may be forming.

Hypothesis:
Enterprise is preparing to scale AI across operations.

Recommendation:
Validate sponsor, budget, use cases and governance maturity with CIO / Chief AI Officer.

## Observation confidence

Confidence belongs to Observations, not just Evidence. An evidence object may be reliable while the derived Observation remains uncertain because the commercial meaning is ambiguous.

Observation confidence depends on:

- evidence quality;
- source authority;
- independent corroboration;
- recency;
- specificity;
- contradiction state;
- historical reliability;
- source family diversity;
- whether the observation is direct, inferred or absence-based.

A highly reliable evidence object may still produce a weak Observation if commercial meaning is ambiguous.

## Observation decay

Observation decay weakens current relevance; it should not erase history. Older observations may remain important as context even when they no longer justify current commercial action.

Fast-decay observations include:

- job adverts;
- live procurement notices;
- executive statements;
- press releases;
- incidents;
- conference claims.

Medium-decay observations include:

- transformation programmes;
- supplier relationships;
- technology platform use;
- financial guidance;
- organisational structures.

Slow-decay observations include:

- executive appointment history;
- completed ERP replacement;
- long-term operating model;
- ownership structure;
- durable regulatory obligations.

## Observation deduplication

Multiple evidence records may support the same Observation. CIOS should not create five duplicate observations if five sources repeat the same announcement.

Instead, CIOS should:

- strengthen the existing observation;
- add corroborating evidence;
- update confidence;
- update source diversity;
- preserve source lineage.

Deduplication should compare statement meaning, observed entity, observation type, category, time window, evidence lineage and contradiction state.

## Observation absence and negative intelligence

Absence can be informative when it is grounded in a defined search context.

Examples:

- No procurement evidence despite high transformation pressure.
- No AI governance evidence despite AI ambition.
- No named executive sponsor despite programme announcements.
- No budget evidence despite transformation language.

Absence observations must:

- record what was searched;
- record where it was searched;
- record search date;
- avoid overclaiming;
- generate evidence demand.

Absence observations should usually carry lower confidence than direct observations unless the search scope is authoritative, repeatable and recent.

## Observation examples

### BT example

Evidence:
BT announcement states it joined Anthropic Project Glasswing for cyber defence.

Observation:
BT is publicly associating frontier AI with cyber resilience.

Signal:
AI-enabled cyber resilience may be becoming strategically relevant.

Hypothesis:
BT may be exploring AI-enabled resilience as part of wider network operations transformation.

Unknowns:
Budget, sponsor, operational deployment, procurement route.

### DWP example

Evidence:
DWP publishes procurement or operational evidence linked to casework, debt, automation or citizen service scale.

Observation:
DWP operational service pressure is visible in citizen-service processes.

Signal:
Operational scale and automation pressure may support service transformation.

Hypothesis:
DWP may need AI-enabled casework or debt-service transformation.

Unknowns:
Policy sponsor, budget, procurement timing, incumbent position.

### National Grid example

Evidence:
National Grid reports grid connection, resilience, investment or regulatory pressure.

Observation:
Grid resilience and capacity pressure increased.

Signal:
Critical infrastructure digital operations may be becoming more urgent.

Hypothesis:
National Grid may require asset intelligence, forecasting or secure-by-design operations transformation.

Unknowns:
Programme owner, supplier ecosystem, investment route, regulatory driver.

# Observation Networks

Observations rarely exist in isolation. Multiple Observations often describe the same enterprise movement from different angles, dates, functions and source families. An Observation Network is a connected set of Observations that together describe a coherent movement, pressure or behaviour.

Example:

```text
Hiring freeze
↓
Margin pressure
↓
Automation investment
↓
Productivity speech
↓
Cost reduction programme
↓
Observation Network
↓
Operating Model Transformation
```

Networks become Patterns. Patterns become Strategic Signals. Strategic Signals support Hypotheses and Commercial Theses.

Observation Networks matter because commercial change is usually distributed. One Observation may be weak; a network can reveal direction. One job advert may be noise; repeated hiring, executive language, procurement and budget movement can indicate enterprise intent.

# Observation Half-Life

Observation Half-Life is the expected period over which an Observation loses half of its current decision relevance if not refreshed, corroborated or converted into more durable state. Half-life formalises decay without erasing history.

Suggested half-life examples:

| Observation source or subject | Indicative half-life |
| --- | ---: |
| Press release | 7 days |
| Conference speech | 14 days |
| Job advert | 30 days |
| Quarterly results | 90 days |
| Procurement notice | 180 days |
| Executive appointment | 2 years |
| ERP programme | 5 years |
| Ownership structure | 10 years |

Half-life matters because it controls review urgency, confidence decay, collection demand and commercial timing. A live procurement notice may be urgent but short-lived. An ownership structure may remain commercially meaningful for years. CIOS should not treat all Observations as equally perishable.

# Observation Maturity

Observation Maturity describes how settled an Observation is in enterprise memory. It differs from Confidence. Confidence measures belief that the Observation is true; Maturity measures how the Observation has aged, been validated, become historically established or lost current relevance.

Stages:

- **Immature:** newly detected, incomplete, weakly corroborated or awaiting validation.
- **Validated:** supported by sufficient evidence to update the Enterprise Model.
- **Established:** repeatedly corroborated or stable enough to be treated as durable enterprise state.
- **Historical:** no longer current but important for understanding trajectory, relationships or precedent.
- **Dormant:** not currently active in reasoning but retained because it may become relevant again.
- **Retired:** no longer commercially relevant except for audit or lineage.

A high-confidence Observation can be Immature if it has just appeared and implications are unknown. A lower-confidence Observation can become Established only after corroboration, repeated support and contradiction handling.

# Observation Learning

Repeated Observations allow Enterprise Learning. Over time, CIOS should learn not only isolated facts but enterprise habits: recurring behaviours, preferred suppliers, buying rhythms, executive language, operating constraints and transformation patterns.

Examples of repeated Observations that become learning inputs:

- repeated hiring spikes before major transformation programmes;
- repeated procurement behaviour using the same frameworks or partners;
- repeated supplier preference across adjacent programmes;
- repeated executive language around productivity, resilience, AI, citizen experience or cost;
- repeated delays after funding announcements;
- repeated absence of named sponsorship despite strategic ambition.

These repeated Observations become enterprise habits. Future EI-013 Enterprise Learning Model will define how these habits are learned, represented, challenged and reused.

# Observation Ethics

Observation doctrine must preserve trust. Enterprise Intelligence should use only public and appropriately licensed information, trusted human input and auditable sources.

CIOS must not use Observations to justify surveillance, covert monitoring or personal profiling beyond legitimate business context. Observations must not infer protected characteristics. Commercial intelligence must remain explainable, proportionate and auditable, with clear lineage from evidence to Observation to reasoning outcome.

# Observation Principles Diagram

```text
Enterprise
↓
Evidence
↓
Observation
↓
Observation Network
↓
Pattern
↓
Signal
↓
Hypothesis
↓
Commercial Thesis
↓
Recommendation
↓
Executive Conversation
↓
Commercial Outcome
```

# Cross References

## Relationship to EI Volume 1

- **EI-001 Commercial Digital Twin:** consumes Observations as durable updates to enterprise state. Observations are how the Commercial Digital Twin remembers meaningful change.
- **EI-002 Enterprise Knowledge Graph:** consumes Observations as nodes, edges, evidence-backed relationships and contradiction links. Observation relationships make enterprise memory navigable.
- **EI-003 Enterprise Behaviour Model:** consumes repeated and networked Observations to infer behavioural tendencies, rhythms and habits.

Observations are the update mechanism for the Enterprise Model. They convert evidence into memory, give the Commercial Digital Twin fresh state, create graph relationships and provide the Behaviour Model with structured signals of enterprise movement.

## Relationship to Foundational Papers

- **FP-007:** consumes Observations as the atomic evidence-backed inputs that keep foundational reasoning grounded in explainable enterprise change.
- **FP-008:** consumes Observations to maintain separation between evidence, memory, interpretation and action.
- **FP-009:** consumes Observations as reusable commercial intelligence units that can be governed, challenged and audited.

## Relationship to CIRM

Observations are the primary intelligence objects entering CIRM.

CIRM should not reason directly over raw evidence where an Observation can be created. Evidence supports Observations. Observations support Strategic Signals. Strategic Signals support Hypotheses and Commercial Conviction.

The CIRM reasoning chain should therefore preserve the distinction:

- Evidence is proof.
- Observation is memory.
- Signal is meaning.
- Hypothesis is interpretation.
- Recommendation is action.

## Relationship to future Volume 5 papers

- **EI-013 Enterprise Learning Model:** will consume repeated Observations to learn enterprise habits, behavioural patterns, supplier preferences and transformation rhythms.
- **EI-014 Commercial Conversation Model:** will consume Observations, Networks and Commercial Theses to prepare executive conversations grounded in explainable enterprise memory.
- **EI-015 Enterprise Question Model:** will consume Observation Questions and turn them into structured investigative prompts, unknowns and validation paths.
- **EI-016 Enterprise Curiosity Engine:** will consume Observation Demand, Half-Life, Maturity, contradiction state and commercial value to decide what CIOS should investigate next.

## Open questions

- How should observations be deduplicated across enterprises?
- How should sector-level observations be handled?
- Should observations be manually validated before supporting high-conviction hypotheses?
- How should observations learn from human feedback?
- What observation types should be mandatory for Level 2 or Level 3 Commercial Digital Twins?
- How should absence observations be prevented from becoming false negatives?
- What quality threshold should be required for an observation to update Opportunity Outlook?

# Final Summary

The Observation is the fundamental reusable unit of Enterprise Intelligence.

Evidence is transient.

Observations persist.

Enterprise Models accumulate observations.

Commercial reasoning interprets observations.

Executive decisions are informed by commercial reasoning.

Every capability within CIOS ultimately exists to detect, understand or exploit meaningful enterprise change.

## Normative Clarification — Observation State Semantics for Financial Intelligence

**Status:** Normative clarification.
**Owner:** EI-012 Enterprise Observation Model.
**Date added:** 2026-07-05.
**Authority:** EI-012 owns Observation lifecycle semantics. EI-001 owns financial metric fact structure and Enterprise Model paths. ADR-010 owns structured-source-first acquisition.

### Separate state concepts

CIOS MUST keep the following concepts separate:

- **Observation lifecycle:** how an Observation progresses through validation, corroboration, strengthening, weakening, contradiction, retirement and archival. The EI-012 lifecycle remains `Detected`, `Validated`, `Corroborated`, `Strengthened`, `Weakened`, `Contradicted`, `Retired` and `Archived`.
- **Observation maturity:** how settled or historically established the Observation is in enterprise memory. Maturity can describe whether a fact is newly observed, repeatedly established, historical or dormant without changing lifecycle meaning.
- **Confidence:** how strongly CIOS believes the Observation is true after considering Evidence quality, corroboration, contradiction and validation.
- **Freshness and temporal relevance:** how current and decision-relevant the Observation remains based on effective period, observed date, half-life, decay and business context.
- **Domain measurement state:** a property owned by the observed domain fact, such as a financial value being `actual`, `guidance`, `target`, `forecast` or `prior_period_comparator`.
- **Accounting basis:** a property of how a financial metric was reported, such as `statutory`, `adjusted`, `alternative_performance_measure` or another explicitly reported basis.

`current` is not an EI-012 Observation lifecycle state. A financial metric's measurement state MUST NOT be placed into the Observation lifecycle field. Freshness MUST NOT be placed into a domain measurement-state field. Accounting basis MUST NOT be confused with measurement state.

### Worked financial example

- **Evidence:** BT annual report page reference for the disclosed metric.
- **Financial fact:** Adjusted EBITDA, FY26, £8.2bn, measurement state `actual`, accounting basis `adjusted`.
- **Observation:** BT Group reported FY26 adjusted EBITDA of £8.2bn.
- **Observation lifecycle:** `Validated`.
- **Freshness:** current according to its reporting period, observed date and applicable financial-reporting half-life.
- **Enterprise Model attribute:** `financial_performance.metrics.adjusted_ebitda.FY26.actual`.

This example is illustrative, not a hard-coded runtime fixture. It shows that financial fact state, accounting basis, freshness and Observation lifecycle are different fields even when a product view renders them together.
