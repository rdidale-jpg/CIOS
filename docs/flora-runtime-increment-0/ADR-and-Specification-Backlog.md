# ADR and Specification Backlog

| Title | Decision type | Classification | Reason | Blocking increment | Owner | Recommended timing |
| --- | --- | --- | --- | --- | --- | --- |
| Increment 1 Read Interface Specification | Specification | Specification required | Needed to freeze read-only contracts without over-creating ADRs. | Increment 1 | CIOS Chief Architect | Before coding Increment 1. |
| Minimal Runtime Identity Envelope | Specification | Specification required | Stable projection identity is incomplete but can be specified narrowly. | Increment 1 | Enterprise Intelligence owner + Flora architecture owner | Before coding Increment 1. |
| Runtime Graph Persistence Approach | ADR | ADR required before later increment | FEIR-001 names physical runtime graph design as Unknown; read-only slice can derive on demand. | Increment 2 or graph persistence work | CIOS Chief Architect | After Increment 1 fixtures prove access patterns. |
| Context Package Schema | Specification, possible ADR only if enduring exchange boundary | Specification required before reasoning increment | ADR-014 requires structured evidence packages; Increment 1 only needs availability/lineage. | Increment 2 | Flora runtime owner | During reasoning-slice design. |
| Worker Schema and Provider Boundary | Specification/ADR | ADR required before worker runtime if provider boundary materially changes | FEIR worker I/O fields exist; no workers in Increment 1. | Increment 2+ | Flora runtime owner | Before GPT worker implementation. |
| Recommendation Eligibility Policy | ADR/specification | ADR required before recommendation increment | ADR-005 governs principle but thresholds/downgrade policy remain unresolved. | Recommendation increment | CIOS Chief Architect + commercial owner | Before any strong recommendation UI. |
| Audit Retention and Observability | ADR | ADR required before production persistence | Increment 1 can emit baseline events; retention/privacy is enduring and material. | Production hardening / before persisted production audit | Runtime operator + architecture owner | Before production deployment. |
| Human Review Roles | Specification | Specification required before review workflows | Increment 1 needs only workspace user, architecture reviewer and runtime operator. | Later review/write-back increments | CIOS Chief Architect | Before candidate promotion/recommendation approval. |
| Write-back Proposal Contract | ADR/specification | ADR required before write-back increment | Material boundary preventing silent canonical mutation. | Write-back increment | Enterprise Knowledge owner + CIOS Chief Architect | After read/reasoning validation. |
| External Output Approval | Specification/ADR | ADR required before external commercial assets | FEIR-001 flags approval workflow; excluded from Increment 1. | External-output increment | Commercial owner + architecture owner | Before external generated assets. |

## Already governed

- Observation primacy: ADR-001.
- Inspectable recommendation lineage: ADR-005.
- Evidence-governed runtime reasoning principle and safe failure: ADR-014.
- Knowledge Pack exchange boundary: ADR-016.
- Hybrid runtime authority boundary: ADR-024.

## Not required before Increment 1

- Database/product selection for runtime graph.
- Model provider selection.
- Recommendation thresholds.
- Write-back implementation.
- Worker orchestration schemas beyond naming out-of-scope interfaces.
