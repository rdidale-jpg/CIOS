# Knowledge Pack Specification v1.0

**Status:** Draft Normative Specification  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning paper:** [FP-010 — Knowledge Pack Architecture](../../founding-papers/FP-010-Knowledge-Pack-Architecture.md) and [FP-011 — Knowledge Exchange Architecture](../../founding-papers/FP-011-Knowledge-Exchange-Architecture.md)  
**Semantic owner:** [EI-013 — Knowledge Asset Exchange Model](../../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md)  
**Owning ADR:** [ADR-016](../../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md)

## Contract

A Knowledge Pack must include package identifier, version, issuer, creation date, intended scope, Knowledge Assets, lineage, validation metadata, rights or handling constraints, Unknowns and Contradictions where present, and recommendation lineage where recommendations are present.

## Acceptance meaning

Accepting a Knowledge Pack means the package contract is valid for Knowledge Repository handling. It does not make contained statements canonical fact.

## Payloads

A Knowledge Pack may carry Twin Presentation Models, Industry Twin lifecycle updates, Market Participant Twin intelligence, Opportunity Twin intelligence, Relational Twin mappings and Cross-Twin Intelligence.

## Twin release package profile

Commercial Digital Twin releases MUST use the Knowledge Pack release structure defined by the Twin Contract:

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

The normative manifest schema is `architecture/specifications/knowledge-packs/twin-release-manifest.schema.json`. Pack acceptance means the release is valid for repository handling; imported data remains candidate intelligence until separately accepted by the owning model process. Presentation Models carried in `payload/presentation-model/` are governed interpretations for declared audiences and purposes, not canonical fact by default. Unsupported content must be quarantined, and Unknowns, Contradictions, Evidence lineage, Observation lineage and human-supplied knowledge labels must remain inspectable.
