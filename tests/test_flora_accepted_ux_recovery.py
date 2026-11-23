"""Accepted journey recovery over the existing Source, IAM and presentation owners."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path

import pytest

from cios.applications.flora import intelligence_presentation as p
from cios.applications.flora import visual_streams as v
from cios.applications.flora import visual_panels as panels
from cios.applications.flora import security
from cios.applications.flora.financial_intelligence import candidate_analytics as financial
from cios.applications.flora.public_routes import public_request_target, owner_inspection_request_target
from cios.applications.flora.security_store import digest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_research_intelligence import web
from tests.test_flora_uxr1_650 import main

pytestmark = pytest.mark.real_security_boundary
LLOYDS = '/enterprises/lloyds'
FLAGSHIP = {'stream': ['landscape'], 'detail': ['flagship']}


class DOM(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.nodes=[]; self.feed(html)
    def handle_starttag(self, tag, attributes):
        self.nodes.append((tag, dict(attributes)))


@pytest.mark.parametrize('path,streams', [('/', ('landscape','forces')),
    ('/industries/banking', ('landscape','forces')),
    (LLOYDS, ('landscape','inside','forces')),
    (v.EASYJET_ROUTE, ('landscape','inside','forces'))])
def test_one_experience_keeps_streams_identity_and_legacy_deep_links(path, streams):
    for stream in streams:
        query={'stream':[stream]}
        current=main(v.render(path,query))
        assert 'aria-label="Reading mode"' not in current
        assert current==main(v.render(path,{**query,'reading':['facts']}))
        assert current==main(v.render(path,{**query,'reading':['insight']}))
        assert 'data-stream="'+stream+'"' in current


def test_recovered_eight_themes_have_native_fallback_and_no_research_payload():
    body=main(v.render(LLOYDS,FLAGSHIP)); dom=DOM(body)
    ids={attrs['id'] for _,attrs in dom.nodes if attrs.get('id','').startswith('llf-swot-')}
    assert ids=={'llf-swot-'+str(i) for i in range(8)}
    assert all(any(attrs.get('href')=='#'+identifier for _,attrs in dom.nodes) for identifier in ids)
    assert all(label in body for label in ('Overview','Explore','Investigate'))
    assert '<details' not in body
    for forbidden in ('Reviewed excerpt','llf-sources','Evidence &amp; scope','canonical acceptance','.pdf'):
        assert forbidden not in body
    assert 'data-semantic-type="reported"' in body and 'data-semantic-type="insight"' in body
    assert 'Management target' in body
    assert 'cannot rank service quality' in body
    assert financial.public_factual_projection()=={}


def test_source_withdrawal_removes_dependent_themes_not_independent_enterprise_context(monkeypatch):
    before=main(v.render(LLOYDS,FLAGSHIP))
    assert 'id="llf-swot-0"' in before and 'id="llf-swot-6"' in before
    data=deepcopy(v.current_data(v.resolve(LLOYDS,FLAGSHIP)))
    next(s for s in data['sources'] if s['id']=='PR-LBG-ENVOY')['withdrawn']=True
    monkeypatch.setattr(v,'current_data',lambda context:data)
    after=main(v.render(LLOYDS,FLAGSHIP))
    assert 'id="llf-swot-0"' not in after and 'id="llf-swot-6"' not in after
    assert 'id="llf-swot-4"' in after
    assert 'Three businesses, different economics' in after


@pytest.mark.parametrize('state',['guest','forged','owner','expired','revoked-membership'])
def test_separate_inspection_retains_existing_owner_authority(authority,tmp_path,state):
    headers={}
    if state=='forged':headers={'X-Flora-Roles':'cios_owner','X-Flora-User':'synthetic-human'}
    if state in {'owner','expired','revoked-membership'}:
        store,token,_,headers,_=signed(authority,tmp_path)
        if state!='owner':
            with store.transaction() as db:
                if state=='expired':db.execute('UPDATE tokens SET expires=0 WHERE hash=?',(digest(token),))
                else:db.execute('UPDATE memberships SET active=0,version=version+1')
            assert security.verified_context(headers) is None
    query={**FLAGSHIP,'lens':['inspection']}
    if state=='owner':
        inspection=panels.research_inspection(LLOYDS,query,headers)
        assert 'Lloyds flagship research inspection' in inspection and 'Reviewed excerpt' in inspection
        assert 'Published' in inspection and 'cost of parallel running' in inspection
        assert '.pdf' not in inspection
    else:
        with pytest.raises(PermissionError):panels.research_inspection(LLOYDS,query,headers)
    assert 'llf-sources' not in main(v.render(LLOYDS,FLAGSHIP,headers))


def test_guest_http_reaches_public_journey_but_not_owner_or_private_selectors(web):
    canonical=LLOYDS+'?stream=landscape&detail=flagship'
    assert public_request_target(canonical)
    assert owner_inspection_request_target(canonical+'&lens=inspection')
    assert web(canonical)[0]==200
    for target in [canonical+'&lens=inspection',canonical+'&analysis=fi-private',
                   '/flora/sales/pipeline','/flora/offers']:
        assert web(target)[0]==403


def test_726_navigation_arrival_and_industry_specific_economics_survive():
    bank=main(v.render('/industries/banking',{}))
    lloyds=v.render(LLOYDS,{})
    air=v.render(v.EASYJET_ROUTE,{})
    for html in (lloyds,air):
        for label in ('Home','Industries','Enterprises','Opportunities','Pipeline'):
            assert label in html
        assert 'aria-label="Explore this enterprise"' in html and 'What’s changed' in html
    assert 'From funding to earnings' in lloyds and 'From seats to earnings' in air
    assert 'href="/industries/banking"' in lloyds
    assert 'Explore Lloyds' in lloyds and '£502.8bn' in lloyds
    assert '/enterprises/lloyds' in bank


def test_compatibility_cut_is_exact_and_does_not_accept_unreviewed_functions():
    from tools.research.eei2b_compatibility import checked_cut, UX_RECOVERY_BASE, UX_RECOVERY_CUTS
    root=Path(__file__).resolve().parents[1]
    for path,(_,functions) in UX_RECOVERY_CUTS.items():
        current=(root/path).read_bytes()
        previous=checked_cut(root,path,current,UX_RECOVERY_BASE,UX_RECOVERY_CUTS)
        assert previous!=current
        changed=current+b'\n# Unreviewed mutation\n'
        assert checked_cut(root,path,changed,UX_RECOVERY_BASE,UX_RECOVERY_CUTS)==changed
