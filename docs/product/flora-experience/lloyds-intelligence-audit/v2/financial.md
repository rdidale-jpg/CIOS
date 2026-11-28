# Lloyds financial integrity audit

Baseline `70319e7905e16eb845b91974ca0fda0aca593b8f`. All amounts below are GBP million at retained precision. The exact inputs are [H1 and Q3 EDGAR reporting packs](inventory.md#f), read through the [current public statement view](../../../../../cios/applications/flora/lloyds_financials.py) via `current` and `select`. Run [verify.py](verify.py) to retrieve them locally through the actual runtime owners and reproduce both bridges. Reported values below are credited to the retained filing. Changes, segment subtotal and residual arithmetic are calculated.

## H1 divisional contribution and separate nine-month result

| Arithmetic | Basis and period | GBP million |
| --- | --- | ---: |
| Retail | H1 2026 underlying segment profit | 2,256 |
| Commercial Banking | H1 2026 underlying segment profit | 1,425 |
| Insurance, Pensions and Investments | H1 2026 underlying segment profit | 245 |
| Three presented businesses | Calculated H1 underlying subtotal | 3,926 |
| Other | H1 2026 underlying segment profit | +289 |
| Group underlying | H1 2026 segment result | 4,215 |
| Restructuring effect from underlying to statutory | H1 2026 input is +34 in the reverse direction | −34 |
| Volatility and other effect from underlying to statutory | H1 2026 input is −112 in the reverse direction | +112 |
| Group statutory pretax | H1 2026 | 4,293 |
| Group statutory pretax | Q3 2026 single quarter | +2,332 |
| Group statutory pretax | Nine months to September 2026 | 6,625 |

`experience_landscape` places the nine-month Group result and H1 business profits in one pictorial economic mechanism. Though individually labelled, shared paths and hierarchy suggest they are compatible components. The executive opening repeats the Group total before the map, and the detailed reconciliation is a click away. Neither the legend nor the route link repairs the immediate implied contribution. Future presentation should lead with independent panels for 9M Group and H1 divisions or show the full H1 bridge and separately labelled Q3 increment. Never label the Q3 increment as having reported segment components from these records.

## Matched divisional requirement sample

This separate census requires three measures across two matching half-years for each of the three principal reporting businesses. The 18 applicable cells are all present in the retained public Financial projection, with a uniform underlying segment basis and ordinary divisional chart routes. This measures a specific data slice, not the completeness of divisional finances or operating intelligence.

| Reporting business | H1 2025 income after lease depreciation / operating costs / pretax | H1 2026 income after lease depreciation / operating costs / pretax |
| --- | ---: | ---: |
| Retail | 5,279 / −2,922 / 1,974 | 5,710 / −2,872 / 2,256 |
| Commercial Banking | 2,688 / −1,394 / 1,194 | 2,897 / −1,409 / 1,425 |
| Insurance, Pensions and Investments | 611 / −466 / 144 | 747 / −494 / 245 |

Income and operating costs alone do not form the segment pretax total. Follow the retained segment credits, impairments and other exact adjustments rather than allocating any arithmetical difference as a reported finance line.

## Nine-month movement

| Signed line | 9M 2025 | 9M 2026 | Calculated change |
| --- | ---: | ---: | ---: |
| Underlying net interest | 10,106 | 11,084 | +978 |
| Underlying other income | 4,526 | 4,996 | +470 |
| Lease depreciation | −1,075 | −1,261 | −186 |
| Underlying net income subtotal | 13,557 | 14,819 | +1,262 |
| Operating costs | −7,176 | −7,246 | −70 |
| Remediation | −912 | −61 | +851 |
| Credit impairment | −618 | −930 | −312 |
| Underlying profit subtotal | 4,851 | 6,582 | +1,731 |
| Restructuring | −16 | −51 | **−35** |
| Volatility and other | −157 | +94 | **+251** |
| Statutory pretax profit | 4,678 | 6,625 | **+1,947** |

The first four opening drivers sum to +1,731. The residual **+216** is calculated from **−35 restructuring and +251 volatility and other**. `executive_earnings` surfaces the total and four effects. `earnings` already presents all signed effects and suppresses its waterfall when exact inputs/basis/reconciliation fail. The fix belongs to opening/public presentation in a later authorised sprint. The full Financial engine does not need replacement.

## Wider model controls and open issues

- **Period and basis.** `current` and `select` index report perimeter, metric and exact period or as-at date; signed bridges validate historical match and statutory/underlying sequence. UI juxtaposition can still mislead, and ordinary bar selectors do not assert every pair's bespoke comparable accounting definition.
- **Currency and units.** Signed ledgers enforce GBP millions; rendered billion labels are scaled display, not additional facts. Maintain sign, rounding and unit in chart labels and evidence. Show Central/Other and underlying-to-statutory adjustments explicitly. Central items or eliminations beyond the declared bridge cannot be imputed.
- **Stocks and flows.** Deposits, loans and capital are dated stocks or as-at ratios. Net income, profit, costs and cash flow are period flows. Do not aggregate across unlike units or imply a funding balance is a period revenue component. Default total or concentration views must expose the denominator.
- **History.** Retained quarterly, annual and H1 observations support bounded time series. Keep accounting definition, effective date, issue and restatement history; a matching period label alone gives no proof of comparable accounting changes. No exhaustive historic original-vs-restatement reconciliation was established across all retained historic Twin and new EDGAR rows.
- **Targets.** FY26 full-year guidance versus 9M 49.3% cost/income and 17.9% RoTE is a progress checkpoint, not measured year-end achievement. The longer-term below-45% target and about £2bn gross savings expectation differ from delivered net cash, structural earnings and investable budget. Preserve version and target status across views.
- **Consistency and withdrawal.** A common typed view underlies detail; opening selection and legacy curated excerpts can still diverge by row and rounding. Prefer same financial result reference and contrast-safe labels for all surfaces. Ensure all dependent figures disappear on source withdrawal, including totals, target checkpoints and comparative calculations, while independently supported figures remain.
- **Operating limits.** No runtime change, official-document republication, source authority change, compensation for missing historical data, or private run was part of this audit.
