"""Validate this documentation-only design delta without altering the real index."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE='97d316c640c96d99c2301819f8aac00b3b9c1398'
PREFIX='docs/product/flora-experience/'
ALLOWED=(PREFIX+'living-enterprise-v2/',PREFIX+'Presentation-Contract-v2.0.md',PREFIX+'FLORA-Experience-Contract-v1.0.md')

def git(*args,env=None,input=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,env=env,input=input)


def validate():
    git('merge-base','--is-ancestor',BASE,'HEAD')
    tracked=git('diff','--name-only',BASE).decode().splitlines()
    untracked=git('ls-files','--others','--exclude-standard').decode().splitlines()
    files=sorted(set(tracked+untracked))
    assert files and all(path.startswith(ALLOWED) for path in files),files
    assert not any(path.endswith(('.pyc','.sqlite','.db','.pdf')) for path in files)
    contract=PREFIX+'FLORA-Experience-Contract-v1.0.md'
    original=git('show',BASE+':'+contract).decode()
    amended=(ROOT/contract).read_text()
    assert original.split('**Status:**',1)[1]==amended.split('**Status:**',1)[1]
    assert original.splitlines()[0]==amended.splitlines()[0]
    images={}
    for path in git('ls-tree','-r','--name-only',BASE,'cios/applications/flora').decode().splitlines():
        if Path(path).suffix.lower() in {'.webp','.png','.svg','.jpg','.jpeg'}:
            raw=(ROOT/path).read_bytes()
            assert raw==git('show',BASE+':'+path),path
            images[path]=sha256(raw).hexdigest()
    assert len(images)==51,len(images)
    links=[]
    for path in [ROOT/name for name in files if name.endswith('.md')]:
        # Existing v1 body is historical evidence, not an invitation to repair
        # unrelated old references. Validate its one new amendment link only.
        text=path.read_text()
        if path.name=='FLORA-Experience-Contract-v1.0.md':text='\n'.join(text.splitlines()[:5])
        for target in re.findall(r'\]\(([^)]+)\)',text):
            url=urlsplit(target.strip('<>'))
            if url.scheme or not url.path:continue
            destination=(path.parent/unquote(url.path)).resolve()
            assert destination.is_relative_to(ROOT) and destination.exists(),(path,target)
            links.append({'from':str(path.relative_to(ROOT)),'target':target})
    # Build the candidate tree and reverse its complete binary patch inside a
    # disposable index. Neither the worktree nor the actual index is changed.
    with TemporaryDirectory(prefix='flora-design-index-') as directory:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(directory)/'index'))
        git('read-tree','HEAD',env=env)
        git('add','--',*files,env=env)
        candidate=git('write-tree',env=env).decode().strip()
        delta=git('diff','--binary',BASE,candidate)
        git('apply','--cached','--reverse','-',env=env,input=delta)
        restored=git('write-tree',env=env).decode().strip()
        assert restored==git('rev-parse',BASE+'^{tree}').decode().strip()
    report={'base':BASE,'checkout':git('rev-parse','HEAD').decode().strip(),
        'changed_files':files,'changed_file_count':len(files),'application_security_source_research_adr_workflow_changes':[],
        'unchanged_original_runtime_images':images,'local_links_checked':len(links),
        'historical_v1_body_unchanged':True,'reverse_patch_restores_exact_base_tree':restored,
        'preview_bytes':(HERE/'preview.html').stat().st_size,
        'no_merge_deploy_or_production_write':True}
    return report

if __name__=='__main__':
    report=validate()
    if '--check' not in sys.argv:
        (HERE/'Integrity-Proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('base','changed_file_count','local_links_checked','historical_v1_body_unchanged','reverse_patch_restores_exact_base_tree')}))
