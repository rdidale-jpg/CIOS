# CIOS Researcher Knowledge Pack

**Pack ID:** CIOS-Researcher-Knowledge-Pack  
**Version:** 2.1.0  
**Owner:** CIOS / Knowledge Pack Owner

This repository-managed pack configures a Researcher to execute Industry Twin and Commercial Digital Twin research from canonical CIOS sources. The repository remains the source of truth; the ZIP is a deterministic distribution artefact.

## Start here

1. `configuration/Researcher-GPT-Instructions.md`
2. `missions/UK-Central-Government-Industry-Twin-Mission.md`
3. `operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md`
4. `DOCUMENT-INDEX.md`

## Build

Run `python3 tools/knowledge-packs/build_researcher_pack.py`. Generated ZIP files belong in `dist/` and are release artefacts, not authoritative sources.

## Authority

Accepted ADRs and owning architecture papers remain authoritative. Pack files preserve source lineage through `manifest.yaml` and generated checksums.

## Update process

Update canonical sources first, update the manifest when source membership changes, rebuild, run tests, review the build report and release a new semantic version.

## Escalation

Escalate conflicts to the Knowledge Pack owner and CIOS architecture governance. Do not silently rewrite authoritative source material inside the pack.
