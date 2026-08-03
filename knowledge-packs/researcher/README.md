# CIOS Researcher Knowledge Pack

**Pack ID:** CIOS-Researcher-Knowledge-Pack  
**Version:** 2.7.0
**Owner:** CIOS / Knowledge Pack Owner

This repository-managed pack configures a Researcher to execute participant-aware Industry Twin and Commercial Digital Twin research from canonical CIOS sources. The repository remains the source of truth; the ZIP is a deterministic distribution artefact.

## Start here

1. `configuration/Researcher-GPT-Instructions.md`
2. `missions/UK-Central-Government-Industry-Twin-Mission.md`
3. `operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md`
4. `DOCUMENT-INDEX.md`

## Participant-aware intelligence

Version 2.7.0 adds reusable, versioned Research Mission templates, manifests, composed contracts and generated TEL-001 fixtures while retaining the existing Twin Object Profile and Knowledge Pack owners. It also packages the WP1-002 High-Fidelity controlled schedules alongside RG-002.

## Build

Run `python3 tools/knowledge-packs/build_researcher_pack.py --version 2.7.0 --output-dir dist` with the selected semantic version. Generated ZIP files belong in `dist/` and are release artefacts, not authoritative sources.

## Authority

Accepted ADRs and owning architecture papers remain authoritative. Review-status documents are packaged only where required to operationalise participant-aware research outputs and remain labelled with their source status. Pack files preserve source lineage through `manifest.yaml`, `source-map.yaml` and generated checksums.

## Update process

Update canonical sources first, update the manifest when source membership changes, select the next semantic version, rebuild with `--version`, run tests, review the build report and release by pushing the matching annotated tag.

## Escalation

Escalate conflicts to the Knowledge Pack owner and CIOS architecture governance. Do not silently rewrite authoritative source material inside the pack.
