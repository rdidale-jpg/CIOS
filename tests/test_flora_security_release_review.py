"""Independent adversarial review probes. Synthetic data; no authority mocks.

These assertions describe required safe behaviour. A failure is review evidence,
not an expected-failure marker or permission to suppress the assertion.
"""
from dataclasses import replace
from html.parser import HTMLParser
import json
from pathlib import Path
import sqlite3
import time

import pytest
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_security_owner_journey import browser,authenticate
from tests.test_flora_security_workspace_boundary import resource,hashes
from cios.applications.flora import document_review,security,security_store
from cios.applications.flora.security_store import COOKIE
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository

pytestmark=pytest.mark.real_security_boundary


def observe(tmp_path, **facts):
    # Only non-secret facts and synthetic markers; never record bearer values.
    (tmp_path/'review-observation.json').write_text(json.dumps(facts,indent=2)+'\n')


@pytest.mark.parametrize('boundary',['denied-resource-acl','conflicting-document-scope'])
def test_financial_get_rejects_acl_denial_and_scope_conflict(authority,tmp_path,browser,boundary):
    store=authority[0];authenticate(authority,tmp_path,browser)
    run,record=resource(store)
    run['document']={'enterprise_id':'synthetic-enterprise','workspace_id':'synthetic-workspace'}
    run['claims']=[{'claim_id':'synthetic-private-claim','original_statement':'REVIEW_PRIVATE_FINANCIAL_MARKER',
        'amended_statement':'REVIEW_PRIVATE_FINANCIAL_MARKER','claim_type':'fact','page_reference':1,
        'source_excerpt':'Synthetic private excerpt','confidence':80,'review_state':'pending'}]
    if boundary=='denied-resource-acl':
        EnterpriseCanvasAccessRepository().save(replace(record,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    else:
        run['document']['workspace_id']='other-workspace'
    document_review._write_json(document_review._run_path('fi-synthetic'),run)
    before=hashes(store.path.parent.parent)
    status,_,body=browser.request('GET','/ai-financial-report/fi-synthetic')
    observe(tmp_path,boundary=boundary,http_status=status,private_marker_disclosed='REVIEW_PRIVATE_FINANCIAL_MARKER' in body,
        files_unchanged=hashes(store.path.parent.parent)==before)
    assert status==403 and 'REVIEW_PRIVATE_FINANCIAL_MARKER' not in body


class Forms(HTMLParser):
    def __init__(self):super().__init__();self.current=None;self.forms=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='form':self.current={'action':attrs.get('action'),'fields':{},'text':''}
        if self.current is not None and tag=='input' and attrs.get('name'):
            self.current['fields'][attrs['name']]=attrs.get('value','')
    def handle_data(self,data):
        if self.current is not None:self.current['text']+=data
    def handle_endtag(self,tag):
        if tag=='form' and self.current is not None:self.forms.append(self.current);self.current=None


def test_visible_home_sign_out_revokes_the_actual_session(authority,tmp_path,browser):
    authenticate(authority,tmp_path,browser)
    original=browser.cookies[COOKIE]
    status,_,body=browser.request('GET','/flora');assert status==200
    forms=Forms();forms.feed(body)
    signout=next(f for f in forms.forms if 'Sign out' in f['text'])
    status,_,_=browser.request('POST',signout['action'],signout['fields'])
    live=security.verified_context({'Cookie':COOKIE+'='+original}) is not None
    observe(tmp_path,rendered_action=signout['action'],http_status=status,session_still_live=live)
    assert status==303 and not live


def test_authority_commit_failure_does_not_leave_protected_write(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path)
    resource(store)
    path=document_review._run_path('fi-synthetic');before=path.read_bytes()
    original_connect=sqlite3.connect
    class FailingFinalCommit(sqlite3.Connection):
        def commit(self):
            count=self.execute("SELECT COUNT(*) FROM audit WHERE event='service_authorized'").fetchone()[0]
            if count:
                raise sqlite3.OperationalError('synthetic final authority commit failure')
            return super().commit()
    def connect(*args,**kwargs):
        kwargs['factory']=FailingFinalCommit
        return original_connect(*args,**kwargs)
    monkeypatch.setattr(security_store.sqlite3,'connect',connect)
    with pytest.raises(sqlite3.OperationalError,match='synthetic final authority commit failure'):
        document_review.update_reviews('fi-synthetic',{},headers=headers)
    with store.transaction() as db:
        persisted_audits=db.execute("SELECT COUNT(*) FROM audit WHERE event='service_authorized'").fetchone()[0]
    changed=path.read_bytes()!=before
    observe(tmp_path,protected_write_survived_rejection=changed,persisted_service_audits=persisted_audits,
        run_status=json.loads(path.read_text())['status'])
    assert path.read_bytes()==before


def test_successful_private_reads_refresh_idle_activity(authority,tmp_path,browser,monkeypatch):
    authenticate(authority,tmp_path,browser)
    base=time.time()
    monkeypatch.setattr(security_store.time,'time',lambda:base+25*60)
    first=browser.request('GET','/settings/general')[0]
    assert first==200
    monkeypatch.setattr(security_store.time,'time',lambda:base+40*60)
    second=browser.request('GET','/settings/general')[0]
    observe(tmp_path,first_read_at_minutes=25,first_status=first,second_read_at_minutes=40,second_status=second,
        gap_since_last_successful_activity_minutes=15)
    assert second==200
