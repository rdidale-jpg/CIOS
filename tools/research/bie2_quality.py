"""Offline QA of Issue635 review artifacts, not an intelligence/runtime engine.

Checks structural and numerical reproducibility. It cannot prove the publisher's
original bytes, rights acceptance, research completeness or canonical authority.
"""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/'docs/flora-runtime/bie2'

def load(root=PACK):
    return {name:json.loads((Path(root)/(name+'.json')).read_text())for name in
        ('Source-Ledger','Actor-Register','Enterprise-Dossiers','Additional-Profiles',
         'Relationship-Candidates','News-Candidates','Industry-Analysis','Admission-and-Integration')}

def window(value, publication=False):
    if not value:return 'outside_or_unverified'
    date.fromisoformat(value)
    if '2026-10-16'<=value<='2026-11-15':return 'current_literal_window'
    if '2026-08-18'<=value<'2026-10-16':return 'prior_90_day_publication'if publication else'prior_90_day_event'
    return 'outside_or_unverified'

def validate(pack):
    """Reject unresolved authority and invalid joins instead of inventing facts."""
    sources={r['id']:r for r in pack['Source-Ledger']}
    assert len(sources)==len(pack['Source-Ledger'])
    for s in sources.values():
        u=urlsplit(s['url'])
        assert u.scheme=='https'and u.hostname and not u.username and not u.password and not u.query
        assert s['canonical_acceptance']=='not_accepted'and s['canonical_id']is None
        assert s['original_bytes_sha256']is None
        assert s['retrieved_on']=='2026-11-15'and s['retrieval_reference']
        if s['publication_date']:assert date.fromisoformat(s['publication_date'])<=date(2026,11,15)
    actors=pack['Actor-Register']['actors'];ids={a['id']for a in actors}
    assert len(ids)==len(actors)
    for a in actors:
        assert a['canonical_id']is None and set(a['identity_sources'])<=sources.keys()
        if a['kind']=='legal_deposit_taker':assert a['frn'].isdigit()and len(a['lei'])==20
    dossiers=pack['Enterprise-Dossiers'];assert len({d['actor_id']for d in dossiers})>=5
    for d in dossiers:
        assert d['actor_id']in ids and set(d['source_ids'])<=sources.keys()
        assert d['canonical_id']is None and d['canonical_acceptance']=='not_accepted'
        assert d['visibility']=='owner_research_artifact_only'and d['gaps']
        assert d['strategic_issue']['buying_intent']=='not established'
        assert d['strategic_issue']['counter_evidence']and d['strategic_issue']['existing_response']
        assert d['strategic_issue']['potentially_open_decision']and d['strategic_issue']['role_accountability']
        for m in d['metrics']:
            assert m['semantic_type']=='reported'and m['measurement_state']=='actual'
            assert m['unit']and m['basis']and set(m['source_ids'])<=set(d['source_ids'])
    by={d['actor_id']:d for d in dossiers}
    reporting={'natwest':'nw-group','santander-uk':'san-group','nationwide':'nbs-group','starling':'star-group','clearbank':'clear-group'}
    assert set(by)=={'actor:'+a for a in ('nw-group','hsbc-uk','san-group','nbs-group','star-group','clear-group')}
    for d in dossiers:
        assert set(d['related_legal_bank_actor_ids'])<=ids
        for m in d['metrics']:
            expected='actor:clearbank'if d['actor_id']=='actor:clear-group'and m['name'].startswith('UK ')else d['actor_id']
            assert m['subject_actor_id']==expected and m['entity_scope']
    def metric(actor,name):return Decimal(str(next(m['value']for m in by['actor:'+reporting.get(actor,actor)]['metrics']if m['name']==name)))
    assert by['actor:hsbc-uk']['currency']=='USD'
    assert metric('hsbc-uk','Revenue')-metric('hsbc-uk','Expected credit losses')-metric('hsbc-uk','Operating expenses')+metric('hsbc-uk','Associates income')==metric('hsbc-uk','Profit before tax')==6084
    assert metric('nationwide','Underlying income')-metric('nationwide','Underlying administrative expenses')-metric('nationwide','Credit impairment')==metric('nationwide','Underlying profit before tax')==2026
    assert metric('nationwide','Statutory profit before tax')==1490
    assert '1 May 2026'in by['actor:san-group']['period']
    assert metric('clearbank','UK bank profit before tax')==Decimal('12.2')
    assert metric('clearbank','Group normalised revenue')==Decimal('121.6')
    assert metric('clearbank','Group statutory profit before tax')==Decimal('-16.7')
    assert metric('starling','Platform accounts')==Decimal('6.2')
    graph=pack['Relationship-Candidates'];seen=set()
    for e in graph['edges']:
        key=(e['subject'],e['predicate'],e['object'],tuple(e['source_ids']))
        assert key not in seen;seen.add(key)
        assert e['subject']in ids and e['object']in ids and set(e['source_ids'])<=sources.keys()
        assert e['canonical_id']is None and e['canonical_acceptance']=='not_accepted'
        assert all(e[k]is None for k in ('contract_value','contract_duration','exclusivity'))
        assert e['entity_scope']and e['limitation']and e['relationship_status']
        if 'development'in e['predicate']:
            assert e['relationship_status']=='announced_development'and e['effective_date']is None
        if e['id']in {'edge:012','edge:013','edge:014'}:assert e['effective_date']is None
        if e['object']=='actor:revolut-uk':assert e['predicate']!='reported_embedded_or_payment_client'
        if e['subject']=='actor:nt':assert e['object']!='actor:barclays-uk'
    news=pack['News-Candidates'];events=news['events']
    assert news['literal_current_window']==['2026-10-16','2026-11-15']and news['literal_current_window_inclusive_days']==31
    assert (date(2026,11,15)-date(2026,8,18)).days+1==90
    assert len({e['dedup_key']for e in events})==len(events)
    assert len({e['id']for e in events})==len(events)
    for e in events:
        assert e['canonical_id']is None and not e['production_news_eligible']
        assert set(e['source_ids'])<=sources.keys()and set(e['actors'])<=ids
        assert e['publication_window']==window(e['publication_date'],True)
        assert e['event_window']==window(e['event_date']if e['event_date_precision']=='day'else None)
        assert e['retraction_status']and e['aliases']is not None
        assert e['interpretation']['counter_evidence']and e['interpretation']['semantic_type']=='insight'
    admitted=pack['Admission-and-Integration']
    assert admitted['owner_only']and not admitted['canonical_mutation']
    assert [r['source_id']for r in admitted['items']if r['visible_in_runtime']]==['FCA-H126']
    assert not any(r['canonical_evidence_accepted']for r in admitted['items'])
    return {'sources':len(sources),'actors':len(actors),'deep_dossiers':len(dossiers),'relationship_candidates':len(graph['edges']),
            'event_records':len(events),'current_window_publications':sum(e['publication_window']=='current_literal_window'for e in events),
            'prior_90_day_publications':sum(e['publication_window']=='prior_90_day_publication'for e in events),
            'runtime_source_releases':1,'canonical_imports':0,'source_bytes_archived':0}

if __name__=='__main__':print(json.dumps(validate(load()),indent=2))
