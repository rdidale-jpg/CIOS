"""Recoverable undo journal for the local, single-writer protected data root.

The authority SQLite IMMEDIATE transaction is the interprocess lock. Backups are
made durable before effects; a commit marker is recorded with the authority
audit only after data fsync. Every authority transaction recovers before serving
readers. This is recovery, not a distributed filesystem/SQLite transaction.
Uncoordinated writers and external side effects are outside this protocol.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import uuid
import tempfile


def sync_dir(path):
    fd = os.open(path, os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def file_digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def inventory(root, security):
    files, directories = {}, []
    def visit(folder):
        for path in sorted(folder.iterdir()):
            if path == security:
                continue
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise PermissionError('Protected storage cannot contain symlinks')
            name = str(path.relative_to(root))
            if stat.S_ISDIR(info.st_mode):
                directories.append(name)
                visit(path)
            elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                files[name] = {'mode': stat.S_IMODE(info.st_mode),
                               'sha256': file_digest(path)}
            else:
                raise PermissionError('Unsupported protected storage entry')
    visit(root)
    return files, directories


class ProtectedJournal:
    def __init__(self, store):
        from .storage import data_root
        self.root = data_root().absolute()
        self.security = store.path.parent
        if (store.path != self.root / 'security' / 'authority.sqlite3'
                or self.root.is_symlink()):
            raise PermissionError('Protected storage requires the authoritative local data root')
        self.path = self.security / 'protected-undo'
        self.staging = self.security / 'protected-undo-preparing'

    def _require_transaction(self, db=None):
        from .security_store import _ACTIVE
        active = _ACTIVE.get()
        if (not active or active[0].parent != self.security or not active[1].in_transaction
                or (db is not None and db is not active[1])):
            raise PermissionError('Protected recovery requires the authority writer transaction')

    def begin(self, db):
        self._require_transaction(db)
        if self.path.exists():
            return  # Nested service: share the outer transaction's journal.
        files, directories = inventory(self.root, self.security)
        self.staging.mkdir(mode=0o700)
        try:
            # Reserve space for replacement-based undo before allowing effects.
            # Unsupported reservation or insufficient capacity denies admission.
            reserve = self.staging / 'undo-reserve'
            fd = os.open(reserve, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                amount = max(((self.root/name).stat().st_size for name in files), default=0) + 1024*1024
                os.posix_fallocate(fd, 0, amount)
                os.fsync(fd)
            finally:
                os.close(fd)
            backups = self.staging / 'files'
            backups.mkdir(mode=0o700)
            for number, (name, entry) in enumerate(files.items()):
                entry['backup'] = str(number)
                target = backups / str(number)
                with target.open('xb') as handle:
                    os.chmod(target, 0o600)
                    with (self.root / name).open('rb') as source:
                        shutil.copyfileobj(source, handle, 64*1024)
                    handle.flush()
                    os.fsync(handle.fileno())
                if file_digest(target) != entry['sha256']:
                    raise OSError('Protected backup changed during capture')
            manifest = {'id': uuid.uuid4().hex, 'files': files, 'directories': directories,
                        'directory_modes': {name:stat.S_IMODE((self.root/name).stat().st_mode) for name in directories}}
            with (self.staging / 'manifest.json').open('x') as handle:
                json.dump(manifest, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            # A separate durable seal binds the complete inventory and metadata.
            with (self.staging / 'manifest.sha256').open('x') as handle:
                handle.write(file_digest(self.staging / 'manifest.json'))
                handle.flush()
                os.fsync(handle.fileno())
            sync_dir(backups)
            sync_dir(self.staging)
            os.replace(self.staging, self.path)
            sync_dir(self.security)
            db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('protected_commit',?)", (manifest['id'],))
        except BaseException:
            # If publication succeeded the durable journal must remain for undo.
            if self.staging.exists():
                shutil.rmtree(self.staging)
            raise

    def flush_data(self):
        self._require_transaction()
        files, directories = inventory(self.root, self.security)
        for name in files:
            with (self.root / name).open('rb') as handle:
                os.fsync(handle.fileno())
        for name in sorted(directories, key=lambda n: n.count('/'), reverse=True):
            sync_dir(self.root / name)
        sync_dir(self.root)

    def recover(self, db):
        self._require_transaction(db)
        # Interrupted post-commit cleanup contains no live undo record.
        for garbage in self.security.glob('protected-complete-*'):
            if garbage.is_symlink():
                raise PermissionError('Unsafe completed journal')
            shutil.rmtree(garbage)
            sync_dir(self.security)
        if self.staging.exists():
            # No service starts before the ready journal has been published.
            shutil.rmtree(self.staging)
            sync_dir(self.security)
        if not self.path.exists():
            return
        if self.path.is_symlink():
            raise PermissionError('Unsafe protected journal')
        manifest = json.loads((self.path / 'manifest.json').read_text())
        self.validate_manifest(manifest)
        marker = db.execute("SELECT value FROM meta WHERE key='protected_commit'").fetchone()
        if not marker or marker[0] != manifest['id']:
            self.restore(manifest)
        # Rename before removal: interrupted cleanup cannot damage a live journal.
        garbage = self.security / ('protected-complete-' + uuid.uuid4().hex)
        os.replace(self.path, garbage)
        sync_dir(self.security)
        shutil.rmtree(garbage)
        sync_dir(self.security)

    def validate_manifest(self, manifest):
        """Validate all metadata and the exact backup inventory before effects.

        No legacy fallback: an unsealed/inconsistent journal needs explicit
        operator recovery and remains available for diagnosis.
        """
        self._require_transaction()
        try:
            source = self.path / 'manifest.json'
            seal = self.path / 'manifest.sha256'
            backups = self.path / 'files'
            if (source.is_symlink() or seal.is_symlink() or backups.is_symlink()
                    or seal.read_text() != file_digest(source)
                    or json.loads(source.read_text()) != manifest):
                raise ValueError('Manifest seal mismatch')
            if (not isinstance(manifest.get('id'), str) or not manifest['id']
                    or not isinstance(manifest.get('files'), dict)
                    or not isinstance(manifest.get('directories'), list)
                    or not isinstance(manifest.get('directory_modes'), dict)):
                raise ValueError('Invalid manifest structure')
            def safe(name):
                path = Path(name)
                if (not isinstance(name, str) or not path.parts or path.is_absolute()
                        or '..' in path.parts or str(path) != name or path.parts[0] == 'security'):
                    raise ValueError('Unsafe snapshot path')
            directories = manifest['directories']
            if len(set(directories)) != len(directories) or set(directories) != set(manifest['directory_modes']):
                raise ValueError('Incomplete directory metadata')
            names = set(manifest['files'])
            if names & set(directories):
                raise ValueError('Conflicting snapshot entries')
            for name in names | set(directories):
                safe(name)
                if any(str(parent) not in directories for parent in Path(name).parents if str(parent) != '.'):
                    raise ValueError('Missing parent directory metadata')
            expected = set()
            for name, entry in manifest['files'].items():
                number = entry['backup']
                if (not isinstance(number, str) or not number.isdigit() or number in expected
                        or type(entry['mode']) is not int or not 0 <= entry['mode'] <= 0o7777):
                    raise ValueError('Conflicting backup metadata')
                expected.add(number)
                backup = backups / number
                info = backup.lstat()
                if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                        or file_digest(backup) != entry['sha256']):
                    raise ValueError('Invalid protected backup')
            if {p.name for p in backups.iterdir()} != expected:
                raise ValueError('Incomplete protected backup inventory')
            if any(type(mode) is not int or not 0 <= mode <= 0o7777
                   for mode in manifest['directory_modes'].values()):
                raise ValueError('Invalid directory permissions')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise OSError('Invalid protected recovery manifest; evidence retained') from exc

    def restore(self, manifest):
        self._require_transaction()
        self.validate_manifest(manifest)
        # Verify every backup and path before changing protected data. Keep the
        # journal on *any* recovery error; subsequent authority resolution denies.
        for name, entry in manifest['files'].items():
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] == 'security':
                raise PermissionError('Unsafe recovery path')
            backup = self.path / 'files' / entry['backup']
            if not entry['backup'].isdigit() or backup.is_symlink():
                raise PermissionError('Unsafe recovery backup')
            if file_digest(backup) != entry['sha256']:
                raise OSError('Invalid protected backup')
        for name in manifest['directories']:
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] == 'security':
                raise PermissionError('Unsafe recovery directory')
        files, directories = inventory(self.root, self.security)
        reserve = self.path / 'undo-reserve'
        if reserve.exists():
            reserve.unlink()
            sync_dir(self.path)
        # Recovery temporaries live in the private journal, never the protected
        # namespace. Interrupted files remain there for inspection/retry.
        recovery = self.path / 'restoring'
        recovery.mkdir(mode=0o700, exist_ok=True)
        if recovery.is_symlink():
            raise PermissionError('Unsafe recovery directory')
        for name in manifest['directories']:
            if not (self.root/name).exists() and name not in manifest.get('directory_modes', {}):
                raise PermissionError('Legacy journal lacks deleted directory permissions')
            (self.root / name).mkdir(parents=True, exist_ok=True)
        for name, entry in manifest['files'].items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary_name = tempfile.mkstemp(prefix='restore-', dir=recovery)
            temporary = Path(temporary_name)
            with os.fdopen(fd, 'wb') as handle:
                with (self.path / 'files' / entry['backup']).open('rb') as source:
                    shutil.copyfileobj(source, handle, 64*1024)
                handle.flush()
                os.fchmod(handle.fileno(), entry['mode'])
                os.fsync(handle.fileno())
            if file_digest(temporary) != entry['sha256']:
                raise OSError('Recovery write verification failed')
            os.replace(temporary, target)
            sync_dir(target.parent)
            sync_dir(recovery)
        for name in files.keys() - manifest['files'].keys():
            (self.root / name).unlink(missing_ok=True)
        for name in sorted(set(directories) - set(manifest['directories']), key=lambda n: n.count('/'), reverse=True):
            (self.root / name).rmdir()
        for name, mode in manifest.get('directory_modes', {}).items():
            if name not in manifest['directories']:
                raise PermissionError('Invalid recovery directory metadata')
            os.chmod(self.root/name, mode)
        self.flush_data()
        actual, actual_directories = inventory(self.root, self.security)
        expected = {name:{key:entry[key] for key in ('mode','sha256')} for name,entry in manifest['files'].items()}
        if actual != expected or set(actual_directories) != set(manifest['directories']):
            raise OSError('Recovered protected state does not match the journal')
        if any(stat.S_IMODE((self.root/name).stat().st_mode) != mode for name,mode in manifest.get('directory_modes',{}).items()):
            raise OSError('Recovered directory permissions do not match the journal')


def serialized_runtime_writer(function):
    """Coordinate existing trusted worker entry points; never supplies authority.

    Workers retain their own capability/domain checks. The no-store path is only
    the pre-existing offline/unit worker mode; privileged services still require
    a real authority resolver. An insecure/corrupt existing store raises.
    """
    from functools import wraps
    @wraps(function)
    def guarded(*args, **kwargs):
        from .security_store import SecurityStore
        store = SecurityStore()
        if not store.path.exists():
            return function(*args, **kwargs)
        with store.transaction():
            return function(*args, **kwargs)
    return guarded
