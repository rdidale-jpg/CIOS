# Flora Runtime Increment 0 — Architecture and Data Readiness Audit

**Status:** Complete  
**Readiness outcome:** Ready with conditions  
**Date:** 2026-07-19  
**Owner:** Rob / CIOS  
**Architecture owner:** CIOS Chief Architect  
**Mission type:** Assessment and specification only. No application functionality changed.

## Deliverables

1. [Flora Runtime Readiness Report](Flora-Runtime-Readiness-Report.md)
2. [Runtime Asset Register](Runtime-Asset-Register.md)
3. [Interface and Schema Register](Interface-and-Schema-Register.md)
4. [Architecture Traceability Matrix](Architecture-Traceability-Matrix.md)
5. [ADR and Specification Backlog](ADR-and-Specification-Backlog.md)
6. [Increment 1 Delivery Definition](Increment-1-Delivery-Definition.md)
7. [Completion Report](Completion-Report.md)

## Completion standard answers

| Question | Increment 0 answer |
| --- | --- |
| What will Increment 1 read? | A bounded UK Banking governed corpus: banking Flora manifest/register, banking industry and infrastructure twins, banking reinvention observations/hypotheses/governance reports, and existing repository-backed Evidence/Observation/Enterprise Model stores where available. |
| Who owns that knowledge? | Enterprise Knowledge and owning Enterprise Intelligence / architecture documents; Flora owns only read projections, workspace state and audit. |
| How are objects identified? | Existing source IDs are usable but uneven; Increment 1 requires a minimal read identity envelope carrying object ID, type, version, authority, source path and lineage refs. |
| What may Flora persist? | Non-canonical workspace state, runtime projection/cache metadata, audit/provenance events and safe ingestion reports. |
| What must Flora never own? | Canonical Evidence, Observations, Enterprise Models, Knowledge Graph semantics, accepted hypotheses, recommendations or governed Knowledge Pack truth. |
| What can the user inspect? | Focus Object identity, governing source, relationships, Evidence/Observation availability, Unknowns, Contradictions and one-hop lineage to source assets. |
| What lineage will be available? | Asset path/version/cut-off, source/evidence/observation references where present, and explicit safe-unavailable markers where lineage is missing. |
| What access controls apply? | Authenticated user, workspace/enterprise allow-list, asset/object checks, fail-closed behaviour and restricted audit access. |
| What audit evidence will be retained? | User/trigger, timestamp, focus object, source assets and versions, operation, outcome, validation result, access decision, failure reason and component version when available. |
| What remains Unknown? | Runtime graph persistence, formal context package schema, audit retention/privacy periods, accepted human role taxonomy, write-back proposal contract and complete governed identity coverage. |
