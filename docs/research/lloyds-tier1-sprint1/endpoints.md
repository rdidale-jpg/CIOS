# Endpoint and relationship mapping register

All N IDs are package-local. No existing canonical endpoint mapping has been verified in the Lloyds workspace. The legal and source references below are review anchors. Preserve submitted direction and descriptive wording pending a mapping to an existing governed predicate.

| Endpoint | Label | Kind | Existing mapping or unresolved requirement |
| --- | --- | --- | --- |
| N01 | Lloyds Bank plc | legal entity | Companies House 00002065 |
| N02 | Lloyds Banking Group plc | legal entity | Group ledger binding and Group legal entity |
| N03 | HBOS plc | legal entity | Companies House SC218813 |
| N04 | Scottish Widows Master Trust | scheme | TPR scheme listing, separate from Scottish Widows Limited |
| N05 | The Pensions Regulator authorised list | publication locator | Keep as Source provenance |
| N06 | Business & Commercial Banking CEO | role | Resolve scoped existing identity with its owner |
| N07 | Business & Commercial Banking | business unit | Resolve scoped existing identity with its owner |
| N08 | Global Head of Transaction Banking | role | Resolve scoped existing identity with its owner |
| N09 | CIB transaction banking | function | Resolve scoped existing identity with its owner |
| N10 | Insurance Pensions and Investments CEO | role | Resolve scoped existing identity with its owner |
| N11 | Insurance, Pensions and Investments | business unit | Resolve scoped existing identity with its owner |
| N12 | Microsoft 365 E7 | application | Resolve scoped existing identity with its owner |
| N13 | Ariba Network | supplier network | Resolve scoped existing identity with its owner |
| N14 | Scottish Widows protection claims and underwriting | process | Resolve scoped existing identity with its owner |
| N15 | Sprout.ai | supplier | Resolve scoped existing identity with its owner |
| N16 | Lloyds Banking Group (Scottish Widows) | regulator participant label | FCA participant label, legal identity unresolved |
| N17 | FCA AI Live Testing cohort 2 | programme cohort | Resolve scoped existing identity with its owner |
| N18 | Scottish Widows | regulator participant label | FCA participant label, legal identity unresolved |
| N19 | FCA Supercharged Sandbox cohort 2 | programme cohort | Resolve scoped existing identity with its owner |
| N20 | RM6325 Payment Acceptance Services | framework | RM6325 listing, no call-off |
| N21 | Gloucestershire County Council | public authority | Resolve scoped existing identity with its owner |
| N22 | Lloyds Bank | supplier label | Council label, confirm legal identity before equivalence with N01 |
| N23 | Future skills programme | programme | Resolve scoped existing identity with its owner |
| N24 | Microsoft | vendor | Resolve scoped existing identity with its owner |
| N25 | GitHub Copilot use at Lloyds Banking Group | product-use label | Resolve scoped existing identity with its owner |

| Edge | Subject → assertion → object | Evidence | Assertion date or observation | Disposition |
| --- | --- | --- | --- | --- |
| R01 | N01 Lloyds Bank plc → lists active PSC → N02 Lloyds Banking Group plc | F01 | 2026-11-22 · register or listing observed | evidence and identity review |
| R02 | N03 HBOS plc → lists active PSC → N01 Lloyds Bank plc | F02 | 2026-11-22 · register or listing observed | evidence and identity review |
| R03 | N04 Scottish Widows Master Trust → appears in authorised list → N05 The Pensions Regulator authorised list | F04 | 2026-11-22 · register or listing observed | withheld from graph; evidence F04 retained |
| R04 | N06 Business & Commercial Banking CEO → public executive remit → N07 Business & Commercial Banking | F05A | 2026-02 · role start | evidence and identity review |
| R05 | N08 Global Head of Transaction Banking → public functional remit → N09 CIB transaction banking | F06B | 2026-11-18 · disclosure date; underlying effective date unresolved | evidence and identity review |
| R06 | N10 Insurance Pensions and Investments CEO → public executive remit → N11 Insurance, Pensions and Investments | F08A | 2026-11-22 · roster observed | evidence and identity review |
| R07 | N02 Lloyds Banking Group plc → reports rollout of → N12 Microsoft 365 E7 | F11A | 2026-06-04 · disclosure date; underlying effective date unresolved | evidence and identity review |
| R08 | N02 Lloyds Banking Group plc → requires registration through → N13 Ariba Network | F12 | 2026-11-22 · register or listing observed | source decision |
| R09 | N14 Scottish Widows protection claims and underwriting → historically trialled with → N15 Sprout.ai | F13 | 2025-06-05 · disclosure date; underlying effective date unresolved | source decision |
| R10 | N16 Lloyds Banking Group (Scottish Widows) → selected for → N17 FCA AI Live Testing cohort 2 | F14B | 2026-04-21 · disclosure date; underlying effective date unresolved | identity evidence required |
| R11 | N18 Scottish Widows → selected for → N19 FCA Supercharged Sandbox cohort 2 | F15 | 2026-07-22 · disclosure date; underlying effective date unresolved | identity evidence required |
| R12 | N01 Lloyds Bank plc → listed supplier on → N20 RM6325 Payment Acceptance Services | F16 | 2026-11-22 · register or listing observed | evidence and identity review |
| R13 | N21 Gloucestershire County Council → historical banking award to → N22 Lloyds Bank | F17 | 2021-10 · historical award commencement | further evidence and identity review |
| R14 | N02 Lloyds Banking Group plc → announced → N23 Future skills programme | F25 | 2026-08-20 · disclosure date; underlying effective date unresolved | source decision |
| R15 | N24 Microsoft → reported agreement extending → N25 GitHub Copilot use at Lloyds Banking Group | F11B | 2026-06-04 · disclosure date; underlying effective date unresolved | governed endpoint and predicate review |

R01/R02/R12 are the first edge-review candidates. R10/R11 need legal or governed participant identity confirmation. R13 also needs accessible buyer evidence. R03 remains in review lineage with F04 as its Evidence path. R15’s product-use label needs an existing permissible mapping. Neither a listing nor a reported partnership establishes a contract award or buying need.
