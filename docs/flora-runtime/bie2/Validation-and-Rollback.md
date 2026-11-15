# Validation, limits and rollback

Final SHA and completed run results belong in the draft PR validation comment. Pre-freeze browser images document this application tree; repeat browser checks at the final committed head, including hosted execution. No preliminary test run is represented as final-head assurance.

## Reproduction

From the committed checkout with `requirements.txt` installed:

```sh
python tools/research/bie2_quality.py
python -m pytest tests/test_flora_bie2_635.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/bie2-final-ci
```

Run the complete semantic selector list from `.github/workflows/flora-isp1-semantics.yml`, all seven separate product groups from `.github/workflows/flora-validation.yml`, and the original VP-2/EAI-2 browser scenarios. The new `.github/workflows/flora-bie2-browser.yml` also runs candidate QA, BIE negative tests and the actual application comparison at `github.event.pull_request.head.sha`. It uses isolated temporary fixture state, local TLS and Playwright1.62.1; no production service or secret is required.

```sh
git worktree add --detach /tmp/flora-bie2-before b5b05f841bc6f17f5ffe3286a65e8745e7c79ec3
python tools/ci/flora_vp2_preview.py --scenario bie2 --output /tmp/bie2-previews --baseline-root /tmp/flora-bie2-before
```

Browser dependencies: Chromium/Playwright, Node and OpenSSL. Hosted workflow installs pinned tooling separately from application dependencies. Public review artifacts contain sanitized checks and screenshots, not account credentials, environment configuration or raw tool logs.

## Meaningful negative cases

- Original issuer links/periods/units versus retained research paraphrases; no fabricated source-byte archive or accepted Evidence.
- Group financials bound to Group actors, not a PRA legal bank; per-metric UK/Group subject checks for ClearBank; USD HSBC reconciliation and Nationwide underlying reconciliation.
- Non-comparable FY/nine-month, partial consolidation, statutory/underlying/normalised, actual/target, customers/accounts and legal entity/Group definitions.
- Dated event versus publication window;31 literal current dates and90 inclusive structural dates; aliases deduplicated, unresolved dates uncounted, future effective state not completed.
- Wrong source, canonical ID, contract value, Revolut brand-to-bank join, National Trust-to-Barclays unsupported edge, fabricated event duplicate and accidental issuer/News runtime admission are rejected.
- Bounded release private/stale/withdrawn/retracted/revoked/contradictory/wrong-subject/wrong-host/malformed-rights/missing cases omit its dependent UI; previous eligible agendas survive.
- Existing whole-assessment, owner/tenant/workspace, source date/expiry and private export tests remain. Candidate research/decision files do not acquire public routes.
-169 old research byte expectations, exact comparator, protected source registry/IAM/Offers/Pipeline owners, original asset hashes, labels and active destinations remain.

## Individual existing assertion adjustments

| Test/scenario | Previous exact assumption | Justified bounded replacement |
|---|---|---|
| INT-1 same-agenda across lenses |3 rows at every scope | UK3 / Banking4 / Lloyds3; all original issue subjects and context checks retained |
| EAI-2 singular agenda keys |3 distinct rows every scope | Same explicit3/4/3, uniqueness, destinations, three regions and owner-data exclusions retained |
| INT-1 history delta |161→169; INT/EAI additions only |161→171; exact same prior161 bytes plus two literal BIE hashes |
| EAI-1 history delta |163→169; EAI additions only |163→171; exact same prior163 bytes and comparator plus BIE pair |
| Unified integration exact inventory dictionary |169 files with six EAI additions |171 with the same historical142/depth4/macro14/trigger1/INT2/EAI6 counts plus exactly two BIE additions; all ancestry checks retained |
| EAI-2 browser |3 unique Banking agenda links |4 Banking,3 other scopes, same uniqueness and original four additions/navigation/access checks |

No inherited failure baseline, comparator signature logic, approved skip/failure list, strict security selector or old test is removed or refreshed. New tests additionally compare all169 prior expected bytes directly against validated main.

## Limits and rollback

Offline QA checks structure, cited identities, defined numerical reconciliations and temporal/rights boundaries. It does not independently reacquire publisher content or prove completeness, production acceptance or rights beyond the recorded review. Original source bytes were not retained or archived; some linked originals also exceeded reader limits. Hashes refer only to retained local excerpts/manifests. The candidate corpus is not a production source registry.

Chromium tests emulate iPad/mobile/touch; physical Safari, assistive technology and production storage/identity are not certified. The narrow three-bank addition increases Banking Main length but adds no navigation system, imagery, graph engine or new destination. Review expiry remains15 December2026.

Before any later authorised integration, review the exact SHA and current main CI, resolve branch protections/conflicts and obtain owner acceptance. This sprint stops at a draft PR and issues **no deployment instructions or production action**.

Rollback in a later separately authorised code release is a normal reviewed revert of this bounded implementation commit, then full exact-head CI. Revert the agenda/Main/pins and the two literal candidate additions together; restore the prior history inventory and cardinality expectations as one coherent change. Alternatively the existing fail-closed source policy can withhold the release when inputs are no longer eligible. No database migration, source import, Evidence deletion, financial record reversal, Pipeline rollback or Render/data operation is needed or performed now. Preserve the research branch and historical review artifacts.
