# Owner walkthrough, acceptance and rollback

No merge, deployment or production/canonical writes are authorised by this PR. The pilot is opt-in and creates no runs automatically after a merge. Its source use covers the specified historical BoE numerical excerpt; issuer admissions remain separate.

## Reproduce in isolated non-production storage

From the checkout, with repository requirements and Playwright/Chromium installed:

```sh
python tools/research/f1_proof.py --output /tmp/flora-f1-proof --preview
python -m pytest tests/test_flora_f1_642.py -q
python tools/ci/flora_ci.py --output /tmp/flora-f1-ci
```

The proof always creates an isolated temporary data root, synthetic local account/workspace/session and resource ACL. Financial values/source are real; authority/ACL fixtures are not a production approval. Source withdrawal alters only a temporary copy of the existing source snapshot. It neither alters the checkout's research history nor revokes production records. `Proof.json` records the actual tested Git SHA, typed stored run and freshly calculated results. No credentials/session tokens enter output artifacts.

The browser opens the existing `/ai-financial-report/{run_id}` route. Inspect two dated source values and both calculations; open Sources and calculation with keyboard/touch to see method, use/attribution, capture/date limits and counter-caveats. Verify the UK→Banking→Lloyds two-selection journey and seven original views still work. The standalone temporary server closes when verification finishes; screenshots are review artifacts, not a persistent deployment URL.

For a subsequent approved non-production owner run, existing IAM must already grant the selected active workspace `package.upload`/`package.inspect` and its exact `BK-IND-002` resource ACL. A trusted service caller uses `candidate_analytics.create_run('boe-household-deposit-stocks', headers=existing_verified_session)` and opens `/ai-financial-report/{returned_id}`. Do not copy the synthetic fixture manifest, forge headers, automatically create a production ACL or invoke a paid refresh. There is deliberately no new anonymous creation endpoint or default UI population. The old `/financial-intelligence/{id}` web route is not opened by this implementation.

## Acceptance checklist

- [ ] Accept the first real result as **historical aggregate funding context**, not named-bank financial intelligence or a complete Banking rollout.
- [ ] Inspect two authentic located source values, exact GBPmillion/NSA/household-retail definition and nullable publication date.
- [ ] Check typed actual run persistence/reload, exact input/recipe versions, Decimal reproduction and explicit stock versus duration meaning.
- [ ] Check source withdrawal removes dependent title/measurements/calculations/links on every external read and retains lawful internal history.
- [ ] Check wrong entity/basis/currency/period/revision and estimated/assumed semantics; no peer ranking, adjusted flow, organic growth, procurement or buyer-need inference.
- [ ] Confirm real resolver/tenant/ACL tests, canonical-operation rejection and legacy latest-run isolation; no auth or authority from a source URL.
- [ ] Review desktop/iPad landscape/portrait/mobile, keyboard/touch/200% text and existing full visual browser evidence. Physical Safari/screen-reader certification remains outside these emulated checks.
- [ ] Review exact final SHA/full hosted gates, unchanged inherited failures/skips and independent critique. No baseline refresh or comparator relaxation.
- [ ] Decide whether to commission F2 composition or separately resolve a named-bank source-use basis. Do not treat either as approved by accepting this draft.

## Rollback

Before integration: close/defer the draft; no operational rollback needed. After separately approved integration, disable trusted creation/use of this opt-in pilot and perform a reviewed revert of the F1 adapter, bounded source snapshot, scoped result hooks, tests/tools/workflow. Re-run full CI. Preserve lawful historical candidate runs; no destructive migration, Evidence deletion, canonical compensation or source-policy rewrite is necessary. Existing Financial records/readers, research packages, seven scenes/variants, Offers and Pipeline are unchanged. A withdrawn source stays withheld; rollback must not bypass revocation or revive a cached result.
