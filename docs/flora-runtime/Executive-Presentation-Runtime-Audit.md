# Executive Presentation Runtime Audit — Flora Imported Twin Runtime

Date: 2026-08-05

## Recommendation: REVISE

Flora now routes imported Twin executive pages, Advanced Diagnostics, Research Gaps, owner-assessment facades and candidate Observation generation through the shared Canonical Factual Projection where factual content is displayed or diagnosed. The audit still recommends **REVISE**, not MERGE, because browser-based before/after screenshots were not produced in this non-interactive audit run and because duplicate legacy compatibility surfaces remain documented even though the implemented runtime consolidation removes the observed contradiction.

## Runtime ownership map

| Stage | Runtime owner | Canonical object consumed | Object produced | Implementation files | Duplicate responsibility |
|---|---|---|---|---|---|
| Researcher Package | Researcher / portable package contract | ZIP package documents and manifest | staged package archive | `blueprint_import/views.py`, `blueprint_import/package_contracts.py`, `blueprint_import/validator.py` | Not changed by this audit. |
| Importer | Blueprint import staging runtime | Package records | staging summary candidates | `blueprint_import/validator.py`, `blueprint_import/runs.py`, `blueprint_import/registry.py` | TEL-001 archive enrichment exists for TMS-001 only and was not modified. |
| Canonical Candidate | Semantic twin assembler | accepted staging candidates | `SemanticObject`, `SemanticEnterprise`, `SemanticTwin` | `blueprint_import/semantic_twin.py`, `blueprint_import/executive_workspace.py` | `ExecutiveRecordViewModel` remains as a compatibility selector. |
| Canonical Factual Projection | Canonical factual projection runtime | `SemanticObject` / `SemanticEnterprise` | `CanonicalFactualProjection` sections plus evidence, unknown and contradiction refs | `blueprint_import/canonical_factual_projection.py` | This is the canonical factual read model. |
| Executive Read Model | Executive workspace page runtime | `CanonicalFactualProjection` plus semantic navigation collections | deterministic HTML sections | `blueprint_import/executive_workspace.py` | Previous page-local formatting is now delegated to the shared formatter. |
| Executive Presentation | Shared executive presentation formatter | canonical factual section values | paragraphs, list items and card/table text | `blueprint_import/canonical_factual_projection.py`, `blueprint_import/executive_workspace.py` | Direct dict/list rendering was consolidated. |
| Advanced Diagnostics | Advanced Inspection runtime | same `CanonicalFactualProjection` | pipeline trace with exact factual counts | `blueprint_import/executive_workspace.py`, `blueprint_import/pilot_diagnostics.py` | Diagnostics still contains pilot-only comparison panels, but factual counts now come from the canonical projection. |
| Research Gaps | Research requirements adapter | semantic subjects, owner assessment projections, source field dispositions | human research requirements | `blueprint_import/research_requirements.py`, `blueprint_import/executive_workspace.py` | It no longer recommissions fields classified as supplied but unassessed. |
| Owner Assessment | Executive assessment projection facade | semantic twin inventory | `ExecutiveAssessmentProjection` / `ReadinessAspect` | `blueprint_import/intelligence_projection.py`, `blueprint_import/executive_workspace.py` | Completeness remains owner-supplied; Flora does not calculate a competing score. |
| Recommendations | Recommendation boundary | owner assessment eligibility | no recommendation for candidate factual projection | `blueprint_import/executive_workspace.py` | No recommendation path is created by this consolidation. |

## Answers to audit questions

1. Raw Python-style dictionaries and lists were exposed because page cards and diagnostics rendered structured values directly from semantic attributes or view-model fields. Formatting belongs in a shared executive presentation layer immediately after Canonical Factual Projection and before HTML card/table construction. This audit adds `executive_value_lines()` as that deterministic formatter and reuses it from executive pages.

2. Advanced Diagnostics disagreed with rendered pages because diagnostics previously reported `executive_record_view_model` field counts while pages displayed Canonical Factual Projection cards for several families. Diagnostics now reports Canonical Factual Projection section counts and evidence/unknown/contradiction counts for the same object consumed by displayed pages and Observation generation.

3. Enterprise diagnostics showed `fields projected 0` / `projection omitted` when the legacy `ExecutiveRecordViewModel` had no selected fields, even though the Enterprise page rendered factual projection content through `factual_projection_for_enterprise()`. The divergence occurred at the diagnostics row labelled Executive projection. That row now reports Canonical Factual Projection sections instead of legacy view-model fields.

4. Research Gaps evaluate semantic subjects plus owner assessment projections and field dispositions. The authoritative layer for factual presence is the imported semantic candidate as presented through Canonical Factual Projection; the authoritative layer for pass/fail readiness remains owner assessment. Research Gaps must commission only absent, invalid, contradicted, unsupported or explicit Unknown fields, not fields that are supplied but pending owner assessment.

5. Executive pages had page-local presentation paths for industry, enterprise, programme, opportunity, market participant and reinvention assessment families. The consolidation keeps navigation-specific layouts but centralises structured value formatting and diagnostic factual counts through the Canonical Factual Projection runtime.

## Supported Twin Object family comparison

| Family | Canonical factual projection produced | Executive presentation produced | Diagnostics presentation | Research Gap evaluation | Owner assessment input |
|---|---|---|---|---|---|
| Industry Overview | Industry sections, evidence refs, unknown refs, contradiction refs | Canonical factual card and overview sections | Canonical section/evidence/unknown/contradiction counts | Industry Fidelity schedule dispositions | `executive_assessments(twin)` |
| Enterprise Dossier | Enterprise identity factual sections with aggregate evidence/unknown/contradiction refs | Enterprise dossier card and detail page | Canonical Enterprise projection counts | Enterprise subject-type schedule dispositions | `executive_assessments(twin)` |
| Programme | Programme factual sections | Programme canonical factual cards | Canonical Programme projection counts | Change Landscape schedule dispositions | `executive_assessments(twin)` |
| Opportunity | Opportunity factual sections | Opportunity factual cards and sales-ready table where owner/use contract allows | Canonical Opportunity projection counts | Opportunity Completeness schedule dispositions | `executive_assessments(twin)` |
| Market Participant | Generic factual sections from executive fields | Participant cards with shared structured formatting | Canonical Market Participant projection counts | Participant classification schedule dispositions | `executive_assessments(twin)` |
| Reinvention Assessment | Generic factual sections for assessment records | Reinvention factual cards | Canonical factual counts when record kind is supported | Temporal Fidelity schedule dispositions | `executive_assessments(twin)` |

## Canonical presentation pipeline

```text
Researcher Package
  -> Blueprint Importer / Validator
  -> Canonical Candidate staging records
  -> SemanticTwin assembly
  -> CanonicalFactualProjection
  -> Shared executive value formatter
  -> Executive pages / Advanced Diagnostics / Observation generation / Research Gaps traces
  -> Owner Assessment and Recommendations remain additive governed layers
```

## Runtime duplication analysis

- Multiple factual projections: Canonical Factual Projection is the canonical factual read model; `ExecutiveRecordViewModel` remains only as a legacy field selector and should not own factual completeness or diagnostic truth.
- Multiple executive projections: Page-specific cards remain, but they now share factual value formatting. Future work should move all family card assembly into a `canonical_executive_presentation` module.
- Multiple completeness calculations: Research Gaps translate owner-supplied deficiencies and source dispositions; `research_count_contracts()` is a count contract, not a completeness score.
- Multiple observation builders: candidate Observation generation uses `ImportedTwinSemanticObservationBuilder` and consumes Canonical Factual Projection; no new builder was introduced.
- Multiple presentation paths: navigation/page composition remains per page; structured field formatting is consolidated.

## Screenshot evidence

Screenshots were not produced in this run. Required targets for a full browser acceptance pass are: Industry, Enterprise, Programme, Opportunity, Market Participant, Research Gaps and Advanced Diagnostics before and after the consolidation.
