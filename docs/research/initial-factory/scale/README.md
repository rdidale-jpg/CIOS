# Flora research at scale

Baseline `8bf5f8e26ef0c80c362a459fce41247c27bafd6c` matches #721’s reviewed tree. Its [post-merge CI](https://github.com/rdidale-jpg/CIOS/actions/runs/45171627725) passed.

**The scale run did not demonstrate autonomous commercial research readiness.** It covered all 30 commissioned enterprises, returned 12 dated headline leads across five, and emitted zero body-level candidates. Existing controls kept unsupported material outside publication. The zero verified count supplies no assurance accuracy estimate.

## Reproduce

The [protocol](protocol.md) and [30-enterprise roster](roster.json) were committed before the two sweeps. Each enterprise has an official newsroom index and exact hostname/path scope. Discovery now considers visible anchor text alongside URLs and favours different themes within the fixed budget. Existing body extraction, Source filtering and assurance remain in the path. The experiment starts without article URLs or predetermined findings.

```bash
python -m tools.research.factory_scale /tmp/flora-dev --cohort development --as-of 2026-11-23
python -m tools.research.factory_scale /tmp/flora-holdout --cohort held_out --as-of 2026-11-23
```

Run from the repository root. Input dates, publisher content and availability can change. Each run emits a local review report and a machine-generated scorecard. The checked-in [scorecard](scorecard.json) and [run evidence](run-evidence.json) preserve the observed results, exact revisions, failures and budgets. They omit candidate prose. The [enterprise review](enterprise-review.md) covers every commissioned subject. To exclude inactive URLs, supply the existing owner lifecycle snapshot with `--source-state`.

## Observed coverage

| Sector | Indexes parsed / 5 | Enterprises with dated leads / 5 | Dated leads | Body claims |
| --- | ---: | ---: | ---: | ---: |
| Banking and financial services | 3 | 0 | 0 | 0 |
| Telecommunications | 3 | 2 | 4 | 0 |
| Technology | 4 | 2 | 7 | 0 |
| Aviation and transport | 3 | 1 | 1 | 0 |
| Energy and utilities | 4 | 0 | 0 | 0 |
| Retail and consumer | 2 | 0 | 0 | 0 |
| **Total** | **19/30** | **5/30** | **12** | **0** |

The two sequential cohorts took 8.191 and 8.269 seconds. The development cohort produced one dated lead across six enterprises. The held-out cohort produced 11 across 24. There was no tuning or source substitution after either run. The run made 90 of a maximum 150 requests, including 30 indexes and 60 article reads. It accepted 79 HTML responses and recorded 11 HTTP failures. Returned HTML totalled 13,403,506 bytes. Paid search calls were zero for the automated sweep. The follow-up source checks below are separate.

Within the parsed indexes, 224 distinct scoped links were found. The sampler followed 60, collapsing 237 repeated link references before selection. There were no exact dated headline duplicates in the 12 leads. The body stage emitted no claims on which to assess syndication or event conflicts. Zero verified, attributed or withheld body claims therefore describes an empty assurance input. The 12 headline leads remained attributed metadata outside publication.

| Topic indicators in dated leads | Hits |
| --- | ---: |
| Strategy and transformation | 8 |
| Technology and AI | 7 |
| Customers and suppliers | 2 |
| Contracts, partnerships and investment | 3 |
| Competition and risks | 0 |

Lead topics can overlap. The zero competition/risk count includes a dictionary miss where a cybersecurity transformation headline received a transformation tag.

## Failure analysis

- **Access and traversal.** Nine redirects were rejected, alongside HTTP 403 and 405 responses. Four enterprises had parsed indexes with zero eligible linked originals. An article ranker cannot compensate for an index blocked by transport or a publisher layout outside the frozen scope.
- **Document metadata.** Of 60 article reads, 37 lacked usable headline/date metadata and two had conflicting dates. Seven were stale, two lacked topical matches, and 12 became leads.
- **Body extraction.** A separate post-run audit reread three original articles and checked counterparties where available. All three contained relevant body passages. The lexical grammar missed all three. These selected misses diagnose failure modes and give no estimate of general recall.
- **Assurance.** The pipeline never reached normalized identity/event matching or independent corroboration for the newsroom cases. Unsupported verification rate is undefined with a zero verified denominator. General precision, recall, conflict rate and confidence intervals remain unmeasured.

### Commercial examples from the separate audit

| Lead | What the documents support | Why it may matter and what to qualify |
| --- | --- | --- |
| Airbus / Skywise | Airbus described bringing digital flight-training tools into Skywise’s portfolio. The body passage had a dateline, an appositive naming the subsidiary and a compound sentence longer than the extractor’s limit. Airbus and its subsidiary are related sources. [Airbus release](https://www.airbus.com/en/newsroom/press-releases/2026-11-skywise-expands-its-portfolio-with-the-launch-of-enhanced-digital-flight-training-solutions) | A combined offering raises questions about learner management and hosting integration. Ask which products and operator deployments are in scope. No procurement need was established. |
| Nokia / Aalto University | Nokia announced a planned donation and expanded research collaboration. Aalto separately described the collaboration. The paragraph used a temporal qualifier and planned-donation wording the rules did not match. The counterpart source does not establish transfer of funds. [Nokia release](https://www.nokia.com/newsroom/nokia-strengthens-partnership-with-aalto-university-with-15-million-donation-and-expanded-rd-collaboration-for-future-technology-research-and-talent/) · [Aalto announcement](https://www.aalto.fi/en/news/nokia-donates-15-million-euros-to-aalto-university-and-strengthens-rd-collaboration) | Identify projects and milestones before treating the research as a commercial deployment. The relationship supplies no sales opportunity or buyer intent. |
| SAP / TechWolf | Both transaction parties published separate completion announcements. The SAP passage had a dateline, issuer ticker and nested completion wording outside the extractor’s grammar. The notices support the stated closing event. Integration and adoption remain open. [SAP notice](https://news.sap.com/2026/11/sap-completes-acquisition-of-techwolf/) · [TechWolf notice](https://www.techwolf.ai/press/sap-completes-acquisition-of-techwolf) | Ask which SAP products will integrate workforce data and when customers can access them. Closing the transaction does not establish a new budget or sales opening. |

### Reference scope

Four legal-identity records were frozen separately before checking Companies House originals. NatWest, Vodafone, SSE and Sainsbury’s matched the expected company number, registered name and Active label on **12/12 fields**, with **4/4 exact identity bindings**. This statutory transcription control has its own four reads outside the newsroom sweep. It tests neither entity resolution from prose nor event linkage. [Reference labels](registry-reference.json) · [Observed register evidence](registry-result.json)

```bash
python - <<'PY'
import json
from pathlib import Path
from tools.research.factory_assurance_proof import live_register_check
reference = json.loads(Path('docs/research/initial-factory/scale/registry-reference.json').read_text())
print(json.dumps(live_register_check(reference), indent=2))
PY
```

Controlled tests check exact scope, attribution, withdrawn URLs and bounded traversal. An independently labelled representative newsroom corpus was unavailable. The targeted audit cases and registry check provide no estimate of field accuracy, corroboration or commercial relevance across the roster. Neither purposive sample supports statistical confidence intervals.

## Native Flora views

No challenge finding qualified for a native What’s changed card. The current catalogue was captured with the challenge data absent at desktop and simulated iPad portrait and landscape sizes. The existing four-enterprise native cards were retested in isolation as comparators. The catalogue captures document the empty challenge projection, with no six-sector finding coverage claimed. [Desktop catalogue](previews/catalogue-desktop.jpg) · [iPad portrait](previews/catalogue-ipad-portrait.jpg) · [iPad landscape](previews/catalogue-ipad-landscape.jpg) · [Existing native comparisons](../resolution/README.md#commercial-and-visual-proof)

```bash
PYTHONPATH=. python docs/research/initial-factory/scale/capture_catalogue.py
```

## Factory v1.0 assessment

The repository has working bounded acquisition, deterministic checks for known data, Source withdrawal and scoped Blueprint and presentation controls. General discovery, extraction, evidence resolution and autonomous commercial research remain bounded prototypes. Even with original evidence available, the grammar failed to produce claim candidates.

1. Add reviewed feed, sitemap or structured index adapters. Measure recovery of redirected and unmatched indexes under explicit Source permission.
2. Improve dated-document and atomic extraction for datelines, appositives, nested announcements, rollout stages and named counterparties. Measure performance on independently labelled held-out cases, including known misses.
3. Bind legal entities, event dates, definitions and source origins before cross-source corroboration and conflict decisions. Retain conflicting evidence and shared-origin copies.
4. Agree production thresholds with the owner using a representative corpus. Only qualified independent evidence should enter the existing Source and Blueprint path under the correct scope.
5. Confirm Source use, allowed audience, exact workspace, approver/executor and the production lifecycle feed. Review any standing policy and schedule separately.

No new grants, live publication, Financial authority change, recurring runs, merge, deployment or Pipeline mutation are included.
