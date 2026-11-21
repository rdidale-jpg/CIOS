#!/usr/bin/env python3
"""Read-only research-pack QA, never a source registry or intelligence engine.

No network, authority producer, promotion or run creation. Arithmetic below
checks fixed documentary reconciliations; future runtime uses existing Financial
recipes. Adversarial source checks reuse existing working_restricted semantics.
"""
from collections import Counter
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
import re
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
BASE='fbac4c37910ed07b2baa516e1a5c8d7f329086de'
AS_OF=date(2026,11,18)


def read(name):return json.loads((HERE/name).read_text())


def unique(rows,key='id'):
    assert all(isinstance(r,dict) and isinstance(r.get(key),str) for r in rows)
    result={r[key]:r for r in rows}
    assert len(result)==len(rows),'Duplicate review identity'
    return result


def research_available(claim,sources):
    """QA fixture for retained candidate availability, NOT public authorisation."""
    from cios.applications.flora.research_intelligence.source_import import working_restricted
    def metadata(record):
        # Documentation freshness is structured; existing restriction helper takes a string.
        # Copy for isolated QA only. No mutation or runtime import contract is introduced.
        copy=dict(record)
        if isinstance(copy.get('freshness'),dict):copy['freshness']=copy['freshness'].get('status')
        return copy
    if working_restricted(metadata(claim)):return False
    return all(sid in sources and not working_restricted(metadata(sources[sid]))
        and sources[sid]['rights']['use_decision']!='excluded' for sid in claim['source_ids'])


def reconcile(recipe,measurements):
    inputs=[measurements[k] for k in recipe['inputs']]
    target=measurements[recipe['target']]
    def perimeter(m):return (m['subject_ref'],m['currency'],m['unit'],m['scale'],m['period'],m['state'])
    assert all(perimeter(m)==perimeter(target)for m in inputs),'Incompatible entity/period/currency/unit/state'
    assert target['period']['kind']=='duration','A stock cannot enter this flow reconciliation'
    assert all(Decimal(m['value']).is_finite()for m in [*inputs,target])
    # Mixed accounting bases are permitted only in the exact documented bridge.
    expected_basis={
      'BE-CALC-LBG-NET':['underlying']*3,
      'BE-CALC-LBG-UPBT':['underlying','underlying_excluding_remediation','separately_presented','underlying'],
      'BE-CALC-LBG-SPBT':['underlying','underlying_to_statutory_adjustment','underlying_to_statutory_adjustment'],
      'BE-CALC-NBS-UPBT':['underlying']*3,
      'BE-CALC-NBS-SPBT':['underlying']+['underlying_to_statutory_adjustment']*3}
    assert [m['accounting_basis']for m in inputs]==expected_basis[recipe['id']],'Wrong accounting definition'
    assert target['accounting_basis']==('statutory' if recipe['id'].endswith('SPBT') else 'underlying'),'Wrong target accounting definition'
    assert all(m['state']=='actual' for m in [*inputs,target]),'Targets or forecasts are not actual results'
    result=sum(Decimal(m['value'])*sign for m,sign in zip(inputs,recipe['signs'],strict=True))
    assert result==Decimal(recipe['expected'])==Decimal(target['value']),'Financial reconciliation failed'
    return result



def cloud_segment_ratio(recipe,measurements):
    """Isolated check of the documented global Cloud ratio, not EMEA economics."""
    a,b=[measurements[recipe[k]] for k in ('numerator','denominator')]
    fields=('subject_ref','currency','period','scale','unit','state','source_id')
    assert all(a[k]==b[k] for k in fields),'Incompatible ratio inputs'
    assert a['subject_ref']=='google-segment','Brand/legal entity cannot inherit segment profit'
    assert a['currency']=='USD' and a['unit']=='currency' and a['scale']=='millions'
    assert a['period']['kind']=='duration' and a['state']=='actual'
    assert a['accounting_basis']==b['accounting_basis']=='segment_operating'
    values=[Decimal(m['value']) for m in (a,b)]
    assert all(v.is_finite() for v in values) and values[1]>0
    result=(values[0]/values[1]*100).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
    assert str(result)==recipe['expected']=='36.2'
    return result


def validate_edge(edge,entities,claims,sources):
    a,b=entities[edge['subject_ref']],entities[edge['object_ref']]
    assert edge['claim_ids'] and all(c in claims for c in edge['claim_ids'])
    assert edge['canonical_acceptance'] is False and edge['import_executed'] is False
    pred=edge['predicate']
    if pred in {'registered_person_with_significant_control_of','lists_as_guarantor_member'}:
        assert a['object_kind']==b['object_kind']=='legal_person','Exact legal parties required'
    if pred=='lists_as_guarantor_member':
        assert a['ref']=='payuk' and b['ref'] in {'lloyds-bank','nationwide'}
        text=(HERE/sources['BE-S-PAY-GUARANTORS']['retained_path']).read_text()
        assert b['name'] in text,'No legal-party match by alias/brand'
    if pred=='registered_person_with_significant_control_of':
        assert (a['ref'],b['ref'])==('lbg','lloyds-bank')
    if pred=='reported_envoy_collaboration_with':
        assert a['ref']=='lbg' and b['object_kind']=='brand','Brand collaboration is not a legal contract'
    if pred=='designates_critical_third_party':
        assert a['ref']=='hmt' and b['ref']=='google-emea' and b['object_kind']=='legal_person'
        assert edge['dates']['published']=='2026-07-10' and edge['dates']['effective']=='2026-07-13'
    if pred=='reported_operator_of':
        assert a['ref']=='payuk' and b['object_kind']=='payment_system'
    if pred=='reported_provides_switching_service':
        assert a['ref']=='payuk' and b['object_kind']=='switching_service'
    assert pred in {'registered_person_with_significant_control_of','lists_as_guarantor_member',
      'reported_envoy_collaboration_with','designates_critical_third_party','reported_operator_of',
      'reported_provides_switching_service','issuer_lists_affiliate_for_maintenance_support',
      'issuer_lists_distinct_affiliate','has_consolidated_reporting_perimeter'},'Unreviewed predicate'
    return True


def validate():
    links=0
    for doc in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if target.startswith('https://'):continue
            assert (doc.parent/target.split('#')[0]).resolve().is_file(),'Broken documentary link: '+target
            links+=1
    changes=subprocess.check_output(['git','diff','--name-status',BASE,'HEAD'],cwd=ROOT,text=True).splitlines()
    for change in changes:
        status,path=change.split('\t',1)
        assert status=='A' and (path.startswith('docs/flora-runtime/bnk-ent-1/') or path=='tests/test_flora_bnk_ent_1_664.py'),'Out-of-scope change: '+change
    preservation=read('Preserved-Inputs.json')
    assert preservation['base']==BASE
    for path,digest in preservation['files'].items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==digest,'Existing owner changed: '+path
    entities=unique(read('Identity-Crosswalk.json')['entities'],'ref')
    assert all(e['canonical_id']is None for e in entities.values())
    assert entities['google-emea']['registration']=='660412' and entities['google-ireland']['registration']=='368047'
    assert entities['google-brand']['object_kind']=='brand' and entities['google-segment']['object_kind']=='reporting_perimeter'
    assert entities['nationwide-group']['object_kind']=='reporting_perimeter'
    assert all(entities[k]['object_kind']!='legal_person'for k in ('fps','bacs','ics','cass'))
    assert read('Identity-Crosswalk.json')['collisions'][0]['identifier']=='BK-ENT-003'
    sources=unique(read('Source-Ledger.json')['sources'])
    quotes=Counter()
    for s in sources.values():
        u=urlsplit(s['url']);assert u.scheme=='https' and not u.username and not u.password
        assert not s['canonical_acceptance'] and s.get('original_content_sha256')is None
        if s.get('publication_date'):assert date.fromisoformat(s['publication_date'])<=AS_OF
        if 'retained_path'in s:
            path=(HERE/s['retained_path']).resolve();assert path.is_relative_to(HERE/'excerpts')
            assert sha256(path.read_bytes()).hexdigest()==s['retained_text_sha256']
            quotes[s['url']]+=len(path.read_text().split())
        else:
            p=(ROOT/s['existing_text_path']).resolve();assert p.is_relative_to(ROOT/'enterprise-knowledge')
            assert sha256(p.read_bytes()).hexdigest()==s['retained_text_sha256']
    assert all(n<=25 for n in quotes.values()),'Excessive retained expression'
    claims=unique(read('Claims.json')['claims'])
    for c in claims.values():
        assert c['subject_ref']in entities and c['source_ids'] and set(c['source_ids'])<=set(sources)
        assert all(sources[sid]['rights']['use_decision']!='excluded'for sid in c['source_ids']),'Excluded source used as business evidence'
        assert c['semantic_type']in {'reported','calculated','estimated','assumed','insight','hypothesis'}
        assert c['status']=='candidate_not_canonical' and not c['qualified_material_pressure'] and not c['pipeline_eligible']
        assert c['entity_perimeter'] and c['period'] and c['caveat']
        if c['semantic_type']in {'insight','hypothesis'}:assert c['reasoning'] and c['counter_evidence'] and c['falsifier']
        for field in ('published','event','effective'):
            if c['dates'][field]:assert date.fromisoformat(c['dates'][field])<=AS_OF
    caps=unique(read('Capability-Maps.json')['capabilities'])
    assert Counter(c['subject_ref']for c in caps.values())=={'lbg':6,'nationwide':6,'google-brand':6,'payuk':6}
    for c in caps.values():
        assert set(c['context_claim_ids'])<=set(claims) and c['structure_status'].startswith('conceptual')
        assert not c['verified_capability_supplier_edges'] and not c['material_pressure_qualified']
        for field in ('economic_mechanism','people_and_accountability','process','information','technology_and_dependencies'):assert c[field]
    finances=read('Financial-Reconciliation.json');measurements=unique(finances['measurements'])
    for m in measurements.values():assert m['subject_ref']in entities and m['source_id']in sources and Decimal(m['value']).is_finite()
    values={r['id']:str(reconcile(r,measurements))for r in finances['recipes']}
    assert values['BE-CALC-NBS-UPBT']=='2026' and values['BE-CALC-NBS-SPBT']=='1490'
    assert finances['integration_cost_memo']['amount']=='127' and finances['integration_cost_memo']['must_not_be_subtracted_again']
    margin=cloud_segment_ratio(finances['ratio_review'],measurements)
    edges=read('Relationship-Handoff.json')['edges']
    unique(edges)
    for e in edges:validate_edge(e,entities,claims,sources)
    assert all(c['disposition'].startswith('reject_')for c in read('Relationship-Handoff.json')['negative_cases'])
    for doc in ('Lloyds.md','Nationwide.md','Google-Cloud.md','Pay-UK.md'):
        text=(HERE/doc).read_text();assert 'Economic' in text or 'economic' in text
        assert 'Falsifier' in text and ('Specific questions' in text or 'Specific Questions' in text)
    frameworks=read('Capability-Maps.json')['frameworks']
    assert frameworks['EI-001']=='Draft' and frameworks['EIF-001'].startswith('Review')
    return {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'base':BASE,'sources':len(sources),'new_review_records':sum('retained_path'in s for s in sources.values()),
      'claims':len(claims),'measurements':len(measurements),'reconciliations':values,'cloud_segment_ratio':str(margin),
      'capabilities':len(caps),'relationship_proposals':len(edges),'preserved_files':len(preservation['files']),
      'documentation_links':links,'additive_changed_files':len(changes),'canonical_writes':0,'runtime_changes':0,'source_permissions_added':0,'scope':'research_QA_not_public_admission_or_canonical_acceptance'}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
