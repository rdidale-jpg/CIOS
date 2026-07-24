from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def test_rg002_defines_mission_learning_and_lifecycle():
    text = (ROOT / 'knowledge-packs/researcher/operating-guidance/RG-002-Research-Mission-Workspace-Standard.md').read_text()
    assert '## 21. Research Mission Learning' in text
    for state in ['OBSERVED', 'CANDIDATE', 'VALIDATED', 'ADOPTED', 'REJECTED']:
        assert f'`{state}`' in text
    assert '`HYPOTHESIS` SHALL NOT be introduced as a separate lifecycle state' in text
    assert 'A pattern SHALL NOT become canonical because it was observed once' in text
    assert 'Mission Learning/' in text


def test_candidate_research_pattern_schema_states():
    schema = json.loads((ROOT / 'knowledge-packs/researcher/schemas/Candidate-Research-Pattern-Register.schema.json').read_text())
    status = schema['$defs']['pattern']['properties']['status']['enum']
    assert status == ['OBSERVED', 'CANDIDATE', 'VALIDATED', 'ADOPTED', 'REJECTED']
    required = set(schema['$defs']['pattern']['required'])
    for field in ['pattern_id','title','description','category','observed_during','evidence_references','evidence_summary','commercial_benefit','architectural_benefit','generalisability_assessment','assumptions','uncertainty','alternatives_considered','proposed_canonical_owner','implementation_impact','operational_impact','confidence','status','review_history']:
        assert field in required


def test_ukcg001_seed_patterns_not_promoted():
    register = json.loads((ROOT / 'knowledge-packs/researcher/missions/UKCG-001/Mission Learning/Pattern Register.json').read_text())
    patterns = {p['pattern_id']: p for p in register['patterns']}
    assert set(patterns) == {f'RP-{i:03d}' for i in range(1, 9)}
    assert all(p['status'] != 'ADOPTED' for p in patterns.values())
    assert patterns['RP-003']['status'] == 'VALIDATED'
    assert patterns['RP-008']['confidence'] == 'low'
    assert all('CP001-CP004' in p['evidence_summary'] and 'repository' in ' '.join(p['uncertainty']).lower() for p in patterns.values())
