"""Exact reviewed research cuts; no automatic approval of future corpus changes."""
import hashlib
import json
from pathlib import Path
import subprocess

MAIN = 'adf205993cc0857183d77766ce4882bf48326fb4'
DEPTH = '6988ba50d29c1f238293fc7fe110d6182f055e68'
MACRO = '111600a56ca0edba0d47d1a8a0c92068060d83a8'
# #591 owner-authorised candidate-only addition; every earlier byte remains pinned.
TRIGGER_SHA256 = '2aa6062fba5ec016e77dbcca81989a318793c3b1746df08031da32e36a7e8927'
TRIGGER_ADDITIONS = ('enterprise-knowledge/technology/research-model/Buying-Trigger-Pilot.json',)
# #625 permits a bounded public presentation candidate, NOT canonical Evidence
# acceptance. Pin exactly its proposal and numerical excerpt. Never admit an
# unknown path, refresh historical bytes or approve a future source revision.
INT1_CANDIDATE_ADDITIONS = {
    'enterprise-knowledge/banking/research-model/source-snapshots/INT1-FCA-Candidate.json':
        '511b5f5225fa6fc005ebdc5484aad75539c1f9e64df8201591a5c628aedec63b',
    'enterprise-knowledge/banking/research-model/source-snapshots/PR-FCA-COMPLAINTS-H126.txt':
        'b1ca214f97c51e0375d054a879d2e01f71c34697bdf26f040953c7a91d98905b',
}
# #628 bounded presentation-only public candidates. Rights are separately
# reviewed; these exact inventory bytes do not approve canonical Evidence.
EAI1_CANDIDATE_ADDITIONS = {
    'enterprise-knowledge/banking/research-model/source-snapshots/EAI1-FCA-Service-Candidate.json':
        '953d7e15fae078295ca21bf6fd4d874ad142f3b813656ba474be789ee670ef9b',
    'enterprise-knowledge/banking/research-model/source-snapshots/EAI1-FCA-Service.txt':
        '015a657f4f7cc232037879c652a8cbb3da91865ede073dfb6186de54f278773d',
    'enterprise-knowledge/banking/research-model/source-snapshots/EAI1-HMT-CTP-Candidate.json':
        '05202f75fe8bf4594d0843a9e224ab18b02d422030ec89b166d678d1f11f175f',
    'enterprise-knowledge/banking/research-model/source-snapshots/EAI1-HMT-CTP.txt':
        '42cef2b7ca812c83551a89bd6500b3884b21e87972f6b0c670951c8acb9bf63f',
    'enterprise-knowledge/macro/research-model/source-snapshots/EAI1-UK-Cyber-Candidate.json':
        '74ec38444ef79f6a5273306e8e93c86a06562647a7865d30145ef035136f9267',
    'enterprise-knowledge/macro/research-model/source-snapshots/EAI1-UK-Cyber.txt':
        'b9abe8eb681cb0310dbf7eec719fc66de5bda0fca2920b0cc02a94a7efc92646',
}
# #635 bounded FCA numerical presentation candidate; every earlier byte stays pinned.
BIE2_CANDIDATE_ADDITIONS = {'enterprise-knowledge/banking/research-model/source-snapshots/BIE2-FCA-Peers-Candidate.json': 'd2536d42b5fcdc8ef3ebf59bd42564dd93d1648ee73b6f05b6ce14497394666d', 'enterprise-knowledge/banking/research-model/source-snapshots/BIE2-FCA-Peers.txt': 'dd68d2c507bea63b5d33f9932dee0c8fa0fbe9053f1aa3289f81822e9dda0338'}
# #637 bounded numerical outcomes release; no earlier byte or permission changes.
BIE3_CANDIDATE_ADDITIONS = {'enterprise-knowledge/banking/research-model/source-snapshots/BIE3-FCA-Outcomes-Candidate.json': 'e8c6b098b0695245b7a47b834ca180fa9d69e430a039affbbb98b46342d4b471', 'enterprise-knowledge/banking/research-model/source-snapshots/BIE3-FCA-Outcomes.txt': '9fa20943561b0f87d3605d12f36fb26ec9e31ff9ba5f3d683a00c8da2f8099da'}
# #642 explicitly commissioned real-source candidate working data. These exact
# two additions are not canonical acceptance or a publisher/source-use grant.
# All 173 earlier files and the comparator remain byte-for-byte pinned.
F1_CANDIDATE_ADDITIONS = {
    'enterprise-knowledge/banking/research-model/source-snapshots/F1-BOE-LPMZ598-Candidate.json':
        'f783bdb4b671c8539e02f69a0fab765a12ecf74ad3bc2ec6c191fb900bfa79d2',
    'enterprise-knowledge/banking/research-model/source-snapshots/F1-BOE-LPMZ598.txt':
        '8584db998bed1cf6050a8158d17e4c72c097db338d628a2bf67a33d089cd75fa',
}
REVIEW = 'enterprise-knowledge/banking/research-model/Understanding-Review.json'
DEPTH_ADDITIONS = tuple('enterprise-knowledge/banking/research-model/source-snapshots/'+name+'.txt'
                        for name in ('DEPTH-LBG-AI','DEPTH-LBG-LEGACY','DEPTH-LBG-WALLET','DEPTH-LBG-CURVE'))
MACRO_ADDITIONS = tuple('enterprise-knowledge/macro/research-model/'+name for name in
    ('Global-Context-Contracts-v1.schema.json','Macro-Context-v1.json','Entity-Traces-v2.json')) + tuple(
    'enterprise-knowledge/macro/research-model/source-snapshots/'+name+'.txt' for name in
    ('GM-BILL','GM-CSRD-FR','GM-CSRD','GM-CYBER-FR','GM-CYBER-GB','GM-SOCIAL','GM-SRS',
     'MT-UK-REGISTER','MT-UK-BANK','MT-UK-SS121','MT-FR-CODE'))

# #648 new routine working research only; every earlier source byte is unchanged.
RUD1_ADDITIONS = {'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-Public-Facts.json': '84777ecb69f2718a28a379c87af81cd7da78114bbb92356d3030f4d350e2ab6b', 'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-FCA-Facts.txt': 'efc71dc5c0f8e3311f5f573b55dcb59570c0a78795d72f75d12fa81e2fb7ef52', 'enterprise-knowledge/banking/research-model/source-snapshots/RUD1-Nationwide-Facts.txt': '690243d6ef1c9acbffe355ec225c05a3da2eafc3b39837319534f5d552602eac'}


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
    candidate=Path(root)/TRIGGER_ADDITIONS[0]
    assert not candidate.is_symlink(), 'Candidate source symlink is not approved'
    content=candidate.read_bytes()
    assert hashlib.sha256(content).hexdigest()==TRIGGER_SHA256, 'Approved candidate source changed'
    assert TRIGGER_ADDITIONS[0] not in expected, 'Existing identity cannot become an addition'
    expected[TRIGGER_ADDITIONS[0]]=content
    for path,digest in INT1_CANDIDATE_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'Candidate source symlink is not admitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'INT-1 candidate proposal/excerpt changed'
        assert path not in expected, 'Existing identity cannot become an addition'
        expected[path]=content
    for path,digest in EAI1_CANDIDATE_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'Candidate source symlink is not admitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'EAI-1 candidate proposal/excerpt changed'
        assert path not in expected, 'Existing identity cannot become an addition'
        expected[path]=content
    for path,digest in BIE2_CANDIDATE_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'BIE-2 candidate source symlink is not admitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'BIE-2 candidate proposal/excerpt changed'
        assert path not in expected, 'Existing identity cannot become an addition'
        expected[path]=content
    for path,digest in BIE3_CANDIDATE_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'BIE-3 candidate source symlink is not admitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'BIE-3 candidate proposal/excerpt changed'
        assert path not in expected, 'Existing identity cannot become an addition'
        expected[path]=content
    for path,digest in RUD1_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'RUD-1 source symlink is not permitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'RUD-1 research revision changed'
        assert path not in expected, 'Existing identity cannot become an addition'
        expected[path]=content
    for path,digest in F1_CANDIDATE_ADDITIONS.items():
        candidate=Path(root)/path
        assert not candidate.is_symlink(), 'F1 candidate source symlink is not admitted'
        content=candidate.read_bytes()
        assert hashlib.sha256(content).hexdigest()==digest, 'F1 candidate proposal/excerpt changed'
        assert path not in expected, 'Existing identity cannot become an addition'
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
    # One explicitly commissioned, inactive factual case is an additive cut,
    # not a revision of the 178-file historical corpus or a source-use grant.
    # Unknown additions still reach the exact comparator and fail unchanged.
    public_path='enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
    if public_path in actual:
        record=json.loads((root/'docs/flora-runtime/public-financial-intelligence/Source-Addition.json').read_text())
        assert record['path']==public_path and record['public_activation'] is False
        assert hashlib.sha256(actual[public_path]).hexdigest()==record['sha256'], 'Unknown public factual candidate cut'
        assert public_path not in expected
        actual.pop(public_path)
    compare_history(expected,actual)
    return {'historical_files':len(expected)-len(DEPTH_ADDITIONS)-len(MACRO_ADDITIONS)-len(TRIGGER_ADDITIONS)-len(INT1_CANDIDATE_ADDITIONS)-len(EAI1_CANDIDATE_ADDITIONS)-len(BIE2_CANDIDATE_ADDITIONS)-len(BIE3_CANDIDATE_ADDITIONS)-len(F1_CANDIDATE_ADDITIONS)-len(RUD1_ADDITIONS),
            'depth_additions':len(DEPTH_ADDITIONS),'macro_additions':len(MACRO_ADDITIONS),
            'trigger_candidate_additions':len(TRIGGER_ADDITIONS),'int1_presentation_candidate_additions':len(INT1_CANDIDATE_ADDITIONS),
            'eai1_presentation_candidate_additions':len(EAI1_CANDIDATE_ADDITIONS),
            'bie2_presentation_candidate_additions':len(BIE2_CANDIDATE_ADDITIONS),
            'bie3_presentation_candidate_additions':len(BIE3_CANDIDATE_ADDITIONS),
            'f1_analytical_candidate_additions':len(F1_CANDIDATE_ADDITIONS),
            'rud1_working_research_additions':len(RUD1_ADDITIONS),
            # Preserve this API's historical-cut report. The additional exact
            # candidate is checked above, not relabelled historical research.
            'total':len(expected),'old_review_records_retained':True}
