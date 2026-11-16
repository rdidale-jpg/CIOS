# Reproducible validation

Run in an isolated nonproduction checkout. Requirements are unchanged. Commands below write temporary test state, never production/canonical records.

```sh
python -m pytest tests/test_flora_f2_644.py tests/test_flora_f1_642.py -q
python tools/ci/flora_ci.py --output /tmp/f2-exact-ci
python -m pytest tests/ci -q
git worktree add --detach /tmp/f2-before 98fcab91aa94180b11c41c60f4cf7e4d4ad39e40
python tools/research/f2_proof.py --output /tmp/f2-proof --preview --baseline-root /tmp/f2-before
python tools/ci/flora_vp2_preview.py --output /tmp/f2-visual-regression
```

Use a fresh output path for `flora_ci.py`. `Proof.json` records the exact checkout SHA, actual stored/reloaded inputs, reproduced results and withdrawal proof. Browser artifacts include assertions, responsive screenshots and an ARIA snapshot; no synthetic passwords/session stores, private authority database, raw server logs or browser configuration are uploaded. Hosted F2 workflow uses the exact PR head, read-only contents permission and pinned Playwright 1.62.1. Existing full regression, semantic, F1, FIG-1 and Banking/VP-2 workflows remain enabled.

F2/F1 focused suite: **151 cases**. F2 browser: **132 assertions**, desktop 1440/1280, iPad landscape/portrait, mobile 390/320, 200% text, keyboard, touch, forced colours, no-JS, browser history, source withdrawal/rights/stale/revision and foreign workspace denial. Existing VP-2 browser: **709 assertions**, including all seven streams, assets, labels and active destinations. Emulated Chromium is not physical Safari or screen-reader certification.

Full 27-suite CI, strict 388 security, 682 semantic/compatibility cases, 371 product cases and 39 CI controls are rerun at the final committed head. Exact-head results/links supersede development runs and are recorded in the draft PR's final validation comment. The immutable failure comparator must report no unexplained change: approved 36 inherited failures and ten skips remain individually matched; no baseline refresh, relaxed comparison or removed test is permitted.

## Individually reconciled historical owner assertions

These are passing byte-preservation tests whose former whole-file assertions conflict with two specifically commissioned dispatch additions. They are separate from the approved inherited-failure baseline, which is unchanged.

| Case | Original assertion / observed difference | Bounded correction |
|---|---|---|
| `test_flora_bie2_635::test_protected_owners_forms_and_proposed_adr_unchanged` | Protected owner file equals historical cut; security dispatcher and visual dispatcher gained private F2 guards | Preserve original Git bytes/hash; permit only the exact two AST additions |
| `test_flora_bie3_637::test_historical_bie2_pack_owners_and_unexecuted_decisions_unchanged` | Same immutable historical owner check | Same narrow exact-guard contract; source packs, proposals and ADR remain byte-exact |
| `test_flora_evidence_expansion_628::test_protected_owners_policy_and_all_existing_dependency_pins_are_unchanged` | Original owner cuts/hash pins | Preserve all historical hashes/cuts, check exact F2 guard only |
| `test_flora_visual_v2_583::test_runtime_source_preserves_canonical_home_and_domain_owners` | `security_web.py` SHA256 equals reviewed ISP-1 digest | Verify old F1 bytes still match that digest, then exact private guard compatibility |
| `test_flora_design_system_585::test_protected_intelligence_security_permissions_matching_and_pipeline_bytes` | Same security owner digest | Same narrow compatibility; all other protected files still byte-identical |

`tests/flora_f2_owner_contract.py` accepts only `security_web.private_read`'s exact Banking/Lloyds authorisation dispatch immediately after the existing parsed path, and `visual_streams.render`'s exact private selector dispatch immediately after the existing panels import. It removes only those exact AST nodes and compares the entire remaining module with the verified F1 bytes. Changed imports, decorators, prior statements, path set, order or guard placement fail. Six negative mutation cases exercise these protections. No arbitrary new candidate hash, ignored owner file, source policy exception or inherited failure signature is blessed.

## Lifecycle and mathematical negatives

Tests exercise actual verified authority, capability removal, revoked memberships, forged headers, foreign workspace/resource, missing ACL/principal, absent runs, malformed/duplicate selectors, country/scope mismatch, unknown formula, forged cache/payload/input revision, source withdrawal/retraction/rights/private/stale/contradiction/version/value changes, and immutable run history. Pure finite tests cover signed amounts, zero/negative/tiny chart axes, exact periods, entity/perimeter, basis/state/unit/currency, assumed dependency propagation, bridge residual/duplicate/revision/source rejection and conflicting stock definitions. Unsupported nonmonetary units are refused rather than relabelled.

The loopback server can report cancelled-image socket disconnects when browser history/navigation aborts downloads. Those are not permission/storage failures; successful HTTP, completed image decodes, layout and source-denial assertions are independently checked. Raw logs remain outside committed artifacts.
