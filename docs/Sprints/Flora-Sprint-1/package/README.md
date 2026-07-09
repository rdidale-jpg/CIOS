# CIOS Flora Sprint 1 Architecture Package v0.1

**Prepared:** 2026-07-09  
**Owner:** Rob / CIOS  
**Purpose:** Establish the architecture and experience baseline that must be merged before further Flora Codex implementation sprints.

## What this package decides

This package records two accepted decisions:

1. An accepted Blueprint package is not automatically canonical Enterprise Memory. Flora must preserve the package, stage candidate intelligence and promote eligible objects through explicit governance.
2. Flora's primary Living Twin navigation is an Enterprise Canvas. Tiles and panels are views over governed state, with progressive disclosure into pains, responses, uncertainty and lineage.

## What this package enables

The first Flora sprint can now be implemented as a sequence of bounded PRs:

- code-binding audit;
- immutable package receipt;
- MOD package adapter and staging;
- validation, mapping and idempotency;
- acceptance, promotion, ledger and reversal;
- Living Twin read model and lineage;
- Enterprise Canvas;
- governed feedback.

## GitHub installation

Copy the package contents into the repository root, preserving paths.

The package contains changed and new files only. It assumes the existing CIOS repository already contains the referenced Founding Papers, Enterprise Intelligence papers, earlier ADRs and application code.

Recommended merge order:

1. Review `architecture/decisions/ADR-012...` and `ADR-013...`.
2. Merge the architecture package as one documentation PR.
3. Run the PR 0 read-only code-binding audit.
4. Review the audit and issue bounded runtime PRs from the Sprint Plan.
5. Do not start runtime implementation by coding directly against the MOD workbook.

## New files

- ADR-012 and ADR-013;
- Blueprint Import Runtime Specification;
- Blueprint Package Import Profile;
- Enterprise Intelligence Experience Standard;
- Enterprise Canvas and Drill-Down Pattern;
- Flora Sprint 1 Delivery Plan;
- Codex PR 0 prompt;
- Architecture Compliance Statement.

## Updated files

- CIOS Reference Architecture v1.0;
- Glossary;
- Document Map;
- ADR index.

## Architecture boundary

No change is made to EI-001, EI-002 or EI-012 semantics.

Pain Point, Burning Platform, Transformation Pressure, current response, residual pain, solution pattern and executive publication remain analytical projections unless a future owning specification or ADR changes that decision.

## Pilot input

The implementation pilot should use the accepted:

`MOD-CDT-v1.2-HSK-Incorporated-Clean-Release.zip`

Do not commit client or bid-sensitive package contents to a public repository. Use a secure local/test fixture strategy appropriate to the repository.

## Start here for Codex

Use:

`docs/Sprints/Flora-Sprint-1/Codex_PR0_Read_Only_Runtime_Binding_Audit.md`

The first Codex task is documentation-only. It must map the architecture to the actual codebase before runtime changes.

## Acceptance statement

This package is the approved architecture baseline for Flora Sprint 1.

Runtime maturity must remain honest: merging the documents does not mean Flora has implemented Blueprint import or a Living Twin Canvas.
