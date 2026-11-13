# Offers v1 — controlled pilot contract

Review of draft PR #575 at `667ce1b3d1f77d4c7d66b20e21c595e7b4882cbb` against Issue #576. The proposal remains a proposal; this review defines the bounded implementation, not a new normative architecture release. Base: main `854a783b3c5f83d6ee3604f49a76772529b7339a`. Independent of unmerged UX PR #574.

## Ownership reconciliation

| Concern | Existing owner and pilot decision |
|---|---|
| Seller identity / mission | Revocable SecurityStore membership; reference existing CommercialMission context/version. One active authorised employer at a time. No inferred identity. |
| Employer | Existing EmployerContext remains a declaration. A CIOS owner explicitly binds it to named active workspace members and delegates a distinct approver. A profile name alone grants no rights. Optional canonical identity is deliberately unbound in this pilot. |
| Offers | Versioned operational extension under existing `commercial_context`, alongside existing mission/employer profiles. No Offer Twin or seller intelligence store. Canonical `capability_offer` and Market Participant truth remain owned by semantic Twin/package promotion; pilot declarations never create or claim those bindings. |
| Assessment | One pure deterministic APPA-aligned interpretation projection, never persisted as opportunity or accepted APPA. Includes source/observation/hypothesis lineage, exclusions, Unknowns, alternatives and limits. Unresolved participant binding means no complete canonical APPA claim. |
| Evidence | Read existing research overlays through their existing validation and SourceSegment adapters. Preserve source status, content digests, retrieval limits and candidate authority. No evidence ingestion/promotion. |
| Pipeline | Existing `sales_pipeline` is sole writer. Pilot only links to its existing Banking/Aviation manual qualification UI. No new writer, origin type, automated capture or claim of unbound Technology capture support. |
| Creative | Explicit per-user/per-workspace opt-in; deterministic composition of accessible version-pinned offers. Private drafts; separate employer approval. No model SDK, paid calls, autonomous agents or outreach. |

## Permissions and state

All reads require `commercial_context.view`; all writes require `commercial_context.edit`, real session, active membership, existing CSRF/origin checks and protected service transaction. Employer setup additionally requires existing CIOS owner authority and an explicit approval reference; delegates must be active members of the same workspace. Approval additionally requires delegated employer approver status, recent authentication and a different reviewer from the author. This is organisational publication approval, never evidence acceptance. No new generic role grants.

Private versions are visible only to author in the same workspace/employer. Submitted versions are also visible to delegated reviewers. Approved versions are available to explicitly bound employer sellers. Only delegated approvers can draft changes to, or withdraw, an employer-approved master; a different reviewer must approve the revision. Changes create immutable versions with optimistic concurrency; prior approval does not carry forward. Variations pin an approved parent version, can change only sector/buyer emphasis and entry play; protected claims/constraints/evidence remain inherited. Retired or superseded parents invalidate their variations for discovery. Withdrawal retains audit/history and does not alter previous assessments.

Private state is stored at `commercial_context/offers-v1/context.json` (0700 directory, 0600 file). The operational envelope contains bindings, selected employer, opt-in and offer versions, not copied enterprise facts or match results. The existing protected journal and atomic JSON writer participate in SecurityStore transactions; audit failure or persistence failure rolls back effects. Audit stores record digests and lineage identifiers, not raw private offer content.

## Matching contract

Identity = seller/workspace + selected employer/binding revision + mission version + offer ID/version + enterprise ID + evidence cutoff + policy version + evidence/content digest. Both discovery paths call exactly the same assessment function; selection only filters pairs. Account access uses the existing resource evaluator. Unknown access, competition, rights and economics constrain posture; no win probability, intent inference, procurement claim or invented value. Pilot recommendations stop at research/validate/partner/deprioritise; create-demand/shaping/pursuit require customer validation outside this pilot. Research maps to APPA `learn`; no sponsored change or complete accepted APPA is claimed.

## Threat model and migration

Threats: employer-name privilege escalation; direct-object/private-version disclosure; self-approval; stale-parent claims; cross-workspace composition; forged identifiers; CSRF; stale/concurrent writes; revoked membership; evidence-cutoff drift; XSS; duplicate pair identities; accidental Pipeline/paid activity. Mitigations and negative tests cover each boundary. No migration of existing profiles, enterprise intelligence or Pipeline records. Operational state is additive. Owner review of bindings and offer rights is required before real organisational use; illustrative templates are not approved company propositions.

Rollback: revert the feature commit to remove routes/navigation, retain the protected operational file for approved retention, and revoke employer bindings/disable Studio before re-enabling. Do not restore old authority snapshots or overwrite Pipeline. No deployment configuration change or deployment in this sprint.
