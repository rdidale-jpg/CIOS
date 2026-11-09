# Security Repair 01A testing and reproduction

Use Python with repository requirements, isolated temporary roots and no
production credentials, paths or network requests. The comparison baseline is
`dc9203e6880f8722e821d39cf53b689732edb0e7`.

## Production security boundary

Run from the repaired checkout:

```sh
FLORA_DATA_DIR=<isolated-data> PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  -p no:cacheprovider tests/test_flora_security_repair_01a.py \
  tests/test_flora_security_service_contracts.py \
  --basetemp=<isolated-pytest> --junitxml=<security-after.xml>
```

The real_security_boundary module never installs the explicit service-test
identity provider. HTTP uses local ephemeral ports, not Render. Fingerprints
cover all files in the synthetic data root across denied and public journeys.
Public Banking derived outputs are redirected to a separate temporary directory.
These tests create no production owner, session or canonical acceptance.

## Exact before and after comparison

1. Make a separate checkout of pinned main. Do not change the developer's checkout
   or use an existing production data root.
2. Overlay only the repaired branch's changed/new tests and fixture files plus
   the pytest marker registration onto that baseline. Do not overlay application
   code. Use identical test files on the two checkouts. This preserves domain
   test inputs after removal of legacy header trust and adds rejection cases.
3. Run the security command above in both checkouts with different isolated roots.
   Vulnerability assertions intentionally fail on main; this is the reproduction,
   not an acceptable baseline deployment result.
4. Run the existing 26-module regression runner from each checkout, separately:

```sh
PYTHONDONTWRITEBYTECODE=1 python \
  docs/flora-runtime/experience-repair-02/run_regressions.py \
  --output <isolated-domain-results>
```

5. Compare exact JUnit case IDs:

```sh
python docs/flora-runtime/security-repair-01a/compare_results.py \
  --before <domain-before> --after <domain-after> \
  --security-before <security-before.xml> \
  --security-after <security-after.xml> \
  --output <comparison.json>
```

The script rejects differing/duplicate case sets and exits nonzero for newly
failing cases. Public output retains failure/skip categories and SHA-256 digests,
omitting raw requests and trace excerpts. Inherited failures are not counted as
passing. Original test-contract changes and fixture limitations are explicit in
Negative-Test-Matrix.md and the comparison metadata.

## Retained inputs and limitations

The repository-retained TEL W5 archive is hash-pinned by the existing tests.
BNK W1 and TEL W6 were unavailable in this execution and remain explicit skips;
no replacement packages were uploaded or fabricated. Domain service tests use a
mocked provider for already-authenticated fixture contexts. Their success does
not establish real session issuance, membership persistence or 01B readiness.

Full regression logs, JUnit XML and temporary stores for this execution are under
`/workspace/work/security-repair-01a/` in the execution workspace. Only compact
exact-case comparison data and reproduction code are committed; no archives,
credentials or owner stores are added to the PR.

## PR 539 targeted review closure reproduction

Use initial PR head `4c029a244cc3212fb9ec56bc762dee420e96c0a4` as the before
checkout; main was independently reverified at the original pinned SHA. Copy the
identical amended `tests/flora_security_fixtures.py`,
`tests/test_flora_security_service_contracts.py` and new
`tests/test_flora_security_review_closure.py` into that checkout. Keep production
modules at their respective revisions. Do not install test fixtures into real
security-boundary suites. Use isolated temporary data roots and derived output.

Run on both checkouts, retaining separate JUnit files:

```sh
python -m pytest -q tests/test_flora_security_repair_01a.py tests/test_flora_security_service_contracts.py tests/test_flora_security_review_closure.py --junitxml=checks.xml
python docs/flora-runtime/experience-repair-02/run_regressions.py --output domain-results
python -m pytest -q tests/test_flora_pilot_auth.py tests/test_flora_pilot_import_bypass.py tests/test_flora_pilot_blueprint_review.py --junitxml=legacy.xml
```

The last command intentionally exits nonzero: retain all 27 results, including
nineteen retired-contract and five pre-existing failures. The domain runner retains
all 436 IDs, including 22 inherited failures and ten unavailable-input skips.
`compare_results.py` provides sanitized `read`/`group` helpers; the review-closure
JSON compares exact equal ID sets with fixed/new/inherited/skip lists separately.
Original main-to-01A comparison artifacts remain unchanged. The new security set
has 104 cases, including five explicit service-context cases; the remaining 99
use the real fail-closed production boundary. All 127 public routes execute within
one exhaustive handler/sentinel case, in addition to individual attack cases.
