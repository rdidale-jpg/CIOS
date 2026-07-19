# Increment 1 Architecture Acceptance

## Decision

**Increment 1 accepted — condition closed**

The Increment 1 condition is closed because the merged validation artefacts match the rendered runtime, the read-only architecture boundary remains intact, all Increment 1 workspace capabilities are usable for the supported object, and no prohibited Increment 2 reasoning, Recommendation, scoring, hypothesis-generation, inference, GPT invocation or write-back behaviour is present in the Increment 1 slice.

## Evidence reviewed

Material evidence reviewed:

- Accepted ADR baseline identified by Increment 0 architecture evidence: ADR-001, ADR-005, ADR-014, ADR-016 and ADR-024.
- CIOS Reference Architecture and Enterprise Intelligence governing sources referenced by Increment 0 and Increment 1 traceability material.
- EI-001 Enterprise Model Specification, EI-002 Enterprise Knowledge Graph and EI-012 Enterprise Observation Model as semantic governing sources.
- FP-009 Hypothesis Validation Standard as an exclusion and later-increment guardrail for hypothesis and Recommendation behaviour.
- ADR-025, FEIR-001 and FA-001 were treated only according to current repository status and were not promoted as accepted authority where repository material presents them as proposed or non-accepted.
- Increment 1 frozen read contracts under `schemas/flora-runtime/v0.1/`:
  - `focus-object-projection-v0.1.schema.json`;
  - `relationship-projection-v0.1.schema.json`;
  - `evidence-observation-availability-v0.1.schema.json`;
  - `unknown-response-v0.1.schema.json`;
  - `contradiction-response-v0.1.schema.json`;
  - `lineage-response-v0.1.schema.json`;
  - `workspace-state-v0.1.schema.json`;
  - `audit-event-v0.1.schema.json`;
  - `ingestion-report-v0.1.schema.json`;
  - `safe-unavailable-response-v0.1.schema.json`;
  - `common-definitions.schema.json`.
- Increment 1 UK Banking fixtures under `fixtures/flora-runtime/increment-1/uk-banking/`, including valid, partial, invalid and safe-unavailable fixture classes.
- Runtime projection implementation in `cios/applications/flora/runtime/increment1.py`.
- Runtime HTML presentation in `cios/applications/flora/runtime/increment1_views.py`.
- Web routing integration in `cios/applications/flora/web/app.py`.
- Automated tests in `tests/flora_runtime/test_increment1_runtime.py`.
- Validation artefacts:
  - `docs/flora-runtime/increment-1-validation/lloyds-validation-report.md`;
  - `docs/flora-runtime/increment-1-validation/lloyds-workspace.html`;
  - `docs/flora-runtime/increment-1-validation/safe-unavailable.html`.
- Rendered route checks for `/flora`, `/flora/object/BK-ENT-001`, `/flora/lloyds`, `/workspace/enterprise/BK-ENT-001` and `/flora/object/unsupported-object` against the running application.
- Merged review history visible in local git history:
  - merge commit `479b45d` for pull request #311, "Validate Flora Increment 1 Lloyds workspace";
  - implementation commit `40bbf86`, "Validate Flora Increment 1 Lloyds workspace";
  - preceding merge commit `3c31d10` for pull request #310, "Expose Flora Increment 1 Lloyds workspace";
  - preceding implementation commit `30a5667`, "Expose Flora Increment 1 Lloyds workspace";
  - preceding merge commit `9e62c96` for pull request #309, "implement-flora-runtime-increment-1".

Note: the requested commit identifier `9e3f57f` was not present in this local checkout. The merged Increment 1 validation history available in the repository is headed by `479b45d`, with implementation commit `40bbf86`.

## Architectural findings

### Authority boundary

The runtime remains a governed read projection over frozen Increment 1 contract fixtures and UK Banking source references. It does not present proposed architecture documents as accepted authority and does not invent authority fields when governed metadata is incomplete. `BK-ENT-001` is shown with its object identity, Enterprise Twin type, authority status, lifecycle status, freshness status, persistence class and provenance reference.

### Canonical versus runtime boundary

The Increment 1 workspace is non-canonical and read-only. The focus object projection is explicitly labelled as a frozen v0.1 read projection; workspace state is labelled non-canonical and short-lived. Fixtures and projections are used for runtime presentation and validation only. No canonical mutation path, Enterprise Knowledge write-back or runtime-to-canonical promotion is included in this acceptance baseline.

### Lineage behaviour

Lineage is inspectable and includes source, evidence, observation, governed object and projection nodes. The runtime also renders partial lineage, access-redacted lineage and unresolved relationship examples as distinct states rather than collapsing them into success or failure. This satisfies the Increment 1 one-hop/inspection baseline while leaving deeper lineage graph persistence for a later increment.

### Unknown and Contradiction handling

Unknowns are represented as governed intelligence gaps with evidence demand and distinction metadata, not as runtime errors. Contradictions are preserved as open competing references with both sides retained and no forced resolution. The Lloyds-specific Unknown limits stronger action and confirms that Increment 1 does not graduate into hypothesis or Recommendation behaviour.

### Workspace-state behaviour

Workspace state remains a transient user workspace context, tied to `BK-ENT-001`, with retention metadata and active perspective. It does not contain canonical objects, evidence bodies, observations, Unknowns or Contradictions as promoted memory.

### Safe-unavailable behaviour

Unsupported object access returns a `safe_unavailable` presentation with reason `identifier_unresolved`, a user-safe explanation, retryability and a return route. The rendered safe-unavailable validation artefact matches the runtime behaviour and avoids fabricated fallback content.

### Prohibited capability checks

The Increment 1 runtime module states and implements a read-only projection boundary: it does not create canonical objects, invoke AI, infer relationships, score opportunities or write Enterprise Knowledge. Prohibited-capability scanning of the Increment 1 runtime, fixtures, schemas, tests and validation artefacts found no hidden GPT invocation, Recommendation generation, opportunity scoring, inferred relationship display or write-back behaviour in the Increment 1 slice. Mentions of hypothesis, Recommendation, scoring and canonical ownership in schemas/fixtures are boundary or exclusion metadata rather than implemented Increment 2 capabilities.

## Review-question conclusions

1. `/flora` leads a normal user to the Lloyds workspace through a visible "Open Lloyds Banking Group Increment 1 workspace" link.
2. `BK-ENT-001` is visibly and correctly in focus in the Lloyds workspace.
3. Identity, type, authority, lifecycle, freshness, persistence and provenance are understandable in the focus-object panel.
4. Governed relationships are distinguished from inferred relationships; the workspace states that no inferred relationships are shown.
5. Evidence and Observations are visibly distinct through separate availability metrics.
6. Unknowns are represented as governed intelligence, not errors.
7. Contradictions are preserved without forced resolution.
8. Complete, partial and access-redacted lineage states are distinguishable.
9. Safe-unavailable behaviour prefers the user-safe explanation.
10. Workspace state remains non-canonical.
11. Fixtures and read projections are distinguished from canonical mutation.
12. No hidden GPT, scoring, Recommendation, hypothesis-generation, inference or write-back behaviour was found in the Increment 1 slice.
13. The validation artefacts accurately represent the merged runtime.
14. The Lloyds fixtures are focused on `BK-ENT-001`.
15. No material reason remains to block Increment 2 planning after this Increment 1 acceptance baseline.

## Residual limitations

### Data limitations

- `BK-ENT-001` retains incomplete governed metadata where the source corpus records values such as owner as `TBD`.
- Individual observation freshness dates vary or are absent.
- Lloyds-specific deposit elasticity, customer journey ownership and executive accountability remain governed Unknowns.
- The corpus is intentionally narrow: UK Banking / Lloyds only.

### Usability limitations

- The workspace is text-heavy, but this is not an acceptance defect under the mission decision standard.
- `/flora` still contains legacy prototype navigation alongside the Increment 1 entry point, although it is labelled as legacy/pre-Increment-1 navigation.
- Increment 1 shows inspection-oriented evidence rather than a redesigned executive workflow.

### Implementation limitations

- The schema validator is intentionally small and scoped to the frozen Increment 1 fixtures rather than a full JSON Schema implementation.
- Fixture corpus loading is file-backed and does not include a production object store, production access-control adapter or runtime graph persistence.
- The supported runtime object set is deliberately limited to `BK-ENT-001` and the Lloyds alias.

### Architecture limitations

- Runtime graph persistence, deeper lineage traversal, context package schema, worker/provider boundary, Recommendation eligibility policy, audit retention and human review roles remain later-increment concerns.
- Proposed documents such as FEIR-001 and FA-001 may inform design but must not become accepted authority until their repository status changes.
- Increment 2 must still establish its own accepted reasoning boundary before implementing reasoning workers or generated outputs.

## Conditions for Increment 2

No Increment 1 acceptance condition remains open.

Before Increment 2 implementation begins, the team must still satisfy the normal Increment 2 entry conditions below; these are forward-looking architecture gates, not retained Increment 1 defects:

- define and approve the Increment 2 reasoning boundary, including what reasoning may do and what it must not do;
- define the context package / evidence package contract used by any reasoning worker;
- define provider, audit, retention and inspection requirements for any GPT or worker execution;
- preserve Unknowns and Contradictions without silent resolution;
- prohibit Recommendation, scoring, hypothesis promotion and write-back unless separately governed and accepted;
- keep `BK-ENT-001` Increment 1 read contracts stable or version any breaking change explicitly.

## Baseline declaration

### Accepted Increment 1 contracts

The accepted Increment 1 contract baseline is `flora-runtime-v0.1` under `schemas/flora-runtime/v0.1/`, covering focus object projection, relationship projection, evidence/observation availability, Unknown response, Contradiction response, Lineage response, Workspace State, Audit Event, Ingestion Report and Safe Unavailable Response.

### Supported object

- `BK-ENT-001` — Lloyds Banking Group Enterprise Twin.
- Alias accepted by the runtime: `lloyds`.

### Supported routes

- `/flora` — Flora home with visible Increment 1 Lloyds workspace entry point and labelled legacy prototype navigation.
- `/flora/object/BK-ENT-001` — primary Increment 1 Lloyds workspace route.
- `/flora/lloyds` — direct Lloyds workspace alias.
- `/workspace/enterprise/BK-ENT-001` — enterprise workspace alias.
- `/flora/object/unsupported-object` and other unsupported object identifiers under `/flora/object/` — safe-unavailable presentation.

### Supported capabilities

- Read-only focus-object projection for `BK-ENT-001`.
- Governed relationship projection without inferred relationship display.
- Evidence and Observation availability presentation.
- Governed Unknown presentation.
- Contradiction preservation.
- Inspectable complete, partial and access-redacted lineage presentation.
- Non-canonical workspace-state presentation.
- Safe-unavailable response for unresolved/unsupported identity.
- Contract-fixture validation and route validation.

### Explicit exclusions

- Increment 2 reasoning implementation.
- GPT or AI-provider invocation.
- Recommendations or Recommendation generation.
- Opportunity scoring or intelligence scoring.
- Hypothesis generation, validation workflow or promotion.
- Inferred relationship generation or hidden inference.
- Canonical mutation, canonical object creation or Enterprise Knowledge write-back.
- New Focus Object types or scope beyond the Lloyds `BK-ENT-001` read workspace.

### Reference commit or release

This acceptance baseline references local repository commit `479b45d` (`Merge pull request #311 from rdidale-jpg/codex/validate-flora-runtime-increment-1-workspace`) and implementation commit `40bbf86` (`Validate Flora Increment 1 Lloyds workspace`). The requested commit `9e3f57f` was not available in this checkout.

## Validation performed

| Check | Command | Outcome |
| --- | --- | --- |
| Relevant Increment 1 tests | `python -m pytest tests/flora_runtime/test_increment1_runtime.py` | Pass: 7 tests passed. |
| Schema/fixture validation | `python - <<'PY' ... validate_fixture_corpus() ... PY` | Pass: all valid, partial, safe-unavailable and expected ingestion-collision fixtures passed; invalid missing-authority focus-object fixture failed as expected. |
| View rendering smoke check | `python - <<'PY' ... increment1_workspace_page(...) ... PY` | Pass: `BK-ENT-001` rendered 200 with Lloyds content; unsupported object rendered 200 safe-unavailable with `identifier_unresolved`. |
| Application startup and route checks | `FLORA_HOST=127.0.0.1 FLORA_PORT=8765 python -m cios.applications.flora.web.app` plus `curl` route checks | Pass: application started and all checked routes returned HTTP 200 with expected titles. |
| Prohibited-capability scan | `rg -n "gpt|openai|recommendation|score|hypothesis|infer|inference|write.?back|canonical_objects|canonical" cios/applications/flora/runtime tests/flora_runtime fixtures/flora-runtime/increment-1/uk-banking schemas/flora-runtime/v0.1 docs/flora-runtime/increment-1-validation -i` | Pass: no implemented prohibited Increment 2 capability found in the Increment 1 slice; matches were boundary/exclusion/schema metadata. |
| Merged history check | `git log --oneline --decorate -5` and `git show --stat --oneline --decorate 9e3f57f -- ...` | Pass with note: local history confirms merged Increment 1 validation PR #311 at `479b45d`; requested `9e3f57f` is not present in this checkout. |

## Completion report

- Decision: **Increment 1 accepted — condition closed**.
- Files created: `docs/flora-runtime/increment-1-validation/Increment-1-Architecture-Acceptance.md`.
- Files modified: none beyond this acceptance record.
- Defects found: no material Increment 1 architecture defect found; the only evidence limitation is that requested commit `9e3f57f` is unavailable in this checkout, while equivalent merged validation history is present.
- Conditions retained or closed: the Increment 1 review condition is closed; no retained Increment 1 condition remains.
- Increment 2 readiness: Increment 2 is unblocked for architecture planning and entry-gate definition, but implementation must not begin until the forward-looking Increment 2 reasoning/provider/context/audit boundaries are approved.
