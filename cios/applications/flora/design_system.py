"""FLORA presentation primitives. No data ownership, matching or write authority.

Each scoped render owns its source/context buffers. No shared private cache;
reset happens on success and failure, including nested and concurrent renders.
"""
from contextvars import ContextVar
from functools import wraps
from html import escape as e
from pathlib import Path

ASSETS = Path(__file__).with_name('design_assets')
_view = ContextVar('flora_design_view', default=None)
from .navigation import PRIMARY
PRODUCT = tuple((href, label) for _, href, label in PRIMARY)


def view_scope(fn):
    @wraps(fn)
    def scoped(*args, **kwargs):
        state = _view.get()
        if state is not None:
            sources, context = len(state['sources']), len(state['context'])
            try:
                return fn(*args, **kwargs)
            except Exception:
                # A caught nested render failure must not publish partial notes.
                del state['sources'][sources:]; del state['context'][context:]
                raise
        token = _view.set({'sources': [], 'context': []})
        try:
            return fn(*args, **kwargs)
        finally:
            _view.reset(token)
    return scoped


def active():
    return _view.get() is not None


def source_note(html):
    """Called only on already-authorised, escaped presentation fragments."""
    state = _view.get()
    if state is None:
        return html  # Standalone/retained specialist rendering stays inspectable.
    if html and html not in state['sources']:
        state['sources'].append(html)
    return ''


def context_link(href, label):
    if not href.startswith('/') or href.startswith('//'):
        raise ValueError('Local contextual destination required')
    state = _view.get()
    if state is not None and (href, label) not in state['context']:
        state['context'].append((href, label))
    return ''


def asset(name):
    files = {'styles': ('design.css', 'text/css; charset=utf-8'),
             'interactions': ('design.js', 'text/javascript; charset=utf-8')}
    if name not in files:
        raise ValueError('Design asset unavailable')
    filename, mime = files[name]
    file = ASSETS / filename
    if file.is_symlink() or not file.resolve().is_relative_to(ASSETS.resolve()):
        raise ValueError('Design asset unavailable')
    return file.read_bytes(), mime


def head():
    return '<link rel="stylesheet" href="/design-system/assets/styles"><script defer src="/design-system/assets/interactions"></script>'


def section_scale(sic):
    """Same scoped 2024 extract as the approved Home, never a sub-sector total."""
    from .visual_v2 import basis
    data = basis(); row = next(r for r in data['districts'] if r['sic'] == sic)
    source = next(s for s in data['sources'] if s['id'] == row['source_id'])
    source_note('<p>' + e(row['label']) + ' is SIC 2007 section ' + e(sic) + '. Its ' + str(data['year'])
        + ' UK GVA share is for that whole section, not the narrower researched industry or its sales market. Current basic prices; rounded ONS weights, not a FLORA estimate.</p><a href="'
        + e(source['url'], quote=True) + '">' + e(source['title']) + '</a>')
    return '<p class="ds-economy-context"><strong>' + f"{row['weight_per_thousand']/10:.1f}%" + '</strong> ' + e(row['label']) + ' · share of UK GVA, ' + str(data['year']) + '</p>'


def header(active='home', account_html='', headers=None):
    if not account_html:
        from .access import blueprint_upload_authorisation
        from .web.app import _account_context_html
        account_html = _account_context_html(blueprint_upload_authorisation(headers or {}))
    state = _view.get() or {'sources': [], 'context': []}
    label = 'Explore'
    menu = ''; seen = {'/', '/pestle?market=GB'}
    for href, text in PRODUCT:
        if href not in seen:
            menu += '<a data-product-link="true" href="' + e(href, quote=True) + '">' + e(text) + '</a>'; seen.add(href)
    context = ''
    for href, text in state['context']:
        if href not in seen:
            context += '<a href="' + e(href, quote=True) + '">' + e(text) + '</a>'; seen.add(href)
    if context:
        menu += '<section class="view-links"><h2>In this view</h2>' + context + '</section>'
    menu += ('<details class="specialist-menu"><summary>Research & specialist tools</summary><div>'
        '<a href="/research">Research</a><a href="/blueprint-import/history">Import History</a><a href="/intelligence">Advanced intelligence</a><a href="/digital-twins">Canvas & Twins</a><a href="/financial-intelligence">Financial Intelligence</a><a href="/governance">Governance</a><a href="/settings">Settings</a></div></details>' + account_html)
    sources = ''.join(state['sources']) or '<p>Source periods, interpretation and material limitations remain with the existing view and its source owner.</p><a href="/research">Source research</a>'
    return ('<header class="product-header"><span class="wordmark">FLORA</span><nav aria-label="Primary product navigation">'
        '<a data-product-link="true" href="/"' + (' aria-current="page"' if active == 'home' else '') + '>Home</a>'
        '<a data-product-link="true" href="/pestle?market=GB"' + (' aria-current="page"' if active == 'pestle' else '') + '>PESTLE</a>'
        '<details class="product-menu" name="flora-header"><summary>' + label + '</summary><div class="menu-sheet">'
        + ('<p class="market-label">Selected market · United Kingdom</p>' if active in ('home','pestle') else '') + menu + '</div></details>'
        '<details class="sources-menu" name="flora-header"><summary>Sources & method</summary><section class="menu-sheet source-sheet" aria-label="Sources and methodology">'
        + sources + '</section></details></nav></header>')
