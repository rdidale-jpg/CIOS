# Validation, limitations and rollback

## Exact-head procedure

Final local and hosted results, SHA and run URLs are recorded in the PR validation comment after execution. The commands below are the reproducible checks, not a substitute for completed results. No baseline refresh, comparator relaxation, security test removal or source/evidence admission is part of this sprint.

```sh
PYTHONPATH=. python tools/ci/flora_ci.py --output /tmp/vp2-ci
python -m unittest discover -s tests/ci -q
python -m pytest tests/test_flora_visual_panels_632.py tests/test_flora_controlled_integration_625.py tests/test_flora_intelligence_presentation_623.py tests/test_flora_visual_streams_612.py tests/test_flora_visual_v2_583.py tests/test_flora_research_intelligence.py tests/test_flora_design_system_585.py tests/test_flora_primary_enrichment.py tests/test_flora_unified_integration.py::test_both_reviewed_workstreams_remain_ancestors_with_exact_source_cuts tests/test_flora_unified_integration.py::test_history_guard_rejects_every_unapproved_change tests/test_flora_commercial_visual_v3.py::test_no_existing_research_history_or_source_identity_is_changed -q
git worktree add --detach /tmp/flora-vp2-before 8a53777d1dec359f56b66e533d512c0a86881939
PYTHONPATH=. python tools/ci/flora_vp2_preview.py --output /tmp/vp2-previews --baseline-root /tmp/flora-vp2-before
```

Install existing requirements plus isolated Playwright 1.62.1 and Chromium for browser proof. The full unchanged `flora-validation.yml` additionally runs the existing product compatibility groups (371 tests). The semantic workflow retains all prior selectors and adds the 137 VP-2 tests (376 total). The dedicated VP-2 browser workflow checks out the exact PR head, uses isolated temporary authentication fixtures and publishes sanitized previews/ARIA/check/performance artifacts. No deployment job is added.

The 27-suite gate includes the unchanged **388 strict security tests**, versioned inherited failures/skips, source/history/artifact integrity and existing domain regressions. New tests cover all seven views, all 51 labels/32 addresses, contextual navigation, exact 23 imports plus seven historical originals/21 variants, finite asset routing and bytes, source denial/revocation/contradiction, private releases, malformed financial scope, supplier relationship withdrawal, authenticated Owner versus outsider, CSRF/cookie boundaries, no new-source/static-design data, cache and no private-model/writer calls.

Browser checks cover actual route journeys with/without JS, native links/history/deep links, peer exits, 32 addresses, six agenda keys, three context layers, source activation, role/account/CSRF behaviour, no private-domain writes, all seven views at desktop/iPad landscape/portrait/mobile/laptop/320px, touch, Retina, effective zoom, full 200% text enlargement, reduced motion/forced colours, no horizontal overflow, missing-art fallback, ARIA snapshots and no page-script errors. The source click is intercepted; this tests the correct publisher URL without asserting publisher uptime.

## Assertion reconciliation

The first diagnostic full run at `ddc38fe7ee203aedd1ef9d0c4dae0297a2c73d46` found **two new failures**. All **36 inherited failure signatures and 10 approved skips matched unchanged**. Both new failures were individually resolved:

| Case | Diagnosis | Correction |
|---|---|---|
| `test_flora_v2_information_architecture::test_primary_workspace_routes_are_served_without_replacing_deep_links` | Raw HTML counted 20 industry markers; mutually exclusive responsive scene trees now serialize 40 | Keep test and route assertions; verify exactly the original 20 unique A–T markers, each twice. Browser verifies only the appropriate scene is accessible/visible. |
| `test_flora_unified_experience::test_canonical_bank_pages_and_other_historical_profiles_are_explicit` | Real omission of the existing canonical link in the new renderer | Restore canonical link in implementation; existing assertion unchanged. |

Earlier focused presentation checks were reconciled individually, without changing baseline identifiers or negative/security assertions:

| Test file / cases | Expected presentation change and retained check |
|---|---|
| `test_flora_visual_streams_612.py` stream links | Native stream focus hash and compatible-detail mapping; original resolver identity, layer, selection and all stream destinations retained |
| Same file, image delivery | Two mutually exclusive portrait subtrees and decorative watermark replace one full-scene image; assert responsive accepted 384/768 assets and preserve all 21 historical variant hash checks |
| Same file, UK labels/exits | 40 serialized SIC / six researched markers across two subtrees; assert original 20 unique sections / three researched exits and inert unsupported subjects |
| `test_flora_design_system_585.py`, three Home aliases | Same responsive duplicate-marker accounting, retaining exact unique section set and per-marker cardinality |

No inherited failing assertion/headline was rewritten. The comparator, baseline file, approved failures/skips and strict security suite are unchanged. Final exact-head gate must report zero unexplained changes; any real regression must be fixed in scope before delivery.

## Evidence and performance limits

- 100 committed application JPGs, three ARIA snapshots and 777 automated browser checks accompany the implementation. They use current permitted owner data, not candidate EAI research or a frozen prototype clock.
- Local cold loopback measurements use 1.6Mbps / 150ms RTT at mobile and desktop. [Performance.json](previews/Performance.json) records FCP, visible-art readiness and requested image byte sizes. FCP is not full-art readiness; mobile defers the collapsed Left. These are single samples, not a production SLA or proof of Render/network performance.
- 384px/768px portraits preserve the exact accepted delivery bytes. Large Retina portraits can still cost roughly 0.32–0.44MB per selected stream; the existing historical assets remain downloadable but are not eagerly loaded in the new workspace.
- Physical iPad/Safari, VoiceOver/real screen-reader review and owner visual acceptance remain manual. Emulated touch, accessible names, focus, keyboard, forced colours and full text enlargement are automated; they are not full WCAG certification.
- Production Render version remains unverified because read-only public requests failed and no authenticated Render service is available. No assumption is made that this branch or main is deployed. Before any future authorised release, the owner must verify production source/configuration and the exact reviewed deployment candidate separately.
- Technology/Aviation remain their existing destinations; this bounded implementation covers the accepted UK/Banking/Lloyds streams. News, Tools and Topic Cards are not activated. The full unmerged #603 Owner Command Centre is not imported.
- Agenda expiry/revocation may legitimately omit content under the existing real-date policy. Unsupported claims are omitted; no research gap/question/administrative content is inserted to fill space. Portraits are conceptual navigation, not representations of actual premises or authoritative organisation diagrams.

## Rollback

No migrations, source imports, canonical mutations, Offers/Pipeline writes or production operations require compensation. If the owner later approves integration and subsequently requests rollback, prepare a reviewed revert of the VP-2 implementation commits on the then-current main; run full security/regression CI on that revert before any separate deployment decision. Restore the prior `visual_streams` render/header composition and remove only VP-2 additive assets/style/workflow/tests/docs as appropriate, retaining intervening work and the existing INT-1/VEX-1 source and permission owners. The known prior application tree is main `8a53777d1dec359f56b66e533d512c0a86881939`; do not hard-reset a shared branch or overwrite later security fixes.

All original art/variants and canonical data remain untouched, so the prior visual renderer can be restored without data conversion. No rollback or deployment is executed by this sprint. Keep the implementation PR draft for explicit owner review.
