"""Real producer acceptance: offline approval and synthetic storage only."""
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

import pytest

from cios.applications.flora import security
from cios.applications.flora.security_store import SecurityStore, COOKIE, PREAUTH, digest, canonical, cookie_token, ABSOLUTE, IDLE, RECENT
from cios.applications.flora.security_operator import reconcile, plan, apply
from cios.applications.flora.security_web import CSRF_COOKIE

pytestmark = pytest.mark.real_security_boundary
PASSWORD = 'synthetic private passphrase 47!'

@pytest.fixture
def authority(tmp_path, monkeypatch):
    root=tmp_path/'runtime';root.mkdir()
    monkeypatch.setenv('FLORA_DATA_DIR',str(root))
    monkeypatch.setenv('FLORA_PUBLIC_ORIGIN','https://flora.test')
    snapshot=tmp_path/'snapshot';snapshot.mkdir()
    (snapshot/'records.json').write_text(json.dumps({'actor_id':'synthetic-human','workspace_id':'synthetic-workspace'}))
    evidence=reconcile(snapshot)
    manifest={'approved':True,'operator':'synthetic-deployment-operator','approval_reference':'synthetic-independent-binding-approval',
        'snapshot_digest':digest(canonical(evidence)),'evidence':evidence['files'],
        'bindings':[{'user_id':'synthetic-human','workspace_id':'synthetic-workspace','roles':['cios_owner'],'enterprise_ids':['synthetic-enterprise']}]}
    store=SecurityStore();store.initialize_offline()
    proposed=plan(store,snapshot,manifest)
    receipt=apply(store,snapshot,proposed,proposed['digest'])
    return store,snapshot,manifest,proposed,receipt


def enroll(authority,tmp_path):
    store=authority[0];delivery=tmp_path/('delivery-'+secrets.token_hex(4))
    store.enroll_offline('synthetic-human',delivery)
    enrollment=delivery.read_text().strip()
    pre,csrf=store.preauth();store.enroll(enrollment,PASSWORD,pre,csrf)
    return enrollment


def signed(authority,tmp_path):
    enroll(authority,tmp_path)
    store=authority[0];pre,csrf=store.preauth()
    token,csrf=store.login('synthetic-human',PASSWORD,pre,csrf)
    before=token
    token,csrf=store.select(token,csrf,'synthetic-workspace')
    headers={'Cookie':f'{COOKIE}={token}; {CSRF_COOKIE}={csrf}'}
    return store,token,csrf,headers,before


def test_offline_bootstrap_receipt_idempotency_no_snapshot_changes(authority):
    store,snapshot,manifest,proposed,receipt=authority
    before=reconcile(snapshot)
    assert apply(store,snapshot,proposed,proposed['digest'])==receipt
    assert reconcile(snapshot)==before
    assert store.path.stat().st_mode & 0o777 == 0o600
    assert store.path.parent.stat().st_mode & 0o777 == 0o700
    with store.transaction() as db:
        assert db.execute('SELECT count(*) FROM memberships').fetchone()[0]==1
        assert db.execute("SELECT count(*) FROM audit WHERE event='bootstrap_applied'").fetchone()[0]==1


def test_conflicting_and_stale_bootstrap_rejected(authority):
    store,snapshot,manifest,proposed,_=authority
    second=plan(store,snapshot,manifest)
    with pytest.raises(ValueError): apply(store,snapshot,second,second['digest'])
    (snapshot/'records.json').write_text('{}')
    with pytest.raises(ValueError): apply(store,snapshot,proposed,proposed['digest'])


def test_enrollment_single_use_and_hashes_only(authority,tmp_path):
    token=enroll(authority,tmp_path);store=authority[0]
    pre,csrf=store.preauth()
    with pytest.raises(PermissionError):store.enroll(token,PASSWORD,pre,csrf)
    raw=store.path.read_bytes()
    assert token.encode() not in raw and PASSWORD.encode() not in raw
    with store.transaction() as db:
        encoded=db.execute('SELECT password FROM principals').fetchone()[0]
        assert encoded.startswith('$argon2id$')


def test_owner_sign_in_workspace_rotation_logout(authority,tmp_path):
    store,token,csrf,headers,old=signed(authority,tmp_path)
    assert security.verified_context({'Cookie':f'{COOKIE}={old}'}) is None
    context=security.verified_context(headers)
    assert context.user_id=='synthetic-human'
    assert context.workspace=='synthetic-workspace'
    assert 'candidate.promote' in context.effective_capabilities
    assert context.membership.active
    assert context.session.expires_at.timestamp()-context.session.authenticated_at.timestamp()==pytest.approx(ABSOLUTE)
    store.logout(token,csrf)
    assert security.verified_context(headers) is None


@pytest.mark.parametrize('claim',[
    {'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner'},
    {'Cookie':'flora_pilot_session=unsigned'},
    {'Cookie':'flora_user=synthetic-human; flora_roles=cios_owner'},
    {'user_id':'synthetic-human','roles':['cios_owner']},
    {'Cookie':f'{COOKIE}='+'a'*43},
])
def test_unverified_claims_never_resolve(authority,claim):
    assert security.verified_context(claim) is None


@pytest.mark.parametrize('change',['expired','idle','revoked','disabled','removed','version','tampered','duplicate'])
def test_invalidated_sessions_fail_closed(authority,tmp_path,change):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    with store.transaction() as db:
        if change=='expired':db.execute('UPDATE tokens SET expires=0 WHERE hash=?',(digest(token),))
        if change=='idle':db.execute('UPDATE tokens SET touched=0 WHERE hash=?',(digest(token),))
        if change=='revoked':db.execute('UPDATE tokens SET revoked=1 WHERE hash=?',(digest(token),))
        if change=='disabled':db.execute('UPDATE principals SET enabled=0')
        if change=='removed':db.execute('UPDATE memberships SET active=0')
        if change=='version':db.execute('UPDATE principals SET version=version+1')
    if change=='tampered':headers={'Cookie':f'{COOKIE}='+secrets.token_urlsafe(32)}
    if change=='duplicate':headers={'Cookie':f'{COOKIE}={token}; {COOKIE}={token}'}
    assert security.verified_context(headers) is None


def test_wrong_workspace_and_csrf_rejected(authority,tmp_path):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    with pytest.raises(PermissionError):store.select(token,csrf,'other-workspace')
    with pytest.raises(PermissionError):
        with store.mutation(headers,'forged'):pytest.fail('mutation entered')
    from cios.applications.flora.access import can_access_enterprise,require_capability
    assert not can_access_enterprise(headers,'synthetic-enterprise','other-workspace')
    with pytest.raises(PermissionError):require_capability(headers,'storage.recover')


def test_security_store_failure_and_permissions_deny(authority,tmp_path):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    store.path.chmod(0o644)
    assert security.verified_context(headers) is None
    store.path.chmod(0o600)
    store.path.write_bytes(b'corrupt synthetic store')
    assert security.verified_context(headers) is None


def test_recovery_revokes_sessions_and_rotates_token(authority,tmp_path):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    delivery=tmp_path/'recovery-delivery'
    store.enroll_offline('synthetic-human',delivery)
    assert security.verified_context(headers) is None
    pre,proof=store.preauth();store.enroll(delivery.read_text().strip(),PASSWORD+' new',pre,proof)
    pre,proof=store.preauth()
    with pytest.raises(PermissionError):store.login('synthetic-human',PASSWORD,pre,proof)
    token2,_=store.login('synthetic-human',PASSWORD+' new',pre,proof)
    assert token2!=token


def test_persistent_throttle_survives_restart(authority,tmp_path):
    enroll(authority,tmp_path);store=authority[0];pre,csrf=store.preauth()
    for _ in range(10):
        with pytest.raises(PermissionError):SecurityStore(store.path).login('synthetic-human','wrong',pre,csrf)
    with pytest.raises(PermissionError):SecurityStore(store.path).login('synthetic-human',PASSWORD,pre,csrf)


def test_recent_authentication_required(authority,tmp_path):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    with store.transaction() as db:
        db.execute('UPDATE tokens SET created=? WHERE hash=?',(time.time()-RECENT-1,digest(token)))
    with pytest.raises(PermissionError):
        with store.mutation(headers,csrf,recent=True):pytest.fail('old authentication accepted')


def test_membership_revocation_serializes_with_mutation(authority,tmp_path):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    attempted=threading.Event();finished=threading.Event()
    def revoke():
        attempted.set();SecurityStore(store.path).revoke_offline('synthetic-human','synthetic-workspace');finished.set()
    with store.mutation(headers,csrf):
        t=threading.Thread(target=revoke);t.start();assert attempted.wait(2)
        assert not finished.wait(.1)
        assert security.verified_context(headers)
    t.join(5);assert finished.is_set()
    assert security.verified_context(headers) is None


def test_missing_resource_acl_denied_without_get_grant(authority,tmp_path):
    _,_,_,headers,_=signed(authority,tmp_path)
    from cios.applications.flora.enterprise_canvas.access import can_access_canvas_record
    assert not can_access_canvas_record(headers,'synthetic-enterprise','synthetic-workspace')


def test_financial_mutation_rejects_wrong_workspace(authority,tmp_path,monkeypatch):
    _,_,_,headers,_=signed(authority,tmp_path)
    from cios.applications.flora import document_review
    run={'run_id':'fi-synthetic','enterprise_id':'synthetic-enterprise','workspace_id':'other-workspace','claims':[]}
    writes=[]
    monkeypatch.setattr(document_review,'load_run',lambda _:dict(run))
    monkeypatch.setattr(document_review,'_write_json',lambda *a:writes.append(a))
    with pytest.raises(PermissionError):document_review.update_reviews('fi-synthetic',{},headers=headers)
    assert writes==[]
