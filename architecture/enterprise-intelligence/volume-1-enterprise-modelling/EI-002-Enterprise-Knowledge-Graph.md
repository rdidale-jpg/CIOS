# EI-002 — Enterprise Knowledge Graph

**Purpose:** Define entities, relationships and evidence-backed links that connect the enterprise model.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons over evidence and signals. Flora is the first runtime implementation that combines both into operational intelligence.

## Purpose

Define entities, relationships and evidence-backed links that connect the enterprise model. This paper is documentation-only and avoids runtime implementation detail.

## Why a graph is needed

Why a graph is needed describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Core entities

- Enterprise
- Business Unit
- Executive
- Board Member
- Committee
- Programme
- Transformation Theme
- Technology Platform
- Supplier
- Contract
- Procurement
- Framework
- Regulator
- Competitor
- Market Force
- Risk
- Financial Metric
- Cost Category
- Evidence
- Source
- Hypothesis
- Recommendation
- Commercial Outcome

## Core relationships

- Enterprise HAS_EXECUTIVE Executive
- Executive OWNS Programme
- Programme USES Technology Platform
- Enterprise CONTRACTS_WITH Supplier
- Supplier DELIVERS Contract
- Contract EXPIRES_ON Date
- Regulator PRESSURES Enterprise
- Evidence SUPPORTS Hypothesis
- Evidence CONTRADICTS Hypothesis
- Financial Metric INDICATES Pressure
- Cost Category CREATES Transformation Pressure
- Procurement SIGNALS Opportunity
- Executive PREVIOUSLY_WORKED_AT Organisation
- Board Member SITS_ON Committee
- Competitor THREATENS Business Unit

## Evidence-backed edges

Evidence-backed edges describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Inferred edges

Inferred edges describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Confidence and uncertainty

Confidence and uncertainty describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Temporal behaviour

Temporal behaviour describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Contradictions

Contradictions describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Relationship decay

Relationship decay describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Graph updates

Graph updates describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Query patterns

Query patterns describes the architectural expectations for this part of the Enterprise Intelligence model. It should be evidence-linked, freshness-aware and distinct from CIRM process mechanics. CIRM explains how CIOS reasons; this section defines what CIOS should know about the enterprise.

## Open questions

- What additional evidence types should strengthen this model?
- Which confidence thresholds should be standardised across EI papers?
- How should user feedback update this part of the Commercial Digital Twin?
