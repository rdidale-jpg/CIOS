# CIOS Architecture Authority Registry

**Document class:** Architecture governance registry  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11

## Purpose

This registry records architecture authority status and release-profile membership for review material that must not be mistaken for accepted architecture. It complements the Reference Architecture, Accepted ADR index and owning EI/FP papers; it does not supersede them.

## Status taxonomy

| Status | Meaning |
| --- | --- |
| Accepted | Approved architecture authority within its stated scope. |
| Draft | Work-in-progress architecture material; useful but not final authority. |
| Proposed | Submitted for decision; not accepted and not authoritative. |
| Review | Review material being evaluated; not accepted and not authoritative. |
| Superseded | Retained for history after a newer authority replaces it. |
| Rejected | Reviewed and not adopted. |

## Release-profile taxonomy

| Profile | Meaning |
| --- | --- |
| architecture-authority | Accepted or otherwise owner-designated authoritative architecture material. |
| researcher-pack | Material approved for production research-agent use. |
| reviewer-pack | Material approved for production reviewer use. |
| none | No production release-profile membership. |

## Review-material registry entries

| ID | Title | Path | Status | Authority classification | Release-profile membership | Dependencies | Validation trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EU-001 | Enterprise Understanding Contract | `architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md` | Review | Proposed operational contract / review material; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack` | Reference Architecture; EI-001; EI-002; EI-003; EI-012; FP-009; ADR-009; Commercial Digital Twin Blueprint Contract | MOD and one materially different enterprise |
| ADR-023 | Enterprise Understanding as the Primary Governed Asset | `architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md` | Proposed | Proposed ADR; not accepted and not authoritative | none — excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack` | Reference Architecture; EI-001; EI-002; EI-003; EI-012; FP-009; ADR-009; Commercial Digital Twin Blueprint Contract; EU-001 | MOD and one materially different enterprise |

## Production profile note

EU-001 and ADR-023 are intentionally absent from the current `FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json` export profile. They must not be added to production Researcher or Reviewer packs until a separate accepted architecture decision approves that change.
