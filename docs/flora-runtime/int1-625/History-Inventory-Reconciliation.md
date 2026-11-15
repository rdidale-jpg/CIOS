# Two corpus-inventory failures: individual reconciliation

The first complete local gate on `f2c5cc8de7ee115682555cc7f05094f103c280fb` reported **two new failures**, not inherited-signature changes. Both called the existing research inventory guard, which correctly rejected the new candidate proposal and numerical excerpt as unknown paths. No GO was issued for that commit. Strict388 security and the separate371 product regressions passed; those passes did not override the failed full gate.

| Existing case | Original assertion / failure cause | Controlled correction |
|---|---|---|
| `test_flora_commercial_visual_v3.py::test_no_existing_research_history_or_source_identity_is_changed` | Calls `verify_history`; byte comparator rejects unapproved proposal/excerpt paths. No historical byte mismatch. | Keep the test and its call unchanged. Extend the existing finite inventory by **two exact candidate paths and SHA256 values**, using the existing candidate-only addition pattern. |
| `test_flora_unified_integration.py::test_both_reviewed_workstreams_remain_ancestors_with_exact_source_cuts` | All ancestry checks pass; `verify_history` rejects the same two files before its historical inventory-count assertion. | Retain every ancestor and historical count:142 historical+4 depth+14 macro+1 trigger. Add an explicitly separate **2 presentation-candidate files**, total163; no canonical acceptance implied. |

The newly pinned paths are only `source-snapshots/INT1-FCA-Candidate.json` and `source-snapshots/PR-FCA-COMPLAINTS-H126.txt` within the existing Banking research model. The first is a proposed unaccepted record; the second is its licensed numerical excerpt. Hashes are literal reviewed bytes in `tools/research/history_integrity.py`, not calculated dynamically to approve arbitrary new content.

**No failure baseline or failure-signature comparator changed.** The research guard's `compare_history` function is also byte-identical. MAIN/DEPTH/MACRO references, trigger digest, all previous161 expected source contents, historical record-prefix checks, symlink checks and unknown/ignored-file rejection are preserved. No broad path exclusion, filename pattern, optional file or automatic future approval is introduced.

Additional tests compare all161 previous expectations directly with the pinned main implementation, assert that only the two new paths are added, compare the exact original byte-comparator implementation, and reject tampering with either candidate file or an unknown adjacent source. The original seven negative inventory tests and both positive tests run early in the dedicated semantic workflow and again through their existing full-gate suites.

This inventory admission authorises only the proposed code-review corpus for #625. It is **not Evidence approval, import, rights clearance for another source, canonical acceptance or permission to change a future candidate revision**. The source-admission review remains necessary and owner acceptance remains pending. No historical research file was edited.
