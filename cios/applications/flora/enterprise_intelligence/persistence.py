from __future__ import annotations
import json, uuid
from cios.applications.flora.storage import atomic_write_text, data_path
from cios.applications.flora.memory.models import now_iso

class InterpretationPersistenceService:
    def approve_selected(self, *, brief: dict, selected_claims: list[dict], approving_user: str) -> dict:
        record={'interpretation_id':'interp-'+uuid.uuid4().hex[:16],'originating_brief':brief.get('brief_id'),'reasoning_profile':brief.get('reasoning_profile'),'model_version':brief.get('model_metadata',{}).get('model'),'prompt_version':brief.get('model_metadata',{}).get('prompt_version','executive_commercial_brief_prompt_v1'),'evidence_package':brief.get('lineage_manifest',{}).get('evidence_package_id'),'claim_lineage':[c.get('lineage') or c.get('supporting_evidence') or [] for c in selected_claims],'approving_user':approving_user,'approval_timestamp':now_iso(),'interpretation_status':'approved_for_governed_persistence','canonical_fact':False,'claims':selected_claims}
        atomic_write_text(data_path('enterprise_intelligence','interpretations',record['interpretation_id']+'.json'), json.dumps(record, indent=2, sort_keys=True))
        return record
