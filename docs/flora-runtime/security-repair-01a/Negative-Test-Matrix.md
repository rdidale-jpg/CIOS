# Security Repair 01A negative security test matrix

All cases run against isolated temporary roots. The production-boundary module
uses the actual resolver and local HTTP handler, without the service-test identity
provider. Three separate service-contract cases use an explicit fixture context to
prove read-only GET semantics even when a downstream caller is authorised.

| Cases | Boundary/evidence |
| --- | --- |
| unverified_claims_never_resolve_authority | Unsigned cookies, conflicting roles/workspaces/enterprise grants, spoofed headers and a trust flag cannot authenticate in production/pilot/development/absent mode. Deployment fingerprint reports the closed boundary. |
| mutating_http_routes_closed_before_dispatch | Seventeen privileged/new-admin paths deny before executors, body parsing or store mutation. Cross-origin headers cannot bypass denial. |
| protected_gets_deny_without_disclosure | Eight private GET families deny without names, counts, IDs or fingerprints and preserve all fixture-store bytes. |
| public_import_entry_does_not_read_or_disclose_registry | Registry reader is replaced with a failing sentinel; public setup renders without invoking it. |
| shared_pilot_cannot_record_human_review | Shared pilot mode cannot create human-review acknowledgement or change store bytes. |
| promotion_service_rejects_forged_owner_before_loading_plan | Direct promotion approval rejects spoofed owner before plan lookup or writes. |
| service_mutations_fail_closed | Direct financial review/apply, recovery, destructive cleanup, candidate deletion, feedback, Commercial Context and brief services deny; no changed fixture records. |
| public_discovery_exposes_only_curated_context | Forged privileged claims expose only curated Banking source context. |
| public_source_views_survive | Public Banking, Intelligence, Digital Twins and closed sign-in remain readable without touching stored imports/canonical records. |
| public_preference_post_rejects_cross_origin | Missing, wrong and null Origin deny the non-authority preference POST. |
| public_preference_is_not_an_authority_grant | Exact configured Origin permits only a reference-navigation cookie; no server intelligence write or identity grant. |
| legacy_listener_cannot_mutate | The obsolete workspace listener cannot accept unauthenticated writes. |
| review_coordinator_rejects_before_job_creation | Direct preparation cannot write a job/defaults without authority. |
| wrong_workspace_history_does_not_disclose | Forged wildcard grants plus another workspace cannot enumerate imports/tombstones. |
| legacy_signed_sessions_have_no_authority | Valid legacy signed, expired and tampered tokens cannot authenticate. This tests retirement, not a new session implementation. |
| legacy_flags_cannot_enable_authority_or_break_public_reads | Auto-sign-in, bypass and auth flags cannot enable privilege or block public source discovery. |
| review_get_does_not_prepare_or_write | Authorised service fixture GET never calls preparation; complete fixture fingerprint unchanged. |
| verified_fixture_wildcard_cannot_cross_resource_workspace | A wildcard enterprise fixture grant cannot bypass explicit resource workspace; history does not expose the other workspace. |
| review_get_without_job_preserves_existing_records | GET without a prepared job returns a read-only explanation and changes no records. |

## Regression fixture changes

Legacy domain/governance modules explicitly opt into an in-process fixture
identity provider in tests/flora_security_fixtures.py. It is not imported by
production code and is not installed in real_security_boundary tests. These
service tests are not evidence of real sign-in or server membership readiness.
Actual HTTP handlers remain closed even when a domain fixture is installed.

Review domain tests perform explicit preparation instead of relying on GET
side effects. Reasoning domain tests supply an explicit fixture request context.
The public resume-cookie test supplies configured Origin. Existing domain
assertions are retained. The old assertion accepting an encoded unsigned owner
cookie is replaced with rejection, while owner-role alias evaluation retains a
positive fixture-context assertion. Its renamed test ID is recorded in the
exact-case comparison; the same revised test is used on main and the repair.

No tests are skipped to hide an authentication failure. Missing retained BNK W1
and TEL W6 archives retain the existing explicit skips. Retained TEL W5 bytes are
hash-checked by the existing Factory/Experience journeys.
