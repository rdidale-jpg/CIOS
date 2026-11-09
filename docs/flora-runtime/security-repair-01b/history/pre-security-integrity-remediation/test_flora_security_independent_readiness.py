"""Independent 01B/01C review probes. Required-safe assertions, synthetic stores.

No authorization providers are mocked; boundary timing and storage failures are
injected only after genuine authority/scope evaluation. Failures remain visible.
"""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
import threading
import time

import pytest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_security_workspace_boundary import resource, hashes
from cios.applications.flora import security,security_store
from cios.applications.flora.security_store import canonical,RECENT
from cios.applications.flora.protected_storage import ProtectedJournal
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository,can_access_canvas_record
from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService

pytestmark=pytest.mark.real_security_boundary


def record(tmp_path, **facts):
    (tmp_path/'independent-observation.json').write_text(json.dumps(facts,indent=2)+'\n')


def feedback(service, headers):
    return service.submit(headers,enterprise_id='synthetic-enterprise',action_type='context',
        user_statement='SYNTHETIC_PRIVATE_FEEDBACK_MARKER',rationale='Synthetic independent review',visibility='restricted')


@pytest.mark.parametrize('boundary',['wrong-workspace','denied-acl'])
def test_feedback_read_enforces_current_resource_scope_and_acl(authority,tmp_path,boundary):
    store,_,_,headers,_=signed(authority,tmp_path)
    _,acl=resource(store)
    service=EnterpriseCanvasFeedbackService();feedback(service,headers)
    if boundary=='wrong-workspace':acl=replace(acl,workspace_id='other-workspace')
    else:acl=replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},))
    EnterpriseCanvasAccessRepository().save(acl)
    assert not can_access_canvas_record(headers,'synthetic-enterprise')
    before=hashes(store.path.parent.parent)
    visible=service.visible_feedback(headers,'synthetic-enterprise')
    record(tmp_path,boundary=boundary,records_disclosed=len(visible),files_unchanged=before==hashes(store.path.parent.parent))
    assert visible==[]


def test_direct_feedback_mutation_cannot_write_after_revocation(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();append=service.repo.append
    def revoke_before_persistence(value):
        store.revoke_offline('synthetic-human','synthetic-workspace')
        return append(value)
    monkeypatch.setattr(service.repo,'append',revoke_before_persistence)
    denied=False
    try:feedback(service,headers)
    except PermissionError:denied=True
    rows=service.repo.list_all()
    record(tmp_path,revoked_session_resolves=security.verified_context(headers) is not None,records_written=len(rows),denied=denied)
    assert denied and rows==[]


def test_undo_cannot_erase_concurrently_accepted_direct_feedback(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();append=service.repo.append
    authorised=threading.Event();persist=threading.Event()
    def paused(value):
        authorised.set();assert persist.wait(10)
        return append(value)
    monkeypatch.setattr(service.repo,'append',paused)
    accepted=None
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(feedback,service,headers)
        assert authorised.wait(5)
        try:
            with pytest.raises(sqlite3.OperationalError):
                with store.transaction() as db:
                    ProtectedJournal(store).begin(db)
                    persist.set();accepted=future.result(5)
                    raise sqlite3.OperationalError('synthetic unrelated authority failure')
        finally:persist.set()
    surviving=service.repo.list_all()
    record(tmp_path,accepted_feedback_returned=accepted is not None,surviving_records=len(surviving),authority_still_valid=security.verified_context(headers) is not None)
    assert accepted is not None and any(r.feedback_id==accepted.feedback_id for r in surviving)


def test_recovery_preserves_existing_names_matching_temporary_pattern(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    root=store.path.parent.parent
    ordinary=root/'synthetic-protected.json';ordinary.write_text('original protected content')
    collision=root/'.synthetic-protected.json.recovery';collision.write_text('independent existing protected content')
    before=hashes(root)
    @security.verified_service_write('package.review')
    def action(*,headers):
        ordinary.write_text('partial protected write')
        raise OSError('synthetic failure before authority commit')
    with pytest.raises(OSError):action(headers=headers)
    after=hashes(root)
    record(tmp_path,before_sha256=before,after_sha256=after,existing_collision_file_preserved=collision.exists(),full_store_unchanged=before==after,
        journal_retained=ProtectedJournal(store).path.exists(),authority_still_valid=security.verified_context(headers) is not None)
    assert before==after


def test_direct_storage_cleanup_requires_recent_authentication(authority,tmp_path,monkeypatch):
    from cios.applications.flora.storage_maintenance import cleanup_superseded_staging_history,DISPOSABLE_HISTORY
    store,_,_,headers,_=signed(authority,tmp_path)
    with store.transaction() as db:db.execute('UPDATE memberships SET recovery=1')
    root=store.path.parent.parent
    version=root/DISPOSABLE_HISTORY/'synthetic-run'/'synthetic-version'
    version.mkdir(parents=True);(version/'retained.txt').write_text('synthetic retained snapshot')
    base=time.time();monkeypatch.setattr(security_store.time,'time',lambda:base+RECENT+10)
    assert security.verified_context(headers) is not None
    denied=False
    try:cleanup_superseded_staging_history(root,keep_versions=0,dry_run=False,headers=headers)
    except PermissionError:denied=True
    record(tmp_path,authentication_older_than_recent_limit=True,cleanup_denied=denied,version_preserved=version.exists())
    assert denied and version.exists()


def test_commercial_profile_write_requires_effective_edit_capability(authority,tmp_path):
    from cios.applications.flora.commercial_mission import save_employer_context,resolve_employer_context
    store,_,_,headers,_=signed(authority,tmp_path)
    with store.transaction() as db:db.execute('UPDATE memberships SET roles=?',(canonical(['package.inspect']),))
    assert 'commercial_context.edit' not in security.verified_context(headers).effective_capabilities
    before=hashes(store.path.parent.parent)
    denied=False
    try:save_employer_context(headers,{'organisation':'Synthetic private employer'})
    except PermissionError:denied=True
    record(tmp_path,effective_edit_capability=False,write_denied=denied,profile_persisted=resolve_employer_context(headers) is not None)
    assert denied and hashes(store.path.parent.parent)==before
