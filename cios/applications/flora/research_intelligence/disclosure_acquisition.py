"""Bounded acquisition of reviewed factual bindings from original publishers."""
import hashlib
import re
from ssl import SSLError
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from .commercial_factory import active, usable_url
from .source_import import extract
from .initial_factory import fingerprint

# Public acquisitions only. These hosts confer no publication or write authority.
PUBLISHERS = frozenset({
    'www.lloydsbankinggroup.com', 'www.fca.org.uk', 'www.bt.com', 'newsroom.bt.com',
    'www.nokia.com', 'newsroom.arm.com', 'corporate.easyjet.com', 'www.airbus.com',
    'www.find-tender.service.gov.uk', 'www.gov.uk',
})


# This shared issuer CDN is only trusted for the previously verified report tenant.
REPORT_TENANTS = {'s203.q4cdn.com': '/522538739/files/doc_financials/'}


def known_publisher(url):
    target = urlsplit(url)
    tenant = REPORT_TENANTS.get(target.hostname)
    return (target.hostname in PUBLISHERS
            or bool(tenant and target.path.startswith(tenant)
                    and re.fullmatch(r'/[A-Za-z0-9_/-]+\.pdf', target.path)
                    and not target.query))


def normalise(text):
    return ' '.join(re.findall(r'[\w%]+', text.casefold()))


def acquire_disclosures(sources, fetch):
    """Validate each bound fact against an exact approved URL and a local passage.

    A fetch failure may retain explicitly labelled replay. A changed document
    that no longer supports a fact must never fall back to that fact's replay.
    """
    if len(sources) > 16:
        raise ValueError('Commercial acquisition exceeds the commissioned document budget')
    cache = {}
    result = []
    for source in sources:
        if not active(source):
            result.append(source)
            continue
        binding = {k: v for k, v in source.items() if k not in {'sha256', 'status', 'withdrawn'}}
        url = source.get('acquisition_url', source['url'])
        if (fingerprint(binding) != source['sha256'] or not usable_url(url)
                or not known_publisher(url)
                or urlsplit(url).hostname != urlsplit(source['url']).hostname):
            result.append(dict(source, status='restricted'))
            continue
        if url not in cache:
            try:
                raw, suffix = fetch(url)
                cache[url] = normalise(extract(raw, suffix)), hashlib.sha256(raw).hexdigest()
            except HTTPError as exc:
                cache[url] = None if exc.code in {429, 500, 502, 503, 504} else ('', '')
            except URLError as exc:
                cache[url] = ('', '') if isinstance(exc.reason, SSLError) else None
            except SSLError:
                cache[url] = '', ''
            except OSError:
                cache[url] = None
            except (ValueError, UnicodeError):
                cache[url] = '', ''
        material = cache[url]
        if material is None:
            result.append(source)
            continue
        text, digest = material
        claims = []
        for claim in source['claims']:
            anchors = [normalise(anchor) for anchor in claim.get('anchors', ())]
            if not anchors or not all(anchors):
                continue
            # All bounded cues must occur together, not in unrelated sections.
            if any(all(anchor in text[m.start():m.start() + 2200] for anchor in anchors)
                   for m in re.finditer(re.escape(anchors[0]), text)):
                claims.append(claim)
        captured = {**binding, 'claims': claims, 'live_content_sha256': digest}
        result.append(dict(captured, sha256=fingerprint(captured),
                           status='current' if claims else 'restricted'))
    return result
