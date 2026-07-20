# Commercial Digital Twin Research Agent Guide

**Status:** Canonical Markdown guidance  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-20  
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


## Industry Twin Researcher operating route

**Purpose:** this route is the operational path for a Researcher producing an Industry Twin from repository documentation alone. It references existing doctrine rather than replacing it. The Researcher must preserve the authority chain in the [Document Map](../reference-architecture/Document-Map.md): Mission → Doctrine → Research Guidance → Enterprise Intelligence → Architecture Review → Implementation.

1. **Select Industry** — identify the industry boundary, target geography and intended research decision. Use [IT-001](../specifications/industry-twins/IT-001-Industry-Twin-Specification.md) for Industry Twin scope and the [Industry Twin Lifecycle Specification](../specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md) for cadence and maintenance.
2. **Define Scope** — state included/excluded segments, material participant classes, source cut-off, public-domain limits, known constraints and explicit non-goals. Preserve Unknowns instead of silently narrowing the Twin.
3. **Build Source Map** — create the minimum source coverage plan using ADR-010, FP-004, FP-005 and FP-006: official/public-body sources, enterprise reporting, procurement and framework sources, regulator/market sources, supplier sources and credible secondary sources.
4. **Research Industry** — produce industry-level Observations, mechanisms, tensions, structural forces, infrastructure dependencies, policy/regulatory pressures, major programmes, procurement routes and gaps. EI-012 owns Observation discipline; EI-017 and EI-015 remain Review inputs where causal mechanisms and Patterns are useful.
5. **Research Enterprises** — select representative enterprises and research each sufficiently to support comparison. Use EI-001 for Enterprise Model structure, EI-002 for relationships and EI-003 for behaviour.
6. **Build Enterprise Intelligence** — build or update Enterprise Twins, enterprise Observations, relationship maps, suppliers, contracts, programmes, stakeholders, hypotheses, Unknowns and Contradictions. Do not treat report text as durable memory.
7. **Assess Coverage** — compare the Industry Twin against the minimum readiness gate in this guide and the production lifecycle in EKPP-001. Record explicit gaps; do not invent scores.
8. **Human Validation** — ask a human owner to validate scope, interpretation, omitted segments, material suppliers, procurement assumptions, uncertainty and whether the Twin is useful enough for Architecture Review.
9. **Architecture Review** — hand the Research output to the Chief Architect for authority, duplication, doctrine, lineage, non-promotion and readiness review under EKPP-001 and ADR-009.
10. **Codex Handover** — provide Codex with the research package, source map, changed documents/assets, link targets, validation notes, explicit gaps and requested repository action. Codex governs repository hygiene, not Enterprise Knowledge truth.

### Minimum Industry Twin readiness gate

An Industry Twin may leave Research only when the following minimum expectations are documented. This is a readiness gate, not a score.

- **Research completeness:** the industry scope, source cut-off, included/excluded segments, core research questions and non-goals are stated.
- **Source coverage:** the source map covers official/public-body, regulator, enterprise, procurement/framework, supplier and credible secondary sources, or records why a category is absent.
- **Supplier coverage:** incumbent suppliers, strategic suppliers, challengers, ecosystem partners and unknown supplier positions are recorded where visible.
- **Procurement coverage:** frameworks, contract notices, awards, renewals, buying routes, major programmes and commercial timing are researched or listed as explicit gaps.
- **Enterprise coverage:** researched enterprises are sufficient to support the claimed industry comparison, and omissions are named.
- **Observation completeness:** material claims are expressed as atomic Observations with lineage, truth status, confidence/freshness and linked Unknowns or Contradictions where applicable.
- **Hypothesis readiness:** hypotheses are labelled as hypotheses, linked to evidence demands and not presented as findings or Recommendations.
- **Human validation:** a human reviewer has checked scope, material omissions, interpretation, uncertainty and readiness for Architecture Review.
- **Explicit research gaps:** unresolved gaps are listed with impact, owner or next research action; gaps are not hidden in narrative prose.

### Supplier, contract and procurement checklist

Use this checklist while building the source map and Enterprise Intelligence. EI-001 owns Enterprise Model structure; EI-002 owns relationships between enterprises, suppliers, programmes, contracts, buyers, evidence and Observations.

- Incumbent suppliers named in official enterprise reports, procurement notices, programme pages, case studies or credible public disclosures.
- Strategic suppliers or alliance partners that materially influence industry change, delivery capacity, control points or access.
- Contract records, awards, extensions, variations and termination signals.
- Frameworks, lots, dynamic purchasing systems and preferred procurement vehicles.
- Renewal windows, expiry dates, break clauses, extension options and budget-cycle signals where visible.
- Procurement routes: direct award, framework call-off, competitive tender, grant, concession, public-private partnership or other visible route.
- Major programmes, transformation portfolios, infrastructure initiatives or policy programmes linked to supplier demand.
- Buying organisations, accountable authorities, sponsor departments, central bodies, shared-service organisations and delivery agencies.
- Commercial timing: budget cycle, spending review, fiscal year, programme milestones, contract renewal, regulatory deadlines and implementation sequencing.

### Banking lessons now applied

These are enduring research-method lessons from Banking, not product defects. Each lesson is now reflected in the guidance above.

- **Deeper supplier intelligence** is required because industry claims are weak without incumbent, strategic supplier and ecosystem context; reflected in the Source Map step, Enterprise Intelligence step, readiness gate supplier coverage and supplier/procurement checklist.
- **Procurement timing matters** because commercial usefulness depends on renewal windows, frameworks, awards, programme milestones and buying cycles; reflected in the Research Industry step, readiness gate procurement coverage and commercial timing checklist.
- **Research completeness must be explicit** because a useful Twin must show what was researched, omitted and bounded; reflected in the Define Scope step, Assess Coverage step and readiness gate research completeness/gaps expectations.
- **Historical context must be preserved** because current industry mechanisms often depend on prior programmes, legacy contracts, regulatory events or market structure; reflected in the Research Industry and Research Enterprises steps through mechanisms, programmes and relationship mapping.
- **Valuation comparables must be labelled with uncertainty** because public research may expose partial comparables without proving value; reflected in the evidence/truth rules and the readiness gate requirement to label hypotheses and gaps rather than overstate conclusions.
- **Explicit uncertainty improves trust** because Unknowns and Contradictions are intelligence objects, not failures; reflected in the Evidence, truth and lineage rules, Define Scope step, Observation completeness and explicit research gaps.
- **Human validation is mandatory before handover** because research judgement, material omissions and practical usefulness need accountable review; reflected in the Human Validation step and readiness gate human validation expectation.

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
