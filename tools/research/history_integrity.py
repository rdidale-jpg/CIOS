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

# Current CEO commission: exact additive working research, not Source rights or
# canonical acceptance. Earlier bytes and the final comparator stay unchanged.


def verify_history(root):
    ceo_research_base = '201fe851a531ecb854d3ba8e3416bc667ab8c860'
    ceo_research_cut = {
        "enterprise-knowledge/banking/research-model/Assessment-Overlay.json": "5cf2812c14ffce3520ea0921ac93c15ce9ff66862f20bb69ee1f6d608080676a",
        "enterprise-knowledge/banking/research-model/Understanding-Review.json": "a0d28a7cf0a6bd2290a807fc04be90a8b3835f64ed70554e9d35d8ae7c780361",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-ANNUAL-OPERATIONS.txt": "8013767e11d63b99616977b2c2d6d8c7a04efe99f1fe6196c563ae07f4189272",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-BOARD.txt": "9747b0dc18b9dd058318bfb13214b4585ad83ed7273a20ecb8a88f44a1a388f8",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-DELIVERY.txt": "6880a29413a1a5582ee598ff8cdddff9a77e2b6e1da75bc24198cdde86db9592",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-LAUNCH.txt": "1c08a6b36070191305da14c7dae060960411a2ddd371eb7c5695d5d6b067eecf",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-SETTLEMENT.txt": "f9450bdb40760f52919e9b27f9a2cf27b56e00a6fdaf27fef06c080520e79bc7",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-VERTEX.txt": "f760c835e2435a8b4fa49e4a45e3c569b6023f303cc228e1063c2d54de83d132",
        "enterprise-knowledge/banking/research-model/source-snapshots/LCE-WORKFORCE.txt": "c6f79702360158232572e52cc6d98dfa482cf0993458f3cc8cf959c0d3551f69"
    }
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
    statement_path='enterprise-knowledge/banking/research-model/source-snapshots/EEI2B-Nationwide-AR26.json'
    if statement_path in actual:
        assert hashlib.sha256(actual[statement_path]).hexdigest()=='0ed1ae901d94af11be0303b81516ae712a6c09df8b3bc121b9e9eeec1c0ec63a', 'Unknown annual statement source cut'
        assert statement_path not in expected
        actual.pop(statement_path)
    flagship_path='enterprise-knowledge/banking/research-model/source-snapshots/LLF-HMT-PAYMENTS.txt'
    if flagship_path in actual:
        assert hashlib.sha256(actual[flagship_path]).hexdigest()=='0b6ba8d32c76e714002792fd84b7f6cbad18e2ac576919a7af0ad87885413a54', 'Unknown Lloyds public policy excerpt'
        assert flagship_path not in expected
        actual.pop(flagship_path)
    # CEO-1 retains one government-attributed professional-role fact as an exact
    # additive research cut. This is not canonical acceptance or a general grant.
    # All previous bytes, unknown-addition checks and comparator stay unchanged.
    for role_path, digest in {'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.json': '1640c40b31756b8d5fbda729c0e183a1b7c5618cca1cc88ef898fcf69ffe4d69', 'enterprise-knowledge/banking/research-model/source-snapshots/CEO1-GOV-ROLE.txt': '061058a0e65aab6e5b97e97feae9bb6d5d4bd10110e9f1584f2a11009d6f328d'}.items():
        assert role_path in actual and role_path not in expected
        assert hashlib.sha256(actual[role_path]).hexdigest()==digest, 'Unknown CEO role source cut'
        actual.pop(role_path)
    # Additive FCA numerical product cells; every historical byte and the exact comparator remain unchanged.
    for path, digest in {'enterprise-knowledge/banking/research-model/source-snapshots/FCA-Lloyds-Products-H126.json': 'e004a835e69655b73381340a0162b076ac53956bd3e97ea22c568fd5dc2ec214', 'enterprise-knowledge/banking/research-model/source-snapshots/FCA-Lloyds-Products-H126.txt': '1d02e44b8a2a79d6eee53b4cd94f7e14962e6c1a0fec3df59a4027ba2de33055'}.items():
        assert path in actual and path not in expected
        assert hashlib.sha256(actual[path]).hexdigest()==digest, "Unknown FCA product numerical source cut"
        actual.pop(path)
    # Gold v2 is one exact additive research cut, never a new permission or
    # canonical decision. Preserve every previous record and byte; reject all
    # unknown additions and mutations before the unchanged comparator runs.
    overlay='enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
    # Normalise only this exact newly commissioned cut back to #744 before
    # applying all the original Gold v2 and earlier historical comparisons.
    # New records do not acquire any prior manual review/Source permission.
    additions=set(ceo_research_cut)-{overlay,REVIEW}
    if additions & set(actual):
        assert additions<=set(actual), 'Incomplete CEO research cut'
        for path,digest in ceo_research_cut.items():
            assert hashlib.sha256(actual[path]).hexdigest()==digest, 'Unknown CEO research cut: '+path
        prior_data=_git(root,'show',ceo_research_base+':'+overlay)
        old,new=json.loads(prior_data),json.loads(actual[overlay])
        assert set(old)==set(new)
        for key,value in old.items():
            assert (new[key][:len(value)]==value if key in {'sources','claims','suppliers','relationships'} else new[key]==value),key
        prior_review=_git(root,'show',ceo_research_base+':'+REVIEW)
        old_review,new_review=json.loads(prior_review),json.loads(actual[REVIEW])
        assert set(old_review)==set(new_review)
        assert all(new_review[k]==value for k,value in old_review.items() if k!='baseline_digest')
        from cios.applications.flora.research_intelligence.cycle import digest
        assert new_review['baseline_digest']==digest(new)
        actual[overlay]=prior_data;actual[REVIEW]=prior_review
        for path in additions:actual.pop(path)
    review_assessment_cut=actual[overlay]
    if hashlib.sha256(actual[overlay]).hexdigest()!='a9376bad782a001258e72d747678a7587ea962e024666d46e10f2b098085d3a2':
        assert hashlib.sha256(actual[overlay]).hexdigest()=='6307d01f80e812327fef1339ef3a8c0f1b6835ca4878c735e4e972f5f3424422', 'Unknown Gold v2 assessment cut'
        original=_git(root,'show','1c8c8ae17bb2af3c95bf264d7df9befb60b0b576:'+overlay)
        assert hashlib.sha256(original).hexdigest()=='a9376bad782a001258e72d747678a7587ea962e024666d46e10f2b098085d3a2'
        assert expected[overlay]==original
        old,new=json.loads(original),json.loads(actual[overlay])
        for key,value in old.items():
            if key in {'sources','claims'}:
                byid={r['id']:r for r in new[key]}
                assert all(byid[r['id']]==r for r in value), 'Previous research record changed'
            elif key!='assessed_at':assert new[key]==value, key
        actual[overlay]=original
        for path,digest in {'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-AIPEOPLE.txt': 'b14118d6bc13cbbd49a0422c5cb268f60db1195ae7211c3628823d1a3a2fbba7', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-BRANDS.txt': '403a05806fb9600713bd159c5e6f88c8900196c630161f6410de01c6814eadbb', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-FRAUD.txt': 'baef9bd50829ad87521aad1e18297f63bedd91dffefc4e5776d5448fc75d6fd0', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-FRONTIER.txt': '1ba285b37b973134b36d76c6d739fdac5fe1f5903827a040f26e357b3a573e6f', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-LEADERS.txt': 'b3a094edac7bd4f6ae0cfbc7185c6d2e27f436e3543e73c6f2e1832f13f9209a', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-PROFILE.txt': '7e2e0521db96267d5ad3bdb49cc47f1382fbd054494224dff085745b9cb3ce59', 'enterprise-knowledge/banking/research-model/source-snapshots/LGV2-TRANSACTIONS.txt': 'ecd4dfb96f3ad48b70e501a46e53efca3d1abdcdf96eed0eef49604950d20779'}.items():
            assert path in actual and path not in expected
            assert hashlib.sha256(actual.pop(path)).hexdigest()==digest, 'Unknown Gold v2 source excerpt'
    # Existing candidate review is rebound to the additive assessment only.
    # All prior sources, assertion judgments and relationship reviews survive.
    if actual[REVIEW] != expected[REVIEW]:
        assert hashlib.sha256(actual[REVIEW]).hexdigest()=='cfdddaec221b9694c04b829ccab7738d620fd598757921e3a774de191cb2b531', 'Unknown Gold v2 candidate review'
        prior=json.loads(expected[REVIEW]); current=json.loads(actual[REVIEW])
        assert set(current)==set(prior)
        assert all(current[k]==v for k,v in prior.items() if k not in {'baseline_digest','as_of','sources'})
        assert len(current['sources'])==len(prior['sources'])
        for old_source,new_source in zip(prior['sources'],current['sources']):
            assert {k:v for k,v in old_source.items() if k!='assessment_digest'}=={k:v for k,v in new_source.items() if k!='assessment_digest'}
            if 'assessment_digest' in old_source:assert new_source['assessment_digest']==current['baseline_digest']
        from cios.applications.flora.research_intelligence.cycle import digest
        assert current['baseline_digest']==digest(json.loads(review_assessment_cut))
        actual[REVIEW]=expected[REVIEW]
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
