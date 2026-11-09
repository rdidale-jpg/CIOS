# Security Bootstrap Contract v1.0

Status: Approved with amendments as the design baseline; this repository change
records the user's approval and implements only Security Repair 01A. Repair 01B,
production deployment and provisioning require separate explicit authorisation.

Baseline: `dc9203e6880f8722e821d39cf53b689732edb0e7` (main including #537/#538).
Research policy: Assurance. Capability profile: isolated code/tests and PR only.

## Authority and reconciliation

The requesting administrator confirms control of the CIOS GitHub repository and
Flora Render account and is the initial trusted deployment operator. Deployment
control is not intelligence-workspace ownership. No account/workspace identifier
is inferred from this designation, a display name, username or synthetic fixture.

Before 01B activation, the operator must inspect the actual existing persistent
root read-only and reconcile package actors/workspaces, Canvas ACLs, review
records, promotion approvals/executions, lifecycle records and audit events.
Record exact identifiers, file digests, supporting ownership evidence,
contradictions and the explicit binding decision. Historical unauthenticated
claims and shared pilot acknowledgements are not verified human acceptance.
Conflicting or absent ownership remains Unknown and blocks that binding.

There is no complete verified user/membership registry in pinned main. Existing
Canvas ACLs describe resource visibility, not the authenticity of their original
principal. Imported domain membership objects are not product-user memberships.
Existing Enterprise and Industry identities retain their current owners.

## Offline bootstrap planned for 01B

Only the explicitly authorised deployment operator may run the offline command;
there must be no public bootstrap or first-user-becomes-owner route. Operator
credentials stay in protected platform/credential storage, not Git or arguments.

1. Verify target service, deployed SHA, existing disk and data root.
2. Present an approved reconciliation manifest and exact target account,
   workspace, role and evidence digests.
3. Produce a dry-run plan; require confirmation of the exact identifiers and
   plan digest; fail closed on contradictions or stale evidence.
4. Apply under a transaction/exclusive lock. Membership plus security audit
   receipt commits atomically. No silent overwrite, wildcard grant or unrelated
   workspace access is permitted.
5. Repeating the identical plan returns the same receipt. A conflicting repeat
   fails and requires a separately approved recovery/change decision.
6. Keep an independent protected backup of the binding evidence and receipt.
   Correct receipts by adding linked events, not rewriting historical events.

Enterprise-grade immutable archives and multi-party operator attestation are
DEFERRED. Append-only/hash-linked local events and independent protected backups
provide operational audit and tamper detection, not immunity to a compromised
host/operator or guaranteed immutable retention. Do not overstate this assurance.

## Minimal operational security persistence planned for 01B

SQLite is conditionally approved for the single-instance pilot, subject to
filesystem durability/locking and security/usability tests. No SQLite store is
created by 01A. Keep FLORA_DATA_DIR and the existing disk unchanged.

Only verified principals, workspace memberships, credentials/enrollment,
revocable sessions and security audit records may be stored. Membership records
reference verified existing workspace IDs; there is no new workspace, Enterprise
or intelligence identity authority. Do not copy Evidence, Observations, Twins,
Enterprise Models, Opportunities or Procurement into this store.

The existing capability evaluator remains the permission-policy owner.
Membership is necessary but does not override existing resource ACLs, workspace
boundaries or canonical governance. Capability/role changes and revocation are
server-controlled and audited. Missing/corrupt state fails closed, never by
falling back to cookies, headers, legacy configuration or automatic bootstrap.

## Human sessions planned for 01B

Use individual verified credentials/enrollment or a separately reviewed identity
provider. No shared owner password, unsigned identity claim or header-trust flag
establishes authority. Enrollment grants no additional membership.

Pilot defaults proposed for validation:

- Eight-hour absolute lifetime and thirty-minute inactivity timeout.
- Immediate revocation on logout, account disablement or membership removal.
- Recent reauthentication for promotion, storage recovery and security admin.
- Cryptographically random opaque tokens; hashes stored server-side; no browser
  role/workspace claims as authority. Rotate tokens on authentication and
  workspace change; do not restore revoked sessions from backups.
- Secure, HttpOnly, host-only cookies, Path=/ and appropriate SameSite policy.
- Session-bound CSRF tokens and exact configured-origin verification before
  state-changing browser operations, including login/enrollment protections.
- Explicit selection among server-authorised workspaces and service-side checks
  immediately before mutation. Credential recovery revokes existing sessions.

A stolen active bearer token remains a risk until expiry/revocation. Password
hashing parameters, throttling, recovery and session usability must be validated
before activating 01B; 01A does not claim to implement or test them.

## Governance and deployment gates

Authentication authorises permitted actions; it does not accept candidate
intelligence. Never auto-approve imports, rewrite pilot review attribution,
manufacture human decisions or bypass canonical constructors/fingerprints,
approval rationale, compensation, lineage or execution receipts.

No privileged production operation may be enabled before verified owner
identity, membership, workspace isolation and negative security acceptance pass.
Then obtain explicit human rollout approval. Safe rollback must retain the
repaired trust boundary or close the service; never restore unsigned authority.

ADR-002/009/012/014/024/026 boundaries are preserved. ADR-014/024 have pre-existing
Draft headers and Accepted body/index status; that ambiguity remains recorded,
without editing accepted decisions. This contract creates no canonical enum,
intelligence store, migration, backfill or owner reassignment.
