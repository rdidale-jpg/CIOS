"""Private seller work, never canonical Opportunity/Twin truth.

Uses the Offers protected envelope for versioned working notes; sales_pipeline
remains the single owner of Pipeline records and qualification transitions.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import date
import json
from . import offers, sales_pipeline as pipeline
from .access import require_capability
from .security import verified_service_read, verified_service_write
from .security_store import canonical, digest

STEPS=('Investigate','Validate','Create Preference','Qualify')
CUSTOMER=frozenset({'Customer statement','Customer document'})
KINDS=('Seller hypothesis','Public evidence','Seller review','Customer statement','Customer document')
TEXT_FIELDS=('challenge','insight','first_conversation','diagnostic','proof','alternatives','next_action','engagement','economics')
ROLES=('Business sponsor','Economic buyer','Technical / delivery owner','Procurement','Security / legal')


def _actor(headers,edit=False):return offers._actor(headers,edit)


def _private(envelope,actor):return envelope['users'].setdefault(offers._key(actor),{}).setdefault('development',{})


def _scope(record,actor,employer,headers,edit=False):
    if record['author']!=actor.user_id or record['workspace_id']!=actor.workspace or record['employer_id']!=employer['id']:
        raise PermissionError('Private development record unavailable')
    if not record['enterprise_id'].startswith('presentation:'):
        require_capability(headers,'commercial_context.edit' if edit else 'commercial_context.view',record['enterprise_id'],actor.workspace)


def _versions(envelope,actor,employer,identifier,headers,edit=False):
    versions=envelope['users'].get(offers._key(actor),{}).get('development',{}).get(identifier)
    if not versions:raise PermissionError('Private development record unavailable')
    _scope(versions[-1],actor,employer,headers,edit)
    return versions


def dependencies(assessment,offer,employer,mission):
    b=assessment['buying_trigger']
    return {'offer':digest(canonical(offer)),'employer':str(employer['version']),
        'mission':digest(canonical(asdict(mission) if mission else None)),'research':b['research_digest'],
        'entry_play':b['entry_play_revision'],'tier':b['tier'],'stage':b['stage'],
        **{'fact:'+f['id']:digest(canonical([f['reference_digest'],f['status'],f['dated_current'],f['supersedes']])) for f in b['timeline']}}


def _current(record,headers,envelope,actor,employer):
    try:
        offer=offers._record(envelope,actor,employer,record['offer_id'])
        result=next((r for r in offers.discover('offer',record['offer_id'],date.today().isoformat(),intelligence=True,headers=headers) if r['enterprise_id']==record['enterprise_id']),None)
        if result is None:raise ValueError('Assessment unavailable')
        return result,dependencies(result,offer,employer,offers.resolve_commercial_mission(headers))
    except (ValueError,PermissionError):return None,{'unavailable':'Offer, identity, mission or research no longer eligible'}


def _view(record,headers,envelope,actor,employer):
    result=deepcopy(record);assessment,current=_current(record,headers,envelope,actor,employer)
    result['changed_dependencies']=[k for k in sorted(set(current)|set(record['dependencies'])) if current.get(k)!=record['dependencies'].get(k)]
    result['stale']=bool(result['changed_dependencies'])
    result['qualification_review']=qualification(record,assessment,employer,headers,result['stale'])
    return result


def qualification(record,assessment,employer,headers,stale=False):
    # Authority remains in the existing service. The same pure checks below
    # drive both real hand-off readiness and owner-only copied-input replay.
    try:
        env=offers._load();actor=_actor(headers);offer=offers._record(env,actor,employer,record['offer_id'])
        approved=offer['state']=='employer_approved' and offers._eligible(env,offer)
    except (ValueError,PermissionError):approved=False
    return qualification_checks(record,assessment,approved,stale)


def qualification_checks(record,assessment,approved,stale=False):
    """Single development gate evaluator; pure and incapable of authorising writes."""
    reasons=[];trace=[];criteria=[];q=record.get('qualification',{})
    def check(key,passed,reason):
        trace.append({'id':key,'passed':bool(passed),'reason':reason})
        if not passed:reasons.append(reason)
    for key in pipeline.CRITERIA:
        item=q.get(key,{})
        note=pipeline._supported(item.get('note'));source=pipeline._supported(item.get('source'))
        required=CUSTOMER if key in {'problem','priority','buyer','funding','decision','timing','relationship','next_action'} else CUSTOMER|{'Seller review'}
        typed=item.get('kind') in required
        criteria.append({'id':key,'note_supported':note,'reference_supported':source,'kind_allowed':typed,
            'required_kinds':sorted(required),'passed':note and source and typed})
        if not note or not source:reasons.append('Missing '+pipeline.CRITERIA[key][0]);continue
        if not typed:reasons.append('Customer/seller confirmation required: '+pipeline.CRITERIA[key][0])
    check('customer_attestation',record.get('customer_attested'),'Attest that customer evidence was actually received and is permitted')
    check('seller_review',record.get('reviewed'),'Explicit seller qualification review required')
    check('next_action',pipeline._supported(record.get('next_action')) and record.get('development_owner'),'Accountable next action required')
    check('seller_proof',pipeline._supported(record.get('proof')) and pipeline._supported(record.get('alternatives')),'Seller proof/rights and competitive alternatives review required')
    check('active',record['activity']=='Active','Candidate is paused or retired')
    check('fresh',not stale,'Stale — Reassess changed dependencies')
    check('research_basis',assessment and assessment['buying_trigger']['tier']!='Research only','Research only; no current supported development basis')
    check('pipeline_identity',assessment and assessment['buying_trigger']['identity_scope']['identity_owner'] in {'existing_banking_reference','existing_aviation_reference'},'Accepted enterprise reference required; unbound identity cannot enter Pipeline')
    check('employer_approval',approved,'Current separate employer approval required')
    return {'ready':not reasons,'reasons':reasons,'classification':'Seller-reviewed evidence completeness, not independent customer verification',
        'criterion_trace':criteria,'gate_trace':trace}


@verified_service_read('commercial_context.view')
def records(identifier='',*,headers=None):
    actor=_actor(headers);env=offers._load();employer=offers._selected(env,actor)
    if identifier:
        return _view(_versions(env,actor,employer,identifier,headers)[-1],headers,env,actor,employer)
    out=[]
    for versions in env['users'].get(offers._key(actor),{}).get('development',{}).values():
        try:_scope(versions[-1],actor,employer,headers)
        except PermissionError:continue
        out.append(_view(versions[-1],headers,env,actor,employer))
    return sorted(out,key=lambda r:(r['activity']!='Active',r['enterprise'],r['offer_name']))


def _append(env,versions,record,headers,action):
    if len(versions)>=100:raise ValueError('Pilot limit: one hundred development revisions')
    record=json.loads(canonical(record));record['version']=len(versions)+1;record['updated_at']=pipeline.now()
    versions.append(record);offers._persist(env,headers,action,record['id']);return deepcopy(record)


@verified_service_write('commercial_context.edit')
def create(shortlist_id,shortlist_version,assessment_id,confirmed=False,*,headers=None):
    if confirmed is not True:raise ValueError('Intentional private development confirmation required')
    actor=_actor(headers,True);env=offers._load();employer=offers._selected(env,actor)
    shortlist=next((r for r in offers.shortlist_snapshot(headers=headers) if r['id']==shortlist_id and r['version']==shortlist_version),None)
    if not shortlist or shortlist['stale']:raise ValueError('Reviewed shortlist changed; review again')
    entry=next((r for r in shortlist['entries'] if r['assessment_id']==assessment_id),None)
    if not entry:raise PermissionError('Reviewed assessment unavailable')
    a=next((r for r in offers.discover('offer',shortlist['offer_id'],shortlist['source_cutoff'],intelligence=True,headers=headers) if r['assessment_id']==assessment_id),None)
    if not a or not a['buying_trigger']['shortlist_eligible']:raise ValueError('Assessment changed; reassess')
    offer=offers._record(env,actor,employer,a['offer_id'])
    identifier='dev-'+digest(canonical([actor.workspace,actor.user_id,employer['id'],a['offer_id'],a['enterprise_id']]))[:32]
    private=_private(env,actor)
    if identifier in private:
        _scope(private[identifier][-1],actor,employer,headers,True)
        return deepcopy(private[identifier][-1])  # Intentional repeat cannot overwrite notes.
    if len(private)>=50:raise ValueError('Pilot limit: fifty private development candidates')
    record={'id':identifier,'author':actor.user_id,'workspace_id':actor.workspace,'employer_id':employer['id'],
        'enterprise_id':a['enterprise_id'],'enterprise_slug':a['enterprise_slug'],'enterprise':a['enterprise_name'],
        'offer_id':offer['id'],'offer_name':offer['content']['name'],'offer_version':offer['version'],
        'shortlist_id':shortlist_id,'shortlist_version':shortlist_version,'assessment_snapshot':deepcopy(a),
        'dependencies':dependencies(a,offer,employer,offers.resolve_commercial_mission(headers)),
        'state':'Investigate','activity':'Active','development_owner':actor.user_id,'due_date':'',
        'challenge':'','insight':a['why_account'],'first_conversation':a['entry_play'],
        'diagnostic':(a['buying_trigger'].get('entry_play_detail') or {}).get('diagnostic',''),
        'proof':'','alternatives':'; '.join(a['contradictions']),'next_action':'Identify a permitted customer route, then ask: '+a['next_validation_action'],
        'engagement':'','economics':'Unknown; no numeric value inferred','buying_group':{r:{'status':'Hypothesis','note':'','source':''} for r in ROLES},
        'buyer_role_hypothesis':offer['content']['buyers'],'qualification':{},'customer_attested':False,'reviewed':False,
        'created_at':pipeline.now(),'pipeline_id':None,'classification':'Private seller development; not a qualified opportunity'}
    _scope(record,actor,employer,headers,True)
    private[identifier]=[]
    return _append(env,private[identifier],record,headers,'development_created')


@verified_service_write('commercial_context.edit')
def save(identifier,expected_version,values,*,headers=None):
    actor=_actor(headers,True);env=offers._load();employer=offers._selected(env,actor)
    versions=_versions(env,actor,employer,identifier,headers,True);record=deepcopy(versions[-1])
    if type(expected_version) is not int or record['version']!=expected_version:raise ValueError('Development changed; reload before saving')
    if record['pipeline_id']:raise ValueError('Handed-off record is retained; use the authorised Pipeline view')
    allowed=set(TEXT_FIELDS)|{'state','activity','due_date','qualification','buying_group','customer_attested','reviewed'}
    if not isinstance(values,dict) or set(values)-allowed:raise ValueError('Only development fields may be edited')
    for key in TEXT_FIELDS:
        if key in values:record[key]=offers._text(values[key])
    for key in ('state','activity','due_date'):
        if key in values:record[key]=offers._text(values[key],64)
    if record['state'] not in STEPS or record['activity'] not in {'Active','Paused','Retired'}:raise ValueError('Choose a development step and activity')
    if record['due_date']:date.fromisoformat(record['due_date'])
    if 'qualification' in values:
        q=values['qualification']
        if not isinstance(q,dict) or set(q)-set(pipeline.CRITERIA):raise ValueError('Existing Pipeline criteria only')
        record['qualification']={}
        for key,item in q.items():
            if not isinstance(item,dict) or set(item)!={'note','source','kind','date'}:raise ValueError('Evidence needs note, source, kind and date')
            row={k:offers._text(v,2000 if k in {'note','source'} else 64) for k,v in item.items()}
            if row['kind'] not in KINDS:raise ValueError('Choose an evidence distinction')
            if row['date'] and date.fromisoformat(row['date'])>date.today():raise ValueError('Evidence date cannot be future')
            if row['kind'] in CUSTOMER:
                if not row['date'] or not pipeline._supported(row['note']) or not pipeline._supported(row['source']):raise ValueError('Customer evidence needs actual dated note and permitted reference')
                public=record['assessment_snapshot']['buying_trigger']['timeline']
                if any(row['source'] in {f['source_id'],f['id'],f['source_url']} for f in public):raise ValueError('Public trigger reference is not customer confirmation')
            record['qualification'][key]=row
    if 'buying_group' in values:
        group=values['buying_group']
        if not isinstance(group,dict) or set(group)-set(ROLES):raise ValueError('Role-based buying group only')
        record['buying_group']={}
        for role,item in group.items():
            if not isinstance(item,dict) or set(item)!={'status','note','source'}:raise ValueError('Buying role needs status, note and reference')
            row={k:offers._text(v,1000) for k,v in item.items()}
            if row['status'] not in {'Hypothesis','Customer-reported','Unknown','Disconfirmed'}:raise ValueError('Unsupported role status')
            if row['status']=='Customer-reported' and (not row['note'] or not row['source']):raise ValueError('Role confirmation needs permitted evidence')
            record['buying_group'][role]=row
    record['customer_attested']=values.get('customer_attested') is True
    record['reviewed']=values.get('reviewed') is True  # every revision requires fresh human attestation
    viewed=_view(record,headers,env,actor,employer)
    if record['state']!='Investigate' and record['activity']=='Active':
        if viewed['stale'] or record['assessment_snapshot']['buying_trigger']['tier']=='Research only':raise ValueError('Reassess research before development progression')
        problem=record['qualification'].get('problem',{})
        if problem.get('kind') not in CUSTOMER or not record['customer_attested']:raise ValueError('Record actual customer problem validation before progression')
        if record['state'] in {'Create Preference','Qualify'} and not all(pipeline._supported(record[k]) for k in ('challenge','insight','diagnostic','proof','alternatives','next_action')):
            raise ValueError('Preference needs a challenge, insight, diagnostic, proof, alternatives and next action')
        if record['state']=='Qualify' and not viewed['qualification_review']['ready']:raise ValueError('; '.join(viewed['qualification_review']['reasons']))
    return _append(env,versions,record,headers,'development_saved')


@verified_service_write('commercial_context.edit')
def reassess(identifier,expected_version,confirmed=False,*,headers=None):
    if confirmed is not True:raise ValueError('Explicit reassessment required')
    actor=_actor(headers,True);env=offers._load();employer=offers._selected(env,actor)
    versions=_versions(env,actor,employer,identifier,headers,True);record=deepcopy(versions[-1])
    if type(expected_version) is not int or record['version']!=expected_version or record['pipeline_id']:raise ValueError('Development changed or handed off')
    a,deps=_current(record,headers,env,actor,employer)
    if not a:raise ValueError('Current assessment unavailable; preserve notes and continue research')
    record.update(assessment_snapshot=a,dependencies=deps,state='Investigate',reviewed=False,customer_attested=False,offer_version=a['offer_version'])
    return _append(env,versions,record,headers,'development_reassessed')


def handoff_checks(record,qualification_result):
    """Actual preconditions shared with read-only inspection; never a write grant."""
    selected=record.get('state')=='Qualify'
    return {'ready':selected and qualification_result['ready'], 'explicit_qualify_selected':selected,
        'qualification_inputs_ready':qualification_result['ready'], 'already_recorded':bool(record.get('pipeline_id')),
        'separate_confirmation_required':True, 'version_and_authority_checked_at_write':True, 'write_authorised_by_inspection':False}


@verified_service_write('commercial_context.edit')
def handoff(identifier,expected_version,confirmed=False,*,headers=None):
    if confirmed is not True:raise ValueError('Explicit human-reviewed Pipeline hand-off required')
    actor=_actor(headers,True);env=offers._load();employer=offers._selected(env,actor)
    versions=_versions(env,actor,employer,identifier,headers,True);record=deepcopy(versions[-1])
    if record['pipeline_id']:
        # Idempotent return; do not overwrite existing Pipeline progression.
        return pipeline.get_opportunity(record['pipeline_id'],headers=headers)
    if type(expected_version) is not int or record['version']!=expected_version:raise ValueError('Development changed; reload')
    view=_view(record,headers,env,actor,employer)
    if not handoff_checks(record,view['qualification_review'])['ready']:raise ValueError('Qualification incomplete: '+'; '.join(view['qualification_review']['reasons']))
    # The outer verified service transaction journals BOTH stores. Failure in
    # create/update/private link or audit rolls back the complete hand-off.
    opp=pipeline.create_opportunity(record['enterprise_slug'],values={'title':record['offer_name']+' — '+record['enterprise'],
        'problem':record['challenge'],'solution':record['insight'],'next_action':record['next_action']},headers=headers)
    opp=pipeline.update_opportunity(opp['id'],opp['version'],{'qualification':{k:{'note':v['note'],'source':v['source']} for k,v in record['qualification'].items()},
        'stage':'Qualified','evidence_reviewed':'yes','confirm':'yes',
        'activity':'Seller-controlled development '+record['id']+' v'+str(record['version'])+'; private origin retained; customer evidence is seller-reported, not independently verified.'},headers=headers)
    record['pipeline_id']=opp['id'];record['handoff_at']=pipeline.now()
    _append(env,versions,record,headers,'development_pipeline_handoff')
    return opp
