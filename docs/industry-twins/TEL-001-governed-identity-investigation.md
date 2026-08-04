# TEL-001 governed identity and scope investigation

## Finding and first failing boundary

**Classification: incomplete Researcher-facing package contract.** The immutable
package is a valid Blueprint profile 1.0 package. Its root manifest identifies
the access/envelope enterprise as `TEL-001`, the package as
`TEL-001_UK-Telecoms-Twin_Wave5-Corrected`, and the profile/version. Profile 1.0
previously had no fields with which a producer could declare the governed Twin
association, primary subject, governed scope, or canonical owner. Flora could
therefore display “Enterprise TEL-001” from the receipt envelope while the
separate governed identity projection correctly remained ambiguous.

Candidate content does contain `twin_id: TEL-001` and the title “UK
Telecommunications Industry Twin” in `composite_industry_twin_wave5`; the
industry overview contains a prose UK telecoms scope. Those are candidate
research records, not a complete owner-backed package identity declaration.
There is no `canonical_owner`, `primary_subject_id`, `primary_subject_class`, or
complete governed identity tuple anywhere in the ZIP. Joining record labels and
prose across files would create a second, inferential identity model and was not
implemented.

## Identity-resolution flow

1. `BlueprintManifest` validates `blueprint_manifest.json`; `read_identity`
   creates the receipt envelope (`package_id`, version, `enterprise_id`, and
   profile).
2. `PackageContractDetector` preserves the manifest as package metadata and now
   projects the optional, complete governed identity tuple through the shared
   inspection adapter.
3. Validation maps declared record sets into staged candidates. Candidate
   payload identity remains candidate evidence and cannot overwrite package
   governance.
4. `project_twin_identity` overlays an audited identity-resolution decision, if
   present, on the immutable package inspection. Otherwise it accepts only the
   complete explicit inspection tuple. An access `enterprise_id` supplies the
   legacy Blueprint enterprise default, but cannot supply a missing subject
   name or governed scope.
5. Review reads that same projection. Ambiguity blocks promotion but does not
   change individual candidate staging dispositions.
6. Dry-run planning calculates effects only. Approval and execution remain
   separate authorised lifecycle operations; identity resolution never writes
   canonical memory.

## Canonical owner map

| Value | Canonical authority | Runtime owner |
|---|---|---|
| Blueprint package identity and access enterprise | `blueprint_manifest.json` | `BlueprintManifest` / package registry |
| Package-to-Twin association | complete manifest governed tuple, or audited match to an already recognised package | `project_twin_identity` and `GovernedIdentityResolutionRepository` |
| Twin identity and primary subject | same owner-backed governed tuple | `TwinIdentityProjection` |
| Governed scope | explicit governed tuple; never filename/content inference | `TwinIdentityProjection` |
| Canonical owner | explicit `canonical_owner` from the governed tuple/recognised registry record | `TwinIdentityProjection` |
| Candidate dispositions | validation findings and reviewer decisions | candidate staging/review repositories |
| Promotion | separately authorised dry-run approval and execution | existing promotion lifecycle |

`GovernedIdentityResolutionRepository.confirm_existing` requires an actor,
rationale, and an existing different registry package whose identity projection
is already recognised. It persists an immutable-checksum-backed audit overlay
under the import run, and subsequent Review/projection requests read it. It
cannot resolve this package in an empty registry and cannot create a free-text
Twin. The former Review anchor exposed no input or POST route, so it was a
description of this service rather than an operable decision surface.

## Exact immutable package inventory

| Requested identity/scope evidence | Present? | Evidence and treatment |
|---|---:|---|
| Governed Twin identifier | No | `TEL-001` occurs as envelope `enterprise_id` and candidate `twin_id`, but no complete governed declaration exists |
| Primary subject identifier/name/class | No | title/name-like candidate values exist; the required governed tuple does not |
| Governed scope declaration | No | the industry overview has a research `definition.scope`, not package governance |
| Canonical owner reference | No | absent |
| Geography | No governed field | “UK” appears inside candidate prose/title |
| Time horizon | No governed field | horizons occur in commercial candidate records, not package identity |
| Included sub-sectors | No governed field | topics appear in candidate scope prose |
| Implementation profile references | Yes | manifest `profile_version: 1.0.0`; import metadata names the Flora contract and Researcher Knowledge Pack |

The reusable contract correction adds a fail-closed optional governed identity
tuple and optional scope-display metadata. Supplying only part of the tuple is a
contract error. The detector now consumes a complete tuple from the canonical
manifest. The TEL-001 ZIP is unchanged and therefore receives an explicit,
actionable missing-governed-identity blocker rather than a guessed identity.

## Quarantine reconciliation and before/after status

The package stages **1,060** candidates: **640 accepted**, **413 ignored**, and
**7 finally quarantined** transformation-pressure projections. The old reported
1,060 quarantine was a provisional package-wide “not promotable while identity
is unresolved” hold presented as though it were an item disposition. It was not
backed by 1,060 quarantine findings, which is why “Quarantined by reason” could
say None. Review now labels only final staging quarantine as quarantine, states
that identity holds are provisional and excluded, and totals the explicit
staging-reason groups to the same value (7).

| Output | Before (reported) | After |
|---|---|---|
| Proposed Twin identity | unresolved | unresolved with explicit missing-contract blocker |
| Primary subject | unresolved | unresolved (genuinely absent governed evidence) |
| Governed scope | unresolved | unresolved (genuinely absent governed evidence) |
| Canonical owner | unresolved | unresolved (absent) |
| Staged | 1,060 | 1,060 |
| Accepted | 0 reported | 640 staging-accepted candidates; no canonical writes |
| Quarantined | 1,060 reported | 7 final; package-wide identity hold separately provisional |
| Quarantine reasons | None | explicit staging reason total 7 |
| Promotion | blocked | blocked by identity; separately authorised even after resolution |

## Recommendation

**REVISE.** The first failing boundary is fixed for future generic Blueprint
packages and the exact TEL-001 package now has coherent dispositions and an
actionable blocker, but TEL-001 must remain unresolved because its immutable
package lacks canonical-owner-backed governed identity and there is no evidenced
existing recognised registry entry to select. Changing that status would require
producer-supplied governed metadata or an authorised match to an existing
governed registry record—not a Flora guess.
