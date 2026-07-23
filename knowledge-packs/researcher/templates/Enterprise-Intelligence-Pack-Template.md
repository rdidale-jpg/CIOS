# Enterprise Intelligence Pack Template

**Document ID:** TEMPLATE-Enterprise-Intelligence-Pack  
**Status:** Proposed operational artefact  
**Owner:** CIOS Research Operations  
**Version:** 2.2.0

## Purpose

Provide the smallest operational shape for Enterprise Intelligence Pack output without creating new doctrine.

## Required lineage fields

- Source path or URL
- Evidence identifier
- Observation identifier
- Enterprise Model object
- Knowledge Graph relationship, where applicable
- Confidence
- Freshness
- Human-validation state
- Unknowns
- Contradictions

## Content separation

Record facts, inference, Hypotheses and Recommendations in separate sections. No strong Recommendation may exist without inspectable lineage.

## Tier 1 Enterprise Twin depth matrix

For Tier 1 enterprises, include a row for each domain with maturity score, Evidence IDs, Observation IDs, Unknowns, Contradictions and next evidence demand:

- purpose, mandate and policy outcomes;
- citizens, customers, users and beneficiaries;
- financial position, expenditure and funding pressure;
- operating and service-delivery model;
- leadership, organisation and governance;
- workforce, skills and productivity;
- technology, infrastructure and legacy estate;
- data, identity, trust and information governance;
- supplier ecosystem, contracts and procurement;
- performance, risk, resilience and behaviour;
- transformation programmes across Operate, Transform and Reinvent;
- dependencies and relationships.

Maturity rubric: 0 = not researched; 1 = superficial; 2 = evidence-backed description; 3 = integrated causal and operational understanding; 4 = decision-grade temporal and executive understanding. Tier 1 completion requires no domain below 2; finance, operating model and transformation portfolio at least 3; overall maturity at least 3; explicit evidence lineage; explicit Unknowns and Contradictions; and coherent three-horizon trajectory.
