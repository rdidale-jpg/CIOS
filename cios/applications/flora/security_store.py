"""Operational human authentication. Never contains canonical intelligence.

Only the offline operator creates the store. Runtime opens an existing private
store; missing/corrupt/insecure stores confer no authority.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import time

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

COOKIE = "__Host-flora_session"
PREAUTH = "__Host-flora_preauth"
ABSOLUTE = 8 * 3600
IDLE = 30 * 60
RECENT = 5 * 60
HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
_ACTIVE: ContextVar[tuple | None] = ContextVar("flora_security_transaction", default=None)
SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO meta VALUES ('schema','1');
INSERT INTO meta VALUES ('generation','0');
CREATE TABLE principals (user_id TEXT PRIMARY KEY, password TEXT, enabled INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE memberships (membership_id TEXT UNIQUE NOT NULL, user_id TEXT NOT NULL REFERENCES principals(user_id), workspace_id TEXT NOT NULL, roles TEXT NOT NULL, enterprises TEXT NOT NULL, recovery INTEGER NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(user_id,workspace_id));
CREATE TABLE tokens (hash TEXT PRIMARY KEY, kind TEXT NOT NULL, user_id TEXT, workspace_id TEXT NOT NULL DEFAULT '', created REAL NOT NULL, expires REAL NOT NULL, touched REAL NOT NULL, csrf TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, revoked INTEGER NOT NULL DEFAULT 0);
CREATE TABLE limits (key TEXT PRIMARY KEY, start REAL NOT NULL, attempts INTEGER NOT NULL);
CREATE TABLE receipts (digest TEXT PRIMARY KEY, receipt TEXT NOT NULL);
CREATE TABLE audit (seq INTEGER PRIMARY KEY, at REAL NOT NULL, event TEXT NOT NULL, payload TEXT NOT NULL, previous TEXT NOT NULL, digest TEXT UNIQUE NOT NULL);
"""


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def utc(value: float) -> datetime:
    return datetime.fromtimestamp(value, timezone.utc)


def default_path() -> Path:
    from .storage import data_root
    return data_root() / "security" / "authority.sqlite3"


def cookie_token(headers, name=COOKIE) -> str:
    # Only an opaque bearer, never caller role/context projections. Reject
    # duplicate cookie names instead of selecting a parser-dependent winner.
    try:
        raw = headers.get("Cookie", "") if headers is not None else ""
        if not isinstance(raw, str) or len(raw) > 8192:
            return ""
        values = [p.strip().partition("=")[2] for p in raw.split(";")
                  if p.strip().partition("=")[0] == name]
        return values[0] if len(values) == 1 and re.fullmatch(r"[A-Za-z0-9_-]{43}", values[0]) else ""
    except (AttributeError, TypeError):
        return ""


def session_cookie(token: str, name=COOKIE, ttl=ABSOLUTE) -> str:
    return f"{name}={token}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age={ttl}"


@dataclass(frozen=True)
class Membership:
    membership_id: str
    user_id: str
    workspace_id: str
    roles: frozenset[str]
    version: int
    active: bool
    checked_at: datetime


@dataclass(frozen=True)
class Session:
    session_ref: str
    authenticated_at: datetime
    expires_at: datetime
    idle_expires_at: datetime
    reauthenticated_at: datetime | None
    revoked: bool
    revocation_version: int
    checked_at: datetime


@dataclass(frozen=True)
class Context:
    user_id: str
    workspace: str
    workspace_ids: frozenset[str]
    membership: Membership
    roles: frozenset[str]
    effective_capabilities: frozenset[str]
    enterprise_ids: frozenset[str]
    session: Session
    verified_human: bool = True
    authentication_source: str = "verified_password_argon2id"


class SecurityStore:
    def __init__(self, path: Path | None = None):
        self.path = (Path(path) if path is not None else default_path()).absolute()

    def _private(self):
        for path, directory in ((self.path.parent, True), (self.path, False)):
            info = path.lstat()
            if (stat.S_ISLNK(info.st_mode) or info.st_uid != os.geteuid()
                    or info.st_mode & 0o077 or (directory and not stat.S_ISDIR(info.st_mode))
                    or (not directory and not stat.S_ISREG(info.st_mode))):
                raise PermissionError("Security storage unavailable")

    def initialize_offline(self):
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.path.parent.is_symlink() or self.path.parent.stat().st_mode & 0o077:
            raise PermissionError("Private security directory required")
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        self._private()
        db = sqlite3.connect(self.path)
        try:
            db.executescript(SCHEMA)
            db.commit()
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        active = _ACTIVE.get()
        if active and active[0] == self.path.absolute():
            try:
                yield active[1]
            except BaseException:
                active[2]['failed'] = True
                raise
            return
        self._private()
        db = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA synchronous=FULL")
        token = None
        try:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0] != '1':
                raise PermissionError("Security storage unavailable")
            state = {'failed': False}
            token = _ACTIVE.set((self.path.absolute(), db, state))
            from .protected_storage import ProtectedJournal
            journal = ProtectedJournal(self)
            journal.recover(db)
            yield db
            if state['failed']:
                raise PermissionError("Protected transaction was rejected")
            if journal.path.exists():
                journal.flush_data()
            db.commit()
            db.execute("BEGIN IMMEDIATE")
            journal.recover(db)
            db.rollback()
        except BaseException as failure:
            db.rollback()
            # Reacquire the writer lock before recovery. An intervening
            # participating transaction performs the same recovery first.
            if token is not None:
                db.execute("BEGIN IMMEDIATE")
                from .protected_storage import ProtectedJournal
                try:
                    ProtectedJournal(self).recover(db)
                except BaseException as recovery_error:
                    # Retain both the primary failure and recovery diagnosis.
                    # Recovery keeps its journal; subsequent resolution denies.
                    failure.add_note(f'Protected recovery failed: {recovery_error}')
                finally:
                    db.rollback()
            raise
        finally:
            if token is not None:
                _ACTIVE.reset(token)
            db.close()

    def audit(self, db, event, **payload):
        previous = db.execute("SELECT digest FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        previous = previous[0] if previous else ""
        stamp = time.time()
        body = canonical(payload)
        value = digest(canonical([stamp, event, body, previous]))
        db.execute("INSERT INTO audit(at,event,payload,previous,digest) VALUES(?,?,?,?,?)", (stamp,event,body,previous,value))
        return value

    def _issue(self, db, kind, user="", workspace="", ttl=ABSOLUTE):
        token, csrf, now = secrets.token_urlsafe(32), secrets.token_urlsafe(32), time.time()
        db.execute("INSERT INTO tokens(hash,kind,user_id,workspace_id,created,expires,touched,csrf) VALUES(?,?,?,?,?,?,?,?)",
                   (digest(token),kind,user,workspace,now,now+ttl,now,digest(csrf)))
        return token, csrf

    def _token(self, db, token, kind):
        row = db.execute("SELECT * FROM tokens WHERE hash=? AND kind=?", (digest(token),kind)).fetchone()
        now = time.time()
        if not row or row['revoked'] or row['expires'] <= now or (kind == 'session' and row['touched'] + IDLE <= now):
            raise PermissionError("Authentication unavailable or expired")
        if kind == 'session':
            user = db.execute("SELECT * FROM principals WHERE user_id=? AND enabled=1", (row['user_id'],)).fetchone()
            if not user or not user['password'] or row['version'] != user['version']:
                raise PermissionError("Authentication unavailable or expired")
        return row

    def preauth(self):
        with self.transaction() as db:
            return self._issue(db, 'preauth', ttl=600)

    def csrf(self, db, token, value, kind='session'):
        row = self._token(db, token, kind)
        if not isinstance(value, str) or not secrets.compare_digest(row['csrf'], digest(value)):
            raise PermissionError("Request verification failed")
        return row

    def _limited(self, db, key):
        now = time.time()
        row = db.execute("SELECT * FROM limits WHERE key=?", (key,)).fetchone()
        if row and row['start'] + 900 > now and row['attempts'] >= 10:
            return True
        if not row or row['start'] + 900 <= now:
            db.execute("INSERT OR REPLACE INTO limits VALUES(?,?,1)", (key,now))
        else:
            db.execute("UPDATE limits SET attempts=attempts+1 WHERE key=?", (key,))
        return False

    def enroll_offline(self, user, delivery: Path):
        # Exclusive private file: secrets never appear in stdout, argv or logs.
        fd = os.open(delivery, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        try:
            with self.transaction() as db:
                if not db.execute("SELECT 1 FROM principals WHERE user_id=? AND enabled=1", (user,)).fetchone():
                    raise PermissionError("Enrollment unavailable")
                db.execute("UPDATE tokens SET revoked=1 WHERE user_id=?", (user,))
                db.execute("UPDATE principals SET version=version+1 WHERE user_id=?", (user,))
                token, _ = self._issue(db, 'enroll', user, ttl=900)
                with os.fdopen(fd, "w") as out:
                    fd = None
                    out.write(token + "\n")
                    out.flush()
                    os.fsync(out.fileno())
                self.audit(db, 'enrollment_issued', user_id=user)
        except BaseException:
            delivery.unlink(missing_ok=True)
            raise
        finally:
            if fd is not None:
                os.close(fd)

    def enroll(self, token, password, preauth, csrf):
        result = False
        with self.transaction() as db:
            self.csrf(db, preauth, csrf, 'preauth')
            limited = self._limited(db, 'enrollment')
            try:
                row = self._token(db, token, 'enroll')
                if limited or not 15 <= len(password) <= 1024:
                    raise PermissionError("Enrollment unavailable")
                db.execute("UPDATE principals SET password=?,version=version+1 WHERE user_id=? AND enabled=1", (HASHER.hash(password),row['user_id']))
                db.execute("UPDATE tokens SET revoked=1 WHERE user_id=? OR hash=?", (row['user_id'],digest(preauth)))
                self.audit(db, 'credential_set', user_id=row['user_id'])
                result = True
            except PermissionError:
                self.audit(db, 'enrollment_failed')
        if not result:
            raise PermissionError("Authentication failed")

    def login(self, user, password, preauth, csrf):
        result = None
        with self.transaction() as db:
            self.csrf(db, preauth, csrf, 'preauth')
            limited = self._limited(db, 'login:' + digest(user))
            limited = self._limited(db, 'login:global') or limited
            row = db.execute("SELECT * FROM principals WHERE user_id=? AND enabled=1", (user,)).fetchone()
            try:
                # Real Argon2 work for unknown IDs as well; do not disclose existence.
                encoded = row['password'] if row and row['password'] else HASHER.hash(secrets.token_urlsafe(32))
                valid = HASHER.verify(encoded, password)
            except (VerificationError, InvalidHashError):
                valid = False
            if valid and row and not limited:
                db.execute("UPDATE tokens SET revoked=1 WHERE hash=?", (digest(preauth),))
                result = self._issue(db, 'session', user)
                db.execute("UPDATE tokens SET version=? WHERE hash=?", (row['version'],digest(result[0])))
                self.audit(db, 'sign_in', user_id=user, session_ref=digest(result[0]))
            else:
                self.audit(db, 'sign_in_failed')
        if result is None:
            raise PermissionError("Authentication failed")
        return result

    def choices(self, token):
        with self.transaction() as db:
            row = self._token(db,token,'session')
            return [r[0] for r in db.execute("SELECT workspace_id FROM memberships WHERE user_id=? AND active=1 ORDER BY workspace_id", (row['user_id'],))]

    def select(self, token, csrf, workspace):
        with self.transaction() as db:
            row = self.csrf(db,token,csrf)
            if not db.execute("SELECT 1 FROM memberships WHERE user_id=? AND workspace_id=? AND active=1", (row['user_id'],workspace)).fetchone():
                raise PermissionError("Workspace unavailable")
            db.execute("UPDATE tokens SET revoked=1 WHERE hash=?", (digest(token),))
            result = self._issue(db,'session',row['user_id'],workspace,ttl=max(0,row['expires']-time.time()))
            # Workspace rotation preserves authentication age and absolute deadline.
            db.execute("UPDATE tokens SET created=?,expires=?,version=? WHERE hash=?", (row['created'],row['expires'],row['version'],digest(result[0])))
            self.audit(db,'workspace_selected',user_id=row['user_id'],workspace_id=workspace,session_ref=digest(result[0]))
            return result

    def logout(self, token, csrf):
        with self.transaction() as db:
            row = self.csrf(db,token,csrf)
            db.execute("UPDATE tokens SET revoked=1 WHERE hash=?", (digest(token),))
            self.audit(db,'sign_out',user_id=row['user_id'],session_ref=digest(token))

    def resolve(self, token, *, touch=False):
        from .access import role_capabilities
        with self.transaction() as db:
            row = self._token(db,token,'session')
            memberships = db.execute("SELECT * FROM memberships WHERE user_id=? AND active=1", (row['user_id'],)).fetchall()
            member = next((m for m in memberships if m['workspace_id'] == row['workspace_id']), None)
            if member is None:
                raise PermissionError("Workspace membership unavailable")
            now = time.time()
            roles = frozenset(json.loads(member['roles']))
            capabilities = set(role_capabilities(roles))
            if member['recovery']:
                capabilities.add('storage.recover')
            if touch:
                db.execute("UPDATE tokens SET touched=? WHERE hash=?", (now,digest(token)))
            membership = Membership(member['membership_id'],row['user_id'],member['workspace_id'],roles,member['version'],True,utc(now))
            session = Session(digest(token),utc(row['created']),utc(row['expires']),utc(min(row['expires'],(now if touch else row['touched'])+IDLE)),utc(row['created']),False,row['version'],utc(now))
            return Context(row['user_id'],member['workspace_id'],frozenset(m['workspace_id'] for m in memberships),membership,roles,frozenset(capabilities),frozenset(json.loads(member['enterprises'])),session)

    @contextmanager
    def mutation(self, headers, csrf, recent=False):
        with self.transaction() as db:
            token = cookie_token(headers)
            self.csrf(db,token,csrf)
            context = self.resolve(token)
            if recent and time.time()-context.session.authenticated_at.timestamp() > RECENT:
                raise PermissionError("Sign in again before this action")
            from .protected_storage import ProtectedJournal
            ProtectedJournal(self).begin(db)
            self.audit(db,'mutation_authorized',user_id=context.user_id,workspace_id=context.workspace,membership_id=context.membership.membership_id,membership_version=context.membership.version,session_ref=context.session.session_ref)
            yield context
            # SQLite IMMEDIATE lock serializes revocation/membership changes
            # with the full protected action, including its last write.
            self.resolve(token, touch=True)

    def revoke_offline(self, user, workspace=None, disable=False):
        with self.transaction() as db:
            if workspace is not None:
                db.execute("UPDATE memberships SET active=0,version=version+1 WHERE user_id=? AND workspace_id=?",(user,workspace))
            if disable:
                db.execute("UPDATE principals SET enabled=0,version=version+1 WHERE user_id=?",(user,))
            db.execute("UPDATE tokens SET revoked=1 WHERE user_id=?",(user,))
            db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='generation'")
            self.audit(db,'authority_revoked',user_id=user,workspace_id=workspace,disabled=disable)
