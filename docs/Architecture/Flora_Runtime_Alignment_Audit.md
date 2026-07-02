# Flora Runtime Alignment Audit

## Founding papers reviewed

- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`
- `architecture/founding-papers/FP-004-Evidence-Acquisition-Standard.md`
- `architecture/founding-papers/FP-005-Enterprise-Intelligence-Collection-Framework.md`
- `architecture/founding-papers/FP-006-Source-Quality-Standard.md`

## Short architectural critique

Flora already had the right implementation constraints: deterministic extraction, governed source lists, JSONL persistence and no LLM/database dependency. The main conflict was that collection still behaved too much like a source-attempt counter. It could show volume and basic diagnostics, but the architecture papers require collection to be an intelligence control: evidence should be acquired against explicit demand, categorised by enterprise evidence coverage, tiered by source quality, and blocked from downstream reasoning when weak.

The sprint therefore treats intake as a reasoning boundary. Evidence is now scored, tiered and mapped to gaps before strategic signals or recommendations can use it.

## Current runtime gaps identified

- Evidence acquisition was source-list led rather than plan led.
- Coverage was summarised at organisation level but not against the FP-005 universal evidence categories.
- Source authority and source yield were not separated cleanly.
- Context, landing-page and boilerplate snippets could still carry too much downstream influence if they matched commercial keywords.
- Source lifecycle recommendations were not explicit enough to retire, replace, split or downgrade noisy sources.
- Human feedback existed elsewhere in the workspace, but live evidence/source feedback was not persisted with collection diagnostics.
- Collection result pages could imply success through extracted evidence volume rather than accepted, primary, rejected, noisy and diagnostics-only quality metrics.

## Alignment priorities

1. Prefer specific, attributable evidence over page volume.
2. Make missing evidence visible through coverage maps and evidence demand.
3. Separate source tier, source quality and source yield.
4. Prevent diagnostics-only and context-only material from creating Strategic Signals.
5. Preserve Render free-tier compatibility through standard-library, JSONL-only persistence.

## Changes implemented in this sprint

- Added deterministic Evidence Acquisition Plans persisted to `.flora_pilot/live_evidence/evidence_acquisition_plans.jsonl`.
- Added FP-005 coverage maps for Strategy, Finance, Technology, Procurement, Leadership, Operations, Regulation, Delivery, Suppliers, Customers / citizens and Risk / security.
- Added evidence quality bands, source tiering and Strategic Signal eligibility gates.
- Added source lifecycle scoring and actions including keep, monitor, downgrade, replace, diagnostics only and split into child sources.
- Added collection priority classification so weak high-priority accounts become collection tasks while weak low-priority accounts are deferred.
- Added an evidence demand model generated from thesis and coverage gaps.
- Added JSONL-backed live feedback hooks for evidence and sources.
- Expanded live collection result and source coverage pages with quality and lifecycle diagnostics.

## Deferred changes

- Adaptive child-source discovery remains recommendation-only; the runtime still avoids broad crawling.
- Source blueprints are implemented as deterministic category/source-family logic, not a separate external rules registry.
- Corroboration is represented in scoring gates, but richer cross-document evidence clustering remains future work.
- Feedback influences deterministic scores, but no learning model or database has been introduced.

## Risks

- Accepted evidence counts may fall because weak snippets are rejected or downgraded; this is expected and aligned with FP-004.
- Existing reports may show weaker confidence until more Tier 1 and Tier 2 source families are configured.
- JSONL persistence remains ephemeral on some free-tier deployments, so feedback and plans may reset after redeploy.
- Deterministic text rules may under-classify unusual but valid evidence; human feedback hooks are intended to expose and correct those cases.
