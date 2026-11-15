# Validation, reconciliation, limits and rollback

The final PR completion comment records exact SHA, completed local/hosted results and links. These commands describe reproducibility; they are not a claim that unfinished checks passed.

## Reproducible gates

```sh
python tools/ci/flora_ci.py --output /tmp/flora-eai2-ci
python -m unittest discover -s tests/ci -q
python -m pytest tests/test_flora_eai2_integration.py tests/test_flora_evidence_expansion_628.py tests/test_flora_visual_panels_632.py tests/test_flora_controlled_integration_625.py tests/test_flora_intelligence_presentation_623.py tests/test_flora_visual_streams_612.py tests/test_flora_visual_v2_583.py tests/test_flora_research_intelligence.py tests/test_flora_design_system_585.py tests/test_flora_primary_enrichment.py tests/test_flora_unified_integration.py::test_both_reviewed_workstreams_remain_ancestors_with_exact_source_cuts tests/test_flora_unified_integration.py::test_history_guard_rejects_every_unapproved_change tests/test_flora_commercial_visual_v3.py::test_no_existing_research_history_or_source_identity_is_changed -q
git worktree add --detach /tmp/flora-eai2-before ce4314c3528d5f4beae6e0e4fa53209ddb56ff5c
python tools/ci/flora_vp2_preview.py --scenario eai2 --output /tmp/flora-eai2-previews --baseline-root /tmp/flora-eai2-before
python tools/ci/flora_vp2_preview.py --output /tmp/flora-vp2-compatibility --baseline-root /tmp/flora-eai2-before
```

Use existing repository requirements and isolated Playwright 1.62.1/Chromium browser tooling. The unchanged full FLORA validation workflow additionally runs all seven product-compatibility groups (371 tests). The semantic workflow retains every existing VP-2 selector and adds the 52 EAI-1 and 72 EAI-2 tests (500 total). Dedicated EAI-2 and existing VP-2 browser workflows check out the exact PR head; the EAI-2 before tree is exact accepted main, not the obsolete EAI-1 layout. All fixture authentication/storage is temporary and no Offers/Pipeline state is written by preview tooling.

The 27-suite gate includes the unchanged **388 strict security tests** and exact inherited failure/skip comparator. Existing protected assets, all previous source expectations, approved failures/skips, CI comparator and baseline remain unchanged. Six exact existing EAI-1 candidate/excerpt files extend the historical inventory from 163 to 169; this is a proposed-corpus byte check, not source registration or Evidence acceptance.

## Covered negative cases

- Release/source rights denied/revoked, malformed rights, missing, private, stale, withdrawn, retracted, core-contradictory, wrong subject, wrong host or canonical-mutation flags remove dependent new content before title/link/preview.
- Original received-only complaint insight survives optional outcome denial; denial of its original received source omits the compound row.
- Whole-assessment and whole-Macro restrictions block dependent agenda enrichment.
- Incorrect deposit unit/entity/date/actual/type/basis and ineligible input omit the delta; other eligible existing financials remain.
- Exact source bytes, original identities, eight unselected/unexecuted forms, Proposed ADR and existing SEC/ONS denial remain; no publisher exception, fake archive or canonical receipt.
- No new public owner-material/export/asset route, no cross-scope agenda, foreign-workspace selection or private model/write-service reach.
- All 51 scene labels/32 original active addresses, nine singular agenda keys, seven streams, one chart/delta and native scope/layer/history/deep-link behaviour.
- 96 EAI-2 before/after JPGs and four ARIA snapshots; 879 EAI-2 browser checks plus the retained 777 VP-2 checks, covering desktop/iPad landscape/portrait/mobile and extended VP-2 keyboard/touch/zoom/320px/forced-colour/missing-art behaviour.

## Individual reconciliation of existing assertions

| Case | Bounded adaptation |
|---|---|
| INT agenda cardinality | Two → three keys per scope; retain uniqueness, subject, native URL and per-stream checks. |
| INT service conclusion | Enriched wording preserves no-deterioration/FOS counter-evidence; assert received/upheld values and absence of unresolved speed metric. |
| INT missing received source | Other valid AI/funding keys remain; no dependent complaint row. |
| INT/unified history counts | Add exactly six explicit existing EAI files while preserving every prior byte expectation and exact comparator. |
| EAI protected-owner manifest | Original #630 manifest remains exact historical evidence. Verify its old bytes against its old base, and verify the VP-2 `visual_streams.py` against current main rather than restoring obsolete renderer bytes. Other protected owners remain exact. |
| VP-2 exact dependency JSON | Artwork/scenes remain exact. Dependency pins now have permitted append-only EAI dependencies; a separate test preserves every original pin and owner basis. |
| VP-2 pending-evidence exclusion | Keep canonical histories, restricted SEC/H1 content, illustrative design data and owner administration excluded. Remove the old blanket ban on the now-commissioned permitted EAI complaint values. |

No test ID is deleted and no inherited failing signature is refreshed. The new negative tests initially redirected the entire source boundary in their fixture, correctly causing original source validation to fail; their fixture now redirects only the candidate-file lookup while preserving the existing owner's explicit-root verification. Another fixture assertion mistook a `69%` illustration coordinate for claim text; it now checks text rather than CSS markup. Neither correction relaxes runtime source or privacy checks. The independent medium finding added a genuine whole-release guard and ten regression cases.

## Known limitations

Physical iPad/Safari, real assistive-technology and owner visual acceptance remain manual. Chromium emulation and ARIA checks are not certification. Prior VP-2 image delivery/performance proof remains applicable because artwork/styles are unchanged; no new production performance measurement is claimed. Review expiry uses the existing real clock/cutoff through 15 December 2026, with no frozen prototype date. Expired/revoked evidence legitimately removes dependent additions.

Render identity and actual canonical target/receipt reconciliation remain unverified without authorised read access. Green GitHub CI does not verify deployment, import success or owner Evidence acceptance. Wider research, source-policy exceptions, News, role actions and the full unmerged Owner Command Centre are not delivered here.

## Rollback

No migration, import or canonical/production compensation is required. If later integrated and rollback is explicitly authorised, prepare a reviewed revert of the EAI-2 implementation commit(s) on then-current main, retaining intervening security changes. This removes the new Main compositions, expanded agenda/pins, six additive candidate files and their explicit history additions while restoring the accepted VP-2 tree at `ce4314c3528d5f4beae6e0e4fa53209ddb56ff5c`. Keep historical #630, eight forms and original evidence/branches; never hard-reset shared history or delete canonical records.

Run full security/regression/semantic and browser checks on the rollback candidate before any separately authorised release. Existing VP-2 imagery, navigation, Offers, Pipeline and source owners remain. No rollback, merge, Render operation or deployment is executed in this sprint.
