"""Design validation over unchanged application owners; not a new runtime suite."""
from copy import deepcopy
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import prototype as d
import pytest

@pytest.mark.parametrize('stream',d.REGIONS)
def test_three_responsibilities_and_four_visual_selections(stream):
    for focus,*_ in d.REGIONS[stream]:
        html=d.render(d.State(stream,focus,focus))
        assert html.count('data-region="top"')==1 and html.count('data-region="left"')==1 and html.count('data-region="main"')==1
        assert html.count('data-region-key=')==4
        assert html.count('aria-current="true"')==1
        assert 'aria-label="Reading mode"' not in html and 'Context layers' not in html
        assert 'data-prototype="design-only"' in html
        assert '.pdf' not in html and 'primary_content_sha256' not in html
        body=html.split('<main ',1)[1]
        assert '<details' not in body
        if stream=='landscape':
            assert '£502.8bn' in body and '£6.6bn' in body
            assert 'SWOT quadrants' not in body and 'Strategy timeline' not in body
        elif stream=='inside':
            assert '£502.8bn' not in body and '£6.6bn' not in body and 'SWOT quadrants' not in body
        else:
            assert body.count('id="llf-swot-')==8
            assert '£6.6bn' not in body

@pytest.mark.parametrize('query',[
    {'stream':['secret']},{'stream':['landscape','forces']},{'focus':['data']},
    {'subject':['private']},{'workspace':['foreign']},{'analysis':['fi-private']},
    {'stream':['inside'],'focus':['funding']},{'focus':['retail','commercial']},
])
def test_invalid_or_private_state_is_not_a_design_selection(query):
    with pytest.raises(ValueError):d.resolve(query)


def test_frame_seams_are_restored_and_subject_survives_perspective_switch():
    left,top=d.panels._left,d.panels._top
    state=d.State('inside','operations','retail')
    html=d.render(state)
    assert 'From Retail Banking' in html and 'no divisional allocation is asserted' in html
    assert d.panels._left is left and d.panels._top is top
    assert 'subject=retail' in d.href(state,stream='forces')


def test_withdrawal_omits_dependent_measures_marker_and_themes():
    data=deepcopy(d.v.current_data(d.v.Context('lloyds','landscape')))
    next(s for s in data['sources'] if s['id']=='PR-LBG-Q326')['withdrawn']=True
    with patch.object(d.v,'current_data',lambda ctx:data):
        body=d.render(d.State())
        assert '£502.8bn' not in body and '£6.6bn' not in body
        assert 'class="change-marker"' not in body and 'No eligible reported measure' not in body
        forces=d.render(d.State('forces','competition','competition'))
        assert 'id="llf-swot-2"' not in forces
        assert 'id="llf-swot-0"' in forces


def test_bad_financial_definition_does_not_appear_as_group_measure():
    data=deepcopy(d.v.current_data(d.v.Context('lloyds','landscape')))
    next(c for c in data['claims'] if c['id']=='LBG-Q326-PROFIT')['metric_unit']='USD million; annual pretax profit'
    with patch.object(d.v,'current_data',lambda ctx:data):
        body=d.render(d.State())
        assert '£6.6bn' not in body and '£502.8bn' in body


def test_blocked_financial_projection_and_original_research_are_not_admitted():
    from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection
    assert public_factual_projection()=={}
    html=d.render(d.State('forces','renewal','renewal'))
    for forbidden in ('£11.084bn','£477.5bn','3.21%','integration progress is established','open procurement'):
        assert forbidden not in html
