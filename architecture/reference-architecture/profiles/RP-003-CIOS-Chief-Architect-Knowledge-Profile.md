# RP-003 — CIOS Chief Architect Knowledge Profile

Status: Accepted
Owner: Chief Architect

## Purpose

RP-003 defines the governed membership profile for the CIOS Chief Architect Knowledge Pack. The pack is an operating-context artefact generated from canonical repository sources; it does not own architectural concepts and does not convert operational reports into accepted architecture.

## Inclusion rules

Include documents by role:

1. Operating authority required to interpret CIOS architecture and Chief Architect behaviour.
2. Core Enterprise Intelligence authority required for enterprise, graph, behaviour, observation and hypothesis-validation judgement.
3. Runtime and product authority required to understand Flora, reasoning, Enterprise Canvas, Blueprint Import, Knowledge Packs, twin types, opportunity architecture, executive briefing and evidence lineage.
4. Current programme state required to distinguish architecture from implementation and delivery status.
5. Templates that help produce future state, decisions, work packages and recommendations without creating authority.

Do not include every architecture document. Exclude documents unless the manifest records why Chief Architect judgement requires them.

## Authority classifications

- `canonical_architecture`: defines architectural meaning.
- `accepted_decision`: records accepted architectural decisions.
- `operating_guidance`: governs companion behaviour.
- `runtime_baseline`: records implemented/runtime evidence.
- `programme_state`: records current delivery state and does not supersede architecture.
- `template`: creates no authority.
- `reference`: supports navigation or audit.

## Freshness model

Static architecture is event-driven. Runtime baseline refreshes on material runtime change. Programme state must be refreshed at least every 14 days and active work package state every 7 days. Stale programme state may be packaged for inspection but must be marked as unverified for strategic recommendation purposes.
