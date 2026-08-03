# Creating and Running a CIOS Research Mission

The Researcher Knowledge Pack owns the reusable method; IT-001 and its profiles own Twin structure; a mission manifest supplies operational scope. A generated commission is a derived, reproducible work order and never confers acceptance, readiness, import or promotion.

## Mission lifecycle

1. Select an active template from the catalogue.
2. Create a manifest and identify the mission, template and predecessor.
3. Define industry, geography, included/excluded domains and material-subject rule.
4. Pin every profile and release-manifest version.
5. Supply the baseline release, governed gaps, subjects, Unknowns and Contradictions.
6. For commercial missions configure H1/H2/H3, estimation, value, confidence, procurement and aggregation policy.
7. Generate the commission and retain its version and generation receipts.
8. Build and validate the Researcher Knowledge Pack.
9. Issue the generated work order and pack; do not edit the commission manually.
10. Validate returned governed records, registers, checksums and release manifest.
11. Record CONTINUE, EVIDENCE_EXHAUSTED or COMPLETE without implying governance acceptance.
12. Create a continuation or monitoring mission from the new governed checkpoint.

## Chief Architect workflow (no repository command line required)

Give Codex the mission configuration and ask it to generate and validate the commission and pack. Review the scope, pins, outputs and outcome controls; merge the reviewed change; provide the built pack to the researcher; receive the executive checkpoint and candidate package; then invoke the separately governed candidate import process when appropriate. Flora may export current state into the manifest interface, but does not own or render the methodology.

## Maintainer validation

Run `python3 tools/knowledge-packs/research_missions.py MANIFEST --output COMMISSION --check`, then build the pack. Any changed input or version requires regeneration. A stale commission fails the pack build.
