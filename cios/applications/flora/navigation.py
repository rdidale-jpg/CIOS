"""Presentation links only. Destination handlers retain their access checks."""
PRIMARY = (('home','/','Home'), ('industries','/industries','Industries'),
           ('enterprises','/enterprises','Enterprises'), ('opportunities','/opportunities','Opportunities'),
           ('pipeline','/flora/sales/pipeline','Pipeline'))


def primary_links(active=''):
    return ''.join(f"<a href='{url}'"+ (" aria-current='page'" if key==active else '')+f'>{label}</a>' for key,url,label in PRIMARY)


def specialist_tools():
    return "<details class='context-tools'><summary>Research & specialist tools</summary><nav aria-label='Specialist tools'><a href='/research'>Research</a> · <a href='/blueprint-import/history'>Import History</a> · <a href='/intelligence'>Advanced intelligence</a> · <a href='/digital-twins'>Canvas & governed Twins</a> · <a href='/financial-intelligence'>Financial Intelligence</a> · <a href='/governance'>Governance</a> · <a href='/settings'>Settings</a></nav><p>Destination permissions apply. These links do not grant access.</p></details>"


def compatibility_body(body, target, label='supporting intelligence'):
    from html import escape
    return (f"<aside class='card' data-legacy-compatibility='true'><strong>Retained {escape(label)} / compatibility view</strong>"
            f"<p>The unified experience is the primary entry point. Historical sources, scenarios and specialist detail remain available below.</p><a class='button-link' href='{escape(target,quote=True)}'>Open unified experience →</a></aside>"
            f"<details class='context-tools'><summary>Open retained {escape(label)}</summary>{body}</details>")
