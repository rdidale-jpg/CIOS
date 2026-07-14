# Commercial Digital Twin Research Agent Guide

**Status:** Canonical Markdown guidance  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11  
**Historical review copy:** `architecture/research/Commercial-Digital-Twin-Research-Agent-Guide.docx`

## Authority and scope

This Markdown file is the canonical Research Agent Guide for Commercial Digital Twin and Research GPT operation. The DOCX file in this folder is a historical review copy and must not be edited as source. This guide aligns with [FP-010](../founding-papers/FP-010-Knowledge-Pack-Architecture.md), [FP-011](../founding-papers/FP-011-Knowledge-Exchange-Architecture.md), [EI-013](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md), the [Knowledge Pack Specification](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md), the [Twin Presentation Model Specification](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) and the [Industry Twin Lifecycle Specification](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md).

Do not change runtime prompts or application code when applying this guide. Research GPT output is candidate intelligence until accepted through the relevant CIOS governance path.

## Research GPT operating model

The Research GPT must produce Knowledge Pack-compatible outputs containing:

- governed Twin candidate data;
- atomic Observations;
- Twin Presentation Model payloads;
- enterprise topology;
- executive themes;
- stakeholder landscape;
- commercial relevance;
- Unknowns;
- Contradictions;
- Recommendations;
- lineage manifest;
- validation report;
- release manifest;
- completion report.

The GPT must use enterprise-specific language and avoid generic summaries where the evidence supports a named enterprise, stakeholder, business unit, market context or decision. Facts, interpretation and projection must be separated. Projections must be labelled as projections, human-supplied knowledge must be labelled as human-supplied knowledge, and every material assertion must carry explicit truth status, source cut-off, confidence and freshness.

## Evidence, truth and lineage rules

The Research GPT must:

1. assign stable IDs to Observations, Hypotheses, Evidence references, Recommendations, Unknowns, Contradictions, Presentation Models and release artefacts;
2. preserve Unknowns and Contradictions rather than smoothing them into a single narrative;
3. link Recommendations to inspectable Hypotheses and Evidence;
4. keep factual claims separate from interpretation, inference and commercial judgement;
5. label unsupported, low-confidence or stale material instead of upgrading it into fact;
6. avoid unsupported profit-centre or cost-centre classification;
7. avoid raw worksheet labels, database labels, internal extraction labels or staging labels in executive-facing outputs;
8. state what not to claim when evidence is insufficient or contradictory.

## Audience profile: `strategic_sales_director_v1`

The default executive-facing Presentation Model audience is `strategic_sales_director_v1`. Output for this audience must answer:

- Who?
- Why now?
- Why them?
- What evidence?
- What remains unknown?
- What contradicts the current view?
- What next?
- What not to claim?

The answer must be commercially relevant without overstating certainty. It should support sales strategy, account prioritisation, executive conversation planning and learning actions.

## Knowledge Pack publishing guidance

When asked to prepare a governed release, the Research GPT must produce or populate the text-based Knowledge Pack release structure:

```text
manifest.json
metadata.json
validation.json
lineage.json
checksums.sha256
payload/twin/
payload/presentation-model/
attachments/
```

The GPT must not be required to create a ZIP archive unless an existing text-based publishing workflow explicitly assigns that responsibility. The package must include a release manifest, lineage manifest, validation report and completion report. Attachments are used only where appropriate and must preserve source, rights, handling and lineage metadata.

Knowledge Pack acceptance means repository handling validity; it does not make GPT-authored content canonical fact. Unsupported content must be quarantined or labelled, and Presentation Models remain governed interpretations unless separately accepted by an owning model process.

## Industry Research GPT guidance

The Industry Research GPT must:

- review the Flora Change Queue before publishing;
- distinguish signal from material change;
- create atomic Industry Observations;
- publish incremental Industry Knowledge Packs;
- run weekly triage;
- prepare monthly governed releases;
- perform quarterly structural assurance;
- trigger event-driven releases for material events;
- propose cross-Twin impacts where industry change affects Enterprise, Market Participant, Opportunity or Relational Twins;
- make no silent updates to related Twins.

Cross-Twin impact proposals are proposals until accepted by the relevant owning Twin or model process.


## Enterprise Intelligence Research Sprint lifecycle

**Status:** Review methodology extension derived from AL-001 and EOD-001. This section is architecture only and does not change runtime prompts, production Researcher packs or accepted model state.

Future Research Sprints must not assume the opportunity is already known. The lifecycle is:

```text
Enterprise
    ↓
Enterprise Opportunity Discovery
    ↓
Opportunity Selection
    ↓
Research Object Validation
    ↓
Enterprise Understanding
    ↓
Research-to-Positioning Handover
    ↓
Opportunity Positioning
    ↓
Positioning Insight Deepening
    ↓
Decision Envelope
    ↓
Provider Fit (outside public research)
    ↓
Executive Pursuit
```

### Stage definitions

1. **Enterprise** — Begin with the named enterprise and its public-domain context, not with a procurement reference or assumed buying event.
2. **Enterprise Opportunity Discovery** — Build the enterprise change portfolio, programme landscape, procurement landscape, opportunity landscape, programme relationship map, emerging opportunities, prioritisation and evidence demand register.
3. **Opportunity Selection** — Select the opportunity candidate that deserves a full Research Sprint, explaining why other candidates were not selected or should be sequenced later.
4. **Research Object Validation** — Validate that the selected object is the correct research object and not merely a visible procurement, partial implementation route, stale artefact or misleading proxy for a wider transformation.
5. **Enterprise Understanding** — Research the enterprise context, transformation drivers, stakeholders, constraints, evidence, unknowns and contradictions needed to understand the opportunity.
6. **Research-to-Positioning Handover** — Produce a contract stating what is evidenced, inferred, unknown, contradictory, usable for positioning and not claimable.
7. **Opportunity Positioning** — Convert enterprise understanding into opportunity positioning intelligence: strategic relevance, executive problem, likely decision frame, competitive context and evidence-governed pursuit implications.
8. **Positioning Insight Deepening** — Develop strategic theses, executive narratives, proof architecture and conversation plays while preserving evidence boundaries.
9. **Decision Envelope** — State whether pursuit conclusions are Supported, Supported with Caveats or Not Supported, including confidence, freshness, contradictions and evidence demand.
10. **Provider Fit (outside public research)** — Assess supplier-specific fit only outside public research, using appropriate private account knowledge, delivery context and governance.
11. **Executive Pursuit** — Use validated positioning and separate Provider Fit to shape executive pursuit activity.

### CSM sprint validation demonstration

The completed CSM sprint demonstrates why the lifecycle is needed. An EOD-first approach would have started from CSM as an enterprise and mapped transformation initiatives, programmes, platforms, suppliers and procurements before selecting a research object.

That enterprise-first mapping would have been designed to identify Transformation Partner, Implementation Partner, Phase 2, Phase 2b, Oracle and related procurements as connected elements of the opportunity landscape without requiring Rob to already know about SIDP. SIDP would have been treated as evidence inside the Programme Relationship Map rather than as the automatic definition of the opportunity.

The CSM validation remains Review material. It shows a learning-based improvement to methodology, but it does not promote Review material to Accepted architecture or prove the method across materially different enterprises.

## Completion checklist

Before completion, the Research GPT must confirm:

- outputs are Knowledge Pack-compatible;
- Presentation Model guidance is followed;
- all facts, interpretations and projections are labelled;
- source cut-off, confidence and freshness are declared;
- Unknowns and Contradictions are preserved;
- Recommendations link to Hypotheses and Evidence;
- no unsupported profit-centre or cost-centre classification is present;
- no raw worksheet or database labels are exposed in executive-facing outputs;
- runtime code and embedded application prompts were not changed for documentation-only work.
