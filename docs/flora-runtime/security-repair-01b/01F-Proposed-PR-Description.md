# FLORA 01B–01E: verified workspace authority and bounded integrity repairs

Verified human authority now governs protected FLORA workflows through server-controlled workspace membership, effective capabilities and resource ACLs. Conflicting or missing persisted scope fails closed. Human-reviewed financial claims cannot use a permitted Enterprise alias to write Evidence or model attributes for another Enterprise/workspace. Destructive candidate deletion now shares the existing authority transaction, recovery journal and mandatory audit boundary, including protection against stale promotion and revocation decisions.

## Dependency and review boundary

Depends on draft [#539](https://github.com/rdidale-jpg/CIOS/pull/539), pinned at `83aee1aaf5a49b36d8c5e397d75b99624422fac3` (`codex/flora-security-repair-01a`). This stack must be reviewed against that dependency, not directly against main as if 01A were new work. At 01F verification, #539 remained open, draft and unmerged, with main base `dc9203e6880f8722e821d39cf53b689732edb0e7`. Reconcile and revalidate if its head or base materially changes.

**Suitable for peer review; not deployment approval.** No production identity provisioning, production configuration/data change, merge or deployment is included. The security bootstrap remains fail closed; no caller-created context, legacy shared cookie or environment shortcut grants production privilege.

## Implementation

- Verified individual enrollment/sign-in/session authority, expiry/revocation, CSRF/origin protections and attributable server-controlled membership/capability evaluation.
- Persisted workspace and Enterprise scope intersect applicable ACLs for financial, Blueprint, Canvas feedback, commercial-context, executive-brief and recovery operations. Enterprise wildcard access cannot select a different workspace.
- Financial apply and its downstream reviewed-ingestion boundary reload the authoritative run and validate declared/canonical/normalized destinations before Evidence or model writes.
- Blueprint promotion retains a consistent administrator policy. Candidate deletion requires recent authority, fresh persisted scope and governance checks, and resource ACL revalidation. Adjacent cancellation enforces its own service boundary.
- Consequential service writes serialize through the canonical authority SQLite transaction and protected filesystem journal. Resource audits, domain ledgers and effects fail atomically; independently committed participating writes survive rollback.
- Recovery validates the complete manifest, durable checksum seal, unique backup inventory, contents, paths and metadata before destructive undo. Invalid recovery artifacts remain available and block authority; interrupted valid recovery can retry. The seal detects corruption and does not authenticate storage against an actor able to rewrite private artifacts.

## Validation

01E acceptance and exact-ID comparisons are retained in the committed evidence; 01F verifies unchanged source hashes/inventory and freshly reruns the seven original adversarial tests.

| Gate | Result |
| --- | --- |
| Security | 388 passed, including all seven original adversarial checks and 23 focused 01E checks |
| Protected-data integrity | 146 unchanged comparisons |
| Committed audit digests / selected audit chains | 17 matching / 15 valid |
| Established domain gate | 404 passed, 22 inherited failures, 10 original skips |
| Factory | 88 passed, 8 skips |
| Experience | 56 passed, 2 skips |
| Governance | 157 passed |
| Supplemental | 39 passed |
| Legacy positive obligations | 19/19 satisfied |
| Historical legacy | 3 passed, 24 historical failures |
| Additional financial diagnostics | 35 passed, 12 unchanged failures |

The repository is not wholly green. The 22 domain failures retain matching original-HEAD evidence and first-failure signatures. The 24 legacy failures include 19 intentionally retired insecure contracts and five pre-existing failures. Twelve additional financial diagnostic failures match hash-verified pre-01E accumulated code; they remain separate from the established 22-domain baseline. Ten original skips require unavailable retained TEL-W6/BNK-W1 artifacts. No new active security/domain regression or unexpected skip was reported. The archived incompatible concurrency harness is preserved as historical evidence; its approved corrected active test retains the security assertion and passes.

## Residual risks and qualification

Production mount/fsync/rename/locking semantics, snapshot/reserve capacity and ENOSPC behavior, load/lock contention, concurrent instance topology, external writers, backup restoration, off-host disaster recovery and migration/rollback require separate qualification. The protocol assumes a private security directory, one canonical authority database/shared protected root and participating writers. Unsealed pending journals require inspected recovery before upgrade; ownership must never be fabricated to unblock migration. Inherited product/harness failures and missing retained inputs remain visible qualification limits.

## Evidence and scope

Start with [01E closure](01E-Bounded-Remediation-Report.md) and its machine-readable evidence. [01F commit inventory](01F-Commit-Preparation.md) separates production, tests, dependencies and essential evidence. Selected 01D reports explain the final independent findings and approved concurrency correction; their earlier verdicts/counts are historical and are superseded by 01E. Failure and legacy obligation registers remain included.

Private `work/`, temporary databases, synthetic stores, raw local logs and duplicate/superseded reports are excluded from the change set. Excluded historical files remain intact locally. Published JSON contains acceptance metadata, test IDs, normalized signatures and hashes; local artifact paths are provenance references, not bundled stores/logs. Broad security discovery or unrelated refactoring is outside this PR.
