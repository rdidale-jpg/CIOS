# Factory Repair 01 — ownership and contract assessment

Recorded before implementation. Baseline main:
`5c1348a0aa714b0b1a63c08443447012689bb97b`, including merged #530–#533.
Retained TEL W5/W6 and BNK W1 bytes and the 8 November audit evidence are locally
available. No NRG artifact is assumed. ADR-002/009/012/026 remain unchanged.

## Reconstructed defect paths

Source `EV-*` -> Researcher adapter -> staged `original_source_id` and payload ->
`views._ensure_reviews_and_mappings` -> `propose_create` -> mapping ID generated
from package checksum/reference + source ID -> approved plan -> `_promote` uses
that proposed canonical ID -> EvidenceRepository indexes only `evidence_id`.
References in other records remain source IDs. The source payload survives but
canonical citation binding fails. Qualifiers/ClaimValidator are correctly strict;
they are not the repair point.

A newer package changes the proposed ID even for identical `source_payload`.
The mapping path never reconciles that source within governed Twin scope.
Same-approval replay already returns the existing execution receipt. Existing
fingerprints in live collection are URL/snippet-oriented and not a sufficient
identity contract for arbitrary Blueprint source claims. Use the existing SHA
utility over exact structured source content, not wording/URL similarity.

Retained manifests lack the complete optional governed identity set. The existing
projection is ambiguous and falls back to enterprise type. `current_release`
requires recognised identity, so the releases cannot be linked. The resolution
repository supports linking to an existing recognised package but cannot record
an initial explicit owner decision. Industry acceptance must require such a
bounded, authorised decision, not a filename or a guessed owner.

## Minimum changes and owners

| Boundary | Existing owner | Bounded change |
| --- | --- | --- |
| Identity decision | GovernedIdentityResolutionRepository / shared BlueprintManifest | Add an explicit complete identity decision with actor/rationale/authorization, preserving immutable package metadata. Existing recognised-identity linking remains. Scope includes access owner/workspace, type, stable Twin, primary subject, canonical owner and governed scope. |
| Source mapping | ImportMappingService / repository | Reconcile exact source ID within that governed scope; retain a free source ID safely or allocate a scoped canonical target for a different owner. Ambiguous same-scope identities fail. Show new/unchanged/corroborating/update/conflict/unresolved distinctly. Explicit reviewed updates preserve history. |
| Evidence truth | EvidenceRepository | Remains the only Evidence store and getter. Add source-scope/content/provenance metadata to accepted rows; no second index or permissive getter. No legacy migration. |
| Citation binding | CanonicalPromotionService | Bind controlled Evidence-reference fields through approved mappings before canonical construction/write, while retaining source payload/IDs and binding lineage. Reject ambiguous, foreign or rejected supplied bindings. |
| Replay/version provenance | Existing mapping/approval/execution/ledger and Evidence record | Unchanged source reuses identity; new release provenance is appended under compensation, without new logical rows or confidence inflation. Updated content needs explicit reviewed mapping and retains prior canonical version. |
| Release current/superseded | TwinImportLifecycleService | Match full governed owner/scope, not only a Twin label. Record release-current changes inside the existing compensated promotion boundary; failed or interrupted execution cannot leave a false current receipt. |
| Operator views | Existing review/completion and web route | Add explicit identity decision and mapping/status disclosure only. Distinguish technical, canonical Evidence and partial domain outcomes. No Canvas/dossier repair. |

The existing optional manifest identity contract is sufficient. No new ADR,
canonical store, identity subsystem, reasoning engine or Researcher-content rewrite
is required. Industry wrappers, Banking associations/fields and model projection
remain outside scope.

## Safety and testing commitments

Source IDs are not globally unique. Automatic reuse requires exact source identity,
matching owner/scope and accepted current support. Equal URLs or similar wording do
not establish identity. Same-scope changed assertions are unresolved until explicit
owner update; explicit contradictory candidates remain conflicts, not silent
replacement. Canonical state is rechecked at approval and execution.

Source payloads, locations and prior-release provenance remain inspectable.
New provenance is metadata, not a new fact or increased confidence. Unknown
legacy scope requires explicit mapping; no existing release is silently relabelled.
Tests cover the real UI defaults and retained bytes, plus scoped collisions,
rejected support, changed content, stale plans, replay and compensation. The
retained artifact hashes are held constant in baseline and after runs.
