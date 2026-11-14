"""Owner-only read projections and copied-input challenges over actual evaluators.

No writes, grants, collectors, new score/qualification engine or global telemetry.
Private development remains actor-private; Pipeline uses its existing scope.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import date
from hashlib import sha256
import inspect
from . import offers,seller_development as dev,sales_pipeline as pipeline
from .research_intelligence import buying_evidence as research
from .access import is_cios_owner,require_capability
from .security import verified_service_read
from .security_store import canonical,digest

BASE='/flora/command-centre/opportunity-assurance'
PATHS=frozenset({'/flora/command-centre',BASE})
CHALLENGES=('Original','Withdraw source','Close programme','Contradict programme','Remove Offer approval','Remove customer attestation','Unbind identity','Expire sources','60-day review policy')


def authority(headers):
    actor=require_capability(headers,'commercial_context.view')
    if not is_cios_owner(headers):raise PermissionError('Verified workspace owner permission required')
    return actor


def _revision(function):return sha256(inspect.getsource(function).encode()).hexdigest()


def _seller(actor,employer,headers):
    m=offers.resolve_commercial_mission(headers)
    return {'user_id':actor.user_id,'workspace_id':actor.workspace,'employer_id':employer['id'],
        'employer_version':employer['version'],'participant_twin_id':employer['participant_twin_id'],
        'mission_id':m.context_id if m else None,'mission_version':m.version if m else None,
        'excluded_accounts':list(m.excluded_accounts) if m else []}


def _business(result):
    b=result['buying_trigger']
    return {k:result[k] for k in ('assessment_id','entry_play','next_validation_action','why_account','contradictions')}|{'tier':b['tier'],'stage':b['stage'],'rank':b['rank_key']}


def _criterion_view(record,decision=None):
    base=pipeline.qualification(record)
    typed={c['id']:c for c in decision.get('criterion_trace',[])} if decision else {}
    rows=[]
    for key,(label,_) in pipeline.CRITERIA.items():
        value=record.get('qualification',{}).get(key,{})
        completed=key in base['complete'];supplied=bool(value.get('note') or value.get('source'))
        trace=typed.get(key)
        rows.append({'id':key,'label':label,'input_state':'Pass' if completed else 'Fail' if supplied else 'Unknown',
            'development_state':('Pass' if trace['passed'] else 'Fail' if supplied else 'Unknown') if trace else 'Unknown',
            'note':value.get('note',''),'reference':value.get('source',''),'evidence_kind':value.get('kind','Unknown — Pipeline stores notes/references only'),
            'date':value.get('date','Unknown'),'actual_development_check':trace})
    return {'complete':len(base['complete']),'total':len(pipeline.CRITERIA),'percent':base['percent'],
        'label':'Qualification input completeness','independently_verified_buyer_need':'Not established',
        'opportunity_accuracy':'Unknown — no empirical labelled outcome cohort','criteria':rows}


@verified_service_read('commercial_context.view')
def overview(cutoff='',*,headers=None):
    actor=authority(headers);cutoff=cutoff or date.today().isoformat()
    if date.fromisoformat(cutoff)>date.today():raise ValueError('Cutoff cannot be future')
    state=offers.snapshot(headers=headers)
    rows=[];developments=[];shortlists=[]
    if state['selected']:
        rows=offers.discover('offer','',cutoff,intelligence=True,headers=headers)
        developments=dev.records(headers=headers) # NEVER enumerate other users.
        shortlists=offers.shortlist_snapshot(headers=headers)
    pipes=pipeline.list_opportunities(headers=headers) # Existing workspace + entity service.
    return {'cutoff':cutoff,'scope':'Current verified workspace/entity scope; private development and shortlists are yours only',
        'counts':{'assessments':len(rows),'Research only':sum(r['buying_trigger']['tier']=='Research only' for r in rows),
        'Investigate':sum(r['buying_trigger']['tier']=='Investigate' for r in rows),'Prioritise':sum(r['buying_trigger']['tier']=='Prioritise' for r in rows),
        'private_shortlists':len(shortlists),'private_development':len(developments),'stale_development':sum(r['stale'] for r in developments),
        'pipeline':len(pipes),'qualified_pipeline':sum(r['stage']=='Qualified' for r in pipes)},
        'assessments':rows,'development':developments,
        'pipeline':[{'id':r['id'],'enterprise':r['enterprise'],'enterprise_slug':r['enterprise_slug'],'stage':r['stage'],'version':r['version']} for r in pipes],
        'policy':{'matching':offers.TRIGGER_POLICY,'matching_revision':_revision(offers.assess_fit),
        'development_revision':_revision(dev.qualification_checks),'handoff_revision':_revision(dev.handoff_checks),'pipeline_revision':_revision(pipeline.qualification),
        'source_revision':research.DATA_SHA256},'accuracy':'Unknown; input completeness is not independent buyer verification or opportunity accuracy'}


def _qualification(record,result,approved,stale):
    if not record:return {'ready':False,'reasons':['No authorised private development record selected'],'criterion_trace':[],'gate_trace':[]}
    return dev.qualification_checks(record,result,approved,stale)


@verified_service_read('commercial_context.view')
def inspect_pair(offer_id,enterprise_slug,cutoff='',candidate='',challenge='Original',source='',fact='',*,headers=None):
    actor=authority(headers);cutoff=cutoff or date.today().isoformat()
    if challenge not in CHALLENGES:raise ValueError('Choose a bounded owner challenge')
    if date.fromisoformat(cutoff)>date.today():raise ValueError('Cutoff cannot be future')
    env=offers._load();employer=offers._selected(env,actor);offer=offers._record(env,actor,employer,offer_id)
    # The bound discovery service is the admission/visibility gate; private IDs
    # cannot be used as a way to inspect an unseen account or Offer.
    original=next((r for r in offers.discover('offer',offer_id,cutoff,intelligence=True,headers=headers) if r['enterprise_slug']==enterprise_slug),None)
    if original is None:raise PermissionError('Authorised assessment unavailable')
    record=dev.records(candidate,headers=headers) if candidate else None
    if record and (record['offer_id']!=offer_id or record['enterprise_slug']!=enterprise_slug):raise PermissionError('Development pair does not match')
    targets=research.accounts(offers.accounts());target=targets[enterprise_slug];seller=_seller(actor,employer,headers)
    replay=offers.assess_fit(seller,offer,target,cutoff,offers.TRIGGER_POLICY)
    if replay!=original:raise ValueError('Unresolved reproduction mismatch; do not claim a reproduced path')
    current_approved=offer['state']=='employer_approved' and offers._eligible(env,offer)
    original_q=_qualification(record,original,current_approved,record['stale'] if record else False)
    modified=deepcopy(target);changed_offer=deepcopy(offer);changed_record=deepcopy(record)
    facts=modified['trigger_research']['facts'];available=original['buying_trigger']['timeline']
    if source and source not in {f['source_id'] for f in available}:raise ValueError('Source must belong to this authorised pair/cutoff')
    if fact and fact not in {f['id'] for f in available}:raise ValueError('Fact must belong to this authorised pair/cutoff')
    note='Actual inputs, no challenge applied';synthetic_ids=[]
    if challenge=='Withdraw source':
        if not source:raise ValueError('Select a retained source')
        for f in facts:
            if f['source_id']==source:f['status']='withdrawn'
        note='Hypothetical source withdrawal; actual register unchanged'
    elif challenge in {'Close programme','Contradict programme'}:
        selected=next((f for f in facts if f['id']==fact),None)
        if not selected or not selected.get('programme_id'):raise ValueError('Select a fact with an explicit programme reference')
        counter=deepcopy(selected);counter.update(id='OWNER-CHALLENGE-'+selected['id'],kind='closed' if challenge=='Close programme' else 'counter',
            counter_scope='programme',status='retained',supersedes=[],statement='Hypothetical owner challenge: programme no longer supports this candidate; not observed research.',owner_challenge=True)
        facts.append(counter);synthetic_ids.append(counter['id']);note='Hypothetical programme invalidation, not a newly observed contradictory source'
    elif challenge=='Remove Offer approval':changed_offer['state']='private_draft';note='Hypothetical loss of separate employer approval'
    elif challenge=='Remove customer attestation':
        if not changed_record:raise ValueError('Select your authorised development record')
        changed_record['customer_attested']=False;note='Hypothetical lost customer attestation; notes remain intact'
    elif challenge=='Unbind identity':
        modified['trigger_research']['identity'].update(identity_owner='existing_technology_foundation',identity_allows_priority=False)
        note='Hypothetical unbound identity; actual enterprise identity is unchanged'
    elif challenge=='Expire sources':
        for f in facts:f['last_verified']='2000-01-01T00:00:00+00:00'
        note='Hypothetical stale verification dates under the pinned cutoff'
    elif challenge=='60-day review policy':modified['trigger_research']['policy']['catalyst_review_days']=60;note='Unapproved alternate policy: 60 versus original 90 review days, same pinned facts/cutoff'
    if challenge=='Original' and (source or fact):raise ValueError('Original replay does not accept challenge selectors')
    changed=offers.assess_fit(seller,changed_offer,modified,cutoff,offers.TRIGGER_POLICY)
    # Compare the actual same dependency calculator. Source/Offer/entry-play
    # drift demands reassessment; there is never an automatic Pipeline edit.
    impacted=False;dependency_changes=[]
    if record and challenge!='Original':
        before=dev.dependencies(original,offer,employer,offers.resolve_commercial_mission(headers))
        after=dev.dependencies(changed,changed_offer,employer,offers.resolve_commercial_mission(headers))
        dependency_changes=[k for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)]
        impacted=bool(dependency_changes)
    changed_q=_qualification(changed_record,changed,False if challenge=='Remove Offer approval' else current_approved,(record['stale'] or impacted) if record else False)
    # Historical successful handoff is not re-authorised by this inspection.
    link=record.get('pipeline_id') if record else None
    linked=pipeline.get_opportunity(link,headers=headers) if link else None
    return {'original':original,'challenged':changed,'reproduced':True,'challenge':challenge,'challenge_note':note,
        'hypothetical_fact_ids':synthetic_ids,'policy':{'id':offers.TRIGGER_POLICY,'matching_revision':_revision(offers.assess_fit),
        'development_revision':_revision(dev.qualification_checks),'handoff_revision':_revision(dev.handoff_checks),'pipeline_revision':_revision(pipeline.qualification),
        'source_revision':research.DATA_SHA256,'cutoff':cutoff,'input_snapshot_digest':digest(canonical([seller,offer,target])),
        'original_review_days':target['trigger_research']['policy']['catalyst_review_days'],'challenged_review_days':modified['trigger_research']['policy']['catalyst_review_days']},
        'offer':{'id':offer['id'],'version':offer['version'],'state':offer['state'],'name':offer['content']['name'],'evidence':offer['content']['evidence'],'constraints':offer['content']['constraints'],'outcome':offer['content']['outcome'],'target_sectors':offer['content']['icp'],
            'buyers_hypothesis':offer['content']['buyers'],'capabilities':offer['content']['capabilities'],'partners':offer['content']['partners'],
            'exclusions':offer['content']['exclusions'],'trigger_pattern':offer['content']['trigger_pattern'],'matched_dimension':original['buying_trigger']['dimension'],
            'template':offer.get('template_source'),'interpretation':'Employer-approved seller proposition; delivery proof and residual customer need still require review'},
        'development':record,'qualification':_criterion_view(record or {},original_q),
        'original_readiness':original_q,'challenged_readiness':changed_q,
        'original_handoff_checks':dev.handoff_checks(record,original_q) if record else None,
        'challenged_handoff_checks':dev.handoff_checks(changed_record,changed_q) if changed_record else None,
        'changed_dependencies':dependency_changes,'would_require_reassessment':impacted,
        'pipeline':{'id':linked['id'],'stage':linked['stage'],'version':linked['version'],'evidence_maturity':pipeline.evidence_maturity(linked)} if linked else None,
        'handoff':'Recorded explicit hand-off; current readiness does not independently verify customer need' if linked else 'No recorded hand-off; no write performed',
        'accuracy':'Unknown — no independent outcome verification or measured accuracy cohort',
        'outcome':'More evidence needed' if not original_q['ready'] else 'Input checks complete; independent verification unknown'}


@verified_service_read('commercial_context.view')
def inspect_pipeline(identifier,*,headers=None):
    authority(headers);record=pipeline.get_opportunity(identifier,headers=headers)
    return {'record':record,'qualification':_criterion_view(record),'evidence_maturity':pipeline.evidence_maturity(record),
        'limitation':'Existing authorised workspace Pipeline record. Private development linkage/notes are not inferred from activity text; no independent buyer-need verification.'}
