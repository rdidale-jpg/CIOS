# Conflict resolution and historical integrity

The integration branch begins at verified main `adf205993cc0857183d77766ce4882bf48326fb4`. A normal local merge of #561 retains #557 ancestry. A second normal local merge of #566 retains #564 ancestry. These are development-branch integration commits, **not merges of any remote PR or changes to main**.

Three conflicts were found and explicitly resolved:

1. **`tests/test_flora_commercial_visual_v3.py` historical guard.** Neither side was chosen wholesale. The original test identity now calls `tools/research/history_integrity.py`. It verifies all 142 original historical files against main, with the sole approved modification being the exact #557 Understanding-Review cut. Every old review list prefix/scalar must remain unchanged. Four explicitly named Depth snapshots and fourteen explicitly named Macro files must match their pinned approved Git blobs byte-for-byte. Exact inventory: **160 files**. Unknown additions, deletions, rewrites, symlinks and even ignored/untracked research files fail. Both prior protection intentions are retained and the approved additions themselves are protected.
2. **`tools/ci/flora-baseline-v1.json`.** The baseline is a structural union. Every original suite—including its selections, case identities, status, failure signature and skip reason—must be identical across source cuts. Added suites are Depth 20, enterprise integration 17, Macro 55 and scoped Macro trace 33 passing identities. A separate 15-test unified suite covers the integration; no failure/skip exception is introduced. Expected passing-identity union is **1,302**, subject to actual strict discovery. Focused runs overlap and are never added again to the gate total.
3. **`.github/workflows/flora-validation.yml`.** Both exact reviewed dependency branches are retained in the finite PR trigger list. Macro knowledge path filters are retained. Permissions, checkout credentials policy, Python version, commands, inherited-failure comparator, artifact retention and production isolation are unchanged. The new draft targets main, already eligible for CI.

## Immutable research cuts

- Main original cut: `adf205993cc0857183d77766ce4882bf48326fb4`.
- Depth approved review/four additions: `6988ba50d29c1f238293fc7fe110d6182f055e68`.
- Macro v1/v2 approved fourteen additions: `111600a56ca0edba0d47d1a8a0c92068060d83a8`; v1 source bytes were unchanged by v2.

The approved paths are named explicitly in the helper, not accepted through a directory wildcard or a moving branch reference. `test_history_is_append_only_and_existing_enterprise_visual_profiles_unchanged` remains active with #557's exact four additions, original-list prefixes, one named relationship and original visual-profile checks.

Seven new negative cases reject historical-byte modification, approved Macro-byte modification, approved Depth-byte modification, an old review-record change, missing file, unknown addition and ignored addition. Actual filesystem probes of the original guard are recorded alongside final validation evidence. No original test is silently retired or omitted.

## Application reconciliation

Application source and Home navigation combined mechanically. Subsequent bounded UI completion reuses the existing eight development modules and print owner for RCO-LBG-005, links Macro scope to the existing Enterprise Twin provides a full-overlay page heading, and retains visible source URLs in the cyber full appendix. No knowledge JSON, original evidence, opportunity record, qualification stage or production security owner is edited by these completion changes.

A browser harness initially targeted the empty bounding-box centre of a curved SVG flow link. Native tapping of its visible label passed in both pre-integration and integrated applications. A provisional decorative-pointer CSS change was removed as unnecessary; no application flow fix is claimed. Phone tests use the existing equivalent-text control when the large diagram is hidden.
