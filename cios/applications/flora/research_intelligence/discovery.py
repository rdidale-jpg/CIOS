"""Bounded newsroom discovery. Results are unverified research candidates."""
from dataclasses import dataclass
from datetime import date, timedelta
from hashlib import sha256
from html.parser import HTMLParser
import json
import re
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit

from .source_import import LIMIT
from .initial_factory import fingerprint

# Exact indices and narrow article paths are read perimeters, not publication grants.
NEWSROOMS = {
    'lloyds-banking-group-plc': (
        'Banking', 'Lloyds Banking Group', 'https://www.lloydsbankinggroup.com/media/press-releases.html',
        r'/media/press-releases/20\d\d/(?:lloyds-banking-group|lloyds)/[a-z0-9-]+\.html'),
    'bt-group-plc': ('Telecommunications', 'BT Group', 'https://newsroom.bt.com/',
                     r'/(?:bt|openreach|ee)-[a-z0-9-]+/'),
    'arm-holdings-plc': ('Technology', 'Arm', 'https://newsroom.arm.com/',
                         r'/(?:news|blog)/arm-[a-z0-9-]+'),
    'easyjet-plc': ('Aviation', 'easyJet', 'https://www.easyjet.com/en/news/',
                    r'/en/news/airline/story/easyjet-[a-z0-9-]+'),
}

MAX_ARTICLES = 8
TOPICS = {
    'Partnership': (r'\b(partner\w*|collaborat\w*|agreement)\b',
                    'Which party owns delivery, and what commitments are disclosed?'),
    'Technology change': (r'\b(digital|connectivity|ai|cloud|network|cpu|wi-fi)\b',
                          'Which services are affected, and is there a confirmed rollout?'),
    'Investment': (r'\b(invest\w*|funding|capital expenditure)\b',
                   'What has been committed, by whom, and over what period?'),
    'Expansion': (r'\b(expan\w*|new routes|launch\w*|roll-out)\b',
                  'Does the expansion create a confirmed operational requirement?'),
}


@dataclass(frozen=True)
class DiscoveryScope:
    industry: str
    publisher: str
    index: str
    article_path: str


SCALE_THEMES = {
    'Strategy and transformation': r'\b(strateg\w*|transform\w*|moderni[sz]\w*|expand\w*|initiative\w*)\b',
    'Technology and AI': r'\b(technology|digital|cloud|ai|network\w*|data centres?|software)\b',
    'Customers and suppliers': r'\b(customer\w*|supplier\w*|procure\w*|sourcing|supply chain)\b',
    'Contracts, partnerships and investment': r'\b(contract\w*|partner\w*|acqui\w*|invest\w*|agreement\w*)\b',
    'Competition and risks': r'\b(competit\w*|risk\w*|regulat\w*|resilien\w*|security|disrupt\w*)\b',
}


def scale_themes(text):
    return [name for name, pattern in SCALE_THEMES.items() if re.search(pattern, text, re.I)]


class NewsPage(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        if not raw or len(raw) > LIMIT:
            raise ValueError('Invalid document size')
        self.links = []
        self.link_labels = {}
        self.open_link = None
        self.properties = {}
        self.structured_dates = []
        self.structured_publishers = set()
        self.is_structured = False
        self.feed(raw.decode('utf-8-sig'))
        self.close()

    def issuer_agrees(self, scoped_publisher, url):
        # Metadata can corroborate the scoped publisher for pronoun binding.
        # Metadata alone cannot establish the scope or confer Source authority.
        return self.structured_publishers == {(scoped_publisher.casefold(), urlsplit(url).hostname)}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
            self.open_link = (attrs['href'], [])
        if tag == 'meta' and attrs.get('content'):
            key = attrs.get('property') or attrs.get('name') or attrs.get('itemprop')
            self.properties.setdefault(key, attrs['content'])
        if tag == 'ads-card' and attrs.get('link'):
            self.links.append(attrs['link'])
        if tag == 'script':
            self.is_structured = attrs.get('type') == 'application/ld+json'

    def handle_endtag(self, tag):
        if tag == 'a' and self.open_link:
            href, parts = self.open_link
            self.link_labels[href] = ' '.join(''.join(parts).split())
            self.open_link = None
        if tag == 'script':
            self.is_structured = False

    def handle_data(self, content):
        if self.open_link and not self.is_structured:
            self.open_link[1].append(content)
        if not self.is_structured:
            return
        try:
            value = json.loads(content)
        except (ValueError, RecursionError):
            return
        nodes = value if isinstance(value, list) else [value]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            graph = node.get('@graph', [])
            for entry in [node, *(graph if isinstance(graph, list) else [])]:
                if not isinstance(entry, dict):
                    continue
                kind = entry.get('@type')
                kinds = kind if isinstance(kind, list) else [kind]
                if any(t in ('Article', 'NewsArticle', 'BlogPosting') for t in kinds):
                    published = entry.get('datePublished')
                    if isinstance(published, str):
                        self.structured_dates.append(published)
                    publisher = entry.get('publisher')
                    if isinstance(publisher, dict) and publisher.get('@type') == 'Organization':
                        name, address = publisher.get('name'), publisher.get('url')
                        if isinstance(name, str) and isinstance(address, str):
                            try:
                                origin = urlsplit(address)
                            except ValueError:
                                continue
                            if (origin.scheme == 'https' and origin.hostname
                                    and origin.netloc == origin.hostname):
                                self.structured_publishers.add((' '.join(name.split()).casefold(),
                                                               origin.hostname))


def parse_date(value):
    prefix = value[:10]
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', prefix):
        try:
            return date.fromisoformat(prefix)
        except ValueError:
            pass
    return None


def article_urls(index, path_pattern, links):
    hostname = urlsplit(index).hostname
    urls = {}
    for href in links:
        url = urlsplit(urljoin(index, href))
        if (url.scheme == 'https' and url.netloc == hostname
                and re.fullmatch(path_pattern, url.path)
                and not re.search(r'quarter|\bresults\b|pension|annual-report|first-half|fixed-deposit-rate', url.path)):
            urls.setdefault(url._replace(query='', fragment='').geturl(), None)
    return list(urls)[:MAX_ARTICLES]


def scoped_article_urls(scope, page, limit):
    """Rank original article links using URL and anchor text within a frozen perimeter."""
    origin = urlsplit(scope.index)
    pattern = re.compile(scope.article_path)
    urls = {}
    duplicates = 0
    for link in page.links:
        try:
            target = urlsplit(urljoin(scope.index, link))
        except ValueError:
            continue
        path = target.path
        if (target.scheme != 'https' or target.netloc != origin.netloc or path == origin.path
                or any(char in path for char in ('%', chr(92)))
                or any(part in {'.', '..'} for part in path.split('/'))
                or not pattern.fullmatch(path)):
            continue
        clean = target._replace(query='', fragment='').geturl()
        themes = scale_themes(path.replace('-', ' ') + ' ' + page.link_labels.get(link, ''))
        if clean in urls:
            duplicates += 1
        if clean not in urls or len(themes) > len(urls[clean]):
            urls[clean] = themes
    # Prefer anchors covering a theme not already selected, then additional
    # signals and original publisher order. Thin indexes still get a sample.
    pending = list(urls)
    selected = []
    covered = set()
    while pending and len(selected) < limit:
        best = max(pending, key=lambda url: (len(set(urls[url]) - covered), len(urls[url])))
        pending.remove(best)
        selected.append(best)
        covered.update(urls[best])
    return selected, len(urls), duplicates


def discover(enterprise, fetch, *, as_of, previous=(), withdrawn=(), include_body=False,
             scope=None, max_articles=MAX_ARTICLES):
    """Read one original index and a bounded set of linked original HTML articles."""
    if scope is None:
        industry, publisher, index, pattern = NEWSROOMS[enterprise]
    else:
        industry, publisher, index = scope.industry, scope.publisher, scope.index
        origin = urlsplit(index)
        if (origin.scheme != 'https' or origin.netloc != origin.hostname
                or not origin.hostname or origin.query or origin.fragment
                or not 1 <= max_articles <= MAX_ARTICLES):
            raise ValueError('Expected an exact bounded HTTPS publisher scope')
    cutoff = date.fromisoformat(as_of)
    if cutoff > date.today():
        raise ValueError('Discovery cut-off cannot be in the future')
    withdrawn = set(withdrawn)
    failures, candidates = [], []
    previous_by_url = {row['url']: row for row in previous if row['enterprise_id'] == enterprise}

    def read(url):
        if url in withdrawn:
            failures.append({'url': url, 'reason': 'withdrawn'})
            return None
        try:
            raw, suffix = fetch(url)
            if suffix != '.html':
                raise ValueError('Not HTML')
            return NewsPage(raw), sha256(raw).hexdigest(), raw
        except HTTPError as exc:
            failures.append({'url': url, 'reason': 'publisher HTTP response', 'http_status': exc.code})
            return None
        except (OSError, ValueError, UnicodeError):
            failures.append({'url': url, 'reason': 'inaccessible or invalid HTML'})
            return None

    directory = read(index)
    discovered = duplicates = stale = no_topic = 0
    urls = []
    if directory:
        if scope is None:
            urls = article_urls(index, pattern, directory[0].links)
        else:
            urls, discovered, duplicates = scoped_article_urls(scope, directory[0], max_articles)
    for url in urls:
        article = read(url)
        if not article:
            continue
        page, digest, raw = article
        title = ' '.join(page.properties.get('og:title', '').split())
        dates = [page.properties.get(key, '') for key in
                 ('article:published_time', 'datePublished', 'publish-date')]
        publication_days = {day for value in dates + page.structured_dates if (day := parse_date(value))}
        if len(publication_days) > 1:
            failures.append({'url': url, 'reason': 'conflicting publication dates'})
            continue
        published = next(iter(publication_days), None)
        if not title or len(title) > 260 or not published or published > cutoff:
            failures.append({'url': url, 'reason': 'headline or publication date unresolved'})
            continue
        if published < cutoff - timedelta(days=90):
            stale += 1
            continue
        topics = [name for name, (pattern, _) in TOPICS.items() if re.search(pattern, title, re.I)]
        if scope is not None:
            topics = scale_themes(title + ' ' + urlsplit(url).path.replace('-', ' '))
        if not topics:
            no_topic += 1
            continue
        identity = fingerprint((enterprise, published.isoformat(), title.casefold()))
        prior = previous_by_url.get(url)
        state = 'new'
        if prior:
            state = 'unchanged' if prior['candidate_id'] == identity else 'conflicting metadata'
        candidate = {
            'candidate_id': identity, 'enterprise_id': enterprise, 'publisher': publisher,
            'industry': industry, 'url': url, 'published': published.isoformat(), 'title': title,
            'document_sha256': digest, 'locator': 'og:title with publication metadata',
            'status': state,
            'document_bytes_changed': prior['document_sha256'] != digest if prior else None,
            'evidence_class': 'publisher headline candidate',
            'themes': topics,
            'verification_questions': [TOPICS[name][1] for name in topics] if scope is None else [],
            'publication_eligible': False,
        }
        if include_body:
            from .assurance import screen_extracted
            from .body_claims import extract_claims
            candidate['body_claims'] = extract_claims(
                raw, enterprise=enterprise, url=url, digest=digest,
                published=published.isoformat(), publisher=publisher,
                issuer=publisher if page.issuer_agrees(publisher, url) else None)
            for claim in candidate['body_claims']:
                claim['assurance'] = screen_extracted(claim, raw, as_of=cutoff)
        candidates.append(candidate)

    unique = {}
    for candidate in candidates:
        key = candidate['candidate_id']
        if key not in unique or candidate['status'] == 'conflicting metadata':
            unique[key] = candidate
    result = {'enterprise_id': enterprise, 'as_of': as_of, 'index': index,
              'article_count': len(urls),
            'candidates': sorted(unique.values(), key=lambda row: row['published'], reverse=True),
            'failures': failures}
    if scope is not None:
        result['coverage'] = {'index_read': bool(directory), 'scoped_links': discovered,
                              'duplicate_links': duplicates, 'stale': stale, 'no_topic': no_topic,
                              'duplicate_headlines': len(candidates) - len(unique)}
    return result
