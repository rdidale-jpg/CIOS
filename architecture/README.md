# CIOS Architecture Repository

**Status:** draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-02

## Purpose

The `architecture/` directory is the source of truth for CIOS design thinking. It preserves the reasoning behind the platform, not just documentation of the software.

CIOS implementation work should be guided by stable institutional memory: founding papers, design documents, research notes, Architecture Decision Records (ADRs) and capability roadmaps.

## Repository sections

- `founding-papers/` contains durable principles and thesis-level papers that should remain stable over time.
- `design/` contains system design documents for platform, product and capability architecture.
- `research/` contains evolving models, hypotheses and notes that may later become formal design or decision records.
- `decisions/` contains Architecture Decision Records that explain important choices, trade-offs and consequences.
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

1. `architecture/founding-papers/`
2. Relevant `architecture/design/`
3. Relevant `architecture/decisions/`

If a requested change conflicts with a founding paper or ADR, explain the conflict before implementation.

## Working principles

- Preserve reasoning as a first-class asset.
- Separate durable principles from evolving research hypotheses.
- Record major decisions before implementation details become implicit.
- Keep architecture documents concise enough to be read before coding.
- Update the relevant architecture file when implementation materially changes the product direction.
