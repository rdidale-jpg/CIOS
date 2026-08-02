# Executive Research Commissioning handoff

## Field lifecycle mapping

The guided form, save handler, existing profile stores, canonical `resolve_commercial_context` read contract and all three projections use the following mappings. Lists use the same trim, empty-removal, case-insensitive deduplication and display-spelling preservation rule.

| User-facing field | HTML/form field name | Request property | Canonical model property | Persistence property | Reload property | Export property | Status |
|---|---|---|---|---|---|---|---|
| Mission name | `mission_name` | `mission_name` | `CommercialMission.mission_name` | `mission_name` | `mission_name` | Mission | Correct; optional |
| Role | `executive_role` | `executive_role` | `executive_role` | `executive_role` | `executive_role` | Role | Correct |
| Geography | `geography` | `geography[]` | `geography` | `geography[]` | `geography` | Geography | Correct |
| Industries | `industries` | `industries[]` | `industries` | `industries[]` | `industries` | Industries | Corrected at normalisation/export boundary |
| Main objective | `commercial_objective` | `commercial_objective` | `commercial_objective` | `commercial_objective` | `commercial_objective` | Primary objective | Corrected label |
| Additional objectives | `objectives` | `objectives[]` | `objectives` | `objectives[]` | `objectives` | Additional objectives | Correct |
| Horizon | `commercial_horizon` | `commercial_horizon` | `commercial_horizon` | `commercial_horizon` | `commercial_horizon` | Horizon | Correct |
| Focus areas | `interests` | `interests[]` | `interests` | `interests[]` | `interests` | Focus areas | Correct |
| Priority customers | `priority_accounts` | `priority_accounts[]` | `priority_accounts` | `priority_accounts[]` | `priority_accounts` | Priority customers | Corrected export source; no longer conflated with all account fields |
| Target accounts | `target_customers` | `target_customers[]` | `target_customers` | `target_customers[]` | `target_customers` | Target accounts | Correct |
| Relevant business units | `relevant_business_units` | `relevant_business_units[]` | `relevant_business_units` | `relevant_business_units[]` | `relevant_business_units` | Relevant business units | Correct |
| Employer | `employer_organisation` | `employer_organisation` | `EmployerContext.organisation` | `organisation` | `organisation` | Employer | Correct |
| Relevant capabilities or services | `employer_capabilities` | `employer_capabilities[]` | `EmployerContext.capabilities` | `capabilities[]` | `capabilities` | Capabilities | Corrected: export reads the separate Employer Context, not the mission's empty legacy projection |
| Offers | `employer_offer_portfolio` | `employer_offer_portfolio[]` | `offer_portfolio` | `offer_portfolio[]` | `offer_portfolio` | Offers | Correct; separate from capabilities |
| Competitors | `employer_competitors` | `employer_competitors[]` | `competitors` | `competitors[]` | `competitors` | Competitors | Correct |
| Partners | `employer_partners` | `employer_partners[]` | `partners` | `partners[]` | `partners` | Partners | Correct |
| Propositions | `employer_propositions` | `employer_propositions[]` | `propositions` | `propositions[]` | `propositions` | Propositions | Correct |
| Employer description | `employer_description` | `employer_description` | `description` | `description` | `description` | Architectural/configuration appendix only | Correct |
| Target sectors | `employer_target_sectors` | `employer_target_sectors[]` | `target_sectors` | `target_sectors[]` | `target_sectors` | Configuration only | Correct |
| Credentials | `employer_credentials` | `employer_credentials[]` | `credentials` | `credentials[]` | `credentials` | Configuration only | Correct |
| Constraints | `employer_constraints` | `employer_constraints[]` | `constraints` | `constraints[]` | `constraints` | Configuration only | Correct |
| Excluded offerings | `employer_excluded_offerings` | `employer_excluded_offerings[]` | `excluded_offerings` | `excluded_offerings[]` | `excluded_offerings` | Configuration only | Correct |

The observed missing values were not submission or persistence failures. They resulted from projection/export field selection and from list deserialisation treating a legacy comma-separated scalar as an iterable. Capabilities were also vulnerable to reading the empty legacy mission-side employer projection instead of the separately persisted Employer Context.

## Applied ordering contract

Mission Emphasis is a read-only subset of the complete commission. It uses, in order: exact named priority customer or target account; an opportunity or programme explicitly linked to that account; explicit domain-to-industry equality; configured competitor or partner identity equality; an explicit structured capability/service association; and exact supported timing-to-horizon equality. Within a class, more valid explicit reasons precede fewer reasons, followed by canonical display name and existing order. It assigns no score and performs no keyword or package-proximity matching.

The complete commission is independently emitted and retains the one Industry Twin, every applicable overview dimension, every canonical enterprise, participant, programme hypothesis, opportunity hypothesis, timing subject, evidence deficiency, Unknown and Contradiction. Mission Emphasis cannot remove any item.

## Rendered evidence register

The generated Markdown export is the primary evidence for the complete commission, mission-specific reasons, researcher acceptance criteria, appendices and clean document structure. Route tests cover the configured form, persistent banner, collection summaries, counts and drill-down links. The implementation does not alter imported Twin truth, Executive Assessment Projection ownership, readiness or promotion.

## Remaining known limitations

Explicit mission emphasis is intentionally limited when imported records omit governed identity, domain, relationship, capability or timing associations. Blank offers and partners remain user configuration gaps, not researcher work. No relevance is inferred to conceal those limitations.
