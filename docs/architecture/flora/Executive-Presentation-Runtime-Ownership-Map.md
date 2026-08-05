# Executive Presentation Runtime Ownership Map

## Evidence basis

This audit inspected the unchanged fixture directly: `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip` (541,823 bytes; SHA-256 `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`). The ZIP declares `enterprise_id` `TEL-001`, package id `TEL-001_UK-Telecoms-Twin_Wave5-Corrected`, package version `5.0-corrected.import.2`, schema/manifest version `1.0`, profile version `1.0.0`, Flora contract `package-contracts/flora-blueprint-import`, Knowledge Pack `CIOS-Researcher-Knowledge-Pack-v2.8.0.zip`, generated at `2026-08-04T10:06:42Z`, and a draft release manifest `TEL-001-REL-W5-DRAFT-CORRECTED` dated `2026-08-03`. Do not infer absent metadata: deployed commit, deployment timestamp, import timestamp, staging timestamp, runtime/profile checksums and adapter/projection versions are absent from the ZIP and must be supplied by runtime fingerprinting in future.

Primary repository evidence reviewed: `docs/audits/TEL-001-Researcher-to-Flora-Translation-Audit.md`, `cios/applications/flora/blueprint_import/canonical_factual_projection.py`, `cios/applications/flora/blueprint_import/cios_twin_adapter.py`, `cios/applications/flora/blueprint_import/researcher_profile_adapter.py`, `cios/applications/flora/blueprint_import/semantic_twin.py`, `cios/applications/flora/blueprint_import/twin_governance.py`, `cios/applications/flora/blueprint_import/intelligence_projection.py`, `cios/applications/flora/blueprint_import/observation_runtime.py`, `cios/applications/flora/blueprint_import/executive_workspace.py`, `cios/applications/flora/blueprint_import/views.py`, `knowledge-packs/researcher/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json`, `cios/contracts/twin_object_profiles/researcher_v1.json`, accepted architecture including EI-012, ADR-024, FEIR-001 and EIRP-001.

## Core finding

TEL-001 implements the Researcher portable object package contract (`TOP-RESEARCHER-PORTABLE-OBJECTS-v1` by repository doctrine, Blueprint package envelope by ZIP metadata). Flora consumes that package through Blueprint manifest validation plus adapter/profile selectors, then constructs `CandidateRecord`, `SemanticTwin`, Canonical Factual Projection, page read models, owner-assessment projections, diagnostics and Research Gaps. The first consistent failing boundary is **not import**: import and staging preserve substantive families. The failing boundary is **projection ownership**: executive pages, Advanced Diagnostics, Research Gaps and owner assessments are not forced to consume one governed Canonical Factual Projection or one explicitly governed derivative.

Earlier Banking and BT experiences rendered because they used Flora-native/demonstrator structures and hand-shaped projections. They proved UI concepts, not unchanged portable Researcher package consumption.

## Required runtime trace

| Stage | Owner/path/function | Input → output | TEL-001 evidence consumed | Duplicate responsibility / first failure | Tests today |
|---|---|---|---|---|---|
| Package detection | `archive.py`, `manifest.py`, `package_contracts.py`, `validator.py` | ZIP/files → package summary | `blueprint_manifest.json`, checksums | Blueprint schema + portable profile split | integrity/validator partial |
| Adapter/profile selection | `cios_twin_adapter.py`, `researcher_profile_adapter.py`, `researcher_v1.json` | source JSON/NDJSON → family payload | `industry_overview_wave5`, dossiers, participants, programmes, opportunities, reinvention | aliases compensate contract drift | adapter/staging partial |
| Candidate staging | `candidates.py`, `validator.py`, `review.py` | payload → `CandidateRecord` | typed candidate object families | candidate class mapping duplicated with semantic constructors | staging counts partial |
| Semantic construction | `semantic_twin.py`, `twin_governance.py` | candidate records → `SemanticTwin` | object ids above | semantic classes are implementation-owned, not declared by fixture | partial |
| Canonical Factual Projection | `canonical_factual_projection.py` | `SemanticTwin` → factual cards/lines | real source fields | should be canonical read object for facts; not universal consumer | partial |
| Executive pages | `executive_workspace.py` | semantic/factual/readiness → HTML | scope, BT dossier, MP-OFCOM, programme/opportunity examples | page-specific formatting sometimes exposes dict/list structures | route snippets partial |
| Observation generation | `observation_runtime.py` | semantic object → candidate Observation | programmes more successful; evidence refs | EI-012 owner separate; not all facts are Observations | partial |
| Owner assessment | `intelligence_projection.py`, `executive_workspace.py` | owner supplied assessment state → readiness | no complete owner output supplied for many families | completeness conflict with visible facts | partial |
| Advanced Diagnostics | `executive_workspace.py`, `pilot_diagnostics.py` | semantic/readiness/raw diagnostics → HTML | source counts and runtime objects | can disagree with visible page model | partial |
| Research Gaps | `executive_workspace.py`, `research_requirements.py` | readiness/assessment → actions | Unknowns, contradictions, visible facts | source absence, unmapped field and pending owner assessment not always separated | partial |
| Recommendation eligibility | `intelligence_projection.py`, `relevance.py` | owner completeness + mission relevance | opportunities `Shape`, buyer unknown | must not infer sales readiness from candidate facts alone | partial |
