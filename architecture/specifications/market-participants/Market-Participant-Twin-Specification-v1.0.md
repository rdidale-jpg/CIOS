# Market Participant Twin Specification v1.0

**Status:** Draft Normative Specification  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning ADR:** [ADR-016 — Knowledge Packs as the Standard Exchange Mechanism](../../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md)  
**Owning papers:** [FP-010 — Knowledge Pack Architecture](../../founding-papers/FP-010-Knowledge-Pack-Architecture.md), [FP-011 — Knowledge Exchange Architecture](../../founding-papers/FP-011-Knowledge-Exchange-Architecture.md), [FP-009 — Hypothesis Validation Standard](../../founding-papers/FP-009-Hypothesis-Validation-Standard.md)  
**Semantic authorities:** [EI-013 — Knowledge Asset Exchange Model](../../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md), [EI-002 — Enterprise Knowledge Graph](../../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md)  
**Related specification:** [Twin Presentation Model Specification v1.0](../presentation-models/Twin-Presentation-Model-Specification-v1.0.md)

## Purpose

A Market Participant Twin is a governed, evidence-aware twin for an organisation or actor that participates in a market around an Enterprise Twin, Industry Twin, Opportunity Twin or account context.

A Market Participant Twin may represent a:

- supplier;
- competitor;
- partner;
- adviser;
- systems integrator;
- technology vendor;
- specialist challenger.

The twin describes what is known, unknown, contradicted and hypothesised about the participant. It must preserve Evidence lineage, Observation lineage, confidence, freshness and interpretation boundaries.

## Core principle: participant strength is account-relative

Participant strength is not absolute. It must be interpreted relative to:

- a specific account;
- a specific enterprise pressure;
- decision ownership;
- access route;
- procurement route;
- incumbent context;
- delivery requirement;
- competitive alternatives.

A participant may be strong in one account context and weak, inaccessible, conflicted or commercially irrelevant in another. Market Participant Twins therefore store participant state, while account-relative claims belong in an Account-Participant Position Assessment or another governed interpretation with lineage.

## Canonical identity and scope

Each Market Participant Twin MUST include:

| Field | Requirement |
| --- | --- |
| `participant_twin_id` | Stable identifier. |
| `participant_name` | Current known name and aliases. |
| `participant_type` | One or more controlled values: supplier, competitor, partner, adviser, systems integrator, technology vendor, specialist challenger. |
| `ownership` | Ownership model, parent, subsidiaries or private/public status where relevant. |
| `geography` | Operating geographies, jurisdictions and account-relevant regions. |
| `sectors` | Sectors served or competed in. |
| `source_cut_off` | Latest evidence date included in the twin. |
| `model_status` | Candidate, accepted, superseded, retired or quarantined. |
| `confidence` | Overall confidence with explanation. |
| `freshness` | Freshness state and expiry/review trigger. |

## Participant intelligence model

A Market Participant Twin SHOULD include the following sections where evidence exists, and MUST record Unknowns where material sections are missing.

| Section | Contents |
| --- | --- |
| Identity | Legal identity, aliases, parent group, identifiers, public-sector identifiers where relevant. |
| Participant type | Role classification and rationale. |
| Ownership | Parentage, ownership status, acquisitions, controlling interests. |
| Geography | Delivery footprint, sales footprint, jurisdictions, account-relevant local presence. |
| Sectors | Target sectors, proven sectors, emerging sectors and sectors claimed only by marketing. |
| Capabilities | Capability taxonomy entries and maturity, each with evidence status. |
| Offerings | Products, services, managed services, advisory propositions, platforms and packaged solutions. |
| Strategic priorities | Public strategy, investment focus, market moves, stated growth priorities. |
| Strengths | Evidence-governed strengths following this specification. |
| Weaknesses | Evidence-governed weaknesses following this specification. |
| Relationships | Partners, suppliers, customers, alliances, channel relationships and ecosystem links. |
| Account presence | Known account relationships, spend, contracts, references and delivery footprint. |
| Incumbent positions | Existing roles in accounts, capabilities, contracts, frameworks or programmes. |
| Delivery evidence | Case studies, contracts, outcomes, references, delivery quality signals and failures. |
| Alliances | Strategic alliances, certified partnerships, co-sell motions and dependency risks. |
| Procurement routes | Frameworks, lots, contracts, public procurement routes and channel access. |
| Commercial frameworks | Rate cards, framework terms, preferred supplier status, resale rights and constraints. |
| Relevant executives | Executives or account leaders relevant to commercial access, strategy or delivery. |
| Reputation | Analyst views, client feedback, controversies, public sentiment and credibility signals. |
| Financial condition | Financial resilience, revenue trends, risk indicators or credit concerns where relevant. |
| Delivery performance | Timeliness, quality, capacity, account satisfaction and incident history where evidenced. |
| Vulnerabilities | Account-relative or general vulnerabilities, each evidence-governed. |
| Unknowns | Explicit missing knowledge and validation questions. |
| Contradictions | Competing claims and unresolved evidence conflicts. |
| Evidence lineage | Evidence IDs, source references, dates, extracts and affected claims. |
| Observation lineage | Observation IDs, lifecycle state and relation to participant claims. |
| Presentation Model | Optional governed rendering payload for audience-specific use. |
| Release lifecycle | Version, status, supersession, review cadence and retirement rules. |

## Strength and weakness governance

Every participant strength or weakness MUST be classified as exactly one of:

- `evidence-backed` — directly supported by Evidence or accepted Observations;
- `inferred` — reasoned from Evidence, Observations or graph relationships and carrying explanation;
- `human-supplied` — provided by a named contributor and date, with rationale;
- `unknown` — not known or not yet assessable;
- `contradictory` — supported and challenged by unresolved competing evidence.

A strength MUST NOT be inferred from marketing claims alone. Marketing claims may create candidate Evidence or validation questions, but they do not establish strength without corroboration, delivery evidence, account evidence or accepted Observation support.

A weakness MUST NOT be asserted without evidence or a clearly labelled inference. Weakness language must distinguish observed delivery failure, account-specific blocker, inferred limitation, stale evidence and unknown.

Each strength or weakness MUST include:

| Field | Requirement |
| --- | --- |
| `claim_id` | Stable claim identifier. |
| `claim_type` | Strength or weakness. |
| `classification` | evidence-backed, inferred, human-supplied, unknown or contradictory. |
| `capability_or_context` | Capability, account context, delivery requirement or market area affected. |
| `supporting_evidence` | Evidence references, or explicit none for unknown. |
| `supporting_observations` | Observation references and lifecycle states. |
| `affected_accounts` | Accounts where the claim may matter; empty only when genuinely general. |
| `confidence` | Confidence score or band with rationale. |
| `freshness` | Last confirmed date, decay rule and next review date. |
| `contradiction_state` | none, potential, active, resolved or quarantined. |
| `validation_questions` | Questions required to strengthen, weaken, resolve or retire the claim. |
| `what_not_to_claim` | Prohibited overstatements arising from lineage limits. |

## Unknowns and Contradictions

Unknowns and Contradictions are first-class model objects, not editorial notes. The twin MUST preserve:

- the affected participant claim or relationship;
- why the gap or conflict matters;
- evidence needed to resolve it;
- owner or next validation action where known;
- confidence impact;
- freshness or review trigger.

Contradictions MUST NOT be silently reconciled by choosing the most convenient claim. Resolution requires dated evidence, reasoning and a retained audit trail.

## Evidence and Observation lineage

Every material participant claim MUST reference Evidence, Observations or a labelled human-supplied source. Lineage MUST preserve:

- source identity and date;
- collected date and observed date where available;
- evidence extract or summary;
- Observation identifier and lifecycle state where applicable;
- affected attributes, relationships, strengths, weaknesses or recommendations;
- inference explanation for inferred claims.

## Presentation Model

A Market Participant Twin MAY include one or more Twin Presentation Models under the Twin Presentation Model Specification. Presentation Models are governed interpretations for declared audiences and purposes. Acceptance of a Presentation Model does not promote its claims to canonical fact.

Presentation Models MUST keep Unknowns, Contradictions, human-supplied knowledge, confidence, freshness and lineage inspectable.

## Release lifecycle

Market Participant Twin releases MUST declare:

- version;
- release type: initial, incremental, correction, supersession, retirement or quarantine;
- source cut-off;
- validation state;
- release owner;
- affected accounts, sectors or opportunities;
- changed claims;
- superseded claim identifiers;
- unresolved Unknowns and Contradictions;
- next review trigger.

## Market Participant Knowledge Pack

A Market Participant Knowledge Pack is the governed exchange container for a Market Participant Twin. It MUST conform to the common Knowledge Pack structure:

```text
manifest.json
metadata.json
validation.json
lineage.json
checksums.sha256
payload/participant-twin/
payload/presentation-model/
attachments/
```

Required content:

| Component | Requirement |
| --- | --- |
| Manifest | Pack identifier, version, issuer, payload inventory, source cut-off and handling constraints. |
| Metadata | Participant identity, scope, producer, intended use, status and rights. |
| Validation | Schema checks, lineage checks, strength/weakness governance checks, contradiction checks and quarantine reasons. |
| Lineage | Evidence lineage, Observation lineage, human-supplied knowledge labels and inference explanations. |
| Checksums | Checksums for payload and attachments. |
| Payload | Participant Twin content and optional Presentation Model. |

Pack acceptance means the package is structurally valid for governed repository handling. Acceptance MUST NOT upgrade interpretation, marketing claims, inferred claims or human-supplied claims into canonical fact.

## Enterprise Knowledge Graph alignment

Market Participant Twin graph projection SHOULD use EI-002 relationship governance. Inferred relationships must preserve explanation and lineage. Recommended relationship types include:

- `Participant SUPPLIES Enterprise`;
- `Participant COMPETES_FOR Opportunity`;
- `Participant PARTNERS_WITH Participant`;
- `Participant INCUMBENT_FOR Capability`;
- `Participant HAS_STRENGTH Capability`;
- `Participant HAS_WEAKNESS Capability`;
- `Participant HAS_ACCESS_TO Stakeholder`;
- `Participant ALIGNS_WITH Account Need`;
- `Participant CONFLICTS_WITH Account Constraint`;
- `Participant VULNERABLE_IN Account Context`.

## Minimum validation checklist

A Market Participant Twin is valid only when:

1. identity and participant type are declared;
2. source cut-off, confidence and freshness are declared;
3. strengths and weaknesses follow evidence governance;
4. Unknowns and Contradictions remain first-class;
5. account-relative claims are separated from general participant state;
6. Evidence and Observation lineage are inspectable;
7. Presentation Models, if present, are labelled as governed interpretations;
8. Knowledge Pack acceptance does not promote interpretation into fact.
