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

No data migration, storage change, new environment variable or feature flag is
required. Deploy the web application normally. Existing package archives,
candidates and promoted Twins remain in their current stores. Verify with an
authorised `package.upload` user that Digital Twins shows **Import Twin**, then
upload TMS-001 and confirm the resulting candidate opens in the Executive
Intelligence Workspace. Promotion remains a separate governed action.

## Regression coverage

Automated coverage verifies authorised navigation visibility, denied-user
visibility, route/form availability, ZIP upload initiation, candidate creation
with unresolved identity/scope/evidence, missing Commercial Mission behaviour,
the Executive Workspace redirect, governance and package-validation links, and
continued visibility of the action after an unreadable package error. Existing
Digital Twins, import interface and Executive Workspace suites continue to cover
previously imported Twins and the established validation/promotion lifecycle.

## Recommendation

**Merge** after deployment verification confirms that an authorised user can
select the supplied TMS-001 ZIP through the visible **Import Twin** action, create
the candidate and reach its Executive Intelligence Workspace while retaining the
candidate review and promotion-governance paths.
