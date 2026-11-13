"""Native, scoped private development forms; inputs grant no authority."""
from html import escape as e
from . import seller_development as service, design_system as ds
from . import sales_pipeline
from .buying_trigger_views import sources
from .offers_views import form,hidden,field,link,url


def select(name,value,choices,label):
    return '<label>'+e(label)+'<select name="'+e(name)+'">'+''.join('<option '+('selected ' if v==value else '')+'value="'+e(v,quote=True)+'">'+e(v)+'</option>' for v in choices)+'</select></label>'


def body(path,state,q,headers):
    ds.context_link(url('/development'),'My development')
    if not q.get('candidate'):
        records=service.records(headers=headers)
        content='<p>Private customer development. Record what you learn; decide each next step.</p>'
        if not records:content+='<p>No development candidates yet. Start from a reviewed shortlist.</p>'+link('/shortlists','Open reviewed shortlists')
        for r in records:
            content+='<article class="pair"><h2>'+e(r['enterprise'])+'</h2><p>'+e(r['offer_name'])+'</p><p>'+e('Stale — Reassess' if r['stale'] else r['state'])+' · '+e(r['activity'])+'</p><p>'+e(r['next_action'])+'</p>'+link('/development','Open development',candidate=r['id'])+'</article>'
        return 'My development',content
    r=service.records(q['candidate'],headers=headers);a=r['assessment_snapshot'];sources([a])
    content='<p class="eyebrow">'+e(r['enterprise']+' · '+r['offer_name'])+'</p><p>Private development · v'+str(r['version'])+' · '+e(r['state'])+'</p>'
    if r['stale']:content+='<p role="status"><strong>Stale — Reassess</strong>: '+e(', '.join(r['changed_dependencies']))+'. Your customer notes are retained.</p>'
    customer_status='Seller-reported customer evidence; not independent verification' if r['customer_attested'] and r['qualification'].get('problem',{}).get('kind') in service.CUSTOMER else 'Seller hypothesis; customer validation unknown'
    content+='<p>'+e(a['buying_trigger']['tier'])+' · '+e(customer_status)+'</p>'
    content+='<h2>Customer challenge</h2><p>'+e(r['challenge'] or 'Not yet customer-validated')+'</p><h2>Commercial insight</h2><p>'+e(r['insight'])+'</p><h2>First conversation</h2><p>'+e(r['first_conversation'])+'</p><h2>Next step</h2><p>'+e(r['next_action'])+'</p><p>Owner: '+e(r['development_owner'])+' · '+e(r['due_date'] or 'No due date')+'</p>'
    if r['pipeline_id']:return 'Development hand-off',content+'<p><a href="/flora/sales/'+e(r['pipeline_id'])+'">Open authorised Pipeline record</a></p><p>Development history is retained. Pipeline stages are managed in Pipeline.</p>'
    values=hidden('candidate',r['id'])+hidden('version',r['version'])
    labels={'challenge':'Customer outcome / problem','insight':'Customer-first commercial insight (hypothesis)','first_conversation':'Specific first conversation (hypothesis)','diagnostic':'Permission-based diagnostic and proof artifact','proof':'Seller delivery proof, rights and constraints','alternatives':'Existing approach, alternatives and disconfirming evidence','next_action':'Accountable next action','engagement':'Actual engagement and outcome; distinguish unknowns','economics':'Benefit levers, costs, assumptions and evidence; unknown values stay unknown'}
    values+='<details open><summary>Progress and next action</summary>'+select('state',r['state'],service.STEPS,'Development task — seller judgement')+select('activity',r['activity'],('Active','Paused','Retired'),'Activity')
    for k in ('challenge','insight','first_conversation','diagnostic','next_action'):values+=field(k,r[k],labels[k],area=True)
    values+='<label>Optional due date<input type="date" name="due_date" value="'+e(r['due_date'],quote=True)+'"></label></details>'
    values+='<details><summary>Proof, competition and commercial assumptions</summary>'
    for k in ('proof','alternatives','engagement','economics'):values+=field(k,r[k],labels[k],area=True)
    values+='</details><details><summary>Buying group — roles are hypotheses until evidenced</summary><p>No named people or relationships are generated.</p><p>Offer role hypothesis: '+e(r['buyer_role_hypothesis'])+'</p>'
    for i,role in enumerate(service.ROLES):
        item=r['buying_group'].get(role,{})
        values+='<fieldset><legend>'+e(role)+'</legend>'+select('role_'+str(i)+'_status',item.get('status','Unknown'),('Hypothesis','Customer-reported','Unknown','Disconfirmed'),'Relationship status')+field('role_'+str(i)+'_note',item.get('note',''),'Role context / permitted seller-supplied details',True)+field('role_'+str(i)+'_source',item.get('source',''),'Permitted reference')+'</fieldset>'
    values+='</details><details><summary>Customer validation and qualification</summary><p>Customer statements are evidence reported by you, not independent verification by FLORA. Public releases and internal task completion do not confirm customer need or access.</p>'
    for key,(label,_) in sales_pipeline.CRITERIA.items():
        item=r['qualification'].get(key,{})
        values+='<fieldset><legend>'+e(label)+'</legend>'+field('q_'+key+'_note',item.get('note',''),'Observed statement / review',True)+field('q_'+key+'_source',item.get('source',''),'Permitted supporting reference')+select('q_'+key+'_kind',item.get('kind','Seller hypothesis'),service.KINDS,'Evidence distinction')+'<label>Actual evidence date<input type="date" name="q_'+key+'_date" value="'+e(item.get('date',''),quote=True)+'"></label></fieldset>'
    values+='<label><input type="checkbox" name="customer_attested" value="yes"> I actually received the customer evidence recorded as such, and may retain these references privately.</label><label><input type="checkbox" name="reviewed" value="yes"> I reviewed timing, authority, funding, incumbent constraints, seller proof/rights and all qualification inputs for this revision.</label></details>'
    content+=form('/development-save',values,'Save development')
    if r['stale']:content+=form('/development-reassess',hidden('candidate',r['id'])+hidden('version',r['version'])+'<label><input type="checkbox" name="confirmed" value="yes" required> Reassess current research; retain my notes and reset internal review.</label>','Reassess')
    check=r['qualification_review']
    content+='<details><summary>Pipeline readiness</summary><p>'+e(check['classification'])+'</p><ul>'+''.join('<li>'+e(x)+'</li>' for x in check['reasons'])+'</ul></details>'
    if r['state']=='Qualify' and check['ready']:
        content+=form('/development-handoff',hidden('candidate',r['id'])+hidden('version',r['version'])+'<label><input type="checkbox" name="confirmed" value="yes" required> I explicitly authorise this reviewed candidate to enter Qualified Pipeline under existing rules.</label>','Create reviewed Pipeline entry')
    return 'Develop opportunity',content


def submit(path,values,headers):
    suffix=path.removeprefix('/flora/offers');allowed={'csrf','candidate','version','confirmed'}
    if suffix=='/development-create':allowed={'csrf','shortlist','version','assessment','confirmed'}
    if suffix=='/development-save':
        allowed|=set(service.TEXT_FIELDS)|{'state','activity','due_date','customer_attested','reviewed'}
        allowed|={f'q_{key}_{part}' for key in sales_pipeline.CRITERIA for part in ('note','source','kind','date')}
        allowed|={f'role_{i}_{part}' for i in range(len(service.ROLES)) for part in ('status','note','source')}
    if set(values)-allowed or any(len(v)!=1 for v in values.values()):raise ValueError('Unsupported or duplicate development fields')
    def one(k,default=''):return values.get(k,[default])[0]
    if suffix=='/development-create':
        r=service.create(one('shortlist'),int(one('version')),one('assessment'),one('confirmed')=='yes',headers=headers)
    elif suffix=='/development-save':
        data={k:one(k) for k in service.TEXT_FIELDS if k in values}
        data.update({k:one(k) for k in ('state','activity','due_date') if k in values})
        data.update(customer_attested=one('customer_attested')=='yes',reviewed=one('reviewed')=='yes')
        data['qualification']={key:{part:one('q_'+key+'_'+part) for part in ('note','source','kind','date')} for key in sales_pipeline.CRITERIA if one('q_'+key+'_note') or one('q_'+key+'_source')}
        data['buying_group']={role:{part:one(f'role_{i}_{part}','Unknown' if part=='status' else '') for part in ('status','note','source')} for i,role in enumerate(service.ROLES)}
        r=service.save(one('candidate'),int(one('version')),data,headers=headers)
    elif suffix=='/development-reassess':r=service.reassess(one('candidate'),int(one('version')),one('confirmed')=='yes',headers=headers)
    elif suffix=='/development-handoff':
        r=service.handoff(one('candidate'),int(one('version')),one('confirmed')=='yes',headers=headers)
        return '/flora/sales/'+r['id']
    else:raise ValueError('Unsupported development action')
    return url('/development',candidate=r['id'])
