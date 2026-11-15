# ADR-027 — Document-scoped publisher admission and permitted use

**Status: Proposed — not accepted or implemented.** Owner/Chief Architect decision required.
**Date:**2026-11-15 · **Commission:** EAI-1 #628
**Authority:** Existing Source/Evidence/Observation owners; ADR-002/005/010/012/014/016/024/026 remain unchanged.

## Decision requested

Decide whether specific SEC-hosted issuer-filing and ONS statistical-document uses may enter the **existing** source-admission path. This proposal grants no rights, changes no publisher rule and accepts no Evidence. EAI-1 retains current restrictions and demonstrates permitted sources only.

`source_import.official_url` uses a positive HTTPS publisher allowlist. SEC/ONS are absent. Git history shows the list grew with bounded pilot publishers, not a conclusion that all omitted facts are false or unlawful. INT-1/#628 require explicit approval before expansion; absence is not a bug to bypass.

Five independent gates apply: original provenance; rights for the exact use; source verification/extent; CIOS publisher/document/audience admission; individual canonical Evidence acceptance with authorised subject mapping. Type, technical validation, official hosting and package acknowledgement do not settle the other gates.

## Options

| Option | Boundary | Recommendation |
|---|---|---|
| Defer restricted documents | Preserve current controls and owner candidates; omit dependent live content; continue permitted sources. | **EAI-1 implementation boundary.** |
| Explicit document-scoped admission | Owner approves exact host/path/category, issuer, purpose, audience, excerpt limit, rights, attribution and revocation; existing validators remain. | Preferred next decision for the narrowly licensed ONS numeric slice; SEC issuer-content use needs a separate rights decision. |
| Independently verified permitted original | Inspect a genuine issuer/official original and its own rights; preserve fresh provenance. | Only when actually available and permitted. Never transplant/relabel a SEC excerpt. Existing Lloyds site terms do not grant broad electronic republication. |

No broad host permission, mirror/proxy, alternate-host copied excerpt, source relabelling, neutral-host bypass or presentation-only admission override. Structured data/XBRL remains preferable where it satisfies the same identity, rights and authority gates; format is not a waiver.

## Exact candidate scope

**ONS:** `https://www.ons.gov.uk/economy/grossdomesticproductgdp/bulletins/gdpmonthlyestimateuk/september2026/pdf`. Only the reviewed GVA2 appendix, 2024 SIC2007 weights, particularly SectionK=81/1000. Proposed use: attributed numerical extraction for GB/industry read-only context, not Banking TAM/current growth or all ONS content. ONS [terms](https://www.ons.gov.uk/help/terms-conditions), reviewed15Nov, state most content is Crown copyright/OGL with third-party exemptions. Exclude images, logos, full prose, third-party material and implied endorsement. The pre-existing frozen public extract is not a route for new imports.

**SEC-hosted issuer filing:** `https://www.sec.gov/Archives/edgar/data/1160106/000116010626000022/lyg-20260630.htm`. CIK1160106, LLOYDS BANKING GROUP PLC, Form6-K dated30July2026, H1 to30June2026, specified underlying Retail/Group rows. SEC hosting does not make an issuer-authored filing a US-government work. No blanket licence for Lloyds prose was verified. Bounded factual numerical review and full-document redistribution are different uses. **Defer runtime admission** until the exact issuer-content use/right is resolved. SEC website-policy retrieval was unavailable; no missing permission is fabricated or general legal opinion claimed.

FCA's separate numerical-data OGL clause2.2 is not authority for SEC/ONS. An ONS licence can support the specific content use while its CIOS admission still remains denied. Source eligibility and canonical acceptance remain independent.

## Conditional future implementation

Extend the owning `source_import` contract, not a second Source/Evidence registry. Specify the approved purpose/audience and immutable document identity before code. Use existing source/mapping/review/promotion owners and real tenant authority; public candidate scope never authorises private source reads.

Bind exact parsed HTTPS host/path/issuer/category. Reject credentials, nonstandard ports, query/fragment aliases, lookalike domains, encoded/dot/backslash path tricks, other issuers/accessions and unreviewed redirects. Same-host redirects do not approve another document. Respect source-specific fair-access/collection rules; this proposal authorises no collector, scraping loop, paid call or scheduled job.

Keep publication, reporting, event/effective, retrieval and review dates separate. Retain legal/reporting-segment scope, basis, sign, unit, actual/target/estimate and source version. Preserve exact excerpt location and the actual retained-text digest. Original bytes unavailable means **null** original-byte digest, never an invented archive, extraction metadata or confidence.

Changed identity, rights, audience, expired review, retraction or core contradiction excludes dependent statements before titles/counts/cache/export. Preserve source and decision history. Rights ≠ verification ≠ Evidence acceptance ≠ import execution ≠ MaterialPressure qualification.

## Tests and release

Test exact approved documents/purposes and reject other issuers/accessions, ONS third-party media, path ambiguity/redirects, private sources, wrong entity/period/basis, stale/revoked/contradicted material and unapproved acceptance. Retain strict388 security, unknown-file rejection and unchanged inherited failure/skip comparator. Prove source-to-statement and financial reconciliation.

Owner approves this decision/use first, then a separate minimal policy implementation with exact-head CI. The eight individual Evidence decisions and actual authorised target/receipt reconciliation stay separate. No import, Offers or Pipeline action follows automatically. A later rollback removes admission/dependent views through the owning policy while preserving historical Evidence/decisions; canonical compensation is not blind deletion.

## Decision record

Owner choice: **pending**. Newly approved documents/purposes/audiences: **none**. Canonical Evidence decisions: **not executed**. SEC/ONS runtime admission in EAI-1: **unchanged / denied**. No accepted ADR or canonical lifecycle is amended.
