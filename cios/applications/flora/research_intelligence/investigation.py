"""Bounded primary-source investigation for four existing research perimeters."""
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import re
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit

from .assurance import (
    Assertion, BoundEvidence, EvidenceRef, FactScope, assure, commercial_reading,
)
from .body_claims import BodyParagraphs
from .discovery import NEWSROOMS, NewsPage, parse_date

MAX_BYTES = 2 * 1024 * 1024
MAX_DOCUMENTS = 2
MAX_ATTEMPTS = 1 + MAX_DOCUMENTS

NOTICE = re.compile(
    r"^(?:Today at Microsoft Ignite 20\d\d, )?(?:we(?:['’]re| are)|Microsoft is) announcing (?:the )?general availability of "
    r"Azure Cobalt 200(?:-based)? virtual machines\b", re.I,
)
COUNTER = re.compile(
    r'\bAzure Cobalt 200(?:-based)? virtual machines (?:are not generally available|'
    r'have been withdrawn|will not be made available)\b', re.I,
)
CANDIDATE_TERMS = {
    'lloyds-banking-group-plc': 'responsible-ai',
    'bt-group-plc': 'swan',
    'arm-holdings-plc': 'cobalt-200',
    'easyjet-plc': 'starlink',
}


@dataclass(frozen=True)
class Perimeter:
    publisher: str
    entry: str
    document_path: str


PERIMETERS = {
    'lloyds-banking-group-plc': Perimeter(
        'Lloyds Banking Group', 'https://www.lloydsbankinggroup.com/who-we-are/group-overview/artificial-intelligence.html',
        r'/who-we-are/group-overview/artificial-intelligence/[a-z0-9-]+\.html'),
    'bt-group-plc': Perimeter(
        'NHS National Services Scotland', 'https://www.nss.nhs.scot/news/',
        r'/news/[a-z0-9-]+/'),
    'arm-holdings-plc': Perimeter('Microsoft Azure', 'https://azure.microsoft.com/en-us/blog/',
                                 r'/en-us/blog/[a-z0-9-]+/'),
    'easyjet-plc': Perimeter('easyJet', 'https://www.easyjet.com/en/news/airline',
                            r'/en/news/airline/story/easyjet-[a-z0-9-]+'),
}


def _links(page, perimeter, term):
    host = urlsplit(perimeter.entry).netloc
    matches = set()
    for link in page.links:
        try:
            target = urlsplit(urljoin(perimeter.entry, link))
        except ValueError:
            continue
        if (target.scheme == 'https' and target.netloc == host
                and re.fullmatch(perimeter.document_path, target.path)
                and term in target.path):
            matches.add(target._replace(query='', fragment='').geturl())
    return sorted(matches, key=lambda url: ('available' not in url, url))[:MAX_DOCUMENTS]


def _notice_observations(raw, url, digest, page, assertion, cutoff):
    """The publisher can substantiate the occurrence of its own exact notice."""
    dates = [page.properties.get('article:published_time', ''), *page.structured_dates]
    days = {day for value in dates if (day := parse_date(value))}
    expected = date.fromisoformat(assertion.scope.period)
    if len(days) != 1 or max(days) > cutoff or max(days) < expected:
        return [], 'publication date differs from the scoped notice'
    observed = max(days)
    parser = BodyParagraphs()
    parser.feed(raw.decode('utf-8-sig'))
    parser.close()
    observations = []
    for index, paragraph in parser.paragraphs:
        for name, pattern in [('counterclaim', COUNTER), ('notice', NOTICE)]:
            if not pattern.search(paragraph) or (name == 'notice' and observed != expected):
                continue
            if name == 'counterclaim' and observed > expected:
                name = 'later_update'
            evidence = assertion if name == 'notice' else Assertion(
                assertion.scope, 'cancelled', 'status', 'Microsoft reports that Cobalt 200 availability was withdrawn.')
            # A counterclaim blocks the projection even if the assurance field
            # for a publication event cannot encode withdrawal as its value.
            observations.append((name, BoundEvidence(
                EvidenceRef(url, digest, f'body p{index}'), evidence, 'Microsoft Azure',
                'Microsoft announcement', 'official', observed)))
    state = ('publication date differs from the scoped notice' if observed != expected and not observations
             else 'examined original publisher body')
    return observations, state



def matches_candidate(candidate, term):
    if term in urlsplit(candidate['url']).path:
        return True
    expression = r'\b' + re.escape(term.replace('-', ' ')) + r'\b'
    return any(re.search(expression, value, re.I) for value in (
        candidate.get('title', ''),
        *(claim.get('excerpt', '') for claim in candidate.get('body_claims', ())),
    ))


def investigate(candidate, fetch, *, as_of, current_revisions=None, withdrawn=()):
    """Acquire only allowlisted originals. No Source admission or publication."""
    enterprise = candidate['enterprise_id']
    perimeter = PERIMETERS[enterprise]
    term = CANDIDATE_TERMS[enterprise]
    candidate_url = candidate['url']
    original = urlsplit(candidate_url)
    _, _, newsroom, path_pattern = NEWSROOMS[enterprise]
    if (candidate.get('publication_eligible') is not False
            or as_of > date.today()
            or candidate.get('status') == 'conflicting metadata'
            or date.fromisoformat(candidate['published']) > as_of
            or original.scheme != 'https' or original.netloc != urlsplit(newsroom).netloc
            or original.query or original.fragment
            or not re.fullmatch(path_pattern, original.path) or not matches_candidate(candidate, term)):
        raise ValueError('Expected the scoped discovery candidate')
    excluded = set(withdrawn)
    audit = []
    found = []
    attempts = 0

    def read(url):
        nonlocal attempts
        if url in excluded:
            audit.append({'url': url, 'state': 'withdrawn'})
            return None
        if attempts >= MAX_ATTEMPTS:
            return None
        attempts += 1
        try:
            raw, suffix = fetch(url, MAX_BYTES)
            if suffix != '.html' or len(raw) > MAX_BYTES:
                raise ValueError('Original HTML exceeds budget or media scope')
            return raw, NewsPage(raw)
        except HTTPError as exc:
            audit.append({'url': url, 'state': 'unavailable', 'http_status': exc.code})
        except (OSError, ValueError):
            audit.append({'url': url, 'state': 'unavailable'})
        return None

    assertion = None
    if enterprise == 'arm-holdings-plc':
        assertion = Assertion(FactScope(
            enterprise, 'microsoft', 'azure-cobalt-200', 'publisher_notice',
            'Microsoft announcement of Azure Cobalt 200 availability', candidate['published']),
            'announced', 'status', 'Microsoft announced general availability of Azure Cobalt 200 virtual machines.')
    entry = read(perimeter.entry) if candidate_url not in excluded else None
    if candidate_url in excluded:
        audit.append({'url': candidate_url, 'state': 'withdrawn'})
    if entry:
        audit.append({'url': perimeter.entry, 'state': 'searched index',
                      'sha256': sha256(entry[0]).hexdigest()})
        for url in _links(entry[1], perimeter, term):
            if url == candidate_url:
                audit.append({'url': url, 'state': 'same document as discovery'})
                continue
            retrieved = read(url)
            if retrieved is None:
                continue
            raw, page = retrieved
            digest = sha256(raw).hexdigest()
            check = {'url': url, 'sha256': digest, 'publisher': perimeter.publisher,
                     'state': 'related material; no exact scoped support'}
            if assertion:
                observations, check['state'] = _notice_observations(raw, url, digest, page, assertion, as_of)
                found.extend(observations)
            audit.append(check)

    report = {
        'candidate_id': candidate['candidate_id'], 'enterprise_id': enterprise,
        'starting_state': 'withheld' if assertion else 'attributed_only',
        'factual_state': 'withheld' if assertion or candidate_url in excluded else 'attributed_only',
        'attempts': attempts, 'maximum_attempts': MAX_ATTEMPTS,
        'maximum_bytes_per_response': MAX_BYTES, 'paid_searches': 0,
        'audit': audit, 'publication_eligible': False,
        'source_relationship': 'No qualifying source relationship established',
        'commercial_reading': {'confirmed_development': None, 'buyer_questions': []},
    }
    if assertion:
        # Fresh reads count for offline factual review only. In a persisted
        # workspace the caller must supply owner-maintained current revisions.
        active = ({(row.reference.url, row.reference.digest) for _, row in found}
                  if current_revisions is None else current_revisions)
        seen = [{'kind': kind, 'reference': asdict(row.reference),
                 'observed_on': row.observed_on.isoformat()} for kind, row in found]
        blockers = {kind for kind, row in found
                    if kind != 'notice' and (row.reference.url, row.reference.digest) in active}
        eligible = [row for kind, row in found if kind == 'notice' and not blockers]
        decision = assure(assertion, eligible, current_revisions=active, as_of=as_of)
        report.update(observations=seen, assurance=decision,
                      factual_state='conflict' if 'counterclaim' in blockers else decision['factual_state'],
                      material_updates=sorted(blockers))
        if not blockers:
            report['commercial_reading'] = commercial_reading(decision)
        if report['factual_state'] == 'verified':
            report['source_relationship'] = 'Microsoft confirms publication of its own notice'
    return report
