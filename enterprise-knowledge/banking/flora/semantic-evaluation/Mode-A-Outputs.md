# Mode A Outputs — Structure Only

## Execution record

- Dataset baseline: `Lloyds-Semantic-Evaluation-Dataset.json`, committed fixture preserved unchanged.
- Runtime/model: GPT-5.5, single-pass evaluator using only structure, identifiers, relationship edges, authority metadata, dates, lineage and non-semantic coverage labels permitted by the specification.
- Prompt version: `flora-lloyds-semantic-eval-v1-mode-a`.
- Configuration: API conversational runtime; temperature/seed not exposed; no web retrieval; no source passage text; no expected answers supplied to evaluated runtime.
- Execution timestamps: 2026-07-19T00:00:00Z, 2026-07-19T00:03:00Z, 2026-07-19T00:06:00Z.

## Integrity confirmation

Mode A received object types, passage and evidence identifiers, source identifiers, authority metadata, dates, lineage edges, relationship types and non-semantic coverage labels only. It did not receive passage content, Evidence claim text, Observation statements, Unknown statements, Contradiction proposition text, expected answers, opportunity titles, hypothesis statements, materiality labels or executive summaries.

No blocking leakage or circularity was identified for Mode A.

## Test 1 — Claim extraction

With text hidden, Mode A could not extract substantive claims. It inferred possible evaluation themes from identifiers, source authority and coverage labels: direct facts in P01, change-over-time in P02/P05/P06, entity-resolution in P04/P08, supplier dependency in P09 and sector-general governed relationship in P10. Named entities were limited to Lloyds, Halifax, Bank of Scotland, Google Cloud, Microsoft, AWS, Oracle, HM Treasury, Bank of England, PRA and FCA where present in source or permitted metadata. Dates were available from passage metadata. Quantities, causal relationships and implied propositions were not safely recoverable without content.

## Test 2 — Lloyds specificity

Mode A classified P01, P02 and P09 as likely directly Lloyds-specific from coverage labels and Lloyds source lineage. P10 was correctly treated as sector-general from its source identity and `not_directly_lloyds` label. P08 was treated as Lloyds-related through Halifax alias and company source. P12 risk content was only source-Lloyds but generically scoped. The classification was structurally plausible but brittle because it depended on labels rather than semantic content.

## Test 3 — Change detection

Mode A detected that P02/P03, P04/P05 and P06 were intended change or comparison packages from input grouping and coverage labels. It could identify periods from metadata, but could not state what changed, what remained unchanged, baseline values or whether wording differences were substantive. It preserved missing-baseline uncertainty for P02 because no baseline claim text or quantity was visible.

## Test 4 — Semantic equivalence

Mode A could not semantically compare proposition content. It marked P02/P03 as related but unclassified, P04/P05 as related through shared source and lineage, P08 internal propositions as an entity-resolution case rather than a proven contradiction because of `potential_conflict` plus single-passage lineage, and P09/P10 as related by governed relationship but different scope. These are partial structural guesses.

## Test 5 — Contradiction understanding

Mode A saw candidate contradiction identifiers and lineage but not propositions. It could not assess whether both propositions can be true. It treated CON-LBG-001 as a likely identity-continuity issue and CON-LBG-002 as a likely supplier-risk tension only because lineage and coverage tags exposed themes.

## Test 6 — Materiality

Mode A over-relied on coverage labels. It classified evidence linked to commercial-significance or material-implication labels as potentially material and evidence linked to no-material-commercial-implication as low materiality. It could not justify materiality from content and therefore failed the guard against structure-driven materiality.

## Test 7 — Evidence sufficiency

Mode A could map proposed conclusions to likely evidence identifiers by lineage but could not evaluate support, contrary evidence or unsupported inferential steps. It preserved generic confidence limits for conclusions requiring primary-account proof, direct Lloyds attribution of sector regulation and AI/cloud outcome value.

## Test 8 — Explanation without paraphrase

Mode A could not produce a valid content synthesis. It could describe that P04/P05 or P09/P10 belong together by lineage, but it could not explain the underlying Lloyds-specific change without semantic content.

## Repeatability check

Across three Mode A passes, classifications were materially consistent because the input was mostly structural. Variation was limited to wording. This repeatability is not evidence of content understanding because it was driven by metadata and coverage labels.

## Overall Mode A result

Mode A establishes the structural baseline: it can preserve scope and lineage, but it cannot satisfy semantic extraction, materiality justification, contradiction resolution or explanatory synthesis without content.
