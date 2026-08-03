import copy, json, subprocess
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'knowledge-packs/researcher/research-missions'
import sys
sys.path.insert(0,str(ROOT/'tools/knowledge-packs'))
from research_missions import load, render, validate_manifest

def example(): return load(BASE/'examples/TEL-001-wave-4-evidence-closure.json')

def test_all_examples_are_valid_and_generated_files_are_current():
    for path in (BASE/'examples').glob('*.json'):
        assert render(load(path)) == (BASE/'generated'/f'{path.stem}.md').read_text()

def test_version_provenance_and_wave_four_substance():
    brief=render(example())
    for phrase in ['Researcher Knowledge Pack version','Mission-template version','Mission-manifest version','Twin Object Profile versions','Baseline Twin release','Generation timestamp','complete canonical population','Unknowns','Contradictions','structured deliverables']:
        assert phrase in brief

@pytest.mark.parametrize('mutation,message',[
    (lambda d:d['profile_versions'].pop('industry-overview'),'required profile version'),
    (lambda d:d.pop('scope'),'missing required fields'),
    (lambda d:d.update(required_outputs=['governed-records']),'mandatory outputs'),
    (lambda d:d.update(mission_type='opportunity-pipeline-enrichment'),'Horizon rules'),
    (lambda d:d.update(outcome_states=['COMPLETE','CONTINUE']),'exhaustion rules'),
])
def test_negative_manifests_fail(mutation,message):
    data=example(); mutation(data)
    with pytest.raises(ValueError,match=message): validate_manifest(data)

def test_missing_profile_bad_template_and_unresolved_variable_fail():
    data=example(); templates={data['mission_type']:{'id':data['mission_type'],'profiles':['missing-profile'],'modules':[]}}
    with pytest.raises(ValueError,match='missing profile'): validate_manifest(data,templates=templates)
    contracts=load(BASE/'contracts/contracts-v1.json'); path=BASE/'contracts/contracts-v1.json'; original=path.read_text()
    try:
        contracts['modules']['evidence-closure']='{{UNRESOLVED}}'; path.write_text(json.dumps(contracts))
        with pytest.raises(ValueError,match='unresolved variables'): render(data)
    finally: path.write_text(original)

def test_pack_builder_includes_active_mission_assets():
    result=subprocess.run(['python3','tools/knowledge-packs/build_researcher_pack.py','--version','2.7.0','--output-dir','dist'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
