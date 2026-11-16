
# FLORA / CIOS — Financial Intelligence & Governance Simplification Challenge
# Sprint: FIG-1 — Architecture Challenge (Design and Decision Only)

REPOSITORY
rdidale-jpg/CIOS

AUTHORITATIVE CONTEXT
- Current origin/main and accepted CIOS architecture/ADRs.
- EAR-1 draft PR #640, exact SHA:
  d7052c9fa8598eb1f15bfa4f92440c9b6b284c06
- BIE-3 merged PR #638, merge SHA:
  e7c58feb84882b0e7a1ea38e7e1c72079402aa86
- Banking research in PRs #636, #638 and earlier research branches.
- Existing Financial, Source, Evidence, Observation, Enterprise Model, Researcher and FLORA presentation owners.
- CIOS Chief Architect guidance and Design Doctrine where available.

MISSION
Challenge whether CIOS has over-engineered the acquisition, classification, acceptance and presentation of financial intelligence.

The owner requires FLORA to deliver the quality and breadth of a capable AI financial analyst across an entire industry, while preserving provenance, accuracy, uncertainty, permissions and security.

A published financial fact should not automatically require individual canonical Evidence promotion before being usable in an accurately attributed analytical view.

Likewise, calculations and estimates should not automatically become durable canonical Observations.

The goal is the smallest repeatable architecture that achieves this safely.

THIS IS A CHALLENGE, NOT AN IMPLEMENTATION COMMISSION.
Do not change production behaviour or approve any previously restricted source.

PHASE 1 — AUDIT EXISTING ARCHITECTURE

Inspect actual code, accepted ADRs, contracts and relevant tests.

Trace:
1. Source acquisition and verification.
2. Publisher/source permissions.
3. Research candidate creation and validation.
4. Financial metric extraction and interpretation.
5. Calculations and estimates.
6. Evidence acceptance and canonical promotion.
7. Observation persistence.
8. Enterprise Model financial attributes.
9. FLORA presentation and source attribution.
10. Revocation, contradiction, supersession and expiry.

Identify each mandatory gate and its actual authoritative owner.

For every gate determine:
- What risk does it control?
- Is it required for source use, analytical presentation, or durable canonical knowledge?
- Is it duplicated elsewhere?
- Is its cost proportionate to the risk?
- Could existing automated validation replace routine manual intervention?
- Can its purpose be retained through simpler contracts?

Distinguish implemented behaviour, architectural intent and inherited historical constraints.

Do not assume existing design is correct merely because it was previously implemented.

PHASE 2 — TEST THE AI FINANCIAL ANALYST CHALLENGE

Use UK Banking as the reference industry.

Assess at least:
- NatWest Group
- HSBC UK Bank plc
- Santander UK / TSB
- Nationwide
- Starling

Construct a representative financial-analysis specification covering:

A. Income statement and profitability.
B. Balance-sheet assets and liabilities.
C. Deposits, lending and funding.
D. Capital, liquidity and risk.
E. Revenue and cost structure.
F. Credit impairment.
G. Cash flow where meaningful.
H. Strategic investments and disclosed transformation expenditure.
I. Financial and operating performance trends.
J. Appropriate comparisons across banks and business models.

Include distinct statutory, underlying, adjusted, Group, subsidiary, reporting-segment and period definitions.

Do not fabricate unavailable metrics or force inappropriate comparability.

For each example trace:
SOURCE → EXTRACTED FACT → VERIFIED METRIC → CALCULATION / ESTIMATE → ANALYTICAL VIEW → OPTIONAL DURABLE KNOWLEDGE.

Show where the current architecture prevents or complicates a legitimate result.

Use authentic official sources and existing research where admissible.
Do not bypass source permissions or imply source acceptance.

PHASE 3 — INDUSTRY-WIDE SOURCE-USE POLICY

Challenge the present publisher allowlist and source-admission model.

Develop a reusable industry-level policy for:
- Company annual and interim financial reports.
- Regulatory filings and numerical disclosures.
- Government and official statistics.
- Company announcements and investor presentations.
- Open-data sources.
- Third-party market research.
- Licensed or restricted content.

Separate:
1. Access rights.
2. Extraction and internal processing.
3. Storage and retention.
4. Factual numerical reuse.
5. Attribution and linking.
6. Public or seller-facing presentation.
7. Redistribution of copyrighted expression.
8. Revocation and expiry.

Assess UK copyright, database-rights, relevant open licences and contractual terms as applicable.

Do not give unsupported blanket legal permission.
Do not presume publicly accessible means unrestricted commercial use.

Determine which source categories can have safe, reusable defaults and which require source-specific exceptions.

Propose a proportionate source-use decision model under existing owners, not a new permissions framework.

PHASE 4 — CHALLENGE THE FINANCIAL DATA MODEL

Investigate EAR-1's findings:
- Missing deposit metric definitions.
- Incorrect point-in-time stock semantics.
- Numeric values lost during Observation serialization.
- Prose fallback instead of durable numeric projection.
- Incomplete lifecycle/revocation checks.

Determine the smallest compatible corrections.

Assess whether CIOS should retain:
- Durable original reported financial measurements.
- Their definitions, source lineage and reporting dates.
- Reproducible calculated values.
- Explicit modelling assumptions and scenario definitions.
- Derived interpretations without automatically promoting them into canonical Observations.

Reuse existing financial, Observation and Enterprise Model owners.

Avoid a new financial database or duplicate financial engine.

Do not treat every calculation, chart point or analytical sentence as a separate canonical fact.

PHASE 5 — OPTIONS AND ARCHITECTURAL CHALLENGE

Produce three genuinely differentiated options:

OPTION A — Minimal remediation of current governance.
OPTION B — A governed analytical-view pathway alongside existing canonical acceptance.
OPTION C — A broader simplification of the financial intelligence lifecycle.

For each:
- Describe architecture and data flow.
- Explain existing owners reused.
- Identify contracts/ADRs affected.
- Estimate implementation complexity qualitatively.
- Evaluate source accuracy and security.
- Assess automation potential.
- Explain implications for financial comparison and analysis.
- Identify migration and compatibility risks.
- Assess future reuse across Banking, Technology and Aviation.
- Identify what can be removed or simplified.

Challenge unnecessary complexity and false distinctions.

Recommend ONE option, supported by concrete evidence from the repository.

PHASE 6 — PROVE THE PROPOSED MODEL

Provide a reproducible, non-production demonstration using existing permitted data or clearly labelled synthetic fixtures.

Show:
1. A reported financial stock with an explicit as-at date.
2. A financial flow over a defined reporting period.
3. A calculation from compatible underlying measurements.
4. An estimate with visible assumptions.
5. Conflicting or superseded evidence.
6. A withdrawn or revoked source.
7. Correct Group versus subsidiary attribution.
8. Persistence and reload of typed numeric data where currently supported; otherwise demonstrate the precise failing contract.
9. A clear distinction between analytical presentation and canonical knowledge.

No fake source receipts or claims of successful canonical promotion.

PHASE 7 — DECISION AND IMPLEMENTATION ROADMAP

Deliver a concise architecture decision paper suitable for owner and Chief Architect review.

Include:
- Executive summary and decision.
- Evidence of unnecessary friction or duplication.
- Before/after workflow.
- Proposed source-use policy.
- Proposed financial data model.
- Reused authoritative owners.
- Exact architectural changes.
- ADR amendments or new ADR proposal, if genuinely needed.
- Security and provenance implications.
- Implementation migration strategy.
- Test and rollback strategy.
- Minimal staged implementation roadmap.
- Commercial outcomes and success criteria.

Each implementation sprint must be independently useful and bounded.

Success is not the number of new research records or approvals.

Success is FLORA's ability to produce substantially richer, accurate, reproducible and attributed financial intelligence with minimal manual intervention.

ACCEPTANCE CRITERIA

- Five differentiated banking exemplars assessed.
- Existing governance and financial paths traced through actual code.
- Industry-wide source-use policy proposed.
- Three architecture options challenged.
- One recommendation with evidence and trade-offs.
- EAR-1 technical findings reconciled.
- Reproducible non-production proof.
- No unsupported financial comparisons.
- No weakening of tenant, role, source or canonical integrity.
- Independent Chief Architect-style architecture critique.
- Commercial usefulness critique.
- Local and hosted checks appropriate to changed artifacts.
- Explicit distinction between source facts, analysis, estimates and accepted Enterprise knowledge.

CONSTRAINTS

- No production writes.
- No canonical Evidence/Observation/Enterprise Model mutations.
- No publisher allowlist changes.
- No acceptance of ADR-027 or any proposed ADR.
- No paid calls or autonomous research services.
- No Render deployment.
- No GitHub merge.
- Do not modify accepted architecture without approval.
- Do not merge EAR-1 PR #640 as part of this challenge.
- Do not introduce another intelligence engine or source registry.

DELIVERABLE

Create a new draft FIG-1 architecture/research PR against verified current main.

Provide:
- PR URL and exact SHA.
- Architecture decision paper.
- Source-use and financial contract proposals.
- Current-versus-proposed architecture.
- Non-production proof.
- Options comparison.
- Independent critique.
- Implementation roadmap with bounded sprints.
- Local/hosted test results.
- Specific owner decisions required.

Stop for owner review and architectural acceptance.

COMPLETION REPORT

Explain:
1. What was found to be genuinely over-engineered.
2. What governance is essential and must remain.
3. What changes are recommended.
4. Which constraints can be simplified immediately.
5. What requires explicit legal, architectural or owner approval.
6. What the smallest first implementation sprint should deliver.

Execute the entire challenge without intermediate owner questions.
