# IT-001 — Industry Twin Specification

**Document class:** Enterprise Intelligence model
**Status:** Review
**Authority:** Proposed Enterprise Intelligence Model
**Owner:** Rob / CIOS
**Last updated:** 2026-07-16
**Production behaviour:** Documentation-only. This specification introduces no runtime behaviour and does not alter production Researcher or Assurance packs.
**Release-profile membership:** none — excluded from production Researcher, Assurance and Reviewer profiles

## 1. Mission and purpose

IT-001 defines the **Industry Twin** as the durable Enterprise Intelligence object that accumulates cross-enterprise learning about an industry. It explains how enterprises within an industry behave, change, invest, regulate, compete and create commercial opportunity.

An Industry Twin is **not** a market report, analyst report, sector overview, collection of Enterprise Twins or collection of procurements. It is a governed Enterprise Intelligence model whose comparative reasoning remains attributable, inspectable and open to falsification.

This Review model has emerged from evidence accumulated through Enterprise Twin validation for **VodafoneThree** (Telecommunications), **National Grid** (Energy Infrastructure) and **United Utilities** (Water Infrastructure). Those Enterprise Twins demonstrate the need for a higher-order intelligence object able to retain cross-enterprise reasoning without losing the evidence, uncertainty or authority of each enterprise.

IT-001 is documentation-only Review material. It does not promote itself to Accepted architecture, alter canonical Enterprise Intelligence semantics, modify production Researcher or Assurance packs, or introduce runtime behaviour.

## 2. Architectural position

The Industry Twin occupies the industry-level position in the proposed Enterprise Intelligence hierarchy:

```text
Evidence
  ↓
Observation
  ↓
Enterprise Mechanism
  ↓
Enterprise Intelligence Pattern
  ↓
Enterprise Twin
  ↓
Industry Twin
  ↓
Opportunity Twin
  ↓
Positioning Intelligence
```

| Layer | Purpose |
| --- | --- |
| **Evidence** | Attributable source material that supports, challenges or contextualises a claim. It is not itself an intelligence conclusion. |
| **Observation** | An evidence-backed, governed intelligence atom describing a meaningful condition, change or relationship. EI-012 continues to own its semantics and lifecycle. |
| **Enterprise Mechanism** | An enterprise-specific causal structure explaining how change propagates through one enterprise, including its conditions, dependencies, effects and uncertainty. |
| **Enterprise Intelligence Pattern** | A governed, reusable reasoning asset derived from comparison of analogous Enterprise Mechanisms across enterprises. It states recurring causal logic, scope and limits; it is not a universal law. |
| **Enterprise Twin** | The authoritative, governed durable memory explaining one enterprise's evidence, state, mechanisms, pressures, behaviours, Unknowns and Contradictions. |
| **Industry Twin** | The governed, comparative model explaining common industry structures, behaviours, mechanisms, pressures, patterns and commercial dynamics across multiple enterprises. |
| **Opportunity Twin** | The governed model explaining one selected commercial opportunity in its enterprise-specific context, including need, timing, constraints, hypotheses and evidence. |
| **Positioning Intelligence** | Governed intelligence that translates an evidence-governed Opportunity Twin into an executive positioning frame without becoming a proposal, supplier recommendation or runtime action. |

The arrows indicate a reasoning relationship, not automatic promotion, inheritance, copying or mutation. Every layer retains its own owner, validation boundary, evidence lineage and uncertainty.

## 3. Industry Twin definition and objectives

An **Industry Twin** is a durable, governed Enterprise Intelligence model representing the common structures, behaviours, mechanisms, pressures, patterns and commercial dynamics observed across multiple enterprises operating within the same industry.

Industry Twins explain industries. Enterprise Twins explain enterprises. Opportunity Twins explain opportunities.

### Objectives

An Industry Twin exists to:

- accumulate validated Enterprise Intelligence without replacing enterprise-specific truth;
- compare Enterprise Twins explicitly and retain the basis of comparison;
- identify recurring Enterprise Mechanisms and their operating conditions;
- identify and contextualise Enterprise Intelligence Patterns;
- identify Pattern Variants;
- identify industry-specific behaviours and sector-wide transformation themes;
- identify emerging opportunity spaces without asserting individual opportunities;
- support the construction and challenge of future Enterprise Twins; and
- retain cross-enterprise learning as durable, governed organisational intelligence.

### What it is and is not

| Industry Twin is **not** | Industry Twin **is** |
| --- | --- |
| Analyst report | Governed intelligence |
| Procurement pipeline | Evidence-governed |
| Supplier landscape | Continuously updated |
| Market-size assessment | Comparative |
| Technology radar | Explainable |
| Sales campaign | Durable and falsifiable |

An Industry Twin may contextualise public policy, market participants, technology or procurement signals where evidence warrants it, but it does not become a supplier landscape, market-size assessment, technology radar, sales campaign or procurement pipeline.

## 4. Required objects

### 4.1 Industry Identity

Every Industry Twin must define its industry identity, including:

- industry definition and the rationale for it;
- boundaries, inclusions and exclusions;
- value chain and material operating roles;
- regulatory landscape; and
- ecosystem, including relevant institutions, participants and dependencies.

### 4.2 Enterprise Population

The Enterprise Population references participating Enterprise Twins and records why each enterprise is in scope, its material differences and the period of participation. It must **not** duplicate Enterprise Twin content. Enterprise Twins remain the authoritative source for enterprise-specific state, evidence, Observations, mechanisms, Unknowns and Contradictions.

### 4.3 Enterprise Mechanism Catalogue

The catalogue records mechanisms observed across the participating enterprises. Each entry must include:

- mechanism;
- enterprises observed;
- confidence;
- contradictions; and
- sector scope.

Each entry must link to the enterprise-specific mechanism and its evidence lineage. A catalogue entry is a comparative index, not ownership transfer or proof that a mechanism is universal.

### 4.4 Enterprise Intelligence Pattern Catalogue

The catalogue references independently governed, validated Enterprise Intelligence Patterns. Each reference must include:

- reuse scope;
- validation state;
- evidence lineage; and
- participating enterprises.

Patterns are consumed as bounded comparative reasoning inputs. The Industry Twin records how a Pattern is relevant or constrained in this industry; it does not change Pattern status, lifecycle, definition or ownership.

### 4.5 Pattern Variants

A **Pattern Variant** is a sector-specific manifestation of an Enterprise Intelligence Pattern that preserves the underlying reasoning while adapting to industry-specific operating conditions.

A Pattern Variant may describe, for example, how a common resilience pattern is conditioned by regulated network obligations or how an investment-governance pattern is conditioned by an industry capital cycle. Such examples are illustrative only; they do not validate a Pattern or Variant.

A Variant must retain a reference to its governing Pattern, the industry conditions that shape it, its participating enterprises, evidence lineage, confidence, contradictions, freshness and validation state. A Variant must not be presented as a new Pattern merely because its sector expression differs.

### 4.6 Industry Pressures

The Industry Twin records the material pressures operating across the industry, including:

- regulation;
- technology;
- workforce;
- investment;
- resilience;
- sustainability;
- customer expectations;
- economics; and
- public policy.

Each pressure must identify its evidence basis, affected scope, confidence, freshness, counterevidence and unresolved questions.

### 4.7 Industry Behaviours

Industry Behaviours explain recurring responses by participating enterprises to shared or comparable pressures. They must distinguish observed recurrence from unsupported generalisation and record meaningful differences in timing, capability, regulation, economics, geography and enterprise strategy.

### 4.8 Industry Change Mechanisms

Industry Change Mechanisms catalogue the causal structures that repeatedly generate enterprise change across the industry. They connect pressures, conditions, actors, constraints, investments and effects while preserving the source Enterprise Mechanisms and any counterexamples.

### 4.9 Industry Opportunity Themes

Industry Opportunity Themes identify recurring **opportunity spaces**, not suppliers, sales plays, procurements or individual opportunities. Illustrative themes include:

- evidence-led regulation;
- infrastructure modernisation;
- operational resilience;
- digital operations;
- customer trust; and
- asset intelligence.

A theme must state the observed industry conditions, evidence lineage, participating enterprises, confidence, Unknowns, contradictions and questions that require enterprise-specific validation. Individual commercial opportunities remain the responsibility of Opportunity Twins.

### 4.10 Industry Strategic Watch

The Industry Strategic Watch defines signals Flora should monitor as future evidence inputs, without introducing monitoring runtime behaviour. Signals may include material regulatory decisions and consultations; investment and funding commitments; resilience incidents; asset performance or capacity constraints; workforce availability; technology adoption; customer-service and trust indicators; sustainability obligations; public-policy changes; and evidence that challenges an existing mechanism, Pattern or Variant.

For each signal class, the watch should record why it matters, relevant industry scope, expected evidence sources, refresh expectation, affected objects and review trigger. This specification does not modify Flora, automate collection or mandate a production watch implementation.

### 4.11 Unknowns

Every Industry Twin must preserve unresolved questions, evidence gaps, contested interpretations and insufficiently comparable enterprise conditions. Unknowns are governed intelligence, not omissions to conceal. They must remain linked to the affected object and direct future comparison, validation or collection.

## 5. Relationships and ownership boundaries

### Relationship to Enterprise Twins

**Enterprise Twins are authoritative. Industry Twins synthesise. Industry Twins never overwrite Enterprise Twins.**

An Industry Twin references and compares enterprise-specific intelligence. It must not replace an Enterprise Twin's evidence, claims, mechanisms, confidence, freshness, Unknowns, Contradictions, validation state or acceptance boundary with an industry-level summary. If industry comparison reveals a challenge, it creates a traceable question or contradiction for review; it does not mutate enterprise truth.

### Relationship to Patterns

**Patterns are governed independently. Industry Twins consume Patterns. Industry Twins do not own Patterns.**

EI-015 remains the Review model for Enterprise Intelligence Patterns. IT-001 may reference a Pattern and describe its bounded industry relevance or Pattern Variant, but cannot validate, promote, redefine, retire or transfer ownership of that Pattern. Pattern lifecycle and governance remain separate from Industry Twin lifecycle and governance.

### Relationship to Opportunity Twins

**Industry Twins identify opportunity themes. Opportunity Twins explain individual opportunities.**

An Industry Opportunity Theme can supply context, hypotheses, questions and evidence demands. It cannot assert that a particular enterprise has an opportunity, select a supplier, rank a pursuit, form a procurement pipeline or substitute for enterprise-specific opportunity reasoning. OT-001 remains the Review specification for the individual Opportunity Twin.

### Relationship to Positioning Intelligence

Positioning Intelligence remains downstream of a governed Opportunity Twin. An Industry Twin can provide contextual reasoning, but it must not create proposals, Provider Fit, supplier recommendations, sales campaigns or executive positioning on its own. EI-014 continues to own Review positioning intelligence after an Opportunity Twin.

## 6. Governance and validation rules

### Governance requirements

Every Industry Twin must preserve:

- evidence lineage;
- confidence;
- freshness;
- contradictions;
- validation state; and
- participating enterprises.

It must also make its industry boundary, comparison method, reuse scope, falsification conditions, Unknowns, review triggers and decision history inspectable. Industry-level claims must trace to contributing Enterprise Twins, their mechanisms or observations, Pattern references where applicable, and the comparison that justifies synthesis.

### Validation rules

An Industry Twin requires:

1. multiple Enterprise Twins;
2. materially different enterprises;
3. explicit comparison;
4. preserved contradictions; and
5. no unsupported generalisation.

A repeated phrase, analyst convention, procurement category or single enterprise case is insufficient evidence for an industry-level claim. Differences between enterprises must be documented, including evidence that narrows a proposed mechanism, Pattern, Variant or opportunity theme. A contradiction may reduce confidence, bound scope, create an Unknown or invalidate a claim; it must never be removed merely to produce a cleaner sector narrative.

## 7. Known Unknowns

The following questions remain open during Review and must remain visible in every subsequent version of this specification and in relevant Industry Twins:

1. What is the minimum number of Enterprise Twins required for an Industry Twin to be useful and valid within a stated scope?
2. How should cross-sector industries be defined where value chains or regulatory structures overlap?
3. How should multinational industries account for materially different national regulation, public policy, operating conditions and enterprise geographies?
4. Where should ecosystem boundaries be drawn, especially for regulators, supply chains, partners, communities and adjacent infrastructure?
5. What governance lifecycle, approval boundary and validation threshold should apply to Pattern Variants?

## 8. Constraints and Review confirmation

IT-001 must not:

- redefine Enterprise Twins;
- redefine Opportunity Twins;
- redefine Enterprise Intelligence Patterns;
- introduce runtime behaviour; or
- modify production Researcher or Assurance packs.

IT-001 is derived from evidence accumulated through Enterprise Twin validation for VodafoneThree, National Grid and United Utilities. That evidence supports Review of this higher-order model; it does not establish universal industry truth or Accepted architecture.

This specification is documentation-only, remains at **Review** status and has no production profile membership.
