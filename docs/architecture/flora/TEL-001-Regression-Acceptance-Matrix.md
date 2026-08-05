# TEL-001 Regression Acceptance Matrix

## Evidence basis

This audit inspected the unchanged fixture directly: `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip` (541,823 bytes; SHA-256 `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`). The ZIP declares `enterprise_id` `TEL-001`, package id `TEL-001_UK-Telecoms-Twin_Wave5-Corrected`, package version `5.0-corrected.import.2`, schema/manifest version `1.0`, profile version `1.0.0`, Flora contract `package-contracts/flora-blueprint-import`, Knowledge Pack `CIOS-Researcher-Knowledge-Pack-v2.8.0.zip`, generated at `2026-08-04T10:06:42Z`, and a draft release manifest `TEL-001-REL-W5-DRAFT-CORRECTED` dated `2026-08-03`. Do not infer absent metadata: deployed commit, deployment timestamp, import timestamp, staging timestamp, runtime/profile checksums and adapter/projection versions are absent from the ZIP and must be supplied by runtime fingerprinting in future.

Primary repository evidence reviewed: `docs/audits/TEL-001-Researcher-to-Flora-Translation-Audit.md`, `cios/applications/flora/blueprint_import/canonical_factual_projection.py`, `cios/applications/flora/blueprint_import/cios_twin_adapter.py`, `cios/applications/flora/blueprint_import/researcher_profile_adapter.py`, `cios/applications/flora/blueprint_import/semantic_twin.py`, `cios/applications/flora/blueprint_import/twin_governance.py`, `cios/applications/flora/blueprint_import/intelligence_projection.py`, `cios/applications/flora/blueprint_import/observation_runtime.py`, `cios/applications/flora/blueprint_import/executive_workspace.py`, `cios/applications/flora/blueprint_import/views.py`, `knowledge-packs/researcher/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json`, `cios/contracts/twin_object_profiles/researcher_v1.json`, accepted architecture including EI-012, ADR-024, FEIR-001 and EIRP-001.

| Surface | Pass criteria using unchanged TEL-001 ZIP | Fail criteria |
|---|---|---|
| Import Twin | SHA matches; manifest validates; no ZIP mutation | checksum drift, repackage, silent repair |
| Inspect | shows package id/version, file counts, checksums, release-manifest draft status | hides missing metadata or alters source |
| Review | shows staged candidate counts for major families and unsupported lineage-only sets | silent record loss |
| Explore Twin | uses same CFP facts as pages/diagnostics/gaps | divergent counts or raw unexplained structures |
| Industry Overview | shows UK scope and `£34.7bn` economics; gaps distinguish owner assessment | says economics/scope absent |
| Enterprises | shows 6 enterprises and BT dossier facts/business units | BT facts invisible or owner pending labelled source absent |
| Market Participants | shows 17 participants and MP-OFCOM role/current activity | role/current activity reported missing |
| Major Programmes | shows 13 programmes and `PROG-BT-TRANSFORMATION` Active/FY26-FY30 | owner/stage/timing reported absent |
| Opportunities | shows 17 opportunities and `OPP-VMO2-AI-CX` customer/unit/problem; buyer Unknown remains gap | recommissions customer/unit/problem |
| Reinvention | shows all 7 `RA-*` records or precise first failing boundary | silent loss of assessment records |
| Evidence | preserves 92 evidence records as support | converts evidence directly into unsupported assertions |
| Unknowns | preserves 30 Unknowns | treats Unknown as generic missingness |
| Contradictions | preserves 11 Contradictions | hides contradictions or treats as completeness only |
| Advanced Diagnostics | agrees with page-visible facts and identifies only mapping/owner/Observation gaps | contradicts visible page content |
| Research Gaps | reason state is source absent vs unmapped vs unassessed vs Unknown/Contradiction | asks for visible candidate facts without qualification |
| Executive Intelligence | no recommendation eligibility without governed owner criteria; factual candidate content is usable | speculative recommendations or raw structures |
