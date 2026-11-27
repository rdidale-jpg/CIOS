"""Source-bound numerical product workload; never a financial allocation."""
from copy import deepcopy
import hashlib
import json
from decimal import Decimal

import pytest

from cios.applications.flora import leadership_agenda as agenda, lloyds_gold as gold
from cios.applications.flora.financial_intelligence import candidate_analytics as finance
from tests.test_flora_rud1_648 import retained as rud_retained, mutate
from tests.test_flora_living_enterprise_preview import http


@pytest.fixture
def retained(rud_retained):
    return rud_retained.with_name("FCA-Lloyds-Products-H126.json")

pytestmark = pytest.mark.real_security_boundary
SID = 'FCA-LLOYDS-PRODUCTS-H126'


def source(data):
    return next(s for s in data['sources'] if s['id'] == SID)


def main(detail='service-bankcards'):
    return gold.render({'focus':['economics'],'detail':[detail]},canonical=True).split('<main ',1)[1].split('</main>',1)[0]


def test_actual_new_product_cells_reconcile_without_claiming_financial_results():
    rows=agenda.lloyds_service_products()
    assert len(rows)==6
    assert [tuple(f.value for f in r[2]) for r in rows]==[
        (Decimal(115687),Decimal(115798),Decimal('66.37')),
        (Decimal(31),Decimal(33),Decimal('30.30')),
        (Decimal(2679),Decimal(2680),Decimal('62.57')),
        (Decimal(339),Decimal(324),Decimal('11.42')),
        (Decimal(26),Decimal(26),Decimal('19.23')),
        (Decimal(118762),Decimal(118861),Decimal('66.12'))]
    assert sum(r[2][0].value for r in rows[:-1])==rows[-1][2][0].value
    html=main()
    assert all(s in html for s in ('115,687','115,798','66.37%','97.4%','Commercial investigation','not cost or customer incidence'))
    assert '66.12% of received' not in html and '£115,687' not in html
    assert finance.public_factual_projection()=={}
    assert 'Open Government Licence v3.0' in html
    assert 'financial_statement' not in html and '<details' not in html


@pytest.mark.parametrize('flag',['owner_only','withdrawn','revoked','stale','superseded','contradictory'])
def test_source_lifecycle_removes_chart_prose_calculations_and_inspection(retained,flag):
    mutate(retained,lambda d:source(d).__setitem__(flag,True))
    assert agenda.lloyds_service_products()==()
    for detail in ('service-workload','service-bankcards','costs','sources'):
        body=main(detail)
        assert '115,687' not in body and '97.4%' not in body and 'Which banking-and-card complaint journeys' not in body
    assert '502.8' in main('funding')  # Unrelated eligible source remains.


@pytest.mark.parametrize('change',[
    {'publisher':'Lloyds Banking Group plc'}, {'reporting_period':'FY2026'},
    {'publication_date':'2026-10-23'}, {'text_sha256':'0'*64},
    {'rights':{'basis':'ordinary_public_factual_analysis'}}, {'restrictions':['private working use']},
    {'third_party_material':True}, {'retained_form':'copied_report'},
])
def test_source_integrity_scope_or_use_change_denies_new_output(retained,change):
    mutate(retained,lambda d:source(d).update(change))
    assert agenda.lloyds_service_products()==()
    assert '115,687' not in main()


@pytest.mark.parametrize('field,value',[
    ('received',115688),('upheld','NaN'),('upheld','101'),('received',True),
    ('period','1 January–30 September 2026'),('scope','Group Retail'),
    ('name','Bank of Scotland plc'),('product','Retail'),('currency','GBP'),
])
def test_unbound_or_incompatible_product_axis_cannot_publish(retained,field,value):
    mutate(retained,lambda d:next(r for r in d['service_profiles'] if r['selection']=='lloyds-service-bankcards').__setitem__(field,value))
    assert agenda.lloyds_service_products()==()


@pytest.mark.parametrize('case',['duplicate-source','duplicate-row','wrong-product-locator','non-reconciling-total'])
def test_ambiguity_column_collision_and_contradiction_fail_closed(retained,case):
    def change(d):
        s=source(d)
        if case=='duplicate-source':d['sources'].append(deepcopy(s))
        elif case=='duplicate-row':d['service_profiles'].append(deepcopy(next(r for r in d['service_profiles'] if r['selection']=='lloyds-service-bankcards')))
        elif case=='wrong-product-locator':s['excerpts'][0]['locator']=s['excerpts'][0]['locator'].replace('Banking and credit cards','Home finance')
        else:
            s['fact_bindings'][0]['facts']['received']=115688
            next(r for r in d['service_profiles'] if r['selection']=='lloyds-service-bankcards')['received']=115688
            s['excerpts'][0]['quote']='115,688'
            from cios.applications.flora.research_intelligence import model
            p=model.REPO/s['text_path'];text=p.read_text().replace('115,687','115,688');p.write_text(text);s['text_sha256']=hashlib.sha256(text.encode()).hexdigest()
    mutate(retained,change)
    assert agenda.lloyds_service_products()==()


def test_corrected_source_revision_changes_all_dependent_output(retained):
    def correction(d):
        s=source(d)
        from cios.applications.flora.research_intelligence import model
        p=model.REPO/s['text_path'];text=p.read_text()
        # Correct the published product allocation, preserving the common total.
        for key,new,old,index in [('bankcards',115000,115687,0),('insurance',1026,339,9)]:
            selection='lloyds-service-'+key
            next(r for r in d['service_profiles'] if r['selection']==selection)['received']=new
            next(b for b in s['fact_bindings'] if b['key']==selection)['facts']['received']=new
            s['excerpts'][index]['quote']=format(new,',')
            text=text.replace(format(old,','),format(new,','))
        p.write_text(text);s['text_sha256']=hashlib.sha256(text.encode()).hexdigest()
    mutate(retained,correction)
    body=main()
    assert '115,000' in body and '96.8%' in body and '115,687' not in body and '97.4%' not in body


@pytest.mark.parametrize('detail',['service-workload','service-bankcards','service-pensions','service-mortgages','service-insurance','service-investments'])
def test_public_direct_views_do_not_discover_private_runs(http,detail):
    status,headers,html=http('/enterprises/lloyds?focus=economics&detail='+detail)
    assert status==200 and 'no-store' in headers.get('Cache-Control','')
    assert '115,687' in html and 'Workspace records' not in html
    status,_,html=http('/enterprises/lloyds?focus=economics&detail='+detail+'&analysis=fi-private')
    assert status==403 and '115,687' not in html


def test_inspection_explains_calculation_without_pdf_link_or_held_projection():
    html=main('sources')
    assert '115687 / 118762 × 100' in html and 'Reported' in html
    assert 'https://www.fca.org.uk/data/firm-level-complaints-data-sortable-table' in html
    assert '2026-lbg-q3-ims.pdf' not in html and '£11,084' not in html


def test_additive_research_preserves_every_historical_pin_and_exact_comparator():
    import ast,subprocess
    from pathlib import Path
    from tools.research import history_integrity as history
    root=Path(__file__).resolve().parents[1]
    path='tools/research/history_integrity.py'
    before=ast.parse(subprocess.check_output(['git','show','6b10935a31079d27fe00c88bf241d3d6bf1e3c98:'+path],cwd=root))
    after=ast.parse((root/path).read_text())
    old={n.name:ast.dump(n,include_attributes=False) for n in before.body if isinstance(n,ast.FunctionDef)}
    new={n.name:ast.dump(n,include_attributes=False) for n in after.body if isinstance(n,ast.FunctionDef)}
    assert all(new[k]==value for k,value in old.items() if k!='verify_history')
    constants=lambda t:{n.targets[0].id:ast.dump(n.value,include_attributes=False) for n in t.body if isinstance(n,ast.Assign)}
    assert constants(before)==constants(after)
    # The comparator still rejects unknown/mutated files; new numerical Sources
    # are exact additive bytes, never a refresh of historical expectations.
    expected=history.approved_history(root)
    with pytest.raises(AssertionError):history.compare_history(expected,{**expected,'unapproved':b'bad'})
    with pytest.raises(AssertionError):history.compare_history(expected,{**expected,next(iter(expected)):b'changed'})
    assert history.verify_history(root)['old_review_records_retained']


def test_new_history_compatibility_cut_is_exact_and_does_not_accept_mutations(tmp_path):
    import subprocess
    from pathlib import Path
    from tools.research.ux_unify_compatibility import predecessor
    root=Path(__file__).resolve().parents[1];path='tools/research/history_integrity.py'
    # Compare against the already established predecessor of the prior main
    # checker; do not update any historical pins to the new source additions.
    expected=json.loads((root/'docs/flora-runtime/rud1-648/Owner-Evolution.json').read_text())[path]['reviewed_sha256']
    assert hashlib.sha256(predecessor(root,path)).hexdigest()==expected
    (tmp_path/'tools/research').mkdir(parents=True)
    changed=(root/path).read_bytes()+b'\n# unreviewed mutation\n'
    (tmp_path/path).write_bytes(changed)
    assert predecessor(tmp_path,path)==changed
