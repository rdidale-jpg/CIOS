# Bounded evidence resolution

Baseline is [#720’s approved tree](https://github.com/rdidale-jpg/CIOS/pull/720) integrated at `ec6249a236166c9d0fd388febd46910ca5242966`. [Post-merge CI passed](https://github.com/rdidale-jpg/CIOS/actions/runs/45157419015). [Evaluation criteria](criteria.md) were committed before the first proof run.

## Reproduce

```sh
printf '%s\n' '["lloyds-banking-group-plc","bt-group-plc","arm-holdings-plc","easyjet-plc"]' >/tmp/resolution-commission.json
python -m tools.research.initial_factory /tmp/resolution-commission.json --discover --extract-body /tmp/resolution-discovery
python -m tools.research.factory_investigation /tmp/resolution-discovery/discovery.json
CIOS_VERIFIED_ROUTE_OUTPUT=/tmp/resolution-routes python -m pytest -q \
  tests/test_flora_investigation.py tests/test_flora_verified_factory.py
PYTHONPATH=. python docs/research/initial-factory/verified/browser.py /tmp/resolution-routes --output /tmp/resolution-previews
```

The CLI accepts the existing owner lifecycle envelope as `--source-state PATH`. With it, exact current URL and digest pairs govern factual re-evaluation, and expressly inactive URLs are skipped unless another revision is current. Without it the report uses freshly retrieved revisions for offline factual assessment. Neither mode grants Source reuse, qualifies publication or writes an approval.

The investigator routes the scoped original candidate to an allowlisted primary publisher index. It searches for topic-matching links, deduplicates tracking URLs, rejects cross-origin links and follows at most two originals. The budget is three reads per enterprise, two MiB per response, the existing 12-second timeout, with zero paid search calls and no redirects. Four enterprises can be commissioned in a run. Exhaustion or unavailable sources leave the candidate without new verified support.

The only automatic positive event binding in this increment is the dated Microsoft Cobalt 200 publisher notice. The investigator checks the exact product name, first-person publication wording in the body and publication date. A matched issuer statement about a future or completed activity is not guessed from general context. An exact contradictory statement blocks the decision. A later report of withdrawal is retained as a material update, without turning it into a contradiction about whether the original announcement occurred. The assurance engine receives the active exact revision and locator. It treats the direct notice as proof of its own publication event, with no independent proof of customer adoption or service outcomes. Entity/event resolution beyond that explicit scope remains open. This is deliberately a small search-and-resolution adapter over the existing extraction and assurance path.

## Live results on 23 November 2026

The [decision trail](live-proof.json) records search routes, original checksums and observed dated evidence. No selected answer article was supplied to the search. The reference answer for the Azure notice was already known from #718 and #720.

| Enterprise | Reads | Outcome |
| --- | ---: | --- |
| Lloyds | 2 | The AI index led to the issuer’s practical guide. This supplies related material. It does not independently establish how Lloyds carries out reviews of complex AI cases. |
| BT | 1 | The public NHS National Services Scotland newsroom index yielded no matching SWAN article within the bounded traversal. BT’s reported completion remains attributed. |
| Arm | 3 | The Azure blog index led to the original Microsoft Cobalt 200 notice and a separate engineering article. The dated body passage moved the announcement from withheld to verified. The engineering article did not establish the same dated event. |
| easyJet | 1 | The airline index linked to the same Starlink release already found by discovery. That duplicate adds no evidence of installation or independent delivery confirmation. |

Coverage was 4/4 scoped questions. Seven public responses were attempted, including three original linked documents after index reads. One of four factual decisions improved and three remained attributed. One of one known target notices was retrieved. This is retrieval coverage against a pre-existing positive reference. It is not a precision or recall benchmark for newsroom research. Different portals and dynamic indexes can lower recall. The controlled suite checks exact identity/perimeter, same-event date, body location, duplicated links, cross-origin rejection, contemporary disagreement, later updates, changed digest, missing/withdrawn support and repeatability. The controls do not estimate field accuracy. An independently labelled representative corpus is still missing. No qualifying precision, recall, corroboration rate or confidence interval is claimed for general newsroom research.

## Commercial and visual proof

Microsoft announced general availability. Arm’s reporting points to that same announcement. This establishes a concrete item to evaluate within Microsoft Azure, with supported regions, workload compatibility and customer adoption still open. A seller can ask which workloads and regions are in scope, and what portability evidence a buyer needs. No requirement, procurement action, sales opportunity or relationship is inferred from the notice.

The existing isolated Blueprint proof loads the newly recovered Microsoft digest for the exact Arm fixture, then uses its existing test-only Source state, scope and Blueprint approval path. Withdrawal removes eligibility and the Arm card. Tests check that an unauthorised viewer cannot see it and that the isolated run produces no Pipeline record. Lloyds, BT and easyJet previews remain comparisons using prior accepted, attributed fixtures. Nothing from those three new investigations was automatically accepted.

| View | Desktop | iPad portrait | iPad landscape |
| --- | --- | --- | --- |
| Lloyds Forces | [Desktop](previews/lloyds-banking-group-plc-route-desktop.jpg) | [Portrait](previews/lloyds-banking-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/lloyds-banking-group-plc-route-ipad-landscape.jpg) |
| BT Canvas | [Desktop](previews/bt-group-plc-route-desktop.jpg) | [Portrait](previews/bt-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/bt-group-plc-route-ipad-landscape.jpg) |
| Arm Landscape | [Desktop](previews/arm-holdings-plc-route-desktop.jpg) | [Portrait](previews/arm-holdings-plc-route-ipad-portrait.jpg) | [Landscape](previews/arm-holdings-plc-route-ipad-landscape.jpg) |
| easyJet Inside | [Desktop](previews/easyjet-plc-route-desktop.jpg) | [Portrait](previews/easyjet-plc-route-ipad-portrait.jpg) | [Landscape](previews/easyjet-plc-route-ipad-landscape.jpg) |

The existing compact What’s changed components retain the artwork and make the fact visible before expansion. The status label identifies the publisher’s role. Users need two expansions to see the supporting source caveat. The browser proof covers keyboard, simulated touch and layout bounds in Chromium. Physical iPad and Safari remain open.

## Readiness and owner decisions

Factory v1.0 remains incomplete. This increment automates retrieval and one scoped positive match. It does not establish broad recall, party or event resolution, independent corroboration, or routine automatic qualification across sectors. Better index discovery and multiple independently bound primary sources are the next technical gaps. A separately labelled reference corpus and thresholds would measure the missing capabilities. Future operation still requires explicit Source and lifecycle decisions, an approved publication audience, scoped workspace access and existing Blueprint approver/executor authority. Lloyds §2 and §5, BT and easyJet Source limits, and Financial authority are unchanged. No standing grant, recurring run, production data change, publication, deployment or Pipeline activity is included.
