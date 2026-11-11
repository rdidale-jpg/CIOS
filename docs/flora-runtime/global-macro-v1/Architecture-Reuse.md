# Global & Macro Intelligence v1 — architecture and reuse

Implementation baseline: verified main `adf205993cc0857183d77766ce4882bf48326fb4`. Reference: [Issue #562](https://github.com/rdidale-jpg/CIOS/issues/562), [proposed ADR in #563](https://github.com/rdidale-jpg/CIOS/pull/563), source ADR revision `5c35ede369e8cc5294da6a462728b595c6efdf8b`. The proposal remains proposed; this bounded proof does not ratify a product-wide migration. No merge/rebase or modifications to #557, #559 or #561.

## Reuse decisions

| Existing owner | Reuse in this increment |
| --- | --- |
| `model.load_assessment`, registry and commercial projection | Same Banking/Aviation models, original 9 Lloyds / 6 easyJet hypothesis identities and source periods. Countries select a context rather than a duplicated industry dossier. |
| `SourceSegment`, `CandidateClaim` | Seven source-owned observations, exact located passages, content-addressed segment IDs; all remain unaccepted candidate intelligence. |
| `source_import` provenance and `model.primary_text` | Existing official-URL policy, checksummed excerpt validation, source dates and path confinement. Four exact official hosts added; Macro gets a confined snapshot boundary, without becoming an industry in `DOMAINS`. |
| `EvidencePackageItem`, `SemanticObject`, `SemanticTwin` | Existing semantic/evidence adapters, candidate governance and `eligible_conclusion=False`. No new truth store. |
| `understanding.source_quality` | Existing source-age/unknown-publication assessment, exposed in the dossier without equating retrieval with freshness. |
| Shared visual specifications and SVG primitives | Original PESTLE and operating-map nodes/identities; presentation URLs change only after canonical spec validation. Existing banking/aviation illustrations and icons are reused. |
| Existing Research Mission / Researcher framework | No second scheduler, source scraper or automatic mission dispatch. The inspector exposes bounded closure questions. Subsequent acquisition/closure should use the existing mission owner and review process. |
| Pipeline and security owners | No service, permission, session, qualification, mutation or capture-schema changes. Existing controlled capture is reached through existing hypothesis pages. |

## Versioned context contracts

[Machine-readable schema](../../../enterprise-knowledge/macro/research-model/Global-Context-Contracts-v1.schema.json) is generated from the Pydantic contracts in `macro_intelligence.py`. [Candidate context bundle](../../../enterprise-knowledge/macro/research-model/Macro-Context-v1.json) carries version, cut-off, provenance, five deduplicated force/instrument records and seven existing-contract observations.

- **GeographicArea:** world, geographic navigation region or ISO-country reference. Europe contains a declared UK/France navigation subset; it is neither a complete coverage claim nor a legal jurisdiction.
- **Jurisdiction:** separately named instrument/authority scope. UK central-government procurement, FCA listing scope, EU reporting and French implementation are distinct.
- **MarketContext:** country × existing industry model × cut-off. UK and France share an industry-model identity, with differing context edges and explicit local-research gaps.
- **LegalEntityScope:** a reference to the existing group identity and an unresolved legal entity. Registry ID, legal name and parent ID are Unknown for both enterprise references. No French subsidiary or registered footprint is fabricated. Verified identity requires registry evidence and still does not establish a regulatory duty.
- **ContextEdge:** typed predicate, country, jurisdiction, entity scope, observed period, instrument date, assessment date, source/claim IDs, status, limitation and supersession reference. Pilot enterprise-applicability edges must remain Unknown.

Force kinds separate observed trends, threats/scenarios, procurement policy, proposed legislation, final regulatory rules and enacted instruments. Underlying UK survey observation is explicitly an observed trend; the cross-market cyber force is a threat/scenario. Industry/capability impacts and hypothesis associations are **analyst interpretations**. None establish enterprise incidents, ownership, compliance or demand.

## Refinements to #563

1. One cross-market cyber force fans out to separately sourced UK and French edges. UK survey observations are not transferred into French prevalence or incident claims.
2. An enacted EU amendment and French national implementation are separate questions. The pilot does not calculate an entity’s legal obligations.
3. Force country IDs record reviewed context coverage; they are not a complete legal territorial-applicability model. Unresearched cross-border reach remains Unknown. UK social-value policy is not propagated to French procurement. A French supplier bidding into covered UK procurement is a different scope question; nationality is not eligibility.
4. Global means a bounded reference-country view, not complete world coverage. Empty categories/countries are unresearched; counts denote reviewed themes rather than severity or market attractiveness.
5. Declared seller offering is an ephemeral URL view preference. It does not become a public seller profile, workspace setting, territorial permission or customer-confirmed need.
6. Existing UK group hypotheses may be explored as thematic research; they are not transplanted into France. Only Lloyds `RCO-LBG-005` and easyJet `RCO-EJ-006` have narrow, interpreted associations in this pilot. Empty hypothesis results are retained honestly.

## Safe integration boundary

Three exact GET routes: `/macro`, `/macro/evidence`, `/macro/spec`. They read only the repository-owned Macro context and curated industry research. Allowed query keys are finite; unsupported values, duplicate keys and private workspace/account selectors are rejected. No prefix exemption or protected resource resolver is introduced.

A Home entry opens the prototype. Existing primary navigation and Industry/Enterprise/Pipeline routes stay available. The contextual Macro PESTLE/enterprise views reuse original nodes without changing their canonical specifications. Native URLs preserve force, market, sector, offering and exploration depth; browser Back returns from existing hypotheses to that context. JavaScript enhances a single inspector; native links work without it.

## Migration and remaining gaps

No database, canonical identifier, research release, permission or Pipeline migration occurs. This repository bundle is a candidate presentation/research specification, not accepted evidence or a duplicate Banking/France model. Future revisions must append source/observation versions, retain content-addressed segments and explicit supersession lineage, and preserve older cuts rather than rewriting captured findings.

Actual legal-entity/footprint research is outstanding. Country-specific regulation, competition and supplier coverage are incomplete; the French view openly reuses a UK-anchored structural reference. Full original source bytes and current French implementing legal text remain unarchived/unverified at instrument level.

Macro context is **not yet added to saved Pipeline capture provenance**. Existing capture still freezes its original research provenance. A future governed adapter must preserve macro snapshot/edge references without changing qualification or authority; no end-to-end saved Macro lineage is claimed here.

Recommended next increment: verify one exact legal entity and current instrument scope in each market; deepen one industry-specific impact with counterevidence; then assess permissioned seller coverage and immutable Macro capture lineage through existing owners. Physical-device and timed owner acceptance remain separate from automated validation.

The existing historical-corpus test remains active with its original identity. It compares every one of the 142 original files byte-for-byte and separately allows only the nine explicitly reviewed Macro files. Unknown additions, modifications and deletions remain rejected; there is no blanket directory exclusion. Future integration with concurrent research PRs must reconcile their approved additions while retaining both identity checks and all passing test suites.
