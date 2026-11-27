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

POLICY = 'BIE-3/1.0'
CUTOFF = '2026-11-15'
REVIEW_UNTIL = '2026-12-15'
KEYS = MappingProxyType({'uk':('growth-mix','public-value','cyber-resilience'),
    'banking':('funding-economics','reporting-change','provider-oversight','service-landscape'),
    'lloyds':('service-recovery','ai-benefits','funding-base')})
# These are dependency fingerprints, not copies of evidence or acceptance.
PINS = Path(__file__).with_name('visual_stream_assets') / 'agenda-dependencies.json'
CANDIDATE = model.REPO / 'enterprise-knowledge/banking/research-model/source-snapshots/INT1-FCA-Candidate.json'
# Explicitly reviewed public releases within the existing source owners.
# No directory scanning, user-selected path, private query or new source engine.
EAI_RELEASES = MappingProxyType({
    'service':('banking','EAI1-FCA-Service-Candidate.json','lloyds','BK-ENT-001',('EAI-LBG-CLOSED','EAI-LBG-UPHELD')),
    'provider':('banking','EAI1-HMT-CTP-Candidate.json','banking','BK-IND-002',('EAI-UK-CTP-DESIGNATION',)),
    'cyber':('macro','EAI1-UK-Cyber-Candidate.json','uk','GB',()),
    'peer-service':('banking','BIE2-FCA-Peers-Candidate.json','banking','BK-IND-002',
                    ('BIE2-BARCLAYS-RECEIVED','BIE2-HSBC-RECEIVED','BIE2-NATWEST-RECEIVED')),
    'bank-outcomes':('banking','BIE3-FCA-Outcomes-Candidate.json','banking','BK-IND-002',
                    ('BIE3-HSBC-CLOSED','BIE3-HSBC-UPHELD','BIE3-NATWEST-CLOSED','BIE3-NATWEST-UPHELD',
                     'BIE3-SANTANDER-RECEIVED','BIE3-SANTANDER-CLOSED','BIE3-SANTANDER-UPHELD')),
})
# Existing Banking selection aliases; no new Twin, route or legal-identity owner.
BANK_SERVICE = MappingProxyType({
    'natwest':('National Westminster Bank PLC','NATIONAL WESTMINSTER BANK PUBLIC LIMITED COMPANY only; not its consolidated Group or other bank subsidiaries',
               ('BIE2-NATWEST-RECEIVED','BIE3-NATWEST-CLOSED','BIE3-NATWEST-UPHELD')),
    'hsbc-uk':('HSBC UK Bank Plc','HSBC UK Bank Plc only; not its consolidated Group or other bank subsidiaries',
               ('BIE2-HSBC-RECEIVED','BIE3-HSBC-CLOSED','BIE3-HSBC-UPHELD')),
    'tsb':('TSB Bank plc','TSB Bank plc only; not TSB Banking Group Limited',()),
    'nationwide':('Nationwide Building Society','Nationwide Building Society only; not its consolidated Group',()),
    'starling':('Starling Bank Limited','Starling Bank Limited only; not its consolidated Group',()),
    'santander-uk':('Santander UK Plc','Santander UK Plc only; not Santander UK Group Holdings plc or TSB Bank plc',
               ('BIE3-SANTANDER-RECEIVED','BIE3-SANTANDER-CLOSED','BIE3-SANTANDER-UPHELD')),
})


def _eai_release(key):
    from .research_intelligence.registry import snapshot_boundary
    domain,name,scope,subject,ids=EAI_RELEASES[key]
    path=snapshot_boundary(domain)/name
    try:
        if path.is_symlink():return None
        package=json.loads(path.read_text())
    except (OSError,ValueError):return None
    if not isinstance(package,dict):return None
    if (fingerprint(package)!=_pins().get('eai_releases',{}).get(key)
            or package.get('authority')!='candidate_intelligence'
            or package.get('canonical_mutation')is not False
            or package.get('owner_only')
            or package.get('scope')!=scope or package.get('subject_ref')!=subject):return None
    source=package.get('source')
    if (not isinstance(source,dict) or p.restricted_metadata(package)
            or p.restricted_metadata(source)
            or source.get('rights',{}).get('status')not in
            {'permitted_numerical_data','permitted_ogl_factual_extract'}):return None
    try:model.primary_text(source)
    except (OSError,ValueError,KeyError):return None
    return package


def _eai_bank_data(data,key):
    package=_eai_release(key)
    if package is None:return data
    _,_,_,subject,ids=EAI_RELEASES[key]
    try:
        if (tuple(c['id']for c in package['claims'])!=ids
                or any(c['asset_id']!=subject for c in package['claims'])):return data
        result=deepcopy(data);result['assessed_at']=CUTOFF
        result['sources'].append(package['source']);result['claims'].extend(package['claims'])
        model.validate(result)
    except (OSError,ValueError,KeyError,TypeError):return data
    return result


def _cyber_estimate():
    package=_eai_release('cyber')
    if package is None:return None
    # The existing Macro contract checks source/segment/claim/date/authority;
    # only a disposable copy receives the proposed source and observations.
    context=deepcopy(visual_v2.macro.load_context())
    if p.restricted_metadata(context):return None
    context['as_of']=CUTOFF
    try:
        context['sources'].append(package['source']);context['observations'].extend(package['observations'])
        visual_v2.macro.validate_context(context)
    except (OSError,ValueError,KeyError,TypeError):return None
    s=package['source']
    return p.Statement('The 2025/26 survey estimated that 43% of eligible UK businesses and 69% of large businesses identified a cyber breach or attack in their preceding 12 months.',
        'estimated','UK surveyed businesses; not an individual bank','August–December 2025 fieldwork; preceding 12 months per interview',
        (p.Source(s['title'],s['url'],s['publisher'],s['publication_date'],s['reporting_period'],locator='Summary / Methodology1.3 / Subgroups1.6 / Footnote3'),),
        'reviewed_excerpt','candidate_intelligence',method='Weighted, self-reported survey estimates. Large businesses have 250 or more employees; size groups are not matched enterprise cohorts.',
        caveats=('Only identified and reported events are captured; hidden attacks can be missed. These are population estimates, not a bank incident census.',
            'The survey excludes sole traders, public-sector organisations outside education, and businesses without IT capacity or online presence.'),
        counter_evidence=('Overall prevalence remained in line with the prior year; the publication does not establish a new surge or a named company control failure.',))


def _deposit_change(facts):
    """One explicit stock-date bridge over two pinned, already public owners.

    Original unit/period strings are checked before mapping their common
    customer-deposit meaning. Not an expression engine or like-for-like flow.
    """
    if len(facts)!=2:return None
    opening,closing=facts
    expected=((opening,'GBP billion; year-end balance','31 December 2025'),
              (closing,'GBP billion; balance at 30 September 2026','Nine months ended / balance sheet at 30 September 2026'))
    if (opening.scope!=closing.scope or any(not p.eligible(f)or f.semantic_type!='reported'
            or f.measurement_state not in {'actual','not_applicable'}or f.value is None
            or f.unit!=unit or f.basis!=unit or f.period!=period for f,unit,period in expected)):return None
    value=closing.value-opening.value
    return p.Statement('The difference between the published Group customer-deposit stocks is £'+str(value)+'bn.',
        'calculated',closing.scope,'31 December 2025 to 30 September 2026; two balance-sheet dates',
        tuple(dict.fromkeys((*opening.sources,*closing.sources))),'derived_from_inputs','derived_view_not_canonical',
        measurement_state='actual',value=value,unit='GBP billion',basis='Consolidated Group customer-deposit stocks at the two stated dates',
        method=f'{closing.value} − {opening.value} = {value} GBP billion; arithmetic comparison of the published stocks.',
        dependencies=(opening.text,closing.text),dependency_types=('reported','reported'),
        input_authorities=(opening.canonical_status,closing.canonical_status),
        caveats=('Not adjusted for consolidation changes, transfers or other balance-sheet effects. This is not an organic inflow, interest-income, margin or supplier-budget measure.',))


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
    if (p.restricted_metadata(data) or data.get('authority')!='candidate_intelligence'
            or data.get('industry_twin_id')!='BK-IND-002'
            or data.get('enterprise_twin_id')!='BK-ENT-001'
            or not model.freshness(data)['eligible']):
        return ()
    if 'LBG-FCA-H126-RECEIVED'in ids:data=_public_data(data)
    for release in ('service','provider','peer-service','bank-outcomes'):
        if set(ids).intersection(EAI_RELEASES[release][4]):data=_eai_bank_data(data,release)
    by_id={c['id']:c for c in data['claims']};sources={s['id']:s for s in data['sources']}
    rows=[]
    for key in ids:
        c=by_id.get(key)
        if not c or fingerprint(c)!=pins['claims'].get(key):return ()
        if p.restricted_metadata(c):return ()
        for sid in c['source_ids']:
            s=sources.get(sid)
            if not s or fingerprint(s)!=pins['sources'].get(sid):return ()
            official_url(s['url'])
            if p.restricted_metadata(s):return ()
            if (sid in {'PR-FCA-COMPLAINTS-H126','EAI-FCA-H126-SERVICE','BIE2-FCA-H126-PEERS','BIE3-FCA-H126-OUTCOMES'}
                    and s.get('rights',{}).get('status')!='permitted_numerical_data'):return ()
            if sid=='EAI-HMT-CTP26'and s.get('rights',{}).get('status')!='permitted_ogl_factual_extract':return ()
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
        dependencies=tuple(f.text for f in facts),counter_evidence=tuple(counter),
        dependency_types=tuple(dict.fromkeys(t for f in facts for t in (f.semantic_type,*f.dependency_types))))
    if p.NON_CORE.search(title) or not p.eligible(conclusion):return None
    return Issue(key,title,conclusion,facts,analysis)


def bank_service_issue(selected,data):
    """A narrow legal-bank service view, never a complete Enterprise Model."""
    if selected not in BANK_SERVICE or p.restricted_metadata(data):return None
    name,scope,ids=BANK_SERVICE[selected]
    if not ids:
        return routine_service_issue(selected)
    facts=_claims(data,ids)
    units=('complaints received; all-product total','complaints closed; all-product total',
           'percent of closed complaints upheld by firm; FCA table total')
    if (len(facts)!=3 or any(f.scope!=scope or f.period!='1 January–30 June 2026'
            or f.unit!=unit or f.semantic_type!='reported' or f.value is None
            or f.measurement_state not in {'actual','not_applicable'}for f,unit in zip(facts,units))):return None
    received,closed,upheld=facts
    facts=tuple(replace(f,caveats=('Received and closed complaints are different cohorts. Firm-upheld is not independent adjudication; these measures establish no harm rate, cost, service-quality ranking or buying need.',))for f in facts)
    text=(name+' received '+format(received.value,',')+' complaints and closed '+format(closed.value,',')
          +' in January–June 2026; '+str(upheld.value)+'% of closed complaints were upheld by the firm. '
          +'These are different cohorts, not a service-quality ranking or backlog measure.')
    return _issue('service-landscape',name+': complaint activity and resolution',text,facts,
        'The same FCA period and legal-bank identity support distinct activity and firm-resolution measures. Group financial results and other bank subsidiaries are outside this view.',
        ('No deterioration, customer denominator, cost, independent outcome or external supplier need is established. Santander UK Plc data are not consolidated with TSB Bank plc.',),
        'Legal-bank service operations · received/closed cohorts and firm-upheld outcomes; no Group aggregation.')



def routine_service_issue(selected):
    """Authored analysis over lawful public numerical facts; no promotion gate."""
    from .research_intelligence.source_import import working_facts, bound_facts, working_restricted
    from decimal import Decimal
    try:
        research, sources = working_facts()
        rows = [r for r in research['service_profiles'] if r['selection'] == selected]
        if len(rows) != 1: return None
        row = rows[0]
        source = sources[row['source_id']]
        if working_restricted(row) or {k:v for k,v in row.items() if k != 'source_id'} != bound_facts(source, selected, 'service_profile'):
            return None
        ref = p.Source(source['title'], source['url'], source['publisher'], source['publication_date'],
                       locator=row['name']+'; all-product Total; '+row['period'])
        caveat = 'Received and closed complaints are different cohorts. Firm-upheld is not independent adjudication; no harm rate, cost, service-quality ranking or buying need is established.'
        facts = tuple(p.Statement(label, 'reported', row['scope'], row['period'], (ref,),
                    'reviewed_excerpt', 'candidate_intelligence', value=Decimal(str(row[key])), unit=unit,
                    caveats=(caveat,)) for key,label,unit in (
                    ('received', row['name']+' received '+format(row['received'],',')+' complaints.', 'complaints received; all-product total'),
                    ('closed', row['name']+' closed '+format(row['closed'],',')+' complaints.', 'complaints closed; all-product total'),
                    ('upheld', row['name']+' upheld '+row['upheld']+'% of closed complaints.', 'percent of closed complaints upheld by firm; FCA table total')))
        if not all(p.eligible(f) for f in facts): return None
        return _issue('service-landscape', row['name']+': complaint activity and resolution',
             row['name']+' reported '+format(row['received'],',')+' complaints received and '+format(row['closed'],',')+' closed; '+row['upheld']+'% of closed complaints were upheld by the firm.', facts,
             'Separate activity and firm-resolution measures for the exact legal entity and reporting period; not a causal diagnosis or cross-bank ranking.',
             (caveat,'Period: '+row['period']+'. Source publication22October2026. No financial redress or Group earnings is inferred.'),
             'Service operations · legal-entity facts and authored interpretation.')
    except (OSError, ValueError, KeyError, TypeError, PermissionError, StopIteration):
        return None


LLOYDS_SERVICE_PRODUCTS = (
    ('bankcards', 'Banking and credit cards'), ('pensions', 'Decumulation & pensions'),
    ('mortgages', 'Home finance'), ('insurance', 'Insurance & pure protection'),
    ('investments', 'Investments'), ('total', 'Grand Total'),
)


def lloyds_service_products():
    """Read the existing Source-owned FCA service profiles, not Financial runs.

    Product groups describe complaint activity, never reporting divisions or
    financial allocations. All cells and their common total must reconcile.
    Every render rechecks the actual Source revision, use and lifecycle.
    """
    from .research_intelligence.source_import import routine_factual_use, bound_facts, working_restricted
    from .research_intelligence.registry import snapshot_boundary
    from decimal import Decimal
    try:
        path = snapshot_boundary('banking', model.REPO) / 'FCA-Lloyds-Products-H126.json'
        if path.is_symlink():return ()
        research = json.loads(path.read_text())
        if (research.get('authority') != 'analytical_working_research'
                or research.get('canonical_mutation') is not False
                or working_restricted(research) or len(research['sources']) != 1):
            return ()
        source = research['sources'][0]
        if source['id'] != 'FCA-LLOYDS-PRODUCTS-H126':return ()
        if routine_factual_use(source) != 'open_numerical_data':return ()
        model.primary_text(source)
        if (source['publisher'] != 'Financial Conduct Authority'
                or source['url'] != 'https://www.fca.org.uk/data/firm-level-complaints-data-sortable-table'
                or source['publication_date'] != '2026-10-22'
                or source['reporting_period'] != '1 January–30 June 2026'):
            return ()
        result = []
        for key, product in LLOYDS_SERVICE_PRODUCTS:
            selection = 'lloyds-service-' + key
            rows = [r for r in research['service_profiles'] if r['selection'] == selection]
            if len(rows) != 1:
                return ()
            row = rows[0]
            if (row['source_id'] != source['id'] or working_restricted(row)
                    or {k:v for k,v in row.items() if k != 'source_id'} != bound_facts(source, selection, 'service_profile')
                    or row['name'] != 'Lloyds Bank PLC' or row['product'] != product
                    or row['scope'] != 'Lloyds Bank PLC only; not consolidated Group or a reporting division'
                    or row['period'] != source['reporting_period']
                    or any(type(row[k]) is not int or row[k] < 0 for k in ('received', 'closed'))
                    or not Decimal(row['upheld']).is_finite() or not 0 <= Decimal(row['upheld']) <= 100):
                return ()
            binding = next(b for b in source['fact_bindings'] if b['key'] == selection)
            for index, metric in zip(binding['excerpt_indices'], ('Open', 'Closed', 'Upheld')):
                if source['excerpts'][index]['locator'] != 'Lloyds Bank PLC;'+metric+' table;'+product+';'+row['period']:
                    return ()
            ref = p.Source(source['title'], source['url'], source['publisher'], source['publication_date'],
                           locator='Lloyds Bank PLC; '+product+'; Open / Closed / Upheld tables; '+row['period'])
            facts = tuple(p.Statement(
                product + ': ' + str(row[k]) + suffix, 'reported', row['scope'], row['period'], (ref,),
                'reviewed_excerpt', 'analytical_working_research', 'actual',
                value=Decimal(str(row[k])), unit=unit,
                caveats=('Different received/closed cohorts; firm-upheld is not independent adjudication. Not Group divisional results, redress, cost, customer incidence or buying need.',))
                for k, suffix, unit in (('received', ' complaints received', 'complaints received'),
                    ('closed', ' complaints closed', 'complaints closed'),
                    ('upheld', '% of closed complaints upheld by firm', 'percent of closed complaints upheld by firm')))
            if not all(p.eligible(f) for f in facts):
                return ()
            result.append((key, product, facts))
        for i in (0, 1):
            if sum(row[2][i].value for row in result[:-1]) != result[-1][2][i].value:
                return ()
        if result[-1][2][0].value <= 0:
            return ()
        return tuple(result)
    except (OSError, ValueError, KeyError, TypeError, PermissionError, StopIteration, ArithmeticError):
        return ()


def agenda(scope,data=None,*,selected=''):
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
        fact=_cyber_estimate()
        rows.append(_issue('cyber-resilience','Cyber exposure remains widespread across UK businesses',
            'The survey estimates indicate broad cyber exposure, especially among large businesses, while overall prevalence remained in line with the prior year.',
            (fact,)if fact else (), 'The same survey reports prevalence by business size. This describes national exposure, not the cause, loss or control effectiveness at an individual enterprise.',
            ('The percentages are weighted self-reported estimates from August–December 2025 fieldwork. They establish neither a fresh incident nor an unmet supplier need at a named bank.',),
            'PESTLE · technological; enterprise-size exposure.'))
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
            facts=_claims(data,('EAI-UK-CTP-DESIGNATION',))
            rows.append(_issue('provider-oversight','Technology oversight extends to the provider layer',
                'The UK critical third-party regime designated four named technology-provider legal entities from 13 July 2026, extending oversight beyond banks’ own controls.',facts,
                'The designation identifies a regulated provider layer in financial-system resilience; it is distinct from a particular bank’s supplier contract.',
                ('Designation does not identify a bank customer, workload, spend, concentration exposure, service failure or open procurement. The announcement was published on 10 July, not 13 July.',),
                'PESTLE · legal and technological; value chain · critical service providers.'))
            facts=_claims(data,EAI_RELEASES['peer-service'][4])
            if facts:
                facts=tuple(replace(f,caveats=('Received complaints are activity counts, not a customer-harm rate, cost or service-quality ranking.',
                    'Contains Financial Conduct Authority information licensed under the Open Government Licence v3.0.'))for f in facts)
            rows.append(_issue('service-landscape','Complaint activity spans distinct banking entities',
                'In January–June 2026, Barclays Bank UK PLC received 90,678 complaints, HSBC UK Bank Plc 79,323 and National Westminster Bank PLC 92,548. These are service-handling volumes, not a service-quality ranking.',
                facts,'The FCA Open table publishes all-product totals for the same six-month period, with each count retained against its reporting legal entity.',
                ('These counts do not establish relative service quality, deterioration, customer harm, cost or unmet supplier need. Customer bases and product mixes differ; no denominator, backlog subtraction or Group aggregation is used.',),
                'Industry operating model · customer service activity; separate legal-entity reporting.'))
        else:
            facts=_claims(data,('LBG-FCA-H126-RECEIVED','EAI-LBG-CLOSED','EAI-LBG-UPHELD'))
            if facts:
                facts=(replace(facts[0],caveats=('Lloyds Bank PLC only, not consolidated Group. A received-complaint count is neither a customer-harm rate nor a cost measure.',
                    'Contains Financial Conduct Authority information licensed under the Open Government Licence v3.0.')),*facts[1:])
            if facts:
                rows.append(_issue('service-recovery','Complaint volumes and upheld outcomes are distinct',
                    'Lloyds Bank PLC received 118,762 complaints in January–June 2026; 66.12% of complaints closed during that period were upheld by the firm. These describe activity and resolution outcomes separately.',
                    facts,'The FCA published 118,762 received and 118,861 closed complaints. Different cohorts prevent treating their difference as backlog clearance or treating upheld cases as a cost measure.',
                    ('No deterioration, avoidable cost or customer-harm rate is established. Firm-upheld is not independent adjudication. FOS April–September cases are a different window and cohort.',),
                    'Enterprise operating model · service recovery; customer outcomes.'))
            else:
                # A withdrawn optional expansion must not erase the previously
                # permitted INT-1 received-only view. The same key stays singular.
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
            facts=_claims(data,('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS'))
            movement=_deposit_change(facts)
            rows.append(_issue('funding-base','Published Group deposits are £6.3bn higher',
                'Published Group customer deposits rose from £496.5bn at 31 December 2025 to £502.8bn at 30 September 2026, a £6.3bn stock difference; this describes funding scale, not interest-income growth.',
                (*facts,movement)if movement else (), 'The arithmetic uses two dated, already-public Group customer-deposit disclosures and keeps balance-sheet stocks separate from profit flows.',
                ('The comparison is not adjusted for consolidation changes, transfers or other balance-sheet effects. It establishes no organic inflow, price sensitivity, margin effect or available supplier budget.',),
                'Enterprise economics · deposits and funding; stock-date bridge.'))
    result=tuple(r for r in rows if r is not None)
    # Existing permitted concern remains the parent. Revoking its original
    # source also removes every dependent selected-bank view and selector.
    if scope=='banking'and any(r.key=='service-landscape'for r in result):
        row=bank_service_issue(selected,data)
        if row:result=tuple(row if r.key=='service-landscape'else r for r in result)
    return result


def bank_service_navigation(ctx,link,issues,data):
    if ctx.scope!='banking' or p.restricted_metadata(data):return ''
    available=[(slug,name)for slug,(name,_,ids)in BANK_SERVICE.items()
               if (not ids or any(r.key=='service-landscape'for r in issues)) and bank_service_issue(slug,data)]
    if not available:return ''
    body='<div class="layer-options bank-service-profiles"><nav aria-label="Bank complaint profiles">'
    for slug,name in available:
        target_agenda='service-landscape' if BANK_SERVICE[slug][2] else ''
        body+='<a href="'+escape(link(ctx,selected=slug,detail='',agenda=target_agenda)+'#agenda-insight',quote=True)+'"'+(' aria-current="true"'if ctx.selected==slug else'')+'>'+escape(name)+'</a>'
    return body+'</nav></div>'


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
    return body+basis(row)+'</section>'


def basis(row):
    """Optional public source basis shared by existing agenda and Main views."""
    e=escape
    body='<details class="agenda-basis"><summary>Basis &amp; perspective</summary>'
    body+=''.join(p.render(f)for f in row.facts)+'<p>'+e(row.analysis)+'</p>'
    if row.key in {'service-recovery','service-landscape'}:
        body+='<p class="source-licence">Contains Financial Conduct Authority information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    if row.key in {'cyber-resilience','provider-oversight'}:
        body+='<p class="source-licence">Contains public sector information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    return body+'</details>'
