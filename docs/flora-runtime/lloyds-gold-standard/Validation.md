# Validation, release boundary and rollback

## Reproduce

Use the repository's requirements and existing Chromium/browser test setup. All runtime stores in tests are isolated temporary directories. No production store or paid service is used.

```sh
python docs/flora-runtime/lloyds-gold-standard/audit.py --check
python -m pytest tests/test_flora_lloyds_gold.py tests/test_flora_living_enterprise_preview.py -q
python tools/ci/flora_ci.py --output /tmp/flora-gold-exact-head-ci
```

Actual browser comparison:

```sh
git worktree add --detach /tmp/flora-gold-baseline eaca26f2b31c3c9227bb797d60f7d3492a8313d1
# Run this branch's absolute browser.py path while cwd is the baseline checkout:
python /absolute/path/to/this/branch/docs/flora-runtime/lloyds-gold-standard/browser.py /tmp/flora-gold-browser before
# Return to this branch's checkout:
python docs/flora-runtime/lloyds-gold-standard/browser.py /tmp/flora-gold-browser after
```

The existing Enterprise Economics workflow runs these exact-head tests and browser journeys in addition to the existing security, financial, compatibility, recovery and semantic suites. Hosted captures are uploaded under the exact PR SHA. The unchanged full comparator retains its original 1,432 identities, 388 strict tests, inherited exception signatures and approved skips. New tests run separately; no baseline refresh or comparator weakening.

## Evidence

The candidate's PR checks and completion report give final exact-head local/hosted outcomes; a passing result is not assumed here. [Browser-before.json](Browser-before.json) records real #730 baseline renders. [Browser-after.json](Browser-after.json) records actual candidate runtime hashes, devices, interactions, source withdrawal and no-JS navigation. Source/code hashes avoid attributing pre-commit screenshots to an untested commit. Exact-head hosted artifacts provide the commit-specific rerun.

Coverage includes all fifteen image regions and deeper states; Group-first arrival; three perspectives; four SWOT quadrants/eight themes; differentiated investigation and counter-evidence; applications/Unknown dates; original/current return paths; division selection across streams, reload, Back/Forward; keyboard/touch, both iPad orientations/mobile, overflow and 200% zoom. Original default/preview content is compared to actual baseline rendering. Existing Banking/Aviation/easyJet public journeys remain exercised.

Source tests cover restriction/revocation/withdrawal, stale/superseded/contradictory/owner-only inputs; all dependent figures, chart meters/accessibility, SWOT, application/provider descriptions and timeline output. A real HTTP history restore and print DOM re-evaluate Source restrictions. No export route, snapshot or persisted client result is added. Dated committed screenshots are review artefacts, not a live export mechanism.

Financial tests reject wrong Group, period, currency, underlying/statutory basis, target/actual state and numerical value/disclosure binding. New segment data and direct PDF links remain absent; Group stock/flow/time definitions and original precision are retained. Guest/forged/owner/expired/revoked-membership Main output remains identical public research, with private Financial reads trapped as errors. Route tests cover invalid selectors, duplicate parameters, path traversal, POST, HEAD and no-store headers. Existing mutation/auth methods and artwork retain exact original bytes/ASTs.

## Exact scope and rollback

The PR Files view and [Changed-Files.txt](Changed-Files.txt) enumerate the final scope. Allowed runtime changes are one optional Lloyds composition, one CSS file, one original-preview entry, finite public route declarations and GET/HEAD dispatch. Existing compatibility code gets one exact-byte evolution layer; tests preserve all historical constants and negative-mutation behaviour. No accepted ADR, source/research input, Source permission, Financial owner, security module, Offer/Pipeline owner, schema, dependency or runtime configuration is changed.

Before merge, rollback is simply closing the draft; production is untouched. After any separately authorised integration, reverting the PR removes the optional route/style/entry and returns to the original default/#730 preview. There are no data writes, migrations or saved runs to unwind. A temporary-index reverse patch must reconstruct baseline tree `e4b37d025f0a8c337c538fab71ad239f9e74b265`; the exact result is reported in the PR/completion. Do not operate on production storage or reset credentials for rollback.

Deployment is not authorised. A future release must pin its then-validated commit and check the existing FLORA - CURRENT service and rollback deployment without new infrastructure. No production or live-SHA repair is claimed by local testing.
