# F1 — typed financial candidate analysis

Implements [Issue642](https://github.com/rdidale-jpg/CIOS/issues/642) from `origin/main` / FIG-1 merge `9f3dcc5b0577eb0408bc0185f0847de19a5c1f66`. Full post-merge [main CI43842727235](https://github.com/rdidale-jpg/CIOS/actions/runs/43842727235) passed. The branch was created from that exact main while the post-merge run was still completing; final acceptance is based on its completed success and the new exact-head checks. GitHub identity does not establish Render deployment identity. The public deployment endpoint could not be read by the available tool; production identity is unverified, with no production access or change performed.

## Actual result

Two **real Bank of England Database LPMZ598** historical measurements: **1,884,726 GBP million at31May2026** and **1,886,281 GBP million at30June2026**. These are UK monetary-financial-institution sterling household retail-deposit stocks, excluding notes/coin, not seasonally adjusted. They are not Lloyds or another named bank's balances.

The existing Financial run repository stores the typed measurements and fixed recipes/input revisions. After an actual repository reload, existing Statement arithmetic plus a bounded percentage operation reproduces **1,555 GBP million** and **0.082505361522046…%** (display0.0825%). These are comparisons of reported stocks, not the Bank's official adjusted flow/growth series, organic inflows, profit, margins or buying needs. This adds **two reported measurements and two derived analytical results**, not four accepted facts.

The real source-to-result proof uses an actual temporary Financial repository and synthetic local authentication/workspace/ACL only. It is not production authority or canonical acceptance. Generic contracts also preserve duration measurements and assumption-dependent results in the same repository in clearly marked Banking/Technology/Aviation tests; those extra company figures are fixtures, not research.

## Scope and limits

- Existing `NumericFactValue`, Financial normalisation scales, Financial run repository, Source snapshot/provenance checks, verified-service/IAM/ACL, Statement/difference and FLORA presentation are reused. No new engine, database, registry or canonical owner.
- An opt-in trusted Financial service creates a candidate run; the existing protected `/ai-financial-report/{run_id}` route displays it. No auto-collection, new public route, global navigation or default population. The older `/financial-intelligence/{id}` web route remains outside the current private-read catalog.
- Typed instant/duration semantics apply to the new versioned payload. Legacy FY records/IDs and old canonical paths are not silently reinterpreted or migrated. Candidate metric definitions do not grant canonical metric mapping or peer comparability.
- Source/use/revision and tenant/resource authority are checked on every external read. Withdrawal removes the title, inputs, numbers, source links and derived output; internal lawful run history remains. There is no analytical result cache or bulk export. `read_run` is current-use filtered; `load_run` remains an internal trusted repository primitive.
- This is a **historical sector funding-context pilot**, not comprehensive Banking analysis or named-bank admission. No actual duration-flow source is added. Source publication day and original release vintage are not verified; only reviewed original-database excerpts were captured, with a genuine retained-text hash and null original-byte hash.
- Current owner-state invalidation is proved. Automatic detection of remote site/licence changes and ongoing data refresh are future work. The bounded editorial source review ends16December2026; this is not a declaration that the OGL itself expires.

Read [architecture/contract](Architecture-and-Contract.md), [source-use decision](Source-Admission.md), [validation](Validation.md), [independent critique](Independent-Critique.md) and [owner acceptance/rollback](Owner-Acceptance-and-Rollback.md). Exact final SHA and hosted outcomes are recorded in the PR validation comment and artifact manifests, avoiding a self-referential commit hash in committed proof output.

No canonical Evidence/Observation/Model mutation, publisher-policy change, ADR acceptance/change, Offers/Pipeline change, paid call, merge or Render deployment. EAR-1#640 remains separate and unmerged. Stop for owner review.
