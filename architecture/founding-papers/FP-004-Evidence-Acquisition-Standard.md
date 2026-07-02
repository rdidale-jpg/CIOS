# FP-004 — Evidence Acquisition Standard

**Purpose:** Define how Flora should think about evidence acquisition as the first stage of intelligence formation.
**Status:** draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-02

## 1. Purpose

This paper defines the standard for how Flora should acquire evidence before downstream reasoning begins. Collection is not a technical scrape step. It is the first stage of intelligence formation, where Flora decides what reality is worth observing, why it matters, and what further evidence is needed to improve commercial judgement.

The standard exists to prevent garbage-in-garbage-out reasoning. Flora should prefer fewer high-quality evidence objects over many weak snippets, and should collect evidence to answer commercial questions rather than merely because evidence is available.

## 2. Why collection quality determines intelligence quality

Flora's downstream signals, transformation theses and recommendations can only be as strong as the evidence foundation beneath them. Weak collection creates false confidence, shallow summaries and recommendations that appear explainable but are not commercially reliable.

High-quality collection improves intelligence by:

- grounding claims in specific, attributable evidence;
- reducing noise before reasoning begins;
- exposing what is unknown rather than hiding gaps inside fluent prose;
- enabling corroboration across independent sources;
- preserving the difference between observed facts, inferred signals and commercial recommendations.

Collection quality is therefore an intelligence control, not an ingestion convenience.

## 3. Evidence acquisition philosophy

Flora should acquire evidence with intent. Every organisation should have an evidence acquisition plan that reflects the commercial questions Flora is trying to answer, the transformation hypotheses under consideration, and the missing evidence needed to strengthen or weaken those hypotheses.

The collection philosophy is:

- evidence is pursued because it can improve judgement;
- collection should be guided by hypotheses and missing evidence;
- every transformation thesis should create evidence demand;
- acquisition should favour specificity, authority, freshness and corroboration;
- collection should stop, redirect or retire sources when yield is low;
- source availability must not be confused with source value.

Landing pages, navigation, menus and boilerplate are context, not evidence. They may help Flora understand an organisation's public surface, but they should not support strategic signals without more specific corroboration.

## 4. Evidence Acquisition Plan

For every monitored enterprise, Flora should maintain an Evidence Acquisition Plan. The plan is the operational bridge between strategic evidence demand and live collection behaviour.

An Evidence Acquisition Plan should contain:

- enterprise type;
- sector;
- priority level;
- active transformation theses;
- required evidence categories;
- current coverage;
- missing evidence;
- priority source families;
- low-yield sources to replace;
- next collection objectives;
- collection confidence.

Live collection should increasingly be driven by this plan rather than by static source lists. Static governed source lists remain useful as safe starting points, but they should not determine the whole collection path. The plan should tell Flora what evidence is needed next, which sources are most likely to produce it, which noisy sources should be replaced or split, and when the evidence base is too weak for confident reasoning.

The plan should evolve after each collection run. New evidence may create additional evidence demand, close gaps, expose contradictions, reveal better child sources or reduce confidence if expected evidence is missing.

## 5. Evidence hierarchy

### Primary Evidence

Primary evidence is direct, attributable material from the organisation, regulator, market authority, procurement body, audit body or named executive. It can usually support stronger signals because it is close to the decision, obligation, spending event or strategic claim.

Examples include annual reports, official strategies, regulatory filings, audit reports, procurement notices, contract awards, investor presentations and named executive speeches.

### Secondary Evidence

Secondary evidence is material that interprets, amplifies or reports on primary events. It can support signals when specific and corroborated, especially where it identifies named programmes, named suppliers, budgets, timelines, operating constraints or leadership changes.

Examples include press releases, supplier announcements, case studies, sector publications, credible industry coverage and senior role advertisements.

### Context Evidence

Context evidence helps Flora understand an organisation but should not by itself support a strategic signal. It can shape search strategy, sector classification, operating model understanding or source discovery.

Examples include homepages, generic service pages, careers landing pages, organisational descriptions, navigation structures and broad marketing pages.

### Rejected Evidence

Rejected evidence is material that should not be used to support strategic signals because it is generic, non-specific, boilerplate, navigational, duplicated or diagnostically useful only.

Examples include cookie text, footers, accessibility statements, generic publication scheme text, contact pages and repeated menu content.

### Evidence classification examples

- Bad evidence: “Jobs and contracts Procurement at DWP Working for DWP Publication scheme”. Classification: reject / diagnostics only.
- Context evidence: an organisation landing page that confirms operating areas but contains no programme, owner, investment, contract or milestone. Classification: context only.
- Secondary evidence: a supplier announcement naming a client, platform and delivery scope, but not independently confirming contract value or benefits. Classification: secondary evidence requiring corroboration.
- Primary evidence: “£15 billion investment to transform Armed Forces and keep the UK safe”. Classification: primary evidence, investment pressure, high specificity.
- High-value evidence cluster: a strategy names a modernisation programme, a contract award names the supplier, an annual report allocates funding, and a named executive describes the delivery milestone. Classification: high-confidence evidence cluster.

## 6. Evidence accept, downgrade and reject rules

Flora should classify evidence before it is allowed to influence strategic signals. The rules below are practical guidance for live collection and curation.

### Accept evidence

Accept evidence when it includes at least one specific, commercially useful feature such as:

- named programme;
- quantified investment;
- named supplier;
- named executive or accountable role;
- contract, tender or award;
- strategy commitment;
- regulatory finding;
- delivery milestone;
- operational incident;
- specific technology platform;
- specific transformation initiative.

### Downgrade evidence

Downgrade evidence when it is useful but limited, including when it is:

- relevant but generic;
- dated but still useful;
- from a biased supplier source;
- single-source only;
- a partial snippet;
- marketing-led but specific.

Downgraded evidence may support context, weak signals or search direction, but should normally require corroboration before supporting strong claims.

### Reject evidence

Reject evidence when it is:

- navigation;
- menu text;
- cookie text;
- footer or header;
- careers landing page;
- generic service catalogue;
- generic GOV.UK publication scheme text;
- accessibility, modern slavery or complaints boilerplate;
- duplicated without new information.

Rejected evidence may remain useful for diagnostics, parser improvement or source replacement, but it must not support strategic reasoning.

## 7. Evidence scoring bands

Suggested evidence quality bands are:

| Score | Interpretation | Typical use |
| --- | --- | --- |
| 90–100 | High-specificity primary evidence | Can support strong signals when current and relevant |
| 75–89 | Strong specific evidence, may need corroboration | Can support signals with caveats or corroboration |
| 60–74 | Useful but limited evidence | Supports context, weak signals or collection direction |
| 40–59 | Context only | Helps source discovery or organisation understanding |
| 0–39 | Reject / diagnostics only | Should not support strategic reasoning |

These bands are architectural guidance, not final runtime constants. Future implementation may adjust thresholds, weighting and calibration, but should preserve the principle that specificity, authority, freshness and corroboration increase reasoning weight.

## 8. Evidence specificity standard

Evidence should identify at least one commercially useful object: an organisation, programme, leader, supplier, budget, contract, regulation, operating pressure, technology domain, customer group, timeline or measurable outcome.

A useful evidence object should answer at least one of the following:

- What is changing?
- Who appears accountable?
- What pressure or ambition is visible?
- What capability is being built, replaced or constrained?
- What money, procurement activity or supplier movement is present?
- What timing signal exists?
- What uncertainty remains?

Generic claims such as "digital transformation is important" or "the organisation uses technology" should be treated as low-specificity unless tied to a concrete programme, decision, obligation or investment.

## 9. Evidence freshness and ageing

Evidence has a useful life. Flora should consider how quickly evidence ages based on its type and commercial use.

- Procurement notices, job adverts, leadership changes and incident reports age quickly.
- Annual reports, strategies and regulatory reviews age more slowly but may become stale when new reporting cycles appear.
- Historical audit reports can remain valuable when they describe persistent operating constraints.
- Old evidence can support trend analysis but should not imply current intent without fresh corroboration.

Freshness should be assessed relative to the commercial question, not as a simple date filter.

## 10. Evidence novelty

Flora should value evidence that adds new information to an existing picture. Novel evidence may introduce a new programme, confirm a previously weak signal, reveal a contradiction, identify a named supplier, expose a budget or show timing acceleration.

Repeated publication of the same claim across multiple low-value pages should not be treated as new evidence. Duplication increases confidence only when it comes from independent, meaningful sources.

## 11. Evidence corroboration

Strong commercial judgement usually requires corroboration. Flora should seek independent support across source types where possible, especially before generating strong signals or recommendations.

Corroboration may occur when:

- a strategy document names a priority and procurement data shows related buying;
- an executive speech states an ambition and job adverts reveal capability build-out;
- regulatory criticism aligns with investment announcements;
- supplier announcements match contract awards or delivery milestones.

Contradictory evidence should be preserved and surfaced rather than smoothed away.

## 12. Evidence duplication and retirement

Duplicate evidence should be consolidated. Flora should avoid treating repeated snippets, mirrored pages or boilerplate as independent support.

Evidence should be retired or downgraded when:

- it is superseded by a newer authoritative source;
- it is duplicated without adding specificity;
- the source becomes unavailable or materially changed;
- the commercial question it served is no longer active;
- it has aged beyond its useful life without corroboration.

Retirement does not mean deletion from history. It means the evidence should no longer carry current reasoning weight.

## 13. Source yield measurement

Flora should measure source yield: the usefulness of a source relative to the effort and noise involved in collecting from it.

Yield should consider:

- number of evidence objects produced;
- specificity of evidence;
- authority of evidence;
- freshness;
- novelty;
- corroboration value;
- duplication rate;
- proportion of rejected or diagnostics-only material.

A source can be authoritative but low-yield, and a noisy source can occasionally produce high-value evidence. Yield should inform collection strategy rather than permanently exclude a source family.

## 14. Evidence coverage thresholds

Flora should not treat collection as complete merely because some evidence exists. Each organisation should have coverage thresholds aligned to enterprise type, account priority and active hypotheses.

Minimum coverage should normally include:

- at least one current authoritative strategy or performance source;
- evidence of recent financial, operational or delivery posture where available;
- evidence of technology, procurement, leadership or regulatory movement relevant to the thesis;
- explicit capture of gaps where expected evidence cannot be found.

Priority accounts should require deeper coverage and stronger corroboration before high-confidence recommendations are produced.

## 15. Evidence gaps as intelligence

Absence of evidence can be meaningful when a source would normally be expected. Missing procurement data, absent strategy updates, unexplained leadership vacancies or lack of supplier announcements may reveal opacity, timing risk, weak market visibility or a need for human follow-up.

Flora should record evidence gaps explicitly. A gap is not proof of absence, but it is intelligence about uncertainty.

## 16. Evidence demand model

Evidence demand is the set of evidence Flora needs to improve a judgement. Demand should be generated by commercial questions and transformation theses.

For example:

- A thesis about AI-enabled operating model change demands evidence of leadership intent, data foundations, procurement, skills and delivery pressure.
- A thesis about cyber resilience demands evidence of regulatory pressure, incidents, security investment, supplier movement and accountable leadership.
- A thesis about cost reduction demands evidence of budget pressure, operating constraints, automation programmes and workforce signals.

The stronger the thesis, the clearer the evidence demand should become.

## 17. Collection feedback loop

Collection should learn from downstream reasoning. When Flora produces weak signals, unsupported claims, contradictory findings or user feedback, those outcomes should inform future collection plans.

The feedback loop should answer:

- Which sources produced useful evidence?
- Which hypotheses lacked support?
- Which evidence categories were missing?
- Which sources produced noise?
- What should Flora collect next to improve judgement?

Collection is therefore adaptive, not a one-time crawl.

## 18. Collection Agent concept

A future Collection Agent should plan, execute and evaluate evidence acquisition for an organisation. Its role would be to translate evidence demand into source selection, collection priorities, gap analysis and source replacement recommendations.

The Collection Agent should not simply gather pages. It should understand enterprise type, active theses, evidence hierarchy, expected source families and quality thresholds. It should return governed evidence and explicit gaps for downstream reasoning.

## 19. Collection handbrakes

Current and likely Phase 1 collection handbrakes include:

- static governed source lists;
- landing-page dependence;
- weak child-page discovery;
- no active evidence demand per thesis;
- limited source replacement learning;
- weak negative-evidence detection;
- limited contradiction seeking;
- limited historical trend capture;
- shallow supplier/incumbent mapping.

Future collection sprints should remove these handbrakes incrementally. Flora should move from “visit known pages” to “pursue missing evidence”, promote useful child pages into governed sources, preserve negative and contradictory evidence, learn which sources repeatedly fail, and build richer historical and supplier context where it improves commercial judgement.

## 20. Human feedback loop

Future UI should allow users to mark evidence and sources as:

- useful evidence;
- weak evidence;
- wrong classification;
- noisy source;
- important source;
- missing source.

This feedback should influence future source yield and evidence quality. A source repeatedly marked noisy should be downgraded, split or replaced. Evidence repeatedly marked useful should improve source yield and help Flora learn which evidence categories matter for similar enterprises and theses. Wrong-classification feedback should feed curation rules and scoring calibration.

## 21. Governance rules

Flora's evidence acquisition should follow these governance rules:

- collect evidence for commercial judgement, not volume;
- preserve source attribution and retrieval context;
- distinguish evidence from context and diagnostics;
- do not allow diagnostics-only material to support strategic signals;
- prefer authoritative and specific sources;
- document gaps and uncertainty;
- retire stale or duplicated evidence;
- expose collection quality before presenting downstream confidence;
- avoid organisation-specific collection logic where enterprise-generic patterns can apply.

## 22. Open questions

- What minimum coverage threshold should block high-confidence recommendations?
- How should Flora weight old but authoritative evidence against fresh but weaker evidence?
- How should evidence acquisition plans be represented in product workflows?
- What source yield metrics should be visible to users?
- How should human feedback alter future collection priorities?
