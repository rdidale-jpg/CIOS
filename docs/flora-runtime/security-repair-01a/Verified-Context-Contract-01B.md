# Verified context integration contract for Repair 01B

The approved Security Bootstrap Contract v1.0 remains authoritative. This document
specifies its minimal application projection, defined as read-only Protocols in
`cios/applications/flora/verified_context_contract.py`. Protocol shape is not proof
of identity. There is no constructor, registration API, issuer, persistence or
runtime switch in 01A. `security.verified_context` unconditionally returns None.
Arbitrary objects, headers, cookies and environment flags cannot install a producer.

| Projection | Required fields and meaning |
| --- | --- |
| Principal | `user_id`: stable server-verified individual; `verified_human`: true only after verification; `authentication_source`: trusted mechanism label, never a request assertion |
| Workspace | `workspace`: selected workspace; `workspace_ids`: server-resolved active membership choices, independently of Enterprise grants |
| Membership | `membership_id`, `user_id`, `workspace_id`, immutable `roles`, `version`, `active`, `checked_at`; selected identity and workspace must match context; absent membership grants no workspace authority |
| Capabilities | Immutable `effective_capabilities` snapshot computed server-side from active membership/policy; context `roles` is the compatible existing role projection |
| Enterprise scope | Immutable `enterprise_ids`: permitted Enterprise scope within the selected workspace; wildcard never supplies workspace membership or bypasses a resource ACL |
| Session | `session_ref` is a non-secret audit reference, not bearer material; `authenticated_at`, `expires_at`, `idle_expires_at`, optional `reauthenticated_at`, `revoked`, `revocation_version`, `checked_at` |

01B must implement a trusted, server-controlled producer at the existing resolver
seam. Before returning an immutable request snapshot it must verify principal,
session integrity/expiry/revocation, current active membership, selected workspace,
role/capability policy and Enterprise scope. Missing, ambiguous, stale or unavailable
verification returns no context. Recheck revocation and membership every request
and before consequential writes; a cached snapshot must not survive invalidation.
The approved proposed defaults remain eight-hour absolute and thirty-minute idle
expiry; a thirty-day legacy pilot cookie is not the contract. No browser value,
shared pilot secret, deployment operator status or owner environment flag supplies
membership or authority. Deployment user administration does not imply workspace
ownership. No hardcoded individual role or shared reviewer attribution is allowed.

Application authorization is the intersection of verified identity, active selected
workspace membership, effective capabilities, existing role policy, permitted
Enterprise scope, resource workspace binding and resource ACL. `require_capability`
now bounds the existing evaluator by the effective-capability snapshot. The upload
decision consumes actual membership, not an Enterprise wildcard. Existing owner
aliases remain policy inputs, not identity producers. 01B must produce consistent
projections and test all service entry points, including existing specialized policy
checks; the Protocol itself does not perform authorization.

Every write, review, approval and execution must record the verified individual,
selected workspace, membership/policy and session references and resource identity.
Submitted actor IDs must equal the verified actor; correlation IDs are not identity.
Preserve independent protected audit/backup requirements in the approved contract.
Do not record raw session tokens or secrets in attribution.

## Positive obligations deferred to 01B

Demonstrate individual sign-in, secure cookie handling, restart behavior, absolute
and idle expiry, logout/revocation, session rotation and required reauthentication.
Demonstrate active membership selection and revocation, cross-workspace denial,
Enterprise and ACL intersections, least privilege and role changes. Show authorised
upload/inspect/stage/review dispositions and separately permitted promotion, with
correct individual attribution and unchanged canonical state until authorised
execution. Exercise malformed archives after identity acceptance, unavailable
authority/audit stores, and absence of private diagnostic disclosures. Tests must
use the real producer, not the opt-in test-only service fixtures. See the retirement
matrix for per-workflow obligations. None of these mechanisms is implemented here.
