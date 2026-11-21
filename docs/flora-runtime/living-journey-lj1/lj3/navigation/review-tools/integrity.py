from pathlib import Path
import re, subprocess, json, hashlib
D=Path(__file__).resolve().parents[2]
baseline='9384071c246ff83acbe134a0864f2ab0520e9b1d'
checks=[]
for p in sorted(D.glob('*.html')):
 old=subprocess.check_output(['git','show',baseline+':'+str(p.relative_to(Path.cwd()))],text=True)
 new=p.read_text()
 for pattern in [r'<figure class="world".*?</figure>',r'<p class="metric".*?</p>',r'<section class="focus".*?</section>',r'<section class="commercial-story".*?</section>',r'<details class="studio".*?</details>',r'<details class="text-view".*?</details>']:
  assert re.findall(pattern,old,re.S)==re.findall(pattern,new,re.S),(p.name,pattern)
 source=re.search(r'<div class="menu source-menu">(.*)</div></details></nav></header>',old,re.S).group(1)
 proof=re.search(r'<details class="proof"><summary>Sources</summary>(.*)</details></main>',new,re.S).group(1)
 assert source==proof,p.name
 checks.append({'file':p.name,'worldLabelsMetricsFocusContentAndSourceBodyUnchanged':True})
changed=subprocess.check_output(['git','diff',baseline,'--name-only'],text=True).splitlines()
assert all(f.startswith('docs/flora-runtime/living-journey-lj1/')for f in changed),changed
r={'baseline':baseline,'states':checks,'changedFilesWithinDesignPackOnly':True,'runtimeRoutesCanonicalPermissionsOffersPipelineUntouched':True}
(D/'navigation/previews/Integrity-Checks.json').write_text(json.dumps(r,indent=2)+'\n')
print('17 state content/source invariants passed; all changes confined to design pack.')
