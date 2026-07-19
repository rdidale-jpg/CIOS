# UK Banking Industry Twin v1 Closure

## Status

Accepted for pilot use

## Final product decision

UK Banking Industry Twin v1 — Accepted for pilot use. It is sufficiently complete for structured sales-director testing, is not production complete, and records known limitations for backlog handling.

## Purpose

Banking v1 tests whether Flora can help a strategic sales director understand an industry, prioritise enterprises, understand enterprise behaviour, identify reinvention pressure, form commercial opportunity hypotheses, estimate opportunity value and timing, and inspect reasoning when challenged.

## Covered enterprises

- Lloyds Banking Group
- Barclays
- NatWest Group
- HSBC UK
- Santander UK

## Covered product journeys and actual routes

- industry portfolio: `/flora`
- UK Banking landing: `/flora/banking`
- industry outlook: `/flora/banking/outlook`
- ranked signals: `/flora/banking/signals`
- AI-native Banking: `/flora/banking/ai-native`
- AI-native capability model: `/flora/banking/ai-native/capability-model`
- reinvention timeline: `/flora/banking/timeline`
- bank comparison: `/flora/banking/compare`
- bank exploration: `/flora/banking/banks`
- commercial pipeline: `/flora/banking/pipeline`
- suppliers and competitors: `/flora/banking/competitors`
- detailed inspection: `/flora/banking/lloyds/evidence`
- safe-unavailable state: `/flora/banking/unknown-bank`

## Capability inventory

### 1. multi-industry shell
- Purpose: Expose Banking as the active accepted industry while preserving other industries as unavailable/deferred
- Route: `/flora`
- Implementation owner/module: `cios.applications.flora.web.app; banking_portfolio.global_industry_portfolio_page`
- Current status: Accepted for pilot use
- Accepted limitations: Only UK Banking is active; no Public Sector or next-industry implementation is included.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 2. Banking industry point of view
- Purpose: Summarise why UK Banking matters now
- Route: `/flora/banking`
- Implementation owner/module: `banking_portfolio.banking_landing_page / industry_outlook_page`
- Current status: Accepted for pilot use
- Accepted limitations: Point of view is a governed v1 synthesis, not live market research.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 3. reinvention-pressure indicator
- Purpose: Show pressure, likely behaviour, barriers and visible responses by bank
- Route: `/flora/banking and /flora/banking/{bank}`
- Implementation owner/module: `Bank records in banking_portfolio.BANKS`
- Current status: Accepted for pilot use
- Accepted limitations: Pressure labels are deterministic hypotheses and not canonical facts.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 4. industry signals
- Purpose: Expose featured and complete ranked Banking signals
- Route: `/flora/banking/signals`
- Implementation owner/module: `INDUSTRY_SIGNALS; industry_signal_explorer_page`
- Current status: Accepted for pilot use
- Accepted limitations: Featured subset is an editorial view; full inventory remains available.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 5. PESTLE and industry forces
- Purpose: Explain political, economic, social, technology, legal and environmental forces
- Route: `/flora/banking/outlook`
- Implementation owner/module: `pestle_view_html; causal_graph_html`
- Current status: Accepted for pilot use
- Accepted limitations: Force strength is qualitative.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 6. AI-native Banking reference model
- Purpose: Describe future AI-native capabilities and horizons
- Route: `/flora/banking/ai-native`
- Implementation owner/module: `AI_NATIVE_CAPABILITIES; ai_native_page`
- Current status: Accepted for pilot use
- Accepted limitations: Horizons are directional, not delivery forecasts.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 7. reinvention journey
- Purpose: Show migration path over time
- Route: `/flora/banking/timeline`
- Implementation owner/module: `timeline_page`
- Current status: Accepted for pilot use
- Accepted limitations: Executive sequence, not account-level committed roadmap.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 8. bank comparison
- Purpose: Compare banks across commercial modes
- Route: `/flora/banking/compare`
- Implementation owner/module: `compare_page`
- Current status: Accepted for pilot use
- Accepted limitations: Non-monetary modes should not be treated as valuation.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 9. enterprise overview
- Purpose: Provide account overview for five banks
- Route: `/flora/banking/{bank}`
- Implementation owner/module: `bank_page`
- Current status: Accepted for pilot use
- Accepted limitations: Standalone HSBC UK disclosure limitations remain visible.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 10. financial-history view
- Purpose: Render available financial metrics without fabrication
- Route: `/flora/banking/{bank}/financial-performance`
- Implementation owner/module: `financial_history_page`
- Current status: Accepted for pilot use
- Accepted limitations: History is incomplete and varies by bank.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 11. market and analyst view
- Purpose: Show market reaction and analyst themes
- Route: `/flora/banking/{bank}/market-analyst-view`
- Implementation owner/module: `market_reaction_page; analyst_history_page`
- Current status: Accepted for pilot use
- Accepted limitations: Market reaction and analyst history are partial.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 12. supplier intelligence
- Purpose: Show sourced or labelled supplier positions
- Route: `/flora/banking/{bank}; /flora/banking/competitors`
- Implementation owner/module: `supplier entries on opportunities; competitors_page`
- Current status: Accepted for pilot use
- Accepted limitations: Supplier coverage is incomplete.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 13. competitor intelligence
- Purpose: Rank competitor capabilities and whitespace
- Route: `/flora/banking/competitors`
- Implementation owner/module: `competitor_capability_html`
- Current status: Accepted for pilot use
- Accepted limitations: Capability coverage is directional and incomplete.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 14. opportunity hypotheses
- Purpose: Expose challengeable commercial opportunity hypotheses
- Route: `/flora/banking/pipeline and /flora/banking/{bank}/opportunity/{id}`
- Implementation owner/module: `pipeline; opportunity_page`
- Current status: Accepted for pilot use
- Accepted limitations: Hypotheses are non-canonical and require account validation.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 15. value estimation
- Purpose: Show value ranges and working estimates
- Route: `/flora/banking/pipeline`
- Implementation owner/module: `Opportunity.value; pipeline_page`
- Current status: Accepted for pilot use
- Accepted limitations: Values are uncalibrated commercial hypotheses.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 16. opportunity timing
- Purpose: Show buying windows and timing triggers
- Route: `/flora/banking/{bank}/event-timeline`
- Implementation owner/module: `enterprise_event_timeline_page`
- Current status: Accepted for pilot use
- Accepted limitations: Timing is indicative.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 17. commercial pipeline
- Purpose: Aggregate current opportunity hypotheses
- Route: `/flora/banking/pipeline`
- Implementation owner/module: `pipeline_page; bank_totals; totals`
- Current status: Accepted for pilot use
- Accepted limitations: Pipeline is not CRM, qualified pipeline, forecast or booked revenue.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 18. feedback and calibration structures
- Purpose: Preserve places for human feedback/calibration without changing canon
- Route: `/flora/banking/{bank}/research-backlog`
- Implementation owner/module: `research_backlog_page and feedback/calibration modules`
- Current status: Accepted for pilot use
- Accepted limitations: Limited account-team validation captured.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 19. provenance and evidence inspection
- Purpose: Expose source labels, lineage keys and detailed inspection
- Route: `/flora/banking/{bank}/evidence`
- Implementation owner/module: `evidence_page; lineage rendering`
- Current status: Accepted for pilot use
- Accepted limitations: Inspection depends on current governed package metadata.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.

### 20. safe-unavailable behaviour
- Purpose: Fail closed for unknown banks/routes
- Route: `/flora/banking/unknown-bank`
- Implementation owner/module: `safe_unavailable_page / bank lookup guards`
- Current status: Accepted for pilot use
- Accepted limitations: Unavailable states are plain HTML rather than polished UX.
- Relevant tests: Banking portfolio, increment 4.2–4.7.1, final pilot, v2 web, route and semantic tests.
- Relevant ADR or architecture decision: Accepted ADRs and architecture papers: architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md; architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md; architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md; architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md.
