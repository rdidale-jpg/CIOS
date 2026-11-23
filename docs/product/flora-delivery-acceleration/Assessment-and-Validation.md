# Delivery friction, authority and validation

## Baseline and review scope

Reviewed main: `c04b242b1c09b584156d838c8634b504e1c988bf`. Its [full hosted validation passed](https://github.com/rdidale-jpg/CIOS/actions/runs/45211537434). This is repository evidence, not a production deployment claim.

Reviewed the [AI context](../../../CIOS-AI.md), [contribution guide](../../../CONTRIBUTING.md), [roadmap](../../../ROADMAP.md), Chief Architect [instructions](../../../knowledge-packs/chief-architect/configuration/Chief-Architect-GPT-Instructions.md), [operating guidance](../../../knowledge-packs/chief-architect/operating-guidance/Chief-Architect-Operating-Guidance.md) and [Handbook](../../../architecture/handbook/CIOS-Chief-Architect-Handbook.md), Researcher [instructions](../../../knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md), [RG-001](../../../knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md), [RG-002](../../../knowledge-packs/researcher/operating-guidance/RG-002-Research-Mission-Workspace-Standard.md), [canonical Research Agent Guide](../../../architecture/research/Commercial-Digital-Twin-Research-Agent-Guide.md), the Experience Contract and relevant accepted ADRs.

## Evidence-based friction analysis

These are instruction conflicts and scope risks, not measured cycle-time statistics or claims that every prior sprint followed the worst interpretation.

| Observed instruction or condition | Delivery friction | Smallest correction |
| --- | --- | --- |
| CIOS-AI already specifies three Initial Decision Twin outputs; its later Research GPT paragraph demands manifests, validation, release and completion reports without a mode qualifier. The canonical Research Agent Guide lists fourteen output categories. | Routine research can be treated as a full publication exercise. | Qualify the AI-context paragraph by ADR-009 mode and commissioned exchange/profile. Keep material intelligence in the three existing outputs; retain required release formats when actually applicable. |
| CIOS-AI's reading order and architecture-compliance list have no explicit reuse boundary. | An unchanged decision can be reread and rewritten for each commit. | Establish the relevant baseline once; revisit changed owners/assumptions and reuse valid evidence. Preserve the material-conflict escalation rule. |
| Chief Architect pack instructions block recommendation-ready status without programme/runtime evidence and checksum validation. | A specific readiness gate can be misapplied to every reversible presentation edit. | Keep it for that readiness judgement; do not invent a fresh recommendation-readiness exercise for implementation already within accepted contracts. |
| Researcher RKI-001/RG-001 and RG-002 include deep profiles, registers, workspace checkpoints and research-exhaustion obligations. | Applying long-running or commissioned High-Fidelity obligations to a bounded product fix creates unrelated work. | Keep those obligations for their actual research mission/profile. Do not downgrade or relabel a commissioned High-Fidelity mission to evade them; do not impose them on a prose/UI-only sprint. |
| Draft #726 owns the public executive recovery journey; #715 separately changes the Initial Decision Twin research path. | Shared-file edits or wholesale draft merges would entangle product recovery with research machinery. | Separate branch and file set; reference their current state without adopting their functionality. |
| Root ROADMAP describes Genesis/bootstrap work. Existing semantic and semantic-v2 research tracks are present. | Historical plans and extraction experiments can displace the owner’s current product priorities. | Add the P0–P3 sequence, retain the history, and defer experiments unless a named milestone demonstrates the need. |
| Screenshot, CI, merge and deployment evidence answer different questions. | Repeated reviews can still miss a broken ordinary arrival or signed-in experience. | One outcome-focused browser walkthrough plus the existing release checks; record genuine limitations instead of multiplying documents. |

The simplified path is frame → reuse/build → validate → owner outcome review → separately authorised release. It has no new standing approval checkpoint. The fourteen research output categories are not fourteen required documents; their material content is retained while publication artefacts become conditional under ADR-009.

## Minimal instruction amendments

Applied in this PR:

- **CIOS-AI:** record context reuse; reconcile the universal Research GPT output paragraph with ADR-009; add one linked FLORA delivery section. Existing runtime context, authority order, conflict escalation and truth/lineage rules remain.
- **CONTRIBUTING:** link the five-step delivery path and distinguish browser acceptance from merge/deployment authority.
- **ROADMAP:** put the owner’s P0–P3 product sequence ahead of the retained historical plan.

Prepared wording for the next already-required role-pack maintenance, **not applied to packaged GPT configurations in this PR**:

| Existing instruction owner | Minimal insertion |
| --- | --- |
| Chief Architect configuration / operating guidance | “Apply ADR-009 proportionately. Reuse current, valid authority and runtime evidence for unchanged scope. Apply recommendation-readiness and pack-validation gates when making those judgements; do not add a fresh architecture decision for implementation within an accepted contract. Escalate material conflicts through the existing owner.” |
| Researcher RKI-001 / RG-001 | “At intake distinguish ordinary Initial Decision Twin work, Assured Release and any explicitly commissioned High-Fidelity/exchange profile. Apply ADR-009's minimum outputs to ordinary work; retain all material lineage, uncertainty and existing canonical authority. Preserve RG-002 workspace/recovery and the commissioned profile obligations wherever applicable.” |

These are proposed operating clarifications, not an external GPT update. Do not rebuild or republish all Knowledge Packs merely for this sprint. At their next necessary refresh, the existing pack owner validates any adopted wording and checksums using the existing mechanism; no new pack or authority is created.

## Authority and conflict assessment

| Existing authority | Compatibility |
| --- | --- |
| Accepted ADR-009 and Handbook Progressive Assurance amendment | Existing basis for minimum routine outputs, decision-relative sufficiency, autonomy and consequence-based assurance. No ADR text changes. |
| Accepted ADR-001/002/004/005, EI-001 and EI-012 ownership | Preserve atomic Observations, durable memory, human-knowledge labels and inspectable lineage. Product completion is not canonical promotion. Owning papers retain their actual Draft/Review statuses; they are not accepted wholesale here. |
| Accepted ADR-012/014/016/024 | Preserve candidate/import versus canonical acceptance, deterministic runtime validation, exchange contracts and hybrid-runtime ownership. No parallel intelligence or governance engine. |
| Accepted ADR-015 | Mission, Research Policy and Capability Profile may be inherited from the commission; no new intake form. |
| Accepted ADR-026 | Material Pressure qualification stays with its existing deterministic gates and durable-model owner. No automatic Opportunity or Pipeline creation. |
| Accepted public-factual policy and Source-owned implementation | Eligible ordinary factual views do not require per-number approval or universal Evidence promotion. Specific rights, identity, withdrawal, financial-use and private-run controls remain intact. |
| Proposed ADR-027, Review IT-001/EIF-001, historical programme/runtime reports | Preserve their status. Use applicable contracts and actual current code; do not infer accepted architecture, complete implementation or current deployment from these documents. |

No new architectural blocker was found for these documentation clarifications. Broader pack/registry freshness and deep-profile reconciliation remain existing-owner work, not prerequisites for this PR or reasons to edit accepted ADRs.

Two existing metadata inconsistencies are explicit: ADR-014 and ADR-024 headers say Draft, while their Status sections and the ADR index say Accepted. This PR relies on the recorded accepted decisions and preserves the historical texts; it does not silently repair ADRs or treat arbitrary drafts as accepted. Metadata reconciliation belongs to the existing architecture owner.

At preflight #726 was draft `12e0362974784fdbab2a48829756598978e2f78c`, with seven changed paths in presentation code/tests. #715 was draft `5b4b67e6f3fc7d0e60c7d1fcfc7470f2dfb61c2c`, with five research/runtime/test paths. Neither shares a path with this PR. Recheck file intersections before integration because both may evolve. No messages, edits, commits or pushes are made to those branches.

## Validation and completion

The exact changed-file inventory and reproducible validation observations are in [Validation.json](Validation.json). Validate introduced relative links and cited paths; verify the relevant ADR statuses; confirm only the six listed documentation paths differ from base; compare concurrent changed-file inventories; and reverse the complete diff in a temporary index to reproduce the base tree. Historical broken links outside this diff are unrelated backlog, not grounds to expand scope.

Runtime/security/browser suites are not rerun for this prose-only change: their code, tests, data, Source inputs and configuration are byte-identical to validated main. There is no visual implementation to accept in a browser here. Future visual increments retain the browser checks in the doctrine. No hosted workflow is dispatched or new CI mechanism introduced merely to approve documents. Report actual automatically triggered checks, if any, without claiming the base run tested new prose.

Before merge, rollback is closing this draft while retaining the branch/history. After a separately authorised merge, a normal revert of this documentation commit restores the prior guidance; apply it through the existing PR process and preserve any later unrelated edits. The temporary-index reverse test demonstrates source restoration only. No database, permissions, canonical data, release configuration or production rollback is involved.

**Self-critique:** clearer instructions do not prove faster delivery. The first P0 increment must demonstrate owner-visible improvement. Current role-pack consumers will not inherit these clarifications until their ordinary maintained instructions are updated. Expenditure and physical-device/deployment status are not inferred from local checks. Do not turn the proposed doctrine or this validation record into another mandatory report for every sprint.

**Owner acceptance recommendation:** accept the bounded delivery guidance and P0–P3 sequencing. Keep #726's visual/implementation acceptance separate. Merge remains an owner decision; no deployment is requested or authorised.
