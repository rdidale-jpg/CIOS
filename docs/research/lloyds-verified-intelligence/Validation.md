# Validation, reproducibility and rollback

## Finite evidence measures

- 49/49 recovered notes have individual dispositions over unchanged IDs, entities, periods and original-record fingerprints. This is disposition coverage, not 49 fully verified facts or a global completeness score.
- 34/34 crosswalk entries have scoped source-review annotations; no canonical/workspace ID is invented.
- All byte digests remain null. No original publisher document, protected table, fabricated archive or new source permission is created.
- Two exemplar original-text reviews and two commercial investigations are prepared. **0/2 new genuine original-byte-bound journeys are complete**; both have explicit byte/use/identity blockers. Tests must not be presented as replacing them.
- Corrections include current Wealth & Insurance versus historical IP&I title; committee-reporting locator; issuer corroboration of engineering adoption; Bank Rate decision versus publication dates; and Halifax's dated, incomplete rebrand. The survey's unresolved named Lloyds chart row remains withheld.

## Commands

```sh
python docs/research/lloyds-verified-intelligence/review.py
python -m pytest -q docs/research/lloyds-verified-intelligence/test_verification.py
python docs/research/lloyds-verified-intelligence/validate.py
python -m pytest -q -o usefixtures=verified_flora_test_authority tests/test_flora_lloyds_recovery_proof.py tests/test_flora_initial_factory.py tests/test_flora_verified_factory.py tests/test_flora_blueprint_import_promotion.py
python tools/ci/flora_ci.py --output /tmp/flora-live-verification-ci-new
```

`review.py` reconstructs annotations from immutable #735 records and the committed review decisions. It does **not** reacquire sources or prove that future page content is unchanged. Reverification requires reading the original URLs again and recording changed support/date/use status, not just rerunning the script.

Seven task-specific checks cover complete identity-preserving disposition, partial/date qualifications, no invented byte hashes, both existing-acquisition holds, missing-evidence assurance despite approval flags, and inactive restricted financial output. The actual-source download denial was separately observed; the service tests use a labelled negative unavailable-fetch input and never manufacture positive publisher HTML.

Existing isolated Factory/Blueprint tests cover correction, withdrawal, repeatability and access denial as regression controls only. They are not counted as new genuine journeys. Full strict security and versioned regression use the unchanged comparator; inherited failures/skips are reported as inherited, not all tests passing. Exact-head results are recorded in the PR completion evidence.

This is a documentation/review-script change stacked on the unmerged #735 candidate. Main-targeted hosted workflows do not automatically run on that stacked target. Do not claim fresh hosted validation of this new SHA if no job was triggered. The four immutable #735 hosted results are independently checked in PR735-Review.md; fresh full local validation is required for this draft. After explicit #735 merge approval, post-merge CI/integrity must be verified before retargeting this draft for integration review.

## Scope and rollback

Only this new review directory changes relative to #735. `validate.py` reconstructs the three JSON manifests, checks 49/34 coverage and all reference/fingerprint boundaries, validates the two blocked journey states and exact file inventory, confirms every original file is unchanged and verifies local links.

It reverses the complete candidate binary diff in a temporary Git index and requires equality with #735 tree `a51265aa64217bbfc673cdff5e9fbb39da96fe2e`. No branch or real index is rewritten. The source-inspection note does not depend on a production migration, new database, service, credential or Source permission. Rejecting this draft needs no runtime rollback. Any future authorised merge can be reverted through normal reviewed Git operations; do not apply isolated test receipts to production or delete historical research.

## Self-critique and remaining decisions

Publisher text inspection improves the actual content quality but does not authenticate original bytes, establish legal permission, prove issuer claims independently or resolve live identity/ACL state. Cached official search support is weaker than a current directly retrieved page. Current rosters do not recreate past page versions. PDF text extraction can lose chart-row identity; the unresolved survey value is deliberately excluded.

No UI change, physical-device acceptance or new content-rendering result is claimed. Presentation copy is a specification for later implementation within existing components. The known 65px technology-heading defect remains in that backlog.

The owner must explicitly approve #735's exact merge candidate; source/identity owners must resolve the genuine journey prerequisites before execution/publication. The network confirmation did not complete, and no environment settings changed. No Source/legal, canonical or Pipeline authority can be inferred from this review or its tests.
