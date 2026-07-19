---
asset_id: "FLORA-LBG-SEM-EVAL-001"
title: "Content Understanding Evaluation Specification"
asset_type: "Evaluation Specification"
domain: "Banking"
status: "Proposed gate"
version: "0.1"
focus_object: "Lloyds Banking Group"
dataset: "LBG-SEM-EVAL-001"
---

# Content Understanding Evaluation Specification

## Gate question

This evaluation asks whether Flora can derive a defensible understanding of Lloyds Banking Group from governed source content and Observations, rather than converting object labels, relationship names or pre-written conclusions into prose.

The gate explicitly excludes the Increment 2 Explain user experience and excludes Recommendations.

## Evaluation artefacts

- Dataset: `Lloyds-Semantic-Evaluation-Dataset.json`.
- Blind tests: this file, section **Blind test cases**.
- Expected answers and rubric: this file, sections **Expected answer key** and **Review rubric**.
- Results, failure analysis, corpus adequacy and readiness decision: this file, sections **Evaluation results**, **Failure analysis**, **Corpus adequacy assessment** and **Increment 2 readiness decision**.

## Dataset adequacy

The Lloyds fixture contains twelve substantive passages from five documents. It covers primary company reporting, a primary company announcement, a primary supplier/AI announcement and public regulatory context. The fixture deliberately includes direct Lloyds facts, cross-time comparisons, entity-resolution cases, apparent tensions, sector-general material, incomplete evidence, low-materiality continuity details and potentially material Lloyds-specific implications.

The dataset should not be enlarged with opportunity documents, hypotheses or executive summaries for this gate. Authored Observations may be used only in Mode C and must remain inspectable through lineage.

## Blind evaluation design

Each test package must be rendered in three modes:

1. **Mode A — Structure Only:** object identifiers, object classes, authority, dates, lineage edges and relationship types. Passage text and authored Observation statements are hidden.
2. **Mode B — Content Only:** passage text, dates, source identity and permitted Lloyds aliases. Evidence claims, Observation statements, contradiction statuses, materiality cues and hypothesis language are hidden.
3. **Mode C — Governed Content:** passage text, derived Evidence, Observations, Unknowns, candidate Contradictions, authority and lineage. Opportunity titles, materiality scores and recommendations remain hidden.

A valid evaluation must show that Mode B improves over Mode A on substantive claim understanding, and Mode C improves over Mode B on uncertainty discipline, lineage and contradiction handling. If Mode A performs nearly as well as Mode C, the test is measuring structure rather than understanding.

## Required test cases

### Test 1 — Claim extraction

Input: one passage at a time, using passages P01, P04, P08, P10 and P12.

Required output:

- explicit claims;
- named entities;
- dates or periods;
- quantities;
- stated causal relationships;
- implied but unstated propositions;
- a clear boundary between explicit content and inference.

### Test 2 — Lloyds specificity

Input: claims extracted from P01 through P12.

Required classifications:

- directly about Lloyds;
- relevant to Lloyds by governed relationship;
- sector-general;
- competitor-specific;
- not safely attributable.

Specific guard: P10 is not directly Lloyds-specific. It becomes relevant to Lloyds only when linked to P09 through Lloyds' Google Cloud usage.

### Test 3 — Change detection

Input sets:

- P02 and P03 for digital/app/current-account-opening activity;
- P04 and P05 for structural hedge balance and income;
- P06 for cost and distribution productivity since 2021.

Required output:

- what changed;
- what did not change;
- period of comparison;
- supporting Evidence;
- missing baseline information;
- whether any wording difference is merely expression rather than substantive change.

### Test 4 — Semantic equivalence

Pairs:

- P02 vs P03: app usage growth and mobile account openings;
- P04 vs P05: hedge-eligible balances and hedge income;
- P08 internal propositions: rebrand/app migration versus unchanged account identifiers;
- P09 vs P10: Lloyds Google Cloud usage versus UK CTP designation.

Required classifications:

- same underlying claim;
- compatible but distinct claims;
- genuine contradiction;
- different scopes or periods;
- insufficient information.

### Test 5 — Contradiction understanding

Candidate contradictions:

- CON-LBG-001: Halifax brand/app migration versus unchanged customer identifiers and FSCS arrangements.
- CON-LBG-002: AI/cloud simplification activity versus supplier, AI, cyber and technology operational-risk disclosure.

Required output:

- proposition A;
- proposition B;
- whether both can be true;
- scope, time, audience or interpretation differences;
- resolving Evidence demand.

### Test 6 — Materiality

Input: all derived Evidence objects.

Required classifications:

- descriptive fact;
- operational signal;
- behavioural signal;
- strategic change;
- potential commercial significance.

Specific guard: materiality must be justified from content. P08 continuity of sort codes/account numbers is a low-materiality customer-continuity fact unless connected to migration execution or customer trust evidence. P05 is potentially commercially material because it contains structural hedge income, year-on-year comparison and forecast earnings.

### Test 7 — Evidence sufficiency

Proposed conclusions:

1. Lloyds' digital activity proves current-account primacy.
2. Lloyds' structural hedge income rose materially from Q1 2025 to Q1 2026.
3. Google Cloud CTP designation is directly a Lloyds-specific regulatory finding.
4. Lloyds is applying AI/cloud at operational scale, but outcome value and control burden remain incompletely evidenced.

Required output:

- supporting Evidence;
- supporting Observations;
- contrary Evidence;
- Unknowns;
- unsupported inferential steps;
- confidence limits.

### Test 8 — Explanation without paraphrase

Prompt: Produce a brief explanation of one Lloyds-specific change using at least two Evidence items.

Required output:

- synthesis of at least two Evidence items;
- why those Evidence items belong together;
- derived Observation;
- separation of fact and interpretation;
- at least one Unknown;
- competing interpretation;
- no source-language restatement.

## Expected answer key

- P01 supports direct Lloyds scale facts only; it does not prove strategy, growth quality or customer primacy.
- P02 supports app activity growth since 2021; it does not identify the 2021 app-user baseline.
- P03 supports mobile journey contribution to account openings; it does not prove retained primary relationships.
- P04 supports a Lloyds-specific link between stable/less rate-sensitive net liabilities, personal current accounts and structural hedge balance.
- P05 supports a quantitative Q1 2025 to Q1 2026 income increase and forward expectation for 2026 and 2027, but forecast statements must be separated from reported results.
- P06 supports operational productivity and cost-reduction signals since 2021; net benefit, service quality and risk impact remain unresolved.
- P07 supports investment activity and strategic priorities; it does not prove capital-allocation causality.
- P08 is an entity-resolution and customer-continuity case, not a contradiction.
- P09 directly concerns Lloyds' use of Google Cloud Vertex AI and migrated modelling systems.
- P10 is sector/regulatory context, not direct Lloyds evidence unless related to P09.
- P11 preserves the primary-account Unknown and blocks over-attribution.
- P12 is risk-factor evidence; it should not be treated as evidence that a failure occurred.

## Review rubric

Use two reviewers: one architecture reviewer and one commercially experienced reviewer familiar with strategic enterprise analysis. Score each category from 0 to 3.

| Category | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Factual correctness | Invents or misstates facts | Frequent unsupported additions | Mostly accurate with minor issues | Accurate and source-bounded |
| Lloyds specificity | Converts sector facts to Lloyds facts | Frequent scope leakage | Mostly preserves scope | Strict scope discipline |
| Semantic coherence | Lists facts without meaning | Weak linkage | Coherent but incomplete | Explains why claims belong together |
| Evidence discipline | No lineage | Partial lineage | Lineage mostly clear | Evidence, Observation and inference separated |
| Uncertainty treatment | Hides Unknowns | Mentions uncertainty generically | Preserves key Unknowns | Specifies evidence demands and confidence limits |
| Commercial relevance | Uses prominence/object type as materiality | Overstates materiality | Supports materiality unevenly | Materiality follows content and implications |
| Absence of invented causality | Treats correlation as causality | Several causal overclaims | Minor causal slippage | No invented causality |

Pass threshold: average at least 2.4 across reviewers, no category below 2, and no failure condition triggered.

Reviewer disagreements must be logged with category, disputed output span, reviewer positions and final adjudication. A disagreement is not a failure unless it reveals unsupported evidence use or semantic overclaiming.

## Evaluation results

No semantic runtime execution result is present in this repository for this gate. The repository now contains a sufficient minimal fixture and a review protocol, but it does not contain scored Mode A/B/C outputs from Flora or signed human-review records.

Current evidence therefore supports only this result:

| Requirement | Status | Basis |
|---|---|---|
| Dataset with at least 10 passages across at least 3 documents | Pass | Dataset has 12 passages across 5 source documents. |
| Blind test cases | Pass | Eight required tests are specified with blind-mode controls. |
| Expected answer and review rubric | Pass | Answer key and scoring rubric are specified. |
| Mode A/B/C comparison results | Not demonstrated | No Flora run outputs are committed. |
| Two-reviewer human review | Not demonstrated | No reviewer scorecards or disagreement log are committed. |
| Architecture-readiness decision | Not ready | Evidence of runtime semantic capability is absent. |

## Failure analysis

Because Flora has not yet been run against the blind cases, observed runtime failures cannot be asserted. The readiness failure is evidential: the gate requires demonstrated semantic performance, not a plausible specification. The highest-risk failure modes to monitor are:

- Mode A performing well by repeating object labels or relationship names;
- converting P10 sector-regulatory content into a direct Lloyds fact;
- treating P08 as a contradiction instead of different aspects of brand identity and customer-account continuity;
- claiming P02/P03 prove primary-account primacy despite UNK-LBG-001;
- turning P07 investment activity into proven capital-allocation causality;
- treating P12 risk language as evidence of an actual operational failure.

## Corpus adequacy assessment

The corpus is adequate for a narrow Lloyds semantic gate because it contains enough governed content variety to expose the required distinctions. It is not adequate for production-grade Lloyds strategic explanation because important Evidence remains absent: salary-flow data, direct-debit concentration, main-bank status, competitor displacement, internal investment-governance allocation, migration sequence, service-quality effect, risk-control burden and independent AI value validation.

The corpus should be treated as an evaluation fixture, not as a complete Lloyds Enterprise Twin refresh.

## Increment 2 readiness decision

**Not ready — corpus or semantic runtime inadequate**

The reason is not that the fixture is too small for the gate. The reason is that no committed Flora Mode A/B/C outputs and no two-reviewer scores demonstrate the acceptance threshold. Proceeding to Increment 2 Evidence-Governed Explain would risk producing polished explanations before proving content understanding.
