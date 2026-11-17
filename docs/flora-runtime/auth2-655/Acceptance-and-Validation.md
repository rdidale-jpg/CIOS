# Owner review and reproducible validation

Implementation is suitable for code/visual review only. Genuine Supabase identity,
live approved workspace binding and missing production CIOS authorisation storage
are not proven by test doubles. No merge/deployment/production action authorised
by this report. Final exact-head results are recorded in the PR validation comment
and hosted artifacts, which avoid committing a self-referential SHA.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_flora_auth2_655.py tests/test_flora_auth1_652.py tests/test_flora_uxr1_650.py -q
python tools/research/auth2_compatibility.py
python tools/ci/flora_ci.py --output /tmp/flora-auth2-full
git worktree add --detach /tmp/flora-auth2-before 7b056b21cd5d824bc4359b4e1ed49a1673a7f5fc
python tools/research/auth2_proof.py --output /tmp/flora-auth2-proof --baseline-root /tmp/flora-auth2-before
```

The proof needs Chromium and Playwright1.62.1 (`NODE_PATH` points at its isolated
installation); the hosted workflow installs both. Only disposable synthetic
accounts/provider state, actual CIOS services and existing permitted source facts
are used. No genuine Supabase or production credentials are available. No paid
service call is made. Hosted jobs check out the exact PR head, not a merge ref.

Existing 388 strict security identities, 27 regression suite identities and the
36 inherited failures / 10 skips remain unchanged. The comparator and approved
baseline files are byte-identical. Separate tests cover provider transport and
claims, explicit binding, email/role non-authority, disabled principals, expired
and idle sessions, key/envelope tampering, provider outage/revocation response,
workspace/ACL isolation, source withdrawal and anonymous public views.

## Individually reconciled assertions, not baseline refreshes

| Prior expectation | AUTH-2 correction and preserved control |
| --- | --- |
| Guest Nationwide lacked earnings | Exact same finite Source facts now public; no private run identity/action/lookup. |
| Wrong workspace/resource/revoked member lacked those earnings | Public Source facts remain; direct private run service and URL still deny. |
| Owner-only/private or withdrawn Source | Both public financial projection and private derivatives still disappear. |
| AUTH-1 / UX-R1 browser price absence used as a privacy proxy | Replace price-absence with private run identity absence plus retained direct403 checks. No test or security boundary removed. |
| Historical byte-pinned SecurityStore, web and presentation owners | Four individually SHA256-pinned AUTH-2 owner changes plus exact unlisted-function AST equality; original historical manifests and assertions retained through the immediate AUTH-1 predecessor. Unknown before/after mutations still fail. |

The four allowed owner evolutions are enumerated in `Owner-Evolution.json`; no
changed inherited failure or skip is approved. Source files, source permissions,
canonical owners, Offers, Pipeline, `security.py`, `access.py`, protected storage,
runtime Render configuration and original artwork remain unchanged.

## Owner walkthrough

1. Compare `previews/before-guest-nationwide-*` and
   `previews/after-guest-nationwide-*`: Group income, underlying/statutory profit,
   member-value reconciliation and distinctly scoped Society service outcomes.
   Public facts do not require preparing a private run.
2. Inspect the warm ivory/forest sign-in and workspace screens; private action
   sign-in is distinct from public exploration. Verify labels, focus and touch.
3. In the isolated proof, authenticated mapped individual selects only an existing
   workspace and can access a Financial run only with its original ACL.
4. Revoke membership or lose the provider: private run403, public facts remain.
   Withdraw the Source: both public and private dependent financial results vanish.
5. Missing authority: simple sign-in-unavailable message; public intelligence
   still readable; no replacement database/account is created.

## Acceptance checklist

- [ ] Accept public product scope and the finite Nationwide factual-use rationale;
      no new issuer licence/source permission or private-run publication implied.
- [ ] Accept managed identity + existing CIOS authorisation, access-token-only
      pilot and sign-in-again expiry tradeoff.
- [ ] Review exact-head local/hosted388-security and unchanged regression signatures,
      focused tests, independent findings and responsive screenshots.
- [ ] Confirm original51 visual files, source/research history and private controls.
- [ ] Independently recover/verify missing CIOS authorisation, resource grants and
      backups; do not create an empty replacement authority.
- [ ] Create separate FLORA provider project and reviewed explicit binding.
- [ ] In non-production, prove genuine provider sign-in, logout/revocation,
      workspace/resource access, recovery and latency with actual configuration.
- [ ] Review remaining limitations: no in-app invitations/recovery/OAuth/MFA,
      no refresh, standard hosted project/new publishable-key format only,
      single operational authority instance, emulated browser/device coverage.
- [ ] Explicitly authorise any later merge/deployment separately.
