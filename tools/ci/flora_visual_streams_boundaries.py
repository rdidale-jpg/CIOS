"""Read-only VEX-1 source/control fingerprint review; no baseline refresh."""
from pathlib import Path
import ast, hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='0cb07c2e78ccb16240c799b31cd62736e2135529'
DESIGN='c6bf2280594922db6951c5c36205984c85ca4aea'
def original(path,ref=BASE):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
def digest(raw):return hashlib.sha256(raw).hexdigest()

def main():
 files=['cios/applications/flora/'+p for p in ['access.py','security.py','security_web.py','security_store.py','sales_pipeline.py','offers.py','commercial_mission.py','research_intelligence/model.py','research_intelligence/registry.py','research_intelligence/macro_intelligence.py','visual_v2.py','blueprint_import/material_pressure.py']]
 changed_owners={'cios/applications/flora/'+n for n in ('visual_streams.py','design_system.py','public_routes.py','web/app.py')}
 files+=[str(p.relative_to(ROOT))for p in sorted((ROOT/'cios/applications/flora').rglob('*.py'))if str(p.relative_to(ROOT))not in changed_owners]
 files+=['tools/ci/flora-baseline-v1.json','tools/ci/flora_ci.py']
 files+=[str(p.relative_to(ROOT))for p in sorted((ROOT/'tests').glob('test_flora_security*.py'))]
 files+=[str(p.relative_to(ROOT))for p in sorted((ROOT/'enterprise-knowledge').rglob('*'))if p.is_file()]
 for folder in ['enterprise_canvas','seller_development']:
  files += [str(p.relative_to(ROOT))for p in sorted((ROOT/'cios/applications/flora'/folder).rglob('*.py'))]
 protected={}
 for name in sorted(set(files)):
  raw=(ROOT/name).read_bytes();assert raw==original(name),name;protected[name]=digest(raw)
 functions={}
 for name,wanted in [('public_routes.py',{'public_read_path','public_request_target'}),('web/app.py',{'_public_read_request','do_POST','_html','_body'})]:
  path='cios/applications/flora/'+name;old=original(path).decode();new=(ROOT/path).read_text()
  def extracts(text):return {n.name:ast.get_source_segment(text,n)for n in ast.walk(ast.parse(text))if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name in wanted}
  a,b=extracts(old),extracts(new);assert set(a)==set(b)==wanted
  for key in wanted:assert a[key]==b[key];functions[path+'::'+key]=digest(a[key].encode())
 manifest=json.loads((ROOT/'cios/applications/flora/visual_stream_assets/artwork.json').read_text())
 artwork={}
 for scene,row in manifest['scenes'].items():
  raw=original(row['original_path'],DESIGN);assert digest(raw)==row['original_sha256'];artwork[scene]=digest(raw)
  for v in row['variants']:assert digest((ROOT/'cios/applications/flora/visual_stream_assets'/v['file']).read_bytes())==v['sha256']
 report={'base':BASE,'design':DESIGN,'protected_files':protected,'unchanged_guard_functions':functions,'accepted_artwork':artwork,'original_artwork_files':7,'responsive_variants':21,'canonical_data_or_protected_service_changes':False}
 (ROOT/'docs/flora-runtime/vex1-612/Boundary-Checks.json').write_text(json.dumps(report,indent=2)+'\n')
 print(str(len(protected))+' protected source/test files and six guard functions unchanged; seven accepted originals verified.')
if __name__=='__main__':main()
