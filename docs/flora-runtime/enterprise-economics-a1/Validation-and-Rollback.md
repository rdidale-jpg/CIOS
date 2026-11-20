# Validation and rollback

## Reproduction

Run from the implementation checkout with the repository requirements installed:

```sh
python -m pytest tests/test_flora_enterprise_economics_a1.py tests/test_flora_experience_684.py tests/test_flora_public_financial.py tests/test_flora_et_integrate_672.py tests/test_flora_f1_642.py tests/test_flora_f2_644.py tests/test_flora_f3_646.py tests/test_flora_rud1_648.py tests/test_flora_auth2_655.py tests/test_flora_visual_panels_632.py -q
python -m pytest tests/test_flora_security*.py -q
python tools/ci/flora_ci.py --output /tmp/flora-a1-full-ci
python tools/research/enterprise_economics_quality.py > /tmp/flora-a1-quality.json
python tools/research/enterprise_economics_preview.py --output /tmp/flora-a1-browser
```

Browser tooling uses Node Playwright 1.62.1 with Chromium. The dedicated workflow installs those dependencies and checks out the **PR head SHA**, not a synthetic merge. The existing full FLORA security/regression gate still runs its unchanged versioned comparator and baseline. Head-specific Actions artifacts are the final validation authority; initial captures can precede the final commit and separately record runtime hashes. Source mutation, identity and legal-resolution fixtures are isolated test doubles, never live authority.

## Tests and failure accounting

The A1 suite checks finite stages/mode URLs, stock/flow/period/entity/basis semantics, withdrawal and unverified sources, counterfactual Source/claim changes, stale derived agenda inputs, aviation research exclusion, public/authenticated equivalence, forged identity, private-run traps, canonical pressure link authority, original artwork and the unchanged legal hold. The browser checks desktop, both iPads, mobile 390/320px, JavaScript-disabled native navigation, keyboard/touch, mode history/reload, portrait illustration expansion, 200% zoom, closed source inspection, print DOM and Source withdrawal through Back and reload.

The inherited public-financial test keeps its original positive/negative/withdrawal assertions; only the fallback title changes to the accepted design. Existing experience tests retain source-withdrawal, identity, route and distinct-perspective checks, replacing obsolete question headings, `data-component` markup, investigation prompts and placeholder expectations with the new headings/stage markup, labelled Insight and omission policy. The existing customer-outcomes link remains. No test is removed, marked skipped or xfailed.

The first hosted head also exposed four specific integration cases, all corrected before final validation:

- `test_customer_markup_has_no_research_controls_even_hidden_or_printable` had the older universal zero-disclosure expectation. Its two Lloyds Landscape cases now permit exactly the **one A1-commissioned** disclosure, require no nested controls/PDF links/private administration, then apply the original clean-editorial assertions to everything outside it. Every other screen retains the original rule.
- EAI-2's browser requires the existing `data-intelligence="funding-base"` marker. It is retained on the single current calculated comparison, with no duplicate entry.
- `test_expired_review_omits_all_new_views_without_empty_preview_sections` found that recomputing from still-eligible stock facts could resurrect a comparison after the existing agenda's release review expired. A1 now also requires that current existing-owner agenda entry; the new negative test preserves unrelated facts while suppressing the comparison/link. No review window or source permission is extended.
- `test_every_interactive_detail_is_server_addressable_without_js[lloyds-landscape]` requires the existing `insight` focus landmark. Selected Economics details retain that landmark and its labelled heading. No detail or accessibility test is removed.

The retained broad browser proof's two root headings are updated to the accepted design; its navigation, source, keyboard, layout and permission checks remain. These are explicit reconciliations, not refreshed inherited-failure signatures.

Exact renderer evolution is bounded by `Renderer-Evolution.json` and an AST comparison that permits only six listed function bodies to differ. Imports, constants and every other function must remain exact. Unknown after-hashes fail validation. Original historical owner pins and their prior checks remain intact; the compatibility chain first validates the current cut then supplies the exact predecessor to historical checks. **This is development assurance, not a runtime rights/approval registry.** Neither `flora_ci.py` nor `flora-baseline-v1.json` changes. Any changed inherited failure/skip signature remains a failure, not an automatically accepted refresh.

## Withdrawal limits

Every controlled render reopens the existing owners; no Economics payload cache, local storage, export endpoint or private-run fallback is introduced. Existing HTTP `Cache-Control: no-store` is retained. Withdrawing a source or input removes dependent stage numbers, calculation, evidence, accessible text and current print representation. Independent illustrative mechanisms and unrelated eligible facts remain. Actual browser tests exercise Back followed by current server rendering and direct reload.

No web application can recall a previously delivered screenshot, saved HTML, offline browser copy or paper print. The proof covers application-controlled fresh reads and tested browser behaviour, not remote artifact erasure or push invalidation of an already open page. Source lifecycle continues to belong to the existing Source owner.

## Rollback evidence and operator procedure

`enterprise_economics_quality.py` applies the **complete reverse patch** from the candidate back to verified baseline `03719d7573f087c65d9622719273aa4b89caf7d3` in a temporary Git index. Its tree must equal that baseline's tree exactly. This proves source rollback without touching the working index, application stores or production. No database migration, new Financial run, canonical change or source admission exists to undo.

Before merge: close the draft or return to validated main; preserve this branch/evidence for review. If later merged under separate approval, prepare a normal revert PR for the A1 merge/commit, rerun security/regression and obtain the normal release approval. Restore the whole A1 source change, including its exact-cut compatibility adapter, rather than partially editing rights or Source records. No automatic Render action is included; do not redeploy or change data under this commission.

## Remaining decisions

Owner visual/implementation acceptance is pending. Lloyds §2 legal applicability and §5 deep links remain unresolved; ADR-027 remains Proposed. New easyJet financial admission and a current qualified canonical Lloyds linkage remain outside this bounded implementation. No deployment readiness or live production behaviour is asserted.
