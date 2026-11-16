# Validation and compatibility review

The final PR validation comment gives the exact candidate SHA, local results and hosted run links. Screenshots committed here come from actual baseline/candidate application renders; the hosted UX-R1 proof regenerates them from the exact PR head. Tests passing alone do not establish owner visual acceptance.

## Reproducible commands

Use repository requirements, Python3.12 and Playwright1.62.1 with Chromium. All browser fixtures run in temporary directories and use isolated synthetic identities with the actual session, workspace, ACL, CSRF/Origin and Financial services. Do not use production accounts or storage.

```sh
python -m pytest tests/test_flora_uxr1_650.py tests/test_flora_rud1_648.py tests/test_flora_f3_646.py tests/test_flora_f2_644.py tests/test_flora_f1_642.py -q
python tools/research/uxr1_quality.py
python tools/ci/flora_ci.py --output /tmp/uxr1-exact-ci

git worktree add --detach /tmp/uxr1-before 93e83d34ee2661ebe17cbc06b047350f6c32e3c3
python tools/research/uxr1_proof.py --output /tmp/uxr1-proof --preview --baseline-root /tmp/uxr1-before
```

The existing FLORA validation, semantic, VP-2, EAI-2, BIE-2/3, FIG-1, F1/F2/F3 and RUD-1 workflows remain enabled. Their existing product/security/source tests run alongside the new UX-R1 workflow. Original comparator implementation and versioned failure/skip baseline are byte-identical; no baseline-writing mode is introduced.

## What the new proof establishes

- 43 service/markup/access cases: all seven scene families, financial amount/date/basis/scale/weak-input meaning, material force caveats, no source markup, verified reads and negative source/authority cases. These are direct Python calls, not HTTP certification.
- 367 browser checks: actual Guest and authenticated owners across desktop1440/1280, iPad1194×834/834×1194 and mobile390/320; before/after Landscape, Forces, Nationwide and private Financial Main. Real GET/HEAD/POST enforcement, persisted actual facts, Owner before-run prepare, inspect-only, foreign/no-resource, withdrawal, no-JS and200% text.
- Actual PDFs are parsed for source-document links and prohibited research labels. No current-source run is created by GET; secure preparation reproduces the same immutable stored bytes. Withdrawal removes the projection/direct selector while retaining history.
- Source/rights, Financial ownership and art are independently checked by `uxr1_quality.py`, including rejection of unknown prior owner digests. Current source/financial historical quality is reused rather than duplicated.

## Reviewed contract changes

Earlier successful UI assertions expected precisely the source click trees this commission removes. They were reconciled individually by purpose; tests were not deleted and failures/skips were not refreshed.

| Contract | Reconciliation |
|---|---|
| EAI-2, BIE-2/3, INT-1 and VEX-1 source/agenda/chart composition assertions | Retain exact assertion content against `tests.flora_editorial_contract.research_render`, a **pure internal Research composition** helper. It grants no session or private-run authority and is not an HTTP route. Ordinary rendering has separate zero-source/negative tests and browser proof. |
| F2 chart scale/zero and original source retention | Numeric/period/private-ACL assertions remain in ordinary Main. Full chart/table/source interactions move to authenticated `lens=inspection`, which requires existing Owner and private-run authority. |
| RUD-1 rich source-use exposition | Retained on existing authorised Financial inspection; ordinary tests require absence of disclosures and direct selected-company financials. Real Financial persistence, calculations, source withdrawal and independent-source availability remain tested. |
| EAI expiry | Still omits every dependent EAI key and its numbers. Does not mistake independently eligible RUD enterprise navigation for a revived expired EAI release. |
| Prior exact-byte UI owner assertions | Seven explicitly listed presentation/dispatch owners have reviewed current hashes and enumerated historic hashes in `Owner-Evolution.json`. Unknown prior/current changes still fail. No source/security/calculation/Financial store/ADR owner exemption. |
| Legacy browser source/index controls | Assert the new source-free ordinary layout. Retain amounts, reporting boundaries, legal entities, routes, permissions, original scenes and negative source cases. Real Financial inspection still receives keyboard/touch/source/chart checks. CSS `gap:` is not treated as a research-gap record. |

## Interpreting disclosure metrics

[Disclosure-Metrics.json](Disclosure-Metrics.json) records actual per-role/device Main height, words, all source anchors and source controls in markup, and controls/anchors visible through closed native-details ancestors. The baseline has closed source links in markup and visible source summary controls: do not describe all retained links as initially visible. New ordinary Main has neither source-document anchors nor source controls in markup. Required separated legal attribution is counted separately.

The new Guest Nationwide page has more meaningful context than its old service-only sentence, and authorised selection adds financial content that was previously elsewhere. Forces keeps important caveats, so “simpler” does not mean every page is shorter in pixels. Compare reading hierarchy, interaction depth, print length and usefulness as well as counts.

## Evidence handling

Workflow artifacts allow only sanitized result JSON, screenshots/PDFs, accessibility snapshots and existing sanitized CI evidence. No credentials, browser configuration, authority database, cookies, production records or raw tool logs are uploaded. The actual-source proof contains retained publicly researched factual records and explicitly synthetic workspace metadata; it is not canonical acceptance or a source-byte archive.
