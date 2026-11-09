"""Opt-in service-test provider. Never production authentication or HTTP proof.

Dictionary arguments here are in-process test fixture specifications. Production
security tests never install this double. No sign-in/membership/CSRF is simulated
as production acceptance by these legacy domain tests.
"""
from types import SimpleNamespace

def fixture_context(spec):
    if type(spec) is not dict:return None
    user=str(spec.get('X-Flora-User') or '')
    if not user:return None
    enterprises={s.strip() for s in str(spec.get('X-Flora-Enterprises') or '').replace('|',',').split(',') if s.strip()}
    selected=str(spec.get('X-Flora-Active-Workspace') or '')
    concrete=sorted(enterprises-{'*'})
    if not selected and len(concrete)==1:selected=concrete[0]
    if selected and '*' not in enterprises and selected.casefold() not in {e.casefold() for e in enterprises}:selected=''
    roles={s.strip() for s in str(spec.get('X-Flora-Roles') or '').replace('|',',').split(',') if s.strip()}
    # Explicit test-only membership/session projections for the 01B interface.
    # No cookie/token is issued, and production never imports this provider.
    from datetime import datetime,timedelta,timezone
    from cios.applications.flora.access import BLUEPRINT_IMPORT_OWNER_PERMISSIONS,CANONICAL_OWNER_ROLES
    now=datetime.now(timezone.utc)
    capabilities=roles-set(CANONICAL_OWNER_ROLES)
    if roles & CANONICAL_OWNER_ROLES and selected:
        capabilities |= set(BLUEPRINT_IMPORT_OWNER_PERMISSIONS)|{'commercial_context.view','commercial_context.edit'}
    if 'blueprint_import_admin' in roles:capabilities |= set(BLUEPRINT_IMPORT_OWNER_PERMISSIONS)
    membership=SimpleNamespace(membership_id='synthetic-membership',user_id=user,workspace_id=selected,
        roles=frozenset(roles),active=bool(selected),version=1,checked_at=now) if selected else None
    session=SimpleNamespace(session_ref='synthetic-session-reference',authenticated_at=now,
        expires_at=now+timedelta(hours=8),idle_expires_at=now+timedelta(minutes=30),
        reauthenticated_at=now,revoked=False,revocation_version=1,checked_at=now)
    return SimpleNamespace(user_id=user,workspace=selected,enterprise_ids=frozenset(enterprises),
        workspace_ids=frozenset({selected}) if selected else frozenset(),membership=membership,
        roles=frozenset(roles),effective_capabilities=frozenset(capabilities),session=session,
        verified_human=True,authentication_source='synthetic-service-fixture')

def prepare_review(*args,**kwargs):
    """Explicit mutation setup; same helper runs on pinned main and repaired code."""
    from cios.applications.flora.blueprint_import import views
    return getattr(views,'prepare_review',views.review_page)(*args,**kwargs)


def generate_brief(runtime, request):
    import inspect
    if 'headers' not in inspect.signature(runtime.generate).parameters:
        return runtime.generate(request)
    return runtime.generate(request, headers={
        'X-Flora-User':request.requested_by, 'X-Flora-Active-Workspace':request.workspace_id,
        'X-Flora-Enterprises':request.enterprise_id+','+request.workspace_id,
        'X-Flora-Roles':'package.review'})


def existing_resource_acl(*, enterprise_id, workspace_id, principal_id):
    """Explicit positive-test setup for a pre-approved exact resource ACL.

    Call only from a scenario that already declares this principal's membership
    and resource scope. Never invoked by authentication or permission evaluation;
    negative missing-ACL tests do not use this helper.
    """
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository
    record=EnterpriseCanvasAccessRecord('1.0','canvas-'+enterprise_id,enterprise_id,workspace_id,principal_id,
        acl=({'principal_id':principal_id,'role':'owner','grant_source':'explicit-test-binding'},))
    return EnterpriseCanvasAccessRepository().save(record)
