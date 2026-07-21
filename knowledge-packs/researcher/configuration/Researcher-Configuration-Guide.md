# Researcher Configuration Guide

**Document ID:** RKI-002  
**Status:** Operational configuration guide  
**Owner:** CIOS / Knowledge Pack Owner  
**Version:** 2.2.0

Use `Researcher-GPT-Instructions.md` as the behavioural operating kernel. Upload the built ZIP as the Researcher's governed knowledge source and keep this guide for setup only.

## Setup

1. Build the pack with `python3 tools/knowledge-packs/build_researcher_pack.py`.
2. Upload the generated `dist/CIOS-Researcher-Knowledge-Pack-vX.Y.Z.zip` for the governed release version to the Researcher configuration.
3. Paste or attach `configuration/Researcher-GPT-Instructions.md` as the primary instruction file.
4. Use the mission brief only to scope the UK Central Government Industry Twin mission.
5. Do not add untracked local bundles unless the manifest is updated and validated.

## Refresh

When canonical documents change, update `manifest.yaml`, rebuild, review the build report, and release a new semantic version.
