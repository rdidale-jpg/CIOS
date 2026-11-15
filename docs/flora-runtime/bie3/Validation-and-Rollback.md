# Validation, exact-head proof and rollback

Final committed SHA and completed local/hosted results are recorded in the draft PR validation comment. Pre-freeze images show this application tree; the browser scenarios must also run after commit and on hosted CI at `github.event.pull_request.head.sha`. Preliminary success is not final-head assurance.

## Reproduction

```sh
python tools/research/bie3_quality.py
python -m pytest tests/test_flora_bie3_637.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/bie3-final-ci
```

Run the full existing selector list plus BIE-3 from `.github/workflows/flora-isp1-semantics.yml`; none of the existing semantic selectors is removed. Run all seven separate product groups from `.github/workflows/flora-validation.yml`. The original VP-2, EAI-2 and BIE-2 browser scenarios remain and the new BIE-3 scenario uses the same isolated actual-application fixture:

```sh
git worktree add --detach /tmp/flora-bie3-before c295e056cbae0f1adebc1070eb272d79b650a45f
python tools/ci/flora_vp2_preview.py --scenario bie3 --output /tmp/flora-bie3-previews --baseline-root /tmp/flora-bie3-before
```

Use Node, Chromium/Playwright1.62.1 and OpenSSL as installed by the hosted browser workflow. Fixture accounts/storage are isolated temporary test state, never production owner credentials or evidence of actual canonical target/receipt status. Sanitized results and screenshots may be published; raw logs, credentials, environment configuration and private records are excluded.

## New tests and negative boundaries

- Original source/retained-note hash distinction, date precision, source identity and each financial cell/sign/typed value; no invented original archives, source redirects or changed publisher admission.
- HSBC reported USD legal-bank earnings, source basis and full nine-month period; Santander signed income/expense/impairment/provision bridge and May–September TSB contribution; NatWest separate deposit definitions and differing CAL comparator bases.
- Group/legal-bank actor bindings, individual reporting periods/units, actual/target state, duplicate subjects, conditional future date versus completed event, supported atomic claim wording and exact existing model prefixes.
- Real canonical IDs/Evidence IDs remain blank; existing `FactualClaim` validation refuses them. Source collection/semantic labels cannot grant issuer admission. Shared Researcher mapping omits producer id, and probes fail if Observation construction or canonical review/mapping/writes are attempted.
- New FCA source revocation/withdrawal/retraction/staleness/contradiction/private/malformed rights/missing release/wrong subject/host removes new outcomes and selectors, preserving the old eligible view. Parent-source denial removes every dependent selected view. Whole-assessment restrictions and editorial expiry remain effective.
- Explicit wrong scope/period/unit/measurement state is rejected by the service composer independently of dependency pins; changed source/claim identities and duplicate releases cannot create another subject or agenda concern.
- Public HTML/routes/ARIA/export boundaries exclude owner proposals, unpublished issuer candidate fields, foreign workspace selectors and research files. Existing full security tests retain their IAM, source-rights, CSRF/origin, audit, idempotency, private seller and Pipeline controls.
- All171 previous research bytes and the comparator are exact; unknown additions still fail. Frozen BIE-2 research, source policy, protected owner services, eight unexecuted forms, proposed ADR and all approved art/navigation assets remain.

The existing atomicity heuristic treats the word “before” as a possible state transition and “May” as a modal. Proposals use the standard financial term **pretax** and explicit ISO event dates rather than weaken the validator; original accounting labels/periods remain in their own metadata and source references. These wording choices do not convert conditional or speculative assertions into facts. PartVII's actual effective date remains null and its expected period separate.

The first touch-navigation browser run checked the URL before its native navigation completed. The test now explicitly waits for the selected-bank URL/load after a touch action, then checks the new content and retained context. Application interaction logic was not changed to mask the test timing issue.

## Exact existing assertion reconciliation

| Existing test | Narrow change | Preserved proof |
|---|---|---|
| INT-1 all161 prior sources | Current inventory171→173; union adds exact BIE-3 pair | All161 prior bytes, unchanged comparator and original addition groups |
| EAI-1 all163 prior sources | Current171→173; union adds BIE-3 pair | All163 prior bytes, original six EAI additions and comparator |
| BIE-2 all169 prior sources | Current171→173; difference is the two BIE-2 plus two BIE-3 artifacts | All169 prior bytes and exact comparator; new BIE-3 test separately checks all171 current-main bytes |
| Unified integration inventory dictionary | Adds `bie3_presentation_candidate_additions:2`, total173 | Historical142/depth4/macro14/trigger1/INT2/EAI6/BIE2=2, all ancestry checks and rejection of unreviewed paths |

No inherited failure baseline, failure signature comparator, approved skip list, strict388 selection, existing test or regression case is removed or mass-refreshed. Banking still has four singular concerns, UK/Lloyds three each; no cardinality relaxation is needed for selected-bank context.

## Quality limits

Offline research QA checks inspectable source/cell references, exact financial arithmetic, current owning-contract compatibility, source policy and unresolved authority. It cannot independently reacquire publisher content or prove exhaustive research, legal permission, production identity or canonical record presence. Twenty financial proposals have located reviewed-cell references; four integration disclosures retain their source locators and separate phase/expectation metadata. Human Evidence/identity decisions remain required.

Original PDF text was read, but full source bytes were not retained. Retained hashes identify only actual bounded review notes/cells. No original-source archive, extraction bbox or canonical approval is fabricated. An accepted web-excerpt candidate path is not conflated with a future original-PDF table-adapter requirement.

Browser checks use actual local application code with Chromium and emulated iPad/mobile. They include four viewport sizes, seven original views, selected-bank switching, close/return, native history/deep links, keyboard,44px touch controls,320px,200% zoom, forced colours and permission/source isolation. Physical iPad/Safari and assistive-technology certification remain outside this proof.

The public release provides service activity and firm-resolution context, not comprehensive enterprise economics, customer pain, buyer authority, finance ranking or sales qualification. Those broader sources/identities/acceptance decisions are explicitly blocked and reviewed separately.

## Rollback

This sprint performs no merge or deployment. A later authorised code integration can be rolled back by a reviewed revert of this bounded commit and its two FCA candidate additions, restoring the prior173→171 inventory and corresponding exact assertion expectations together, then running full exact-head CI. Keep the historical candidate/decision pack and research branch inspectable.

There is no schema migration, canonical import, production financial update or Pipeline mutation to reverse. A denied source already withholds dependent read-only profiles. Any separately authorised future canonical import follows its existing governed history/compensation process, not blind deletion or reassignment of Evidence.
