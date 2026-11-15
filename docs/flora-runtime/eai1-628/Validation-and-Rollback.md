# Validation and controlled rollback

The exact final SHA, local counts and hosted workflow URLs are recorded in the draft PR validation comment. This committed document defines reproducible checks, not a claim that a pending run passed. Baseline is validated main `8a53777d1dec359f56b66e533d512c0a86881939`, post-merge push run [43709888042](https://github.com/rdidale-jpg/CIOS/actions/runs/43709888042).

## Reproduce

Commit before full validation: the driver captures HEAD. Use the project dependencies, Python and repository root.

- `PYTHONPATH=. python tools/ci/flora_ci.py --output /tmp/eai1-EXACT-SHA-ci`: all 27 versioned suites including strict 388, inherited failures/skips, identity/source/security and repository-integrity checks.
- `python -m unittest discover -s tests/ci -q`: 39 gate-behaviour tests.
- Run the exact semantic pytest command in `.github/workflows/flora-isp1-semantics.yml`: 291 cases including 52 new EAI cases. All prior selectors remain.
- Run the existing product regression commands in `.github/workflows/flora-validation.yml`: 371 additional cases covering Technology, Offers/library/strategic offers, Buying Trigger Intelligence, seller development, visual/release and public navigation.
- `PYTHONPATH=. python tools/ci/flora_eai1_preview.py --output /tmp/eai1-browser --baseline-root /path/to/baseline-worktree`: baseline worktree must be exact main8a above. Requires Playwright, Chromium at `/usr/bin/chromium` and local TLS tooling. Isolated fixture storage/authentication only; no production settings or domain writes. Compare all 92 JPG hashes with committed previews.

Hosted full workflow remains byte-identical; the separate semantic workflow is extended, not substituted. Both must pass against the exact final candidate SHA. No source-admission implementation, accepted ADR, private owner, route, matcher, Pipeline service, strict-security test, comparator or inherited failure/skip baseline changes.

## Test adjustments, individually justified

| Assertion | Reason | Preserved negative/property |
| --- | --- | --- |
| Per-scope agenda count 2 → 3 | One permitted new item per scope | Exact ordered keys and source boundaries |
| Missing old FCA candidate leaves AI and funding-base | New funding issue is independent of that file | Service issue still omitted on missing/withdrawn/unreadable source |
| Service “deterioration” check reads counter-evidence rather than headline | Updated declarative statement focuses on received/closed/upheld; the no-deterioration caveat remains in reasoning | No FOS inference, no speed value, exact received/upheld values |
| Inventory 163 → 169 | Six specifically named new candidate/excerpt files | All 163 prior bytes retained; six literal digests; unknown/symlink/tamper rejection |
| Original 161-source ancestor comparison permits INT2 + EAI6 | Reflects exact additive inventory, not a baseline refresh | Original historical bytes and comparator are unchanged |

The first targeted run identified the stale headline assertion, corrected as above. No assertion or test was removed. No mass refresh or weakened comparator. The six new files are unaccepted public candidate inputs, validated in disposable copies by existing banking/macro owners; no shared assessment is rewritten.

## Browser and performance proof

[558 browser checks](previews/Browser-Checks.json), 92 before/after JPGs, three accessibility snapshots and [six cold-load observations](previews/Performance.json). Four principal sizes plus 320px, Retina DPR2, effective 200% zoom, forced colours, keyboard/touch, no-JS direct two-selection route, deep links, Back/Forward, subject/selection preservation and optional original-source activation. Source activation is intercepted locally, not a publisher availability check. No cross-workspace inspection; owner-only routes retain their guard.

Single-run loopback emulation at 1.6Mbps/150ms RTT: before/after artwork bytes remain 410,442 UK, 422,290 Banking, 410,602 Lloyds. FCP before 644/616/620ms, after 856/612/612ms; artwork durations before 2371/2433/2391ms, after 2372/2444/2380ms. FCP measures initial text/header, not full-image readiness. No production performance/SLA claim. Emulated Chromium is not physical iPad/Safari or screen-reader certification.

## Owner decision and rollback

GO is for owner review only after exact-head CI succeeds. Source/Evidence acceptance remains separate from code review. All eight owner choices are unselected; actual canonical target IDs, acceptance receipts and deployed SHA remain UNVERIFIED. Read-only production reconciliation requires an authorised owner service/session; no private probe or fixture identity substitutes for it. SEC/ONS remain blocked; ADR-027 is Proposed and inactive.

There is no migration, canonical import, Material Pressure promotion or Pipeline compensation. A code rollback can revert this EAI commit to main8a while retaining INT-1's six-type policy and owner-only inspection controls. Do not revert those earlier security controls. Revalidate the rollback commit before any separately authorised release.

A source withdrawal fails closed and omits dependent insights. A reviewed withdrawal commit must reconcile only the exact new candidate digests and agenda pins, keeping historical bytes, all unknown-file rejection and source revocation tests. Never delete or refresh the old evidence ledger/baseline to conceal a withdrawal or contradiction. Canonical acceptance/import, merging and Render deployment each require separate explicit owner review; none is performed here. No Render storage/auth/origin/backup configuration is altered or certified by this sprint.
