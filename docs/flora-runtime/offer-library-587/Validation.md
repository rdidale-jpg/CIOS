# Sprint A validation contract

Base `3b8bd2c5e5177c012826658f820eeeb4ea2705f5`; exact candidate SHA and hosted run are reported in the draft PR and its current-head checks. The hosted validation checkout explicitly pins the PR head SHA (or the triggering SHA for push/dispatch), so the tested checkout is the candidate itself rather than a synthetic merge ref. Repository evidence describes the tested scope; it does not claim future CI success. No raw logs, runtime stores, credentials or real private research are committed.

## Required gates

- `python -m unittest discover -s tests/ci -v`: 39 CI-policy tests, including fail-closed comparator behaviour.
- `python tools/ci/flora_ci.py --output /tmp/flora-587-ci`: complete approved 1,432-identity selection. All **388 strict security cases must pass**, with no approved-failure signature or skip changes. Current approved baseline totals: 1,386 passing, 36 inherited failures, 10 skips. The baseline JSON and comparator are unchanged.
- Existing explicit hosted gates: Technology owner journey, UX #573, integration #578, original Offers, visual experience #583, design system #585, terminology #586, navigation/accessibility.
- Added explicit hosted gate: `python -m pytest tests/test_flora_offer_library_587.py -q`. Coverage includes all 24 methods, distinct IDs, source labels, private preference compatibility, multi-category dedup, atomic adoption rollback/audit, confirmation/CAS, foreign-employer rejection, independent proof/review, variations/rejection/retirement, stale/withdrawn/content-changed source handling, same-engine distinct matching, no Pipeline writes, real HTTP CSRF/escaping and unchanged authority-function ASTs.

The historical #585 immutable-owner evidence stays intact. The #583/#585 presentation-only tests permit exactly two owner-authorised functional revisions pinned separately by old/new hashes and unchanged control ASTs; all other protected files remain byte-exact. No baseline refresh, test removal, skip changes, security-selection change or comparator weakening.

## Reproduce previews

Install existing requirements and Playwright/Chromium in a disposable development environment. No new runtime dependency is introduced.

```sh
git worktree add --detach /tmp/flora-587-before 3b8bd2c5e5177c012826658f820eeeb4ea2705f5
PYTHONPATH=. python tools/ci/flora_offer_library_preview.py --baseline-root /tmp/flora-587-before --output /tmp/flora-587-previews
```

The helper starts isolated loopback HTTPS fixtures for before/after, narrows example memberships before enrollment, seeds explicit example portfolios and uses existing sign-in/CSRF controls. Browser checks run with JavaScript disabled at 1440×1000, 1194×834, 834×1194, 390×844 and 320×780. Public research and approved images are not modified. Seeding is local-only; cleanup destroys the temporary authority and commercial stores. Optional source snapshots retain vendor-category and seller-proof boundaries.

Review [browser-checks.json](previews/browser-checks.json), [gallery](README.md) and exact-head hosted status together. Physical iPad/Safari, screen readers, high zoom, real employer setup/proof and human time-to-portfolio remain manual acceptance. This sprint prepares a draft, not a production deployment approval.
