# Reproducible F3 validation

Baseline full post-merge CI 43881361135 passed at the exact F2 merge before branching. Final exact SHA and hosted links are recorded in the PR validation comment rather than embedded self-referentially in committed proof output.

```sh
python tools/research/f3_quality.py
python -m pytest tests/test_flora_f3_646.py tests/test_flora_f2_644.py tests/test_flora_f1_642.py -q
python -m pytest tests/ci -q
python tools/ci/flora_ci.py --output /tmp/f3-exact-ci
git worktree add --detach /tmp/f3-before 45f7e32676769a5829d8a9399c0b8c4f3ddb7b0b
python tools/research/f3_proof.py --output /tmp/f3-proof --preview --baseline-root /tmp/f3-before
python tools/ci/flora_vp2_preview.py --output /tmp/f3-visual-regression
```

Use fresh output directories. All runtime stores/authentication are isolated synthetic nonproduction authority. Genuine source data in the application proof is only the unchanged permitted BoE pilot. The F3 admission audit separately reports32 typed review measurements, five offline reconciliations and zero issuer permissions/runs/visibility. No real issuer success is substituted by a synthetic fixture.

Targeted tests cover series scope and uses/audiences, terms/review/version/lifecycle exceptions, cumulative extraction caps, no approved/caller-authorised status, unsafe/encoded URL aliases, actual unchanged origin policy, denied issuer creation with unchanged storage, explicit signed roles and same basis, separate reported endpoint, duplicate/subtotal/residual rejection, currency/entity/perimeter/source/date/state guards, full annual and leap-year boundaries, weaker assumption propagation, acquisition/361-day rejection and exact F1 payload identity. Synthetic annual measurements pass actual guarded Financial persistence/reload; removing their test-only input adapter immediately removes projection while preserving history.

Full local and hosted acceptance gates include the existing 27-suite/1,432-case comparator, strict 388 security,682 semantic/FIG/compatibility cases,371 product checks and39 CI controls. The 36 inherited failures and ten skips must match their exact existing signatures/reasons. Neither comparator nor baseline changes. No historical assertion refresh or test removal is part of F3.

The actual loopback Financial browser walkthrough has 132 assertions, with before/after F2 Main in desktop/iPad/mobile, keyboard/touch, 200% text, forced colours, no-JS, history, exact values, foreign workspace and source withdrawal/rights/stale/revision denials. Existing VP-2/EAI-2/BIE-2/BIE-3 and F1 browser workflows remain enabled. New F3 workflow checks out the exact PR head, runs targeted contracts/research QA and reuses the same isolated proof/browser tools. Before comparison parameters are backward-compatible; F2 defaults still compare against its original F1 cut.

Only sanitized JSON, screenshots, ARIA and performance findings are uploaded. Raw logs, ephemeral authentication database/configuration, cookies, synthetic passwords and runtime stores are excluded. Browser navigation can cancel image requests and produce existing loopback socket-disconnect diagnostics; those logs are not evidence of source/security acceptance and are not committed. Tests require actual successful HTTP, image decode, layout and denial assertions.

The committed preservation manifest checks all 175 historical research files and 51 visual assets against validated F2. Source policy/registry/contracts, source import, route guards, UI shell, approved/proposed ADRs, eight owner proposals and core Financial admitted-source/persistence/projection functions remain exact. No canonical/production write, source import, new permission, external paid call, merge or deployment is performed.
