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


def extract_claims(raw, *, enterprise, url, digest, published, publisher):
    """Return attributed candidate excerpts only. No authority or eligibility."""
    parser = BodyParagraphs()
    parser.feed(raw.decode('utf-8-sig'))
    parser.close()
    facts = {}
    for paragraph, text in parser.paragraphs:
        for number, sentence in enumerate(re.split(r'(?<=[.!?])\s+(?=[A-Z])', text), 1):
            if not 25 <= len(sentence) <= 320 or UNCERTAIN.search(sentence):
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
        roles = {tuple(sorted((pair['name'], pair['role']) for pair in row['relationship_candidates']))
                 for row in claims_in_group if row['relationship_candidates']}
        differences = [label for label, values in (
            ('status', statuses), ('date mentions', dated), ('relationship descriptions', roles),
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
