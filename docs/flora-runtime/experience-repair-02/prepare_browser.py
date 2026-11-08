"""Build isolated browser fixtures using existing import/model/access owners only."""
from pathlib import Path
import os,json,shutil
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService
from cios.applications.flora.memory.repository import EnterpriseModelRepository
from cios.applications.flora.memory.models import EnterpriseUnknown
from cios.applications.flora.enterprise_canvas.access import repair_enterprise_canvas_access
from tests.test_flora_blueprint_import_validation import pkg
from tests import test_flora_factory_presentation_repair as r3
root=Path(os.environ['FLORA_DISCOVERY_BROWSER_EVIDENCE']).resolve()/'browser-fixtures';current=root/'current';history=root/'history';empty=root/'empty'
if current.exists() or history.exists():
 raise SystemExit('Use a fresh disposable evidence directory; refusing to overwrite existing fixtures')
current.mkdir(parents=True,exist_ok=True);empty.mkdir(exist_ok=True)
os.environ.update(FLORA_DATA_DIR=str(current),FLORA_PILOT_DIR=str(current),FLORA_ENVIRONMENT='development',FLORA_TRUST_PROXY_HEADERS='1')
from cios.applications.flora.blueprint_import import review_plan
review_plan.ASYNC_THRESHOLD=100000
path,source_hash=r3.ARTIFACTS['BNK-W1'];BlueprintPackageRegistry().receive(path.read_bytes(),path.name,'alice','workspace-a');r3.test_actual_retained_user_journey_and_honest_promotion('BNK-W1')
source=BlueprintPackageRegistry().list()[0]
for enterprise,workspace,user in [('synthetic-airline','workspace-a','alice'),('private-protected-fixture','workspace-b','bob')]:
 repo=EnterpriseModelRepository();model=repo.get(enterprise);model.unknowns['SYNTHETIC-UNKNOWN']=EnterpriseUnknown('SYNTHETIC-UNKNOWN',enterprise,'Synthetic missing buyer evidence; no real customer facts','commercial');repo.save(model);repair_enterprise_canvas_access(enterprise,workspace,user)
# An intentionally incomplete source identity, never name-matched to the model.
meta=r3.IDENTITY|{'primary_subject_name':'Ambiguous source fixture'}
p=BlueprintPackageRegistry().receive(pkg(manifest_extra=meta,records=[]),'misleading-model-name.zip','alice','workspace-a')
from cios.applications.flora.blueprint_import import BlueprintPackageValidator
BlueprintPackageValidator().validate_and_stage(p.package_ref,'alice',r3.HEADERS)
BlueprintPackageRegistry().update_inspection(p.package_ref,{'twin_id':None,'governed_scope':None})
shutil.copytree(current,history,dirs_exist_ok=True)
os.environ.update(FLORA_DATA_DIR=str(history),FLORA_PILOT_DIR=str(history))
ImportLifecycleService().mark_superseded(source.import_run_id,'alice','synthetic-successor-fixture')
(root/'fixture-metadata.json').write_text(json.dumps({'current_root':str(current),'historical_root':str(history),'empty_root':str(empty),'source_import_run_id':source.import_run_id,'source_sha256':source_hash,'history_transition':'Synthetic lifecycle-only transition over retained BNK content; no actual successor package accepted','models':'Synthetic model/access fixtures only; no real customer facts or production state'},indent=2))
print('Browser fixtures ready',source.import_run_id)
