# TEL-001 Enterprise Factual Presentation Correction

## Architectural intent

The correction reuses the existing semantic Twin and Canonical Factual Projection as the factual owner. Candidate evidence, inferred/human provenance, confidence, freshness, Unknowns and Contradictions remain factual metadata. Owner assessment and recommendation are separate owners. No new factual model or TEL-001-specific presentation model was introduced.

## Implemented runtime before

Staging and semantic construction retained substantive Enterprise dictionaries. CFP could format those dictionaries, but Enterprise list, dossier, completeness diagnostics and Research Gap surfaces made independent presence decisions. The list gated description wording on owner assessment; dossier selectors required unrelated scalar shapes; Operating Model escaped a dictionary; financial diagnostics inspected identity attributes while the dossier searched separate record kinds.

## Root causes

1. **G — fact wrongly gated by assessment:** profile display copy equated an unassessed candidate with a missing description.
2. **E — CFP to executive loss:** dossier-local selectors ignored retained identity attributes for strategy, finance, pressures, suppliers, procurements and transformation.
3. **F — executive to render loss:** scalar escaping rendered structured factual content as container syntax.
4. **Contradictory consumers:** diagnostics and dossier used different financial presence rules.
5. **I — unsupported:** Enterprise Economics and Leadership/Governance have architecture but no independent runtime dimensions.

There were no source-to-candidate, candidate-to-semantic, or semantic-to-CFP losses. Industry/domain is source absence, not a defect.

## Canonical owners corrected

* `canonical_factual_projection.py`: the existing CFP now owns a typed Enterprise dimension projection and structured executive line conversion.
* `executive_workspace.py`: Enterprise list, dossier and Advanced Inspection consume that projection. Programme and Opportunity sections continue to consume explicit relationship association truth.
* `current_pilot_change.json`: Import Twin operational acceptance describes this correction and records that no reimport is required.

## Before / after matrix

The complete 84-combination source-to-render matrix is in the companion reconciliation audit. Across each Enterprise the after state is: Profile PASS; Industry EXPECTED ABSENCE; Strategy PASS; Operating Model PASS; Financial PASS; Economics UNSUPPORTED; Pressures PASS; Leadership/Governance UNSUPPORTED; Technology PASS; Supplier/Ecosystem PASS; Programmes PASS or truthful relationship-set absence; Procurements PASS; Transformation PASS; Opportunities PASS or truthful relationship-set absence.

## Assessment separation

Candidate facts render while the dossier continues to say “Assessment not yet performed”. Rendering does not call review, promotion, assessment, Observation persistence or recommendation owners. Candidate governance and sufficiency values are asserted unchanged by regression tests.

## True absence

Industry/domain remains “Not established” because the Enterprise candidates contain no explicit semantic domain. Twin membership is not promoted into Enterprise industry evidence. Unsupported independent Enterprise Economics and Leadership/Governance are labelled architectural intent—not implemented. No other dimension is filled from a neighbouring field.

## Structured content

The shared formatter recursively converts mappings and sequences into deterministic labelled factual lines. It preserves source wording and nested meaning without emitting Python dictionaries or JSON, and without composing new prose.

## Protected capabilities

The immutable fixture checksum remains unchanged. Candidate identity propagation, 308 Relationship candidates, explicit association resolution, 13 Programmes, 17 Opportunities and candidate governance are unchanged. BT retains `PROG-BT-TRANSFORMATION`, excludes narrative-only `PROG-BT-VERIZON-JV`, and retains explicitly related `OPP-BT-VERIZON-JV-INTEGRATION`.

## Known unsupported capabilities

Independent Enterprise Economics and Leadership/Governance dimensions are not implemented in the current runtime. This correction reports `UNSUPPORTED`; it does not fake facts or silently convert that state to PASS.

## Fresh import

**NO.** The factual information was retained before persistence and already exists in current candidates. This is a read-only projection/presentation correction.
