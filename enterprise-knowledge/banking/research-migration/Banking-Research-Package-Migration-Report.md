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


## Knowledge Retention and Lineage Verification

- Permanent extraction is intentionally absent. The immutable source ZIP files remain under `docs/Research/`, and this PR records durable archive-member metadata without committing extracted source trees.
- Every ZIP member is inventoried in `package-validation-inventory.json`, including file and directory entries plus internal archive metadata, CRC values, and file SHA-256 values where feasible.
- Every semantically eligible source Markdown document is registered in `source-document-registry.json` with source ZIP hash, archive-member path, archive-member hash, migration status, extracted object counts, and review flags.
- Every migrated canonical object in `banking-research-canonical-objects.json` now carries source ZIP and archive-member lineage. Incomplete lineage must remain reviewable rather than inferred; the validation currently requires complete object-to-document registry agreement for retained objects.
- Unknowns and Contradictions are preserved as first-class queryable canonical objects with review status and resolution actions; they are not resolved or collapsed into prose-only summaries.
- Broken references, terminology conflicts, duplicate identifiers, and the path-casing concern are preserved in `migration-review-items.json` for owner review.
- Round-trip lineage validation is implemented in `tools/enterprise_knowledge/validate_banking_research_migration.py` and verifies `canonical_object → source_document_id → archive_member_path → source_zip_path → source_zip_sha256` for at least one object from each source ZIP.
- Remaining owner-review items include `WS0-RET-001` for canonical source path casing (`docs/Research/` exists; `docs/research/` does not), plus preserved broken references, terminology conflicts, duplicates, excluded/quarantined archive members, and semantically eligible source documents with zero extracted objects where identified by the registries.
