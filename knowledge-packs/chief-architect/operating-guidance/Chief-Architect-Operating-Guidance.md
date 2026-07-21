# Chief Architect Operating Guidance

**Document ID:** CA-OG-001
**Status:** Required operating guidance
**Owner:** CIOS / Chief Architect
**Last updated:** 2026-07-21

## Operating rules

1. Treat Knowledge Packs as governed exchange containers, not canonical memory.
2. Apply authority classifications before using a source: accepted ADRs and accepted/reference architecture authorities outrank proposed specifications, draft roadmap material and generated outputs.
3. Use CURRENT-PROGRAMME-STATE.md as the programme freshness source.
4. Do not infer recommendation readiness from a roadmap.
5. Block strong Recommendation outputs unless inspectable lineage, runtime baseline, programme-state baseline, Unknowns and Contradictions are present.
6. Preserve canonical acceptance boundaries for Enterprise Models, graph state, behaviour state and Observations.

## Required validation sequence

1. Verify manifest checksums.
2. Verify mandatory programme-state and runtime-baseline documents are present.
3. Verify no mandatory document is placeholder-like.
4. Verify authority classes are declared for every source.
5. Verify PACK-STATE.md cites evidence for each WP-012 deliverable and acceptance criterion.
6. Only then evaluate recommendation readiness.
