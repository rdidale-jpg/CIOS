# FLORA Research Intelligence v2

Builds on main `5106e9e51bd33fe620fe0247038727c6db3fbc32` and the **unmerged** v1 diagnostic in [PR #547](https://github.com/rdidale-jpg/CIOS/pull/547), head `eea6943127a1f0dd0b4b41c97baad4d2d4bd419c`. No merge or deployment is assumed. This candidate includes that small dependency so the v2 draft can be compared and validated against main; #547 remains untouched.

## Architecture reuse and bounded gaps

| Existing owner | Reuse in this increment | Remaining limitation |
| --- | --- | --- |
| RG-001 2.5.0 | Prioritise enterprise understanding, provenance and disconfirming research before opportunities; source-family routes and actionable questions | Not a claim that either Twin passes Research-ready |
| RG-002 1.1.0 | Bounded waves, deterministic checkpoint hashes, retained baseline/history, resumable queue, explicit CONTINUE | Local operational export, not the authoritative full governed Mission Workspace; no exhaustion/completion certification |
| IT-001, High-Fidelity Contract §5.2 and Intelligence Density Matrix | Deficiency screen across fourteen existing enterprise dossier dimensions; source/date/relationship limitations visible | Does not score IT-001 maturity, causal completeness or all 22 controlled dimensions; counts never certify a tier |
| Research Intelligence Diagnostic v1 | Existing `assess()` inventory and registered gap backlog | Its original “source-supported” count includes limited official index excerpts; v2 excludes index-only material from its stronger dossier passage-support count |
| Researcher mission catalogue, profiles and `tools/knowledge-packs/research_missions.py` | Generate and validate **DRAFT targeted-evidence-closure** manifests and reproducible commissions using the owning generator and version pins | The emitted “current governed gaps” section labels each entry a candidate overlay task, not accepted canonical gaps; operator assignment and governance remain outstanding |
| `SemanticTwin` / `SemanticObject` | Existing read-only semantic projection for candidate observations and graph edges; connected-context traversal uses that projection | No new accepted Enterprise identity or competing canonical graph store |
| `SourceSegment`, `CandidateClaim`, `EvidencePackageItem` | Existing passage and Evidence adapters; imports extract exact located quotations into candidate contracts | A quotation does not automatically entail a reviewer’s target/effect or prove publisher authorship |
| Observation memory identity functions | Existing deterministic fingerprints with enterprise, attribute and reporting-period scope | Accepted `Observation` objects are intentionally **not** persisted: their existing contract requires accepted Evidence IDs |
| Existing overlay graph and revision history | Original claim/relationship IDs, unknowns, sources and full baseline retained; proposed contradiction/supersession links are additive | Contract award/expiry and measured programme→outcome relationships remain unmodelled, not fabricated |
| Existing Unified views and access controls | Extend the two exact diagnostic GET routes, shared shell, responsive details and existing evidence drill-downs | No new public upload, generic lookup, authority mechanism, private-package reader or Pipeline mutation |

The source of truth remains the existing research and governed frameworks. The cycle/checkpoint is a derived operational proposal, not a replacement Twin or accepted Evidence model.

## Working research journeys

Open **Enterprises → Lloyds / easyJet → Research Intelligence Diagnostic**.

Inspect the original inventory, **Deepen enterprise understanding**, the selected next evidence wave, fourteen dossier dimensions, source freshness/extent and connected relationships. Expand a topic to inspect evidence needs, suggested searches (including contrary evidence), source families and closure tests. Follow claim links to the existing passage/provenance pages.

[Desktop Lloyds](previews/desktop-lloyds.png) · [Desktop easyJet](previews/desktop-easyjet.png) · [Tablet Lloyds](previews/tablet-lloyds.png) · [Tablet easyJet](previews/tablet-easyjet.png)

Desktop 1440×1000 and tablet-sized 1024×1366 Chromium checks cover navigation, task expansion, passage drill-down, no horizontal page overflow and no runtime errors. These are not physical iPad/Safari tests.

## Reference outputs at 10 November 2026

| Reference | Existing inventory | Selected next tasks |
| --- | --- | --- |
| [Lloyds assessment](lloyds-assessment.json) | 45 claims; 24 v1 source-supported; 24 sources; 1/123 graph edges source-supported | Operating-model deficiency (49); AI benefit evidence (48); programme/investment allocation (48) |
| [easyJet assessment](easyjet-assessment.json) | 22 claims; 22 v1 source-supported **with extent limitations**; 14 sources; 3/58 edges source-supported | Measured operating outcomes (48); fuel-data responsibilities (48); industry coverage and competition (48) |

Priority is a transparent research-effort rule, not truth confidence or deal likelihood: domain materiality ×10 plus deficiency 3/6/9, registered High gaps 48 and customer qualification deferred to 12, with stable-ID tie-breaks. Missing mapped factual claims are a conservative lower-bound screen: domain aliases can omit facts expressed elsewhere. Missing structure is not evidence of real-world absence. Publisher counts do not establish independent corroboration; period-label counts do not establish comparability. Publication age is distinct from collection date and source effective period.

The committed [Lloyds mission](lloyds-mission.json) / [commission](lloyds-commission.md) and [easyJet mission](easyjet-mission.json) / [commission](easyjet-commission.md) are reproducibly generated from the current existing evidence. They are draft research work orders, not issued authority or a new research architecture.

**Acquisition update:** direct shell networking remains restricted, but the approved web-research tool successfully opened two official pages on 10 November 2026. The real reference cycle now retains a short located Lloyds Athena metric and easyJet SSDM reference as proposed observations. The Lloyds article was published 29 January 2026; easyJet’s page has no verified publication date. These are newly reviewed excerpts, not new publication claims or full original archives. Original page bytes are unavailable and their hashes remain null. Existing snapshots and overlays are unchanged. No network restriction was bypassed. Four proposed-effect behaviours remain explicitly synthetic tests, not invented customer findings.

## Repeatable local cycle

```sh
python tools/research/flora_cycle.py --enterprise lloyds --as-of 2026-11-10 --output /tmp/lloyds-wave-1
python tools/research/flora_cycle.py --enterprise easyjet --as-of 2026-11-10 --output /tmp/easyjet-wave-1
```

Use a **new** local output directory each time. The page also exposes a retained public source review, its publication/retrieval distinction and proposed implications. Output: `plan.json`, `checkpoint.json`, `mission.json` and generated `commission.md`. No runtime store, environment flag or production configuration is used. Limit is 1–10 tasks (default three), with at most eight located passages of 20–4000 characters per supplied source.

For acquisition, pass `--submissions /LOCAL/submissions.json`. Its JSON array has one entry per selected task:

- `task_id`: a selected stable task ID from the plan.
- `path`: a local downloaded HTML, PDF or UTF-8 text file.
- `metadata`: the existing `source_import.import_proposal` contract: official and retrieval URLs, title, publisher, reporting period, timezone-aware retrieval date, publication date/evidence or explicit unknown, reviewed-by/notes, downloader provenance attestation, expected original-byte SHA-256, and `reviewed_quotes` containing `quote` and `locator`.
- `effect`: `strengthen`, `weaken`, `invalidate`, or `new`; `target_claim_id` must name an existing **same-enterprise** claim for the first three, and be null for new findings.
- `rationale`: explicit reviewer reasoning; semantic entailment, atomicity, author authenticity and contrary evidence remain review requirements.

Alternatively, an entry may supply `source`: the existing reviewed-web-excerpt descriptor (same registered industry, confined public snapshot path, text checksum, official retrieval URL/reference, dated provenance and located `excerpts`). The cycle reuses `model.primary_text`; it rejects cross-domain paths, changed text or a fabricated original-byte hash. The two committed `enterprise-knowledge/{banking,aviation}/research-model/Research-Cycle-v2-Source.json` receipts are working examples. These are candidate acquisition receipts, not additions to the canonical source registry.

Original supplied bytes are retained under the explicit **local** `sources/` output with content-addressed names. Retained web excerpts are archived with an explicit `.excerpt.txt` suffix and null original-byte checksum. Metadata and located excerpts remain in the checkpoint. Same-document receipts retain matching existing source IDs rather than replacing them. Do not commit private research bundles. File hashes establish consistency, not publisher authenticity. A supplied file must not claim a hash of original bytes that are unavailable. Index-only excerpts stay limited until original-source re-verification.

Resume with `--resume /LOCAL/prior/checkpoint.json --output /LOCAL/new-wave`. Previously acquired tasks remain explicitly pending review while the acquisition queue advances; no task or Unknown is automatically declared closed. Prior waves and full original overlay remain retained; altered checkpoint digests, another enterprise, changed baseline or backwards cut-off fail. On a changed baseline, explicitly review/rebase instead of overwriting history. Checkpoint hashes are integrity checks, not authentication. Preserve previous bundles so earlier acquired original files remain addressable.

A new passage produces stable candidate IDs, exact quote hashes/locations, target lineage, proposed effect and outstanding review checks. Contradictory evidence remains linked to its target. A proposed invalidation leaves the original fact and historical period intact; mismatched reporting periods cannot invalidate a historical finding. Nothing promotes a canonical finding, creates accepted Observations, resolves Unknowns or qualifies a Pipeline deal automatically.

## Verification and next increment

- Focused cycle tests: 25 identities, including both enterprises, four proposed effects, provenance/quote/cross-scope rejection, bound enforcement, checkpoints/resume, semantic reuse, canonical mission generation, CLI export and existing HTTP routes.
- An initial full-gate attempt correctly failed on a malformed new-suite selection (pytest received a filename character rather than the required selection list). The list configuration was corrected; no test assertion or inherited exception was relaxed.
- The CI baseline adds only mandatory passing v2 identities; all pre-existing failure signatures and ten original skip identities/reasons remain unchanged. The runner and strict security comparator are unchanged.
- Final local established gate: **PASS before the four additional excerpt tests — 1,012 passed, 57 matched inherited failures, ten original skips; 1,079 unique identities.** The final focused suite has 25 cycle tests and four diagnostic tests. The final-candidate full gate is rerun and reported in the PR; no earlier result is attributed to later code. Separately, all 25 CI-policy tests and actionlint pass. Actual draft-candidate hosted status is reported in the PR, not inferred from this local result.

The real reference review adds detail but closes no material gap: Lloyds’ Athena measure is a product-specific company report, not proof of net Group-wide AI benefit; easyJet names an existing disruption self-service response but supplies no measured deflection or cost baseline. No customer budget, supplier award or buying intent follows.

Next: obtain verified original documents for the three selected tasks per enterprise, run those imports, inspect opposing evidence and adjudicate the proposed observations through the existing governed Evidence workflow. Deepen programme→capability→supplier/contract→measured-outcome relationships only when supported. Assign a research operator and integrate these operational exports into an existing authorised Mission Workspace before claiming persistent autonomous RG-002 operation. No extra commercial candidates are needed to demonstrate progress.

Known limitations: deterministic mapping rather than a complete semantic field audit; coarse hand-declared materiality; missing causal-depth and independent corroboration assessments; incomplete structured contract/outcome and contradiction registers; private customer demand remains unverified; no browser upload/background crawler; no deployment or production-data modification.
