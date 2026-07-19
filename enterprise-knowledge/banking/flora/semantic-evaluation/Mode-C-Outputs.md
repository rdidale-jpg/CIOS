# Mode C Outputs — Governed Content

## Execution record

- Dataset baseline: `Lloyds-Semantic-Evaluation-Dataset.json`, committed fixture preserved unchanged.
- Runtime/model: GPT-5.5, governed-content evaluator using passages, Evidence, Observations, Unknowns, candidate Contradictions, lineage, authority and freshness metadata.
- Prompt version: `flora-lloyds-semantic-eval-v1-mode-c`.
- Configuration: API conversational runtime; temperature/seed not exposed; no web retrieval; opportunity titles, recommendations, executive summaries and expected answers hidden.
- Execution timestamps: 2026-07-19T00:20:00Z, 2026-07-19T00:23:00Z, 2026-07-19T00:26:00Z.

## Integrity confirmation

Mode C received governed content, Evidence, Observations, Unknowns, candidate Contradictions, lineage, authority and freshness metadata. It did not receive opportunity titles, materiality scores, recommendations, executive summaries or expected answers.

No blocking leakage or circularity was identified for Mode C. Because Observation statements are intentionally included in Mode C, Mode C results must be read as evidence-governed explanation performance rather than blind raw-content understanding.

## Test results

Mode C matched Mode B's substantive extractions and improved evidence discipline. It consistently separated passage fact, derived Evidence, Observation and inference; named Unknowns; and cited lineage for conclusions. It used OBS-LBG-001 to block primary-account overclaiming, OBS-LBG-002 to explain why deposit/hedge/NII evidence belongs together and OBS-LBG-003 to tie Lloyds' Google Cloud usage to sector CTP context without converting P10 into a direct Lloyds finding.

For claim extraction, Mode C preserved explicit claims from P01, P04, P08, P10 and P12 and used Evidence identifiers to group them without adding unsupported conclusions. For Lloyds specificity, it maintained strict scope boundaries, especially for P10. For change detection, it combined P02/P03, P04/P05 and P06 while preserving baseline and outcome unknowns. For semantic equivalence and contradiction understanding, it resolved P08 and CON-LBG-001 as identity/continuity rather than contradiction and CON-LBG-002 as transformation/risk tension rather than contradiction.

For materiality, Mode C gave the strongest answer: P05/EV-LBG-003/OBS-LBG-002 were commercially material because reported hedge income rose year-on-year and forward earnings guidance was tied to a Lloyds-specific liability mechanism; P08/EV-LBG-005 remained low materiality absent migration-outcome evidence; P09/P10/EV-LBG-006/OBS-LBG-003 were potentially material but bounded by UNK-LBG-003. For evidence sufficiency, it explicitly mapped conclusions to supporting Evidence, Observations, contrary Evidence, Unknowns and unsupported steps. For explanation without paraphrase, it explained why Evidence belongs together instead of restating labels.

## Repeatability check

Across three Mode C passes, factual claims, classifications and conclusions were materially consistent. Wording varied, but reasoning variation was limited to whether the AI/cloud package was labelled “potential commercial significance” or “operational signal with potential commercial significance.” Adjudication: wording variation, not a material semantic inconsistency.

## Overall Mode C result

Mode C materially outperformed Mode B on lineage discipline, Unknown preservation, contradiction framing and explainability. The improvement was not merely presentation: governed structures prevented over-attribution, forced explicit evidence demands and improved explanation of why Evidence belongs together.
