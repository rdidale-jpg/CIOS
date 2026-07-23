from pathlib import Path
import hashlib
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'knowledge-packs/researcher/manifest.yaml'
VERSION = '2.3.0'
BASENAME = f'CIOS-Researcher-Knowledge-Pack-v{VERSION}'


def docs():
    out=[]; cur=None
    for line in MANIFEST.read_text().splitlines():
        if line.startswith('  - '):
            cur={}; out.append(cur); line='    '+line[4:]
        if cur is not None and line.startswith('    '):
            k,v=line.strip().split(': ',1); cur[k]=v
    return out


def build(version=VERSION):
    cmd=['python3','tools/knowledge-packs/build_researcher_pack.py','--version',version,'--output-dir','dist']
    return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)


def test_manifest_completeness_and_sources():
    ds=docs(); ids={d['document_id'] for d in ds}
    required={'RG-001','RKI-001','RKI-003','EI-001','EI-002','EI-003','EI-012','FP-009','FP-010','FP-012','ADR-016','MISSION-UKCG-001','TEMPLATE-Industry-Twin-Maturity-Assessment','TEMPLATE-Executive-Intelligence-Handover'}
    assert required <= ids
    for d in ds:
        src=ROOT/d['source_path']
        assert src.exists(), d
        assert hashlib.sha256(src.read_bytes()).hexdigest()==d['checksum']


def test_fp_identity_and_no_stale_paths():
    ds=docs()
    assert [d for d in ds if d['document_id']=='FP-010'][0]['source_path']=='architecture/founding-papers/FP-010-Knowledge-Pack-Architecture.md'
    assert [d for d in ds if d['document_id']=='FP-012'][0]['source_path']=='architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md'
    assert not any('obsolete' in d['source_path'].lower() or 'collision' in d['source_path'].lower() for d in ds)


def test_required_content_and_instruction_ownership():
    text=(ROOT/'knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md').read_text()
    for phrase in ['Research-ready','Architecture-ready','Human-supplied knowledge must record','No strong Recommendation may exist without inspectable lineage']:
        assert phrase in text
    rg=(ROOT/'knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md').read_text()
    for phrase in ['Minimum Research-ready gate','Supplier, contract and procurement checklist','Enduring Banking research-method lessons','Architecture handover requirements']:
        assert phrase in rg


def test_builder_accepts_valid_semantic_version_and_is_deterministic():
    first = build()
    assert first.returncode == 0, first.stderr
    zip_path=ROOT/f'dist/{BASENAME}.zip'
    h1=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    second = build()
    assert second.returncode == 0, second.stderr
    h2=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert h1==h2


def test_builder_rejects_malformed_versions():
    for version in ['2.3', 'v2.3.0', '2.3.0-beta']:
        result = build(version)
        assert result.returncode != 0
        assert 'Invalid Researcher Knowledge Pack version' in result.stderr


def test_generated_filenames_metadata_report_and_root_use_requested_version():
    result = build()
    assert result.returncode == 0, result.stderr
    zip_path=ROOT/f'dist/{BASENAME}.zip'
    report_path=ROOT/f'dist/{BASENAME}-build-report.md'
    assert zip_path.exists()
    assert report_path.exists()
    report = report_path.read_text()
    assert f'Requested pack version: {VERSION}' in report
    assert f'Version: {VERSION}' in report
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist())
        assert all(name.startswith(f'{BASENAME}/') for name in names)
        manifest = z.read(f'{BASENAME}/manifest.yaml').decode()
        pack_state = z.read(f'{BASENAME}/pack-state.yaml').decode()
        assert f'  version: {VERSION}' in manifest
        assert f'version: {VERSION}' in pack_state
        assert f'root_directory: {BASENAME}' in pack_state
        for needed in ['DOCUMENT-INDEX.md','checksums.sha256','configuration/Researcher-GPT-Instructions.md','missions/UK-Central-Government-Industry-Twin-Mission.md','architecture/EI-001-Enterprise-Model-Specification.md']:
            assert f'{BASENAME}/{needed}' in names
        assert not any('/enterprise-knowledge/banking/' in n for n in names)


def test_source_version_mismatch_fails_with_clear_message():
    result = build('9.9.9')
    assert result.returncode != 0
    assert 'Version mismatch: requested version 9.9.9; conflicting version 2.3.0' in result.stderr
    assert 'source file: knowledge-packs/researcher/VERSION; field: VERSION' in result.stderr


def test_no_generated_operational_output_contains_previous_hard_coded_release():
    result = build()
    assert result.returncode == 0, result.stderr
    zip_path=ROOT/f'dist/{BASENAME}.zip'
    allowed_history = {'CHANGELOG.md', 'MIGRATION.md'}
    forbidden = [b'CIOS-Researcher-Knowledge-Pack-v2.1.0']
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.rsplit('/', 1)[-1] in allowed_history:
                continue
            data = z.read(name)
            for needle in forbidden:
                assert needle not in data, name


def test_checksum_validation_succeeds_from_dist_directory():
    result = build()
    assert result.returncode == 0, result.stderr
    zip_path=ROOT/f'dist/{BASENAME}.zip'
    checksum_path=ROOT/f'dist/{BASENAME}.sha256'
    checksum_path.write_text(f'{hashlib.sha256(zip_path.read_bytes()).hexdigest()}  {zip_path.name}\n')
    check = subprocess.run(['sha256sum', '--check', checksum_path.name], cwd=ROOT/'dist', text=True, capture_output=True)
    assert check.returncode == 0, check.stderr


def test_workflow_tag_version_validation_patterns():
    accepted = {
        'researcher-knowledge-pack-v2.3.0': '2.3.0',
        'researcher-knowledge-pack-v10.4.12': '10.4.12',
    }
    pattern = re.compile(r'^researcher-knowledge-pack-v([0-9]+\.[0-9]+\.[0-9]+)$')
    for tag, version in accepted.items():
        assert pattern.fullmatch(tag).group(1) == version
    for tag in ['researcher-knowledge-pack-v2.3','researcher-knowledge-pack-2.3.0','researcher-knowledge-pack-v2.3.0-beta']:
        assert pattern.fullmatch(tag) is None


def test_progressive_twin_method_manifest_membership_and_authority_boundaries():
    ds = docs()
    ids = {d['document_id'] for d in ds}
    required = {
        'RKI-001', 'RG-001', 'MISSION-UKCG-001',
        'EI-001', 'EI-002', 'EI-003', 'EI-012',
        'IT-001', 'ITL-SPEC-001', 'MPT-001',
        'TEMPLATE-Enterprise-Intelligence-Pack',
        'TEMPLATE-Market-Participant-Twin',
        'TEMPLATE-Programme-Catalogue',
        'TEMPLATE-Coverage-Matrix',
    }
    assert required <= ids
    accepted_authorities = {
        'EI-001': 'enterprise-intelligence-specification',
        'EI-002': 'enterprise-intelligence-specification',
        'EI-003': 'enterprise-intelligence-specification',
        'EI-012': 'enterprise-intelligence-specification',
        'IT-001': 'industry-twin-specification',
        'ITL-SPEC-001': 'industry-twin-lifecycle-specification',
        'MPT-001': 'market-participant-specification',
    }
    by_id = {d['document_id']: d for d in ds}
    for document_id, authority in accepted_authorities.items():
        assert by_id[document_id]['authority'] == authority


def test_progressive_twin_method_required_operating_rules():
    texts = {
        path: (ROOT / path).read_text()
        for path in [
            'knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md',
            'knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md',
            'knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md',
        ]
    }
    combined = '\n'.join(texts.values()).lower()
    required_phrases = [
        'progressive twin development method',
        'load and assess existing governed and candidate twin state',
        'produce a delta plan',
        'operate, transform and reinvent',
        'rank enterprises, market participants and control bodies by structural significance',
        'tier 1 enterprise twin',
        '0 = not researched',
        'finance, operating model and transformation portfolio at least 3',
        'business or policy goal → pressure or failure mechanism → programme',
        'structurally significant market participant twin',
        'must not stop merely because a long report has been written',
        'a record target has been met',
        'every named entity has one observation',
        'the first source list is exhausted',
        'automatically choose the next highest-impact incomplete area',
        'genuine external blocker',
        'missing evidence, materiality, sources attempted, maturity consequence',
        'do not create a new twin type',
        'do not redefine enterprise intelligence doctrine',
    ]
    for phrase in required_phrases:
        assert phrase in combined


def test_ukcg_mission_baseline_reuse_completion_gates_and_outputs():
    mission = (ROOT / 'knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md').read_text().lower()
    for phrase in [
        'existing research baseline, not a completed industry twin',
        'reuse prior evidence, observations and candidate twin state',
        'initial government-wide industry and three-horizon frame',
        'determine tier 1 and tier 2 organisations from evidence',
        'build deep enterprise twins for all tier 1 organisations',
        'material supplier, market participant, regulatory, assurance, policy, funding and control-body',
        'connected government transformation programme portfolio',
        'derive industry relevance only after participant-neutral cross-twin synthesis',
        'completion gates pass only when',
        'one consolidated handover containing',
        'incremental change log from the prior baseline',
    ]:
        assert phrase in mission


def test_no_parallel_twin_type_or_silent_architecture_authority_change():
    changed_operating = '\n'.join(
        (ROOT / path).read_text().lower()
        for path in [
            'knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md',
            'knowledge-packs/researcher/operating-guidance/RG-001-Commercial-Digital-Twin-Research-Agent-Guide.md',
            'knowledge-packs/researcher/missions/UK-Central-Government-Industry-Twin-Mission.md',
        ]
    )
    assert 'new twin type' in changed_operating
    assert 'does not create a new twin type' in changed_operating or 'do not create a new twin type' in changed_operating
    prohibited_new_types = ['control-body twin type', 'control body twin type', 'control twin type']
    for phrase in prohibited_new_types:
        assert phrase not in changed_operating
    architecture_files = [
        'architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md',
        'architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md',
        'architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md',
        'architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md',
        'architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md',
        'architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md',
    ]
    for path in architecture_files:
        assert (ROOT / path).exists()
