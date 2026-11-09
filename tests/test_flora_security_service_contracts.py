"""Domain-boundary contracts under an explicit fixture identity provider.

These are not authentication acceptance tests. Production HTTP remains closed.
"""
import os
from hashlib import sha256
from pathlib import Path
import pytest
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.validator import BlueprintPackageValidator
from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
from cios.applications.flora.blueprint_import.views import review_page

pytestmark = pytest.mark.usefixtures('verified_flora_test_authority')
H={'X-Flora-User':'alice','X-Flora-Enterprises':'*','X-Flora-Active-Workspace':'workspace-a','X-Flora-Roles':'blueprint_import_admin'}

@pytest.fixture
def candidate(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    p=BlueprintPackageRegistry().receive(pkg(),'fixture.zip','alice','workspace-a')
    BlueprintPackageValidator().validate_and_stage(p.package_ref,'alice',H)
    return p

def fingerprint():
    root=Path(os.environ['FLORA_DATA_DIR'])
    return {str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def test_review_get_does_not_prepare_or_write(candidate,monkeypatch):
    before=fingerprint()
    def forbidden(*a,**kw):pytest.fail('GET attempted review preparation')
    monkeypatch.setattr(BlueprintReviewPlanCoordinator,'ensure_job',forbidden)
    html,status=review_page(candidate.import_run_id,H)
    assert status==200 and fingerprint()==before


def test_review_get_without_job_preserves_existing_records(candidate):
    before=fingerprint()
    html,status=review_page(candidate.import_run_id,H)
    assert status==200 and 'Review preparation required' in html
    assert fingerprint()==before


def test_verified_fixture_wildcard_cannot_cross_resource_workspace(candidate):
    from cios.applications.flora.access import can_access_enterprise
    from cios.applications.flora.blueprint_import.views import history_page
    wrong=H|{'X-Flora-Active-Workspace':'workspace-b'}
    assert not can_access_enterprise(wrong,candidate.identity.enterprise_id,candidate.workspace_id)
    html,status=history_page(wrong)
    assert status==200 and candidate.import_run_id not in html


def test_membership_is_not_inferred_from_enterprise_wildcard(monkeypatch):
    from tests.flora_security_fixtures import fixture_context
    from cios.applications.flora import access
    context=fixture_context(H)
    context.membership=None
    context.workspace_ids=frozenset()
    monkeypatch.setattr(access,'verified_context',lambda *_:context)
    assert access.blueprint_upload_authorisation(H).resolved_membership=='unresolved'
    assert access.blueprint_upload_authorisation(H).decision=='denied'


def test_effective_capability_snapshot_bounds_existing_policy(monkeypatch):
    from tests.flora_security_fixtures import fixture_context
    from cios.applications.flora import access,security
    context=fixture_context(H)
    context.effective_capabilities=frozenset()
    monkeypatch.setattr(access,'verified_context',lambda *_:context)
    monkeypatch.setattr(security,'verified_context',lambda *_:context)
    with pytest.raises(PermissionError):access.require_capability(H,'package.review')
