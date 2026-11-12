"""Attach bounded decisions to the existing scoped operational dependency ledger."""
import json
from ...cycle import digest
from .assurance import POLICY,Proposal


def record_decision(operations,job_id,proposal,decision,parent_id):
    proposal=Proposal.model_validate(proposal)
    if digest(proposal.model_dump(mode="json"))!=decision.get("claim_digest"):raise ValueError("Receipt/proposal digest mismatch")
    if decision.get('policy')!=POLICY or decision.get('canonical_promotion') is not False or decision.get('pipeline_qualification') is not False:
        raise ValueError('Non-promoting versioned assurance receipt required')
    with operations.db() as db:
        job,programme=operations._job(db,job_id)
        if job['cancel']:raise ValueError('Cancelled research job')
        parent=db.execute("SELECT * FROM objects WHERE job=? AND id=? AND kind='candidate' AND state='active'",(job_id,parent_id)).fetchone()
        if not parent:raise ValueError('Active scoped candidate required')
        if json.loads(parent['payload'])['candidate']['statement']!=proposal.statement:raise ValueError('Receipt must assess the complete actual parent statement')
        allowed={s.source_id for s in programme.sources}
        if any(p['source_id'] not in allowed for p in decision['passage_refs']):raise PermissionError('Assurance evidence outside issued programme; no source-policy fallback')
        if decision['claim_id']!=parent_id:raise ValueError('Receipt must assess its actual candidate identity')
        identifier='SEM-'+digest(decision)[:24]
        operations._put(db,job_id,identifier,'semantic_decision',decision,state='active' if decision['outcome']=='accept_bounded' else 'withheld',parents=(parent_id,))
        operations.event(db,job_id,'semantic_receipt',{'receipt_id':identifier,'outcome':decision['outcome'],'policy':POLICY})
        return identifier
