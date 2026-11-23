# Flora semantic extraction recovery

This increment recovers three commercial developments missed by the #722 scale challenge. It improves extraction on a small held-out sample. Factory v1.0 still lacks enough coverage and independent evidence resolution to operate autonomously at scale.

## Baseline and root causes

The starting tree is #722’s merge at `78cfe07192341b37a17d6e657e7110ef8b5899ef`. See the [scale protocol and scorecard](../scale/README.md) and [post-merge CI](https://github.com/rdidale-jpg/CIOS/actions/runs/45179871280).

| Original miss | What failed | Recovery |
| --- | --- | --- |
| Airbus / Skywise | The dateline was read as part of the subject. The description of Skywise as an Airbus digital services company and the long product list exceeded the single-sentence grammar. | Separate the dateline and named actor, bind the exact portfolio-expansion clause and leave the product list in source context. |
| Nokia / Aalto University | One paragraph contains a proposed donation and an ongoing research commitment. The old grammar had no expression for either combination of modality, activity, amount and counterparty. | Extract the planned €1.5m donation and a distinct commitment to research collaboration with projects worth approximately €1.3m annually. |
| SAP / TechWolf | The em dash, exchange ticker and announcement wrapper obscured the reported acquisition close. | Anchor the original source span, bind the announcement’s subject to the nested pronoun and classify the acquisition as reported completed. |

## Architecture and controls

The existing newsroom extractor adds bounded local parsing of clause structure. The scope includes datelines, exchange tickers, entity appositives, explicit subjects after semicolons, announcement wrappers, and narrow typed events with dates and qualified amounts. It retains distinct source claims with a revision hash and an exact character span within the normalized HTML paragraph. The existing assurance screen rereads that span against the original bytes. The extractor produces textual actor and counterparty mentions. Resolving those mentions to legal enterprises and mapping event identities still belong to the existing owners.

ADR-010 prefers structured acquisition and bounded interpretation. ADR-014 and ADR-024 preserve deterministic evidence checks and treat semantic interpretations as candidate data. The existing Financial document provider and governed reasoning provider serve their own contracts. This sprint uses local clause parsing after the existing deterministic metadata checks, with zero external model calls. A future semantic model should propose typed, source-bounded spans for the same validation and should be evaluated under its own cost and accuracy budget. No provider binding or cost approval was added here.

Existing Source scope, digest, lifecycle exclusion and review windows stay in force. Competing qualified values surface as differences within existing grouped events. Source, Evidence, canonical Observation, Enterprise Model, workspace and Blueprint promotion authority remain with their established owners. The run used no execution approval, public release or Pipeline writes.

## Accuracy benchmark

The [reference](reference.json) was manually grounded in exact public publisher revisions before implementation, independently of extractor output. The known development documents are separate from held-out documents. One T‑Mobile date transcription was corrected against its full-month source dateline after the first comparison. This is a selected, single-reviewer paragraph sample across aviation, technology and telecom. There is no independent second annotation or representative population estimate. Negative labels cover four paragraphs with no target event in scope.

| Paragraph sample | Baseline recovered | Recovered | Exact precision on predictions | Exact recall |
| --- | ---: | ---: | ---: | ---: |
| 3 known development paragraphs, 4 expected claims | 0/4 | 4/4 | 4/4 | 4/4 |
| 9 held-out paragraphs, 5 expected claims | 0/5 | 2/5 | 2/2 | 2/5 |

Baseline precision is undefined because it made no predictions. Across six predictions, all six matched the labelled actor, target, event, milestone, explicit date mentions, amount and counterparty fields, and publisher/revision attribution. These are textual checks. Legal entity resolution, cross-document event matching and independent corroboration were outside those denominators. Zero mismatched predictions among six measures this sample only. With zero independently verified events, the unsupported verification rate is undefined.

The three held-out misses are a first-person partnership expansion, delivery under an existing partnership, and a migration expressed as a nominal phrase. The bounded extractor abstains on those forms. It also leaves secondary product lists, vague future integration benefits and URLs without acceptable dates outside these candidates. The next corrective increment should test explicit active-issuer context and project milestones against freshly labelled documents with independently reviewed negative cases.

## Paired scale rerun

The original roster, six development and 24 held-out enterprises, four-article budget, URL scope, five themes, date cutoff and discovery definitions were retained. The two versions read the same files in the primary replay. The separate fresh capture processed the cohorts sequentially under the original access policy and reproduced the same counts. Six reference revisions differed in that second capture and were excluded from its accuracy denominators. The [results](results.json) retain counts, per-paragraph outcomes and exact hashes. Original publisher responses stay in the operator’s local capture.

| Metric | #722 challenge | Recovery paired baseline | Recovery paired replay |
| --- | ---: | ---: | ---: |
| Enterprises attempted | 30 | 30 | 30 |
| Indexes read | 19 | 19 | 19 |
| Articles read | 60 | 60 | 60 |
| Dated leads | 12 | 12 | 12 |
| Enterprises with body findings | 0 | 0 | 4 |
| Body candidates | 0 | 0 | 6 |
| Attributed only / withheld / verified | 0 / 0 / 0 | 0 / 0 / 0 | 2 / 4 / 0 |

Each capture made 90 requests and read roughly 13.4 MB. The separate fresh capture took 19.284 seconds across both cohorts. Replay wall time is recorded separately and is a single run, so it supplies no reliable estimate of the CPU overhead. All six predictions on the labelled replay were within the labelled passages. The output increase is an extraction gain under identical access. It does not fix the 11 index errors, metadata coverage or lack of independent verification.

## Commercial reading and remaining questions

| Finding | Attributed commercial significance and qualification |
| --- | --- |
| Skywise announced the portfolio expansion on 2 November 2026. The publisher describes Skywise as an Airbus digital services company. | The combined training offer could change hosting and learner administration. Ask which training products moved and which operators already use them. No buying decision was evidenced. |
| Nokia announced a planned donation to Aalto and a separate ongoing research commitment. | Distinguish university research from funded commercial deployment. Ask which projects, milestones and participants fall within the collaboration. Aalto’s announcement supports the collaboration, with payment and execution outside the proof. |
| SAP reported completing its TechWolf acquisition. | Track which workforce intelligence features SAP integrates and when customers can adopt them. Separate announcements by both transaction parties support the closing report, while adoption remains open. |
| SAP reported AstraZeneca’s migration to SAP Cloud ERP Private. | Ask which processes and rollout phases the migration covers. The source describes migration in progress. Delivery, additional supplier needs and spend remain open. |
| T‑Mobile reported publishing its cybersecurity transformation report. | Use the report to understand delivery priorities and questions about operating changes. Publication itself establishes no new procurement. |

The existing safety screen withheld the compound research commitment and three ticker-containing statements for its atomicity rules. These are reviewable excerpts. They cannot be published or used as accepted facts. The new code leaves visual components unchanged because the run yielded no newly eligible material for a native view.

## Reproduce

Use a clean baseline worktree, the recovery checkout, and a private capture directory. The first command acquires original publisher documents using the unmodified #722 roster. The other commands replay the same byte-checked responses. A fresh capture can contain changing publisher revisions. Labels with changed bytes remain unscored. Use the recorded hashes to distinguish a repeat from a revised-source experiment.

```bash
recovery=$PWD
git worktree add --detach /tmp/flora-semantic-baseline 78cfe07192341b37a17d6e657e7110ef8b5899ef
ref="$recovery/docs/research/initial-factory/semantic/reference.json"
script="$recovery/tools/research/factory_semantic_benchmark.py"
python -m tools.research.factory_semantic_benchmark /tmp/flora-capture /tmp/flora-live.json --read-live --as-of 2026-11-23
(cd /tmp/flora-semantic-baseline && PYTHONPATH="$PWD" python "$script" /tmp/flora-capture /tmp/flora-before.json --as-of 2026-11-23 --reference "$ref")
python -m tools.research.factory_semantic_benchmark /tmp/flora-capture /tmp/flora-after.json --as-of 2026-11-23
```

The next release criterion is reliable body-claim recovery on a larger held-out corpus, followed by independent source resolution and existing verification and publication checks. Authority for any later model spend or live operation requires a separate owner decision.
