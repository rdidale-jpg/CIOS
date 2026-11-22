# Initial Decision Twin · routine research preparation

Use this path for a scoped research or refresh decision under [ADR‑009](../../architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md). Start from the existing Twin, Source records and applicable research obligations. Collect only within existing Source authority. Prepare dated assertions, provenance, Unknowns and Contradictions in the existing Researcher profiles. The initiating mission can run the local review as soon as those records are prepared. A Source or identity hold on an individual record does not stop unrelated preparation. Use the established Assured Release process when the consequence or audience requires it.

```sh
python tools/research/initial_decision.py docs/research/lloyds-tier1-sprint1 \
  --as-of 2026-11-22 --decision lloyds-service
```

The command takes a reviewed Blueprint source directory with the existing Evidence, Source, endpoint and review-lineage registers. It uses the portable Researcher manifest checker and Flora profile adapter. It checks local identities, dates, Source references and exact same-scope repeats, preserves the original registers, and prints one review brief. The brief groups IDs for continued preparation, external context ownership or explicit hold. It invokes the existing Source-bound service view for the Lloyds example. Arbitrary package statements never enter that view. For fresh reviewed local submissions, the existing `flora_cycle.py` reads and validates each source once and reuses the validated bytes for the export.

## Why the path was slow

| Step | Existing requirement | Correction |
| --- | --- | --- |
| Scope, research and preparation | ADR‑009 permits routine work through decision sufficiency. Source and legal constraints apply to actual collection and use. | Use the existing mission and reviewed inputs. Independent package review, integration and another briefing can be useful for release, but routine local preparation uses the existing package once. |
| Supplied-source validation | Source provenance, cut-off, reviewed locations and subject scope matter. | The old CLI acquired each supplied Source before invoking a cycle that acquired it again. Export now uses the same acquisition that produced the candidate and checksum. |
| Existing package validation | Blueprint format, input integrity and record lineage still matter. | Run the producer’s checks on the existing files directly. Local review does not rebuild a ZIP, receipt or copy of the registers. Use normal Blueprint inspection if later authorised for intake. |
| Identity and renewal | Research asset, legal subject and canonical Enterprise/workspace bindings have different owners. | Match exact local endpoints and repeated dated assertions in one pass. Use established live mappings only through existing scoped owners. Normalised names are insufficient proof of alias equivalence. |
| Executive presentation | Attribution, Source lifecycle and uncertainty apply to the intended view. | Reuse the existing candidate decision projection. The Lloyds preview uses Flora’s eligible FCA facts and preserves their period, reporting entity and interpretation limits. |
| Durable update | [ADR‑012](../../architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md) governs staging, mapping, plan, approval and execution. | The brief prepares one handoff. Existing Source checks, live duplicate comparison, `candidate.promote`, target and Canvas scopes, audit and reversal still apply to any later authorised action. |

## Lloyds #714 replay

The previous history used six separately commissioned stages from research through acceptance preparation, or five between-stage handoffs. That history included original research and corrections. It is not a timing benchmark for this replay. From the merged package, preparation and the decision view now use one command, zero intermediate handoffs and zero owner interruptions. Durable acceptance remains a separate, blocked phase.

- Reused 40 evidence candidates and the existing registers, including 31 Unknowns, two reconciliation records, ten superseded IDs and R03 held in Evidence lineage.
- Eleven Evidence IDs can proceed to preparation and seven to separate external context review. Twenty-two are deferred at their recorded Source or primary-evidence boundary. Three relationships can proceed to mapping review, and eleven remain deferred. The package makes no live identity binding. Accessible primary evidence for F17 and the existing Source, identity and role checks remain genuine blockers to the affected writes.
- One duplicated acquisition per supplied source was removed from the wave exporter. In this replay, three redundant preparation outputs are avoided compared with rebuilding a ZIP and making separate validation and preview outputs. The original ledgers and published material remain the evidence of record.
- A local replay took under one second on the task workspace. This measures the command from existing inputs and excludes new research, independent adjudication or canonical operations.

## Architectural critique

The fast path works as local candidate preparation and decision presentation. It cannot verify live rights, canonical duplicates or workspace membership from package metadata. Keep those decisions at their existing owners and scope. A repeated assertion is only a local exact repeat when subject, date, wording, source references and caveats agree. Conflicts still require review. The supplied format supports the Lloyds v1.1 input and other packages using the same reviewed registers. The command does not replace other Researcher workflows or authorise a new Source or application route. A Source or package withdrawal must still be checked before any later write. No durable Researcher write is claimed without the existing authority.
