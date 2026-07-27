# WP1-004 — TMS-001 governed import compatibility assessment

## Assessment and owner decision

The authoritative fixture is `enterprise-knowledge/TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip` (SHA-256 `25e8ef0f49b4320e3fff2b347b06708ed231a670b5497a7402abf7ca26380371`). It has one wrapper root, a governed `00_manifest.json`, 47 declared members with byte counts and SHA-256 hashes, and `21_industry_twin_delta_for_flora.json`. The source ZIP is preserved unchanged.

The package is supportable without weakening governance. Its Delta is a projection of stable identifiers rather than the generic inline/`primary_objects` shape already understood by Flora. The smallest owner-aligned correction is therefore an adapter-side TMS inventory projection, not an importer redesign or package rewrite. Flora continues to own receipt, archive, inspection, staging, review, reconciliation and explicit promotion. IT-001/TMS-001 retains release meaning, including the package's **Research-ready with conditions** and **not promotion-ready** declarations; import compatibility does not elevate either status.

## Artefact classification

Every ZIP member is persisted in `package_inspection.artefact_classification`; the following rules give the canonical owner and treatment for every class.

| Class | Package artefacts | Canonical owner | Import treatment |
|---|---|---|---|
| Promotable canonical candidate | HFT object, fact, relationship and uncertainty inventories; source evidence register; reasoning lineage; Flora Delta | Enterprise Intelligence authorities | Project stable-ID records only, validate relationship endpoints, stage and require review/approval. The Delta itself controls projection but is not duplicated as a canonical object. |
| Supporting evidence or lineage | Source/evidence registers | Evidence authority | Stage individual evidence records with package checksum and source-file lineage. |
| Derived decision or presentation output | Executive intelligence/briefs, ranked opportunities, AI/maturity/completeness products, navigation index, mission summaries and README material | Producing decision/presentation authority | Retain in immutable package lineage; exclude from canonical staging to avoid duplicate objects and status elevation. |
| Mission or workspace state | Final/HFT workspaces, restart state, checkpoints and research queue disposition | Research mission/workspace authority | Retain unchanged; never promote. |
| Release assurance or validation evidence | Manifests, baseline manifest, validation, assurance, deficiency and assessment summaries | IT-001 controlled release schedules and package authority | Validate identity/declarations/checksums and retain for audit; never treat assurance as canonical intelligence. |
| Unsupported or ambiguous | Baseline domain models, final twin products, analyst/news/capability/historical inventories, final unknown/contradiction/evidence duplicates, and other content not named by the canonical HFT projection | Respective Enterprise Intelligence or presentation owner | Retain and explicitly classify; do not infer or silently map. A future canonical-owner contract may add an unambiguous projection. |

## Compatibility findings

* **Package construction:** valid archive and internally consistent declared byte counts/checksums; no rewrite required.
* **Manifest declaration:** identity is expressed as `mission_id`/`id`, and declared members use `filename`; existing governed identity precedence resolves `TMS-001`. Flora now verifies every declared file, byte count and checksum at validation.
* **Industry Twin Delta projection:** the exact incompatibility was identifier lists named `new_twins`, `new_relationships`, `new_unknowns`, `new_contradictions` and `evidence_references`, rather than generic inline records. The adapter now resolves the canonical HFT inventories explicitly and refuses missing inventories or relationship endpoints.
* **Adapter mapping:** canonical objects map to `entity` while preserving their `object_type`; facts remain governed `fact` records rather than being silently coerced into observations; sources map to evidence; uncertainty maps to Unknowns and Contradictions; the reasoning document maps to governed lineage.
* **Staging constructors:** `fact` and `reasoning_lineage` use the existing generic stable-ID canonical store. A TMS contradiction's declared single `statement` is retained as a summary assertion, not invented into two opposing claims.
* **Flora runtime:** no parallel lifecycle is required. Existing authenticated receipt, candidate review, dry-run reconciliation, approval, atomic promotion, repositories and completion/Explore projection are used.

## Proven result and remaining unsupported content

The repository-fixture integration proof stages and promotes exactly **315** reviewed mutations: 59 objects, 63 facts, 56 evidence records, 102 relationships, 20 Unknowns, 14 Contradictions and one reasoning-lineage document. Quarantined and rejected counts are both zero; all 204 relationship endpoints resolve. Before approval the expected canonical mutation count is explicit and canonical writes remain zero. Repeat execution is `repeat_no_change`; corrupt declared content fails validation without canonical mutation.

Remaining unsupported content is retained, classified and inspectable in package lineage: the baseline/final domain-model products (`01`–`15` except the Delta), duplicate final registers (`16`–`18`), research disposition/restart/readmes/summaries (`19`, `20`, `22`), deficiency and high-fidelity summaries, executive products, Flora navigation output, analyst/news/capability/assurance/historical inventories, validation output, and both research workspaces/checkpoints. Supporting these as new canonical classes requires a future declaration from their canonical owners; WP1-004 does not infer those semantics.

## Recommendation

**Merge.** The real repository package now traverses the existing governed lifecycle with evidence, uncertainty and reasoning lineage preserved, while derived/workspace/ambiguous content remains retained but non-promotable and Research-ready status is not promoted into Accepted or Architecture-ready status.
