# Increment 1 Delivery Definition — Read-Only Object Workspace Slice

## Scope boundary

Increment 1 is a read-only object workspace over a bounded UK Banking governed corpus. It must not implement runtime services beyond local adapters/projections required for the slice, must not introduce runtime infrastructure, and must not write canonical knowledge.

## Supported Focus Object types

1. `industry`: UK Banking.
2. `enterprise`: only enterprises already named in governed Banking assets.
3. `mechanism` or `pressure`: only banking mechanisms/pressures already present in governed Banking assets.
4. `observation`: only existing Observation records/rows with source lineage where available.

## Governed corpus

- `enterprise-knowledge/banking/flora/Banking-Knowledge-Manifest.json`
- `enterprise-knowledge/banking/flora/Banking-Knowledge-Register.md`
- `enterprise-knowledge/banking/flora/Banking-Strategic-Sales-Navigation-Specification.md`
- `enterprise-knowledge/banking/industry/`
- `enterprise-knowledge/banking/infrastructure/`
- `enterprise-knowledge/banking/reinvention/`
- `enterprise-knowledge/banking/governance-reports/`
- Existing repository-backed Evidence/Observation/Enterprise Model code paths may be read only when they can expose stable ID, owner and source path.

## Supported relationships

- Focus object to source asset.
- Industry to banking mechanism/pressure where explicitly recorded.
- Enterprise to Observation where explicitly recorded.
- Observation to Evidence/source reference where available.
- Unknown/Contradiction to parent focus object or asset.

No inferred relationship becomes canonical; unresolved relationships are marked `relationship_unknown`.

## Evidence and Observation views

- Availability counts and lists where records exist.
- Source/evidence/observation identifiers where present.
- Safe unavailable response where lineage is absent or access denied.
- One-hop lineage from displayed object to source asset; deeper lineage deferred.

## Unknowns and Contradictions

Increment 1 displays existing Unknowns and Contradictions from the governed corpus and preserves missing evidence as Unknown. It does not resolve, rank, suppress or rewrite them.

## Workspace state

May persist only:

- selected focus object;
- selected perspective;
- exploration trail;
- filters;
- read-only inspection state;
- user preference needed for workspace experience.

Workspace state is runtime state and must not be interpreted as Enterprise Knowledge.

## Access boundary

- Authenticated user required.
- Workspace/enterprise allow-list required.
- Asset/object access checked before projection.
- Cross-enterprise retrieval denied unless source asset explicitly governs comparison.
- Audit access restricted to runtime operator/architecture reviewer.
- Denial returns safe unavailable, not partial leakage.

## Explicit exclusions

- GPT workers or model-provider selection.
- Runtime graph database/product selection.
- Canonical Evidence/Observation/Enterprise Model writes.
- Knowledge Pack promotion.
- Candidate intelligence persistence beyond audit/projection diagnostics.
- Strong Recommendations, opportunity scoring or opaque ranking.
- Write-back proposals.
- External-output approval flows.
- Refactoring existing Flora UI beyond isolating read-only slice entry points.

## Acceptance criteria

1. User can open UK Banking Focus Object and inspect identity, owner, source assets and status.
2. User can switch between overview, relationships, evidence/observations, Unknowns/Contradictions and lineage perspectives.
3. Every displayed material object has source path/version/cut-off where available or safe-unavailable reason.
4. No canonical governed asset is written.
5. Workspace state persistence contains no canonical facts.
6. Access denial and missing lineage are safe and auditable.
7. Audit event fixture validates all baseline fields.
8. FA-001 compliance checklist, Flora DoD, accepted ADR checks and no-second-source-of-truth review pass.

## Validation plan

- Static contract tests for interface fixture shape.
- Repository path tests for governed corpus.
- Collision report for object IDs.
- Access allow/deny tests.
- Safe-unavailable tests for missing asset, missing lineage and denied enterprise.
- Manual architecture review against FA-001, Flora Definition of Done, ADR-001, ADR-005, ADR-014, ADR-016 and ADR-024.

## Estimated implementation sequence

1. Approve Increment 1 read interface and identity specifications.
2. Add read-only corpus adapter and path validator.
3. Add Focus Object projection fixtures for UK Banking.
4. Add relationship and Evidence/Observation availability projections.
5. Add Unknown/Contradiction and lineage projections.
6. Add workspace state persistence constrained to runtime state.
7. Add audit event emission and validation fixtures.
8. Wire minimal UI routes while isolating pilot collection/write/reasoning routes.
9. Run compliance and no-second-source-of-truth validation.
