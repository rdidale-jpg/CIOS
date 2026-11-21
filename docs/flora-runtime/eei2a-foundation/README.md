# EEI-2A · Public financial statement foundation

Base `df6173c186e6469783c732247f4c13aaa961aec4` includes #698, #699, #701 and #704. The [FS1 assessment](https://github.com/rdidale-jpg/CIOS/pull/706) is an input, as is the accepted Source-first and dual-speed Financial architecture. #705 stays on its separate draft branch. ADR-027 retains Proposed status. [ADR-010](../../../architecture/decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md) · [ADR-011](../../../architecture/decisions/ADR-011-Dual-Speed-Financial-Intelligence.md) · [Approved factual-use policy](../public-facts-policy/README.md)

## Implementation and ownership

| Stage | Existing owner reused | EEI-2A responsibility |
| --- | --- | --- |
| Official Source, verification and eligibility | `source_import.routine_factual_use`, `provenance`, `minimal_factual_integrity` | The existing integrity function gains an opt-in, exact instant-date branch for stock facts. Legacy callers retain duration-only checks. Digest covers Source document/version and exact bindings. Stored provenance and absence of a material exception remain necessary. |
| Typed read model | F1 `Measurement`, `FinancialPeriod`, `SourceReference` and the shared numeric value | `Line` adds statement, reported label, fiscal-year label, sign convention, optional accounting standard and revision state. Basis, consolidation scope, currency/scale, precision, stock/date versus flow/duration and actual/estimate/target/forecast types stay with the existing owners. The ordinary public read path admits reported actuals. A reported actual percentage can be displayed with explicit unit and precision. |
| Revision and comparison | SHA-bound Source facts; Financial `calculate` and its finite recipes | A statement revision retains its binding and report revisions. Restatement references the exact predecessor binding digest; compatible superseded records are retained in the validated package but excluded from current render. A conflicting, withdrawn or invalid package fails closed. Monetary calculations reuse F1 after additional statement, standard, sign and perimeter checks. Reported percentages stay out of F1 monetary arithmetic. |
| Presentation | ISP-1 `Statement` eligibility and the Enterprise Economics composition | One shared summary with Facts and Insight. Reported labels and displayed values are passed through from eligible inputs; reporting dates and scope stay visible, and source and basis are inspectable. Public Nationwide Landscape reuses the existing AUTH-2 input on every render. Legacy charts, bridge and private-run entry points are retained. |

[Source owner](../../../cios/applications/flora/research_intelligence/source_import.py) · [Statement projection](../../../cios/applications/flora/financial_intelligence/public_statements.py) · [F1 arithmetic](../../../cios/applications/flora/financial_intelligence/candidate_analytics.py) · [Economics](../../../cios/applications/flora/enterprise_economics.py)

The reusable projector accepts a **trusted, preselected record** and exact expected subject. It exposes no HTTP endpoint, source URL parameter, scraping, run lookup, storage, canonical or Pipeline operation. No new Source or publisher origin is introduced. Neither policy reuse nor creation of a typed line approves a Source. Source selection across multiple real reports is an EEI-2B integration decision; there is no new registry.

### Coverage and data status

| Statement | Supported typed shape | Concrete proof |
| --- | --- | --- |
| Income | Dated duration lines for revenue/income, expenses, operating/pretax/net profit and properly scoped segment results | Nationwide eligible income facts, plus two annual synthetic revenue lines per fixture. |
| Balance sheet | Instant lines for assets, liabilities, equity, cash, borrowings, working-capital components, leases, intangibles, goodwill and suitably defined capital/liquidity measures | Synthetic year-end cash lines and a percentage-type validation example. Nationwide summary marks no eligible figures for this statement. |
| Cash flow | Dated duration lines for operating, investing, financing, capex, defined free cash flow and financing/debt movements | Synthetic operating cash lines across two periods. Nationwide summary marks no eligible figures for this statement. |

Labels, metric definitions and scopes are Source-bound data. No metric list implies coverage or availability. The examples do not fill absent categories.

| Reference enterprise | What actually runs |
| --- | --- |
| Nationwide | Existing eligible AUTH-2 public projection adapted into five income-oriented lines. No new financial Source or values. Also demonstrated a separately labelled synthetic three-statement package through the generic Source reader. |
| easyJet | Existing Landscape Economics and eligible operating facts unchanged. Two synthetic reporting periods, each with three statements, pass the generic reader and shared renderer in isolation. Real monetary data still needs verified eligible Source admission and a finite selection binding. |
| BT Group | Existing TEL-001 evidence remains in its owner. Official BT origins are outside the current Source allowlist. Verified statement-level provenance, actual/APM status and Group/Openreach scope remain separate work. An isolated negative case verifies the boundary. |
| Equinix | Existing Technology FY2025 consolidated USD presentation remains in its existing owner. The issuer investor host is outside the current Source allowlist. Typed Source binding, documented use scope and Group vs UK entity reconciliation remain unproven. An isolated negative case verifies the boundary. |
| Lloyds | Existing §2 hold remains inactive and §5 direct PDF links remain deferred. The generic reader excludes the existing special-case issuer and never changes the dedicated Source guard. |

### Self-critique and EEI-2B

The first eligible public view covers only a slice of one statement and remains alongside the existing Nationwide presentation. The generic fixture path keeps restatement history within a bounded verified package; it is not a cross-document history store. A changed or withdrawn input invalidates the whole package rather than falling back to a superseded figure. Existing F1 annual calculations still require comparable, adjacent complete fiscal years and the same presented Source version. The view supports eligible reported percentages but performs arithmetic on compatible monetary inputs only. It makes no interoperability claim for arbitrary accounting tags or ratios.

EEI-2B can now define a finite Source-owned issuer/report selection and prepare one verified easyJet monetary income fact, then add eligible stock and cash-flow facts or a matched comparator as verified. It still needs actual document acquisition/use evidence, issuer and period bindings, source lifecycle proof, and separate owner review before anything new is activated. BT and Equinix still need separately scoped origin and evidence review. No implementation decision here widens Financial-run ACLs or authorises sector-level aggregation.

### Review and verification

| Outlook | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Existing eligible Nationwide income | [Desktop](previews/nationwide-desktop.jpg) | [Landscape](previews/nationwide-ipad-landscape.jpg) | [Portrait](previews/nationwide-ipad-portrait.jpg) |
| Isolated synthetic travel group | [Desktop](previews/synthetic-desktop.jpg) | [Landscape](previews/synthetic-ipad-landscape.jpg) | [Portrait](previews/synthetic-ipad-portrait.jpg) |

Chromium loopback proof. No live service or production financial activation. [Browser harness](browser.py) · [Browser results](previews/browser.json). Exact-head local/hosted checks and reverse-tree rollback are recorded in the PR. The historical compatibility helper checks the exact new hashes and rejects AST differences outside the two named functions before passing their prior cuts to the existing historical tests. No comparator or inherited signatures are changed.
