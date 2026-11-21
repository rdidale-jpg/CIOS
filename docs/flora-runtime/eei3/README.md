# EEI‑3 public financial history

## Review boundary

PR #708 merged into main at `cef08949f511f51604c20009a3df27fd484fe3f2`. The merge tree exactly matches its approved head `e6d49f3391f5cd1527ace9010db8ab56f459b87b`. PR #709 targets that main baseline and its 25-file review delta is the original EEI‑3 delta. The browser captures below are from the earlier review heads. The reconciliation leaves the captured runtime code and Source data byte-identical.

## The routine path

1. Research the original issuer report or official filing through ordinary access. Establish the filer, accounting perimeter, dates, financial meaning and the actual use conditions. Record original document identity, version digest and exact cell locators. Keep protected expression and original bytes out of the review package.
2. Add the minimal Source record and catalogue binding. A publisher can have a verified issuer origin or an official archive binding. For EDGAR, match the filer CIK and accession in the official index against the exact document URL. The public application opens confined repository files and verifies their provenance, lifecycle, selected facts and bounded-use scope. It makes no outbound request. A catalogue administrator's binding and independent provenance check support authenticity. A file hash alone proves only identity of bytes.
3. EEI‑2A projects the same typed lines across issuers and reports. Duplicate same-value comparatives retain historical provenance and take the recent eligible publication for display. Divergent duplicates require a compatible predecessor and an explicit restatement. Withdrawal suppresses dependent rows and calculations. Closing-balance differences and same-document annual growth use the existing Financial F1 contract. The view retains source precision, scopes and dates, with display-only rounding of percentages.
4. Existing Banking and Technology presentations resolve the catalogue using their established presentation identities. Technology reuses the existing `detail` context and offers Facts and Insight in the Business & financials view. The shared Economics renderer resolves current values, sources and basis. The operation supplies public working facts only. Durable Evidence and Enterprise Model acceptance, financial runs, resource permissions and Pipeline retain their existing owners.

The working package is a repository-owned Source input outside the immutable historical research corpus. It holds provenance and bounded records for review. It grants no permission over a host or the use of an entire document, and it cannot enter the existing Financial-run selection catalogue. The older #708 finite selection remains a compatibility path with no production view caller. The proposal in ADR‑027 remains Proposed.

## Real evidence

| Existing view | Record and scope | What the view shows |
| --- | --- | --- |
| Nationwide | FY2026 original audited Group report on the existing Nationwide results origin. #708's intact Source record has 44 facts for FY2026 and FY2025. | Income, balance sheet, cash flows and regulatory ratios. Closing cash and central bank balances increased by £8,928m. FY2025 flow duration and Virgin Money scope prevent a like-for-like annual trend. |
| Equinix | FY2025 and FY2024 original SEC EDGAR 10‑Ks. Filed by Equinix, CIK 1101239. Minimal scoped values were checked against displayed table cells and inline XBRL filing contexts. Both filings retain 30 bindings. | Consolidated income, balance sheet and cash flows, and separately scoped Americas segment capital expenditure. 45 active measurements across FY2023–FY2025. FY2025 revenues increased from $8,748m to $9,217m, or 5.36%. Assets rose by $5,056m. Operations supplied $3,911m and investing used $6,484m in FY2025. No UK-only result or free cash flow conclusion follows. |

[Original Nationwide report and provenance](../eei2b-real-statements/README.md) · [Equinix FY2025 filing](https://www.sec.gov/Archives/edgar/data/1101239/000110123926000032/eqix-20251231.htm) · [Equinix FY2024 filing](https://www.sec.gov/Archives/edgar/data/1101239/000162828025005126/eqix-20241231.htm) · [EDGAR filer identity and filing dates](https://data.sec.gov/submissions/CIK0001101239.json) · [EDGAR access and fair access conditions](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)

The same passing process starts with Nationwide alone, adds the verified Equinix FY2024 record and binding without Python changes, then adds FY2025 data using the same factual-use policy. Both Equinix original publications remain in history. The correction test exercises an altered value and explicit lineage on isolated copies because the selected genuine comparatives did not require a restatement.

## Restrictions and critique

- Equinix's investor-site terms question remains open. The new statement records come from statutory EDGAR filings and retain independent numerical facts under ordinary use. They grant no new copying or bulk collection rights. Existing legacy summary values and its source link are outside the new projection.
- easyJet's corporate terms applicability remains unresolved. BT's issuer-origin and distribution-terms questions remain open. No facts from those sources enter this path. Lloyds §2 stays inactive and §5 direct PDF links remain deferred. The existing inactive Lloyds case and a scoped exception test exercise the blocking rules.
- Runtime has no general crawler or upload API. Checking issuer identity, selecting values and inspecting a new report or actual terms change remain evidence work. A repo data change is sufficient for a compatible report or a new compatible issuer in an opted-in presentation. A genuinely new Enterprise route still needs a presentation owner.
- Presentation supports repeated fiscal years by exact dates and labels, with bounded horizontal scroll for wide series. The first correction contract selects one explicit restatement and fails closed on ambiguity. Chained corrections and audited versus unaudited interim comparisons need further work. This increment supplies no invented margin, working-capital or AFFO definitions. Multi-factor ratios and additional sector recipes require compatible Financial contracts and reviewed facts.
- Source inspection exposes published report titles, periods, locators and homepage attribution. It exposes no retained raw documents, research administration or private runs. Physical iPad and assistive technology review remain outstanding.

## Browser evidence

| Equinix Business & financials | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Before on #708 | [Desktop](previews/before-desktop.jpg) | [Landscape](previews/before-ipad-landscape.jpg) | [Portrait](previews/before-ipad-portrait.jpg) |
| After, Facts | [Desktop](previews/after-desktop.jpg) | [Landscape](previews/after-ipad-landscape.jpg) | [Portrait](previews/after-ipad-portrait.jpg) |
| After, Insight | [Desktop](previews/insight-desktop.jpg) | [Landscape](previews/insight-ipad-landscape.jpg) | [Portrait](previews/insight-ipad-portrait.jpg) |

[Loopback harness](browser.py) · [Before observations](previews/before.json) · [After observations](previews/after.json). Chromium viewport and touch simulation. Exercise mode navigation, Back, direct reload and withdrawal of the latest document while the earlier report remains available. No production activation or deployment.
