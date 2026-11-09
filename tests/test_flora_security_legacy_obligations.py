"""Semantic replacements for retired shared-pilot expectations.

Real synthetic enrollment/session/membership producer. Historical raw tests and
assertions remain unchanged; these tests establish the intended secure contract.
"""
from io import BytesIO
import json
import os
import sqlite3
import subprocess
import sys
import zipfile
from urllib.parse import urlencode

import pytest
from tests.test_flora_security_repair_01b import authority,signed,enroll,PASSWORD
from tests.test_flora_security_owner_journey import browser,authenticate,hidden,multipart
from tests.test_flora_security_workspace_boundary import hashes
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora import security
from cios.applications.flora.security_store import SecurityStore,COOKIE,ABSOLUTE,IDLE,canonical

pytestmark=pytest.mark.real_security_boundary


def test_individual_session_restart_and_cookie_lifetime(authority,tmp_path,browser):
    store=authority[0];authenticate(authority,tmp_path,browser)
    cookies=browser.last_response_cookies
    assert any(c.startswith(COOKIE+'=') and 'Max-Age=28800' in c for c in cookies)
    assert all('Secure' in c and 'HttpOnly' in c and 'SameSite=Strict' in c and 'Domain=' not in c for c in cookies)
    token=browser.cookies[COOKIE]
    script="""import sys,json
from cios.applications.flora.security import verified_context
from cios.applications.flora.security_store import COOKIE
context=verified_context({'Cookie':COOKIE+'='+sys.stdin.read()})
print(json.dumps({'user':context.user_id,'workspace':context.workspace}))
"""
    result=subprocess.run([sys.executable,'-c',script],input=token,text=True,capture_output=True,timeout=20,check=True)
    assert json.loads(result.stdout)=={'user':'synthetic-human','workspace':'synthetic-workspace'}
    context=security.verified_context({'Cookie':COOKIE+'='+token})
    assert context.session.expires_at.timestamp()-context.session.authenticated_at.timestamp()==pytest.approx(ABSOLUTE)
    assert context.session.idle_expires_at.timestamp() <= context.session.checked_at.timestamp()+IDLE


def test_legacy_flags_do_not_replace_verified_identity_or_membership(authority,tmp_path,monkeypatch):
    _,_,_,headers,_=signed(authority,tmp_path)
    before=security.verified_context(headers)
    for key,value in {'FLORA_PILOT_AUTO_SIGN_IN':'1','FLORA_PILOT_IMPORT_BYPASS':'1','FLORA_ENVIRONMENT':'pilot',
                      'FLORA_PILOT_OWNER_ID':'other-human','FLORA_PILOT_WORKSPACE':'other-workspace','FLORA_PILOT_ROLE':'cios_owner','FLORA_TRUST_PROXY_HEADERS':'1'}.items():
        monkeypatch.setenv(key,value)
    after=security.verified_context(headers)
    assert (after.user_id,after.workspace,after.roles)==(before.user_id,before.workspace,before.roles)
    assert security.verified_context({'X-Flora-User':'other-human','X-Flora-Roles':'cios_owner'}) is None
    from cios.applications.flora.pilot_auth import pilot_auto_sign_in_status
    assert pilot_auto_sign_in_status().active is False  # semantic obligation, no wording match


@pytest.mark.parametrize('path',['/auth/sign-in','/pilot-sign-in'])
def test_query_credentials_never_issue_authority(authority,browser,path):
    status,_,body=browser.request('GET',path+'?'+urlencode({'user_id':'synthetic-human','password':PASSWORD,'pilot_secret':PASSWORD}))
    assert status==403
    assert COOKIE not in browser.cookies
    assert PASSWORD not in body


def test_login_audit_failure_rolls_back_session_without_disclosure(authority,tmp_path,browser,monkeypatch):
    store=authority[0];enroll(authority,tmp_path)
    status,_,body=browser.request('GET','/auth/sign-in');assert status==200
    csrf=hidden(body)
    before=hashes(store.path.parent.parent)
    def unavailable(*a,**kw):raise sqlite3.OperationalError('synthetic audit unavailable')
    monkeypatch.setattr(SecurityStore,'audit',unavailable)
    status,_,body=browser.request('POST','/auth/sign-in',{'csrf':csrf,'user_id':'synthetic-human','password':PASSWORD})
    assert status==503 and COOKIE not in browser.cookies
    assert str(store.path) not in body and PASSWORD not in body
    assert hashes(store.path.parent.parent)==before


def test_least_privilege_reviewer_dispositions_do_not_grant_promotion(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    with store.transaction() as db:
        db.execute('UPDATE memberships SET roles=?',(canonical(['package.upload','package.inspect','package.review']),))
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator,CandidateReviewService,DryRunPlanningService
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    content=pkg(records=[{'external_id':'EV-REVIEW','record_class':'evidence','truth_class':'evidence_backed','payload':{'quote':'Synthetic reviewable evidence'}}])
    package=BlueprintPackageRegistry().receive(content,'synthetic-review.zip','synthetic-human','synthetic-workspace')
    BlueprintPackageValidator().validate_and_stage(package.package_ref,'synthetic-human',headers)
    candidate=BlueprintPackageValidator().staging_summary(package.import_run_id)['candidates'][0]
    memory=store.path.parent.parent/'memory'
    before=hashes(memory) if memory.exists() else {}
    for disposition in ('defer','reject','quarantine','unsupported','approve'):
        decision=CandidateReviewService().record_decision(candidate['candidate_record_id'],disposition,'synthetic-human','Explicit synthetic disposition',headers)
        assert decision.reviewer_identity=='synthetic-human' and decision.decision==disposition
    plan=DryRunPlanningService().create_plan(package.import_run_id,'synthetic-human',headers)
    with pytest.raises(PermissionError):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Not permitted',headers)
    assert (hashes(memory) if memory.exists() else {})==before


@pytest.mark.parametrize('kind',['invalid-zip','unsafe-member','bad-extension'])
def test_authenticated_archive_and_form_validation_precede_import_mutation(authority,tmp_path,browser,kind):
    store=authority[0];csrf=authenticate(authority,tmp_path,browser)
    content=b'invalid synthetic ZIP'
    filename='synthetic.zip'
    if kind=='unsafe-member':
        out=BytesIO()
        with zipfile.ZipFile(out,'w') as archive:archive.writestr('../escaped.json','{}')
        content=out.getvalue()
    if kind=='bad-extension':filename='synthetic.txt';content=pkg()
    root=store.path.parent.parent
    def protected():
        return {name:hashes(root/name) if (root/name).exists() else {} for name in ('memory','blueprint_import/packages','blueprint_import/archives','blueprint_import/staging')}
    before=protected()
    raw,content_type=multipart({'csrf':csrf,'expected_type':'enterprise'},filename,content)
    status,_,_=browser.request('POST','/blueprint-import/upload',raw=raw,content_type=content_type)
    assert status in {400,403}
    assert protected()==before
    assert not (root/'escaped.json').exists()


def test_settings_and_diagnostics_show_only_authorised_scope(authority,tmp_path,browser):
    store=authority[0];csrf=authenticate(authority,tmp_path,browser)
    status,_,body=browser.request('GET','/settings/general')
    assert status==200 and 'synthetic-workspace' in body and 'synthetic-human' in body
    assert 'other-workspace' not in body and str(store.path.parent.parent) not in body
    assert browser.cookies[COOKIE] not in body
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry
    content=pkg(records=[{'external_id':'EV-PRIVATE','record_class':'evidence','truth_class':'evidence_backed','payload':{'quote':'OTHER_WORKSPACE_PRIVATE_MARKER'}}])
    private=BlueprintPackageRegistry().receive(content,'other-private.zip','other-human','other-workspace')
    status,_,body=browser.request('GET',f'/blueprint-import/{private.import_run_id}/diagnostics')
    assert status==403 and 'OTHER_WORKSPACE_PRIVATE_MARKER' not in body
    # Anonymous settings remain protected, not a security administration API.
    browser.cookies.clear()
    assert browser.request('GET','/settings/general')[0]==403


@pytest.mark.parametrize('scope',['other-workspace',''])
def test_verified_reviewer_cannot_review_unscoped_or_other_workspace_package(authority,tmp_path,scope):
    store,_,_,headers,_=signed(authority,tmp_path)
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator,CandidateReviewService
    from cios.applications.flora.blueprint_import.review import can_review_blueprint_candidate
    content=pkg(records=[{'external_id':'EV-REVIEW','record_class':'evidence','truth_class':'evidence_backed','payload':{'quote':'Synthetic reviewable evidence'}}])
    package=BlueprintPackageRegistry().receive(content,'synthetic-review.zip','synthetic-human','synthetic-workspace')
    BlueprintPackageValidator().validate_and_stage(package.package_ref,'synthetic-human',headers)
    candidate=BlueprintPackageValidator().staging_summary(package.import_run_id)['candidates'][0]
    path=store.path.parent.parent/'blueprint_import/packages'/f'{package.package_ref}.json'
    persisted=json.loads(path.read_text());persisted['workspace_id']=scope;path.write_text(json.dumps(persisted))
    before=hashes(store.path.parent.parent)
    assert not can_review_blueprint_candidate(headers,'synthetic-enterprise',scope)
    with pytest.raises(PermissionError):
        CandidateReviewService().record_decision(candidate['candidate_record_id'],'approve','synthetic-human','Denied review',headers)
    assert hashes(store.path.parent.parent)==before
