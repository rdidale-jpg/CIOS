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
