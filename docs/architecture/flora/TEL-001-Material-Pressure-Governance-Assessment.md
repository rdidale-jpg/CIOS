# TEL-001 Material Pressure Governance Assessment

**Assessment date:** 2026-08-16
**Decision:** GOVERNANCE GAP RESOLVED BY ADR-026
**Runtime change authorised in this sprint:** No
**Subsequent runtime implementation authorised:** Yes
**Qualification contract status:** ACCEPTED — [ADR-026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md)

## Authority reviewed

| Authority | Recorded status | Role in this assessment |
|---|---|---|
| ADR-014 | ACCEPTED | Evidence-bounded interpretation, lineage, Unknown/Contradiction and safe-failure constraint. |
| ADR-024 | ACCEPTED | Hybrid governed runtime and candidate-validation boundary. |
| ADR-026 | ACCEPTED | Sole Material Pressure qualification authority. |
| EI-001 | DRAFT | Canonical durable-model owner named by ADR-026; not independently accepted. |
| EI-003 | DRAFT | Informative behaviour model, not qualification authority. |
| EI-004 | DRAFT | Intended Commercial Reasoning owner, constrained by ADR-026's durable/derived boundary. |
| EI-012 | DRAFT | Informative Observation model and candidate-input pattern. |
| EIF-001 | REVIEW | Informative Enterprise foundation context. |
| EIRP-001 | PROPOSED | Proposed runtime pipeline subordinate to accepted ADRs. |
| FEIR-001 | PROPOSED | Proposed runtime architecture subordinate to ADR-024. |
| CURRENT-PROGRAMME-STATE | OTHER — programme-state baseline | Current Chief Architect programme baseline, not domain authority. |
| Flora Runtime Capability Baseline (WP-011) | OTHER — runtime baseline | Implementation evidence, not domain authority. |

The Chief Architect Knowledge Pack version is 1.1.0. Inclusion in that pack does not promote Review, Draft or Proposed documents. Before ADR-026, ADR-002 established the durable-memory boundary and ADR-014/ADR-024 constrained reasoning, but **no Accepted authority qualified Material Pressure**.

## Resolved architectural gap

ADR-026 **amends and accepts** the earlier proposed six-gate contract. It:

- establishes EI-001 as the single durable-model owner while EI-001 remains Draft;
- makes ADR-026 the accepted qualification authority;
- requires governed input, Enterprise applicability, pressure semantics, semantic identity/singularity, explainable materiality, supported Enterprise consequence and complete assurance lineage;
- permits Unknown only in non-core detail;
- makes core contradiction `UNRESOLVED` and permits qualification-with-contradiction only when the core gates remain supported;
- uses governed timing/resolution/supersession rather than a new fixed lifecycle enumeration;
- deterministically rejects keyword, generic, cross-Enterprise, metric-only, Programme-only, Opportunity-only, Procurement-only, priority-only, unsupported, immaterial, duplicate and core-contradictory candidates; and
- keeps durable Enterprise understanding separate from seller-specific Commercial Reasoning.

The former annex in this document is superseded by ADR-026 and is not repeated. In particular, its combined “consequence and commercial significance” gate was unsafe: ADR-026 removes commercial significance from durable qualification.

## Runtime boundary and readiness

The TEL-001 factual projection currently reads only the explicit Enterprise `pressures` field. ADR-026 does not change that projection, runtime reasoning, dossier behaviour, Opportunities, Procurements, Watchpoints or Evidence. No source fact is promoted by this assessment.

Architecture is now sufficiently precise for a subsequent runtime sprint. That sprint may implement gate outcomes, semantic singularity, lineage, Unknown and Contradiction handling under ADR-024 without making a new architectural decision. It must demonstrate conformance before production use; authorisation is not implementation.

| Question | Finding |
|---|---|
| Governance gap | Resolved by Accepted ADR-026. |
| Contract decision | AMENDED and ACCEPTED. |
| Durable-model owner | EI-001, under ADR-026; EI-001 status remains Draft. |
| Qualification authority | ADR-026. |
| Commercial reasoning | Derived, under existing commercial-reasoning governance; never durable Pressure truth by implication. |
| Runtime implementation in this PR | Not authorised and not performed. |
| Subsequent implementation readiness | Ready and authorised, subject to ADR-026 conformance tests. |
| Fresh import | Not required. |

## Conceptual and falsification result

ADR-026 records the full unchanged-TEL-001 matrix for BT Group, CityFibre, Openreach, TalkTalk, Virgin Media O2 and VodafoneThree. It deliberately produces `YES`, `NO` and `UNRESOLVED` outcomes. Its BT examples distinguish raw revenue, cost-base and legacy-estate labels from qualified debt/capex and regulated-pricing conditions. Its falsification matrix safely rejects metrics, generic industry assumptions, competitor conditions, Programmes, Opportunities, Procurements, weak unsupported observations, unsupported consequences and duplicates, and holds core contradictions unresolved.

## Merge decision record

- **Authority hierarchy respected:** Yes.
- **Exactly one qualification authority:** ADR-026.
- **Exactly one durable-model owner:** EI-001, established by ADR-026.
- **EI-001 status represented truthfully:** Draft; unchanged.
- **Production semantics changed:** No.
- **Runtime implementation authorised after this PR:** Yes.
- **Decision:** SAFE TO MERGE, subject to repository validation and unchanged TEL-001 checksum.

## Fixture integrity

The TEL-001 ZIP was not modified. Its expected SHA-256 remains `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
