# CIOS Architecture Repository

**Status:** draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

The `architecture/` directory is the source of truth for CIOS design thinking. It preserves the reasoning behind the platform, not just documentation of the software.

CIOS implementation work should be guided by stable institutional memory: founding papers, design documents, research notes, Architecture Decision Records (ADRs) and capability roadmaps.


## CIOS Reference Architecture

The [CIOS Reference Architecture](reference-architecture/README.md) is the recommended starting point for anyone trying to understand CIOS. It is the single authoritative architecture entry point that explains how the Founding Papers, CIRM, Enterprise Intelligence and Flora runtime relate.

Start with:

- [CIOS AI Context](../CIOS-AI.md)
- [Reference Architecture area](reference-architecture/README.md)
- [CIOS Reference Architecture v1.0](reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [CIOS Design Doctrine](reference-architecture/CIOS-Design-Doctrine.md)
- [AI Session Handoff](reference-architecture/AI-Session-Handoff.md)
- [ADR index](decisions/README.md)

Use it before reading a specific paper or changing runtime behaviour.

## CIOS Intelligence Reference Model — CIRM

CIRM defines how CIOS converts observable enterprise reality into strategic commercial judgement. It makes the founding papers read as one intelligence architecture: first observing what is happening, then reasoning about what it means and what action is justified.

### Volume I — Observation

**Purpose:** what is happening?

Volume I includes:

- FP-003 — Flora Intelligence Architecture
- FP-004 — Evidence Acquisition Standard
- FP-005 — Enterprise Intelligence Collection Framework
- FP-006 — Source Quality Standard

### Volume II — Reasoning

**Purpose:** what does it mean?

Volume II includes:

- FP-007 — Strategic Signal Standard
- FP-008 — Commercial Conviction Model
- FP-009 — Hypothesis Validation Standard

Future founding papers should explicitly state where they sit within CIRM.

### Canonical intelligence pipeline

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Strategic Signals
→ Commercial Insights
→ Transformation Themes
→ Transformation Theses
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendations
→ Commercial Outcomes
→ Continuous Learning
```

### Shared CIRM terminology

- **Observable Enterprise Reality:** The external facts, events, statements, decisions and conditions emitted by an organisation or its environment.
- **Governed Source Collection:** The controlled acquisition of evidence from approved, explainable and source-specific locations.
- **Raw Evidence:** A factual, attributable record of something observed.
- **Evidence Quality:** The assessment of evidence authority, specificity, freshness, relevance, independence and usefulness.
- **Strategic Signal:** A commercially meaningful interpretation of evidence that indicates potential enterprise change, pressure or opportunity.
- **Commercial Insight:** A reasoned pattern derived from multiple signals.
- **Transformation Theme:** A recurring category of enterprise change such as AI transformation, cyber resilience, cloud modernisation, legacy replacement, operating-model change or cost transformation.
- **Transformation Thesis:** A coherent, evidence-backed judgement about what may be happening in an enterprise and why it matters commercially.
- **Hypothesis:** A testable proposition used to validate or challenge a transformation interpretation.
- **Commercial Conviction:** The structured judgement that sufficient evidence and reasoning exist to justify a level of commercial action.
- **Executive Recommendation:** A recommended next learning or engagement action, grounded in the reasoning chain.
- **Commercial Outcome:** The result of action, feedback or market development that can improve future judgement.

### Shared transformation concepts

- **Transformation Pressure:** The internal and external forces that make change more likely or necessary. Internal pressure examples include legacy technology, operating cost, service quality, cyber exposure, workforce constraints, fragmented data, delivery failure and technical debt. External pressure examples include regulation, political direction, customer expectations, market disruption, competitive moves, supplier change, economic pressure and technology shifts.
- **Transformation Inevitability:** The degree to which an enterprise appears structurally compelled to transform, regardless of whether procurement, budget or sponsor evidence is visible. Transformation inevitability is not the same as commercial opportunity: an enterprise may need to transform but still be inaccessible, already committed to another provider, internally constrained or commercially unattractive.

### Standard lifecycle language

- **Strategic Signal lifecycle:** New, Emerging, Strengthening, Stable, Weakening, Dormant, Retired.
- **Hypothesis lifecycle:** Created, Emerging, Strengthening, Validated, Weakening, Rejected, Retired.
- **Conviction evolution:** Very Low, Low, Emerging, Medium, Strong, Very Strong.
- **Evidence lifecycle:** Discovered, Collected, Accepted, Downgraded, Context Only, Rejected, Retired.
- **Source lifecycle:** Discovered, Classified, Monitored, Downgraded, Replaced, Retired, Diagnostics Only.



## Enterprise Intelligence Architecture

Enterprise Intelligence defines the enterprise knowledge model CIOS builds and maintains for each monitored organisation. Where the Founding Papers define the intelligence process, the Enterprise Intelligence papers define what CIOS knows about an enterprise.

- Founding Papers define the intelligence process.
- Enterprise Intelligence papers define the enterprise knowledge model.
- Flora is the first runtime implementation.

The Enterprise Intelligence series begins with each monitored enterprise as a living Commercial Digital Twin that supports executive intelligence, account planning, opportunity prediction and strategic business development. Volume 5 adds Intelligence Foundations, including the Enterprise Observation Model that defines Observations as reusable intelligence atoms between evidence acquisition and CIRM reasoning. See [`enterprise-intelligence/README.md`](enterprise-intelligence/README.md).

## Repository sections

- `enterprise-intelligence/` contains the EI series defining the enterprise knowledge model and Commercial Digital Twin architecture.
- `founding-papers/` contains durable principles and thesis-level papers that should remain stable over time.
- `design/` contains system design documents for platform, product and capability architecture.
- `research/` contains evolving models, hypotheses and notes that may later become formal design or decision records.
- `decisions/` contains Architecture Decision Records that explain important choices, trade-offs and consequences. Start with the [ADR index](decisions/README.md), including accepted [ADR-001](decisions/ADR-001-Observations-as-Atomic-Intelligence-Unit.md), [ADR-002](decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md), [ADR-003](decisions/ADR-003-CIRM-and-EI-Separation.md), [ADR-004](decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md) and [ADR-005](decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md). Proposed ADR placeholders retained for review are [ADR-006](decisions/ADR-006-Signal-Architecture.md), [ADR-007](decisions/ADR-007-Transformation-Thesis.md) and [ADR-008](decisions/ADR-008-Recommendation-Engine.md).
- `roadmap/` contains capability evolution plans for CIOS, Flora, Newton and the Observatory.


## Founding papers

- FP-001 — CIOS Vision
- FP-002 — Strategic Signal Standard
- FP-003 — Flora Intelligence Architecture
- FP-004 — Evidence Acquisition Standard: defines evidence acquisition plans, evidence acceptance rules, scoring bands, curation guidance and collection handbrakes for Flora's live intake phase.
- FP-005 — Enterprise Intelligence Collection Framework: defines enterprise evidence blueprints, coverage scoring and collection priority rules so Flora can adapt evidence collection by enterprise type and commercial priority.
- FP-006 — Source Quality Standard: defines source tiering, source quality and yield scoring, lifecycle actions and feedback loops for source selection and replacement.

Together FP-004, FP-005 and FP-006 define the Evidence Collection Architecture: how Flora should plan collection, recognise useful evidence, select and curate sources, score coverage, damp weak evidence and learn from user feedback before downstream reasoning begins.

## Phase 2 — Commercial Reasoning

These papers define how Flora converts evidence into strategic commercial judgement.

- FP-007 — Strategic Signal Standard: defines the Strategic Signal as the bridge between observable evidence and commercial reasoning.
- FP-008 — Commercial Conviction Model: defines how Flora assesses whether evidence is sufficient to justify executive engagement without confusing conviction with opportunity.
- FP-009 — Hypothesis Validation Standard: defines how Flora creates, tests, strengthens, weakens, rejects and retires commercial hypotheses.

## Developer instruction note

Before major implementation work, review:

1. `../CIOS-AI.md`
2. `architecture/reference-architecture/README.md`
3. `architecture/reference-architecture/CIOS-Design-Doctrine.md`
4. `architecture/decisions/README.md`
5. `architecture/founding-papers/`
6. Relevant `architecture/design/`
7. Relevant `architecture/decisions/`

If a requested change conflicts with a founding paper or ADR, explain the conflict before implementation.

## Working principles

- Preserve reasoning as a first-class asset.
- Separate durable principles from evolving research hypotheses.
- Record major decisions before implementation details become implicit.
- Keep architecture documents concise enough to be read before coding.
- Update the relevant architecture file when implementation materially changes the product direction.
