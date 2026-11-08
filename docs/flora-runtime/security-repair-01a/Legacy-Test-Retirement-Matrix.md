# Legacy authentication test retirement matrix

All 27 historical cases still run unchanged and separately. None is silently
excluded, skipped, relaxed or counted as passing. Nineteen previously passing
cases depend on retired authority/presentation contracts; their negative
replacements pass in 01A. Their legitimate authorised workflows require real
01B coverage. Some historical tests contain sound negative assertions but fail
in obsolete pilot setup before reaching them; those assertions remain obligations.
Retirement is a documented contract classification, not deletion of the suite.

The JSON companion records exact parametrized replacement IDs; this table uses
function names for readability. Each row is classified **replaced; requires future
positive coverage**. This does not assert that negative tests prove the future
positive workflow.

| Historical exact test ID | Obsolete expectation/setup | Replacement negative function | 01B obligation |
| --- | --- | --- | --- |
| `tests/test_flora_pilot_auth.py::test_blueprint_get_and_post_use_same_signed_session_and_anonymous_denied` | Shared pilot cookie authorises import GET/POST | `test_legacy_signed_sessions_have_no_authority` | Individual sign-in grants only member/capability/ACL-bound import access |
| `tests/test_flora_pilot_auth.py::test_cookie_security_attributes_for_https_deployment` | Legacy shared-secret issuer supplies HTTPS cookie | `test_mutating_http_routes_closed_before_dispatch` | Real issuer sets Secure, HttpOnly, SameSite and bounded expiry |
| `tests/test_flora_pilot_auth.py::test_deprecated_auto_sign_in_conflicts_with_canonical_pilot_mode` | Pilot-mode flags determine automatic sign-in behavior | `test_legacy_flags_cannot_enable_authority_or_break_public_reads` | No automatic/shared actor sign-in under any legacy mode |
| `tests/test_flora_pilot_auth.py::test_persistent_cookie_has_30_day_expiry_survives_restart_and_rejects_expired` | Thirty-day shared pilot cookie survives restart | `test_legacy_signed_sessions_have_no_authority` | Real sessions obey approved absolute/idle expiry, restart and revocation |
| `tests/test_flora_pilot_auth.py::test_pilot_auto_sign_in_defaults_false_and_refuses_non_pilot` | Environment pilot configuration can enable automatic identity | `test_legacy_flags_cannot_enable_authority_or_break_public_reads` | Explicit individual sign-in only |
| `tests/test_flora_pilot_auth.py::test_pilot_auto_sign_in_missing_canonical_configuration_fails_safely[FLORA_PILOT_ROLE-membership]` | Environment role configuration supplies membership | `test_unverified_claims_never_resolve_authority` | Server membership roles independent of environment configuration |
| `tests/test_flora_pilot_auth.py::test_pilot_auto_sign_in_missing_canonical_configuration_fails_safely[FLORA_PILOT_WORKSPACE-workspace]` | Environment workspace configuration supplies membership | `test_unverified_claims_never_resolve_authority` | Server membership selection and cross-workspace denial |
| `tests/test_flora_pilot_auth.py::test_pilot_sign_in_route_accepts_secret_only_by_post_and_sets_cookie` | POST shared secret issues an authority cookie | `test_mutating_http_routes_closed_before_dispatch` | Individual authentication issues protected session; query secrets never accepted |
| `tests/test_flora_pilot_auth.py::test_sign_in_issues_one_cookie_and_browser_reuses_it_for_import_get_and_post` | Shared pilot cookie is reusable import authority | `test_legacy_signed_sessions_have_no_authority` | One real individual session across authorised import GET/POST and revocation |
| `tests/test_flora_pilot_auth.py::test_synthetic_headers_ignored_and_tampered_cookie_rejected` | Setup creates legacy pilot cookie before testing tamper/header rejection | `test_legacy_signed_sessions_have_no_authority` | Real token integrity and header rejection; preserve sound negative assertions |
| `tests/test_flora_pilot_auth.py::test_unexpected_diagnostic_storage_failure_preserves_denied_context` | Diagnostic failure journey first issues a shared pilot cookie | `test_protected_gets_deny_without_disclosure` | Unavailable diagnostic/audit store fails closed without leaking context |
| `tests/test_flora_pilot_auth.py::test_valid_pilot_session_cookie_resolves_owner_workspace_role_and_policy` | Pilot cookie resolves owner/workspace/role from configuration | `test_unverified_claims_never_resolve_authority` | Server identity and active membership resolve least-privilege policy |
| `tests/test_flora_pilot_blueprint_review.py::test_non_pilot_workspace_and_capability_checks_are_unchanged` | Browser role/workspace claims satisfy non-pilot capability checks | `test_arbitrary_objects_and_claims_cannot_supply_context` | Verified member can review only permitted workspace resources |
| `tests/test_flora_pilot_blueprint_review.py::test_pilot_upload_review_and_dispositions_do_not_grant_promotion` | Pilot upload/review/disposition path is authorised by shared actor | `test_shared_pilot_cannot_record_human_review` | Individual review/dispositions attributed correctly, no implicit promotion |
| `tests/test_flora_pilot_import_bypass.py::test_deployment_endpoint_identifies_canonical_import_runtime` | Public deployment endpoint returns environment-derived runtime metadata | `test_public_fingerprint_excludes_environment_configuration` | Public safe code fingerprint; sensitive diagnostics require scoped authority |
| `tests/test_flora_pilot_import_bypass.py::test_form_validation_secure_mode_and_promotion_boundary` | Anonymous form processing occurs before the authority boundary | `test_mutating_http_routes_closed_before_dispatch` | Authorised input validation and separate promotion privilege |
| `tests/test_flora_pilot_import_bypass.py::test_one_canonical_mode_and_conflicting_legacy_modes_fail` | Legacy mode flags define a functional pilot authority mode | `test_legacy_flags_cannot_enable_authority_or_break_public_reads` | Mode flags never enable authority |
| `tests/test_flora_pilot_import_bypass.py::test_secure_mode_settings_route_reports_root_authorisation_decision` | Anonymous settings exposes detailed root authorization context | `test_protected_gets_deny_without_disclosure` | Authorised settings reveal only scoped diagnostics |
| `tests/test_flora_pilot_import_bypass.py::test_validation_and_archive_safety_precede_identity` | Anonymous archive validation precedes verified identity | `test_mutating_http_routes_closed_before_dispatch` | Authorised archive safety/validation before import mutation |

## Five failures already present on main

These five IDs failed before 01A and still fail. They are not part of the nineteen
intentional newly incompatible cases. Current fail-closed rejection can mask the
earlier assertion, so identical failing status is not proof of identical cause.
The original sanitized diagnostics/hashes remain in Retired-Legacy-Contracts.json.
They require reconciliation with real authorised 01B fixtures and current UI/import
expectations, without restoring browser or pilot authority.

- `tests/test_flora_pilot_auth.py::test_cios_owner_can_upload_inspect_and_stage_mod_package_without_canonical_mutation`
- `tests/test_flora_pilot_auth.py::test_owner_managed_enterprise_policy_is_case_normalised_and_workspace_bound`
- `tests/test_flora_pilot_import_bypass.py::test_configured_module_complete_http_commercial_context_and_twin_map`
- `tests/test_flora_pilot_import_bypass.py::test_deployed_equivalent_pilot_route_imports_candidate_to_executive_workspace`
- `tests/test_flora_pilot_import_bypass.py::test_pilot_configure_save_and_recompose_uses_narrow_actor_scope`

## Accounting

Original main: 22 passed / 5 failed. Initial PR head: 3 passed / 24 failed.
Review closure: compare all 27 exact IDs against the initial PR head in
Review-Closure-Regression-Comparison.json. The nineteen and five are disjoint;
all twenty-four failing cases are explicitly retained in reporting. New negative
coverage is additive and runs without installing a production identity provider.
