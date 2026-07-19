# Mode B Outputs — Content Only

## Execution record

- Dataset baseline: `Lloyds-Semantic-Evaluation-Dataset.json`, committed fixture preserved unchanged.
- Runtime/model: GPT-5.5, content-only evaluator using source passages, minimal Lloyds identity, source dates and provenance.
- Prompt version: `flora-lloyds-semantic-eval-v1-mode-b`.
- Configuration: API conversational runtime; temperature/seed not exposed; no web retrieval; authored Observations, Unknown summaries, Contradiction summaries, Evidence claims, hypothesis language, materiality classifications and expected answers hidden.
- Execution timestamps: 2026-07-19T00:10:00Z, 2026-07-19T00:13:00Z, 2026-07-19T00:16:00Z.

## Integrity confirmation

Mode B received passage text, source identity, dates, provenance and permitted Lloyds aliases only. It did not receive authored Observations, Unknown summaries, Contradiction summaries, Evidence claim text, expected answers, opportunity titles, hypothesis statements, materiality labels or executive summaries.

No blocking leakage or circularity was identified for Mode B.

## Test 1 — Claim extraction

Mode B extracted explicit claims accurately from P01, P04, P08, P10 and P12. P01 yielded Lloyds scale quantities at 2025 year-end: 28m customers, 23.6m digitally active customers, £496.5bn deposits and £481.1bn loans. P04 yielded a structural-hedge mechanism: stable or less-rate-sensitive net liabilities, including personal current accounts, are covered by a £246bn Q1 2026 hedge balance and contributed to an increase. P08 separated Halifax app/brand migration from unchanged sort codes, account numbers and existing FSCS arrangements. P10 was extracted as UK financial-sector regulatory context for designated technology providers, not as a Lloyds finding. P12 was extracted as forward-looking risk language rather than evidence of an actual failure. Inferences were mostly bounded, though one pass used the phrase “technology dependency risk” without enough detail on criticality.

## Test 2 — Lloyds specificity

Mode B reliably separated directly Lloyds-specific passages from sector-general content. P10 was not classified as directly Lloyds-specific; it became relevant only if linked to Lloyds' Google Cloud use in P09. P11 blocked over-attribution of digital activity to primary-account primacy. P12 was treated as Lloyds disclosure language but generic in event status and not proof that a failure occurred.

## Test 3 — Change detection

Mode B identified app use up about 45% since 2021 and approximately 21.5m app users at 2025 year-end, but preserved the missing 2021 app-user baseline. It connected P03 to the 2025 mobile-account-opening share while noting this is not the same metric as app-user growth. For P04/P05, it identified structural hedge income rising from £1.2bn in Q1 2025 to £1.6bn in Q1 2026 and separated reported results from 2026/2027 expectations. For P06, it identified cost savings and productivity improvements since 2021, but did not infer net benefit, service quality or risk impact.

## Test 4 — Semantic equivalence

Mode B classified P02/P03 as compatible but distinct: one concerns app users and app-use growth; the other concerns mobile current-account openings in 2025. P04/P05 were compatible but distinct: one explains hedge balance and eligible liabilities; the other reports hedge income and forecasts. P08 contained no genuine contradiction because brand/app presentation can change while account identifiers and protection arrangements stay unchanged. P09/P10 were different scopes: Lloyds-specific Google Cloud usage versus sector-level CTP designation.

## Test 5 — Contradiction understanding

Mode B resolved CON-LBG-001 as not a contradiction: customer-facing brand/app migration and account-continuity arrangements can both be true. It resolved CON-LBG-002 as a tension rather than contradiction: Lloyds can report AI/cloud migration and simplification while also disclosing supplier, AI, cyber and technology operational risks. It demanded further evidence on workload criticality, control obligations, outages and migration sequencing before treating the tension as operational harm or control burden.

## Test 6 — Materiality

Mode B classified P01 as descriptive scale, P02/P03 as behavioural/digital signals, P04/P05 as commercially material because balances, personal current accounts, hedge income, year-on-year movement and forward earnings are connected, P06/P07 as operational and strategic signals with incomplete causality, P08 continuity details as low materiality unless tied to migration execution or customer trust outcomes, P09/P10 as potentially material supplier-control and AI-scale context, P11 as uncertainty guard and P12 as risk-factor context. Materiality was largely content-bound.

## Test 7 — Evidence sufficiency

Mode B rejected “digital activity proves current-account primacy” because the passages show digital use and mobile openings but explicitly lack salary-flow, direct-debit, main-bank or challenger-displacement evidence. It supported the structural-hedge income increase using P05. It rejected direct Lloyds attribution of the CTP designation because P10 is sector-level and only becomes Lloyds-relevant through P09. It supported the statement that Lloyds is applying AI/cloud at operational scale using P09, while preserving unknowns about outcome value, criticality and control burden using P10/P12.

## Test 8 — Explanation without paraphrase

Mode B produced a valid brief synthesis around structural hedge change: P04 explains why stable or less-rate-sensitive liabilities, including personal current accounts, matter to the hedge balance; P05 shows the associated income increase and forward expectation. The derived interpretation was that Lloyds' liability mix and rate environment created a commercially relevant earnings mechanism. Unknowns included durability, customer behaviour and capital-allocation use of the income. A competing interpretation was that income growth may reflect rate/back-book dynamics rather than strategic account primacy.

## Repeatability check

Across three Mode B passes, factual claims and classifications were materially consistent. Wording varied. One run over-compressed AI/cloud evidence into “dependency risk,” which was adjudicated as minor reasoning variation because it did not claim a failure or direct regulatory finding. No material inconsistency changed a test outcome.

## Overall Mode B result

Mode B materially outperformed Mode A on semantic extraction, specificity, change detection, contradiction understanding, evidence sufficiency and explanation. Weaknesses remained in explicit lineage discipline and systematic Unknown preservation because governed Unknown objects were hidden.
