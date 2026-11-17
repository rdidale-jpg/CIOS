# AUTH-2: public intelligence, managed individual identity

Commission: #655. Implementation proposal for owner review; no ADR is accepted by
this PR. Baseline `7b056b21cd5d824bc4359b4e1ed49a1673a7f5fc`, full main run
[44057735885](https://github.com/rdidale-jpg/CIOS/actions/runs/44057735885) passed.

**Implemented, not live-activated.** Supabase is an individual identity provider;
CIOS remains the only workspace, role, enterprise/resource ACL, canonical and audit
authority. Missing `/var/data/flora/security/authority.sqlite3` remains a private
access blocker. A Supabase project does not restore missing CIOS permissions.

## Options and existing ownership

| Option | Assessment |
| --- | --- |
| A: finish bespoke passwords/account recovery | Existing Argon2, enrollment and sessions work in isolated tests, but add ongoing identity lifecycle work and do not solve missing operational authority. Retained only as explicit transitional local mode. |
| B: Supabase identity + existing CIOS authorisation | Recommended and implemented as an opt-in adapter. No second ACL engine, tenant inference, Supabase role grants, canonical owner or database. |
| C: another managed provider | Feasible at the same resolver seam, but adds another configuration and verification path with no demonstrated present benefit. |

Reviewed accepted ADR-001, ADR-003, ADR-010/011/012 and ADR-026 boundaries
and the existing Security Bootstrap/Verified Context contracts. No Source,
Evidence, Observation, Enterprise Model or Material Pressure ownership changes.
ADR-024 has a historical Draft header / Accepted body ambiguity; its existing
ownership boundary is preserved without editing or reaccepting it. Proposed
ADR-025/027 retain their existing status. This records the commissioned implementation
choice; it does not declare an accepted canonical ADR.

The accessible Elliott repository exposed a README-only tree. No Supabase
implementation was available to reuse; no credentials, tenant configuration or
private application code were copied. The adapter instead follows the official
[password sign-in](https://supabase.com/docs/reference/python/auth-signinwithpassword),
[getUser](https://supabase.com/docs/reference/python/auth-getuser),
[server guidance](https://supabase.com/docs/guides/auth/server-side/advanced-guide),
[sessions](https://supabase.com/docs/guides/auth/sessions) and
[sign-out](https://supabase.com/docs/reference/javascript/auth-signout) contracts,
reviewed 17 November 2026.

## Identity and authorisation sequence

1. Existing same-origin POST, bounded form and pre-authentication CSRF protect
   email/password submission. No signup, public bootstrap, auto-owner, OAuth,
   magic-link callback or caller-selected return URL is introduced.
2. Server sends credentials only to the configured separate HTTPS Supabase
   project's password endpoint using a publishable key. It discards refresh
   tokens; no password is stored in CIOS for this flow.
3. Server decodes claims solely for consistency and calls genuine `/auth/v1/user`
   to verify the token remotely. Exact issuer, audience, UUID subject/session,
   expiry, non-anonymous status and confirmed individual email are required.
   Decoded claims, email, metadata roles and deployment access never confer CIOS
   authority. Supabase's current user response is cross-checked against subject.
4. Existing SecurityStore requires an explicitly approved exact issuer/UUID to
   existing enabled CIOS principal binding. That principal's current memberships,
   capabilities, enterprise grants and independent resource ACL still decide
   access. Provider bindings live in this same operational owner, not a parallel
   user store; the helper cannot create a principal, membership or resource grant.
5. Browser receives only the existing opaque `__Host-flora_session` and CSRF
   cookies, Secure/HttpOnly/SameSite=Strict. CIOS retains this authorisation
   envelope for workspace selection, protected write serialisation and audit; it
   is not a second password identity service. The provider access token is Fernet
   authenticated-encrypted under an external key, bound to issuer, subject and
   opaque session digest. JWT session ID is inside the authenticated envelope.
6. Every protected transaction checks live provider identity and current CIOS
   authority. Only that locked transaction reuses a successful provider result;
   no cross-request positive cache exists. A context-local negative-only cache
   avoids repeatedly waiting for a failed provider within one public render.
7. Existing eight-hour absolute, thirty-minute idle and five-minute recent-auth
   controls remain, with absolute expiry further capped by provider JWT expiry.
   Workspace rotation reseals credentials and preserves original auth age and
   expiry. **No refresh engine:** sign in again at expiry (typically within an
   hour, depending on project settings). No silent renewal or renewed recency.
8. Local sign-out validates opaque bearer + CSRF and commits revocation first,
   even during provider outage/expiry. Provider sign-out is best effort with
   `scope=local`; it does not sign out unrelated devices. CIOS revocation is
   immediate. Remote getUser rejection denies access; actual FLORA-project
   revocation behaviour must be verified by the owner. Do not claim universal
   instantaneous provider-wide revocation: absent earlier rejection, JWT expiry
   is the conservative external bound. No JWT-only local signature acceptance.

Provider transport validates normal TLS, forbids redirects/arbitrary hosts and
service-role keys, caps JSON at 64KiB and uses a five-second timeout. Network and
provider error bodies never reach users or audit logs. Multiple protected checks
can add latency; current single-instance SQLite authorisation/writer serialisation
is preserved. Load-test actual provider latency before expanding pilot volume.

## Transition and retirement

`FLORA_AUTH_PROVIDER=local` (default) deliberately preserves the deployed local
mechanism until owner setup/review. `supabase` rejects old local-password sessions
and enrollment and **never falls back**, including during outage or bad settings.
Unknown mode denies authentication. Supabase sessions are also denied in local
mode. There is no session migration. Applying a binding revokes that principal's
old sessions. A deliberately authorised rollback to local mode must explicitly
revoke any still-valid historical local sessions for affected principals before
requiring fresh sign-in; merely changing an environment mode is not a global
session revocation operation.

After genuine provider, revocation, resource access and recovery proofs, a later
review can retire local Argon2 login, password-enrollment issuance and enrollment
UI. Do not delete historical principals, memberships, audit, protected journal,
resource ACL, workspace/session/CSRF or approved recovery tooling. They are CIOS
authorisation controls, not redundant provider password machinery.

No runtime store creation or schema migration. New bindings/encrypted envelopes
use namespaced entries in existing schema-v1 operational metadata. Bindings are
audited and explicit, forbid principal reassignment, active duplicate individual
bindings and replay of an inactive-to-active approval. Reactivation requires a
separate recovery review. Existing revocation, principal version, membership and
protected journal semantics remain authoritative.
