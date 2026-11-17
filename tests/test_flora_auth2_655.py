"""Isolated provider contracts + real CIOS authority, never live Supabase proof."""
from copy import deepcopy
import base64
import json
import time

from cryptography.fernet import Fernet
import pytest

from cios.applications.flora import security, security_store as ss, supabase_identity as identity
from cios.applications.flora.financial_intelligence import candidate_analytics as financial
from cios.applications.flora import visual_streams as visual, document_review as review
from tests.test_flora_security_repair_01b import authority, signed, PASSWORD
from tests.test_flora_f1_642 import permitted
from tests.test_flora_uxr1_650 import retained, main

pytestmark = pytest.mark.real_security_boundary
SUBJECT = '00000000-0000-4000-8000-000000000001'
SESSION = '00000000-0000-4000-8000-000000000002'
URL = 'https://' + 'a'*20 + '.supabase.co'
EMAIL = 'isolated@example.invalid'
HTTP_REQUEST = identity.Provider.request


def jwt(claims):
    return 'eyJhbGciOiJSUzI1NiJ9.' + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=') + '.TEST-SIGNATURE'


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv('FLORA_AUTH_PROVIDER', 'supabase')
    monkeypatch.setenv('FLORA_SUPABASE_URL', URL)
    monkeypatch.setenv('FLORA_SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_' + 'x'*32)
    monkeypatch.setenv('FLORA_SUPABASE_SESSION_KEY', Fernet.generate_key().decode())
    claims = {'iss': URL+'/auth/v1', 'sub': SUBJECT, 'aud': 'authenticated', 'exp': int(time.time())+3600,
              'iat': int(time.time()), 'session_id': SESSION, 'is_anonymous': False, 'role': 'authenticated'}
    state = {'claims': claims, 'user': {'id': SUBJECT, 'is_anonymous': False, 'email_confirmed_at': '2026-11-17T00:00:00Z'},
             'offline': False, 'revoked': False, 'calls': []}
    def request(self, method, path, *, token='', body=None):
        state['calls'].append((method, path))
        if state['offline'] or state['revoked']:
            raise PermissionError('Sign-in unavailable')
        if path.startswith('/token'):
            if body != {'email': EMAIL, 'password': PASSWORD}:
                raise PermissionError('Sign-in unavailable')
            state['access'] = jwt(state['claims'])
            return {'access_token': state['access'], 'refresh_token': 'DISCARD-THIS-TEST-SECRET'}
        if path == '/user':
            if token != state.get('access', jwt(state['claims'])):
                raise PermissionError('Sign-in unavailable')
            return deepcopy(state['user'])
        if path == '/logout?scope=local':
            state['revoked'] = True
            return {}
        raise AssertionError('Unexpected provider call')
    monkeypatch.setattr(identity.Provider, 'request', request)
    return state


def bind(store, **changes):
    proposal = dict(issuer=URL+'/auth/v1', subject=SUBJECT, user_id='synthetic-human',
                    operator='isolated-reviewer', approval_reference='ISOLATED-APPROVAL', active=True)
    proposal.update(changes)
    identity.bind_offline(store, proposal, ss.digest(ss.canonical(proposal)))
    return proposal


def login(store):
    pre, csrf = store.preauth()
    token, csrf = store.login(EMAIL, PASSWORD, pre, csrf)
    return store.select(token, csrf, 'synthetic-workspace')


def test_verified_provider_identity_preserves_existing_membership_and_cookie(authority, provider):
    store=authority[0];bind(store);token,csrf=login(store)
    context=store.resolve(token)
    assert context.user_id=='synthetic-human' and context.authentication_source=='supabase_get_user'
    assert context.workspace=='synthetic-workspace' and 'candidate.promote'in context.effective_capabilities
    assert context.session.expires_at.timestamp() <= provider['claims']['exp']
    assert 'Secure; HttpOnly; SameSite=Strict'in ss.session_cookie(token)
    assert 'supabase'not in ss.session_cookie(token) and provider['access']not in ss.session_cookie(token)
    raw=store.path.read_bytes()
    for secret in (PASSWORD,provider['access'],'DISCARD-THIS-TEST-SECRET'):
        assert secret.encode()not in raw
    with store.transaction()as db:
        assert db.execute('SELECT password FROM principals').fetchone()[0] is None
        audit=' '.join(r[0]for r in db.execute('SELECT payload FROM audit'))
        assert EMAIL not in audit and provider['access'] not in audit


@pytest.mark.parametrize('change', ['issuer','subject','audience','expiry','future-iat','anonymous','session-id','signature','user-id','unconfirmed','remote-anonymous','banned','outage','revoked'])
def test_provider_claim_and_remote_identity_boundaries(authority,provider,change):
    store=authority[0];bind(store)
    if change=='issuer':provider['claims']['iss']='https://foreign.supabase.co/auth/v1'
    if change=='subject':provider['claims']['sub']='not-a-uuid'
    if change=='audience':provider['claims']['aud']='service_role'
    if change=='expiry':provider['claims']['exp']=0
    if change=='future-iat':provider['claims']['iat']=int(time.time())+1000
    if change=='anonymous':provider['claims']['is_anonymous']=True
    if change=='session-id':provider['claims']['session_id']='bad'
    if change=='signature':provider['revoked']=True  # Network rejects token, no decoded-claim authority.
    if change=='user-id':provider['user']['id']=SESSION
    if change=='unconfirmed':provider['user']['email_confirmed_at']=None
    if change=='remote-anonymous':provider['user']['is_anonymous']=True
    if change=='banned':provider['user']['banned_until']='2999-01-01T00:00:00Z'
    if change in {'outage','revoked'}:provider[change if change=='revoked'else'offline']=True
    pre,csrf=store.preauth()
    with pytest.raises(PermissionError):store.login(EMAIL,PASSWORD,pre,csrf)
    with store.transaction()as db:assert db.execute("SELECT count(*) FROM tokens WHERE kind='session'").fetchone()[0]==0


@pytest.mark.parametrize('change',['unmapped','email-role','wrong-issuer','wrong-principal','inactive'])
def test_no_implicit_binding_or_roles(authority,provider,change):
    store=authority[0]
    if change=='inactive':bind(store,active=False)
    if change=='email-role':provider['user'].update(email='owner@example.invalid',app_metadata={'role':'cios_owner','workspace':'synthetic-workspace'})
    if change=='wrong-issuer':
        with pytest.raises(ValueError):bind(store,issuer='https://foreign.supabase.co/auth/v1')
    if change=='wrong-principal':
        with pytest.raises(PermissionError):bind(store,user_id='new-owner')
    pre,csrf=store.preauth()
    with pytest.raises(PermissionError):store.login(EMAIL,PASSWORD,pre,csrf)


@pytest.mark.parametrize('change',['disabled','membership','version','binding','encryption-key','sealed','legacy-mode','bad-mode','provider-outage','provider-revoked','expiry','idle'])
def test_active_sessions_recheck_current_authority_and_provider(authority,provider,monkeypatch,change):
    store=authority[0];bind(store);token,csrf=login(store)
    with store.transaction()as db:
        if change=='disabled':db.execute('UPDATE principals SET enabled=0')
        if change=='membership':db.execute('UPDATE memberships SET active=0')
        if change=='version':db.execute('UPDATE principals SET version=version+1')
        if change=='binding':db.execute("DELETE FROM meta WHERE key LIKE 'supabase:binding:%'")
        if change=='sealed':db.execute('UPDATE meta SET value=? WHERE key=?',(json.dumps({'subject':SUBJECT,'sealed':'bad'}),identity.credential_key(ss.digest(token))))
        if change=='expiry':db.execute('UPDATE tokens SET expires=0')
        if change=='idle':db.execute('UPDATE tokens SET touched=0')
    if change=='encryption-key':monkeypatch.setenv('FLORA_SUPABASE_SESSION_KEY',Fernet.generate_key().decode())
    if change in {'legacy-mode','bad-mode'}:monkeypatch.setenv('FLORA_AUTH_PROVIDER','local'if change=='legacy-mode'else'invalid')
    if change=='provider-outage':provider['offline']=True
    if change=='provider-revoked':provider['revoked']=True
    assert security.verified_context({'Cookie':ss.COOKIE+'='+token}) is None


def test_workspace_rotation_preserves_age_rechecks_and_reseals(authority,provider):
    store=authority[0];bind(store);token,csrf=login(store);context=store.resolve(token)
    old=token;token,csrf=store.select(token,csrf,'synthetic-workspace');after=store.resolve(token)
    assert after.session.authenticated_at==context.session.authenticated_at and after.session.expires_at==context.session.expires_at
    with pytest.raises(PermissionError):store.resolve(old)
    before=len(provider['calls'])
    with store.transaction():store.resolve(token);store.resolve(token)
    assert len(provider['calls'])==before+1
    store.resolve(token);assert len(provider['calls'])==before+2


def test_csrf_wrong_workspace_and_local_logout_during_outage(authority,provider):
    store=authority[0];bind(store);token,csrf=login(store)
    with pytest.raises(PermissionError):store.select(token,csrf,'foreign-workspace')
    with pytest.raises(PermissionError):store.select(token,'wrong','synthetic-workspace')
    with pytest.raises(PermissionError):store.logout(token,'wrong')
    provider['offline']=True;store.logout(token,csrf)
    with store.transaction()as db:assert db.execute('SELECT revoked FROM tokens WHERE hash=?',(ss.digest(token),)).fetchone()[0]==1
    provider['offline']=False
    with pytest.raises(PermissionError):store.resolve(token)


def test_binding_approval_no_reassignment_and_revocation(authority,provider):
    store=authority[0];proposal=bind(store);token,csrf=login(store)
    with pytest.raises(PermissionError):bind(store,subject=SESSION)
    with pytest.raises(ValueError):identity.bind_offline(store,proposal,'wrong-digest')
    bind(store,active=False)
    with pytest.raises(PermissionError):store.resolve(token)
    with pytest.raises(PermissionError):identity.bind_offline(store,proposal,ss.digest(ss.canonical(proposal)))
    with store.transaction()as db:
        assert db.execute('SELECT count(*) FROM principals').fetchone()[0]==1
        assert db.execute('SELECT count(*) FROM memberships').fetchone()[0]==1


def test_decoded_claims_with_forged_signature_never_supply_identity(provider):
    claims=jwt(provider['claims'])
    forged=claims.rsplit('.',1)[0]+'.FORGED-SIGNATURE'
    with pytest.raises(PermissionError):identity.Provider.configured().verify(forged)
    assert provider['calls']==[('GET','/user')]


def test_supabase_mode_denies_legacy_password_sessions_and_enrollment(authority,tmp_path,monkeypatch):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    monkeypatch.setenv('FLORA_AUTH_PROVIDER','supabase')
    assert security.verified_context(headers)is None
    with pytest.raises(PermissionError):store.enroll('bad',PASSWORD,'bad','bad')
    pre,csrf=store.preauth()
    with pytest.raises(PermissionError):store.login('synthetic-human',PASSWORD,pre,csrf)


@pytest.mark.parametrize('key,value',[
    ('FLORA_SUPABASE_URL','http://'+ 'a'*20+'.supabase.co'),('FLORA_SUPABASE_URL',URL+'/'),
    ('FLORA_SUPABASE_URL','https://localhost'),('FLORA_SUPABASE_URL',URL+'@evil.invalid'),
    ('FLORA_SUPABASE_PUBLISHABLE_KEY','service_role_secret'),('FLORA_SUPABASE_PUBLISHABLE_KEY',''),
    ('FLORA_SUPABASE_SESSION_KEY',''),('FLORA_SUPABASE_SESSION_KEY','bad')])
def test_misconfiguration_fails_closed(provider,monkeypatch,key,value):
    monkeypatch.setenv(key,value)
    with pytest.raises(PermissionError):identity.Provider.configured()


def test_missing_store_is_never_created(provider,tmp_path):
    store=ss.SecurityStore(tmp_path/'missing'/'authority.sqlite3')
    with pytest.raises(OSError):store.preauth()
    with pytest.raises(OSError):bind(store)
    assert not store.path.parent.exists()


def test_private_financial_service_uses_unchanged_workspace_and_acl(permitted,provider):
    store,_,acl=permitted;bind(store);token,csrf=login(store);headers={'Cookie':ss.COOKIE+'='+token}
    run=financial.create_run('nationwide-fy2026',headers=headers)
    assert len(financial.read_analysis(run,headers=headers)['measurements'])==8
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    EnterpriseCanvasAccessRepository().path.unlink()
    with pytest.raises(PermissionError):financial.read_analysis(run,headers=headers)
    assert len(financial.public_nationwide_projection()['measurements'])==8


def test_public_projection_never_reads_private_store_runs_or_provider(monkeypatch,tmp_path):
    def forbidden(*a,**kw):raise AssertionError('Public facts must not read private state')
    monkeypatch.setenv('FLORA_AUTH_PROVIDER','supabase')
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path/'absent'))
    monkeypatch.setattr(ss.SecurityStore,'transaction',forbidden)
    monkeypatch.setattr(review,'load_run',forbidden)
    monkeypatch.setattr(financial,'find_existing_run',forbidden)
    monkeypatch.setattr(identity.Provider,'request',forbidden)
    html=visual.render('/industries/banking',{'selected':['nationwide']},{})
    assert '£2.026bn'in main(html) and '£1.49bn'in main(html) and '100,886'in main(html)
    assert 'Guest'in html and 'FY2026'in html and '<details'not in main(html)
    assert not(tmp_path/'absent').exists()


@pytest.mark.parametrize('flag',['withdrawn','revoked','owner_only','contradiction','superseded','stale'])
def test_public_source_revocation_and_restriction_flags(retained,flag):
    assert financial.public_nationwide_projection()
    data=json.loads(retained.read_text());data['sources'][1][flag]=True;retained.write_text(json.dumps(data))
    assert not financial.public_nationwide_projection()
    assert '£2.026bn'not in main(visual.render('/industries/banking',{'selected':['nationwide']}))


def test_public_outage_with_existing_cookie_has_no_repeated_provider_wait(authority,provider):
    store=authority[0];bind(store);token,csrf=login(store);provider['offline']=True
    before=len(provider['calls'])
    html=visual.render('/industries/banking',{'selected':['nationwide']},{'Cookie':ss.COOKIE+'='+token})
    assert '£2.026bn'in main(html) and 'Guest'in html
    assert len(provider['calls'])==before+1
    provider['offline']=False
    assert store.resolve(token).verified_human  # No cross-request negative cache.


def test_expired_provider_ban_does_not_block_verified_individual(authority,provider):
    provider['user']['banned_until']='2020-01-01T00:00:00Z'
    store=authority[0];bind(store);token,csrf=login(store)
    assert store.resolve(token).verified_human


@pytest.mark.parametrize('fault',['binding-list','sealed-list','wrong-session','wrong-subject','wrong-issuer'])
def test_corrupt_or_transplanted_provider_envelopes_deny(authority,provider,fault):
    store=authority[0];bind(store);token,csrf=login(store)
    with store.transaction()as db:
        if fault=='binding-list':db.execute('UPDATE meta SET value=? WHERE key=?',('[]',identity.binding_key(URL+'/auth/v1',SUBJECT)))
        else:
            ref=ss.digest(token);entry=json.loads(db.execute('SELECT value FROM meta WHERE key=?',(identity.credential_key(ref),)).fetchone()[0])
            p=identity.Provider.configured()
            payload={'issuer':p.issuer,'subject':SUBJECT,'session':ref,'access':provider['access']}
            if fault=='sealed-list':payload=[]
            if fault=='wrong-session':payload['session']='other-session'
            if fault=='wrong-subject':payload['subject']=SESSION
            if fault=='wrong-issuer':payload['issuer']='https://foreign.invalid/auth/v1'
            entry['sealed']=p.cipher.encrypt(json.dumps(payload).encode()).decode()
            db.execute('UPDATE meta SET value=? WHERE key=?',(json.dumps(entry),identity.credential_key(ref)))
    assert security.verified_context({'Cookie':ss.COOKIE+'='+token})is None


@pytest.mark.parametrize('fault',['oversize','non-object','invalid-json','redirect','timeout','valid'])
def test_real_transport_contract_is_bounded_verified_https_no_redirect(provider,monkeypatch,fault):
    import io
    from urllib.error import HTTPError,URLError
    calls=[]
    class Response:
        status=200
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,maximum):
            assert maximum==65537
            return b'x'*65537 if fault=='oversize' else b'[]'if fault=='non-object'else b'{'if fault=='invalid-json'else b'{"id":"bounded"}'
    class Opener:
        def open(self,request,timeout):
            calls.append(request)
            assert timeout==5 and request.full_url==URL+'/auth/v1/user'
            assert request.headers['Authorization']=='Bearer TEST-NOT-A-REAL-TOKEN'
            if fault=='redirect':raise HTTPError(request.full_url,302,'redirect',{},io.BytesIO(b'PRIVATE-REMOTE-ERROR'))
            if fault=='timeout':raise URLError('PRIVATE-CONNECTION-ERROR')
            return Response()
    def opener(handler):
        assert handler is identity.NoRedirect
        handler=handler()
        assert handler.redirect_request(None,None,None,None,None,None)is None
        return Opener()
    monkeypatch.setattr(identity,'build_opener',opener)
    p=identity.Provider.configured()
    if fault=='valid':assert HTTP_REQUEST(p,'GET','/user',token='TEST-NOT-A-REAL-TOKEN')=={'id':'bounded'}
    else:
        with pytest.raises(PermissionError,match='^Sign-in unavailable$'):HTTP_REQUEST(p,'GET','/user',token='TEST-NOT-A-REAL-TOKEN')
    assert len(calls)==1
