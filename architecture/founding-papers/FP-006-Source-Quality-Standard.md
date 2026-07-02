# FP-006 — Source Quality Standard

**Purpose:** Define how Flora should assess the authority, usefulness and limitations of sources.
**Status:** draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-02

## 1. Purpose

This paper defines the source quality standard for Flora. It explains how Flora should assess sources before using them to support evidence, signals, transformation theses or recommendations.

Source quality and evidence quality are related but not identical. A source can be authoritative but low-yield. A source can be noisy but occasionally produce high-value evidence. Flora should therefore evaluate both the authority of a source and the usefulness of the evidence it produces.

## 2. Why all sources are not equal

All public material should not carry the same reasoning weight. A named executive speech, audited report or procurement award is more useful for strategic judgement than a homepage banner or generic service menu. Treating all pages equally encourages volume-driven collection and weak reasoning.

Source quality matters because it affects:

- confidence in observed facts;
- strength of downstream signals;
- need for corroboration;
- freshness expectations;
- bias and commercial intent;
- whether a source should provide evidence, context or diagnostics only.

## 3. Source tiering model

Flora should classify sources into tiers before assigning reasoning weight.

- Tier 1 sources can support strong signals when the extracted evidence is specific and current.
- Tier 2 sources can support signals when specific and corroborated.
- Tier 3 sources usually provide context only.
- Rejected or diagnostics-only sources must not support strategic signals.

Tiering does not remove the need to assess individual evidence objects. A Tier 1 document can contain generic text, and a Tier 2 source can contain a highly specific supplier or programme signal.

## 4. Tier 1 sources

Tier 1 sources are authoritative, specific and close to the organisation's formal decisions, obligations or performance.

Examples include:

- annual reports;
- financial results;
- investor presentations;
- Capital Markets Day materials;
- regulatory reports;
- NAO / audit reports;
- procurement notices;
- contract awards;
- official strategy documents;
- named executive speeches.

Tier 1 sources can support strong signals when they identify concrete priorities, budgets, obligations, programmes, leaders, suppliers, timelines or performance constraints.

## 5. Tier 2 sources

Tier 2 sources are useful but usually require specificity and corroboration before supporting strong signals.

Examples include:

- press releases;
- technology partnership announcements;
- case studies;
- sector publications;
- major industry publications;
- senior job adverts.

Tier 2 sources are valuable when they reveal programme detail, supplier movement, capability build-out, market positioning or leadership emphasis. They should be handled carefully where commercial intent or marketing bias is present.

## 6. Tier 3 sources

Tier 3 sources usually provide context rather than strategic evidence.

Examples include:

- homepages;
- generic organisation pages;
- careers landing pages;
- supplier service menus;
- tag/category pages;
- marketing pages.

Tier 3 sources can help Flora understand language, structure, service areas or source discovery paths. They should not normally support transformation theses unless they contain unusually specific and corroborated evidence.

## 7. Rejected / diagnostics-only sources

Rejected or diagnostics-only sources should not support strategic signals.

Examples include:

- cookie text;
- navigation;
- footers;
- modern slavery boilerplate;
- accessibility statements;
- generic publication scheme text;
- generic contact pages.

These sources may help diagnose collection quality, page parsing issues or site structure, but they are not evidence of commercial transformation.

## 8. Source quality scoring

Source quality scoring should estimate how much reasoning weight a source can carry before considering the extracted evidence in detail.

A suggested Source Quality Score should consider:

- authority;
- proximity to decision;
- specificity potential;
- freshness;
- independence;
- historical yield;
- bias or commercial intent;
- parseability;
- stability of URL;
- relevance to active evidence demand.

The score should guide collection and reasoning weight, not replace evidence-level judgement. For example, an annual report may score highly for authority and stability, while a supplier case study may score lower for independence but higher for specificity potential if it names a programme, platform, client and delivery outcome.

## 9. Source yield scoring

Source yield scoring measures the usefulness of a source after collection. It asks whether the source produced valuable evidence relative to noise.

A suggested Source Yield Score should consider:

- accepted evidence count;
- primary evidence count;
- rejection rate;
- duplicate rate;
- signal conversion rate;
- thesis contribution rate;
- user usefulness feedback.

A high-quality source can be low-yield for a particular organisation or question. A low-tier source can occasionally produce a high-yield item, but that item may still require corroboration. Yield should be recalculated over time, because a source that was useful during a procurement cycle may become stale after award or delivery.

## 10. Source freshness

Freshness expectations should vary by source type.

- Procurement notices, contract awards, job adverts and incident reports may become stale quickly.
- Annual reports, strategies and regulatory documents often remain useful across reporting cycles.
- Historical audit material can remain relevant when it describes persistent constraints.
- Marketing pages may be current but still weak because they lack specificity.

Flora should assess freshness against the commercial question being answered.

## 11. Source reliability

Reliability reflects whether a source is likely to describe reality accurately and consistently. Official, audited, regulatory and procurement sources are generally more reliable for formal facts. Supplier or marketing sources may be reliable for announcement content but less reliable for commercial significance.

Reliability should be strengthened by attribution, publication date, named authorship, stable URLs, formal status and corroboration.

## 12. Source bias and commercial intent

Many sources exist to persuade. Press releases, case studies, supplier pages and marketing materials can reveal valuable evidence, but they may overstate impact, omit failure, compress timelines or frame activity as more strategic than it is.

Flora should preserve useful facts from commercially biased sources while reducing unsupported inference. Bias does not make a source useless; it changes the corroboration requirement.

## 13. Source failure diagnostics

Flora should diagnose source failure rather than silently ingest noise. Common failures include:

- boilerplate extracted as evidence;
- navigation or menu text dominating content;
- stale pages treated as current;
- duplicated pages counted as independent;
- generic pages used to support strategic claims;
- source access failure misread as evidence absence;
- low-specificity text promoted into high-confidence signals.

Diagnostics should inform source replacement, parser improvement and evidence gap reporting.

## 14. Source replacement recommendations

When a source is low-yield, stale, noisy or inappropriate for the active question, Flora should recommend replacement sources.

Replacement should prefer:

- a more authoritative source in the same category;
- a fresher source covering the same event;
- an independent corroborating source;
- a sector-specific source family;
- a source closer to procurement, regulation, finance, leadership or delivery.

Replacement recommendations should be captured as part of collection feedback.

## 15. Source lifecycle actions

Sources have lifecycles. They may be discovered, classified, collected, scored, used, monitored, downgraded, retired or replaced.

Flora should support the following source lifecycle actions:

- keep: continue using the source at its current tier and cadence;
- monitor: retain the source but collect less aggressively until new evidence demand appears;
- downgrade: reduce reasoning weight because evidence is stale, generic, biased or low-specificity;
- replace: seek a better source family for the same evidence category;
- retire: stop using the source for current reasoning while preserving traceability;
- diagnostics only: retain only for parser, site-structure or failure analysis;
- split into child sources: decompose a noisy parent page into more specific subpages, feeds or document families;
- promote child source to governed source: elevate a high-yield child page or document family into the governed collection plan.

Lifecycle management should ensure that Flora does not continue to rely on stale, duplicated or low-value sources simply because they are easy to collect. Retirement should reduce current reasoning weight while preserving historical traceability where appropriate.

A noisy parent page should not necessarily be removed. Flora should first try to discover and promote better child pages. For example, a generic newsroom index may be noisy, but a specific capital investment announcement, contract award tag, regulatory response page or executive speech page beneath it may be high-yield.

## 16. Source and evidence examples

- Bad evidence: “Jobs and contracts Procurement at DWP Working for DWP Publication scheme”. Classification: reject / diagnostics only; likely source action is diagnostics only or split into child sources.
- Context evidence: a homepage describing services without a named programme, investment, supplier or delivery milestone. Classification: Tier 3 context source.
- Secondary evidence: a supplier announcement naming a transformation platform for a client. Classification: useful but biased; downgrade unless corroborated by contract, client or regulatory evidence.
- Primary evidence: “£15 billion investment to transform Armed Forces and keep the UK safe”. Classification: high-specificity primary evidence from an authoritative source.
- High-value evidence cluster: annual report funding, contract award, named executive statement and regulator or audit finding all pointing to the same transformation thesis. Classification: strong source diversity and high source yield.

## 17. Human feedback loop

Future UI should allow users to mark:

- useful evidence;
- weak evidence;
- wrong classification;
- noisy source;
- important source;
- missing source.

This feedback should influence both Source Quality Score and Source Yield Score. “Useful evidence” should improve historical yield and thesis contribution. “Noisy source” should increase rejection-rate concern and may trigger split, downgrade or diagnostics-only actions. “Important source” and “missing source” should inform future evidence acquisition plans and source replacement recommendations.

## 18. Open questions

- What scoring scale should be used for source quality and source yield?
- Which source tiers should be mandatory for high-confidence signals?
- How should source scores be exposed to users without creating false precision?
- How should Flora learn that a noisy source family is valuable for a specific sector?
- What diagnostics should trigger parser or collection workflow improvements?
