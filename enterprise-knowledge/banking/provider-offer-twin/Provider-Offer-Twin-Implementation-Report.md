# Provider Offer Twin Implementation Report

## 1. Purpose

This report introduces the first governed Provider Offer Twin and Commercial Reasoning foundation for the Banking reference implementation. It uses the migrated Banking canonical object store as the only source corpus for initial provider-side seed objects.

Enterprise Need, Provider Capability, Provider Offer, Provider Fit, Commercial Accessibility, Commercial Conviction and Recommendation remain separate governed objects.

## 2. Architecture decision implemented

The implementation establishes the provider-side half of Enterprise Intelligence:

```text
Enterprise Twin + Provider Offer Twin + Commercial Reasoning = Enterprise Intelligence
```

The current PR does not implement runtime Flora reasoning. It persists schemas, seed objects, relationships, validation rules and owner-review hooks so that later reasoning can operate over governed, lineaged objects.

## 3. Object model introduced

The Provider Offer Twin schema introduces Provider, Provider Capability, Provider Offer, Offer Variant, Provider Proof, Provider Constraint and Partner Dependency. The Commercial Reasoning schema introduces Provider Fit, Commercial Accessibility, Commercial Conviction and Recommendation.

## 4. Concept separation rules

Provider Capability describes what a provider can do. Provider Offer describes a market-facing proposition. Provider Fit assesses capability and/or offer relevance to an enterprise need. Commercial Accessibility assesses route, timing, procurement, incumbency and relationship access. Commercial Conviction synthesises need, fit, accessibility, evidence, timing and constraints into an explainable decision posture. Recommendation is not valid without a Commercial Conviction reference.

## 5. Relationship model

Canonical relationships registered by the foundation include:

- Provider HAS_CAPABILITY ProviderCapability
- ProviderCapability EXPRESSED_AS ProviderOffer
- ProviderOffer HAS_VARIANT OfferVariant
- ProviderOffer SUPPORTED_BY ProviderProof
- ProviderCapability SUPPORTED_BY ProviderProof
- ProviderOffer CONSTRAINED_BY ProviderConstraint
- ProviderCapability CONSTRAINED_BY ProviderConstraint
- ProviderOffer DEPENDS_ON PartnerDependency
- ProviderCapability DEPENDS_ON PartnerDependency
- ProviderCapability FITS_ENTERPRISE_NEED EnterpriseNeed
- ProviderOffer ADDRESSES_ENTERPRISE_NEED EnterpriseNeed
- ProviderFit ASSESSES Provider + EnterpriseNeed + OpportunityCandidate
- CommercialAccessibility ASSESSES Provider + OpportunityCandidate + RouteToMarket
- CommercialConviction SYNTHESISES EnterpriseNeed + ProviderFit + CommercialAccessibility + EvidenceStrength + Timing + Constraints
- Recommendation REQUIRES CommercialConviction

## 6. Banking reference implementation

The initial Banking seed is deliberately small. Google Cloud is mapped as a Provider from migrated public evidence entries. A data and AI cloud Provider Capability, Provider Proof and Provider Constraint are created from the same migrated evidence and related unknown / contradiction objects. No Provider Offer is created because the migrated canonical store does not expose enough structured offer detail to define a sellable Banking offer without inventing facts.

## 7. Source lineage behaviour

Every seeded provider-side object carries lineage back to canonical migrated object IDs and, through those records, to source ZIP paths, source ZIP hashes, archive member paths and archive member hashes where available. Partial commercial reasoning lineage is preserved and marked for owner review rather than silently repaired.

## 8. Unknowns and Contradictions handling

Unknowns and contradictions remain queryable through their migrated canonical object IDs or through the Provider Offer Twin review register. Commercial reasoning objects reference unknown and contradiction IDs directly, preserving the evidence gaps that prevent strong recommendations.

## 9. Validation approach

The deterministic validator checks stable IDs, object type presence, lineage, confidence, review status, conceptual separation between capability, offer, fit, accessibility and conviction, recommendation lineage requirements, unknown / contradiction referential integrity, canonical-store traceability and owner-review marking for partial lineage.

## 10. Remaining owner-review items

Owner review is required for provider objects with partial commercial lineage, unsupported migrated claims, unresolved provider/supplier terminology conflicts, fit assessments blocked by missing enterprise need linkage, accessibility assessments blocked by missing procurement or relationship evidence and conviction records downgraded because lineage is incomplete.

## 11. Next implementation step toward Flora reasoning

The next step is to bind EnterpriseNeed and OpportunityCandidate identifiers to provider fit candidates through a Flora-readable reasoning layer that can traverse Provider Proof, Provider Constraint, Commercial Accessibility and Commercial Conviction without collapsing them into a single score.
