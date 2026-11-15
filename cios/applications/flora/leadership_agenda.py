"""SI-1 Option A: bounded, read-only editorial views over existing owners.

Concern keys are URL selections, not durable StrategicIssue identities. No
network, private lookup, acceptance, scoring, model invocation or persistence.
Every dependency is resolved and checked before a title or count is returned.
"""
from dataclasses import dataclass, replace
from copy import deepcopy
from datetime import date
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from types import MappingProxyType

from . import intelligence_presentation as p, visual_v2
from .research_intelligence import model
from .research_intelligence.source_import import official_url

POLICY = 'INT-1/1.0'
CUTOFF = '2026-11-15'
REVIEW_UNTIL = '2026-12-15'
KEYS = MappingProxyType({'uk':('growth-mix','public-value'),
    'banking':('funding-economics','reporting-change'),
    'lloyds':('service-recovery','ai-benefits')})
# These are dependency fingerprints, not copies of evidence or acceptance.
PINS = Path(__file__).with_name('visual_stream_assets') / 'agenda-dependencies.json'
CANDIDATE = model.REPO / 'enterprise-knowledge/banking/research-model/source-snapshots/INT1-FCA-Candidate.json'


def fingerprint(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def _pins():
    try:return json.loads(PINS.read_text())
    except (OSError,ValueError):return {}


@dataclass(frozen=True)
class Issue:
    key: str
    title: str
    conclusion: p.Statement
    facts: tuple[p.Statement, ...]
    analysis: str


def _public_data(data):
    """Validate one proposed public SourceRecord/claim using the existing owner.

    The original assessment and its baseline-bound understanding review are
    never revised. This is an in-memory presentation composition, not a second
    research owner, source registry, accepted record or canonical import.
    """
    pins=_pins()
    try:proposal=json.loads(CANDIDATE.read_text())
    except (OSError,ValueError):return data
    if fingerprint(proposal)!=pins.get('candidate_proposal'):return data
    if (proposal['authority']!='candidate_intelligence' or proposal['canonical_mutation']
            or proposal['source']['id']!='PR-FCA-COMPLAINTS-H126'
            or proposal['claim']['id']!='LBG-FCA-H126-RECEIVED'):return data
    result=deepcopy(data)
    result['assessed_at']=CUTOFF
    result['sources'].append(proposal['source']);result['claims'].append(proposal['claim'])
    try:model.validate(result)
    except (ValueError,KeyError,OSError):return data
    return result


def _claims(data, ids):
    """Exact public owner release only; no name joins or private fallbacks."""
    pins=_pins()
    if not pins:return ()
    if (data.get('authority')!='candidate_intelligence'
            or data.get('industry_twin_id')!='BK-IND-002'
            or data.get('enterprise_twin_id')!='BK-ENT-001'
            or not model.freshness(data)['eligible']):
        return ()
    if 'LBG-FCA-H126-RECEIVED'in ids:data=_public_data(data)
    by_id={c['id']:c for c in data['claims']};sources={s['id']:s for s in data['sources']}
    rows=[]
    for key in ids:
        c=by_id.get(key)
        if not c or fingerprint(c)!=pins['claims'].get(key):return ()
        if c.get('freshness') in {'stale','withdrawn','superseded'} or c.get('retracted'):return ()
        for sid in c['source_ids']:
            s=sources.get(sid)
            if not s or fingerprint(s)!=pins['sources'].get(sid):return ()
            official_url(s['url'])
            if s.get('withdrawn') or s.get('rights',{}).get('status') in {'revoked','denied','unknown'}:return ()
            if sid=='PR-FCA-COMPLAINTS-H126' and s.get('rights',{}).get('status')!='permitted_numerical_data':return ()
        item=p.claim_view(data,c)
        if item is None:return ()
        # Existing owner validates the excerpt; agenda does not republish the
        # existing issuer prose. Attributed factual statements remain scoped.
        item=replace(item,sources=tuple(replace(s,quote='') for s in item.sources))
        rows.append(item)
    return tuple(rows)


def _issue(key,title,text,facts,reason,counter,analysis):
    if not facts or any(not p.eligible(f) for f in facts):return None
    conclusion=p.Statement(text,'insight',facts[0].scope,'; '.join(dict.fromkeys(f.period for f in facts)),
        tuple(dict.fromkeys(s for f in facts for s in f.sources)),
        'repository_interpretation','derived_view_not_canonical',reasoning=reason,
        dependencies=tuple(f.text for f in facts),counter_evidence=tuple(counter))
    if p.NON_CORE.search(title) or not p.eligible(conclusion):return None
    return Issue(key,title,conclusion,facts,analysis)


def agenda(scope,data=None):
    """Same scope/cutoff/dependencies → same agenda, independent of lens/user.

    Public repository candidates only. Private records can never enter this
    projection; future private intelligence requires its existing ACL owner.
    """
    if scope not in KEYS or not date.fromisoformat(CUTOFF)<=date.today()<=date.fromisoformat(REVIEW_UNTIL):return ()
    rows=[]
    if scope=='uk':
        pins=_pins()
        if not pins:return ()
        # Existing frozen ONS view is reused without new ingestion, source
        # substitution or publisher admission. New ONS research stays blocked.
        basis=visual_v2.basis()
        if fingerprint(basis)==pins['existing_economy']:
            row=visual_v2.insight('economic');s=row['sources'][0]
            fact=p.Statement(row['text'],'reported','United Kingdom',basis['growth']['period'],
                (p.Source(s['title'],s['url'],'Office for National Statistics',s['publication_date'],basis['growth']['period'],locator=s['locator']),),
                'reviewed_excerpt','existing_frozen_public_view',caveats=('Preliminary volume estimate, subject to revision.',))
            rows.append(_issue('growth-mix','Services lead the latest UK expansion',
                'Services led the 0.7% UK real GDP expansion in the three months to September 2026; the aggregate does not establish growth in every industry.',
                (fact,),'The existing GDP release identifies services as the leading contributor; national and sector performance are different scopes.',
                ('A preliminary national volume measure does not establish productivity improvement, company pain or buying demand.',),
                'PESTLE · economics; industry mix.'))
        if fingerprint(visual_v2.macro.load_context())==pins['existing_macro']:
            row=visual_v2.insight('political')
            sources=tuple(p.Source(s['title'],s['url'],s.get('publisher',''),s.get('publication_date')or'')for s in row['sources'])
            if all(official_url(s.url) for s in sources):
                fact=p.Statement('From January 2027, the reviewed social-value policy covers specified UK central-government tenders.','reported',
                    'Specified UK central-government procurements; contract scope and transition rules apply','January 2027 policy implementation',sources,
                    'reviewed_excerpt','existing_public_macro_candidate',measurement_state='commitment')
                rows.append(_issue('public-value','Public-contract value extends into delivery',
                    'For covered central-government contracts, social-value commitments connect bid economics with delivery obligations.',(fact,),
                    'The existing procurement policy links evaluation commitments with contract delivery; it is not a universal requirement on UK enterprises.',
                    ('Covered tenders and transition rules differ; existing delivery teams may already satisfy the commitments. No Lloyds contract is asserted.',),
                    'PESTLE · political and social; value chain · bid to delivery.'))
    else:
        data=data if data is not None else model.load_assessment()
        if scope=='banking':
            facts=_claims(data,('UK-RATE-NOV26',))
            rows.append(_issue('funding-economics','Funding repricing connects customer choice and bank economics',
                'The November 2026 Bank Rate decision changes the policy-rate backdrop; deposit pricing and lending repricing determine how each bank transmits it.',
                facts,'Bank Rate is a common input. Deposit mix, competition and repricing timing determine the direction and scale of bank-specific effects.',
                ('Rate direction alone proves neither margin deterioration nor customer demand. Deposit balances are not a measure of customer price sensitivity.',),
                "PESTLE · economic; Five Forces · buyer choice; value chain · deposits and lending."))
            facts=_claims(data,('UK-PRA-REPORT27','UK-FCA-REPORT27'))
            rows.append(_issue('reporting-change','Incident and third-party reporting change in March 2027',
                'The reviewed PRA and FCA policies place incident and third-party reporting changes on an 18 March 2027 timetable.',facts,
                'The common timetable connects operational incident information and third-party reporting, within each regulator’s scope.',
                ('Sector policy does not establish an individual legal entity’s duties, readiness, supplier shortfall or open procurement.',),
                'PESTLE · legal and technological; value chain · resilience and suppliers.'))
        else:
            facts=_claims(data,('LBG-FCA-H126-RECEIVED',))
            if facts:
                facts=(replace(facts[0],caveats=('Lloyds Bank PLC only, not consolidated Group. A received-complaint count is neither a customer-harm rate nor a cost measure.',
                    'Contains Financial Conduct Authority information licensed under the Open Government Licence v3.0.')),)
            rows.append(_issue('service-recovery','Complaint handling is a substantial service activity',
                'Lloyds Bank PLC’s 118,762 received complaints in January–June 2026 identify a substantial service-handling volume, without establishing deterioration or avoidable cost.',
                facts,'An observed received-complaint volume supports service-activity scale, not the cause, cost per case, customer harm or a case for an external supplier.',
                ('No matched historical or customer denominator is used. Closed cases can include earlier complaints; FOS April–September cases are a different window and cohort.',),
                'Enterprise operating model · service recovery; customer outcomes.'))
            facts=_claims(data,('LBG-AI26-REPORTED','LBG-AI26-EXPECTED','LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS'))
            rows.append(_issue('ai-benefits','AI benefit ambitions sit on existing capabilities',
                'Lloyds reported about £50m of AI value for 2025 and expected more than £100m for 2026; its announced Envoy platform and Google Cloud collaboration place benefit realisation within an existing capability base.',
                facts,'Reported value, future expectation and announced platform capabilities are separate measures. They support a benefit-realisation theme within an existing technology response.',
                ('Expected 2026 value is not achieved net benefit, supplier revenue or a budget. Company-described controls do not establish effectiveness; internal teams and incumbents may already cover delivery.',),
                'Enterprise economics · actual versus expected; relational SWOT · existing capability and benefit realisation.'))
    return tuple(r for r in rows if r is not None)


def navigation(ctx,link,issues):
    if not issues:return ''
    e=escape
    body='<details class="leadership-agenda"'+(' open'if ctx.agenda else '')+'><summary>Leadership Agenda</summary><nav aria-label="Leadership Agenda">'
    for row in issues:
        body+='<a href="'+e(link(ctx,agenda=row.key,detail='')+'#agenda-insight',quote=True)+'"'+(' aria-current="true"'if ctx.agenda==row.key else '')+'>'+e(row.title)+'</a>'
    return body+'</nav></details>'


def detail(ctx,link,issues):
    row=next((r for r in issues if r.key==ctx.agenda),None)
    if not row:return ''
    e=escape
    body='<section class="focus agenda-focus" id="agenda-insight" tabindex="-1" aria-labelledby="agenda-title"><a class="close close-insight" href="'+e(link(ctx,agenda='')+'#visual-content',quote=True)+'" aria-label="Close Leadership Agenda">×</a><h2 id="agenda-title">'+e(row.title)+'</h2>'
    body+=p.render(row.conclusion)
    body+='<details class="agenda-basis"><summary>Reported basis &amp; perspective</summary>'
    body+=''.join(p.render(f)for f in row.facts)+'<p>'+e(row.analysis)+'</p>'
    if row.key=='service-recovery':
        body+='<p class="source-licence">Contains Financial Conduct Authority information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    body+='</details>'
    return body+'</section>'
