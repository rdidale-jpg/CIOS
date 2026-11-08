# Security Repair 01A completion report

Implemented Trust Boundary Hardening against verified main
`dc9203e6880f8722e821d39cf53b689732edb0e7`, including merged #537 and #538.
Privileged access is closed pending the separately authorised Repair 01B.
No merge, deployment, Render/environment change, account provisioning, workspace
reassignment, canonical promotion, migration or production data mutation occurred.

## Implementation

Browser cookies, role/workspace/enterprise assertions, legacy signed sessions,
shared pilot actors and identity-header flags cannot resolve a production
principal. There is no session issuer, provider-registration flag, bootstrap
endpoint, SQLite database or temporary owner bypass. The verification seam
returns no principal in 01A; 01B must supply real verification and membership.

The main handler denies protected GET/HEAD before resource reads and privileged
POST before body parsing/dispatch. Source-curated public Banking and discovery
remain readable. The only accepted public POST is the existing reference
navigation preference, requiring exact configured Origin and granting no
identity/capability or server intelligence write. Missing origin configuration
keeps it closed. The obsolete secondary workspace HTTP listener is also closed.

Service-level checks protect financial review/apply, brief attribution,
recovery/cleanup, deletion, review preparation and existing review/promotion
boundaries. Explicit resource workspace checks precede wildcard enterprise grants.
Review/approval/execution attribution must match the verified actor. Review GET
renders existing state; preparation is now a separate explicit operation.

Public import setup does not enumerate the registry. Candidate-backed panels
filter access before constructing output. History no longer globally appends
unscoped tombstones or invents canonical Banking history from a source-file
presence check. Historical records remain intact for restricted operator
reconciliation. Existing constructors, plans, rationale, fingerprints,
compensation, lineage and canonical execution receipts are retained.

## Evidence and comparison

The earlier 12 isolated baseline reproductions ran against the same main SHA
before implementation. Final identical-test-source comparisons are in
[Regression-Comparison.json](Regression-Comparison.json).

| Exact case set | Pinned main | Repair 01A |
| --- | --- | --- |
| 61 new security/service cases | 15 passed, 46 failed | 61 passed |
| 436 cases in 26 domain/governance modules | 403 passed, 23 failed, 10 skipped | 404 passed, 22 failed, 10 skipped |

All 61 new cases pass: 58 exercise actual production resolution/local HTTP with
no fixture provider; three explicitly mocked service-context cases prove GET
read-only behaviour and workspace isolation. Complete synthetic-store hashes
remain unchanged through the tested rejected and public journeys. No test
performs live upload, deletion, recovery or promotion.

There are zero newly failing cases in those two exact-case comparisons. The one
fixed domain case is the strengthened unsigned-cookie rejection assertion;
legitimate owner-role alias behaviour retains a positive service-fixture check.
The comparison includes its original/revised ID mapping. All other domain
assertions remain. Domain tests explicitly opt into a test-only service identity
provider, not header trust in production. Review setup and reasoning tests now
supply explicit mutation setup/request context; the same overlay is used on main.
These fixtures do not demonstrate real sign-in or 01B readiness.

Factory Repairs: evidence/release 38 passed / 3 skipped; researcher/model 29
passed / 3 skipped; presentation 21 passed / 2 skipped. Experience Repair 01:
31 passed. Experience Repair 02: 25 passed / 2 skipped. Retained TEL W5 journeys
pass with original hash-pinned archive bytes. BNK W1 and TEL W6 are unavailable;
the ten skips across modules are existing explicit retained-input skips, not
suppressed security failures. No substitute package is invented or uploaded.

The 22 inherited failures are Banking portfolio increment 3 (7), executive
navigation increment 44 (4), visual increment 45 (1), visual correction 451 (1),
reinvention increment 42 (6), and Enterprise Canvas (3). Exact IDs and failure categories/digests
are retained publicly; raw diagnostics remain in local JUnit evidence. This is not an entirely green repository claim.

### Historical permissive pilot tests

The original, unmodified legacy auth/pilot suites were also run separately:
main 22 passed / 5 failed; 01A 3 passed / 24 failed. Nineteen previously passing cases now fail;
the five previously failing cases also remain failed. These historical contracts expect
legacy owner cookie issuance, header-derived owner access, shared pilot review
or anonymous intake that the user explicitly authorised 01A to discontinue.
Their exact before/after IDs are in
[Retired-Legacy-Contracts.json](Retired-Legacy-Contracts.json). They are not
silently classified as passing or inherited. The new production-boundary tests
replace those insecure acceptance expectations; no permissive authentication
is restored to make the historical suite green. Full legacy workflow
compatibility is intentionally not an acceptance claim for 01A.

Compile and diff checks pass. No production-origin or hosted-CI validation is
claimed. Final affected-module reruns replace preliminary results by exact case
ID; reproduction instructions are in [Testing.md](Testing.md).

## Updated design and rollout

[Security Bootstrap Contract v1.0](Security-Bootstrap-Contract-v1.0.md) records the
approved amendments: single-owner/single-instance proportionality, explicit
offline binding, atomic membership creation and audit, independent protected
backup, conditional operational SQLite, eight-hour absolute/thirty-minute idle
session defaults for validation, and immediate revocation. Enterprise immutable
archives/multi-party attestation are deferred with assurance limits stated.
No Accepted ADR is edited; ADR-014/024 metadata ambiguity remains explicit.

[Trust Boundary Assessment](Trust-Boundary-Assessment.md),
[Negative Test Matrix](Negative-Test-Matrix.md), and
[Deployment and Rollback Plan](Deployment-and-Rollback.md) identify decisions,
coverage, known limitations and safe transition. Rollback may retain the repair
or close the service; it must never restore unsigned-cookie authority.

## Remaining dependencies and risks

- Legacy privileged workflows and private resource routes are intentionally
  unavailable. There is no working verified owner journey in 01A.
- 01B needs separate authorisation, verified existing human/workspace bindings,
  offline operator provisioning, server-controlled membership and credentials,
  revocable sessions, workspace selection, resource ACL intersection, recent
  reauthentication, session-bound CSRF/origin protections and negative tests.
- Existing service/disk/root and deployed SHA remain unverified production facts.
  Protected independent backup and an approved binding precede provisioning.
- Actual owner review/promotion/logout must pass on isolated synthetic data
  before explicit human approval for privileged production activation.
- Unscoped historical tombstones need evidence-backed scope resolution before
  online audit visibility can be restored. No history is deleted or reattributed.
- The historical operational declaration/schema mismatch remains; no PASS
  metadata is fabricated. It requires separate evidence-based reconciliation.
- Host/operator compromise and active bearer-token theft are not solved by a
  closed browser boundary. Session/credential security is deferred to 01B.

Stop after Security Repair 01A. This PR is for review only: do not merge,
deploy, provision, activate privilege or begin 01B automatically.

## Public draft publication review

The administrator explicitly authorised a public draft in rdidale-jpg/CIOS.
The [publication safety review](Publication-Safety-Review.md) covers the entire
committed repair diff and documentation. Public comparison artifacts preserve
case IDs, statuses, counts, failure categories and diagnostic SHA-256 digests;
verbose request/trace excerpts are omitted. The application implementation and
recorded test outcomes are unchanged by this publication-only redaction.
