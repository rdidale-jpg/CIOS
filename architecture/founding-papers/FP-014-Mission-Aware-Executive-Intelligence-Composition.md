# FP-014 — Mission-Aware Executive Intelligence Composition

**Identifier:** FP-014  
**Version:** 0.1  
**Document Type:** Founding Paper  
**Authority Classification:** Proposed founding paper; documentation-only and non-runtime  
**Status:** Proposed  
**Date:** 2026-07-28  
**Owner:** Rob / CIOS  
**Release-profile membership:** None — review context only

## 1. Status and authority

FP-014 is proposed architecture in the governed Founding Papers collection. It defines a product-composition doctrine, not an implementation design, canonical intelligence model, persistence contract or claim of delivered capability. It is subordinate to accepted ADRs and the owning Enterprise Intelligence papers and specifications. Review or merge does not make the capabilities described here operational, promote intelligence, or add this paper to a production Knowledge Pack.

Within the CIOS Intelligence Reference Model, FP-014 is a composition and presentation paper over governed observation and reasoning outputs. It does not add a step to CIRM or take ownership from Evidence, Observations, Enterprise Models, Industry Twins, Market Participant Twins, Opportunity Twins or Presentation Models.

## 2. Purpose

FP-014 defines how Flora composes governed Enterprise Intelligence into an **Executive Intelligence Workspace** using a declared **Commercial Mission**. It establishes a legible route from material change to commercially relevant investigation while preserving the intelligence and trust boundaries beneath it.

**Flora is an Executive Intelligence Companion.** Its purpose is to help executives recognise material change, identify emerging transformation opportunities, understand when industries and enterprises are approaching significant reinvention, and inspect the evidence supporting those conclusions before opportunities formalise into programmes or procurements.

## 3. Problem statement

An executive does not normally arrive wanting to inspect an import record. The executive wants to know what has changed, whether it matters to the organisation they lead or represent, why attention is warranted now, who else is involved, and whether the conclusion can be defended. A technically correct inventory without mission context makes relevance difficult to recognise. Conversely, commercial tailoring that changes facts, hides inconvenient evidence or invents supplier fit destroys trust.

Flora therefore needs a governed composition boundary between common Twin inspection and a mission-relevant executive workspace. The boundary must make its inputs and transformations inspectable, preserve uncertainty, and never convert presentation relevance into canonical truth.

## 4. Vision

The same governed Twin can support different Executive Intelligence Workspaces for a Strategic Sales Director, industry leader or another executive because their declared missions foreground different questions. The underlying Enterprise Intelligence remains identical. Each workspace explains what was selected, why it is relevant, what is not known and how to inspect the evidence.

Flora helps every executive answer:

1. **What is happening?**
2. **Why does it matter to my Commercial Mission?**
3. **Why now?**
4. **Why should I believe it?**

## 5. Relationship to FP-013

[FP-013](FP-013-Executive-Intelligence-Workspace.md) remains authoritative for executive-first inspection, progressive disclosure, trust through inspection, evidence visibility, the common inspection experience and **“Why should I believe this?”** FP-014 extends FP-013; it neither replaces nor weakens it.

FP-014 owns the proposed mission-aware composition that occurs before and around detailed inspection. FP-013 owns the shared inspection experience into which that composition leads. The Twin Inspection Shell and Common Executive Inspection Contract remain presentation and orchestration boundaries, not new intelligence owners. All detailed evidence inspection continues through FP-013 and the applicable canonical owner.

## 6. Architectural principles

1. **Commercial Mission determines relevance. Enterprise Intelligence determines truth.**
2. **Executives arrive to understand opportunity. They remain to inspect evidence.**
3. **Commercial awareness without commercial bias.** Flora may interpret relevance but must not favour an employer, supplier, conclusion or desired sale.
4. **Mission-aware composition, not opaque personalisation.** Declared inputs and deterministic rules replace hidden behavioural inference.
5. **Commercial opportunity is a function of relevance, timing and evidence.** None may be silently substituted for another.
6. **Reinvention Timing is evidence-led.** Urgency must be explained through observed maturity, not manufactured.
7. **Commercial Mission may influence foregrounding, grouping and navigation, but must never alter governed intelligence.**
8. **Unknowns, Contradictions and missing Evidence remain visible.** Commercial inconvenience is never a reason for suppression.

## 7. Commercial Mission

**Commercial Mission** is a declared, visible and inspectable composition input describing the executive's bounded commercial purpose. It is distinct from the transient AI-agent **Mission** and Runtime Context owned by [ADR-015](../decisions/ADR-015-Runtime-Mission-Context.md). A future runtime may carry a Commercial Mission within runtime context, but that does not make it durable Enterprise Intelligence.

A Commercial Mission may include:

- executive role;
- employer;
- associated Market Participant;
- governed offer and capability portfolio;
- strategic competitors;
- strategic partners;
- priority industries;
- priority geography;
- priority accounts;
- active campaigns;
- commercial objectives; and
- inspection depth.

Commercial Mission:

- is not Enterprise Intelligence and is not part of the inspected Twin;
- does not alter canonical intelligence, Evidence or governed relationships;
- must be visible to the user, including the fields and sources used for composition;
- may be incomplete, stale or absent;
- must not cause Flora to invent relevance, fit, relationships or consequences; and
- must preserve and display uncertainty wherever context is absent.

Missing mission fields narrow what Flora can explain. They do not authorise behavioural inference. For example, absent employer or offer context means offer alignment is **unresolved**, not that every offer is relevant.

## 8. Commercial landscape context

Where configured, Flora should understand the user's principal competitors, strategic partners, likely incumbents and ecosystem participants. Supplier, competitor and partner are contextual roles of governed Enterprise or Market Participant identities; FP-014 creates no separate supplier or competitor model. Participant claims remain subject to the Market Participant Twin and Knowledge Graph authorities, including their account-relative and evidence-lineage constraints.

Commercial landscape context exists to improve interpretation: it can reveal a delivery route, overlap, displacement constraint, incumbent position or validation question. It must not fabricate competitor presence, suppress an opportunity because a competitor is present, favour the user's employer, alter Evidence, or infer a relationship without governed support. Where no governed Evidence links a competitor or partner to an industry, enterprise or opportunity, Flora must state: **“No governed evidence is currently available.”**

Human-supplied competitor, partner or incumbent context must remain labelled with contributor, date and rationale under [ADR-004](../decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md); it cannot be rendered as independently established fact.

## 9. Mission-aware composition pipeline

The architectural flow is:

```text
Governed Enterprise Intelligence
→ Twin Inspection Shell
→ Common Executive Inspection Contract
→ Commercial Mission
→ deterministic mission-aware composition
→ Executive Intelligence Workspace
→ evidence inspection
```

“Deterministic” means that the same governed inputs, declared Commercial Mission, versioned composition rules and effective time produce the same composition, with the basis available for inspection. It does not mean that stale or incomplete inputs become certain.

Mission-aware composition may change only:

- ordering;
- grouping;
- prioritisation;
- presentation;
- navigation; and
- explanatory narrative.

It must never change Evidence, provenance, freshness, lineage, Contradictions, Unknowns, assumptions or canonical intelligence. It must not copy canonical records into a new mission-specific store. The workspace is a read composition over owner-provided projections; canonical workflows remain the destinations for governance and inspection.

## 10. Executive questions

Every Executive Intelligence Workspace must answer all four questions:

### 10.1 What is happening?

Describe the current state, challenges, changes and pressures affecting the inspected Industry, Enterprise or Market Participant. Distinguish observed fact, governed interpretation, hypothesis and missing Evidence.

### 10.2 Why does it matter to my Commercial Mission?

Explain relevance to the user's employer, offers, competitors, partners, markets and commercial objectives. Name the mission inputs used; do not imply alignment where those inputs or governed links are missing.

### 10.3 Why now?

Explain the evidence-backed maturity and urgency of reinvention pressures, including principal drivers, affected functions, freshness, contradictions and changes over time where history exists. Urgency is not confidence, access, value or procurement probability.

### 10.4 Why should I believe it?

Expose Evidence, provenance, freshness, Contradictions, Unknowns, assumptions and lineage through FP-013's progressive inspection experience. A concise executive explanation must link to, not replace, owned inspection.

## 11. Strategic Sales Director composition

For a **Strategic Sales Director** Commercial Mission, an Industry Twin workspace must foreground the following composition. “Must foreground” governs navigation and presentation when the owning intelligence exists; it does not require Flora to fabricate a complete section.

### 11.1 Intelligence Coverage

Counted tiles with drill-down should show what intelligence exists in the Twin: Evidence sources, Observations, industry pressures, transformation signals, enterprises, Market Participants, opportunity hypotheses, Unknowns, Contradictions and stale intelligence. Counts retain owner scope and must not imply quality or completeness by volume alone.

### 11.2 Industry Outlook

Compose commercially understandable insight into financial condition, structural challenges, regulatory pressures, technology shifts, operating-model pressure, workforce pressure, investment climate and transformation themes. Preserve the distinction between cross-industry synthesis and enterprise-specific claims.

### 11.3 Financial Assessment

Where Evidence exists, compose revenue and demand pressure; profitability and margin; cost pressure; capital allocation; investment commitments; savings and productivity targets; financial resilience; and differences between participant types. Label disclosed facts, estimates, interpretation and missing Evidence separately. The dual-speed and source-first financial intelligence boundaries remain owned by accepted ADR-011 and ADR-010.

### 11.4 Priority Prospects

Present prospect enterprises grouped by the user's governed offer or capability portfolio. Each prospect should explain:

- why the organisation is exposed;
- why timing matters;
- relevant transformation themes and offers;
- known incumbent, competitor or partner context;
- supporting Evidence, Contradictions and Unknowns; and
- a proportionate recommended investigation.

No opaque lead score is permitted. Offer grouping is unresolved when governed offer linkage is absent.

### 11.5 Opportunity Hypotheses

Present evidence-backed opportunities to investigate before procurement formalises. Each must expose the target enterprise or participant type, relevant industry pressure, triggering Observations, transformation hypothesis, relevant supplier offer or capability, timing indicators, likely executive concern, competitor/incumbent/partner context, Contradictions, missing Evidence and a proportionate next action.

An Opportunity Hypothesis is not confirmed procurement. Its lifecycle and validation remain governed by FP-009 and applicable Opportunity Twin doctrine, and recommendations require inspectable lineage under ADR-005.

### 11.6 Reinvention Timing

Show the evidence-backed proximity and affected functions described in section 12, without predicting purchasing events or presenting an unexplained score.

### 11.7 Reinvention Domains

Where Evidence permits, show domain-specific assessments from section 13. Omit or mark unresolved any domain with insufficient Evidence; never populate a complete heatmap for visual symmetry.

### 11.8 Reinvention Drivers

Expose supported drivers and their observations, affected domains, freshness, counter-evidence and mission relevance rather than listing generic reasons for change.

### 11.9 Competitor Activity

Present only evidence-supported competitor presence, partnerships, account activity, platform or capability positions, market announcements and likely areas of competitive overlap. “Likely” is an inference and must display its reasoning and limits.

### 11.10 Partner Activity

Present evidence-supported strategic alliance activity, partner relationships, ecosystem opportunities, channel or delivery routes and partner-led Opportunity Hypotheses. Do not turn an alliance announcement into proof of account access or delivery.

### 11.11 Commercial Watchlist

Present signals that may materially change opportunity timing: leadership changes, strategy announcements, financial deterioration, regulatory deadlines, procurement precursors, contract events, competitor or partner movements, major programme announcements and Evidence requiring refresh. Watchlist inclusion is a monitoring decision, not proof of an opportunity.

### 11.12 Coverage and Limitations

Expose enterprises with strong or partial coverage, missing priority enterprises, stale Evidence, material Contradictions, unresolved assumptions, unsupported financial conclusions and missing Commercial Mission context. Coverage labels must state their basis and scope and must not become a universal trust score.

## 12. Reinvention Timing

**Reinvention Timing** is **“The evidence-backed proximity of an industry or enterprise to material transformation across one or more business functions.”** Its purpose is to answer: **“Why is this becoming commercially important now?”**

Reinvention Timing assesses the observed maturity of transformation pressure. It must not predict procurement dates, contract awards, budget approval or purchasing decisions. Transformation pressure can mature without an accessible commercial opportunity, and Evidence of need is not Evidence of buying intent.

The repository has no accepted canonical Reinvention Timing stage vocabulary. The terms **Monitor, Emerging, Accelerating, Active and Embedded** may be used as an explainable FP-014 presentation vocabulary, not as replacements for the established Strategic Signal, Hypothesis, Conviction or Evidence lifecycles. Their meanings are:

| Stage | Evidence-led interpretation |
| --- | --- |
| Monitor | Relevant pressure is observed, but materiality, mechanism or timing remains weak or unresolved. |
| Emerging | Corroborated pressure or early action indicates that material change is forming. |
| Accelerating | Multiple fresh indicators show increasing pressure, commitment or breadth of response. |
| Active | Evidence shows material transformation activity underway in the assessed functions. |
| Embedded | Evidence shows the transformed capability or operating change in sustained use; residual reinvention needs may remain. |

These stages are ordinal descriptions, not numbers. A stage must not be inferred merely from the number of sources. Any assessment must expose:

- current stage and its dated assessment scope;
- affected business functions;
- principal drivers;
- supporting Evidence and Observations;
- contradictory Evidence;
- missing Evidence and assumptions;
- change since the previous assessment where comparable historical Evidence exists; and
- commercial relevance to the declared Commercial Mission.

If history is absent, Flora states **“No governed historical comparison is available”** rather than manufacturing a trend. If the Evidence cannot support a stage, the assessment is **unresolved**.

## 13. Reinvention domains and drivers

Where Evidence permits, Reinvention Timing may be assessed across: Executive Leadership; Strategy; Finance; Customer; Sales and Commercial; Operations; Technology; Data and AI; Cyber and Risk; Workforce; Supply Chain; Products and Services; and Sustainability.

The domain list is a composition lens, not a new canonical taxonomy. Domains may overlap owner-defined models and must link back to those source concepts. Completeness is not forced: an unsupported domain is omitted or marked unresolved, and Flora must not invent Evidence to complete a heatmap.

Evidence-supported drivers may include cost pressure, productivity pressure, financial deterioration, AI adoption, technology debt, customer expectations, regulation, workforce constraints, competitive pressure, operational resilience, leadership change, strategy change, contract or platform lifecycle and ecosystem change. A driver is not sufficient on its own: the assessment explains its observed effect, affected domain, recency, counter-evidence and remaining gap.

## 14. Competitor and partner intelligence

Competitor and partner intelligence remains governed, inspectable and account-relative. Every material participant claim must identify the governed participant, its contextual role, relationship or activity claimed, Evidence and Observation lineage, freshness, affected account/industry/opportunity, confidence basis, Contradictions and Unknowns.

Composition may compare evidenced positions or identify possible overlap. It cannot create a relationship, declare absolute participant strength, infer employer advantage, or convert marketing claims into delivery proof. Competitor presence must not suppress a prospect; it becomes context for investigation. Partner presence must not imply access, consent, capacity or a viable route without supporting Evidence.

## 15. Progressive disclosure

FP-013's Executive, Analyst, Architect and Technical levels remain the common pattern:

- **Executive:** what is happening, mission relevance, Reinvention Timing, material opportunity hypotheses and bounded limitations;
- **Analyst:** domains, pressures, participant activity, comparisons, assumptions, Unknowns and Contradictions;
- **Architect:** canonical ownership, provenance, lineage, composition-rule version and governance boundaries; and
- **Technical:** identifiers, read projections, assessment inputs and runtime diagnostics where implemented.

Commercial Mission must be inspectable from the workspace at every level appropriate to its sensitivity. Progressive disclosure may defer detail; it must never hide the basis of relevance or prevent evidence inspection.

## 16. Explainability

Every material conclusion must answer:

- Why this industry?
- Why this organisation?
- Why is this relevant to my Commercial Mission?
- Why now?
- Why should I believe it?

The relevance explanation exposes role, employer, offer alignment, competitor or partner context, industry pressure and enterprise exposure. The evidence explanation exposes Evidence, provenance, freshness, lineage, Contradictions, assumptions and Unknowns. A missing element is displayed as missing or unresolved, not removed from the explanation.

Explanations must make the composition path reproducible: governed conclusion → mission field(s) → composition rule → workspace placement → owning Evidence inspection. Generated narrative is a presentation output and must not introduce a claim absent from that path.

## 17. Runtime capability assessment

### 17.1 Architectural intent

This paper proposes mission-aware Executive Intelligence composition, Commercial Mission, competitor- and partner-aware composition, Reinvention Timing and the Strategic Sales Director workspace. These are target architecture only.

### 17.2 Implemented runtime capability

Repository evidence demonstrates a Twin Inspection Shell and common inspection composition for the UK Banking Industry, Enterprise Canvas and candidate import surfaces; governed Evidence links, Unknowns, Contradictions and progressive inspection are available in those bounded paths. WP-011 also records an operational evidence-bounded Enterprise Intelligence brief pipeline with validation, audit and deterministic fallback, plus separate observatory and opportunity-assistant demonstrations. These capabilities do not demonstrate FP-014 end-to-end.

The repository does **not** establish a general, durable or accepted implementation of Commercial Mission or Reinvention Timing. No runtime capability is claimed merely because this paper names it.

### 17.3 Unconfirmed or incomplete capability

The following remain explicitly unconfirmed, incomplete or planned:

- persistent user-to-employer context;
- durable Commercial Mission storage;
- governed offer-portfolio linkage;
- competitor and partner configuration;
- Market Participant Twin runtime completeness;
- Reinvention Timing computation;
- historical trend comparison; and
- function-level reinvention assessment.

### 17.4 Programme-state reconciliation

The packaged canonical baseline, `CURRENT-PROGRAMME-STATE` dated 2026-07-21, identifies WP-012 Chief Architect Knowledge Pack as the active work package and WP-011 as the runtime baseline. Newer WP2-001 and WP2-003 documents dated 2026-07-27 provide operational context for the Twin Inspection Shell and deterministic relevance projection, including bounded UK Banking and Enterprise support and an explicit Market Participant gap. They do not silently supersede the packaged programme-state authority.

Recommended reconciliation is for the programme-state owner to assess and, through its governed refresh process, incorporate accepted WP2 outcomes while retaining WP-011 or naming an accepted successor as the runtime baseline. Until then FP-014 treats the packaged baseline as canonical and the newer WP2 material as newer operational evidence, not a replacement authority.

## 18. Governance boundaries

- Canonical owners retain Evidence, Observation, identity, relationship, Twin, hypothesis, recommendation, lifecycle and promotion semantics.
- Commercial Mission is a composition input, never canonical truth about the inspected subject.
- Presentation Models and the Twin Inspection Shell remain read/presentation boundaries.
- Mission-relative narrative must retain truth class and cannot promote an inference.
- Human-supplied context remains labelled; provider output remains candidate until governed.
- Recommendations and next actions remain proportionate to Evidence and expose lineage.
- Security and access policy may restrict data visibility, but commercial preference may not hide inconvenient intelligence.
- FP-014 introduces no canonical model, persistence service, scoring engine, relationship store or duplicated runtime.

## 19. Prohibited behaviour

FP-014 prohibits:

- opaque AI relevance, opportunity or urgency scores;
- fabricated commercial consequences;
- invented supplier, competitor, incumbent or partner relevance;
- hidden behavioural personalisation;
- suppression of contradictory or commercially inconvenient Evidence;
- changing a Twin according to the user;
- presenting hypotheses as confirmed opportunities or procurement;
- predicting procurement without Evidence;
- inferring unsupported participant relationships;
- treating pressure, confidence, value, access and urgency as one indicator;
- duplicating canonical models or persistence; and
- claiming runtime capability that is not implemented and evidenced.

## 20. Commercial outcome

FP-014 moves the executive experience from:

> “What statements were imported?”

to:

> “Where should my organisation investigate transformation demand next, why is it becoming urgent, who else is involved, and what evidence supports that conclusion?”

**Executive Intelligence exists to help leaders recognise the right opportunity at the right time. Mission-aware composition ensures relevance. Reinvention Timing explains urgency. Enterprise Intelligence provides the evidence that makes both trustworthy.**

## 21. Acceptance criteria

FP-014 is complete when it demonstrates that:

- the same governed Twin can produce different Executive Workspaces for different Commercial Missions while the underlying Enterprise Intelligence remains unchanged;
- a Strategic Sales Director can immediately understand industry pressures, financial condition, prospects, Opportunity Hypotheses, competitor activity and Reinvention Timing;
- Reinvention Timing is evidence-backed and function-specific where Evidence exists, and urgency is never represented through an unexplained score;
- competitor and partner intelligence is surfaced only where governed Evidence supports it;
- every material conclusion explains relevance, urgency and evidential support;
- missing Commercial Mission context results in visible uncertainty;
- Contradictions, Unknowns and missing Evidence remain inspectable;
- FP-013 remains authoritative for trust through inspection; and
- no new canonical intelligence model or duplicated runtime is introduced.

Acceptance of this architecture remains separate from implementation acceptance. A future implementation must demonstrate deterministic composition, security controls, owned read projections, non-mutation of canonical intelligence, evidence links and honest unsupported states before it may claim conformance.
