# Banking Research Package Discovery, Validation and Migration Report

**Migration version:** `banking-research-migration-v0.1`  
**Migration timestamp:** `2026-07-19T00:00:00Z`  
**Source package directory:** `docs/Research/`  
**Source preservation:** Original ZIP files were only read and extracted to `/tmp/cios_banking_research_import2`; no source ZIP was modified.

## Package validation
- `docs/Research/banking-market-participant-intelligence-release.zip` — integrity PASS; manifest PASS; release `market-participant`; files 21; missing assets: none; malformed assets: none.
- `docs/Research/banking-offer-supplier-intelligence-release.zip` — integrity PASS; manifest PASS; release `offer-supplier-intelligence`; files 13; missing assets: none; malformed assets: none.
- `docs/Research/banking-reinvention-hypotheses-release.zip` — integrity PASS; manifest PASS; release `reinvention`; files 6; missing assets: none; malformed assets: none.

## Inventory summary
- Documents classified: 40
- Canonical object rows migrated: 81
- Evidence rows captured: 56
- Unknown rows captured: 30
- Contradiction rows captured: 15

## Cross-release analysis
- Duplicate/conflicting IDs are preserved in `cross-release-analysis.json`; no automatic repair or reconciliation was attempted.
- Terminology inconsistencies are recorded, including the requested `docs/research/` path versus actual `docs/Research/` path and the expected Commercial Position wording versus uploaded Reinvention Hypotheses release.
- Broken references are preserved where uploaded packages intentionally point to pre-existing governed assets not contained in these ZIPs.

## Governed outputs
- Deterministic package/document inventory: `enterprise-knowledge/banking/research-migration/package-validation-inventory.json`
- Cross-release analysis: `enterprise-knowledge/banking/research-migration/cross-release-analysis.json`
- Canonical migrated knowledge object store: `enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json`
