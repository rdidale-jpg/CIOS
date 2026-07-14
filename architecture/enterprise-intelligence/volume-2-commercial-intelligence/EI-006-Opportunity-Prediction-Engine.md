# EI-006 — Opportunity Prediction Engine

**Purpose:** Define how CIOS predicts where commercial opportunities may emerge.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons over evidence and signals. Flora is the first runtime implementation that combines both into operational intelligence.

## Purpose

Define how CIOS predicts where commercial opportunities may emerge. This paper is documentation-only and avoids runtime implementation detail.

## Why opportunity prediction exists

Why opportunity prediction exists describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Inputs

Inputs include enterprise economics, transformation pressure, leadership change, supplier position, procurement activity, relationship access, competitive movement, evidence quality and provider fit.

## Opportunity themes

- Likely opportunity theme
- Likely business owner
- Likely technology owner
- Likely budget owner
- Likely procurement route
- Likely timing window
- Likely value range where inferable
- Incumbent supplier position
- Competitive landscape
- Provider fit
- Relationship access
- Commercial attractiveness
- Opportunity confidence
- Recommended shaping action

## Opportunity timing

Opportunity timing describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Opportunity ownership

Opportunity ownership describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Procurement route prediction

Procurement route prediction describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Value estimation

Value estimation describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Provider fit

Provider fit describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Competitive position

Competitive position describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Confidence and unknowns

Confidence and unknowns describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Relationship to recommendations

Relationship to recommendations describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Open questions

- What additional evidence types should strengthen this model?
- Which confidence thresholds should be standardised across EI papers?
- How should user feedback update this part of the Commercial Digital Twin?

## Review interfaces for Opportunity Twin positioning

EI-006 remains the owner for Opportunity Prediction and Opportunity Twin logic. The current Review interface material beneath EI-006 is:

- **OT-001 — Opportunity Twin Specification:** defines the Review Opportunity Twin object and interface shape.
- **OPI-001 — Opportunity Positioning Intelligence:** contributes candidate positioning objects to the Opportunity Twin.
- **RTP-001 — Research-to-Positioning Input Contract:** defines the governed handover from Research to Positioning.

These relationships are explicit Review interfaces, not Unknown relationships. OPI-001 candidate positioning objects and RTP-001 handover fields remain Review material pending wider validation. They do not change runtime behaviour, production Researcher profiles or production Assurance profiles, and they do not mark OT-001, OPI-001 or RTP-001 as Accepted.
