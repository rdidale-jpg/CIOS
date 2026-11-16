# Document-specific source-use decision

This is candidate source-use review, **not canonical Evidence acceptance or a new publisher/category grant**. Existing `source_import.official_url` already permits `www.bankofengland.co.uk`; no host, permission rule, SEC/ONS exception or proposed ADR is changed.

## Selected real material

[Official LPMZ598 Database viewer](https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?CSVF=TT&DAT=RNG&FD=1&FM=Jan&FNY=Y&FY=2021&Filter=N&FromSeries=1&SeriesCodes=LPMZ598&TD=15&TM=Aug&TY=2026&ToSeries=50&Travel=NIxAZxSUx&UsingCodes=Y&VPD=Y&html.x=66&html.y=26&title=LPMZ598). Original header and the two May/June rows were checked in one response, independently re-opened by both reviewers. The existing Source owner's `reviewed_web_excerpt` contract retains the actual short text with a SHA256, approved-tool references and **null original-byte checksum**. No original CSV/PDF archive is asserted. Direct shell download was unavailable; the approved web research tool provided the original viewed content.

| Measurement | Value | Meaning |
|---|---:|---|
| 31May2026 | 1,884,726 GBP million | MFI sterling retail deposits from household sector, excluding notes/coin; NSA amount outstanding |
| 30June2026 | 1,886,281 GBP million | Same definition and series; same reviewed response/vintage |
| Derived difference | 1,555 GBP million | Closing minus opening published stock |
| Derived relative difference | 0.082505361522046…% | Difference/opening×100; display0.0825%; not official statistical monthly growth |

The original publication day and release vintage are not established: metadata keeps `publication_date=null`. The retrieval date16November2026 is not relabelled publication. The URL date bounds are query controls, not release evidence. Values may be revised; this is not a latest-release claim.

[BoE M4 methodology](https://www.bankofengland.co.uk/statistics/details/further-details-about-m4-data) distinguishes stocks from adjusted changes and explains reporting-population/sector effects. Retail describes advertised-rate deposits, not all household deposits. Foreign-currency balances and notes/coin are outside this selected sterling series. The separate statistical changes/growth series are not reconstructed here. One reviewer initially saw a conflicting July response; July was excluded and the selected May/June pair was independently rechecked. No disputed later value is used.

## Applicable use, not a blanket licence

[Bank of England legal page](https://www.bankofengland.co.uk/legal), Database heading, expressly licenses Database numerical reuse under the UK Open Government Licence, unlike the general site's non-commercial-use clause. Its selected third-party FX and Crown Dependency exceptions remain excluded. No such exception was identified for these two UK sterling household-deposit cells. The linked full National Archives OGL page was not accessible to the review tool; this inspection limit is retained. The Database's express provision and already-used OGL attribution pattern support this narrow data use; this is not a certification of all legal questions or Bank content.

| Use dimension | Bounded decision |
|---|---|
| Access | Official public Database via approved web tool; existing positive publisher policy; no robots/paywall/redirect workaround |
| Processing | Two numerical rows and exact identifying definition; fixed financial compatibility and arithmetic |
| Retention | Necessary attributed numerical working data and short located excerpt under existing source/Financial owners; no copied full document or dataset |
| Numerical reuse | Database-specific OGL; no Bank report, prose, logo, imagery or third-party series licence inferred |
| Attribution/link | Original Database URL, series, source extent and dates; Bank copyright/OGL acknowledgement, licence link and no endorsement |
| Audience | Existing verified Financial workspace/resource users; no new anonymous feed, bulk export or general rights policy |
| Redistribution | Two numbers, identifying meaning and own calculation; no copyrighted narrative or recreated publisher visual |
| Withdrawal | Re-resolve owner source/use/revision on each read. Source denial/withdrawal removes all dependent output. Historical lawful working history retained. Editorial review until16December is distinct from legal licence duration |

## Excluded alternatives and decisions still required

- **Lloyds:** earlier EAI permitted bounded display/reuse of existing factual deposits, but the [current issuer terms](https://www.lloydsbankinggroup.com/site-terms-and-conditions.html), sections2/5, raise unresolved reproduction/storage/linking limits for the new persistent private candidate use. Current display alone is not a storage permission. F1 therefore creates **no Lloyds analytical run** and makes no new issuer-use grant. This does not rewrite or remove the existing accepted visual release.
- **NatWest/HSBC/Santander/SEC/ONS:** no source acceptance, policy expansion, proxy, import or canonical promotion. Proposed ADR-027 remains Proposed; EAR-1 stays unmerged.
- **BT:** selected acquisition configuration and a technically accepted receipt do not themselves establish commercial processing/reuse permission; no such licence is inferred.
- Broader named-bank research, actual flow-source expansion, refreshed vintages and category defaults need their own applicable source-use basis. Canonical Evidence/Observation/Model acceptance remains a separate explicit owner path.

The independently reviewed per-document decision is embedded in the bounded candidate package, consistent with existing EAI source snapshots. It is not another source registry or a mechanism for caller-supplied `rights:true` to grant access.
