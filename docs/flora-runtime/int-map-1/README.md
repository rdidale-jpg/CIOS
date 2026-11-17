# INT-MAP-1 — FLORA intelligence-model stocktake and decision

**Status:** Draft for owner architectural acceptance, **assessment only**, 17 November 2026. Issue [#653](https://github.com/rdidale-jpg/CIOS/issues/653). Based on verified GitHub `main` at `fbac4c37910ed07b2baa516e1a5c8d7f329086de` (AUTH-2); this is not a claim about live Render state. No runtime, source policy, canonical, authentication, Pipeline or deployment change. See [ownership matrix](Model-and-Ownership.md), [ripple/change scenarios](Change-and-Ripple.md) and [challenge/decision](Decision-and-Critique.md).

## Executive conclusion

**FLORA has substantial intelligence components, but does not yet have one coherent change-to-synthesis loop.** Its current UK/Banking/Lloyds Top/Left/Main scenes are mostly bounded, source-pinned editorial compositions. Richer PESTLE, Porter, value-chain, operating-model and supplier views exist through other owners or historical routes; the BIE-2 news register has **17 research candidates** but is not an admitted or regularly refreshed news service. An existing canonical external-change interpreter offers a narrow, read-only eligibility/enterprise-applicability assessment; it is **not** general-purpose research ripple-through or autonomous model maintenance. Actual news-to-industry-to-enterprise dependency recomposition is not proven.

The product should organise around three distinct questions:
- **Landscape — What is this industry and how does it work?** Structure, actors, value creation, business models and enterprise exploration.
- **Forces — Why does it behave and evolve as it does?** Persistent economics, regulation, rivalry, buyer/supplier forces, technology and resilience; not an event list.
- **What's changing? — What actually moved, where and why does it matter?** Dated changes, affected enterprise/industry mechanisms, supported implications and explicit uncertain applicability. **Recommend a third contextual toggle only after a small working design proof**, not by adding a static feed.

The essential architecture is **one sourced event/fact, many derived views**. Facts, ownership, source revisions and analysis remain in existing research, Financial, Model and presentation owners. Build a **read-only recomposition/impact index** over existing source/event/subject/relationship keys, with a dependency-based invalidation contract. Do **not** build a new ripple engine, Evidence registry, crawler, candidate database or automatic canonical promoter.

## Actual inventory and authority distinctions

| Level / concern | Runtime reality at baseline | Models/frameworks and repository owner | Assessment |
| --- | --- | --- | --- |
| UK, macro and national context | UK Landscape/Forces routes live in `visual_streams.SCOPES['uk']`; existing `/macro`/historical global prototype and PESTLE context have bounded routes, not proof of live continuous country model updates | `visual_streams.py`, `visual_panels.py`, `research_intelligence.unified_views`; `global-macro-v1/README.md` historical | **Implemented views / partial integration**, not automatic macro propagation |
| Banking Industry Twin | `/industries/banking` has `landscape|forces` streams; composed from assessed source-pinned claims, leadership issues and illustrated scenes | `visual_streams.py`, `visual_panels.py`, `leadership_agenda.py`; `research_intelligence.model` Assessment Overlay | **Live curated presentation**; many richer frameworks are outside primary scene |
| Industry analysis | PESTLE, Porter Five Forces, horizontal value chain, profit-pool/economic narratives and relational SWOT appear in structured assessed research and alternate routes | `research_intelligence.visual_templates`, `research_intelligence.unified_views`, `docs/flora-runtime/bie2/Industry-Analysis.json` | **Candidate/parallel analytical presentations**, no proven canonical Industry Twin recomposition |
| Enterprise economics | AUTH-2 makes **public Nationwide FY2026** eight source-bound measurements and two reconciliations visible; F1/F2 protected runs still exist | `financial_intelligence.candidate_analytics`, `analyst`, `visual_panels`; Source owner | **Working**, materially uneven issuer coverage; subject/basis/date guarded |
| Enterprise operation, leadership, tech and suppliers | Lloyds illustrated Inside/Landscape/Forces has bounded associations; separate operating maps, customer/supplier relationships, programmes and commercial hypotheses survive in overlay/legacy paths | `visual_streams`, `unified_views`, `Assessment-Overlay.json`, legacy `banking_portfolio.py` | **Partial/disconnected**; a supplier association is not a verified contract |
| News and events | `bie2/News-Candidates.json` has original event/publication/retrieval/effective dates, dedup and interpreted meanings; each is `production_news_eligible:false` in the reviewed source file | Research pack `News-Candidates.json`, Enterprise timeline/legacy Banking routes | **Candidate research / historical pages**, not general admitted, recurring News |
| Changes / pressure | `ExternalChangeInterpretationService.assess` resolves *governed* external Evidence and annotated linked enterprise observations, returns eligible/rejected assessments and evidence demands; `material_pressure.qualify_candidates` applies ADR-026 | `enterprise_intelligence.change_interpretation`, `blueprint_import.material_pressure`, accepted **ADR-026** | **Read-only narrow governed assessment**; no general working research propagation or canonical auto-update |
| Source facts / memory | Research source snapshots and candidate claims, working Financial runs, canonical Evidence/Observation/Model are different owners | `research_intelligence.model`, `intelligence_presentation`, `memory.repository`, EI-001 **Draft** and accepted applicable ADRs | **Important separation**; analytical views needn't promote every fact |
| Opportunities / Pipeline | Legacy Banking signals, candidate opportunity research and authorised Pipeline stages are distinct; a rendered view/association cannot qualify a buyer need | `unified_views`, `banking_portfolio`, Pipeline owner, accepted ADR-026 boundary | **Existing but not driven by automatic change-to-opportunity loop** |
| UX | Three-panel beautiful editorial shell, 7 visual scenes and existing 2-option UK/Banking/Enterprise stream grammars; public source citations removed from ordinary Main | `visual_streams.SCOPES`, `visual_panels._editorial_banking`, presentation six types | **Polished core, shallow coverage;** selected enterprise often becomes one topic |

**Authority caution:** `IT-001-Industry-Twin-Specification.md` carries **Review/Proposed** status and `EI-001-Enterprise-Model-Specification.md` remains **Draft**; cite them as design intent, not accepted runtime law. ADR-026 is **Accepted** and reserves durable Material Pressure for evidenced canonical enterprise applicability. Earlier Banking v1 `docs/product/UK-Banking-Industry-Twin-v1-Closure.md` says “Accepted for pilot use” for historical routes: this is **not** proof those functions are the current main visual experience or that their numerical claims are freshly verified.

## Concrete disconnections (with code anchors)

1. **View ownership is fragmented.** `visual_streams.SCOPES` only permits `landscape|forces` for Banking, while `unified_views.industry_page` supports `overview|pestle|porter|value-chain|ai-disruption|regulation|commercial`. More available research has not meant more current Banking Main intelligence.
2. **News candidate ≠ source admitted event ≠ enterprise update.** BIE-2 preserves 17 event candidates with `production_news_eligible:false`; no current direct incremental event-to-twin refresh path is established by that dataset.
3. **A linkage can be only navigation.** `visual_templates` draws nodes and links from existing overlays. A hyperlink from UK force to a bank cannot prove enterprise exposure, canonical adoption or model mutation.
4. **Static pinning is deliberate but brittle.** The curated claims and agendas use explicit IDs/eligible source status; source changes can suppress views, but there is no verified generalized dependency-led industry resynthesis. Keep privacy, source lifecycle and invalidation safeguards.
5. **Comparability is hard.** Nationwide Group FY2026 income/profit, FCA Society complaints, NatWest Group deposits and HSBC UK Bank plc USD earnings have different legal subjects and dates. They cannot be aggregated into industry trend without qualified cross-entity definitions.
6. **Private/public were previously entangled.** AUTH-2 now serves bounded public Nationwide financial facts without privileged run lookup. Keep this approach to public intelligence; authentication is a separate workstream, not an industry research prerequisite.

## Framework placement (not seven separate screens)

- **PESTLE:** UK and external environmental causes; sector relevance is assessed, not assumed.
- **Porter's Five Forces:** structural industry competitive mechanisms; not a synonym for four recent news items.
- **Industry value chain / profit pools:** where money, control, customers and supplier roles flow; explicitly distinguish conceptual from verified bilateral edges.
- **Enterprise operating model/capabilities/technology and financial economics:** how *this enterprise* makes, spends, operates and changes; source-grounded real identity, scopes and periods.
- **Leadership/relationships:** who owns decisions, linked customer and vendor ecosystems, contract evidence versus collaboration announcements.
- **Event/news and timeline:** dated change signals linked to actors, decisions and existing mechanisms; news is input, not the Twin.
- **Material Pressure / opportunity:** separately reasoned enterprise-specific consequence and commercial hypothesis; ADR-026 still governs durable qualification and Pipeline remains explicit.

## Decision recommendation

Accept **Option A: bounded read-only “What's changing?” composition + dependency-based reassessment within existing source, enterprise and presentation owners**. Do not implement until owner accepts the decision and an actual user-journey design. Defer Option B's more general change maintenance after real pilot usage proves a need. Next, use a small subset of actual dated public material from Banking to demonstrate *working* change stories—not static candidate News text or speculative sales plays. Read [Change-and-Ripple.md](Change-and-Ripple.md) and [Decision-and-Critique.md](Decision-and-Critique.md).

**No new external news or law was verified for this assessment.** The examples and dates use existing repository records as of the assessed commit; live recency must be rechecked before any later public News activation.
