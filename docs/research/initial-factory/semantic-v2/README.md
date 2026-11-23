# Flora semantic extraction v2

This increment recovers three known newsroom misses in the existing candidate path. It finds some unfamiliar acquisition facts. Broad generalisation remains unproven, and Factory v1.0 should stay out of autonomous production research.

## What changed

- First-person partnership expansion binds “We” to the configured newsroom issuer only when the source’s structured organisation name and HTTPS host agree. Quoted paragraphs and unbound pronouns abstain.
- Delivery under an existing partnership keeps its reported in-progress status. A signed agreement to acquire stays planned. A reported completion uses its existing separate status.
- A nominal migration links a company reference to the named actor in the immediately preceding, unambiguous sentence. Both source spans stay bound to the same captured revision. The existing assurance screen checks the actor span as well as the event span.
- Dates in both publisher dateline formats are retained. Amounts and modifiers already captured by #723 stay attached to their own candidate. One paragraph can yield distinct claims with independent locations.

ADR-010 supports closest adequate structured and local extraction. ADR-014 and ADR-024 retain evidence and verification with their existing owners. The existing Source lifecycle, workspace permissions and Blueprint approval remain independent from extraction. No Financial or Pipeline paths changed. [Baseline #723 main CI](https://github.com/rdidale-jpg/CIOS/actions/runs/45187990875) · [#722 scale](../scale/README.md) · [#723 recovery](../semantic/README.md)

## Accuracy and scope

The first label commit froze 20 previously unlabelled publisher documents, with one targeted paragraph per document. The existing three known misses were development examples for this increment. After inspecting the first unfamiliar run, five additional primary-source confirmation paragraphs were frozen before the follow-up changes. The UPS dateline from the initial held-out evaluation informed the follow-up, so its recovery is diagnostic and supplies no clean held-out gain. The two Microsoft confirmation documents exercise the declared acquisition pattern against original releases. The three quote negatives include NTT DATA and ServiceNow versions of one release, so they are related controls.

Labels describe exact passage-level issuer assertions, dates, event status and parties. They came from reading public originals independently of extractor output. There was one annotator and no separate peer labelling. The confirmation set was pattern-selected and is small. These denominators cover the specified passages only. [Frozen labels and revision hashes](reference.json) · [Per-passage results](results.json)

| Evaluation | Expected | #723 exact correct / output | v2 exact correct / output | v2 recall |
| --- | ---: | ---: | ---: | ---: |
| Unfamiliar development | 2 | 0/1 | 0/0 | 0/2 |
| Unfamiliar validation | 4 | 0/1 | 0/1 | 0/4 |
| Initial unfamiliar held-out | 9 | 0/2 | 1/3 after iteration | 1/9 after iteration |
| Fresh targeted confirmation | 2 | 0/1 | 2/3 | 2/2 |
| Known scale passages | 9 | 6/6 | 9/9 | 9/9 |

Across the unfamiliar corpus, v2 matched actor, counterparty, event, date, status, target and amount on the three exact correct predictions. All seven predictions mapped to the recorded publisher and document revision. That is traceability, with no legal entity resolution implied. The other four predictions are inherited errors in the selected passages. Two joint aircraft-order announcements attributed the announcement rather than the buyer’s specific order. One facility opening used the generic announcement category and included a temporal adverb in the actor. One speculative supplier phrase was misclassified as a partnership. Commercially material misses include an expanded custody relationship, a multi-party technical collaboration, two fleet orders and a planned engineering rollout. These errors warrant keeping generic fallback outputs away from independent factual verification.

## Method comparison

| Method | Evidence on identical bytes |
| --- | --- |
| A. Bounded deterministic extraction | 9/9 known claims, 2/3 targeted confirmation precision and 2/2 targeted recall. Actor, event and revision provenance are inspectable. Local parser pass took about half a second for the 25 documents. Zero model calls. |
| B. Semantic model | The existing static provider is a fixture. The external reasoning provider serves a governed brief and the Financial provider has a separate document contract. Neither supplies an authorised no-cost newsroom model run. Accuracy, traceability, cost and repeatability are unmeasured. |
| C. Semantic model plus deterministic evidence gates | No model arm was available. The in-scope combination of A and the existing deterministic gates left three scale candidates issuer-attributed and six withheld. Zero candidates became verified or publishable. |

Keep A with the existing evidence checks for bounded experiments. This conclusion follows from the observed gains and remaining errors. A future model comparison needs an explicitly authorised bounded provider and the same independently reviewed source set. The current elapsed measurements are one replay per version and timing is not a throughput guarantee.

## Paired scale proof

All three implementations replayed identical SHA-checked bytes from the #723 capture of the frozen #722 cohort. The original #722 trial recorded the same 12 dated URLs and counts. Five of its 12 dated hashes match the capture used here. Consequently the paired results isolate code differences within one archive and the historical trial is a coverage reference. No original sources were substituted between paired runs.

| Paired metric | #722 | #723 | v2 |
| --- | ---: | ---: | ---: |
| Enterprises / scopes | 30 | 30 | 30 |
| Indexes / originals / dated leads | 19 / 60 / 12 | 19 / 60 / 12 | 19 / 60 / 12 |
| Enterprises with body candidates | 0 | 4 | 5 |
| Labelled correct body candidates | 0 | 6 | 9 |
| Unmatched scale predictions in labelled paragraphs | 0 | 0 | 0 |
| Issuer-attributed / withheld / verified | 0 / 0 / 0 | 2 / 4 / 0 | 3 / 6 / 0 |

The three additional scale candidates are the original known misses, so they demonstrate recovery rather than held-out generalisation. The headline denominator stayed constant, including 11 inaccessible index responses. Source and acquisition coverage did not increase.

### Technical critique

The subject checks trade recall for evidence integrity. Structured metadata is corroborating publisher context within a previously scoped origin. It cannot establish legal identity or support a new Source permission. The narrow antecedent rule abstains on competing named entities. Its legitimate stage interpretation remains subject to existing atomicity and review. Legacy generic announcements still produce actor/event errors on complex orders. The next engineering step is scoped joint-announcement parsing with explicit buyer, vendor and order-stage roles, tested against new negative examples. A wider issuer-independent sample and separate annotator are needed before claiming broad accuracy.

### Commercial critique

- Anthropic describes expansion of an existing GSA relationship. The useful sales question is which eligible agencies, procurement channels and delivery stages are covered. Expanded access does not evidence a buying decision.
- T‑Mobile reports activating an existing Formula 1 partnership. Ask which venues and network operations are covered before treating the development as a wider rollout. The source does not establish a fresh award.
- SAP reports Takeda moving toward Cloud ERP. Separate the reported migration from a completed cutover. Next questions are which business processes, milestones and providers are in scope.
- UPS reported a signed acquisition agreement for Smartways Logistics. A future coverage assessment should distinguish signing, approvals and close before discussing integration. The direct corpus check did not admit this dated article into the scale pipeline.

These examples use the cited revisions in the results. They establish no Pipeline opportunity and do not require owner fact-checking. No eligible native view change arose.

## Reproduce

Use the retained private #723 capture with its URL-keyed manifests and the supplementary capture. The original response bodies stay outside the repository. To recreate a supplementary archive, use `acquisition(directory, True)` from `tools.research.factory_semantic_benchmark` with `MAX_BYTES` from `factory_scale` and the confirmation URLs in the reference. Revision mismatches stay out of scored denominators.

```bash
repo=$PWD
script="$repo/tools/research/factory_semantic_v2_benchmark.py"
ref="$repo/docs/research/initial-factory/semantic-v2/reference.json"
known="$repo/docs/research/initial-factory/semantic/reference.json"
capture=/tmp/flora-semantic
supplement=/tmp/flora-semantic-v2/supplement
for sha in 78cfe07192341b37a17d6e657e7110ef8b5899ef d14f93b975f8ffc9bcc4dd7b81ead7a7696115d0; do
    git worktree add --detach "/tmp/flora-v2-$sha" "$sha"
    (cd "/tmp/flora-v2-$sha" && PYTHONPATH="$PWD:$repo" python "$script"         "$capture" "$ref" "$known" "/tmp/$sha.json" --additional-capture "$supplement")
done
python "$script" "$capture" "$ref" "$known" /tmp/flora-v2.json --additional-capture "$supplement"
```
