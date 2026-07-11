# ADR-016 — Knowledge Packs as the Standard Exchange Mechanism

**Status:** Accepted
**Date:** 2026-07-11
**Owner:** Rob / CIOS
**Supersedes:** Earlier unmerged architecture update pack as a merge baseline, not its carried-forward concepts
**Superseded by:** None
**Owning documents:** FP-010, FP-011, EI-013, Knowledge Pack Specification v1.0, Twin Presentation Model Specification v1.0, Industry Twin Lifecycle Specification v1.0
**Implementation state:** Documentation foundation only; no Flora runtime implementation in this phase.

## Context

CIOS needs a governed way to exchange useful enterprise, industry, participant, opportunity and relational intelligence without treating every exchanged package as canonical fact. Previous architecture work introduced GPT-authored Twin Presentation Models, Flora as validator/repository/renderer, Industry Twin lifecycle concepts, Market Participant Twins, Cross-Twin Intelligence, and account-participant comparison. Those concepts are preserved, but the prior unmerged update pack is superseded as the merge baseline by the Architecture v2.0 Foundations Pack.

## Decision

Knowledge Pack is the standard exchange mechanism for portable CIOS knowledge. A Knowledge Pack carries Knowledge Assets, lineage, declared authorship, validation metadata, Unknowns, Contradictions, recommendations, and optional payloads such as Twin Presentation Models. Acceptance of a Knowledge Pack means the package is valid for repository handling; it does not silently promote all contents to canonical Enterprise Twin, Industry Twin, Market Participant Twin, Opportunity Twin or Relational Twin fact.

The authority chain is:

Accepted ADR → owning Founding Paper or Enterprise Intelligence paper → normative specification → runtime implementation contract.

FP-010 owns conceptual Knowledge Pack architecture. FP-011 owns Knowledge Exchange Architecture. EI-013 owns exchanged Knowledge Asset semantics. The Knowledge Pack Specification owns the package contract. The Twin Presentation Model Specification owns presentation payload semantics. The Industry Twin Lifecycle Specification owns Industry maintenance and cadence.

## Consequences

Flora may later validate, version, store and render accepted Knowledge Packs and accepted Twin Presentation Models, but this ADR does not implement a repository, importer, exporter, renderer, monitoring system, database migration or runtime reasoning change. Human-supplied knowledge remains labelled. Recommendations retain inspectable lineage. Unknowns and Contradictions remain first-class.

## Acceptance step

Accepted as the Architecture v2.0 Knowledge Pack authority for this reconciliation phase.
