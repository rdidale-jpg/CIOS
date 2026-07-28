> **“Executives should understand before they inspect.”**

# WP2-003 — Executive Intelligence Workspace

**Identifier:** WP2-003
**Version:** 0.1
**Document type:** Canonical Executive Experience Blueprint
**Status:** Proposed — implementation guidance, documentation-only and non-runtime
**Date:** 2026-07-28
**Canonical owner:** Repository Work Package collection (Rob / CIOS)
**Implements:** [FP-014 — Mission-Aware Executive Intelligence Composition](../../founding-papers/FP-014-Mission-Aware-Executive-Intelligence-Composition.md)
**Consumes:** [FP-012 — Enterprise Reinvention Intelligence](../../founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md), [FP-013 — Executive Intelligence Workspace](../../founding-papers/FP-013-Executive-Intelligence-Workspace.md) and FP-014
**Release-profile membership:** None — review context only

## 1. Authority, scope and reading rule

WP2-003 is the canonical experience blueprint for composing the architectural intent of FP-014 into one coherent Executive Intelligence experience. It governs information architecture, experience sequence, composition behaviour, navigation, interaction, explainability and progressive disclosure. It does not specify screens, layouts, colours, styling, widgets, frameworks, presentation technology or runtime implementation.

FP-012, FP-013 and FP-014 remain authoritative for their respective Enterprise Reinvention Intelligence, executive inspection and mission-aware composition doctrine. This blueprint consumes their terms and constraints; it does not redefine Enterprise Intelligence, Executive Inspection, Evidence, Observation, Commercial Mission, Reinvention Timing, governance or any canonical model. Because all three Founding Papers are currently Proposed or Review material, WP2-003 is also Proposed. Merge does not accept those papers, create runtime capability or add this document to a production Knowledge Pack.

The repository convention established by [WP2-001A](WP2-001A-Executive-Intelligence-Workspace-UX-Blueprint.md) locates Flora experience work packages in `architecture/specifications/flora/` and uses the `WP2-NNN-Title.md` identifier-and-title filename. “Must” and “should” in this document constrain a future conforming implementation; they are not claims that the capability exists.

## 2. Purpose and governing principle

The Executive Intelligence Workspace provides immediate understanding whenever an executive opens a supported Twin. Inspection follows understanding and is entered only when required.

> **“Understanding before interaction.”**

The Workspace must be:

- understandable before explorable;
- commercially meaningful before technically complete;
- Evidence-first rather than AI-first;
- progressively inspectable;
- deterministic in composition;
- transparent in uncertainty;
- mission-aware without mission bias; and
- explainable rather than scored.

It is composed executive information, not a collection of application screens. It should feel like reading an executive briefing rather than inspecting a dashboard.

## 3. Executive journey

```text
Select Twin
    ↓
Executive Intelligence Workspace
    ↓
Understand
    ↓
Investigate
    ↓
Inspect Evidence
    ↓
Govern
    ↓
Act
```

**Every supported Twin begins with an Executive Intelligence Workspace. Inspection is entered only when required.** “Govern” and “Act” lead to existing owner-governed workflows; the Workspace does not create a decision, promotion or write model.

The journey is progressive, not a mandatory wizard. An executive may return from Evidence inspection to the same conclusion, investigation and Twin context. The experience first establishes meaning, then helps the executive choose what deserves attention, then permits deeper inspection sufficient to govern or act responsibly.

## 4. Executive narrative and questions

The Workspace tells one coherent story in this natural progression:

```text
Current state
    ↓
Commercial significance
    ↓
Transformation pressure
    ↓
Priority organisations
    ↓
Opportunity hypotheses
    ↓
Evidence
    ↓
Recommended investigation
```

The narrative must answer:

1. **What is happening?** State current conditions and material change, distinguishing observation, interpretation and hypothesis.
2. **Why is it relevant?** Explain commercial significance and name the Commercial Mission inputs used; missing context remains unresolved.
3. **Why now?** Explain evidence-backed transformation pressure and Reinvention Timing without predicting procurement.
4. **Why should I believe it?** Expose Evidence, lineage, freshness, Contradictions, Unknowns and assumptions.
5. **What deserves my attention first?** Explain investigation priority rather than substituting an opaque score.

The fifth question transforms understanding into prioritisation. Prioritisation is a reproducible composition decision, not a new intelligence judgement.

## 5. Executive Experience Composition

The following are compositions of owner-provided intelligence within the common narrative. They are not screens, canonical objects or promises that missing intelligence will be generated. A composition with insufficient owner-provided intelligence is omitted or shown as unresolved according to materiality; it is never completed for symmetry.

### 5.1 Intelligence Coverage

**Purpose:** Immediately demonstrate intelligence richness while preventing volume from implying quality or completeness.

Expose, where supplied, Observations, Evidence, enterprises, Market Participants, Opportunity Hypotheses, Unknowns, Contradictions and freshness. Counts retain owner scope and lead to the counted intelligence. Coverage must distinguish absent, restricted, stale, unsupported and not assessed states.

### 5.2 Industry / Enterprise Outlook

**Purpose:** Explain current conditions in commercially understandable language.

Compose the available financial outlook, transformation themes, operating pressures, technology pressures, customer trends, regulatory pressure, workforce conditions and investment climate. Preserve the boundary between industry synthesis and enterprise-specific claims, and label disclosed fact, interpretation, estimate and missing Evidence distinctly.

### 5.3 Reinvention Timing

**Purpose:** Explain urgency as the evidence-backed proximity to material transformation, using FP-014's definition and presentation vocabulary without creating a canonical lifecycle.

Expose maturity, principal drivers, affected business functions, supporting Evidence, Contradictions and historical movement where comparable governed history exists. If no history exists, state **“No governed historical comparison is available.”** If Evidence cannot support an assessment, show it as unresolved. Never infer urgency from confidence, supplier preference, source volume, opportunity scoring or procurement prediction.

### 5.4 Priority Prospects

**Purpose:** Identify where executive investigation should begin.

Each prospect explains, where governed intelligence exists:

- organisation and industry;
- commercial relevance and why now;
- Reinvention Timing;
- transformation themes and affected business functions;
- relevant offers;
- competitor and partner landscape;
- Evidence, Contradictions and Unknowns; and
- recommended investigation.

Priority Prospects are investigation priorities. **They are not lead scores and not opportunity predictions.** Relevance or offer alignment is unresolved when the required Commercial Mission field or governed linkage is absent.

### 5.5 Opportunity Hypotheses

**Purpose:** Present evidence-backed opportunities for executive investigation.

Every hypothesis explains why it exists, why now, supporting Evidence, affected business functions, Commercial Mission relevance and recommended investigation. It retains its owner-defined lifecycle, validation state, Contradictions, Unknowns and lineage. It must never be presented as confirmed procurement or a procurement prediction.

### 5.6 Competitor Landscape

**Purpose:** Present evidence-backed competitor activity.

Show governed participant identity, contextual role, evidenced activity or position, affected industry/enterprise/opportunity, freshness, reasoning limits, Contradictions and Unknowns. Competitor presence informs investigation; it does not suppress a prospect or establish employer disadvantage. When no link is supported, state **“No governed evidence is currently available.”**

### 5.7 Partner Landscape

**Purpose:** Present ecosystem opportunities.

Show evidence-backed alliances, relationships, delivery routes and partner-linked hypotheses with their scope and limits. Partner presence never implies access, consent, delivery capacity or viable route without supporting Evidence.

### 5.8 Commercial Watchlist

**Purpose:** Highlight changes likely to alter executive priorities.

Compose monitored leadership, strategy, financial, regulatory, contract, programme, competitor, partner and Evidence-refresh changes when owner-provided intelligence supports them. Inclusion is a transparent monitoring decision, not proof of an opportunity or authority to predict one.

### 5.9 Coverage & Limitations

**Purpose:** Demonstrate intellectual honesty.

Expose coverage gaps, stale intelligence, unsupported conclusions, missing enterprises, missing or incomplete Commercial Mission and unresolved Evidence. Also preserve material Contradictions, assumptions, access restrictions and unavailable owner projections. Limitations appear in the narrative where they affect a conclusion as well as in this composition; progressive disclosure must not become concealment.

## 6. Information Priority model

Where executive attention is limited, use this default semantic priority:

1. Industry condition
2. Reinvention Timing
3. Opportunity Hypotheses
4. Priority Prospects
5. Competitor Landscape
6. Partner Landscape
7. Commercial Watchlist
8. Coverage & Limitations

This ordering organises attention; it does not rank truth or create a fixed layout. Intelligence Coverage establishes orientation before the ordered narrative, while material limitations are disclosed adjacent to affected conclusions regardless of their eighth-place summary composition. Detailed inspection remains progressively available.

A declared Commercial Mission may reorder, group or foreground available compositions under section 7. The resulting order and its basis must be inspectable. In the absence of sufficient mission context, retain this default and identify mission-relative relevance as unresolved rather than infer user intent.

## 7. Composition Behaviour model

The controlling flow remains FP-014's architecture:

```text
Governed Enterprise Intelligence
→ Twin Inspection Shell
→ Common Executive Inspection Contract
→ declared Commercial Mission
→ deterministic mission-aware composition
→ Executive Intelligence Workspace
→ Evidence inspection
```

Commercial Mission may determine only:

- ordering;
- prominence;
- grouping;
- narrative emphasis; and
- investigation priorities.

Commercial Mission never determines:

- truth;
- Evidence;
- urgency;
- confidence; or
- Observations.

**Enterprise Intelligence remains authoritative.** Composition must also preserve provenance, freshness, lineage, Contradictions, Unknowns, assumptions, truth class and canonical ownership.

Composition is deterministic when the same governed inputs, declared Commercial Mission, versioned composition rules and effective time produce the same result and inspection basis. The Workspace exposes the relevant mission fields and composition rationale. It does not infer missing mission context from behaviour, copy canonical records into a mission store, or promote generated narrative. Security may restrict visibility; commercial preference may not suppress inconvenient intelligence.

## 8. Twin consistency

Industry Twins, Enterprise Twins, Market Participant Twins and Opportunity Twins must use the same Executive Experience model **when they are supported by an owner-approved read projection, routable governed identity and inspection adapter**. Only the composed intelligence changes. Executives should never need to learn different interaction patterns for different Twin types.

Consistency does not assert that every named Twin type is implemented. It does not permit a presentation layer to fabricate a Twin, relationship, hierarchy or missing adapter. An unsupported type receives an honest unsupported state, not a locally invented experience.

## 9. Navigation and progressive disclosure

```text
Executive
    ↓
Analyst
    ↓
Architect
    ↓
Technical
```

These are depths in one continuous experience, not separate applications or role-value tiers:

| Depth | Executive purpose |
| --- | --- |
| Executive | Understand current meaning, significance, timing, priorities and material limitations. |
| Analyst | Investigate domains, Evidence, relationships, assumptions, Unknowns and Contradictions. |
| Architect | Inspect canonical ownership, provenance, lineage, composition-rule version and governance boundaries. |
| Technical | Diagnose identifiers, owner-provided projections, assessment inputs and runtime metadata where implemented. |

Navigation must preserve the selected Twin, conclusion, Commercial Mission basis, effective scope and prior position. Deeper disclosure qualifies the same content rather than silently replacing it. Returning restores the originating context. Governed cross-Twin navigation carries the investigation question and makes any changed Twin scope explicit. The executive should never feel they have entered a different application.

## 10. Interaction Principles

Every interaction should either **improve understanding** or **improve confidence**. No interaction should increase cognitive effort without increasing executive understanding.

Consequently:

1. Narrative meaning precedes metrics and technical structure.
2. Material conclusions provide direct, in-context access to support and challenge.
3. Evidence access starts from the conclusion, not from an identifier or document browser.
4. Progressive disclosure defers detail but never hides the basis of relevance or prevents inspection.
5. Context, labels and truth class remain stable across depth changes.
6. Counts orient; they never substitute for meaning, quality or completeness.
7. Empty, stale, restricted, unresolved and unsupported states remain distinct.
8. Recommendations are proportionate to Evidence and lead to investigation or an existing owner workflow.
9. AI-generated interpretation is labelled and bounded; inspection never depends upon generation.
10. The Workspace creates no mutation, relationship, score or canonical judgement through interaction alone.

## 11. Explainability model

Every executive conclusion exposes this path:

```text
Observation
    ↓
Interpretation
    ↓
Commercial relevance
    ↓
Evidence
    ↓
Inspection
```

This is an experience order, not a replacement for canonical reasoning lineage. Where the owner supplies a different or more complete lineage, including ADR-005's Recommendation → Hypothesis → Signal → Observation → Evidence → Source chain, that lineage remains intact and inspectable.

Every major conclusion must answer:

- **Why this?** Identify the observed change, affected subject and selection rationale.
- **Why now?** Expose the dated timing assessment, drivers, freshness and counter-evidence.
- **Why me?** Name the declared Commercial Mission fields and governed links that establish relevance; otherwise say unresolved.
- **Why believe it?** Expose Evidence, source/provenance, truth class, lineage, assumptions, Unknowns and Contradictions.

The reproducible composition path is: governed conclusion → declared mission field(s) → versioned composition rule → workspace placement → owner-governed Evidence inspection. Missing steps remain visible. Explainability qualifies conclusions; it must not collapse confidence, completeness, urgency, relevance or conviction into a universal score.

## 12. Workspace Completion model

The Executive Workspace has achieved its purpose when the executive can confidently answer:

- What has changed?
- Why does it matter?
- Why now?
- What deserves investigation?
- What Evidence supports that conclusion?
- What remains uncertain?

Completion means sufficient understanding to choose a bounded next investigation, governance route or action. It is not completion of the Twin, proof of an opportunity, acceptance of a recommendation or resolution of every Unknown. The Workspace should make a decision to inspect no further as legitimate as deeper investigation when the visible limitations permit it.

## 13. Non-goals

The Executive Workspace is not:

- a BI dashboard;
- a CRM;
- a procurement prediction engine;
- a sales forecasting tool;
- an AI recommendation engine; or
- a replacement for Evidence inspection.

Its purpose is executive understanding. WP2-003 also introduces no architecture, canonical intelligence, scoring model, persistence service, relationship store, runtime capability, UI technology or visual design system.

## 14. Future capability hooks

The common experience reserves non-prescriptive extension points for persistent Commercial Mission, Enterprise Twins, Market Participant Twins, Opportunity Twins, Scenario Analysis and Executive Briefs. A hook means only that future owner-approved intelligence may enter the same composition, navigation and explainability contracts. It does not select storage, schema, API, framework or presentation technology and does not claim delivery.

Future Executive Briefs remain interpretations over governed intelligence and may accelerate understanding, but cannot become the only inspection path or replace the deterministic evidence-bounded experience. Persistent Commercial Mission requires separate architecture and governance; this blueprint does not create it.

## 15. Acceptance Criteria

A future implementation conforms only when a Strategic Sales Director can open a supported Industry Twin and, within two minutes, accurately understand:

- industry condition;
- transformation pressures;
- Reinvention Timing;
- Priority Prospects;
- Opportunity Hypotheses;
- competitor landscape;
- partner landscape;
- where investigation should begin;
- Evidence supporting every material conclusion; and
- remaining uncertainty.

Validation must additionally demonstrate that:

1. every supported Twin begins in the common Executive Intelligence Workspace and preserves context through Executive → Analyst → Architect → Technical disclosure;
2. every material conclusion provides an accessible path to its Observation, interpretation, commercial relevance, Evidence, challenge and owning inspection route;
3. Commercial Mission changes only ordering, prominence, grouping, narrative emphasis and investigation priority, with its fields and applied rule inspectable;
4. identical governed inputs, Commercial Mission, composition-rule version and effective time yield identical composition;
5. missing mission context, Evidence, history and adapters produce honest unresolved or unsupported states rather than inferred content;
6. Priority Prospects remain investigation priorities, Opportunity Hypotheses remain hypotheses and no lead score or procurement prediction is presented;
7. Unknowns, Contradictions, stale intelligence and limitations are visible at the depth where they affect executive understanding;
8. Industry, Enterprise, Market Participant and Opportunity Twin implementations use the same experience contract when supported, without duplicated runtimes or UI-local models;
9. architecture review finds no new canonical model, runtime, persistence owner, score, relationship or presentation technology in this blueprint; and
10. repository link, documentation and applicable automated validation pass.

The two-minute criterion requires moderated or instrumented validation against populated, supported Industry Twin intelligence. Repository documentation review alone cannot claim that outcome.

## 16. Existing capability and implementation gaps

Repository evidence distinguishes target experience from delivered runtime:

| Area | Repository evidence | Gap retained by WP2-003 |
| --- | --- | --- |
| Twin Inspection Shell | WP1-007 and WP2-001A record an implemented presentation/orchestration shell, Enterprise adapter and bounded UK Banking/import paths. | No demonstrated common Executive Experience across all named Twin types; Market Participant and Opportunity coverage remain unconfirmed. |
| Enterprise Canvas | ADR-013 and WP2-001A establish the strongest implemented read/navigation and Evidence-lineage foundation. | Conclusion-centred composition and continuous context-preserving depth are not universally proven. |
| Executive Brief | WP-011 programme evidence and WP2-001A record an evidence-bounded brief pipeline with validation and deterministic fallback. | Brief availability and validation do not implement FP-014 composition or make generated interpretation authoritative. |
| Commercial Mission | FP-014 defines a declared composition input and distinguishes it from ADR-015 Runtime Mission Context. | No general durable or accepted Commercial Mission implementation is established. |
| Reinvention Timing | FP-014 defines an evidence-led presentation assessment and boundaries. | No accepted canonical vocabulary, general computation or historical comparison capability is established. |
| Relevance projection | The existing WP2-003 relevance pre-flight records a bounded deterministic presentation projection for candidate import review. | That local projection is not the Executive Intelligence Workspace, a Commercial Mission model or canonical classification authority. |
| Programme state | `CURRENT-PROGRAMME-STATE` names WP-012 as active and WP-011 as runtime baseline. | Newer WP2 evidence has not been incorporated through the programme-state owner's governed refresh. |

The implementation path is therefore to compose over the existing Twin Inspection Shell, Enterprise Canvas, owner-provided projections and Evidence routes. This document does not authorise a parallel workspace or duplicate intelligence infrastructure.

## 17. Validation summary

### Authorities consulted

- FP-012 for Enterprise Reinvention Intelligence boundaries;
- FP-013 and WP2-001A for executive-first inspection, Twin Inspection Shell, progressive disclosure and trust-through-inspection;
- FP-014 for Commercial Mission, deterministic composition, Reinvention Timing, Strategic Sales composition and runtime-gap boundaries;
- accepted ADR-004, ADR-005, ADR-012, ADR-013 and ADR-015 for human-knowledge labels, recommendation lineage, promotion boundaries, Canvas navigation and Runtime Mission Context separation;
- ADR-014 and ADR-024 as repository-recorded accepted reasoning/runtime decisions, noting their internally inconsistent draft headers;
- the Twin Presentation Model Specification and Flora workspace reference architecture for presentation and composition ownership;
- WP1-007, WP-011 capability evidence, the existing WP2-003 relevance pre-flight and implemented-work summaries in WP2-001A/FP-014; and
- `CURRENT-PROGRAMME-STATE` as programme-state authority.

### Boundary validation

- FP-012, FP-013 and FP-014 remain authoritative and are linked rather than duplicated.
- Commercial Mission changes composition, never truth or governed intelligence.
- Evidence, uncertainty, Contradictions, Unknowns, lineage and canonical ownership remain first-class.
- The blueprint describes semantic experience and behaviour, not screens, visual design or implementation technology.
- Named future capabilities and unsupported Twin types are explicit hooks or gaps, not runtime claims.
- No canonical intelligence, architecture, score, persistence, relationship or procurement-prediction capability is introduced.

### Assumptions

- The Work Package naming/location convention established by WP2-001A remains applicable to WP2-003.
- The existing Twin Inspection Shell remains FP-013's presentation/orchestration boundary.
- Owner-provided read projections can be composed without transferring ownership or copying canonical state.
- “Supported Twin” means an authorised, routable governed identity with an owner-approved read projection and inspection adapter.

### Validation disposition

**Recommend Merge**, subject to repository validation passing. This recommendation accepts WP2-003 only as Proposed canonical experience guidance; it does not accept FP-012, FP-013 or FP-014, alter production profiles, or claim implementation completion.

## 18. Implementation summary

- **Files changed:** this blueprint and the Flora architecture-specification register.
- **Canonical location:** `architecture/specifications/flora/WP2-003-Executive-Intelligence-Workspace.md`, following the existing WP2 work-package convention.
- **Authorities consulted:** those enumerated in section 17, with programme state sourced only from its canonical baseline.
- **Architectural boundaries preserved:** Enterprise Intelligence and canonical owners remain authoritative; the Workspace is a deterministic read composition and inspection experience.
- **Doctrine reused:** executive-first inspection, trust through inspection, progressive disclosure, mission-aware composition, Evidence lineage, uncertainty preservation and Enterprise Canvas/Twin Inspection Shell boundaries.
- **Assumptions made:** only those explicitly listed in section 17.
- **Implementation gaps identified:** common Twin coverage, persistent Commercial Mission, governed offer linkage, general Reinvention Timing/history, conclusion-centred inspection and programme-state reconciliation.
- **Validation completed:** authority/status reconciliation, terminology and boundary review, Markdown/link validation and repository tests listed in the delivery record for this change.
