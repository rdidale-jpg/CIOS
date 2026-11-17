"""AUTH-1 actual isolated authority, read-only diagnostics and fail-closed faults."""
from contextlib import contextmanager
from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading

import pytest

from cios.applications.flora import security_store as ss,security_readiness as readiness,protected_storage as protected
from cios.applications.flora.security_operator import main as operator
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_f1_642 import permitted

pytestmark=pytest.mark.real_security_boundary


def snapshot(root):
    return {str(p.relative_to(root)):(sha256(p.read_bytes()).hexdigest(),p.stat().st_mode,p.stat().st_uid)
        for p in root.rglob('*')if p.is_file()and not p.is_symlink()}


@pytest.fixture
def empty(tmp_path,monkeypatch):
    root=tmp_path/'private-root';monkeypatch.setenv('FLORA_DATA_DIR',str(root));monkeypatch.delenv('FLORA_PILOT_DIR',raising=False)
    store=ss.SecurityStore();store.initialize_offline()
    return root,store


def inspect(store,**kwargs):
    return readiness.inspect_security_storage(store,expected_root=store.path.parent.parent,quiesced=True,**kwargs)


@contextmanager
def web():
    from cios.applications.flora.web.app import FloraWebHandler
    class Quiet(FloraWebHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def get(path,headers=None):
        c=HTTPConnection('127.0.0.1',server.server_port)
        try:
            c.request('GET',path,headers=headers or {});r=c.getresponse()
            return r.status,r.read().decode(),dict(r.getheaders())
        finally:c.close()
    try:yield get
    finally:server.shutdown();server.server_close();thread.join(2)


def test_diagnostic_is_read_only_and_never_invokes_mutating_helpers(permitted,monkeypatch):
    store,headers,_=permitted
    from cios.applications.flora.financial_intelligence import candidate_analytics as f
    identity=f.create_run('nationwide-fy2026',headers=headers)
    root=store.path.parent.parent;before=snapshot(root)
    def forbidden(*a,**kw):raise AssertionError('Forbidden write or recovery probe')
    for name in ('transaction','preauth','initialize_offline','audit'):
        monkeypatch.setattr(ss.SecurityStore,name,forbidden)
    monkeypatch.setattr(protected.ProtectedJournal,'recover',forbidden)
    result=inspect(store)
    assert result['assessment']=='read_only_checks_passed' and result['code']=='read_only_checks_passed'
    assert result['counts']['password_configured_principals']==1 and result['counts']['active_memberships']==1
    assert result['counts']['acl']['workspace_bound']==1
    assert all(result[k]=='UNKNOWN'for k in ('writer_readiness','render_persistence','live_authentication','specific_workspace_and_financial_access'))
    assert identity not in json.dumps(result) and snapshot(root)==before


@pytest.mark.parametrize('fault,code',[
    ('root-missing','data_root_missing'),('directory-missing','security_directory_missing'),
    ('database-missing','authority_file_missing'),('directory-mode','private_permissions_invalid'),
    ('database-mode','private_permissions_invalid'),('owner-write-missing','private_permissions_invalid'),
    ('wrong-owner','ownership_mismatch'),('database-symlink','symlink_refused'),
    ('directory-symlink','symlink_refused'),('root-symlink','symlink_refused'),
    ('hardlink','hardlink_refused'),('corrupt','sqlite_corrupt_or_empty')])
def test_operator_distinguishes_filesystem_faults_without_creating_replacements(empty,tmp_path,monkeypatch,fault,code):
    root,store=empty
    if fault=='root-missing':store.path.unlink();store.path.parent.rmdir();root.rmdir()
    elif fault=='directory-missing':store.path.unlink();store.path.parent.rmdir()
    elif fault=='database-missing':store.path.unlink()
    elif fault=='directory-mode':store.path.parent.chmod(0o755)
    elif fault=='database-mode':store.path.chmod(0o644)
    elif fault=='owner-write-missing':store.path.chmod(0o400)
    elif fault=='wrong-owner':
        actual=os.geteuid();monkeypatch.setattr(readiness.os,'geteuid',lambda:actual+1)
    elif fault=='database-symlink':
        target=tmp_path/'preserved';store.path.rename(target);store.path.symlink_to(target)
    elif fault=='directory-symlink':
        target=tmp_path/'preserved-dir';store.path.parent.rename(target);store.path.parent.symlink_to(target,target_is_directory=True)
    elif fault=='root-symlink':
        target=tmp_path/'preserved-root';root.rename(target);root.symlink_to(target,target_is_directory=True)
    elif fault=='hardlink':os.link(store.path,tmp_path/'preserved-link')
    elif fault=='corrupt':store.path.write_bytes(b'PRIVATE-SENTINEL-corruption')
    existed=store.path.exists();before=store.path.read_bytes()if existed else None
    result=inspect(store)
    assert result['assessment']=='blocked' and result['code']==code,result
    assert not result['counts'] and not result['database_created']
    assert (store.path.read_bytes()if store.path.exists()else None)==before
    assert 'PRIVATE-SENTINEL'not in json.dumps(result) and str(tmp_path)not in json.dumps(result)


@pytest.mark.parametrize('fault,code',[
    ('version','schema_metadata_invalid'),('missing-version','schema_metadata_invalid'),
    ('generation','schema_metadata_invalid'),('columns','schema_unrecognised'),
    ('extra-table','schema_unrecognised'),('extra-view','schema_unrecognised'),('roles','membership_metadata_invalid')])
def test_read_only_schema_and_membership_failures_are_sanitized(authority,fault,code):
    store=authority[0]
    with sqlite3.connect(store.path)as db:
        if fault=='version':db.execute("UPDATE meta SET value='999'WHERE key='schema'")
        elif fault=='missing-version':db.execute("DELETE FROM meta WHERE key='schema'")
        elif fault=='generation':db.execute("UPDATE meta SET value='PRIVATE-SENTINEL'WHERE key='generation'")
        elif fault=='columns':db.execute('ALTER TABLE principals ADD COLUMN unexpected TEXT')
        elif fault=='extra-table':db.execute('CREATE TABLE unexpected(value TEXT)')
        elif fault=='extra-view':db.execute('CREATE VIEW unexpected AS SELECT 1')
        elif fault=='roles':db.execute("UPDATE memberships SET roles='PRIVATE-SENTINEL'")
    before=snapshot(store.path.parent.parent);result=inspect(store)
    assert result['code']==code and result['assessment']=='blocked',result
    assert snapshot(store.path.parent.parent)==before and 'PRIVATE-SENTINEL'not in json.dumps(result)


@pytest.mark.parametrize('name',['protected-undo','protected-undo-preparing','protected-complete-interrupted'])
def test_pending_protected_journal_is_not_replayed_or_removed(empty,name):
    root,store=empty;folder=store.path.parent/name;folder.mkdir(mode=0o700)
    (folder/'manifest.json').write_text('PRIVATE-SENTINEL-malformed')
    before=snapshot(root);result=inspect(store)
    assert result['code']=='protected_journal_requires_review' and result['phase']=='protected_journal'
    assert snapshot(root)==before and folder.exists()


@pytest.mark.parametrize('suffix',['-journal','-wal','-shm'])
def test_sqlite_sidecars_are_preserved_without_read_or_recovery(empty,suffix,monkeypatch):
    root,store=empty;sidecar=Path(str(store.path)+suffix);sidecar.write_bytes(b'PRIVATE-SENTINEL');sidecar.chmod(0o600)
    def forbidden(*a,**kw):raise AssertionError('Must not open SQLite with pending sidecars')
    monkeypatch.setattr(readiness.sqlite3,'connect',forbidden)
    before=snapshot(root);result=inspect(store)
    assert result['code']=='sqlite_journal_requires_quiesced_review' and snapshot(root)==before


def test_wal_header_without_sidecar_does_not_create_shared_memory(empty,monkeypatch):
    root,store=empty;raw=bytearray(store.path.read_bytes());raw[18:20]=b'\x02\x02';store.path.write_bytes(raw)
    before=snapshot(root);result=inspect(store)
    assert result['code']=='sqlite_format_requires_quiesced_review' and snapshot(root)==before


def test_exclusive_sqlite_lock_is_observed_without_lock_bypass(empty):
    root,store=empty;before=store.path.read_bytes();db=sqlite3.connect(store.path,isolation_level=None)
    try:
        db.execute('BEGIN EXCLUSIVE');result=inspect(store)
        assert result['code']=='sqlite_locked',result
        assert store.path.read_bytes()==before
    finally:db.rollback();db.close()


@pytest.mark.parametrize('fault',['expected-root','store-root','legacy-env','relative-env','mount'])
def test_configuration_mismatches_fail_before_database_open(empty,tmp_path,monkeypatch,fault):
    root,store=empty;kwargs={'expected_root':root}
    if fault=='expected-root':kwargs['expected_root']=tmp_path/'foreign'
    elif fault=='store-root':store=ss.SecurityStore(tmp_path/'foreign/security/authority.sqlite3')
    elif fault=='legacy-env':monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path/'foreign'))
    elif fault=='relative-env':monkeypatch.setenv('FLORA_DATA_DIR','relative')
    elif fault=='mount':kwargs['expected_mount']=root
    result=readiness.inspect_security_storage(store,**kwargs)
    assert result['assessment']=='blocked'
    assert result['code']in {'data_root_configuration_invalid','data_root_configuration_mismatch','expected_mount_not_observed'}
    assert str(tmp_path)not in json.dumps(result)


def test_empty_store_is_not_reported_as_provisioned_authentication(empty):
    root,store=empty;result=inspect(store)
    assert result['assessment']=='read_only_checks_passed'
    assert result['counts']['principals']==0 and 'account_provisioning_incomplete'in result['warnings']
    assert 'workspace_acl_not_observed'in result['warnings'] and result['live_authentication']=='UNKNOWN'


def test_sql_diagnosis_requires_explicit_operator_quiescence_attestation(empty,monkeypatch):
    root,store=empty
    def forbidden(*a,**kw):raise AssertionError('No unconfirmed live SQL connection')
    monkeypatch.setattr(readiness.sqlite3,'connect',forbidden)
    before=snapshot(root)
    result=readiness.inspect_security_storage(store,expected_root=root)
    assert result['code']=='quiescence_confirmation_required' and not result['counts']
    assert result['quiescence']=='not_attested' and snapshot(root)==before


def test_invalid_expanduser_configuration_is_sanitized(empty,monkeypatch):
    root,store=empty
    monkeypatch.setenv('FLORA_DATA_DIR','~AUTH1_UNKNOWN_USER_SENTINEL/private')
    result=inspect(store)
    assert result['code']=='data_root_configuration_invalid' and 'SENTINEL'not in json.dumps(result)


def test_backend_error_text_and_paths_are_never_reported(empty,monkeypatch):
    root,store=empty
    def fail(*args,**kwargs):raise sqlite3.OperationalError('PRIVATE-SENTINEL-password-token-path')
    monkeypatch.setattr(readiness.sqlite3,'connect',fail)
    result=inspect(store)
    assert result['code']=='sqlite_unavailable' and 'PRIVATE-SENTINEL'not in json.dumps(result)


def test_readonly_filesystem_is_distinguished_without_write_probe(empty,monkeypatch):
    root,store=empty
    class ReadOnly:
        f_flag=os.ST_RDONLY
    monkeypatch.setattr(readiness.os,'statvfs',lambda p:ReadOnly())
    result=inspect(store)
    assert result['code']=='filesystem_read_only' and not result['counts']


def test_real_process_interrupted_journal_is_retained_without_recovery(empty):
    root,store=empty;(root/'payload.txt').write_text('original private fixture')
    code='''import os
from cios.applications.flora.security_store import SecurityStore
from cios.applications.flora.protected_storage import ProtectedJournal
from cios.applications.flora.storage import data_root
s=SecurityStore()
with s.transaction()as db:
 ProtectedJournal(s).begin(db)
 (data_root()/'payload.txt').write_text('interrupted private fixture')
 os._exit(0)
'''
    subprocess.run([sys.executable,'-c',code],check=True)
    before=snapshot(root);result=inspect(store)
    assert result['code']=='protected_journal_requires_review'
    assert (store.path.parent/'protected-undo/manifest.json').exists()
    assert snapshot(root)==before and (root/'payload.txt').read_text()=='interrupted private fixture'


def test_cli_outputs_only_sanitized_report_and_never_initializes(empty,tmp_path):
    root,store=empty;before=snapshot(root)
    r=subprocess.run([sys.executable,'-m','cios.applications.flora.security_operator','diagnose','--store',str(store.path),
        '--expected-data-root',str(root),'--quiesced'],capture_output=True,text=True)
    assert r.returncode==0 and r.stderr==''
    report=json.loads(r.stdout);assert report['live_authentication']=='UNKNOWN'
    assert str(tmp_path)not in r.stdout and snapshot(root)==before
    store.path.unlink();r=subprocess.run([sys.executable,'-m','cios.applications.flora.security_operator','diagnose','--store',str(store.path),
        '--expected-data-root',str(root),'--quiesced'],capture_output=True,text=True)
    assert r.returncode==1 and json.loads(r.stdout)['code']=='authority_file_missing' and not store.path.exists()


@pytest.mark.parametrize('fault',['missing-schema-row','journal-json','journal-array','journal-unicode'])
def test_runtime_fault_is_generic_503_preserves_store_and_public_reading(empty,fault):
    root,store=empty
    if fault=='missing-schema-row':
        with sqlite3.connect(store.path)as db:db.execute("DELETE FROM meta WHERE key='schema'")
    else:
        folder=store.path.parent/'protected-undo';folder.mkdir(mode=0o700)
        (folder/'manifest.json').write_bytes(b'\xff'if fault=='journal-unicode'else b'[]'if fault=='journal-array'else b'PRIVATE-SENTINEL')
    before=snapshot(root)
    with web()as get:
        status,body,headers=get('/auth/sign-in')
        assert status==503 and 'Security storage unavailable'in body
        assert not any(x in body for x in ('PRIVATE-SENTINEL',str(root),'Traceback','authority.sqlite3'))
        assert 'Set-Cookie'not in headers
        assert get('/industries/banking')[0]==200
        assert get('/operations/security-readiness')[0]==403
        assert get('/industries/banking?analysis=fi-f1-'+'a'*32)[0]==403
    assert snapshot(root)==before


def test_connection_is_closed_when_early_pragma_fails(empty,monkeypatch):
    _,store=empty;closed=[]
    class Failed:
        row_factory=None
        def execute(self,*args):raise sqlite3.OperationalError('PRIVATE-SENTINEL')
        def rollback(self):pass
        def close(self):closed.append(True)
    monkeypatch.setattr(ss.sqlite3,'connect',lambda *a,**kw:Failed())
    with pytest.raises(sqlite3.OperationalError):
        with store.transaction():pytest.fail('Failed setup cannot yield authority')
    assert closed==[True] and ss._ACTIVE.get()is None
