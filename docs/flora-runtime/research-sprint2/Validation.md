# Validation and acceptance boundary

Focused new suite: **60 passed**. Combined new suite + all 76 foundation tests + 15 unified integration tests: **151 passed**. CI-policy/comparator suite: **25 passed**, including deliberate false-acceptance-of-failures and unexpected-skip rejection cases. Targeted actionlint, Python compilation and diff checks passed. The held-out evaluation is separate research evidence: 35 controlled cases, 0/30 false acceptances, 0/5 false rejections, 11/35 unresolved. It is not an empirical semantic accuracy result.

Actual base evidence is [recorded by test identity](Actual-Base-Evidence.json): #568 head b4a2c2c680d21bc252f3bc7e365c7eb08af178d3, verified successful hosted run 43209875649 and downloaded artifact digest. Its tested merge tree exactly matches that head. Base result: 1,378 passed, 57 inherited failures and 10 original skips, 1,445 unique identities. No historical totals are assumed. The candidate baseline adds only 60 passing identities; every previous suite, failure fingerprint, skip reason and security selection remains structurally identical. Candidate full local and actual hosted conclusions must be read from the draft PR's completed checks and final validation comment.

Original source bytes and all 15 original candidate identities remain intact. The exact source guard extends 165→167 for two pinned additions; no directory-wide exception is introduced. The existing exact-count test is explicitly updated while retaining byte-for-byte checks. CI changes only add the exact stacked PR base branch trigger, leaving permissions, commands, artifact scope and inherited-failure policy unchanged.

[Browser results](previews/Browser-Results.json): actual Chromium at 1440×1050, 1024×1366 and 390×844; existing programme entry → research view → Oxford Ionics profile → Banking/Aviation journeys → seven source cards. Desktop keyboard SVG activation, no observed horizontal overflow or JavaScript exceptions. Full-page actual screenshots include before/after context. These checks establish rendering and navigation, not human comprehension or owner acceptance. The diagrams show research coverage rather than verified organisational dependencies.

[Correction proof](Correction-Proof.json): clearly synthetic fixture, seven affected claim/semantic-receipt/index/relationship/hypothesis/visual objects invalidated; next release excludes the claim; prior release preserved. No real source or production record is withdrawn.

Reproduce focused checks:

```sh
python -m pytest tests/test_flora_technology_semantic_sprint2.py -q
python -m unittest discover -s tests/ci -q
python tools/ci/flora_ci.py --output /tmp/flora-sprint2-ci-UNUSED
python tools/research/validate_flora_sprint2_ui.py \
  --base-url https://localhost:8876 --baseline-url https://localhost:8875 \
  --output /tmp/flora-sprint2-browser-UNUSED
```

The browser command requires separately started isolated local HTTPS services, Playwright and Chromium. It cannot seed data, provision accounts, start infrastructure or contact production.

Unmet acceptance requirements are material and explicit: no independent general semantic verifier/model endpoint, no independent real-source ground-truth corpus, original population identity/UK significance unresolved, current enterprise rights and complete per-segment baselines missing, and the new-family autonomous programme adapter not integrated. These remain blockers to claiming full Sprint 2 acceptance. CI success cannot waive them. No merge, production deployment, paid-service commitment or unattended monitoring occurs.
