# V3 validation results

| Gate | Actual local result |
| --- | --- |
| Full strict regression profile | **PASS: 1,140 passed, 57 matched inherited failures, 10 original skips; 1,207 exact identities** |
| Existing strict security suite | **388 passed**, included above |
| New v3 suite | **27 passed**, included above |
| Primary enrichment + new v3 suite after compatibility correction | **45 passed**, subsets of the full gate |
| Existing focused visual/commercial/sales/multi-industry/research suites | **120 passed**, subsets of the full gate |
| CI-policy failure-behaviour tests | **25 passed**, separate policy self-tests |
| Workflow syntax | actionlint passed |
| Browser | 24 industry/lens/viewport combinations; desktop keyboard, tablet/mobile touch, evidence/enterprise return path, explicit synthetic capture/qualification/duplicate linking, no overflow/console errors; additional empty/unsupported, dense/disputed and private-mobile checks passed |
| Print | Primary map activities retained on page one, public counterevidence/Unknowns retained, synthetic qualification references retained; disclosure state restored after printing |

Inherited failures remain exactly **21 domain + 12 financial diagnostics + 24 historical legacy = 57**. All ten original skip reasons and all prior baseline entries are unchanged. Only the 27 new expected passing identities were added. No new/changed failure or unexpected skip was accepted.

The first full comparison found a real compatibility regression in `test_old_captured_opportunity_stays_unchanged_after_primary_enrichment`: the new review annotation attempted to use a current review against an older assessment digest. The correction attaches review metadata only when that pinned digest matches. Older captures preserve their original provenance and remain Discovered/unqualified; no newer review is invented, no record is migrated and no permission or qualification control changes. The unchanged historical test and the complete primary-enrichment suite now pass. A new negative assertion also verifies that mismatched historical snapshots acquire no current review metadata.

The negative v3 cases use real isolated server sessions and existing producers. Anonymous/CSRF/scope/role/revocation/expiry/workspace/ACL denials preserve the business-store hash. Successful qualification records an actor/workspace audit; repeat capture returns the same ID and unchanged version/provenance. Public GET exploration does not create records or enumerate private Pipeline IDs.

[Browser evidence](Browser-Checks.json) and [print evidence](Print-Checks.json) describe completed checks. Private records and references in screenshots/PDFs are explicitly SYNTHETIC acceptance fixtures, created only by deliberate actions in a disposable local HTTPS workspace. No production seeding or account provisioning occurred.

Hosted validation is verified separately on the published PR candidate, with the actual run/check and retained sanitized artifacts. Local results are not substituted for GitHub execution. Human comprehension, independent customer verification, physical iPad/Safari and assistive-technology usability remain unmeasured/untested; see the comparison protocol and limitations in the README.
