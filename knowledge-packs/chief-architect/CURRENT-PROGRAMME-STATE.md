# Current Programme State

**Document ID:** CURRENT-PROGRAMME-STATE
**Status:** Programme-state baseline
**Owner:** CIOS / Chief Architect
**As of:** 2026-07-21
**Last updated:** 2026-07-21
**Canonical source:** `knowledge-packs/chief-architect/CURRENT-PROGRAMME-STATE.md`

## Purpose

This document is the Chief Architect Knowledge Pack programme-state baseline. It records the current CIOS delivery state, not Knowledge Pack acceptance criteria. Roadmaps are planning inputs only; they must not be used as evidence that runtime, programme-state or recommendation-readiness gates are current. Knowledge Pack validation rules remain in PACK-STATE.md, source-map validation and Chief Architect operating guidance.

## Architecture baseline

CIOS is governed by the accepted reference architecture, architecture principles, Chief Architect Handbook and accepted ADRs. The active Enterprise Intelligence baseline combines EI-001 Enterprise Model, EI-002 Enterprise Knowledge Graph, EI-003 Enterprise Behaviour Model, EI-004 Commercial Reasoning Framework, EI-012 Enterprise Observation Model and EIF-001 Enterprise Intelligence Foundation Model, with FP-009 and FP-012 governing hypothesis validation and enterprise reinvention recommendations.

## Runtime baseline

The current runtime baseline is WP-011 Flora Runtime Capability Baseline, supported by FEIR-001 Flora Enterprise Intelligence Runtime Architecture, EIRP-001 Enterprise Intelligence Reasoning Pipeline Specification, ADR-014 Evidence-Governed Enterprise Intelligence Reasoning Runtime and ADR-024 Hybrid Enterprise Intelligence Runtime. Runtime evidence is the implemented Flora Enterprise Intelligence stack, retrieval pipeline, validation/audit flow, deterministic fallback and Commercial Opportunity Assistant described by WP-011.

## Active work package

WP-012 Chief Architect Knowledge Pack is the active governance work package for packaging the accepted Chief Architect authority set with a current programme-state baseline and runtime-baseline evidence. WP-011 remains the included implementation baseline and is not superseded by WP-012.

## Current delivery objective

Deliver a recommendation-ready Chief Architect Knowledge Pack that can answer architecture and governance questions against accepted sources, current delivery state and demonstrable runtime evidence without treating roadmap material or pack-acceptance text as programme state.

## Current product / twin focus

The current product focus is Flora as the first operational CIOS runtime for Enterprise Intelligence. The current twin focus is the evidence-bounded enterprise / commercial digital twin used to generate executive commercial briefs, expose observations and preserve inspectable reasoning lineage.

## Demonstrable capability

Flora can assemble bounded enterprise evidence, run the Enterprise Intelligence reasoning pipeline, produce evidence-limited executive commercial briefs, validate claims, persist audit artefacts and fall back deterministically when external provider execution is unavailable. The opportunity-assistant and observatory components provide additional commercial reasoning demonstrations while remaining separate from final sales authority.

## Work in progress

- Harden the Chief Architect Knowledge Pack validation path so every source-map identifier resolves to one manifest entry and every manifest checksum is verified before packaging.
- Keep CURRENT-PROGRAMME-STATE.md as a substantive delivery-state baseline containing architecture, runtime, product/twin and delivery fields.
- Preserve WP-011 as the single runtime implementation baseline in the pack while adding required Enterprise Intelligence authorities such as EI-004 when referenced by the source map.
- Continue reconciling draft Enterprise Intelligence papers with accepted authority classes before promoting any additional recommendation doctrine.

## Blockers

- No blocker prevents packaging the current Chief Architect Knowledge Pack once source-map resolution, checksums and substantive programme-state validation pass.
- Strong recommendation outputs remain blocked if required runtime or programme-state authorities are missing, stale, checksum-invalid or placeholder-like.

## Risks

- Programme-state drift if delivery facts are replaced by roadmap or pack-acceptance language.
- Authority ambiguity if source-map identifiers reference documents missing from the manifest.
- Recommendation overreach if draft EI authorities are treated as accepted beyond their documented authority class.
- Runtime confidence risk if provider-backed generation is assumed when only deterministic fallback evidence is available in an environment.

## Open decisions

- Decide which draft Enterprise Intelligence commercial-reasoning documents should be promoted, retained as draft authority, or excluded from recommendation doctrine.
- Decide whether a dedicated programme-state owner and refresh cadence should be added to Chief Architect operating guidance.
- Decide whether WP-011 should gain a single automated acceptance test suite for the complete runtime capability matrix.

## Next decision

Confirm whether EI-004 Commercial Reasoning Framework remains a required recommendation-doctrine source in the Chief Architect Knowledge Pack despite draft status, or whether recommendation doctrine should be narrowed to accepted/founding authorities only in a future pack version. For this baseline, EI-004 is included because source-map doctrine and WP-011 runtime evidence both reference commercial reasoning.
