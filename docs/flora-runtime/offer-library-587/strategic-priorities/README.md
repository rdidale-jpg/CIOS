# Owner strategic priorities — PR #588 continuation

Continues the owner-reviewed draft at `558a1d6750b018651e93bce856a10ae176f46136`; main remains `3b8bd2c5e5177c012826658f820eeeb4ea2705f5`. No merge, deployment, production-data or Render configuration change.

**89 named types, 29 developed playbooks:** the original 84 rows and IDs remain byte-for-byte equivalent as parsed data; five strategic programmes are added. The original 60 catalogue-only types stay catalogue-only. No example implies seller capability, customer demand, approved procurement or a live opportunity.

## Owner coverage matrix

| Priority / exact playbook | Differentiating customer proposition | Existing narrower Offers preserved |
|---|---|---|
| [Enterprise Digital Transformation](Playbooks.md#tech-strategic-digital-transformation) · `tech-strategic-digital-transformation` v1 / taxonomy v2 | End-to-end service, operating-model change and sustained business value | `tech-consulting-01/02` remain diagnostics/advisory, not renamed transformation |
| [AI-first Business Transformation](Playbooks.md#tech-strategic-ai-first-transformation) · `tech-strategic-ai-first-transformation` v1 / taxonomy v2 | Process, roles, controls and organisational adoption around a justified AI operating model | `tech-data-02` remains a bounded experiment |
| [Enterprise Cybersecurity & Resilience](Playbooks.md#tech-strategic-cybersecurity-resilience) · `tech-strategic-cybersecurity-resilience` v1 / taxonomy v2 | Critical-service risk, resilience and independent assurance; three named programme variants | `tech-cyber-01/02` remain managed detection/response and privileged identity |
| [Complex Legacy Application Modernisation](Playbooks.md#tech-strategic-complex-legacy-modernisation) · `tech-strategic-complex-legacy-modernisation` v1 / taxonomy v2 | Whole-estate treatment choices, multi-vendor rights, continuity and transition risk | `tech-engineering-01` remains a bounded reversible increment |
| [Social Value & ESG Transformation](Playbooks.md#tech-strategic-social-value-esg) · `tech-strategic-social-value-esg` v1 / taxonomy v2 | Material social/environmental commitments, additional delivery, measurement boundaries and accountable reporting | `tech-advisory-07` remains catalogue-only Sustainable IT measurement |

[Complete five playbooks](Playbooks.md) · [89-type coverage](../Coverage.md) · [15 differentiated sample matches](previews/Sample-Matches.json) · [Browser check evidence](previews/Browser-Checks.json) · [Original-84 content pins](Original-84.json)

## Category and version contract

- Stored category ID `consulting` is retained; the customer-facing label becomes **Digital Transformation & Consulting**. All 12 supplier category IDs remain.
- **Systems Integration** is an explicit optional delivery specialism, stored privately as `CommercialMission.technology_delivery_specialisms`. It overlaps business categories and supports architecture, interfaces, migration and multi-vendor delivery. Selecting it grants no employer authority or verified capability.
- New programmes have overlapping categories and one stable library ID each. Relevant priority programmes appear first; search still reaches all developed offers. Systems Integration search also finds existing integration/modernisation offers through an external delivery crosswalk, without editing their historic rows.
- The library container advances to v2, but `template_source.taxonomy_version` is pinned to each row's version. All original rows retain taxonomy v1 and their exact content hashes. An additive catalogue release therefore does not invalidate existing private or employer-approved offers. Changes/withdrawals to an actual row still fail closed; no historic snapshot is mutated or silently upgraded.
- Older profile clients preserve the new preference when they omit it; explicit empty selection clears it. Category/binding/mission version checks, CSRF/origin, independent employer approval, journal/audit and stale-parent checks remain.

## Updated desktop / iPad / phone previews

Before is the actual owner-reviewed #588 candidate at `558a1d6`, using its original three-offer SI fixture. After is a **separate illustrative transformation seller** explicitly selecting all five priorities, with one independently reviewed fixture example and four private drafts. It is a comparison of library coverage, not a claimed migration of that seller or real company endorsement. Original Sprint A evidence remains intact in the parent gallery.

| View | Desktop | iPad landscape | iPad portrait | Phone 390 | Phone 320 |
|---|---|---|---|---|---|
| Priority selection | [Before](previews/desktop-selection-before.jpg) · [After](previews/desktop-selection-after.jpg) | [Before](previews/ipad-landscape-selection-before.jpg) · [After](previews/ipad-landscape-selection-after.jpg) | [Before](previews/ipad-portrait-selection-before.jpg) · [After](previews/ipad-portrait-selection-after.jpg) | [Before](previews/mobile-selection-before.jpg) · [After](previews/mobile-selection-after.jpg) | [Before](previews/mobile-320-selection-before.jpg) · [After](previews/mobile-320-selection-after.jpg) |
| Five-offer portfolio | [Before](previews/desktop-portfolio-before.jpg) · [After](previews/desktop-portfolio-after.jpg) | [Before](previews/ipad-landscape-portfolio-before.jpg) · [After](previews/ipad-landscape-portfolio-after.jpg) | [Before](previews/ipad-portrait-portfolio-before.jpg) · [After](previews/ipad-portrait-portfolio-after.jpg) | [Before](previews/mobile-portfolio-before.jpg) · [After](previews/mobile-portfolio-after.jpg) | [Before](previews/mobile-320-portfolio-before.jpg) · [After](previews/mobile-320-portfolio-after.jpg) |
| Lloyds comparisons | [Before](previews/desktop-discovery-before.jpg) · [After](previews/desktop-discovery-after.jpg) | [Before](previews/ipad-landscape-discovery-before.jpg) · [After](previews/ipad-landscape-discovery-after.jpg) | [Before](previews/ipad-portrait-discovery-before.jpg) · [After](previews/ipad-portrait-discovery-after.jpg) | [Before](previews/mobile-discovery-before.jpg) · [After](previews/mobile-discovery-after.jpg) | [Before](previews/mobile-320-discovery-before.jpg) · [After](previews/mobile-320-discovery-after.jpg) |
| Cyber playbook excerpt | [After](previews/desktop-cyber-after.jpg) | [After](previews/ipad-landscape-cyber-after.jpg) | [After](previews/ipad-portrait-cyber-after.jpg) | [After](previews/mobile-cyber-after.jpg) | [After](previews/mobile-320-cyber-after.jpg) |
| ESG playbook excerpt | [After](previews/desktop-esg-after.jpg) | [After](previews/ipad-landscape-esg-after.jpg) | [After](previews/ipad-portrait-esg-after.jpg) | [After](previews/mobile-esg-after.jpg) | [After](previews/mobile-320-esg-after.jpg) |

Selection captures focus on the five leading priorities; remaining developed offers and the full catalogue remain available below. Cyber/ESG captures are readable excerpts, with the complete methods in [Playbooks.md](Playbooks.md) and the native optional disclosures. No general UI redesign or duplicate navigation was added.

## Sample enterprise matching assessment

Both discovery routes call the existing single `offers.assess_fit`. New programmes add an **unvalued economic hypothesis**, disconfirming evidence and conditional follow-on information, while actual `economics` remains null and `pipeline_eligible` remains false. Existing non-priority offers keep their response shape. No second matching engine, score or canonical APPA is created.

| Programme | Lloyds context / distinct first decision | easyJet / Equinix limits |
|---|---|---|
| Digital Transformation | Reported application retirement/cloud priority; test an end-to-end service outcome, benefit ownership and process-only alternatives | easyJet digital self-service is context; residual business need unknown. Equinix has no matching programme indicator. |
| AI-first Transformation | Reported data-enablement strategy; test process/role redesign, non-AI baseline and adoption/control costs | easyJet ICC/predictive support is an existing capability, not an AI transformation mandate. Equinix has no matching indicator. |
| Cybersecurity & Resilience | Existing Envoy controls weaken a greenfield pitch; test one authorised service scenario and current assurance | ICC is operational context, not a security gap. Equinix's general account context supplies no cyber trigger. |
| Complex Legacy Modernisation | Same published retirement priority, but different estate-option, vendor-rights, whole-life cost and continuity decisions | Neither easyJet nor Equinix is assigned an unsupported estate-modernisation signal. |
| Social Value & ESG | No ESG-specific account indicator; research only, no urgency or procurement claim | Research only for both other accounts. A company sector or public policy reference does not establish ESG demand. |

The 15 generated examples retain existing source claim IDs and cutoff `2026-11-13`, proposed buyer roles, unknown access/funding, existing counter-indicators and private seller status. They prove offer-led/account-led equality and differing entry plays, not lead qualification. Reported enterprise facts remain owned by the existing governed adapters and original verification/rights limits.

## Owner acceptance walkthrough

1. Open Offers → Set up my offers for an already authorised employer. Choose **Digital Transformation & Consulting**, optional overlapping categories and optional **Systems Integration**. No employer or delivery authority is granted by these preferences.
2. Search each priority name, AI-first, cybersecurity, complex legacy, social value or ESG. All five appear first for the consulting category; narrower developed offers remain reachable. Select explicitly unchecked examples and confirm seller validation responsibility.
3. Review the five private versioned drafts. Open each sales playbook to inspect outcome, target segment, buyers, economic method/costs, structural and event observables, rival/disconfirming evidence, entry plays, seller proof and gated follow-ons. No numeric value or company entitlement is prefilled.
4. Add permissioned seller delivery/rights evidence before submission. A separate reviewer must approve; old approved v1 offers remain eligible, while real source edits/withdrawals and stale parents continue to block progression. No automatic approval or upgrade.
5. Compare all five for Lloyds, easyJet and Equinix through both discovery routes. Verify Digital and Legacy ask different questions even where they use the same source context; AI and Cyber use their own relevant context; ESG remains research. Value hypotheses are qualitative/unvalued and never Pipeline contract values.
6. Use keyboard Tab/Space and native disclosures, inspect the one header Sources location, and compare desktop, both iPad orientations and phone widths. Physical Safari/screen-reader/high-zoom and human one-minute onboarding acceptance remain owner checks.

## Research and regulatory boundaries

New method references: [GOV.UK Service Standard](https://www.gov.uk/service-manual/service-standard), [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [NCSC CAF](https://www.ncsc.gov.uk/collection/cyber-assessment-framework), [Cabinet Office PPN 002](https://www.gov.uk/government/publications/ppn-002-taking-account-of-social-value-in-the-award-of-contracts), [GHG Protocol Corporate Standard](https://ghgprotocol.org/corporate-standard). Reviewed 13 November 2026; publication dates are not asserted where not established. Public links and original authored paraphrase only; no copied standard, professional certification or legal opinion.

GDS guidance is government-service context, NIST is not UK law, CAF is not automatic certification, PPN 002 is not universal UK/private/devolved procurement policy, and an inventory is not a verified emissions reduction. Social, environmental and financial measures stay separate unless an approved transparent valuation method is supplied. No actual enterprise ESG facts or procurement events are invented from these references.

## Validation and compatibility

Full local and hosted gates must validate the exact final candidate; authoritative current-head results are attached to PR #588. The explicit technology-library CI step now also runs `tests/test_flora_strategic_offers_588.py`. Existing 1,432 baseline identities, 388 strict security selection, comparator, approved failures/skips and canonical/research/Pipeline/security source owners remain unchanged.

Tests cover all 84 historic content/reference pins; five complete differentiated programmes; optional specialism validation/persistence/clearing; legacy-client compatibility; real permission and CSRF denials; independent proof/review; old approved-offer eligibility; identical shared-mode assessments; unvalued value cases; no invented ESG signal; no Pipeline write; and all original Offer/regression cases. Browser evidence covers real local HTTPS sign-in, native keyboard Space, labels, overflow, one header/source location, specialism selection, five-offer portfolio and idempotent adoption.

No migration script or production operation runs. Atomic rollback, retained source history and the original [rollback contract](../Architecture.md#rollback-and-limits) still apply. Do not roll back a populated store blindly; retain new private declarations and source history. Creative Studio remains default-off, and paid calls, autonomous research, outreach and Pipeline capture remain outside this sprint.
