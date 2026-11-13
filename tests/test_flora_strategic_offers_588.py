"""Owner priority programmes preserve v1 lineage and existing verified controls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_offers_v1 import actor, pilot
from tests.test_flora_sales_pipeline import web
from tests.test_flora_offer_library_587 import preferences, adopt, refs
from cios.applications.flora import offer_library as library, offers
from cios.applications.flora.commercial_mission import resolve_commercial_mission, save_commercial_mission
from cios.applications.flora.storage import data_path

pytestmark=pytest.mark.real_security_boundary
ROOT=Path(__file__).resolve().parents[1]


def test_original_84_ids_content_and_source_references_remain_exactly_current():
    original=json.loads((ROOT/'docs/flora-runtime/offer-library-587/strategic-priorities/Original-84.json').read_text())
    rows={r['id']:r for r in library.catalogue()['offers']}
    assert len(rows)==89
    for identifier,checksum in original['rows_sha256'].items():
        row=rows[identifier]
        assert library.fingerprint(row)==checksum,identifier
        if row['stage']=='deep':
            ref={'id':identifier,'version':1,'digest':checksum,'taxonomy_version':1,
                 'classification':'seller-declared adoption of a general commercial method'}
            assert library.source_ref(row)==ref and library.current(ref),identifier


def test_five_priority_programmes_are_distinct_complete_and_discoverable():
    d=library.catalogue();ids=d['strategic_priorities'];rows=[library.template(i) for i in ids]
    assert len(ids)==len(set(ids))==5 and sum(r['stage']=='deep' for r in d['offers'])==29
    assert [r['name'] for r in rows]==['Enterprise Digital Transformation','AI-first Business Transformation','Enterprise Cybersecurity & Resilience','Complex Legacy Application Modernisation','Social Value & ESG Transformation']
    assert [r['id'] for r in library.suggestions(['consulting'])[:5]]==ids
    for term,identifier in [('digital transformation',ids[0]),('AI-first',ids[1]),('cybersecurity',ids[2]),('complex legacy',ids[3]),('ESG',ids[4]),('social value',ids[4])]:
        assert identifier in {r['id'] for r in library.suggestions(['consulting'],term)}
    for r in rows:
        assert r['taxonomy_version']==2 and r['version']==1 and library.current(library.source_ref(r))
        assert len(r['subindustries'])>1 and r['target_segments'] and r['disconfirming_evidence']
        assert len(r['structural_triggers'])>=2 and len(r['event_triggers'])>=2
        assert len(r['entry_plays'])==2 and len(r['validation_tests'])==2
        assert r['economic_value']['amount'] is None and all(r['economic_value'][k] for k in ['mechanisms','measures','method','costs','disconfirmation'])
        assert r['follow_on_opportunities'] and r['seller_validation']['proof_required']
        assert all(f['status'].startswith('Conditional hypothesis') for f in r['follow_on_opportunities'])
    assert len({r['economic_value']['method'] for r in rows})==5
    assert len({r['entry_plays'][0]['disconfirming_question'] for r in rows})==5
    cyber=rows[2];assert len(cyber['variants'])==3
    assert {'tech-cyber-01','tech-cyber-02'}<=set(cyber['adjacent_offer_ids'])
    assert 'tech-engineering-01' in rows[3]['adjacent_offer_ids']
    esg=rows[4];assert not esg['research_context_claim_ids']
    assert 'PPN 002 is not a universal UK' in esg['constraints'][0]


def test_customer_category_and_delivery_specialism_overlap_without_new_authority(pilot):
    d=library.catalogue();assert next(c for c in d['subindustries'] if c['id']=='consulting')['label']=='Digital Transformation & Consulting'
    assert all(c['label']!='Systems Integration' for c in d['subindustries'])
    e=pilot['employer'];h=pilot['seller']
    m=offers.configure_library(['consulting','engineering'],e['id'],e['version'],0,delivery_specialisms=['systems-integration'],headers=h)
    assert m.technology_subindustries==('consulting','engineering') and m.technology_delivery_specialisms==('systems-integration',)
    assert not m.industries and not offers.snapshot(headers=h)['offers']
    assert not offers.snapshot(headers=h)['studio_enabled']
    suggestions=library.suggestions(m.technology_subindustries,'Systems Integration',m.technology_delivery_specialisms)
    assert 'tech-consulting-02' in {r['id'] for r in suggestions} and len(suggestions)==len({r['id'] for r in suggestions})
    save_commercial_mission(h,{'executive_role':'Account lead','commercial_objective':'Preserve preferences'})
    assert resolve_commercial_mission(h).technology_delivery_specialisms==('systems-integration',)
    m=resolve_commercial_mission(h)
    m=offers.configure_library(['consulting'],e['id'],e['version'],m.version,headers=h)
    assert m.technology_delivery_specialisms==('systems-integration',)  # Legacy client omission preserves preference.
    m=offers.configure_library(['consulting'],e['id'],e['version'],m.version,delivery_specialisms=[],headers=h)
    assert not m.technology_delivery_specialisms
    with pytest.raises(PermissionError):offers.configure_library(['consulting'],e['id'],e['version'],0,delivery_specialisms=['systems-integration'],headers=pilot['outsider'])


@pytest.mark.parametrize('bad',[['unsupported'],['systems-integration','systems-integration'],'systems-integration',[True]])
def test_invalid_delivery_specialisms_fail_closed(bad):
    with pytest.raises(ValueError):library.specialisms(bad)


def test_five_priority_drafts_share_matching_and_require_independent_proof_review(pilot):
    preferences(pilot,('consulting','data','cyber','engineering'))
    ids=library.catalogue()['strategic_priorities'];rows=adopt(pilot,*ids)
    assert len(rows)==5 and all(r['state']=='private_draft' and not r['content']['evidence'] for r in rows)
    assert not offers.snapshot(headers=pilot['reviewer'])['offers']
    before=offers._path().read_bytes();account=offers.discover('account','lloyds',headers=pilot['seller'])
    assert len(account)==5
    for row in rows:
        a=next(r for r in account if r['offer_id']==row['id'])
        b=next(r for r in offers.discover('offer',row['id'],headers=pilot['seller']) if r['enterprise_slug']=='lloyds')
        assert a==b and a['economics'] is None and a['economic_value_hypothesis']['amount'] is None
        assert a['pipeline_eligible'] is False and a['credibility'].startswith('Private seller declaration')
        assert a['library_context']['disconfirming_evidence'] and a['library_context']['follow_on_opportunities']
    assert len({r['entry_play'] for r in account})==5
    esg=next(a for a in account if a['offer_id']==rows[4]['id'])
    assert esg['recommended_posture']=='research' and esg['why_account'].startswith('No account-specific indicator')
    cyber=next(a for a in account if a['offer_id']==rows[2]['id'])
    assert 'Envoy' in cyber['why_account']  # Existing controls, not a fabricated security gap.
    assert offers._path().read_bytes()==before
    r=offers.transition(rows[0]['id'],1,'submit',headers=pilot['seller'])
    with pytest.raises(ValueError):offers.transition(r['id'],r['version'],'approve','no seller proof',headers=pilot['reviewer'])
    r=offers.transition(r['id'],r['version'],'changes','Add permissioned delivery and rights proof',headers=pilot['reviewer'])
    r=offers.save_offer({'evidence':'Example permissioned delivery and rights reference; fixture only'},r['id'],r['version'],headers=pilot['seller'])
    r=offers.transition(r['id'],r['version'],'submit',headers=pilot['seller'])
    with pytest.raises(PermissionError):offers.transition(r['id'],r['version'],'approve','self',headers=pilot['seller'])
    approved=offers.transition(r['id'],r['version'],'approve','Example independent employer review',headers=pilot['reviewer'])
    assert approved['state']=='employer_approved' and approved['template_source']==rows[0]['template_source']
    assert not data_path('sales_pipeline','opportunities.json').exists()


def test_old_approved_library_offer_remains_eligible_when_new_catalogue_is_added(pilot):
    preferences(pilot,('engineering',));r=adopt(pilot,'tech-engineering-01')[0]
    assert r['template_source']['taxonomy_version']==1
    r=offers.save_offer({'evidence':'Example proof; fixture only'},r['id'],1,headers=pilot['seller'])
    r=offers.transition(r['id'],r['version'],'submit',headers=pilot['seller'])
    r=offers.transition(r['id'],r['version'],'approve','Example review',headers=pilot['reviewer'])
    assert next(o for o in offers.snapshot(headers=pilot['seller'])['offers'] if o['current'])['eligible']
    data=library.catalogue();data['version']=99
    from unittest.mock import patch
    with patch.object(library,'catalogue',return_value=data):
        assert library.current(r['template_source'])
        assert offers.discover('offer',r['id'],headers=pilot['seller'])


def test_native_specialism_onboarding_and_economic_playbook_are_accessible_and_private(pilot,web):
    e=pilot['employer']
    status,html,_=web('/flora/offers/start')
    assert status==200 and 'Delivery specialism (optional)' in html and 'Digital Transformation &amp; Consulting' in html
    assert 'name="specialisms" value="systems-integration"' in html
    payload={'employer_id':e['id'],'employer_version':e['version'],'mission_version':0,'primary':'consulting','specialisms':'systems-integration'}
    assert web('/flora/offers/onboard-preferences',payload|{'csrf':'forged'})[0]==403
    assert web('/flora/offers/onboard-preferences',payload|{'specialisms':'grant-employer'})[0]==403
    assert web('/flora/offers/onboard-preferences',payload)[0]==303
    m=resolve_commercial_mission(pilot['owner']);assert m.technology_delivery_specialisms==('systems-integration',)
    status,html,_=web('/flora/offers/start')
    assert status==200 and '89 offer types, 29 developed playbooks' in html and 'Economic value to validate' in html
    assert html.count('Sources & method</summary>')==1 and 'Automatic' not in html
    assert not data_path('sales_pipeline','opportunities.json').exists()
