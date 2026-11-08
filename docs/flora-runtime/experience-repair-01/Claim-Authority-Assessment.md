# Experience Reconciliation Repair 01 — pre-change claim/authority trace

Pinned main: `7f40bf2242f3b49da2eaac6c05a6db9450f78b95` (merged #530–#536).
Recorded before implementation; source is the 8 November reconciliation audit
(F01/F02/F05/F06) and the current effective renderers, including their wrappers.
ADR-002/009/012/026 carry Accepted metadata. ADR-014/024 headers say Draft while
body Status says Accepted; this ambiguity is recorded, not changed or used to
weaken their evidence/ownership boundaries.

| Executive route family | Current owner / derivation | Qualification dropped / minimum correction |
| --- | --- | --- |
| `/flora/banking`, `/banks`, `/portfolio` | banking_portfolio BANKS, _bank_card and portfolio_page; five code-defined accounts; GENERATED_DATE=2026-07-19 | Show curated pilot status, working account ranks, scenario horizons and unverified sizing aggregates. No accepted Industry/model implication. |
| `/flora/banking/<bank>`, `/briefing` | effective bank_page wrapper (2166), body (2024); formatted financial snapshot and COH opportunities | Existing £205m Barclays sum is 85+80+40; keep numbers but identify illustrative external-services scenario sum, not customer budget/economic value/qualified pipeline. Show each sizing formula and assumptions beside its range. |
| `/flora/banking/<bank>/opportunity/<COH>` | estimate_value (54), opp (83), source entries (98), base detail (718), final wrapper (2083) | Formula is fixed scale/category/scope/managed-service multipliers and rounding; status/assumptions/risks/disconfirming evidence are retained in objects but lost in detail. Remove unsupported appended buying-activity assertion. Sponsor, buyer, funding, scope and procurement remain unknown. |
| `/pipeline`, `/heatmap`, `/heatmap/detail`, `/compare` | inherited renderers and latest chart/card helpers, COH value midpoints/theme scores | Qualify every aggregate as scenario sizing; expose constituent formulas rather than upgrade sums into pipeline. Ranks and scores are editorial working scenarios, not accepted evidence confidence or deal probabilities. |
| `/competitors`, supplier cards/detail | SupplierEntry, _supplier, _supplier_cell; all eight existing relationship entries have insight_basis=inferred | Name/traction renderer drops inference, rationale, default source_date=2025-01-01 and Medium confidence. Show these limits; no contract-specific accepted Evidence exists in these entries. Market presence cannot prove incumbency, renewal or displacement. |
| `/outlook`, `/signals`, `/industries/uk-banking` | INDUSTRY_SIGNALS / PESTLE; first featured item High, others Moderate by index; inspection profile says Governed / Owner-backed | Preserve narratives; call conviction editorial, not calibrated Evidence confidence or ADR-026 qualification. Show snapshot date, missing claim-level Evidence/applicability and investigation requirement. Correct inspection authority profile. |
| `/ai-native`, `/ai-native/capability-model`, `/timeline`, enterprise event timeline | fixed future-state tracks, horizon buckets, placeholder event dates | Label strategic scenarios and assumed timing, not programme milestones, buying triggers or procurement dates. Generic timeline rows are illustrative, not source-located events. |
| `/evidence`, `/financial-performance`, `/market-analyst-view`, `/market-reaction`, `/analyst-history`, `/research-backlog` | generic source labels, static snapshot / gaps; _lineage hashes bank.id, sources, GENERATED_DATE | Preserve navigation, disclose missing accepted Evidence IDs/locators/Observation mapping; hash is view identity only. Do not manufacture Evidence. |
| Home `/` and `/intelligence?tab=industries` | _flora_home_page / _flora_intelligence_page; literal one governed Industry and six represented enterprises, plus separate BRH-003-derived pipeline | Keep Banking link labelled curated repository pilot. Separate visible Industry candidate/current partial-release counts using existing identity/lifecycle/permissions. Do not claim full acceptance or register a fake Canvas. Scope derived participant/gap counts. |

Existing legitimate controls remain: canonical memory repositories, governed
identity/lifecycle, factory subset promotion and supported Observation/model
handoff; ClaimValidator and BK-OPP commercial eligibility. This repair does not
make the static COH scenarios accepted inputs to those services, add reasoning,
create qualified opportunities, or connect unified navigation/canonical adapters.

Implementation approach: use a small Banking-only page disclosure and existing
rendering helpers for consistent source/authority framing, with object-specific
formula/timing/supplier disclosure beside material estimates. Reuse read-only
owner status and access checks for Home; no second registry or canonical count
owner. Test visible text and real browser routes, including inherited wrappers.
