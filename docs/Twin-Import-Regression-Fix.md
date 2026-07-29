# Twin import regression fix

## Root cause

Git history shows that commit `dbfc960` added the governed package importer and
linked it from Digital Twins as **Import Blueprint**, rather than the established
user-facing **Import Twin** action. Commit `67e98cc` then replaced the Digital
Twins landing/list experience and carried that generic label forward. The route,
upload control, registry receipt, validation, candidate staging and governance
services were not removed. The regression was a discoverability and navigation
contract failure: the current Twin experience did not expose an action recognisable
as **Import Twin**, so the supported route was effectively hidden in plain sight.

Commit `5632e78` subsequently made the existing import-run route open the new
Executive Intelligence Workspace after upload. That redirect is correct and is
retained; it was not the cause of the missing entry point.

The pilot failure had a second cause. The original importer in `dbfc960`
required a resolved user, workspace membership and upload permission before its
GET or POST path could proceed. Later recovery commits added a secret-backed
session (`fb54dae`), a route-boundary HTML guarantee (`f0cf19e`), auto-sign-in
(`2cf9cb5`) and a scoped import bypass (`65dcf40`). Those compensating paths made
it unclear which deployment setting owned the pilot journey. Commit `f7c53b4`
removed the route injection and consolidated import authority under
`FLORA_ENVIRONMENT=pilot`; repository HEAD therefore contains the recovery, but
the production evidence supplied on 29 July 2026 is consistent with an older or
differently configured deployment. Production SHA and environment remain to be
verified by the deployment operator.

## Repository runtime path

| Concern | Canonical repository owner |
| --- | --- |
| Render start | `python -m cios.applications.flora.web.app` |
| GET `/digital-twins` | `FloraWebHandler.do_GET` → `digital_twins_landing_page` |
| Digital Twins HTML | `cios/applications/flora/digital_twins.py` |
| GET `/blueprint-import` | `FloraWebHandler.do_GET` → `import_blueprint_entry_page` |
| POST `/blueprint-import/upload` | `FloraWebHandler.do_POST` → `upload_and_validate_blueprint` |
| Pilot import policy | `cios/applications/flora/pilot_import.py` |
| Package receipt and inspection | `BlueprintPackageRegistry.receive` → `BlueprintPackageValidator.validate_and_stage` |

`render.yaml` installs third-party requirements only and starts the module from
the repository working tree. There is no `Dockerfile` or `Procfile`, no editable
or wheel installation of `cios`, and no second route registration. The separate
`cios/applications/flora/workspace/app.py` is a workspace service object, not an
HTTP server and not the configured Render entry point.

## Regression evidence

| Capability | Last known-good | First regressing or blocking change | Current canonical owner | Current repository result |
| --- | --- | --- | --- | --- |
| Discoverable import entry | `dbfc960` exposed `/blueprint-import` as **Import Blueprint** | `67e98cc` retained the route but its catalogue rewrite and generic label did not protect the **Import Twin** product contract | `digital_twins_landing_page` | Visible exactly once in pilot mode, including an empty catalogue |
| Import form | `dbfc960` introduced the selector/file form | `dbfc960` also returned 403 on GET without resolved authority | `import_blueprint_entry_page` | GET is setup-only and returns the canonical form in pilot mode |
| Package receipt/inspection | `dbfc960` introduced registry receipt and validator inspection | `dbfc960` blocked POST before receipt when identity/workspace/permission was unresolved | `upload_and_validate_blueprint` | `FLORA_ENVIRONMENT=pilot` uses an explicit non-human pilot actor and reaches receipt/inspection |
| Candidate-only import | `dbfc960` staged candidates separately from promotion | No removal found; overlapping pilot access patches obscured the boundary | validator, candidate repositories and promotion service | Upload leaves canonical memory unchanged; promotion still requires normal authority |

The first complete pilot-mode repository journey is `65dcf40`. The canonical
single-mode cleanup is `f7c53b4`. No later repository commit between `f7c53b4`
and pre-change HEAD `036faa469ce97a4ca0efd445c434d725bc54f195` removes that
journey. Consequently, the exact production regression commit cannot be named
until the deployed SHA is recorded.

## Previous and corrected behaviour

Previously, an authorised user saw **Import Blueprint** among an existing-Twin
landing experience. The import page itself was titled **Import governed package**.
Neither label expressed that this was the route for creating a new Twin candidate.

The Digital Twins landing page now presents an authorised user with a primary
**Import Twin** action, including when no governed Twin exists. The existing route
and form now identify themselves as **Import Twin** and explicitly state that no
existing Twin selection or Commercial Mission is required. A successful upload
continues to redirect to `/blueprint-import/{import_run_id}`, the Executive
Intelligence Workspace for the candidate.

## Existing functionality preserved

This change does not introduce another importer. It continues to use the existing
Blueprint package registry, archive handling, validator, candidate staging,
lineage, evidence, review, identity/scope resolution, restaging and promotion
services. Semantic Twin assembly and Commercial Mission composition are unchanged.
The Executive Intelligence Workspace now also gives an explicit **View package
validation** link alongside candidate governance, scope resolution and import
decision inspection.

## Deployment considerations

No data migration is required. Render must use `FLORA_ENVIRONMENT=pilot`,
`FLORA_TRUST_PROXY_HEADERS=0`, and a writable persistent `FLORA_DATA_DIR`.
Deprecated import overlays `FLORA_PILOT_IMPORT_BYPASS` and
`FLORA_PILOT_AUTO_SIGN_IN` must be absent or false. A process restart/redeploy is
required after environment changes. `/health` is the liveness route and
`/deployment` reports the revision, application module, pilot-mode status,
canonical route owner and implementation version. The same safe fingerprint is
embedded as an HTML comment on both import entry pages.

## Regression coverage

Automated coverage verifies authorised navigation visibility, denied-user
visibility, route/form availability, ZIP upload initiation, candidate creation
with unresolved identity/scope/evidence, missing Commercial Mission behaviour,
the Executive Workspace redirect, governance and package-validation links, and
continued visibility of the action after an unreadable package error. Existing
Digital Twins, import interface and Executive Workspace suites continue to cover
previously imported Twins and the established validation/promotion lifecycle.

## Lessons learned and merge gate

- A working import capability was lost from the usable vertical journey even
  though individual importer services remained.
- Partial presenter/UI tests did not protect navigation, multipart receipt,
  inspection and candidate staging through the configured HTTP entry point.
- Route ownership was not proven before route-boundary injection was attempted.
- Deployment identity was not verified against the merged revision.
- Secret sign-in, auto-sign-in, route injection and bypass patches created
  ambiguous security ownership.
- PR completion was judged from implementation rather than deployed outcome.
- The entry-point HTTP integration test now protects the complete candidate
  journey, and the deployment fingerprint plus human checklist make matching SHA
  and browser proof mandatory before production acceptance.

## Human deployment verification gate

1. Merge the PR.
2. Confirm Render deploys the merged commit and record the deployed SHA.
3. Confirm `FLORA_ENVIRONMENT=pilot` and deprecated overlays are absent.
4. Open `/deployment` and match its SHA, module, mode and route owner.
5. Open `/digital-twins` and confirm **Import Twin** appears once.
6. Open `/blueprint-import` and confirm Twin type and file selection.
7. Upload the TMS-001 ZIP and retain the resulting diagnostics.
8. Confirm package receipt and inspection audit events.
9. Confirm candidate creation and no automatic promotion.
10. Record the result in the PR or this programme-state record.

Production verification remains pending until this checklist is completed by an
operator with Render and browser access.
