# Existing work, decisions and minimal integration

| Input / accepted requirement | Exact existing implementation / state | This sprint |
| --- | --- | --- |
| #712 executive density | Draft `e9daf762131c1e70cf83bebca5c811c56f4138d9`; selectively recovered in #728 | Reuse flagship's eight SWOT analyses, counter-evidence, source adapter and timeline; no merge of historical branch |
| #728 unified executive presentation | Merged `97d316c640c96d99c2301819f8aac00b3b9c1398` | Preserve unified facts/interpretation and no reading-mode selector; default renderer unchanged |
| #729 Presentation v2 / visual direction | Draft design `da1a6c7b5e4b95e85ef2de3697bc8c506368192c`; not a new canonical architecture | Retain responsibilities and original art; latest commission removes repeated Explore/Investigate steps from the new experience |
| #730 optional live preview | Merged `eaca26f2b31c3c9227bb797d60f7d3492a8313d1`, approved candidate `b1a3ccb849531a8e1fa74e6a06e306ef99cb1960` | Preserve original route/selection/default; add only an evaluation entry in its notice |
| Group-first arrival | #730 defaults to Retail | New optional Gold route defaults to Group, without replacing #730 |
| Only Landscape / Inside / Forces | Existing Top stream owner | Same three controls; five illustrated subjects each, no second perspective toolbar |
| Economics A1 | Existing `enterprise_economics`, `lloyds_recovery` and Financial Analyst | Reuse typed public statement guards and amount renderer; add zero-based stock presentation, no calculation engine, persistence or duplicate dashboard |
| LEI-1 / W3 | Research packages on main; not source admission or canonical acceptance | Audit and retain; no new segment numbers, executive mandates or supplier edges published |
| Production contract | `docs/architecture/enterprise-twin-production/` assessment/schedules; accepted owners constrain its proposals | Keep factual families separate from evidence status and derived interpretation; Unknown contract fields remain Unknown |
| Accepted architecture | Authority Registry, ADR-001/002/005/009/010/011/012/013/014/024/026 | Atomic lineage, durable-model ownership, inspectability, progressive assurance, source-first acquisition, financial semantics, promotion gates and canvas navigation preserved |
| Lloyds legal restrictions | #698/#699 existing Source exception; ADR-027 remains Proposed | §2 projection inactive, §5 direct PDF links deferred, homepage attribution only |
| Product Delivery Doctrine | #727 plus #728 bounded amendment | One complete draft, reusable existing work, source/security integrity, browser acceptance, no additional authority or process layer |

## Runtime responsibility

`lloyds_gold.py` is a finite Lloyds **presentation composition**, using the existing frame seam; it is not a second framework, model owner, evidence store, source registry or matcher. It reads `visual_streams.current_data` under `public_read`, obtains eligible statements through `lloyds_flagship._facts`, verifies the existing exact Group/period/unit/actual guards, and composes the selected view. The existing Leadership Agenda supplies the separately scoped FCA service measurements and existing stock-date calculation; no duplicate calculation is implemented. Source and primary-quote checks run anew for every request. The small financial display additionally checks the value matches its disclosure and source quote; no new measurement is persisted.

The original scene, skyline, Top navigation, `visual_panels._frame`, Source ownership and current default renderers are unchanged. The original #730 interaction script handles compact scenes and re-evaluation of restored pages. New finite GET/HEAD routes use the existing public target validator; malformed, duplicate, private and foreign state cannot become a resource lookup. There is no export, static HTML snapshot, JSON endpoint, client storage, private run selection or write action.

## Depth and representations

- L0 Group: business cards, dated scale, one supported strategic interpretation.
- L1 division / capability / force: contextual Main; no generic repeated three-step explanation.
- L2 economics: stock chart and business-model comparison, with Central / Equity accounting boundary. Inside: value-stream matrix, durable capability library, disclosed application/provider records and programme table. Forces: dated timeline, separate applicability reasoning and visual four-quadrant SWOT.
- L3 evidence / contracts / uncertainties / investigation: native details pages, not nested accordions. Source attribution, legal entity, dates, basis, caveats and counter-evidence are available. Named commercial questions are research questions, not buyer intent.

The retained `subject` is navigation context only. Switching to another perspective chooses compatible Group-level content and shows the retained subject; switching back restores the original division. No cross-perspective relationship is asserted. Browser URL state and ordinary links supply history/deep links; no parallel state store.

## Compatibility and release

Only finite GET/HEAD dispatch and the public route catalogue change. All handler mutation/authentication/workspace methods retain identical ASTs. Exact-byte route evolution pins unwrap this reviewed addition to #730 before applying the **unchanged historical pins**. Unknown bytes remain rejected; no failure/skip baseline, security discovery or comparator is loosened. Tests verify both preservation and negative mutation cases.

This branch makes no production claim. Main CI does not prove deployment; current live identity and comparison with the absent owner screenshots remain outside this draft. No changes to #712/#729 or other development branches.
