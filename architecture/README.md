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
