"""Offline deployment-operator diagnostics, never an authority producer.

No transaction(), preauth(), startup probes, recovery, writes or provisioning.
The report contains fixed codes/booleans/counts, never paths or database rows.
A readable store does NOT establish writable sign-in, ownership or source access.
"""
from __future__ import annotations
import errno
import json
import os
from pathlib import Path
import re
import sqlite3
import stat

from .security_store import SCHEMA, SecurityStore
from .storage import data_root


class _Blocked(Exception):
    def __init__(self, code): self.code=code


def _entry(path, *, directory=False, private=False):
    info=path.lstat()
    if stat.S_ISLNK(info.st_mode):raise _Blocked('symlink_refused')
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise _Blocked('wrong_entry_type')
    if private:
        if info.st_uid!=os.geteuid():raise _Blocked('ownership_mismatch')
        required=0o700 if directory else 0o600
        if info.st_mode & 0o077 or info.st_mode & required != required:
            raise _Blocked('private_permissions_invalid')
        if not directory and info.st_nlink!=1:raise _Blocked('hardlink_refused')
    return info


def _ancestors(path):
    for parent in reversed((path,*path.parents)):
        _entry(parent,directory=True)


def _exists(path):
    try:path.lstat();return True
    except FileNotFoundError:return False


def _schema(db):
    # Compare schema1 to its existing owner's DDL, not a second schema registry.
    expected={name:'CREATE TABLE '+name+' ('+body+')'
        for name,body in re.findall(r'CREATE TABLE (\w+) \((.*?)\);',SCHEMA,re.S)}
    normal=lambda sql:re.sub(r'\s+',' ',sql.strip()).casefold()
    actual={name:sql for name,sql in db.execute("SELECT name,sql FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'")}
    if (set(actual)!=set(expected) or any(not isinstance(actual[n],str)for n in expected)
            or any(normal(actual[n])!=normal(expected[n])for n in expected)):
        raise _Blocked('schema_unrecognised')
    meta=dict(db.execute("SELECT key,value FROM meta WHERE key IN ('schema','generation')"))
    if meta.get('schema')!='1' or not re.fullmatch(r'0|[1-9][0-9]*',meta.get('generation','')):
        raise _Blocked('schema_metadata_invalid')
    if db.execute('PRAGMA foreign_key_check').fetchone()is not None:
        raise _Blocked('schema_references_invalid')


def _acl_counts(root):
    parent=root/'enterprise_canvas';path=parent/'access.json'
    if not _exists(parent) or not _exists(path):return {'records':0,'workspace_bound':0}
    _entry(parent,directory=True);_entry(path)
    if path.stat().st_size>16*1024*1024:raise _Blocked('acl_inventory_requires_review')
    raw=json.loads(path.read_text())
    rows=raw.get('records',[])if isinstance(raw,dict)else raw
    if not isinstance(rows,list)or any(not isinstance(row,dict)for row in rows):
        raise _Blocked('acl_inventory_requires_review')
    return {'records':len(rows),'workspace_bound':sum(bool(row.get('workspace_id'))for row in rows)}


def inspect_security_storage(store: SecurityStore, *, expected_root: Path, expected_mount: Path|None=None, quiesced=False):
    """Read the canonical existing store only; never create, recover or repair it.

    Run as the application's OS user in its runtime context. Explicit expected
    paths come from the operator's verified service/disk configuration. Neither
    the default path nor an OS mount proves Render persistence or live access.
    SQL reads require an explicitly operator-attested quiesced context: mode=ro
    alone cannot guarantee no ancillary writes during a concurrent WAL switch.
    Pending SQLite/WAL or protected journals require separate reviewed recovery;
    they are not opened/replayed by this diagnostic. No immutable-lock bypass.
    """
    report={'schema':'auth1-read-only-v1','assessment':'blocked','code':'not_checked',
        'checks':{},'counts':{},'warnings':[],
        'writer_readiness':'UNKNOWN','render_persistence':'UNKNOWN',
        'live_authentication':'UNKNOWN','specific_workspace_and_financial_access':'UNKNOWN',
        'database_created':False,'recovery_executed':False,'authority_changed':False,
        'quiescence':'operator_attested_not_verified'if quiesced is True else'not_attested'}
    phase='configuration'
    db=None
    try:
        try:configured=data_root()
        except (RuntimeError,ValueError):raise _Blocked('data_root_configuration_invalid')
        expected=Path(expected_root)
        if not configured.is_absolute()or not expected.is_absolute()or '..'in configured.parts or '..'in expected.parts:
            raise _Blocked('data_root_configuration_invalid')
        root=configured.absolute()
        legacy=os.getenv('FLORA_PILOT_DIR','')
        if (root!=expected.absolute()or store.path!=root/'security'/'authority.sqlite3'
                or legacy and os.getenv('FLORA_DATA_DIR')and Path(legacy).absolute()!=root):
            raise _Blocked('data_root_configuration_mismatch')
        report['checks']['configuration']='matched_expected_root'
        phase='data_root';_ancestors(root)
        fs=os.statvfs(root)
        if fs.f_flag & os.ST_RDONLY:raise _Blocked('filesystem_read_only')
        if fs.f_bavail==0:report['warnings'].append('filesystem_capacity_exhausted')
        if fs.f_files and getattr(fs,'f_favail',fs.f_ffree)==0:report['warnings'].append('filesystem_inodes_exhausted')
        report['checks']['data_root']='existing_non_symlink_directory'
        if expected_mount is None:
            report['checks']['mount']='UNKNOWN'
        else:
            phase='mount';mount=Path(expected_mount)
            if not mount.is_absolute()or '..'in mount.parts:raise _Blocked('expected_mount_invalid')
            _ancestors(mount)
            if (not root.is_relative_to(mount.absolute())or not os.path.ismount(mount)
                    or root.stat().st_dev!=mount.stat().st_dev):
                raise _Blocked('expected_mount_not_observed')
            report['checks']['mount']='os_mount_observed_not_render_attested'
        phase='security_directory';_entry(store.path.parent,directory=True,private=True)
        report['checks']['security_directory']='private_owner_matched'
        phase='authority_file';before=_entry(store.path,private=True)
        report['checks']['authority_file']='private_owner_matched'
        phase='protected_journal'
        for path in store.path.parent.iterdir():
            if path.name in {'protected-undo','protected-undo-preparing'}or path.name.startswith('protected-complete-'):
                _entry(path,directory=True,private=True)
                raise _Blocked('protected_journal_requires_review')
        report['checks']['protected_journal']='no_pending_entries_observed'
        phase='sqlite_sidecar'
        for suffix in ('-journal','-wal','-shm'):
            path=Path(str(store.path)+suffix)
            if _exists(path):
                _entry(path,private=True)
                raise _Blocked('sqlite_journal_requires_quiesced_review')
        fd=os.open(store.path,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            opened=os.fstat(fd)
            if (opened.st_dev,opened.st_ino)!=(before.st_dev,before.st_ino):raise _Blocked('authority_changed_during_probe')
            header=os.read(fd,100)
        finally:os.close(fd)
        if len(header)<100 or header[:16]!=b'SQLite format 3\x00':raise _Blocked('sqlite_corrupt_or_empty')
        if header[18:20]!=b'\x01\x01':raise _Blocked('sqlite_format_requires_quiesced_review')
        if quiesced is not True:raise _Blocked('quiescence_confirmation_required')
        phase='sqlite'
        db=sqlite3.connect(store.path.as_uri()+'?mode=ro',uri=True,timeout=.25,isolation_level=None)
        db.execute('PRAGMA query_only=ON')
        # A read transaction obtains SQLite's native shared lock. No writer
        # probe, BEGIN IMMEDIATE, immutable=1, checkpoint or journal_mode change.
        db.execute('BEGIN')
        if db.execute('PRAGMA quick_check(1)').fetchall()!=[('ok',)]:raise _Blocked('sqlite_integrity_failed')
        report['checks']['sqlite']='read_only_integrity_check_passed'
        phase='schema';_schema(db);report['checks']['schema']='existing_schema1_matched'
        phase='accounts'
        for roles,enterprises in db.execute('SELECT roles,enterprises FROM memberships'):
            for value in (roles,enterprises):
                parsed=json.loads(value)
                if not isinstance(parsed,list)or any(not isinstance(v,str)for v in parsed):
                    raise _Blocked('membership_metadata_invalid')
        principals=db.execute('SELECT count(*),sum(enabled=1),sum(enabled=1 AND password IS NOT NULL AND length(password)>0)FROM principals').fetchone()
        memberships=db.execute('SELECT count(*),sum(active=1),count(DISTINCT workspace_id)FROM memberships').fetchone()
        report['counts']={'principals':principals[0],'enabled_principals':principals[1]or 0,
            'password_configured_principals':principals[2]or 0,'memberships':memberships[0],
            'active_memberships':memberships[1]or 0,'workspaces':memberships[2]}
        if os.getenv('FLORA_AUTH_PROVIDER','local') == 'supabase':
            # Managed identity does not need a bespoke CIOS password. These
            # counts prove neither provider binding nor successful sign-in.
            # Never call the provider or inspect credentials in this RO probe.
            report['checks']['local_password_readiness']='not_applicable_managed_identity'
            report['provider_binding_readiness']='UNKNOWN'
            if not report['counts']['enabled_principals']or not report['counts']['active_memberships']:
                report['warnings'].append('cios_authorisation_provisioning_incomplete')
        elif not report['counts']['password_configured_principals']or not report['counts']['active_memberships']:
            report['warnings'].append('account_provisioning_incomplete')
        phase='acl';report['counts']['acl']=_acl_counts(root)
        if not report['counts']['acl']['workspace_bound']:report['warnings'].append('workspace_acl_not_observed')
        after=_entry(store.path,private=True)
        if (after.st_dev,after.st_ino)!=(before.st_dev,before.st_ino):raise _Blocked('authority_changed_during_probe')
        report.update(assessment='read_only_checks_passed',code='read_only_checks_passed')
    except _Blocked as exc:
        report['code']=exc.code
    except FileNotFoundError:
        report['code']={'data_root':'data_root_missing','mount':'expected_mount_missing',
            'security_directory':'security_directory_missing','authority_file':'authority_file_missing'}.get(phase,'storage_entry_missing')
    except PermissionError:
        report['code']='filesystem_permission_denied'
    except sqlite3.Error as exc:
        code=getattr(exc,'sqlite_errorcode',0)&255
        report['code']=('sqlite_locked'if code in {sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED}else
            'sqlite_corrupt'if code in {sqlite3.SQLITE_CORRUPT,sqlite3.SQLITE_NOTADB}else
            'sqlite_read_only'if code==sqlite3.SQLITE_READONLY else
            'schema_unrecognised'if phase=='schema'else'sqlite_unavailable')
    except (ValueError,TypeError,KeyError,UnicodeError):
        report['code']='membership_metadata_invalid'if phase=='accounts'else'acl_inventory_requires_review'if phase=='acl'else'storage_metadata_invalid'
    except OSError as exc:
        report['code']='filesystem_read_only'if exc.errno==errno.EROFS else'storage_io_unavailable'
    except Exception:
        # Diagnostics must never turn unexpected backend data into operator
        # stdout tracebacks/rows. This grants no authority and changes no data.
        report['code']='diagnostic_unavailable'
    finally:
        if db is not None:
            try:db.close()
            except sqlite3.Error:
                report.update(assessment='blocked',code='sqlite_unavailable')
    if report['assessment']=='blocked':report['counts']={}
    report['phase']=phase
    return report
