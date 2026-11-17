"""Supabase verifies identity; existing SecurityStore owns all CIOS authority.

No signup, refresh engine, provider roles, provisioning or canonical writes.
Only an encrypted access token is retained for live getUser verification. Expiry
requires interactive sign-in; a provider refresh cannot extend authentication age.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken

_PUBLIC_DENIALS = ContextVar('flora_public_identity_denials', default=None)


@contextmanager
def public_read():
    """Negative provider cache for ONE public render, never verified authority."""
    reset = _PUBLIC_DENIALS.set(set())
    try:
        yield
    finally:
        _PUBLIC_DENIALS.reset(reset)


def selected():
    mode = os.getenv('FLORA_AUTH_PROVIDER', 'local')
    if mode not in {'local', 'supabase'}:
        raise PermissionError('Sign-in unavailable')
    return mode == 'supabase'


def uuid(value):
    if not isinstance(value, str) or str(UUID(value)) != value:
        raise ValueError('Exact provider identifier required')
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


@dataclass(frozen=True)
class Provider:
    url: str
    key: str
    cipher: Fernet

    @classmethod
    def configured(cls):
        url = os.getenv('FLORA_SUPABASE_URL', '')
        key = os.getenv('FLORA_SUPABASE_PUBLISHABLE_KEY', '')
        # Separate hosted project only. No arbitrary host, path, redirect or
        # service-role secret; custom domains require a future reviewed change.
        if (not re.fullmatch(r'https://[a-z0-9]{20}\.supabase\.co', url)
                or not re.fullmatch(r'sb_publishable_[A-Za-z0-9_-]{12,256}', key)):
            raise PermissionError('Sign-in unavailable')
        try:
            cipher = Fernet(os.environ['FLORA_SUPABASE_SESSION_KEY'].encode('ascii'))
        except (KeyError, ValueError, UnicodeError):
            raise PermissionError('Sign-in unavailable') from None
        return cls(url, key, cipher)

    @property
    def issuer(self):
        return self.url + '/auth/v1'

    def request(self, method, path, *, token='', body=None):
        headers = {'apikey': self.key, 'Accept': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        raw = None
        if body is not None:
            headers['Content-Type'] = 'application/json'
            raw = json.dumps(body).encode()
        request = Request(self.issuer + path, method=method, headers=headers, data=raw)
        try:
            with build_opener(NoRedirect).open(request, timeout=5) as response:
                data = response.read(65537)
                if len(data) > 65536 or response.status not in {200, 204}:
                    raise ValueError('Invalid response')
                if not data:
                    return {}
                result = json.loads(data)
                if not isinstance(result, dict):
                    raise ValueError('Invalid response')
                return result
        except (HTTPError, URLError, OSError, ValueError, UnicodeError):
            # Never expose provider bodies, credentials, account existence or
            # remote URLs in a user response or log.
            raise PermissionError('Sign-in unavailable') from None

    def verify(self, token):
        denied = _PUBLIC_DENIALS.get()
        ref = hashlib.sha256(token.encode()).hexdigest() if isinstance(token, str) else ''
        if denied is not None and ref in denied:
            raise PermissionError('Sign-in unavailable')
        try:
            if not isinstance(token, str) or len(token) > 16384:
                raise ValueError('Invalid token')
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError('Invalid token')
            claims = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (-len(parts[1]) % 4)))
            subject = uuid(claims['sub'])
            uuid(claims['session_id'])
            expires = claims['exp']
            if (claims['iss'] != self.issuer or claims['aud'] != 'authenticated'
                    or claims.get('is_anonymous') is not False
                    or type(expires) is not int or expires <= time.time()
                    or type(claims.get('iat')) is not int or claims['iat'] > time.time() + 30):
                raise ValueError('Invalid claims')
            # Decoding is never authority. The real provider verifies signature,
            # project and identity on every protected transaction.
            user = self.request('GET', '/user', token=token)
            ban = user.get('banned_until')
            if ban and datetime.fromisoformat(ban.replace('Z', '+00:00')) > datetime.now(timezone.utc):
                raise ValueError('Banned individual')
            if (uuid(user['id']) != subject or user.get('is_anonymous') is not False
                    or not user.get('email_confirmed_at')):
                raise ValueError('Unverified individual')
            return subject, expires
        except (KeyError, ValueError, TypeError, AttributeError, UnicodeError, PermissionError):
            if denied is not None:
                denied.add(ref)
            raise PermissionError('Sign-in unavailable') from None

    def sign_in(self, email, password):
        if not isinstance(email, str) or not 3 <= len(email) <= 254 or not 1 <= len(password) <= 1024:
            raise PermissionError('Sign-in unavailable')
        result = self.request('POST', '/token?grant_type=password', body={'email': email, 'password': password})
        # Refresh tokens are intentionally discarded, never stored or logged.
        access = result.get('access_token')
        subject, expires = self.verify(access)
        return access, subject, expires

    def seal(self, token, *, session, subject):
        return self.cipher.encrypt(json.dumps({'issuer': self.issuer, 'subject': subject,
            'session': session, 'access': token}, sort_keys=True).encode()).decode('ascii')

    def open(self, sealed, *, session, subject):
        try:
            data = json.loads(self.cipher.decrypt(sealed.encode('ascii')))
            if (data['issuer'], data['subject'], data['session']) != (self.issuer, subject, session):
                raise ValueError('Envelope identity mismatch')
            return data['access']
        except (InvalidToken, ValueError, TypeError, KeyError, AttributeError, UnicodeError):
            raise PermissionError('Sign-in unavailable') from None


def binding_key(issuer, subject):
    from .security_store import digest
    return 'supabase:binding:' + digest(issuer + '\n' + uuid(subject))


def credential_key(session):
    return 'supabase:session:' + session


def read_binding(db, provider, subject):
    row = db.execute('SELECT value FROM meta WHERE key=?', (binding_key(provider.issuer, subject),)).fetchone()
    if not row:
        raise PermissionError('Sign-in unavailable')
    data = json.loads(row[0])
    if not isinstance(data, dict) or data.get('issuer') != provider.issuer or data.get('subject') != subject or data.get('active') is not True:
        raise PermissionError('Sign-in unavailable')
    return data['user_id']


def bind_offline(store, proposal, confirmation):
    """Explicit reviewed identity binding only; never creates principal or role.

    The operator must first independently recover/verify existing CIOS authority.
    The issue's missing production store must not be initialized by this tool.
    """
    from .security_store import canonical, digest
    provider = Provider.configured()
    required = {'issuer', 'subject', 'user_id', 'operator', 'approval_reference', 'active'}
    if (set(proposal) != required or proposal['issuer'] != provider.issuer
            or not proposal['operator'] or not proposal['approval_reference']
            or type(proposal['active']) is not bool or confirmation != digest(canonical(proposal))):
        raise ValueError('Confirm exact independently approved binding digest')
    key = binding_key(provider.issuer, proposal['subject'])
    with store.transaction() as db:
        if not db.execute('SELECT 1 FROM principals WHERE user_id=? AND enabled=1', (proposal['user_id'],)).fetchone():
            raise PermissionError('Existing enabled CIOS principal required')
        prior = db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        if prior and json.loads(prior[0])['user_id'] != proposal['user_id']:
            raise PermissionError('Identity reassignment requires separate recovery review')
        if prior and json.loads(prior[0]).get('active') is False and proposal['active']:
            raise PermissionError('Reactivation requires separate recovery review')
        for row in db.execute("SELECT value FROM meta WHERE key LIKE 'supabase:binding:%'"):
            existing = json.loads(row[0])
            if (existing['issuer'] == provider.issuer and existing['user_id'] == proposal['user_id']
                    and existing['subject'] != proposal['subject'] and existing['active'] and proposal['active']):
                raise PermissionError('One active provider individual per CIOS principal')
        db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)', (key, canonical(proposal)))
        db.execute('UPDATE tokens SET revoked=1 WHERE user_id=?', (proposal['user_id'],))
        return store.audit(db, 'supabase_binding_reviewed', **proposal)


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    from .security_store import SecurityStore
    parser = argparse.ArgumentParser(description='Bind an independently approved Supabase identity to EXISTING CIOS authority')
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--proposal', type=Path, required=True)
    parser.add_argument('--confirm', required=True)
    args = parser.parse_args()
    print(json.dumps({'audit_digest': bind_offline(SecurityStore(args.store), json.loads(args.proposal.read_text()), args.confirm)}))
