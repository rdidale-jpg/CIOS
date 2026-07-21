# ADR-004: Commercial Intelligence recommendations, ranking and valuation

**Governance classification:** Product decision outside the architecture authority set; non-canonical architecture ADR; related canonical authority: ADR-004.
**Canonical architecture identifier:** None.
**Related document:** ADR-004

Status: Accepted
Date: 2026-07-19

## Decision

For Increment 4 and later Commercial Intelligence capabilities, Flora may produce commercial Recommendations, account priority, theme relevance, opportunity priority, estimated contract value and estimated pipeline value.

These outputs are transient, non-canonical, inspectable, explicitly derived, feedback-sensitive and never written directly into governed Enterprise Models as facts.

## Distinction

Flora preserves a strict distinction between governed Enterprise Intelligence, Flora commercial interpretation, Flora Recommendation, estimated commercial value, human commercial judgement and confirmed commercial outcome.

Recommendations and estimates must not masquerade as Evidence or Observation.

## Rationale

A sales-director product that never makes a commercial judgement is not useful enough. The risk of a transparent, improvable estimate is preferable to the commercial irrelevance of perpetual safe ambiguity.

Where this ADR conflicts with earlier mission constraints that categorically prohibited Recommendations, ranking or valuation, this Accepted ADR governs Increment 4 and later Commercial Intelligence capabilities.
