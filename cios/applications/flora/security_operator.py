"""Offline-only operator tools. Never import application storage initializers.

An explicitly supplied snapshot is read-only evidence, not an identity provider.
Approval is a deliberate deployment-operator action after independent ownership
verification. Ambiguous evidence must be rejected by that operator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets

from .security_store import SecurityStore, canonical, digest

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:@-]{0,127}")


def reconcile(snapshot: Path):
    snapshot = snapshot.resolve(strict=True)
    if not snapshot.is_dir():
        raise ValueError("Explicit snapshot directory required")
    files, principals, workspaces = {}, set(), set()
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and ID.fullmatch(item):
                    if key in {'user_id','actor_id','reviewer_id','requested_by','approved_by','executed_by'}:
                        principals.add(item)
                    if key in {'workspace','workspace_id'}:
                        workspaces.add(item)
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    for path in sorted(snapshot.rglob('*')):
        if path.is_symlink():
            raise ValueError("Snapshot symlinks are forbidden")
        if path.is_file():
            raw = path.read_bytes()
            files[str(path.relative_to(snapshot))] = hashlib.sha256(raw).hexdigest()
            if path.suffix == '.json':
                visit(json.loads(raw))
    return {'files':files,'principal_references':sorted(principals),'workspace_references':sorted(workspaces),
            'warning':'Historical claims are unverified. Independent binding approval is required.'}


def plan(store: SecurityStore, snapshot: Path, manifest: dict):
    evidence = reconcile(snapshot)
    if manifest.get('approved') is not True or not manifest.get('approval_reference') or not manifest.get('operator'):
        raise ValueError('Independent ownership approval required')
    if manifest.get('snapshot_digest') != digest(canonical(evidence)):
        raise ValueError('Snapshot evidence changed')
    if not manifest.get('evidence') or any(evidence['files'].get(p) != h for p,h in manifest['evidence'].items()):
        raise ValueError('Exact evidence references and digests required')
    bindings = manifest.get('bindings', [])
    if not bindings:
        raise ValueError('Exact bindings required')
    seen = set()
    for binding in bindings:
        user, workspace = binding['user_id'], binding['workspace_id']
        if (not ID.fullmatch(user) or user == 'flora-pilot-operator' or not ID.fullmatch(workspace)
                or user not in evidence['principal_references'] or workspace not in evidence['workspace_references']
                or (user,workspace) in seen or binding.get('roles') != ['cios_owner']
                or not binding.get('enterprise_ids') or '*' in binding['enterprise_ids']
                or any(not ID.fullmatch(e) for e in binding['enterprise_ids'])):
            raise ValueError('Conflicting, missing or non-exact binding')
        seen.add((user,workspace))
    with store.transaction() as db:
        generation = db.execute("SELECT value FROM meta WHERE key='generation'").fetchone()[0]
    body = {'manifest':manifest,'generation':generation,'snapshot_digest':digest(canonical(evidence))}
    return dict(body, digest=digest(canonical(body)))


def apply(store: SecurityStore, snapshot: Path, proposed: dict, confirmation: str):
    body = {k:v for k,v in proposed.items() if k != 'digest'}
    if confirmation != proposed.get('digest') or digest(canonical(body)) != confirmation:
        raise ValueError('Confirm the exact reviewed plan digest')
    if digest(canonical(reconcile(snapshot))) != proposed['snapshot_digest']:
        raise ValueError('Stale snapshot')
    with store.transaction() as db:
        prior = db.execute('SELECT receipt FROM receipts WHERE digest=?',(confirmation,)).fetchone()
        if prior:
            return json.loads(prior[0])
        if proposed != plan(store,snapshot,proposed['manifest']):
            raise ValueError('Stale plan')
        for b in proposed['manifest']['bindings']:
            if db.execute('SELECT 1 FROM memberships WHERE user_id=? AND workspace_id=?',(b['user_id'],b['workspace_id'])).fetchone():
                raise ValueError('Assignment already exists; explicit recovery required')
            db.execute('INSERT OR IGNORE INTO principals(user_id) VALUES(?)',(b['user_id'],))
            db.execute('INSERT INTO memberships(membership_id,user_id,workspace_id,roles,enterprises,recovery) VALUES(?,?,?,?,?,?)',
                       (secrets.token_hex(16),b['user_id'],b['workspace_id'],canonical(b['roles']),canonical(b['enterprise_ids']),int(b.get('recovery_grant') is True)))
        audit = store.audit(db,'bootstrap_applied',plan_digest=confirmation,operator=proposed['manifest']['operator'],approval_reference=proposed['manifest']['approval_reference'],bindings=proposed['manifest']['bindings'])
        receipt = {'plan_digest':confirmation,'audit_digest':audit,'bindings':proposed['manifest']['bindings']}
        db.execute('INSERT INTO receipts VALUES(?,?)',(confirmation,canonical(receipt)))
        db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='generation'")
        return receipt


def private_json(path, value):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd,'w') as out:
        out.write(json.dumps(value,indent=2)+'\n')
        out.flush()
        os.fsync(out.fileno())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['inspect','initialize','plan','apply','enroll','revoke','disable'])
    p.add_argument('--store',type=Path)
    p.add_argument('--snapshot',type=Path)
    p.add_argument('--manifest',type=Path)
    p.add_argument('--plan',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--confirm')
    p.add_argument('--user')
    p.add_argument('--workspace')
    args=p.parse_args()
    if args.command == 'inspect':
        private_json(args.output,reconcile(args.snapshot)); return
    if not args.store:
        p.error('Explicit operational store required')
    store=SecurityStore(args.store)
    if args.command == 'initialize':
        if args.confirm != 'CREATE EMPTY SECURITY STORE':
            p.error('Explicit empty-store confirmation required')
        store.initialize_offline()
    elif args.command == 'plan':
        private_json(args.output,plan(store,args.snapshot,json.loads(args.manifest.read_text())))
    elif args.command == 'apply':
        private_json(args.output,apply(store,args.snapshot,json.loads(args.plan.read_text()),args.confirm))
    else:
        if not args.user or args.confirm != args.user:
            p.error('Confirm exact principal ID')
        if args.command == 'enroll':
            store.enroll_offline(args.user,args.output)
        else:
            store.revoke_offline(args.user,args.workspace,disable=args.command=='disable')


if __name__ == '__main__':
    main()
