# ADR (Proposed): FLORA Visual Intelligence & Macro-to-Pursuit Context Graph

**Status:** Proposed / architectural review (not accepted, no runtime or schema migration)
**Date:** 2026-11-11
**Scope:** FLORA product-wide; cross-sector (Banking and Aviation initially), future sectors and enterprise pursuits
**Related:** issue #558, PR #557, design-only PR #559, integration PR #561; new implementation issue to follow

## 1. Decision proposition

Adopt **visual-first progressive intelligence** as a product-wide UX contract, and introduce a **Macro Intelligence** context layer that allows traceable systemic forces to be investigated through industry PESTLE, enterprise exposure/response, commercial hypotheses, and an authorised pursuit.

The macro layer is **logically above** Industry in the user journey, but **many-to-many across** industries and enterprises in the data model. It is NOT a fixed hierarchical parent, an independent source-of-truth, a second research engine, an unverified ontology, or an opportunity creation shortcut.

**Canonical journey:** Macro force → industry interpretation → enterprise-specific exposure/response → research hypothesis → deliberate authorised Pipeline capture → customer-validated pursuit. Each transition is an explicit typed, scoped, dated, traceable edge, or remains Unknown.

The canonical existing evidence spine (SourceSegment, CandidateClaim, reviews, immutable captured source references) and stage/permission contracts remain authoritative. Existing Industry/Enterprise/Opportunities/Pipeline routes remain supported; Macro is an additional entry point.

## 2. Product design charter

**Simple by default. Powerful through exploration. Rigorous in evidence.**

Each substantive intelligence screen shall implement:
- **SEE:** a memorable, high-quality visual anchor, not a decorative picture placed above a report.
- **UNDERSTAND:** selecting a visual node reveals a high-signal 4-part summary: *what matters; why it matters; what is known/uncertain; what next*.
- **EXPLORE:** purposeful, visually meaningful contextual drill-through into relationships, dates, stakeholders, alternatives and commercial consequences.
- **INVESTIGATE:** explicit full research/evidence report, complete source provenance, counterevidence and historical versions.
- **ACT:** an appropriate controlled action (research question, qualification task, or authorised Pipeline capture). Actions never imply qualification merely because a user clicks.

Only **one primary contextual inspector** should be visible; avoid repeated full cards, text-heavy accordions and duplicated dossiers on the default screen. All substantive claims remain accessible through keyboard, screen reader, non-JS meaningful fallback and separate executive/full-evidence print. Visual presentation cannot suppress counterevidence or change source facts.

Three personas, one adaptable experience: newcomer selling an offering and requiring rapid industry orientation; domain expert seeking deep detail; intermediate operator combining both. Depth is progressive, not separate incompatible modes. Optional expertise preference may speed navigation but must not alter evidence or authorisation.

**Commercial relevance:** User-approved seller offerings/capabilities (e.g. cyber services or AI integration) may highlight matching macro forces, industries, enterprises and hypotheses. Matching outputs are *seller fit / analytical relevance*, not customer demand, estimated TCV, win probability, contractual status or a qualified lead. Explain *why matched* and *what would disconfirm*.

## 3. Conceptual taxonomy (not a legal taxonomy)

Navigation domain categories:
1. Cybersecurity & systemic resilience
2. Sustainability, ESG & public social value
3. AI, digital & technology change
4. Economy, finance & geopolitics
5. Demographics, workforce & society
6. Public policy, legal & regulation

Each force can have multiple tags. Deduplicate on stable subject/event identity and the governing instrument where applicable; do not create independent duplicate records for cyber regulation vs cyber threats.

Classify the **force type** separately from domain tags: `observed_trend`, `threat_or_scenario`, `policy_priority`, `proposed_legislation`, `enacted_law`, `regulatory_rule`, `contractual_requirement`, `voluntary_standard`, `corporate_commitment` or `analyst_scenario`. This is an initial proposed enum, not an approved software schema. Distinguish a requirement's legal force from the enterprise's applicability.

## 4. Graph entities and typed relationships (conceptual projection)

Use existing canonical entities and IDs wherever present. Minimum additions for design/prototyping:
- `MacroForce`: stable ID, concise title/description, kind, thematic tags, jurisdiction, sector scope, applicable entity types, status/effective period, publication date vs announcement vs retrieval date, owner, linked source/evidence refs, limitations, version lineage.
- `ImpactAssessment`: a scoped analyst interpretation connecting a macro force to a specific industry PESTLE factor or industry capability, with mechanism, direction, magnitude **only if justified**, timeframe, status, claim/source refs, conflicts and explicit uncertainty.
- `EnterpriseExposure`: source-supported or explicitly interpreted applicability of an impact to an enterprise/legal entity/business capability/programme, with ownership status (verified/inferred/unknown), affected outcomes, evidence and counterevidence; **not** automatic corporate responsibility or supplier demand.
- `SellerCapabilityMatch`: reversible private/user-approved relevance projection tying offerings to possible services/hypotheses, with rationale and fit uncertainty; does not alter public truth or Pipeline.
- Existing `CommercialCandidate` and Pipeline opportunity remain canonical; no duplicate store.

Proposed typed edges:
`MACRO_FORCE -[AFFECTS / EXPLAINS, interpreted]-> INDUSTRY_PESTLE`
`INDUSTRY_PESTLE -[IMPACTS, interpreted]-> INDUSTRY_ACTIVITY_OR_CAPABILITY`
`INDUSTRY_CONTEXT -[APPLIES_TO, verified/inferred/unknown]-> ENTERPRISE_OR_ENTITY`
`ENTERPRISE_ENTITY -[RESPONDS_WITH, evidenced or unverified]-> PROGRAMME_OR_CAPABILITY`
`ENTERPRISE_CAPABILITY -[MOTIVATES_INVESTIGATION, interpreted]-> COMMERCIAL_HYPOTHESIS`
`SELLER_OFFERING -[MATCHES_POTENTIAL_SERVICE, interpreted]-> COMMERCIAL_HYPOTHESIS`
`COMMERCIAL_HYPOTHESIS -[CAPTURED_AS, authorised action]-> PRIVATE_PIPELINE_RECORD`

Do not infer the latter edge from the existence of any upstream link. Preserve direction and the distinction between cause, relevance, documented response, programme intent and verified service gap. Never draw a solid verified contractual dependency based solely on a diagram edge.

### Required edge metadata
Stable IDs; subject/object IDs; relationship predicate; explicit entity and geographic scope; validity/effective period; observed or publication time; assessment time; source/claim IDs and exact locator; evidence status; analytical vs factual classification; source limitations; counterevidence/contradiction IDs; supersession lineage; owner/reviewer; snapshot/digest and immutable capture rules. Handle regulatory transitional and grandfathered regimes explicitly.

## 5. Example: social value → public sector

At 11 Nov 2026, UK Cabinet Office PPN 026 (published 28 Oct 2026) specifies a new Social Value Model for *in-scope* central-government bodies and new covered procurements of £1m+ from 1 Jan 2027, with framework/transitional considerations. This is a **specific procurement-policy force**, not generic mandatory ESG for all firms or bids.
Primary URL: https://www.gov.uk/government/publications/ppn-026-the-social-value-model/guidance-on-using-ppn-026-the-social-value-model-html

Proposed trace (must be investigated for each organisation and procurement): macro policy → public-sector PESTLE (Political / Legal / Social) → procurement evaluation processes / supplier deliverables → a specific in-scope authority and contract framework → customer/procurement requirements and evidence → potential *seller* service or bid differentiation. This may be a **win requirement** rather than a standalone revenue opportunity. Do not infer legal duty for every buyer or a new project budget.

## 6. Example: UK listed-company sustainability disclosure → banking

FCA PS26/19, published 30 Sept 2026, introduces comply-or-explain UK SRS S1/S2 reporting from accounting periods beginning 1 Jan 2027 for specified listing categories, with rule detail. Do not imply this applies identically to every Lloyds subsidiary, regulated bank or private company.
Primary URL: https://www.fca.org.uk/firms/climate-change-sustainable-finance/reporting-requirements

Trace: macro regulatory rule → Banking PESTLE Legal/Environmental → listed issuer reporting/data/assurance process → check precise listed legal entity and applicability → enterprise data, reporting and controls capability → possible evidence-based delivery hypothesis → buyer/competitors/funding validation. Separate climate disclosure duty from social-value procurement policy.

## 7. Example: cyber threat + developing cyber law → banking, aviation, critical services

Cyber threat is a **risk/scenario with evidence and probabilistic uncertainty**, while the Cyber Security and Resilience (NIS) Bill is a **proposed law**, not automatically enacted law as at 11 Nov 2026; after Lords third reading it returned to the Commons for consideration of amendments.
Primary URLs: https://bills.parliament.uk/bills/4035 and https://www.parliament.uk/business/news/2026/october-2026/cyber-security-and-resilience-bill-lords-third-reading/

Trace separate but related force records to industry PESTLE Technology/Legal/Political, then industry critical workflows and supplier dependencies, then enterprise-specific business processes and governance. The same threat creates different exposure in a bank, airline, critical service or government department. No automatic evidence of a vulnerability, regulatory breach, named incumbent or addressable services contract.

## 8. Visual grammar and interaction

- **Macro screen:** memorable systemic-force atlas; visually prioritise importance only through disclosed methodology and evidence, never arbitrary scores; topic chips are filters, not proof.
- **Industry screen:** retained main illustrated map and PESTLE; select a macro force to illuminate relevant framework nodes, affected activities, enterprise illustrations and evidence links. Industry implications are scoped interpretations, not facts for every organisation.
- **Enterprise screen:** existing visual operating model with selected force/industry pressure overlays, verified/unknown entity applicability, programme/capability response and hypothesis markers. Labels distinguish research capability vs actual business-unit/organisation owner.
- **Opportunity screen:** short causal narrative showing force/industry/enterprise/outcome lineage, separate strategic relevance, evidence and access, principal disconfirming alternative, visible next action; one contextual inspector.
- **Pursuit screen:** 8 Shipley-inspired modules with visual stakeholder network, financial value model, hot buttons, competitor landscape, win strategy, and execution where supported; editable only inside existing authorised private workspace and after schema/audit review.
- Deep links preserve selection and breadcrumb `Macro → Industry → Enterprise → Opportunity`, and a user can reverse trace from opportunity to systemic driver.
- All visual nodes and edges must have a non-visual list/table equivalent with matching semantics. Avoid an image-only or canvas-only truth surface.

## 9. Non-functional / governance rules

1. No parallel evidence store, duplicate authority, opportunity engine, or inferred qualification.
2. Jurisdiction, instrument status, effective dates, exemptions/transitions, covered organisation/entity, and source version are mandatory for claims of legal or regulatory applicability.
3. Retrieval date is never publication/effective date; enacted vs proposed and disclosure vs compliance are distinct.
4. Unknown ownership, budgets, contracts, technologies, actual exposure and buyer urgency stay Unknown.
5. Analysts can challenge/disconfirm impact mechanisms; contradiction is displayed, not quietly averaged away.
6. Private seller profile, customer intelligence and pursuit notes are workspace-scoped; no public-store leakage.
7. Reuse the current authorisation, immutable capture, duplicate-capture and Pipeline stage gates.
8. Performance/accessibility: progressively loaded details, screen-reader descriptions, keyboard/touch, reduced motion, no-JS fallback, high-quality tablet view, and distinct executive/full print.
9. Versioned, deterministic visual specifications and explicit acceptance tests prevent invented edges, misleading statuses and dropped evidence.

## 10. Phased delivery, separate from ongoing PR #561

**Phase A — architecture acceptance:** Review this ADR, classify key statuses/typed relationships, validate industry/enterprise visual placement; no runtime or data writes.

**Phase B — tiny cross-sector pilot:** Three macro themes (PPN 026 social value; FCA PS26/19 sustainability reporting; cyber resilience threat plus proposed law) traced to Banking and Aviation. Use bounded official primary documents. Show one illustrative Lloyds and one easyJet *candidate* effect only where evidence supports the entity scope. If evidence lacks enterprise applicability, stop at industry and display Unknown. Preserve existing PESTLE/industry functions.

**Phase C — visual UX:** Macro atlas + Industry PESTLE pressure overlay + Enterprise visual highlights + reverse trace into existing hypothesis. Validate novice/intermediate/expert journeys. Match FLORA's illustrated design style rather than adding large text sections.

**Phase D — seller-fit:** Explicitly user-approved capability/offering inputs highlight relevant hypotheses. Explain fit; do not auto seed Pipeline.

**Phase E — pursuit evolution:** Only after user, permissions and schema reviews, extend the existing private Pipeline with structured commercial financials, organisation business owners, stakeholder hot buttons, competition and capture activity.

Each phase requires draft PR, test evidence, screenshots, preserved existing Banking/Aviation identities and architecture reuse review. Do not merge/deploy as part of acceptance of this ADR.

## 11. Product acceptance questions

- **20-second novice:** Can a seller new to an industry understand its core structure, key systemic forces and where the seller's offering might matter?
- **Expert:** Can an industry specialist skip orientation and inspect precise scope, dated source evidence, contradictions, exposure and an actionable commercial hypothesis?
- **Intermediate:** Can the user change depth without losing context?
- **Evidence:** Can every visual edge be explained with facts/interpretations/unknowns and primary provenance?
- **Commercial:** Can a user distinguish a macro trend from a customer-validated opportunity and proceed only through authorised capture?
- **Design:** Is the visual memorable and genuinely interactive, with concise insight rather than a long scroll of accordions?

**Decision pending:** architecture/UX owner review, including nomenclature for the proposed Macro Intelligence navigation layer; no claim of adopted architecture or implemented features.
