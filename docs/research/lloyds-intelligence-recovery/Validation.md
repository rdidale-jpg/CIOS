# Reproduction, validation and rollback

## Reconstruct the recovery handoff

Use an existing authorised repository checkout and the pinned research package objects listed in `recover.py`. They are draft-branch history, not required runtime dependencies. If Git lacks an object, fetch that exact existing commit using normal authorised Git read access; do not merge or cherry-pick those branches. The audit's original packs and this recovery's hashes distinguish repository records from unavailable publisher bytes.

```sh
python docs/research/lloyds-intelligence-recovery/recover.py
python -m pytest -q tests/test_flora_lloyds_recovery_proof.py
CIOS_LLOYDS_RECOVERY_OUTPUT=/tmp/flora-lloyds-recovery-result python -m pytest -q tests/test_flora_lloyds_recovery_proof.py
```

Compare the two generated `ai.json` / `division.json` summaries with the committed receipts. The test fixture installs temporary in-process identity only; it is not a login or real HTTP authentication proof. Tests use temporary stores, with no network/paid services and no production credentials.

## Applicable regression commands

```sh
python -m pytest -q -o usefixtures=verified_flora_test_authority tests/test_flora_initial_factory.py tests/test_flora_verified_factory.py tests/test_flora_blueprint_import_promotion.py tests/test_flora_lloyds_recovery_proof.py
python tools/ci/flora_ci.py --output /tmp/flora-lloyds-recovery-ci-new
python docs/research/lloyds-intelligence-recovery/validate.py --output /tmp/flora-lloyds-recovery-qa.json
```

The existing CI gate enforces all **388 strict security tests**, approved failure/skip signatures and integrity comparisons without baseline changes. Full regression success means the comparator passes: it does not turn approved inherited failures into passing assertions. Exact-head local and hosted results are linked in the PR and completion comment; do not infer deployment from them.

The only existing-file edit adds this proof and its path triggers to the existing verified Factory workflow. That workflow also runs its existing Source-revision-withdrawal regression and existing desktop / both-iPad browser proof. No workflow permissions, comparator or security tests are changed. No new approval service or deployment job is introduced. Existing fixture authentication is never installed in strict real-security-boundary tests.

`validate.py` reconstructs all four generated manifests from immutable refs, checks original-record/rights/identity distinctions, all 21 backlog dispositions, eight unchanged proposal fingerprints, 13 Decimal reconciliations, local links and exact changed-file scope. It verifies every original file outside the one additive CI workflow is byte-identical. Original artwork, source ownership, Financial policy, runtime routes, canonical files and Pipeline controls therefore remain unchanged.

## Rollback proof

Stage the candidate files before running QA. The validator takes the exact staged tree, reverses the complete binary diff in a **temporary Git index**, and checks equality with baseline tree `576599df46ebacdceef4b74bd8b3e39b7cdd772e`. It changes neither the real index nor working tree during that check. This demonstrates exact repository rollback, not a production database restore.

The new PR stays draft and unmerged. Rejection therefore needs no runtime or data rollback. If these documentation/tests were later merged with explicit approval, revert that merge through the existing reviewed Git workflow; no application deployment, source-policy change, database migration or Financial-run deletion is needed for this sprint. Isolated proof stores are disposable pytest temporary directories; never apply the test promotion receipts to production.

## Limits and critique

The proof establishes integration under test authority, not new original-source verification or real seller/customer validation. Legacy replay needs real document-revision binding before automatic Source withdrawal can be claimed for those specific records. The existing revision-aware suite is separate evidence, not a substitute for that missing binding.

The recovery selects explanatory material rather than reproducing financial tables. The 362-record denominator is package identity, not semantic or enterprise completeness. Source metadata has repeated originals and aliases, not 100 independent verified sources. Historical rights labels are retained as evidence of prior status, not new legal conclusions.

No new desktop/iPad designs or captures are commissioned here. The accepted audit's diagnostic captures remain evidence for the deferred 65px defect. Existing browser regression covers unchanged route/source behavior; it is not final owner visual acceptance. Production canonical/private status remains UNKNOWN.
