# Flora package authorisation boundary audit

## Current boundary findings

| Concern | Finding | Classification |
|---|---|---|
| Authentication | `authenticated_flora_user` resolves the pilot session first, then explicitly trusted proxy headers or Flora cookies. | Implemented and reusable |
| Active workspace | `active_flora_workspace` uses canonical session workspace, or a selected/single workspace constrained to the account's allowed set. | Implemented and reusable |
| Membership | Blueprint receipt requires the active workspace to occur in authenticated workspace access. | Implemented and reusable |
| Owner recognition | Canonical owner roles inherit import permissions through the shared Flora access registry, not route exceptions. | Implemented and reusable |
| Receipt | `package.upload` is the established receipt permission and is enforced before route code reads the submitted bytes. | Implemented and reusable (canonical equivalent of logical `package.receive`) |
| Inspection | Inspection was coupled to `package.review`; the validator already enforced it at its service boundary. | Implemented but too broadly scoped |
| Review | `package.review` guards review routes and review-decision services. Review records and staging are non-canonical. | Implemented and reusable |
| Promotion | `candidate.promote` guards route approval and both canonical service approval and execution. | Implemented and reusable |
| Archive safety | ZIP inventory validation, traversal checks, limits, checksum verification, and immutable archive preservation are in the existing registry/validator. | Implemented and reusable |
| Retention | Successfully received originals are retained by archive storage; rejected receipts create no package/run record; cancellation retains audit and follows the existing archive policy. No new retention rule is introduced here. | Implemented and reusable; expiry duration unclear |
| Lifecycle/history | Durable receipt, staging/audit, cancellation and promotion records exist. The lifecycle vocabulary does not yet express every requested denied/awaiting state. | Partially implemented |
| Diagnostics | The summary accepted a caller-provided stage while the table inferred authentication failure independently, causing contradictory failed stages. | Implemented but too broadly constructed |
| Package contracts | Blueprint is the only current contract. Generic multi-contract detection and lifecycle support are not present. | Missing (deliberately deferred) |

## Capability mapping

| Logical boundary | Canonical capability | Notes |
|---|---|---|
| Package receive | `package.upload` | Existing canonical name retained for compatibility. Requires account, active workspace and membership. |
| Package inspect | `package.inspect` | Added to the canonical Flora import permission registry. Existing `package.review` remains an inspection superset for role compatibility. Inspection alone grants neither review nor promotion. |
| Package review | `package.review` | Existing candidate/review authority retained. |
| Package promote | `candidate.promote` | Existing stronger capability retained and rechecked by `CanonicalPromotionService`. |

Canonical owners and `blueprint_import_admin` inherit all four permissions. A workspace member can now hold `package.upload,package.inspect` without review or promotion.

## Stage and diagnostic model

The single ordered presentation model is: Account recognised; Workspace recognised; Membership resolved; Package receive permission checked; Upload request accepted; Package received; Package inspected; Package validated; Review generated; Canonical import committed.

For a terminal failure, the model marks preceding stages `Completed`, exactly one stage `Failed`, and subsequent stages `Not started`. The failure summary derives its failed stage and receipt/inspection facts from that same model. Thus an anonymous request reports Account recognised as the sole failure and never claims receipt, inspection, validation, or canonical changes.

## Implementation and impacts

* Inspection-only users can receive and validate a Blueprint and view filename/package identity, checksum, detected type, profile version, asset counts, warnings, errors and compatibility. The report explicitly says inspection does not change the governed Twin.
* Review links are omitted without review authority. Promotion forms are omitted without promotion authority, and direct promotion confirmation and execution remain server-side denied.
* Existing review roles retain inspection access, avoiding a Blueprint and Banking regression. No importer, IAM subsystem, canonical persistence format, or retention policy was duplicated.
* Canonical writes remain confined to explicit promotion service execution. Inspection and denials preserve zero canonical writes.

## Remaining unknowns and contradictions

* Archive retention has an established preservation boundary but no explicit expiry duration in the inspected lifecycle service.
* Import history does not yet persist pre-receipt rejections (correctly) and does not provide every requested fine-grained denial/awaiting lifecycle state.
* Receipt currently performs safe ZIP inventory and Blueprint identity reading as one atomic registry operation. A future storage quarantine abstraction would be needed to persist bytes before semantic identity inspection without weakening archive checks.
* The current package model requires Blueprint identity and therefore is not ready to represent the other proposed package contracts. This increment intentionally does not reinterpret them.

## Recommendation

**Merge.** This is the smallest evidence-based increment: it separates inspection from promotion, fixes the observed diagnostic contradiction, keeps existing receipt/review compatibility, and preserves all canonical no-write and promotion-service controls. Follow-up work should define retention expiry and broaden lifecycle states before multi-contract ingestion.
