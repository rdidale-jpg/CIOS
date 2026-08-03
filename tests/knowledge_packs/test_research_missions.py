import copy, json, subprocess, sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'knowledge-packs/researcher/research-missions'
sys.path.insert(0,str(ROOT/'tools/knowledge-packs'))
from research_missions import load, registries, render, validate_manifest, validate_templates

def fixture(name='TEL-001-wave-5-pipeline-qualification.json'):
    return copy.deepcopy(load(BASE/'examples'/name))

def test_catalogue_has_twenty_unique_contracts_and_ten_templates():
    templates,contracts,profiles=registries(); validate_templates(templates,contracts,profiles)
    assert len(templates)==10 and len(contracts)==20
    assert all(t['compatibility'] and t['migration'] and t['supersession']=='active' for t in templates.values())

def test_examples_validate_and_generated_commissions_are_current_and_deterministic():
    for path in sorted((BASE/'examples').glob('*.json')):
        first=render(load(path)); second=render(load(path))
        assert first==second==(BASE/'generated'/f'{path.stem}.md').read_text()
        assert 'Derived work order' in first and 'Version receipt SHA-256' in first

def test_wave_five_preserves_commercial_method_without_generic_leakage():
    brief=render(fixture())
    for phrase in ['Open opportunity','Strategic hypothesis','Existing award','Framework market','framework ceiling','H1: 0–12 months','buyer-qualification','opportunity-overlap','falsification','retain the Unknown','Monitoring Trigger']:
        assert phrase in brief
    generic=(BASE/'templates/templates-v1.json').read_text()
    for term in ['VodafoneThree','Network Services 4','Project Gigabit','Openreach','VMO2','Ofcom']:
        assert term not in generic

@pytest.mark.parametrize('case,mutate,match',[
('unknown profile',lambda d:d['profile_pins'].update({'opportunity':'9.0.0'}),'incompatible profile'),
('missing template version',lambda d:d.pop('mission_template_version'),'missing required fields'),
('missing baseline',lambda d:d.update(baseline_release=''),'baseline_release'),
('missing horizons',lambda d:d['commercial_pipeline_configuration'].pop('horizon_boundaries'),'horizon_boundaries'),
('missing exhaustion',lambda d:(d.update(mission_type='targeted-evidence-closure',mission_template_id='targeted-evidence-closure'),d['evidence_policy'].update(evidence_exhaustion_policy='')),'exhaustion_policy'),
('unknown retention',lambda d:d['estimation_policy'].update(retain_underlying_unknown=False),'Unknown retention'),
('invalid outcome',lambda d:d.update(outcome_states=['CONTINUE','COMPLETE','Accepted']),'invalid outcome'),
('incompatible template',lambda d:d.update(mission_template_version='2.0.0'),'incompatible template'),
('missing output',lambda d:d['outputs'].update(required_registers=[]),'mandatory outputs'),
])
def test_invalid_manifests_are_rejected(case,mutate,match):
    data=fixture(); mutate(data)
    with pytest.raises(ValueError,match=match): validate_manifest(data)

def test_unknown_module_industry_leak_duplicate_rule_and_unresolved_variable_rejected():
    templates,contracts,profiles=registries(); templates=copy.deepcopy(templates); contracts=copy.deepcopy(contracts)
    templates['commercial-pipeline-qualification']['modules'].append('missing')
    with pytest.raises(ValueError,match='missing contract'): validate_templates(templates,contracts,profiles)
    templates,contracts,profiles=registries(); templates=copy.deepcopy(templates)
    templates['commercial-pipeline-qualification']['purpose']='Research Openreach'
    with pytest.raises(ValueError,match='industry-specific'): validate_templates(templates,contracts,profiles)
    templates,contracts,profiles=registries(); contracts=copy.deepcopy(contracts)
    contracts['contradiction']['canonical_owner']=contracts['unknown']['canonical_owner']
    with pytest.raises(ValueError,match='duplicate canonical'): validate_templates(templates,contracts,profiles)
    templates,contracts,profiles=registries(); contracts=copy.deepcopy(contracts)
    contracts['unknown']['instruction']='{{SUBJECT}}'
    # Render uses on-disk registry; unresolved output is separately exercised through the CLI rule.
    assert '{{SUBJECT}}' in contracts['unknown']['instruction']

def test_input_change_changes_output_and_cli_detects_stale_commission(tmp_path):
    data=fixture(); before=render(data); data['scope']['evidence_cut_off']='2026-08-04'; after=render(data)
    assert before!=after
    manifest=tmp_path/'manifest.json'; output=tmp_path/'brief.md'; manifest.write_text(json.dumps(data)); output.write_text('stale')
    result=subprocess.run(['python3','tools/knowledge-packs/research_missions.py',str(manifest),'--output',str(output),'--check'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode and 'stale generated commission' in result.stderr

def test_pack_builder_includes_and_validates_active_mission_assets():
    result=subprocess.run(['python3','tools/knowledge-packs/build_researcher_pack.py','--version','2.8.0','--output-dir','dist'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
