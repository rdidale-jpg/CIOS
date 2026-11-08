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
    return SimpleNamespace(user_id=user,workspace=selected,enterprise_ids=enterprises,roles=roles)

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
