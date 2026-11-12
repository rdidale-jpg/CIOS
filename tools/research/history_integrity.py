"""Exact reviewed research cuts; no automatic approval of future corpus changes."""
import json
from pathlib import Path
import subprocess

MAIN = 'adf205993cc0857183d77766ce4882bf48326fb4'
DEPTH = '6988ba50d29c1f238293fc7fe110d6182f055e68'
MACRO = '111600a56ca0edba0d47d1a8a0c92068060d83a8'
REVIEW = 'enterprise-knowledge/banking/research-model/Understanding-Review.json'
DEPTH_ADDITIONS = tuple('enterprise-knowledge/banking/research-model/source-snapshots/'+name+'.txt'
                        for name in ('DEPTH-LBG-AI','DEPTH-LBG-LEGACY','DEPTH-LBG-WALLET','DEPTH-LBG-CURVE'))
MACRO_ADDITIONS = tuple('enterprise-knowledge/macro/research-model/'+name for name in
    ('Global-Context-Contracts-v1.schema.json','Macro-Context-v1.json','Entity-Traces-v2.json')) + tuple(
    'enterprise-knowledge/macro/research-model/source-snapshots/'+name+'.txt' for name in
    ('GM-BILL','GM-CSRD-FR','GM-CSRD','GM-CYBER-FR','GM-CYBER-GB','GM-SOCIAL','GM-SRS',
     'MT-UK-REGISTER','MT-UK-BANK','MT-UK-SS121','MT-FR-CODE'))


def _git(root, *args):
    return subprocess.check_output(['git',*args],cwd=root)


def approved_history(root):
    """Pinned objects, exact additions and old-record prefix preservation."""
    paths=_git(root,'ls-tree','-r','--name-only',MAIN,'--','enterprise-knowledge').decode().splitlines()
    assert paths, 'Historical source inventory missing'
    expected={p:_git(root,'show',MAIN+':'+p) for p in paths}
    old=json.loads(expected[REVIEW]);review=_git(root,'show',DEPTH+':'+REVIEW);new=json.loads(review)
    assert set(old)==set(new)
    for key,value in old.items():
        assert (new[key][:len(value)]==value if isinstance(value,list) else new[key]==value),key
    expected[REVIEW]=review
    for ref, additions in ((DEPTH,DEPTH_ADDITIONS),(MACRO,MACRO_ADDITIONS)):
        for path in additions:
            assert path not in expected, 'Existing identity cannot become an addition'
            expected[path]=_git(root,'show',ref+':'+path)
    # Fixed, code-reviewed addition hashes; every previous source byte remains pinned.
    from cios.applications.flora.research_intelligence.foundation.snapshot import PINS
    import hashlib
    for path,checksum in PINS.items():
        assert path not in expected, 'Research identity reuse denied'
        content=(Path(root)/path).read_bytes()
        assert hashlib.sha256(content).hexdigest()==checksum, 'Unreviewed foundation source change: '+path
        expected[path]=content
    from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import PINS as S2_PINS
    for path,checksum in S2_PINS.items():
        assert path not in expected, 'Research identity reuse denied'
        content=(Path(root)/path).read_bytes()
        assert hashlib.sha256(content).hexdigest()==checksum, 'Unreviewed sprint2 source change: '+path
        expected[path]=content
    from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import COMPLETION_PINS
    for path,checksum in COMPLETION_PINS.items():
        assert path not in expected, "Completion identity reuse denied"
        content=(Path(root)/path).read_bytes()
        assert hashlib.sha256(content).hexdigest()==checksum, "Unreviewed completion source change: "+path
        expected[path]=content
    return expected


def compare_history(expected, actual):
    assert set(actual)==set(expected), {'missing':sorted(set(expected)-set(actual)),
                                      'unapproved':sorted(set(actual)-set(expected))}
    for path,content in expected.items():
        assert actual[path]==content, 'Historical or approved source changed: '+path


def verify_history(root):
    root=Path(root);expected=approved_history(root)
    # Inspect the filesystem too: ignored/untracked additions are not an escape.
    files=list((root/'enterprise-knowledge').rglob('*'))
    assert not any(p.is_symlink() for p in files), 'Research symlink is not a reviewed source'
    actual={str(p.relative_to(root)):p.read_bytes() for p in files if p.is_file()}
    compare_history(expected,actual)
    from cios.applications.flora.research_intelligence.foundation.snapshot import PINS
    from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import PINS as S2_PINS
    from cios.applications.flora.research_intelligence.foundation.sprint2.snapshot import COMPLETION_PINS
    return {'historical_files':len(expected)-len(DEPTH_ADDITIONS)-len(MACRO_ADDITIONS)-len(PINS)-len(S2_PINS)-len(COMPLETION_PINS),
            'depth_additions':len(DEPTH_ADDITIONS),'macro_additions':len(MACRO_ADDITIONS),
            'foundation_additions':len(PINS),'sprint2_additions':len(S2_PINS),'completion_additions':len(COMPLETION_PINS),'total':len(expected),'old_review_records_retained':True}
