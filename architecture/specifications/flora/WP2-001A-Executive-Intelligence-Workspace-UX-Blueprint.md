# WP2-001A — Executive Intelligence Workspace UX Blueprint

**Identifier:** WP2-001A
**Version:** 0.1
**Document type:** Canonical UX blueprint
**Status:** Proposed — implementation guidance, not evidence of runtime capability
**Date:** 2026-07-27
**Canonical owner:** Flora workspace presentation and Twin Inspection Shell boundary (Rob / CIOS)
**Governing doctrine:** [FP-013 — Executive Intelligence Workspace](../../founding-papers/FP-013-Executive-Intelligence-Workspace.md)

## 1. Authority, scope and reading rule

This blueprint is the canonical experience-design specification for applying FP-013. It belongs in `architecture/specifications/flora/` because it specifies the Flora workspace experience beneath founding doctrine and accepted architecture; it does not create doctrine, a runtime or a canonical model. **FP-013 remains Proposed.** Consequently this blueprint is also Proposed and creates no production obligation until separately accepted.

The following authorities were inspected before authoring:

- FP-013 for the executive-first doctrine and CIOS Five Questions;
- [FP-004](../../founding-papers/FP-004-Evidence-Acquisition-Standard.md), [FP-006](../../founding-papers/FP-006-Source-Quality-Standard.md), [EI-012](../../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) and [FP-009](../../founding-papers/FP-009-Hypothesis-Validation-Standard.md) for Evidence acquisition, source quality, Observations, hypotheses and preserved challenge;
- [ADR-005](../../decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md), [ADR-012](../../decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md), [ADR-013](../../decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md) and [ADR-014](../../decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md) for lineage, promotion, navigation and reasoning boundaries;
- the [Twin Presentation Model Specification](../presentation-models/Twin-Presentation-Model-Specification-v1.0.md) for presentation-payload semantics and the [Flora workspace reference architecture](../../reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md) for composition; and
- [WP1-007](../../reviews/WP1-007-Twin-Intelligence-Inspection-Runtime-Assessment.md), the current Twin Inspection Shell, Enterprise Canvas services/views, inspection adapter, routes and focused tests for repository-current runtime capability.

Where this blueprint uses “must,” it constrains a future WP2-001 implementation. It does not claim the behaviour is implemented. Evidence, Observation, Unknown, Contradiction, confidence, completeness, relationship and recommendation semantics always remain with their named owners. This document specifies their presentation and inspection, never redefines them.

## 2. Purpose

The **Executive Intelligence Workspace** is the environment in which an executive, sales director, commercial leader, analyst or architect can **understand, inspect, challenge and decide whether to trust governed Enterprise Intelligence** before using it in a decision.

It is not a dashboard that asks users to accept an AI summary, a repository browser, or a technical observability console. It is a continuous inspection experience over owner-provided governed read models. Its product promise is:

> Important intelligence is understandable quickly, and no material conclusion is a dead end: the user can inspect why it is shown, what supports it, what challenges it, what is absent and who owns it.

The workspace supports judgement rather than automating trust. The user remains able to decide “sufficient,” “insufficient,” or “sufficient only for a bounded next action.”

## 3. Trust-through-inspection doctrine

**Trust through inspection is the primary product principle.** Trust is not created by the visual polish of a summary, by repeating a recommendation, or by displaying a confidence score. A score without scope, basis and lineage is an assertion, not an explanation.

Trust emerges when the user can inspect, in business context:

| Trust concern | Required inspection answer |
| --- | --- |
| Provenance | Where did this intelligence originate, and through which governed path did it arrive? |
| Evidence | What attributable material supports this specific conclusion? |
| Source quality | What owner-defined quality assessment applies, on what basis and at what date? |
| Corroboration | Which independent or additional Evidence reinforces it? |
| Contradiction | What Evidence, Observation or position conflicts with it, and why is the conflict retained? |
| Freshness | When was the underlying material effective, observed, cut off and refreshed? |
| Completeness | Complete for which purpose and scope, according to which owner and method? |
| Uncertainty | What qualification limits the conclusion? |
| Assumptions | Which propositions are being relied upon without being presented as observed fact? |
| Reasoning lineage | How did governed inputs become an inference, hypothesis or recommendation? |
| Material unknowns | What missing knowledge could change the commercial decision, and what could resolve it? |

The UI must preserve distinctions among **Evidence**, **Observation**, **inference/projection**, **hypothesis**, **human-supplied knowledge** and **recommendation**. Absence of a contradiction is not proof of corroboration. Missing lineage must be shown as a gap, never hidden by an authoritative tone. Competing hypotheses remain visible until their owner resolves them.

## 4. Executive trust journey

The canonical sequence is a judgement loop, not a rigid wizard:

```text
UNDERSTAND             ASSESS                 INSPECT
What is it saying?  -> Is the view current? -> Why believe this conclusion?
Why commercially       Complete enough?       Evidence, provenance, quality,
significant?            Reliable enough?       corroboration and lineage
       ^                                             |
       |                                             v
DECIDE                 <-                 CHALLENGE
Sufficient for what                         What is disputed, stale,
commercial action?                          assumed, missing or alternative?
```

1. **Understand.** Lead with the Twin's identity, purpose, material conclusion and commercial significance in plain language.
2. **Assess.** Show bounded trust signals: owner-scoped confidence and completeness, freshness, assurance/acceptance state, material Unknowns and Contradictions.
3. **Inspect.** From a material statement, disclose its direct support and research/reasoning lineage without forcing a technical view.
4. **Challenge.** Present counter-evidence, assumptions, stale inputs, missing lineage, competing hypotheses and evidence needs alongside—not after—the support.
5. **Decide.** Let the user record mentally or through an existing owning workflow whether the intelligence is sufficient for the stated decision. The inspection shell itself creates no new decision or write model.

Users may move backward whenever inspection changes their understanding. Context—Twin, conclusion, decision question, active layer and prior depth—must remain stable during that movement.

## 5. The CIOS Five Questions as UX behaviour

| FP-013 question | Default behaviour | Inspection affordance | Honest failure state |
| --- | --- | --- | --- |
| **1. What is this?** | Persistent identity, Twin type, purpose, canonical owner, status/version and effective scope. | “About this Twin” discloses authority and lifecycle context. | Unsupported type or absent purpose is explicitly unavailable; never inferred from a route or title. |
| **2. What do we currently know?** | Executive narrative states the material understanding and recent change, separating observed facts from interpretation. | Each material conclusion has “Why should I believe this?” and truth-class labels. | “No governed conclusion available” with known facts and gaps; no generated filler. |
| **3. How complete and trustworthy is that understanding?** | Scoped confidence, completeness, freshness, Evidence coverage, Unknown and Contradiction signals appear together. | “Inspect basis” opens owner, scope, method, as-of date, inputs, penalties/caps and material gaps where supplied. | “Not assessed,” “not supplied,” “not applicable” and “stale” remain distinct. |
| **4. Why does it matter commercially?** | Commercial consequence follows the meaning, labelled as interpretation or recommendation as appropriate. | Inspect reasoning chain, assumptions, addressability constraints and “what not to claim.” | No commercial conclusion is manufactured from factual presence alone. |
| **5. Where should I explore next?** | Prioritised areas for inspection and related governed Twins are explained by decision relevance. | Links preserve context and resolve through governed identity, relationship and authorisation. | Unroutable or ungoverned relationships are not rendered as Twin links. |

## 6. Twin landing experience

### 6.1 Canonical anatomy and order

The landing view should answer “what, so what, and how much should I rely on this?” before exposing implementation vocabulary.

1. **Identity and purpose** — governed display name, Twin type, one-sentence purpose, status/version, canonical owner and temporal scope.
2. **Executive summary** — concise current understanding. Its truth class and generation/validation status must be visible without dominating the narrative.
3. **Commercial significance** — consequence, decision relevance and limits; not a disguised opportunity score.
4. **Trust strip** — separate confidence, completeness and freshness signals, each with scope/basis access; assurance or acceptance state where owned.
5. **Recent change** — what materially changed, effective date and comparison basis. If a general change view is unavailable, say so rather than reconstructing history.
6. **Material uncertainty** — prominent decision-relevant Unknowns, Contradictions, assumptions, stale Evidence and missing lineage. Severity comes from an owner-defined impact or explicit decision relevance, not visual guesswork.
7. **Recommended areas for inspection** — two or three explained links such as “Inspect delivery contradiction because it could reverse pursuit timing.” These are navigation prompts, not new recommendations.
8. **Material conclusions** — conclusion cards with commercial consequence and direct inspection trigger.
9. **Related governed Twins** — relationship type, target identity and reason it matters, only when the owner supplies a governed, authorised, routable relationship.
10. **Further depth** — business domains, full Evidence and governance. Technical diagnostics remain last and optional.

### 6.2 Landing-state rules

- Prefer an accepted Presentation Model when supplied; otherwise a validated generated brief may be shown as generated interpretation; otherwise use the deterministic governed overview. Inspection must never require generation.
- Never average incompatible confidence values or relabel import/package maturity as current Twin completeness.
- Show the most commercially material gap before counts of trivial gaps.
- Use counts only as orientation; the user must be able to see what the counted items are.
- “Unavailable” must state whether the cause is absence, unsupported adapter, authorisation, stale projection or owner not supplying the measure when known.

## 7. Inspectable-conclusion interaction model

### 7.1 Material conclusion unit

Every material executive statement is rendered as a coherent unit containing:

- **statement** — plain-language conclusion;
- **truth class** — for example observed fact, governed projection/inference, hypothesis, generated interpretation or recommendation, using owner-provided semantics;
- **commercial consequence** — why the statement matters to the current decision;
- **bounded trust signals** — confidence/qualification, completeness relevance and freshness where supplied;
- **challenge preview** — the highest-impact Contradiction, Unknown, assumption, stale input or lineage gap; and
- **“Why should I believe this?”** — a stable inspection action.

### 7.2 Two-interaction inspection path

```text
[Material conclusion]
  └─ 1. Why should I believe this?
       ├─ Support: Observations + Evidence + source + freshness
       ├─ Challenge: contradictions + unknowns + assumptions
       ├─ Basis: confidence/completeness scope and method
       └─ 2. Inspect lineage / open governed source
            ├─ research or reasoning chain
            ├─ corroborating and contradictory Evidence
            └─ owner view; technical references remain collapsed
```

The first interaction opens an in-context inspection panel or section; it does not navigate to diagnostics. It must provide access to:

| Required content | Presentation requirement |
| --- | --- |
| Supporting Observations | Plain-English Observation summary, date, qualification and provenance type; retain its governed identity in deeper detail. |
| Source provenance | Source title/type/reference, acquisition or package path and owning lineage. |
| Source quality | Display the FP-006 owner-provided tier/assessment and basis; do not invent a UI quality label. |
| Corroborating Evidence | Group by the conclusion it reinforces and expose independence/relationship only if supplied by the owner. |
| Contradictory Evidence | Place beside support with the competing position, status and why retained; never bury it in a generic warning count. |
| Freshness | Observation/effective/publication dates, source cut-off and refresh date as distinct fields where available. |
| Assumptions | Explicitly labelled assumptions tied to the reasoning step that depends on them. |
| Unknowns | Question, decision impact and resolution need where supplied. |
| Reasoning/research lineage | Human-readable sequence from Evidence/Observation through interpretation or hypothesis to conclusion/recommendation. |

If any required content is absent, the panel names the missing lineage or unsupported semantic. Technical IDs, raw payloads and processing logs are available only through progressive disclosure. Thus an executive can perform substantive inspection without entering technical diagnostics.

## 8. Progressive disclosure model

Progressive disclosure is **one continuous experience**, not four products or role-gated silos. Level indicates information depth, not user worth; authorised users may move directly to the depth they need while retaining the conclusion and Twin context.

| Level | Primary concern | Content and affordances |
| --- | --- | --- |
| **Executive** | Meaning and decision sufficiency | Narrative meaning; commercial consequence; scoped trust signals; material gaps; conclusion inspection triggers; decision-relevant next areas. |
| **Analyst** | Evidence and challenge | Evidence detail; business domains; Observations; governed relationships; corroboration; Contradictions; assumptions; competing hypotheses; evidence needs. |
| **Architect** | Authority and integrity | Governance; provenance; lineage; canonical ownership; authority boundaries; lifecycle/acceptance state; unavailable-provider reasons. |
| **Technical** | Runtime diagnosis | Identifiers; payloads; runtime metadata; hashes; processing diagnostics; broken references and provider failures. |

Continuity rules:

1. The Twin identity, selected conclusion and temporal scope persist in the header/breadcrumb.
2. Disclosure expands the same content object rather than opening an unrelated data explorer.
3. Back/close returns to the exact prior conclusion and scroll/focus position.
4. Labels remain stable; more detail qualifies earlier content rather than silently replacing it.
5. Authorisation may restrict data, but the experience explains that restriction without implying there is no evidence.

## 9. Information hierarchy

```text
LAYER 1 — EXECUTIVE INTELLIGENCE
  identity -> current meaning -> commercial consequence -> material trust signals
                         | inspect conclusion
                         v
LAYER 2 — BUSINESS INTELLIGENCE DOMAINS
  pressures | change | stakeholders | risks | opportunities | owner-supplied domains
                         | inspect claim / relationship
                         v
LAYER 3 — CONNECTED DIGITAL TWINS
  governed relationship -- authorised route --> governed Twin identity
                         | inspect cross-Twin basis
                         v
LAYER 4 — EVIDENCE AND GOVERNANCE
  Observations -> Evidence -> Sources -> provenance/package
  + Unknowns + Contradictions + assumptions + reasoning + ownership + diagnostics

Trust inspection also travels upward:
Evidence challenge -> domain qualification -> relationship impact -> executive decision
```

### Trust across the four layers

- **Layer 1 — Executive Intelligence:** inspect the basis and challenge of each material conclusion, not merely the summary's score.
- **Layer 2 — Business Intelligence Domains:** compare which governed facts, Observations and interpretations create the conclusion; preserve domain-specific gaps.
- **Layer 3 — Connected Digital Twins:** inspect why the relationship exists, its owner and temporal status before carrying intelligence across it. Never infer a hierarchy or create a local graph.
- **Layer 4 — Evidence and Governance:** inspect direct support, counter-evidence, provenance, source quality, research/reasoning lineage, owner and technical detail at the appropriate depth.

The layers organise attention, not storage. Example domains establish neither a taxonomy nor a new Twin type.

## 10. Evidence experience — “Why should I believe this?”

The primary Evidence experience begins with the user's conclusion and question, not with an Evidence ID, payload table or package folder.

**Default panel order:**

1. **Conclusion being inspected** and its truth class.
2. **What supports it** — attributable Observations and Evidence, grouped by reasoning role.
3. **How strong and current the support is** — source quality, corroboration and dates, each owner-scoped.
4. **What challenges it** — contradictory Evidence, competing hypotheses and stale inputs with equal visual legitimacy.
5. **What is assumed or unknown** — impact on the decision and next Evidence need.
6. **How the conclusion was reached** — readable research/reasoning lineage.
7. **Governance and technical detail** — owner, identifiers, package locations, payloads and diagnostics under disclosure.

Evidence cards should prioritise source title, relevant observation, date, contribution to the conclusion, source-quality basis and challenge status. IDs remain copyable at Architect/Technical depth. The experience must never imply source quality from brand styling, corroboration from item count alone, or certainty from the absence of visible challenge.

## 11. Confidence and completeness

Confidence and completeness answer different bounded questions. **Neither is a universal certainty score, and they must never be combined into a trust score.**

Every displayed measure must retain, where its owner supplies them:

- owner and measure name;
- scope (claim, projection, domain, package, Twin/version or decision);
- purpose/basis and method/version;
- value or qualitative qualification;
- as-of/effective/cut-off dates;
- Evidence inputs and lineage;
- caps, penalties and unresolved gaps; and
- “not assessed,” “not supplied,” “not applicable” or “stale” state.

“Inspect basis” reveals derivation rather than only a tooltip definition. A package completeness measure stays labelled package completeness after promotion. Mixed claim qualifications stay mixed rather than becoming an average. Materiality controls prominence: a missing procurement constraint that could reverse a pursuit decision appears before a low-impact missing description, provided the owning model supplies that impact. Where materiality is not governed, the UI says “materiality not assessed” and does not invent ranking.

## 12. Representative commercial journeys

### 12.1 Sales director — should we pursue this opportunity?

| Stage | Journey |
| --- | --- |
| Initial question | “Is this opportunity sufficiently evidenced and addressable to justify pursuit now?” |
| First presented | Opportunity/enterprise identity and purpose, material commercial conclusion, consequence, freshness, separate confidence/completeness, and the highest-impact gap. |
| Trust concerns | Buyer pressure may be inferred; sponsor/procurement Evidence may be missing; supplier fit may be confused with opportunity conviction. |
| Inspection path | Open “Why should I believe this?” on the pursue conclusion → inspect supporting enterprise Observations and Evidence → compare contradictory procurement Evidence and sponsor Unknown → follow only a governed Enterprise/Opportunity relationship if routable. |
| Decision outcome | “Proceed to bounded discovery,” not “opportunity proven”; use an existing owning workflow for any recorded action. |
| Unresolved uncertainty | Budget authority and procurement route remain unknown; next Evidence need is explicit. |

### 12.2 Executive — is a market conclusion reliable?

| Stage | Journey |
| --- | --- |
| Initial question | “Can I rely on the conclusion that this market is accelerating?” |
| First presented | Market/Industry Twin identity where supported, current conclusion, commercial significance, source cut-off, scoped qualification, completeness basis, recent material change and prominent counter-signal. |
| Trust concerns | Recency bias, non-independent corroboration, geographic scope and a competing stability hypothesis. |
| Inspection path | Inspect conclusion → see source-quality assessments and Evidence dates → separate corroborating from related/duplicate sources → inspect competing hypothesis and reasoning lineage → open governed sources if needed. |
| Decision outcome | Use conclusion for scenario planning but not a market-entry commitment until geographic Evidence is refreshed. |
| Unresolved uncertainty | Industry Twin adapter/general route is not implemented today; the future journey depends on an owner-approved read adapter. Geographic representativeness remains unresolved in the scenario. |

### 12.3 Analyst — challenge a recommendation

| Stage | Journey |
| --- | --- |
| Initial question | “Which premise makes this recommendation fragile, and what Evidence is missing?” |
| First presented | Recommendation labelled separately from Evidence and inference; consequence, assumptions, qualification, freshness and material Unknown/Contradiction preview. |
| Trust concerns | Recommendation may depend on an old Observation, an untested hypothesis or human-supplied knowledge. |
| Inspection path | Open recommendation lineage → traverse reasoning steps to supporting Observations → inspect human-supplied label and stale source → compare retained Contradiction → identify the owner-stated next Evidence need. |
| Decision outcome | Challenge the recommendation through an existing feedback/review owner workflow; do not mutate canonical state in the shell. |
| Unresolved uncertainty | No universal reasoning-lineage renderer is proven across all Twin/recommendation types; the gap stays visible rather than reconstructed locally. |

## 13. Existing-capability assessment (repository at 2026-07-27)

“Implemented” below means executable in this repository, not proven deployed or populated in every environment.

| Capability | Architectural intent | Implemented runtime capability found | Current programme-state gap / UX treatment |
| --- | --- | --- | --- |
| **Twin Inspection Shell** | One adapter-driven presentation/orchestration boundary. | Implemented route fallback, `InspectionProfile`, `InspectionSection`, Enterprise adapter, ordered/conditional sections, truth-class/freshness metadata and access/not-found states. | The shell is minimal and Enterprise-only; its profile is metric-first, material conclusions are not first-class contract objects, section anchors/providers are uneven, and trust inspection is not fully composed. Evolve it; do not create a new runtime. |
| **Enterprise Canvas** | Accepted primary Living Enterprise Twin navigation and read-only view. | Implemented overview, commercial material, Model Explorer/tile detail, claim-to-Observation/Evidence/Source/package lineage, Unknowns, Contradictions, freshness and governed feedback candidates. | Strongest experience foundation, but conclusion-centred inspection, source-quality/corroboration presentation, scoped completeness basis and continuous depth need alignment. Do not rebuild existing Canvas or lineage views. |
| **Inspection adapter** | Owner-provided projections composed without copying canonical records. | Enterprise adapter reuses `EnterpriseCanvasService`, calculates presentation counts, exposes research lineage and omits unavailable sections. | No type-neutral route resolver or adapters for other governed Twin types; some aggregate strings risk appearing more authoritative than their heterogeneous bases. Add presentation semantics only where owner-backed. |
| **Evidence views** | Evidence reachable near material conclusions. | Canvas tile lineage exposes Observations, Evidence, Sources, human knowledge, Unknowns, Contradictions, package location, missing lineage and technical references; generic and specialist Evidence routes also exist. | Views are fragmented; current Canvas lineage does not consistently expose FP-006 quality basis, explicit corroboration role, assumptions or full reasoning lineage. Converge navigation/labels rather than duplicate Evidence storage. |
| **Executive Intelligence Brief** | Optional evidence-bounded executive interpretation. | Implemented, availability-dependent, validated/safe-fallback behaviour over governed state; deterministic Canvas overview remains available. | Generated/accepted/deterministic opening policy must be made legible. It cannot replace canonical fact or be required for inspection. |
| **Completeness and confidence read models** | Scoped, inspectable owner measures. | Import maturity/completeness is implemented for candidate/package context; Canvas supplies acceptance state, qualitative qualifications, dates, lineage and uncertainty counts. | No accepted universal post-promotion Twin completeness or confidence aggregation. Present existing scoped measures; do not invent one. |
| **Related Twins and relationships** | Navigate governed identities and relationships. | Relationship/nested markers and specialist links exist; models contain broader relationship structures. | A universal authorised, routable cross-Twin chain is not implemented. Render only owner-supplied resolvable targets. |
| **Timeline/change history** | Conditional owner-provided history. | Import, feedback, banking and financial histories exist in separate owning workflows. | No universal Twin change-history projection. Link to owners; do not synthesize a feed. |
| **Technical inspection** | Last disclosure level. | IDs, package references, runtime metadata and diagnostic surfaces exist across shell, Canvas and specialist pages. | Current fragmentation can force users into technical surfaces. Bring existing business-readable lineage nearer without moving or copying diagnostics. |

### 13.1 Capability conclusion

The architectural intent is substantially aligned with this blueprint, and the repository already contains the runtime foundation and much of the Evidence path. The principal product gap is **experience composition**, not missing canonical intelligence infrastructure: a material executive conclusion is not yet a stable inspection unit spanning summary, support, challenge, measure basis and lineage. Universal Twin coverage, route resolution and consistent owner-scoped measures remain future work.

## 14. UX principles

1. **Trust through inspection** — every material conclusion has a purposeful path to support and challenge.
2. **Understanding before detail** — establish what the intelligence means before showing its structure.
3. **Narrative before metrics** — state the conclusion and consequence; metrics qualify rather than substitute for meaning.
4. **Commercial meaning before implementation terminology** — use business language first, retaining canonical terms at deeper levels.
5. **Evidence without clutter** — keep Evidence near conclusions through disclosure, not a wall of citations.
6. **Uncertainty preserved** — never resolve, average away or euphemise uncertainty.
7. **Material gaps made visible** — decision-changing absence outranks cosmetic completeness.
8. **Governed relationships only** — no UI-local relationship or Twin hierarchy.
9. **One inspection experience across Twin types** — adapters compose owned projections; they do not become separate products.
10. **Progressive disclosure rather than separate products** — executive, analyst, architect and technical depth share context and navigation.

## 15. Acceptance criteria for future implementation

A future WP2-001 increment is acceptable only when evidence demonstrates:

1. In moderated or instrumented testing, at least 4 of 5 representative executive/commercial users can state a supported Twin's purpose and material conclusion accurately after approximately **30 seconds** on the landing view.
2. From every rendered material conclusion in the pilot, supporting Evidence is reachable in **no more than two user interactions**, excluding authentication; automated route tests assert the links and manual testing confirms business-readable content.
3. Every material Contradiction and material Unknown supplied by the adapter is visible on the landing view or first conclusion-inspection panel **without Technical disclosure**; no supplied item is hidden only in diagnostics.
4. Every displayed confidence or completeness value/qualification exposes its owner, scope, basis/method, date and gaps when supplied; unsupported fields show an honest absence state. No universal or combined trust score appears.
5. Users can distinguish Evidence, Observation, inference/projection, hypothesis, human-supplied knowledge and recommendation by adjacent labels and an accessible explanation; a content audit finds no unlabeled recommendation presented as fact.
6. Every Related Twin link is produced from a governed relationship and governed target identity, passes authorisation-aware route resolution and has a valid supported destination; unresolved objects are not rendered as Twin links.
7. The increment runs through the **existing Twin Inspection Shell and Enterprise Canvas providers**; architecture/code review confirms no new runtime, persistence owner, canonical data model or Twin type.
8. Keyboard users can open/close inspection depth, follow Evidence and return to the originating conclusion with visible focus and preserved context; headings and link purpose remain meaningful to assistive technology.
9. Stale Evidence, missing lineage, unavailable assessment, contradictory Evidence and competing hypotheses have tested empty/adverse states and are never converted into positive trust signals.
10. The pilot traces at least one conclusion end to end: rendered statement → Observation → Evidence → Source/provenance → research/reasoning lineage, while retaining canonical ownership at every step.

## 16. Open questions, assumptions and Evidence gaps

### Assumptions

- The existing Twin Inspection Shell remains the governed presentation/orchestration boundary and may evolve without transferring canonical ownership.
- Enterprise Twins remain the first supported scope because the Enterprise Canvas provides the strongest implemented read model.
- Owner-provided materiality, quality, confidence and completeness semantics may be rendered but not recomputed by the UI.
- Existing feedback, review, promotion and decision workflows remain the owners of mutations; inspection is read-first.

### Open questions requiring owner decisions or runtime evidence

1. Which existing/accepted object marks a statement as **material**, and how is decision-specific materiality supplied when absent?
2. Which provider supplies explicit corroboration relationships and independence, rather than leaving the UI to infer them from Evidence counts?
3. Where are assumptions and reasoning steps addressable consistently for deterministic Canvas projections, generated briefs and accepted Presentation Models?
4. Should the canonical inspection URL remain the Canvas path, use the current legacy fallback, or adopt a type-neutral alias that redirects without duplicating rendering?
5. What is the accepted precedence among an accepted Presentation Model, validated generated brief and deterministic overview, including staleness behaviour?
6. Which owner-approved confidence/completeness methods expose scope, basis, method version and gaps through current read models?
7. How should authorisation-filtered Evidence be described so users distinguish “restricted” from “absent” without leaking sensitive facts?
8. Which governed relationships currently guarantee target identity, relationship semantics, authorisation and a supported inspection adapter?
9. Production usability, accessibility, latency, data population and cross-browser performance are not proven by repository inspection and require validation.

These are visible delivery gates, not invitations for the presentation layer to invent semantics.

## 17. Recommended scope for WP2-001

### Smallest evidence-based implementation increment

Implement **one conclusion-centred trust path for supported Enterprise Twins inside the existing Twin Inspection Shell**, reusing the Enterprise Canvas and its lineage service:

1. Add a presentation-only material-conclusion contract referencing existing Canvas content and owner records; do not persist copied claims.
2. Reorder the landing experience to identity/purpose → narrative conclusion → commercial consequence → scoped trust strip → material challenge → inspection recommendations.
3. Add “Why should I believe this?” to each pilot material conclusion and compose the existing Canvas lineage response into an in-context business-readable panel.
4. Surface existing Observations, Evidence, Sources, dates, Unknowns, Contradictions, human-supplied labels and missing-lineage state; add source-quality, corroboration, assumptions and reasoning only when current owners supply them.
5. Make current confidence, completeness/acceptance and freshness presentations inspectable with scope and honest unavailable states; create no new score.
6. Preserve Research Package/Import Run links and technical references at Architect/Technical depth.
7. Pilot one governed promoted Enterprise Twin and validate the acceptance criteria, adverse states and two-interaction path.

### Explicitly out of scope

- React, CSS redesign or a new UI framework;
- a new runtime, store, canonical model, Evidence semantic or Twin type;
- a universal trust, confidence, completeness, maturity or Evidence-density score;
- universal graph, timeline or change-feed construction;
- Industry, Market Participant or Opportunity adapters until owner read models and identities satisfy the contract;
- copying Canvas/Evidence data into the shell; and
- automatic resolution of Unknowns, Contradictions or competing hypotheses.

This increment is smaller than a workspace rebuild, does not recommend capability already present, and directly tests the doctrine's critical claim: a commercial user can understand a material conclusion quickly and personally inspect why it deserves—or does not deserve—trust.
