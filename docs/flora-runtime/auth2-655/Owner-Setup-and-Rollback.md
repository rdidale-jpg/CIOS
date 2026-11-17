# Owner setup — instructions only, not executed

**Private production readiness: NO-GO pending actual setup and proof.** There is
no configured/verified FLORA Supabase tenant or approved live provider binding in
this session. Owner reports the Render persistent disk exists but the CIOS
security directory/database were absent on 17 November 2026. Do not create an
empty replacement authority database, bootstrap an owner or reset credentials.
Supabase does not supply CIOS permissions, resource ownership or lost audit data.

## 1. Establish existing CIOS authority first

Use AUTH-1's read-only diagnosis and independently verified backups/ownership
records. Confirm the correct persistent mount, service user, private 0700 security
directory / 0600 database, schema, protected journal, ACL and audit history. Do not
run `initialize`, `enroll`, public bootstrap, ad hoc SQLite CREATE/INSERT or a
chmod/chown guess against production. If authority cannot be recovered, stop
private activation for an explicit approved authorisation-recovery decision. This
PR's binding tool requires an **already existing enabled principal** and gives it
no new memberships/roles/resources.

With Supabase mode selected, the read-only diagnostic marks local passwords not
applicable and still reports provider binding/login UNKNOWN; metadata counts are
not authentication proof. CIOS principal/membership/storage checks remain.

Back up the verified authority, resource ACL and protected working records with
the existing consistent/quiesced backup process. Keep the encryption key outside
database backups with appropriately restricted recovery access. Test restore on a
separate non-production copy. Leave Render branch/main, Auto-Deploy OFF and disk
configuration unchanged during this review.

## 2. Create a separate FLORA Supabase project

Owner creates a separate project using the suitable free/pilot offering; no paid
services are commissioned here. Do not reuse Elliott's project, users or keys.
Enable email/password, require confirmed email, disable anonymous sign-ins and
open signup. Configure provider password policy to preserve at least the existing
15-character enrollment minimum (and the provider's stronger available checks);
verify it before pilot activation rather than relying on project defaults.
Create the intended individual through Supabase's supported private
dashboard workflow with a secure confirmed account/password. No automatic Owner
account is created by FLORA. Email establishes individual sign-in, never CIOS
privilege. Record the exact Auth user UUID independently.

Site URL: `https://flora-current.onrender.com`. No wildcard redirect allowlist.
This pilot implements server password sign-in, not OAuth/PKCE callbacks, magic
links, public enrollment, invitation completion, MFA or in-app password recovery.
Do not configure recovery/invitation redirects to an unsupported FLORA route.
Account lifecycle/recovery must be handled by the provider's supported controlled
operator process until an explicitly reviewed application flow exists.

Use the project HTTPS URL and **new-format publishable key**, never a service-role,
secret API, database password or JWT signing key. This version supports standard
`https://<20-character-project-ref>.supabase.co` domains only. Custom domains and
legacy anon JWT key formats intentionally fail closed. Keep reasonable short JWT
expiry (normally up to one hour); users sign in again at expiry. No refresh tokens
are retained or refreshed by FLORA.

## 3. Prepare configuration privately

After review, an authorised operator sets these in the target service's protected
configuration; **this sprint does not change them**:

| Name | Value |
| --- | --- |
| `FLORA_AUTH_PROVIDER` | `supabase` |
| `FLORA_SUPABASE_URL` | Separate FLORA project's exact HTTPS URL, no trailing slash |
| `FLORA_SUPABASE_PUBLISHABLE_KEY` | Its `sb_publishable_...` key |
| `FLORA_SUPABASE_SESSION_KEY` | Separately generated Fernet key, confidential |
| `FLORA_PUBLIC_ORIGIN` | `https://flora-current.onrender.com`, exact, no trailing slash |
| `FLORA_DATA_DIR` | Existing verified `/var/data/flora` persistent root |

Generate the session key on an authorised secure machine directly into a new
0600 operator file (never commit, paste into chat, argv or job logs):

```python
import os
from cryptography.fernet import Fernet
fd = os.open('flora-session-key.private', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'wb') as out:
    out.write(Fernet.generate_key() + b'\n')
```

Store that key in the service secret configuration using its secure UI. Losing or
rotating it invalidates existing Supabase-backed CIOS sessions; it does not
recreate accounts, change roles or reset protected records. No tokens in browser
localStorage, URLs, committed files, previews or public diagnostics. Ensure
authentication responses/cookies are not cached by a proxy/CDN.

## 4. Bind the verified individual, without granting authority

On the approved operational copy/service, prepare a private JSON proposal:

```json
{
  "issuer": "https://<project-ref>.supabase.co/auth/v1",
  "subject": "<exact-confirmed-Supabase-UUID>",
  "user_id": "<independently-verified-existing-CIOS-principal>",
  "operator": "<accountable-operator-reference>",
  "approval_reference": "<explicit-independent-identity-binding-approval>",
  "active": true
}
```

Review exact issuer, UUID and existing individual identity independently of email
or deployment access. Check that person's existing selected workspace and resource
grants; this tool cannot add them. Compute SHA256 of `security_store.canonical`
JSON and review/confirm that exact non-secret digest. Only then run:

```bash
python -m cios.applications.flora.supabase_identity \
  --store /var/data/flora/security/authority.sqlite3 \
  --proposal /secure/operator/approved-binding.json \
  --confirm <reviewed-canonical-proposal-sha256>
```

The tool refuses absent stores/principals, mismatched project, reassignment,
duplicate active provider individuals for one CIOS principal and replay of a
deactivated binding. It audits the approved binding and revokes that principal's
old sessions. `active:false` is a reviewed deactivation; reactivation requires a
separate recovery review. No principal/workspace/role/resource grant is created.

## 5. Owner acceptance in a separate test environment

Before any separately authorised production activation, prove genuine configured
Supabase sign-in → only authorised workspace choices → permitted private Financial
run. Verify logout, expired token, provider/user/session revocation, membership
revocation, wrong workspace and denied ACL; inspect actual expiry and provider
latency. Prove public Nationwide remains readable during identity/store outage and
that a private `analysis=` URL is 403 to Guest. Check owner Research provenance,
Offers and Pipeline with their existing controls. Record exact code SHA, provider
project identity and non-sensitive test outcomes; publish no credentials.

The repository browser proofs use a **labelled isolated provider double**, actual
CIOS services and existing permitted facts. They do not prove live Supabase or
Render sign-in. Do not mark the incident resolved until real sign-in, workspace
selection and resource access have been observed by the owner.

## Rollback

No production migration or application data rewrite is required. After separate
approval, roll back application code to the validated AUTH-1 baseline using the
owner-controlled exact-SHA process. Do not replace/delete authority or working
records. Supabase sessions are unusable in local mode and need fresh sign-in.
Use the existing approved offline per-principal revocation operation to retire
still-valid historical local sessions before local rollback; switching modes alone
does not revoke every principal's old local session. Only deliberately choose
`FLORA_AUTH_PROVIDER=local` if the original verified
local account/password authority is present and approved; outage never causes
automatic fallback. Otherwise retain public access with private access denied.
Retain audit/binding history, backups and original research. No Render action is
performed by this PR.
