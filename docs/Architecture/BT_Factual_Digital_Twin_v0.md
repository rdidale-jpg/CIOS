# BT Factual Digital Twin v0

## Factual scope

The BT foundation twin models factual state before commercial reasoning: identity, organisational structure, financial performance, strategy and leadership.

## Domain definitions

- **Identity:** legal name, sector, geography, listing, reporting currency and financial year.
- **Structure:** group, reporting segments, business units, operating units, internal capabilities and brands.
- **Financial performance:** group and segment metrics, periods, units, status and reporting basis.
- **Strategy:** stated purpose, ambition, pillars, commitments, measures and target dates.
- **Leadership:** current, historical and announced roles with effective dates where evidenced.

## Required attributes

Coverage is calculated from required attributes per domain. Coverage is not confidence; confidence remains attached to Evidence, Observations and model attributes.

## Source set

The BT baseline profile includes Annual Report 2026, FY26 full-year results, strategy, organisation disclosure and leadership sources. PDF sources are handled as authoritative documents rather than rejected as non-HTML.

## Maturity gates

- **Not established:** insufficient factual model; suppress commercial scores and recommendations.
- **Foundation:** identity, structure, financials, strategy and leadership populated with lineage.
- **Structured:** broader temporal factual coverage supports comparisons.
- **Behavioural:** repeated history supports behaviour interpretation.
- **Commercial:** commercial accessibility evidence supports opportunity qualification.

## Coverage model

Each domain reports expected, populated, unsupported, stale and contradicted attributes plus source count. The model can reach Foundation without implying Behavioural or Commercial maturity.

## Drill-down hierarchy

The workspace follows: group overview → domain views → attribute detail → Evidence detail. Attribute detail exposes current value, state, period, confidence, previous values, Observation IDs, Evidence IDs and page references.

## Deferred domains

The sprint does not implement the full Commercial Digital Twin, Knowledge Graph infrastructure, prediction, supplier intelligence, procurement intelligence or recommendation redesign.

## Acceptance process

Accepted facts must flow from authoritative document to governed Evidence, atomic Observation, Enterprise Model attribute and navigable Digital Twin view. Targets, guidance and actuals remain distinct temporal objects.
