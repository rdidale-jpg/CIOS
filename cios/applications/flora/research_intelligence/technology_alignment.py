"""Technology presentation over the existing finite research experience."""
from html import escape
from urllib.parse import urlencode

from .. import reading_views

ALIGNED = frozenset(('', '/district', '/participants', '/enterprise', '/operating-model'))


def address(path, query, reading):
    context = {key: value for key, value in query.items() if key != 'reading' and value}
    if reading == 'insight':
        context['reading'] = reading
    return path + ('?' + urlencode(context) if context else '') + '#technology-main'


def frame(path, suffix, query, body):
    from . import technology_experience as x
    reading = query.get('reading', 'facts')
    district = query.get('district') or query.get('selected') or (
        'cloud' if suffix in ('/district', '/operating-model') else '')
    parts = [x.link('/', 'UK'), x.link(x.BASE, 'Technology')]
    if district:
        parts.append(x.link(x.url('/district', district=district), x.DISTRICTS[district][0]))
    if suffix in ('/enterprise', '/operating-model'):
        foundation, _ = x.research.load()
        key = query.get('enterprise') or 'equinix'
        label = next(row['label'] for row in foundation['providers'] if row['key'] == key)
        parts.append(escape(label))
    perspective = 'Inside' if suffix == '/operating-model' else 'Landscape'
    controls = x.link(address(x.BASE + suffix, query, reading), perspective, aria_current='page')
    if suffix == '/operating-model':
        controls = x.link(x.url('/enterprise', enterprise='equinix'), 'Landscape') + controls
    elif suffix == '/enterprise' and query.get('enterprise', 'equinix') == 'equinix':
        controls += x.link(x.url('/operating-model'), 'Inside')
    modes = '<nav class="reading-mode" aria-label="Reading mode">' + ''.join(
        x.link(address(path, query, mode), label, **({'aria_current': 'page'} if reading == mode else {}))
        for mode, label in (('facts', 'Facts'), ('insight', 'FLORA Insight'))
    ) + '</nav>'
    navigation = '<nav class="t1-links" aria-label="Technology context">' + ''.join(
        x.link(href, label) for href, label in (
            (x.url('/participants'), 'Compare participants'),
            (x.research.BASE + '/providers', 'Provider directory'),
            (x.url('/enterprise', enterprise='nvidia', district='ai'), 'NVIDIA'),
            (x.url('/enterprise', enterprise='equinix', district='cloud'), 'Equinix'),
            (x.research.BASE + '?lens=uses', 'Programmes & relationships'),
            (x.research.BASE + '/evidence', 'Sources & research'),
        )
    ) + '</nav>'
    if suffix == '':
        artwork = x.scene(query.get('selected', ''), heading=False)
    elif suffix == '/enterprise':
        artwork = x.link(x.BASE, 'Explore the Technology landscape', class_='t1-map-link')
    else:
        artwork = (x.link(x.BASE, 'Explore the Technology landscape', class_='t1-map-link')
                   + f'<img src="{x.ASSET_BASE}artwork" alt="" width="1536" height="1024">')
    return (reading_views.STYLE + '<div class="t1">'
            '<header data-region="top"><nav aria-label="Current scope">' + ' / '.join(parts) + '</nav>'
            '<nav class="t1-perspective" aria-label="Perspective">' + controls + '</nav></header>'
            '<div class="t1-layout"><aside data-region="left" aria-label="Technology landscape">'
            + artwork + navigation + '</aside><section data-region="main" id="technology-main" tabindex="-1"'
            f' aria-label="Technology {perspective}" data-reading="{reading}">'
            + modes + body + '</section></div></div>')
