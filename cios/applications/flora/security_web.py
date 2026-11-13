"""Small browser boundary. No public provisioning or administration routes."""
from __future__ import annotations
from html import escape
import os
import re
import sqlite3
from urllib.parse import parse_qs, urlsplit

from .security_store import SecurityStore, COOKIE, PREAUTH, cookie_token, session_cookie

CSRF_COOKIE = '__Host-flora_csrf'
AUTH_PATHS = {'/auth/sign-in','/auth/enroll','/auth/workspace','/auth/sign-out'}


def origin_valid(headers):
    origin = os.getenv('FLORA_PUBLIC_ORIGIN','')
    parsed = urlsplit(origin)
    return bool(origin and parsed.scheme == 'https' and parsed.hostname and not parsed.username
                and not parsed.password and not parsed.path and not parsed.query and not parsed.fragment
                and headers.get('Origin','') == origin)


def clean_target(handler):
    words = handler.requestline.split()
    parsed = urlsplit(handler.path)
    return bool(len(words)==3 and words[1]==handler.path and not parsed.scheme and not parsed.netloc
                and not parsed.fragment and not re.search(r'[%\\;\x00-\x20\x7f]',parsed.path)
                and '//' not in parsed.path and all(p not in {'.','..'} for p in parsed.path.split('/')))


def page(title, content):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><style>body{{font:18px system-ui;max-width:40rem;margin:2rem auto;padding:1rem}}input,select,button{{font:inherit;display:block;max-width:100%;padding:.7rem;margin:.7rem 0}}label{{display:block}}a{{display:inline-block;padding:.6rem}}</style></head><body><a href="/flora">Flora</a><h1>{escape(title)}</h1>{content}</body></html>'''


def form(path, csrf, content, label):
    return f'<form method="post" action="{path}"><input type="hidden" name="csrf" value="{escape(csrf)}">{content}<button type="submit">{escape(label)}</button></form>'


def auth_get(handler, path):
    store = SecurityStore()
    try:
        if path in {'/auth/sign-in','/auth/enroll','/pilot-sign-in'}:
            token, csrf = store.preauth()
            if path == '/auth/enroll':
                title='Set your password'
                fields='<label>Private enrollment token<input name="enrollment_token" autocomplete="off" required></label><label>New password (at least 15 characters)<input type="password" name="password" minlength="15" maxlength="1024" autocomplete="new-password" required></label>'
                target='/auth/enroll'
            else:
                title='Sign in'
                fields='<label>Account identifier<input name="user_id" autocomplete="username" required></label><label>Password<input type="password" name="password" autocomplete="current-password" required></label><p><a href="/auth/enroll">Use a private enrollment token</a></p>'
                target='/auth/sign-in'
            handler._html(page(title,form(target,csrf,fields,title)),set_cookie=[session_cookie(token,PREAUTH,600),session_cookie(csrf,CSRF_COOKIE,600)])
        elif path == '/auth/workspace':
            csrf=cookie_token(handler.headers,CSRF_COOKIE)
            choices=store.choices(cookie_token(handler.headers))
            fields='<label>Workspace<select name="workspace_id" required>'+''.join(f'<option value="{escape(w)}">{escape(w)}</option>' for w in choices)+'</select></label>'
            content=form(path,csrf,fields,'Select workspace') if choices else '<p>No active workspace membership. Contact your deployment operator.</p>'
            handler._html(page('Select workspace',content+form('/auth/sign-out',csrf,'','Sign out')))
        else:
            handler._html(page('Sign out',form('/auth/sign-out',cookie_token(handler.headers,CSRF_COOKIE),'','Sign out')))
    except (OSError,sqlite3.Error):
        handler._html(page('Privileged operations disabled','<p>Security storage unavailable. Public Banking remains readable.</p><a href="/auth/sign-in">Sign In</a>'),status=200 if path == '/pilot-sign-in' else 503)
    except PermissionError:
        handler._html(page('Session unavailable','<p>Your session is unavailable or expired. <a href="/auth/sign-in">Sign in</a></p>'),status=403)


def read_form(handler, maximum=1024*1024):
    if handler.headers.get('Transfer-Encoding') or len(handler.headers.get_all('Content-Length',[])) != 1:
        raise PermissionError('Invalid request framing')
    length=int(handler.headers.get('Content-Length','0'))
    if length < 0 or length > maximum:
        raise PermissionError('Request too large')
    raw=handler.rfile.read(length)
    if len(raw) != length:
        raise PermissionError('Incomplete request')
    if 'multipart/form-data' in handler.headers.get('Content-Type',''):
        from .web.app import _parse_multipart
        fields,_=_parse_multipart(handler.headers,raw)
        return raw,{k:[v] for k,v in fields.items()}
    if handler.headers.get('Content-Type','').split(';')[0] != 'application/x-www-form-urlencoded':
        raise PermissionError('Unsupported request format')
    return raw,parse_qs(raw.decode('utf-8'),keep_blank_values=True,max_num_fields=200)


def one(fields,key):
    values=fields.get(key,[])
    if len(values)!=1:
        raise PermissionError('Request verification failed')
    return values[0]


def auth_post(handler,path):
    store=SecurityStore()
    _,fields=read_form(handler,16384)
    csrf=one(fields,'csrf')
    if path == '/auth/enroll':
        store.enroll(one(fields,'enrollment_token'),one(fields,'password'),cookie_token(handler.headers,PREAUTH),csrf)
        handler._redirect('/auth/sign-in',set_cookie=session_cookie('',PREAUTH,0))
    elif path == '/auth/sign-in':
        token,csrf=store.login(one(fields,'user_id'),one(fields,'password'),cookie_token(handler.headers,PREAUTH),csrf)
        handler._redirect('/auth/workspace',set_cookie=[session_cookie(token),session_cookie(csrf,CSRF_COOKIE),session_cookie('',PREAUTH,0)])
    elif path == '/auth/workspace':
        token,csrf=store.select(cookie_token(handler.headers),csrf,one(fields,'workspace_id'))
        handler._redirect('/blueprint-import/history',set_cookie=[session_cookie(token),session_cookie(csrf,CSRF_COOKIE)])
    elif path == '/auth/sign-out':
        store.logout(cookie_token(handler.headers),csrf)
        handler._redirect('/flora',set_cookie=[session_cookie('',COOKIE,0),session_cookie('',CSRF_COOKIE,0)])
    else:
        raise PermissionError('Route unavailable')


def private_read(handler):
    """Only existing handlers with resource-level guards are reachable."""
    if not clean_target(handler):
        return False
    parsed=urlsplit(handler.path)
    from .security import verified_context
    from .access import require_capability
    context=verified_context(handler.headers)
    if context is None:
        return False
    ident=r'[A-Za-z0-9][A-Za-z0-9_.:@-]{0,127}'
    path=parsed.path
    if path in {'/blueprint-import','/blueprint-import/history','/digital-twins'} or re.fullmatch(r'/blueprint-import/'+ident+r'(?:/(?:inspect|review|promote|intelligence|explore|health|research-brief|diagnostics|mission|restage|staging-history|archive|cancel|delete)|/aspects/'+ident+r'|/enterprises/'+ident+r')?',path):
        require_capability(handler.headers,'package.inspect')
        return True
    if re.fullmatch(r'/digital-twins/'+ident+r'/(?:canvas(?:/tiles/'+ident+r'(?:/lineage)?)?|executive-intelligence-brief)',path):
        # Existing Canvas service enforces its independent resource ACL.
        return True
    if re.fullmatch(r'/ai-financial-report/'+ident,path):
        from .document_review import read_run
        try:
            read_run(path.rsplit('/',1)[1], headers=handler.headers)
            return True
        except (OSError, ValueError, PermissionError):
            return False
    if path in {'/flora/sales/pipeline', '/flora/sales/new'} or re.fullmatch(r'/flora/sales/opp-[a-f0-9]{32}', path):
        require_capability(handler.headers, 'commercial_context.view')
        return True
    from .offers import READ_PATHS
    if path in READ_PATHS:
        require_capability(handler.headers, 'commercial_context.view')
        return True
    if path == '/settings/general':
        require_capability(handler.headers,'package.inspect')
        return True
    if path == '/operations/storage-recovery':
        require_capability(handler.headers,'storage.recover')
        return True
    return False


def mutation_capability(path):
    from .offers import WRITE_PATHS
    if path in WRITE_PATHS: return 'commercial_context.edit'
    ident=r'[A-Za-z0-9][A-Za-z0-9_.:@-]{0,127}'
    if path in {'/flora/sales/capture', '/flora/sales/create'} or re.fullmatch(r'/flora/sales/opp-[a-f0-9]{32}/save', path): return 'commercial_context.edit'
    if path=='/operations/storage-recovery': return 'storage.recover'
    if path=='/blueprint-import/upload': return 'package.upload'
    if re.fullmatch(r'/blueprint-import/'+ident+r'/(?:approve)',path): return 'candidate.promote'
    if re.fullmatch(r'/blueprint-import/'+ident+r'/(?:prepare-review|mark-reviewed|reviews|evidence-mapping|identity|stage|restage|researcher-observation|mission|decline|cancel|delete)',path): return 'package.review'
    if re.fullmatch(r'/digital-twins/'+ident+r'/executive-intelligence-brief/generate',path): return 'package.review'
    if re.fullmatch(r'/digital-twins/'+ident+r'/canvas/feedback',path): return 'commercial_context.edit'
    if re.fullmatch(r'/ai-financial-report/'+ident+r'/review',path): return 'package.review'
    if re.fullmatch(r'/ai-financial-report/'+ident+r'/apply',path): return 'candidate.promote'
    return ''


def decorate_forms(html,headers):
    csrf=cookie_token(headers,CSRF_COOKIE)
    if not csrf:
        return html
    # Supply session-bound CSRF to existing same-origin forms without scripts.
    hidden=f'<input type="hidden" name="csrf" value="{escape(csrf)}">'
    def decorate(match):
        text = match[0]
        if re.search(r"name\s*=\s*['\"]csrf['\"]", text, re.I):
            return text
        return text.replace('>', '>' + hidden, 1)
    return re.sub(r"<form\b[^>]*\bmethod\s*=\s*['\"]post['\"][^>]*>.*?</form\s*>", decorate, html, flags=re.I | re.S)


def scoped_settings_page(headers):
    """Only the verified selected membership; no disk roots or global metadata."""
    from .access import require_capability
    context = require_capability(headers, 'package.inspect')
    content = ('<p>Selected workspace: ' + escape(context.workspace) + '</p>'
               '<p>Signed in as: ' + escape(context.user_id) + '</p>'
               '<p>Active membership: verified</p>'
               '<p>Available capabilities: ' + escape(', '.join(sorted(context.effective_capabilities))) + '</p>'
               '<p>Private resources also require their existing ACL and exact workspace scope.</p>'
               '<a href="/auth/workspace">Choose workspace</a>')
    return page('Workspace access settings', content)
