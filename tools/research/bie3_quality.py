"""Read-only Issue637 review compatibility, not an admission or model engine.

Uses existing contract owners without approved IDs, Observation construction,
staging, private-record lookup or persistence. Research review JSON is never
loaded by the application renderer.
"""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import hashlib,json,re
from pathlib import Path
from urllib.parse import urlsplit
import sys

# Standalone CLI (including hosted CI) must resolve this checkout without an
# inherited PYTHONPATH or dependence on the caller's working directory.
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from cios.applications.flora.memory.service import FactualClaim,validate_factual_claim,CLAIM_VOCABULARY
from cios.applications.flora.memory.source_contracts import contract_for
from cios.applications.flora.financial_intelligence.schema import NumericFactValue
from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
from cios.applications.flora.blueprint_import.researcher_profile_adapter import adapt_researcher_payload,contract_checksum
from cios.applications.flora.research_intelligence.source_import import official_url
from cios.applications.flora import leadership_agenda as agenda

ROOT=Path(__file__).resolve().parents[2];PACK=ROOT/'docs/flora-runtime/bie3'

def load(root=PACK):
    return {name:json.loads((Path(root)/(name+'.json')).read_text())for name in
        ('Source-Review','Claim-Proposals','Commercial-Cases','Reconciliations','BIE2-Dispositions')}

def existing_candidate(row):
    """No guessed ID: the owning validator must refuse these unbound proposals."""
    return FactualClaim('',row['claim_type'],row['statement'],row['proposed_model_domain'],
        row['proposed_attribute'],row['reported_value'],row['unit'],row['currency'],
        row['reporting_period'],row['measurement_state'],'',row['source_locator'],50,row['id'])

def admission_report(pack):
    """Return observations about current gates, never authority decisions."""
    sources={s['id']:s for s in pack['Source-Review']};rows=[]
    for c in pack['Claim-Proposals']:
        s=sources[c['source_ids'][0]]
        try:official_url(s['url']);host=True
        except ValueError:host=False
        contract=contract_for(s['source_type']);permitted_type=c['claim_type']in contract.permitted_claim_types
        try:validate_factual_claim(existing_candidate(c));binding='unexpectedly_valid'
        except ValueError as exc:binding=str(exc)
        rows.append(dict(claim_id=c['id'],actor_ref=c['actor_ref'],subject_name=c['subject_name'],
            source_ids=c['source_ids'],original_url=s['url'],source_locator=c['source_locator'],
            reviewed_cell_index=c.get('reviewed_cell_index'),reporting_period=c['reporting_period'],
            currency=c['currency'],unit=c['unit'],accounting_basis=c['accounting_basis'],
            researched_candidate=True,source_verified=c['source_verified'],technical_host_admitted=host,
            exact_use_rights='unresolved; not a finding that the factual measurement is prohibited',
            source_permitted=False,canonical_owner_accepted='UNVERIFIED',visible_runtime=False,
            canonical_target_id=None,canonical_evidence_id=None,canonical_observation_id=None,
            proposed_existing_owner='EI-001 Enterprise Model via existing Evidence / memory / Blueprint owners',
            source_contract=s['source_type'],source_type_foundation_compatible=bool(permitted_type and contract.foundation_eligible),
            claim_type_supported=permitted_type,factual_binding_result=binding,
            proposed_attribute=c['proposed_attribute'],publication_date=c['publication_date'],
            publication_date_limitation='No universal null-publication rejection is invented. Existing Researcher event handoff needs complete publication day; financial provenance allows null with explicit limitations.',
            original_byte_extent='No archive retained. Reviewed web excerpts can support candidates under the existing owner; a future original-PDF table-adapter route needs real document bytes/hash, never a synthetic archive.',
            owner_actions=['Resolve exact document/fact/attribution/link use rights and existing source-admission decision',
                          'Use real authorised workspace identity and receipt reconciliation; public aliases are not target IDs',
                          'Review each supported Evidence assertion separately, then existing mapping/plan/promotion controls if separately authorised'],
            additional_contract_action=None if permitted_type else 'Current investor-results foundation contract does not permit this event/structure update; retain context or obtain a qualifying original under existing contracts; do not relabel the source'))
    package=agenda._eai_release('bank-outcomes')
    visible_ids=set()
    for selected,(name,_,ids)in agenda.BANK_SERVICE.items():
        selected_rows=agenda.agenda('banking',selected=selected)
        if any(r.key=='service-landscape'and r.title==name+': complaint activity and resolution'for r in selected_rows):
            visible_ids.update(ids)
    if package:
        for c in package['claims']:
            rows.append(dict(claim_id=c['id'],actor_ref=None,subject_name=c['entity_scope'],
                researched_candidate=True,source_verified=True,technical_host_admitted=True,
                exact_use_rights='Existing FCA numerical Data OGL permission; narrative excluded',source_permitted=True,
                canonical_owner_accepted='UNVERIFIED',visible_runtime=c['id']in visible_ids,canonical_target_id=None,
                canonical_evidence_id=None,canonical_observation_id=None,proposed_attribute=None,
                publication_date='2026-10-22',canonical_approval_executed=False,
                existing_owner='Banking research assessment on disposable copy → existing agenda / Statement / Main',
                owner_actions=['Review this bounded public presentation separately from any canonical Evidence acceptance']))
    return {'owner_review_only':True,'approval_executed':False,'canonical_writes':0,'rows':rows,
            'reused_existing_public_claims':['BIE2-HSBC-RECEIVED','BIE2-NATWEST-RECEIVED'],
            'new_runtime_claim_ids':[c['id']for c in (package or{}).get('claims',[])]}

def compatibility(pack):
    """Shared Researcher profile mapping only; no import/package receipt."""
    out=[]
    for case in pack['Commercial-Cases']:
        selected=[c for c in pack['Claim-Proposals']if c['id']in case['fact_ids']]
        # Omitting id is deliberate: the adapter's producer id alias must not
        # accidentally become a real workspace/canonical Enterprise identifier.
        producer={'name':case['subject'],'executive_overview':{'what':case['economic_mechanism']},
                  'financial_intelligence':{'candidate_claim_refs':[c['id']for c in selected if c['claim_type']=='financial_metric_reported']},
                  'evidence':[]}
        klass,payload=adapt_researcher_payload('enterprise_twin',producer)
        assert klass=='enterprise_twin'and not payload.get('enterprise_id')
        out.append({'actor_ref':case['actor_ref'],'owner_class':klass,'profile_checksum':contract_checksum(),
                    'mapped_fields':payload['mapping_diagnostics']['mapped_fields'],
                    'unmapped_fields':payload['mapping_diagnostics']['unmapped_fields'],
                    'canonical_enterprise_id':None,'accepted_evidence_refs':[],
                    'status':'source-preserving mapping preview only; no receipt, staging, approval or promotion',
                    'candidate_claim_refs':producer['financial_intelligence']['candidate_claim_refs']})
    return out

def validate(pack):
    sources={s['id']:s for s in pack['Source-Review']};assert len(sources)==len(pack['Source-Review'])==10
    for s in sources.values():
        u=urlsplit(s['url']);assert u.scheme=='https'and u.hostname and not u.username and not u.password and not u.query
        assert s['original_bytes_sha256']is None and not s['canonical_approval_executed']
        assert s['retrieved_on']=='2026-11-15'and s['retrieval_reference']
        if s['publication_date']:assert date.fromisoformat(s['publication_date'])<=date(2026,11,15)
        if s.get('retained_excerpt_path'):
            p=(ROOT/s['retained_excerpt_path']);assert p.resolve().is_relative_to(PACK.resolve())and not p.is_symlink()
            text=p.read_text();assert hashlib.sha256(text.encode()).hexdigest()==s['retained_excerpt_sha256']
            assert sum(len(e['quote'].split())for e in s['reviewed_cells'])<=25
            assert all(e['locator']and e['quote']in text for e in s['reviewed_cells'])
    claims={c['id']:c for c in pack['Claim-Proposals']};assert len(claims)==len(pack['Claim-Proposals'])==24
    original=json.loads((ROOT/'docs/flora-runtime/bie2/Actor-Register.json').read_text())
    actors={a['id']for a in original['actors']};seen=set()
    for c in claims.values():
        assert c['actor_ref']in actors and set(c['source_ids'])<=sources.keys()
        assert all(c[k]is None for k in ('canonical_target_id','canonical_evidence_id','canonical_observation_id','canonical_model_id'))
        assert c['canonical_record_presence']=='UNVERIFIED'
        assert c['owner_decision']=={'selected':None,'recorded':False,'executed':False}
        assert c['source_verified']and c['semantic_type']=='reported'and c['pipeline_effect']=='none'
        assert c['states']=={'researched_candidate':True,'source_permitted':False,'owner_accepted_canonical':'UNVERIFIED','visible_runtime':False}
        assert validate_atomic_statement(c['statement']).atomic,c['id']
        spec=CLAIM_VOCABULARY[c['claim_type']]
        assert c['proposed_model_domain']==spec['domain']and c['proposed_attribute'].startswith(spec['attribute_prefix'])
        assert c['measurement_state']in spec['states']
        with_binding=existing_candidate(c)
        try:validate_factual_claim(with_binding)
        except ValueError as exc:assert 'canonical_enterprise_id'in str(exc)
        else:raise AssertionError('Unbound candidate cannot become validated canonical memory')
        if c['reported_value']is not None:
            NumericFactValue(amount=Decimal(str(c['reported_value'])),scale=c['unit']if c['currency']else None,
                             unit=None if c['currency']else c['unit'],currency=c['currency'])
            cell=sources[c['source_ids'][0]]['reviewed_cells'][c['reviewed_cell_index']]
            raw=cell['quote'].replace(',','').rstrip('%')
            parsed=-Decimal(raw[1:-1])if raw.startswith('(')and raw.endswith(')')else Decimal(raw)
            assert Decimal(str(c['reported_value']))==parsed
            assert c['measurement_state']=='actual'
        key=(c['actor_ref'],c['proposed_attribute'],c['reporting_period']);assert key not in seen;seen.add(key)
        for field in ('publication_date','event_date','effective_date','period_start','period_end','balance_sheet_date'):
            if c.get(field):assert date.fromisoformat(c[field])<=date(2026,11,15)
    assert claims['BIE3-SA-PARTVII']['effective_date']is None
    assert claims['BIE3-SA-PARTVII']['expected_period']=='H1 2027'
    assert claims['BIE3-SA-PARTVII']['underlying_phase_state']=='planned_conditional'
    assert claims['BIE3-SA-PARTVII']['measurement_state_meaning']=='Current disclosure, not completed future transfer'
    for c in claims.values():
        if c['id'].startswith('BIE3-HS-'):
            assert c['actor_ref']=='actor:hsbc-uk'and c['currency']=='USD'
            assert c['accounting_basis'].startswith('Reported US-dollar legal-bank results;')
        if c['id'].startswith('BIE3-NW-'):assert c['actor_ref']=='actor:nw-group'
        if c['id'].startswith('BIE3-SA-'):
            expected='actor:santander-uk'if c['id']in {'BIE3-SA-ACQUISITION','BIE3-SA-EMPLOYER','BIE3-SA-PARTVII'}else'actor:san-group'
            assert c['actor_ref']==expected
    assert claims['BIE3-NW-DEPOSITS-TOTAL']['reported_value']=='454.3'
    assert claims['BIE3-NW-DEPOSITS-EX-CENTRAL']['reported_value']=='453.4'
    assert 'excluding central items'in claims['BIE3-NW-DEPOSITS-EX-CENTRAL']['accounting_basis']
    assert claims['BIE3-SA-TSB-PBT']['period_start']=='2026-05-01'
    assert claims['BIE3-SA-TSB-COST']['period_start']=='2026-05-01'
    assert claims['BIE3-SA-OPEX']['reported_value']==-2122
    assert claims['BIE3-SA-RESTRUCT']['reported_value']==-495
    for calc in pack['Reconciliations']['items']:
        inputs=[claims[i]for i in calc['input_ids']]
        assert len({(c['actor_ref'],c['currency'],c['unit'])for c in inputs})==1
        if calc['operator']=='signed_sum':
            assert len({(c['reporting_period'],c['period_start'],c['period_end'])for c in inputs})==1
            v=sum(Decimal(str(c['reported_value']))for c in inputs)
            assert v==Decimal(str(claims[calc['reported_result_id']]['reported_value']))==Decimal(calc['expected'])
        else:
            assert [c['balance_sheet_date']for c in inputs]==['2026-09-30','2025-12-31']
            assert all('.published_stock.'in c['proposed_attribute']for c in inputs)
            assert Decimal(str(inputs[0]['reported_value']))-Decimal(str(inputs[1]['reported_value']))==Decimal(calc['expected'])==Decimal('110.9')
    report=admission_report(pack)
    assert sum(r['source_permitted']for r in report['rows'])==7
    assert sum(r['visible_runtime']for r in report['rows'])==7
    assert all(r['factual_binding_result']!='unexpectedly_valid'for r in report['rows']if 'factual_binding_result'in r)
    assert not any(r['technical_host_admitted']for r in report['rows']if 'factual_binding_result'in r)
    assert len(compatibility(pack))==3
    return {'reviewed_sources':10,'source_verified_research_proposals':24,'new_permitted_runtime_claims':7,
            'reused_public_received_claims':2,'differentiated_commercial_cases':3,
            'new_canonical_approvals':0,'new_canonical_imports':0,'real_canonical_receipt_status':'UNVERIFIED'}

if __name__=='__main__':print(json.dumps(validate(load()),indent=2))
