# Validation and controlled rollback

The final tested SHA and **exact-head hosted/local results** are published in this draft PR’s validation comment, with workflow URLs and sanitized summaries. This document is the reproducible check/acceptance contract; opening a draft PR or a green unrelated SHA is not release evidence.

## Checks

- `PYTHONPATH=. python -m pytest tests/test_flora_controlled_integration_625.py tests/test_flora_intelligence_presentation_623.py tests/test_flora_visual_streams_612.py tests/test_flora_visual_v2_583.py tests/test_flora_research_intelligence.py tests/test_flora_design_system_585.py tests/test_flora_primary_enrichment.py -q`
- `PYTHONPATH=. python tools/ci/flora_ci.py --output /tmp/int1-EXACT-SHA-ci` — all27 versioned suites, strict388; original baseline, comparator, test IDs and skips unchanged. Commit before starting this command because it captures HEAD.
- `python -m unittest discover -s tests/ci -q` — gate failure behaviour; hosted full validation also runs the existing Technology/Offers/library/strategic-Offers/BTI/seller-development/visual/release regressions.
- `PYTHONPATH=. python tools/ci/flora_int1_preview.py --output /tmp/int1-browser-proof --baseline-root /workspace/cios-isp1-before` — isolated app/storage; baseline worktree must be exactfe66516…, no production configuration. Requires Playwright/Chromium, local TLS tooling and project test dependencies. No credentials or private fixture files are published.

The dedicated exact-head workflow extends the reviewed ISP semantic gate to source-admission and agenda tests. Full existing `flora-validation.yml` remains byte-identical. All388 original security tests and their services remain unchanged. The sole ISP security code delta adds the existing owner read check for finite inspection routes; original byte-compatibility records and per-case fixture rationale are retained under `isp1-623`.

Tests cover claim/source/entity/date/status/rights pin changes; denied/withdrawn/missing/unreadable candidate omission; no new SEC/ONS publisher exceptions; actual versus expectation; transitive uncertainty and incompatible calculations; correct legal/segment/Group boundaries; no H1 financial proxy; on-demand traceability; owner-only inspection and revoked membership; invalid/foreign/duplicate selectors; no hidden HTML/ARIA/admin or seller question; no private owner/matcher/Offer/Pipeline reads/writes; unchanged seven original artworks,21 variants, geometry, original overlay and protected owners.

## Browser findings

Committed proof: [Browser-Checks.json](previews/Browser-Checks.json), [Performance.json](previews/Performance.json), three scope accessibility snapshots and76 before/after JPGs. **482 checks passed**, four screenshot sizes plus320px, iPad DPR2,720px effective zoom, forced colours, keyboard/touch, no-JS two-selection journey, history, deep links, source activation and selected context. A browser harness navigation race was corrected by awaiting native navigation; it was not an application data/control exception.

Cold emulation,1.6Mbps/150ms RTT,DPR1, one run per scope: before/after art bytes unchanged410,442 UK /422,290 Banking /410,602 Lloyds. FCP before572/560/576ms, after644/596/604ms; art request durations before2350/2434/2368ms, after2378/2427/2375ms. FCP includes header/text and is **not** full-art readiness. No performance SLA or production speed claim; original responsive cache/asset policy is retained.

## Compatibility finding and correction

An exploratory attempt to append the numerical candidate to the shared assessment exposed its historical understanding-review cutoff binding. That approach was removed. The final assessment/art manifest/metadata are unchanged; the one proposed record is validated in memory only for the agenda. No understanding review, historical failure signature, source baseline or old source count was refreshed. The source count inside existing owner inspection therefore still describes its original assessment; INT-1 does not pretend that all RIC sources have been imported.

Reviewed ISP inspection fixture revisions are justified individually in [Inspection-Fixture-Reconciliation.md](../isp1-623/Inspection-Fixture-Reconciliation.md). They retain original test IDs, content/negative assertions and CSRF forms, using real verified-owner fixtures for newly restricted positive reads; anonymous denial is tested separately. No strict security file or approved inherited failure/skip list is changed.

## Release and rollback

**GO is limited to owner review when final exact-head CI is green. Merge/deployment remain unauthorised.** Production acceptance receipts are unverified. Physical-device acceptance, source-admission review and explicit release authorisation remain required. No production backup/storage/auth/origin or Render configuration has been altered or newly certified by this sprint.

There is no data migration, canonical import, material-pressure mutation, Pipeline write, feature flag or production compensation to undo. A content withdrawal can remove/revoke the single proposed FCA record in a reviewed commit; its fingerprint check omits the dependent issue and retains the other agenda. A presentation rollback removes the optional agenda composition/selector/markup and restores the prior reviewed ISP renderer while keeping its owner-only inspection check and six-type policy. Re-run exact-head source/security/regression checks on that rollback candidate before owner-controlled release.

A blind revert of the whole integration to pre-ISP main would restore the former anonymous research-inspection surface. Preserve the owner-only read restriction in any release rollback; a full baseline revert requires a separate security review. Repository commits are not a substitute for canonical-data compensation or an owner-approved production backup/rollback procedure, neither of which is exercised here.
