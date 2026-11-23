"""Extract bounded, attributed event candidates from publisher HTML paragraphs."""
from html.parser import HTMLParser
import re

from .initial_factory import fingerprint

# Ordered, asymmetric rules. A plan to launch must not appear as a launch.
EVENTS = (
    ('partnership', 'announced', r'(?:has )?(?:partnered|partners) with|(?:formed|announced) a partnership with|(?:signed|entered into) (?:an? )?agreement with'),
    ('supplier selection', 'announced', r'(?:has )?(?:selected|appointed)'),
    ('supply', 'planned', r'will supply'),
    ('investment', 'announced', r'(?:announced|committed to) (?:an? )?investment (?:in|of)|(?:has )?invested in'),
    ('availability', 'available', r'(?:announced|announcing) the general availability of'),
    ('rollout', 'planned', r'(?:plans? to|will) (?:start to |begin to )?(?:deploy|roll out|introduce)'),
    ('rollout', 'planned', r'will (?:be deployed|be rolled out)'),
    ('rollout', 'completed', r'(?:has )?completed|announces? the completion of'),
    ('rollout', 'delayed', r'(?:has )?(?:delayed|postponed)'),
    ('rollout', 'cancelled', r'(?:has )?cancelled'),
    ('announcement', 'announced', r'(?:has )?(?:published|announced|unveiled|introduced|launched)'),
)
RULES = tuple((kind, status, re.compile(
    r'^(?P<actor>[^.;:]{2,85}?)\s+(?:' + verb + r')(?:\s+(?P<object>[^.;:]+))?[.!?]?$',
    re.I)) for kind, status, verb in EVENTS)
DATE = re.compile(
    r'\b(?:20\d\d-\d\d-\d\d|(?:\d{1,2} )?(?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d|(?:the )?(?:first|second) half of 20\d\d|(?:early |late )?20\d\d)\b',
    re.I)
UNCERTAIN = re.compile(r"\b(?:not|never|may|might|could|if|whether|reportedly|considering)\b|n['’]t\b", re.I)
NAME = re.compile(r'[A-Z][\w&-]*(?:\s+(?:[A-Z][\w&-]*|of|for|the|and))*')

# Local semantic recovery for bounded announcement and event clauses.
MONTH = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
DATELINE_DATE = rf'{MONTH} \d{{1,2}}, 20\d{{2}}'
DATELINE = re.compile(
    rf'^(?:[A-Z][\w .’\'-]{{1,32}})(?:, [A-Z][\w .’\'-]{{1,25}})?'
    rf'\s+[-–—]\s+(?:(?P<date>{DATELINE_DATE})\s+(?:[-–—]\s+)?|(?=[A-Z]))'
)
ENTITY = r"[A-Z][\w&'’.‑-]*(?: (?:[A-Z][\w&'’.‑-]*|of|for|and|the))*?"
SUBJECT = (
    rf'(?P<actor>{ENTITY})(?: \([A-Z][A-Z0-9 ]{{1,11}}: [A-Z0-9. -]{{1,15}}\))?'
    rf'(?:, (?:an?|the) [^,.;:!?]{{3,85}},)?'
)
ANNOUNCE = r'(?:today )?(?:announces?|announced)'
NESTED = re.compile(rf'^{SUBJECT} {ANNOUNCE} (?:that )?(?P<clause>.+)$')
VALUE = r'(?:approximately |about |up to |at least )?(?:[€£$]\d+(?:[.,]\d+)*|\d+(?:[.,]\d+)* (?:EUR|GBP|USD))(?: (?:thousand|million|billion))?(?: (?:annually|per year))?'
EVENT_CLAUSES = (
    ('acquisition', 'completed', 'acquired entity',
     r'(?:has )?completed (?:its |the )?acquisition of', rf'(?P<target>{ENTITY})(?=,|[.!?]?$)'),
    ('donation', 'planned', 'recipient',
     rf'(?:{ANNOUNCE} )?plans? to donate',
     rf"(?P<value>{VALUE}) to (?:{ENTITY}’s )?(?P<target>{ENTITY})(?=,|[.!?]?$)"),
    ('research collaboration', 'committed', 'collaborator',
     r'(?:has )?committed to (?:continue and increase|expand|continue) (?:its )?(?:R&D|research) collaboration with',
     rf'(?P<target>{ENTITY})(?:, focusing on projects worth (?P<value>{VALUE})'
     r'(?= across\b|,|$)|(?=,|$))'),
    ('portfolio expansion', 'announced', None,
     rf'{ANNOUNCE} (?:a )?(?:major )?expansion of',
     r'(?:its |the )?(?P<target>portfolio)(?=,|[.!?]?$)'),
    ('migration', 'in progress', None,
     r'is migrating to', r'(?P<target>[^,;.!?]{3,140})(?=,|[.!?]?$)'),
    ('announcement', 'announced', None,
     r'(?:today )?published', r'(?P<target>[^,;.!?]{4,140})(?=,|[.!?]?$)'),
)
SENTENCE_BREAK = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
SPAN_LOCATOR = re.compile(r'body p(\d+), sentence (\d+), chars (\d+)–(\d+)')

SEMANTIC_RULES = tuple((kind, status, role, re.compile(rf'^{SUBJECT} {verb} {target}'))
                       for kind, status, role, verb, target in EVENT_CLAUSES)


def semantic_clause(sentence):
    """Extract one narrow event assertion, anchored to its exact displayed text."""
    dateline = DATELINE.match(sentence)
    if dateline and not (dateline['date'] or dateline[0].isupper()):
        dateline = None
    offset = dateline.end() if dateline else 0
    prefix = re.match(r'In parallel, ', sentence[offset:])
    if prefix:
        offset += prefix.end()
    text = sentence[offset:].rstrip('.!?')
    # A nested issuer statement can name a different actor. Resolve only an
    # explicit entity or the grammatical subject pronoun within this wrapper.
    nested = NESTED.fullmatch(text)
    interpretations = [(text, offset, None)]
    if nested:
        clause = nested['clause']
        start = offset + nested.start('clause')
        if clause.startswith('it '):
            start += 3
            interpretations.append((nested['actor'] + ' ' + clause[3:], start, nested['actor']))
        elif clause[0].isupper():
            interpretations.append((clause, start, None))
    for interpretation, start, substituted in interpretations:
        for kind, status, role, rule in SEMANTIC_RULES:
            match = rule.match(interpretation)
            if match is None or (kind == 'announcement' and dateline is None):
                continue
            stop = start + match.end() - (len(substituted) + 1 if substituted else 0)
            excerpt = sentence[offset:stop]
            target = match['target']
            value = match.groupdict().get('value')
            dates = [found.group().casefold().removeprefix('the ') for found in DATE.finditer(excerpt)]
            if dateline and dateline['date']:
                dates.insert(0, dateline['date'].casefold())
            return (kind, status, match['actor'], target, dates, [value] if value else [],
                    [{'name': target, 'role': role}] if role else [], offset, stop)
    return None


class BodyParagraphs(HTMLParser):
    """Count HTML body paragraphs, including skipped paragraphs for stable locators."""
    def __init__(self):
        super().__init__()
        self.body = False
        self.ignored = []
        self.paragraph = None
        self.paragraphs = []
        self.ordinal = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.body = True
        if tag in {'script', 'style', 'nav', 'footer', 'header', 'aside', 'template', 'noscript'}:
            self.ignored.append(tag)
        if tag == 'p' and self.body:
            self.ordinal += 1
            self.paragraph = None if self.ignored else []

    def handle_data(self, data):
        if self.paragraph is not None and not self.ignored:
            self.paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == 'body':
            self.body = False
            self.paragraph = None
        if self.ignored and tag == self.ignored[-1]:
            self.ignored.pop()
        if tag == 'p' and self.paragraph is not None:
            self.paragraphs.append((self.ordinal, ' '.join(''.join(self.paragraph).split())))
            self.paragraph = None


def body_paragraphs(raw):
    parser = BodyParagraphs()
    parser.feed(raw.decode('utf-8-sig'))
    parser.close()
    return parser.paragraphs


def excerpt_at_span(raw, locator):
    """Return display text at a zero-based, end-exclusive sentence span."""
    match = SPAN_LOCATOR.fullmatch(locator)
    if match is None:
        return None
    paragraph, number, start, stop = map(int, match.groups())
    for index, text in body_paragraphs(raw):
        if index == paragraph:
            sentences = SENTENCE_BREAK.split(text)
            if 1 <= number <= len(sentences) and 0 <= start < stop <= len(sentences[number - 1]):
                return sentences[number - 1][start:stop]
            break
    return None


def semantic_spans(sentence):
    # A named subject must be explicit on each side of a semicolon.
    for part in re.finditer(r'[^;]+', sentence):
        statement = part[0].strip()
        if not 25 <= len(statement) <= 640 or UNCERTAIN.search(statement):
            continue
        if (clause := semantic_clause(statement)) is not None:
            *fields, start, stop = clause
            offset = part.start() + len(part[0]) - len(part[0].lstrip())
            yield *fields, offset + start, offset + stop


def extract_claims(raw, *, enterprise, url, digest, published, publisher):
    """Return attributed candidate excerpts only. No authority or eligibility."""
    facts = {}
    for paragraph, text in body_paragraphs(raw):
        for number, sentence in enumerate(SENTENCE_BREAK.split(text), 1):
            semantic = tuple(semantic_spans(sentence)) if len(sentence) <= 640 else ()
            for kind, status, actor, target, dates, values, parties, start, stop in semantic:
                key = kind, status, actor.casefold(), target.casefold(), tuple(dates), tuple(values)
                facts.setdefault(key, {
                    'claim_id': fingerprint((url, digest, paragraph, number, start, stop)),
                    'event_hint': fingerprint((enterprise, kind, actor.casefold(), target.casefold())),
                    'enterprise_id': enterprise,
                    'source': {'url': url, 'sha256': digest, 'publisher': publisher,
                               'published': published,
                               'locator': f'body p{paragraph}, sentence {number}, chars {start}–{stop}'},
                    'excerpt': sentence[start:stop],
                    'actor_text': actor, 'target_text': target, 'date_mentions': dates,
                    'value_mentions': values, 'relationship_candidates': parties,
                    'kind': kind, 'reported_status': status,
                    'classification': 'issuer claim candidate', 'publication_eligible': False,
                })
                if len(facts) >= 6:
                    return list(facts.values())
            if semantic or not 25 <= len(sentence) <= 320 or UNCERTAIN.search(sentence):
                continue
            statement = re.sub(r'^(?:At|In|On) [^,]{3,70},\s*', '', sentence)
            for kind, status, rule in RULES:
                match = rule.fullmatch(statement)
                if not match:
                    continue
                actor = match['actor']
                if not re.fullmatch(r"[\w&'’() -]+", actor) or not NAME.search(actor):
                    break
                obj = match['object'] or ''
                dates = [found.group().casefold().removeprefix('the ') for found in DATE.finditer(sentence)]
                target = re.split(r'\s+(?:from|by|on|in|until)\s+(?=(?:the )?(?:first|second|early|late|20\d\d|[A-Z][a-z]+ \d))', obj, maxsplit=1)[0].strip(' .')
                if not target:
                    # For passive delivery, the named actor is the initiative.
                    target = actor
                identity = fingerprint((enterprise, kind, actor.casefold(), target.casefold()))
                identifier = fingerprint((url, digest, paragraph, number))
                duplicate_key = kind, status, actor.casefold(), target.casefold(), tuple(dates)
                counterparties = []
                role = {'partnership': 'partner', 'supplier selection': 'supplier',
                        'supply': 'customer'}.get(kind)
                party_text = target if kind != 'supply' else target.rsplit(' to ', 1)[-1]
                if kind == 'supplier selection' and not re.search(r'\bas (?:its |a |the )?supplier\b', target, re.I):
                    role = None
                if kind == 'supply' and not re.search(r'\bcustomer\b', party_text, re.I):
                    role = None
                if role and (kind != 'supply' or ' to ' in target) and (name := NAME.match(party_text)):
                    counterparties = [name[0].strip()]
                facts.setdefault(duplicate_key, {
                    'claim_id': identifier, 'event_hint': identity, 'enterprise_id': enterprise,
                    'source': {'url': url, 'sha256': digest, 'publisher': publisher,
                               'published': published, 'locator': f'body p{paragraph}, sentence {number}'},
                    'excerpt': sentence, 'actor_text': actor, 'target_text': target,
                    'relationship_candidates': [{'name': name, 'role': role}
                                                for name in counterparties],
                    'kind': kind, 'reported_status': status, 'date_mentions': dates,
                    'classification': 'issuer claim candidate', 'publication_eligible': False,
                })
                break
            if len(facts) >= 6:
                return list(facts.values())
    return list(facts.values())


def assess_claims(claims, *, reviewed_events=None, reviewed_origins=None):
    """Group narrow event hints, preserving all competing evidence for review."""
    reviewed_events = reviewed_events or {}
    reviewed_origins = reviewed_origins or {}
    groups = {}
    for claim in claims:
        event = reviewed_events.get(claim['claim_id'], claim['event_hint'])
        groups.setdefault((claim['enterprise_id'], event), {})[claim['claim_id']] = claim
    result = []
    for (enterprise, event), rows in sorted(groups.items()):
        claims_in_group = list(rows.values())
        statuses = {row['reported_status'] for row in claims_in_group}
        dated = {tuple(row['date_mentions']) for row in claims_in_group if row['date_mentions']}
        values = {tuple(row['value_mentions']) for row in claims_in_group if row.get('value_mentions')}
        roles = {tuple(sorted((pair['name'], pair['role']) for pair in row['relationship_candidates']))
                 for row in claims_in_group if row['relationship_candidates']}
        differences = [label for label, values in (
            ('status', statuses), ('date mentions', dated), ('relationship descriptions', roles),
            ('reported values', values),
        ) if len(values) > 1]
        publishers = {row['source']['publisher'] for row in claims_in_group}
        origins = {reviewed_origins[key] for key in rows if reviewed_origins.get(key)}
        if len(publishers) > 1 and all(reviewed_origins.get(key) for key in rows):
            diversity = ('same reported origin' if len(origins) == 1 else
                         'distinct reviewed origins')
        else:
            diversity = ('multiple publishers: independence unverified'
                         if len(publishers) > 1 else 'one publisher')
        result.append({
            'enterprise_id': enterprise, 'event_hint': event, 'claim_ids': sorted(rows), 'differences': differences,
            'disposition': ('material change or conflict: review' if differences else
                            'possible repeated reporting' if len(rows) > 1 else 'single report'),
            'source_diversity': diversity,
            'publication_eligible': False,
        })
    return result
