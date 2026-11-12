"""Read-only visual bridge from enterprise capabilities to commercial hypotheses.

No independent business-owner inference, opportunity state, or Pipeline write path.
"""
from collections import defaultdict
from html import escape as e

STYLE = """
.eo{--eo:#174d3f;--eo-gold:#b58a4b;margin:18px 0;color:#174d3f}
.eo *{box-sizing:border-box}
.eo-hero{background:linear-gradient(125deg,#153d33,#276252);border-radius:22px;padding:27px;color:white}
.eo-hero h1,.eo-hero h2{font:600 clamp(1.55rem,3vw,2.2rem)/1.15 Georgia,serif;color:white;margin:9px 0}
.eo-hero p{color:#d4e6db;max-width:720px}
.eo-kicker{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
.eo-grid{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(280px,1fr);gap:17px;margin:17px 0}
.eo-map{position:relative;background:radial-gradient(ellipse at center,#eaf0e5,#f7f5e9);border:1px solid #c8d8ca;border-radius:20px;padding:20px;min-width:0}
.eo-map:before{display:none;content:"";position:absolute;inset:30px 18%;border:1px dashed #b2cabb;border-radius:50%;pointer-events:none}
.eo-map>*{position:relative}
.eo-map h3{font-size:1.1rem;margin:0 0 8px}
.eo-node-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.eo-node{font:inherit;color:#174d3f;text-align:left;background:#fffef8;border:1px solid #b8cdbb;border-radius:14px;padding:15px;min-height:102px;cursor:pointer}
.eo-node strong,.eo-node small{display:block;overflow-wrap:anywhere}
.eo-node strong{line-height:1.28}
.eo-node small{font-size:.77rem;color:#52695e;margin-top:6px}
.eo .eo-node:hover,.eo .eo-node:focus-visible{background:#e5eddf;color:#174d3f}.eo .eo-node:hover small{color:#52695e}.eo-node[aria-pressed=true]{background:#174d3f;border-color:#174d3f;color:white}
.eo-node[aria-pressed=true] small{color:#cee0d4}
.eo-inspector{background:#fffef8;border:1px solid #cbd9c9;border-radius:20px;padding:21px;min-width:0}
.eo-inspector h3{font:600 1.45rem Georgia,serif;line-height:1.2}
.eo-inspector p{line-height:1.5}
.eo-inspector ul{padding-left:18px}
.eo-inspector li{margin:9px 0}
.eo-inspector a{color:#174d3f}
.eo-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:#8b693d}
.eo-warning{font-size:.85rem;border-left:3px solid var(--eo-gold);padding-left:12px}
.eo-unknown{display:inline-block;background:#f4ecdb;border-radius:9px;padding:5px 9px;font-size:.8rem}
.eo-module-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:18px 0}
.eo-module{font:inherit;text-align:center;min-height:78px;padding:10px 5px;border:1px solid #c6d5c7;border-radius:12px;background:#fffef7;color:#174d3f;cursor:pointer}
.eo-module[aria-pressed=true]{background:#174d3f;color:white}
.eo-panel{background:#fffdf7;border:1px solid #cbd9c9;border-radius:18px;padding:21px}
.eo-panel h3{font:600 1.4rem Georgia,serif;margin:0}
.eo-panel p{margin:10px 0}
.eo-action{display:inline-flex;border-radius:22px;padding:10px 15px;background:#174d3f;color:white!important;min-height:44px;align-items:center;text-decoration:none}
.eo button:focus-visible,.eo a:focus-visible{outline:3px solid #b58a4b;outline-offset:3px}
.eo-comparison{overflow:auto}.eo-comparison table{width:100%;border-collapse:collapse;font-size:.8rem}.eo-comparison th,.eo-comparison td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #cbd7c6}.eo-comparison caption{text-align:left;padding:12px}.eo-landmark{display:block;width:100%;height:100%;min-height:120px;grid-column:2;grid-row:2;align-self:center}.eo-symbol{width:34px;height:34px;float:right;color:#799782}.eo-dots{display:block;color:#af8241;font-size:.85rem;margin-top:8px;letter-spacing:3px}.eo-map-key{font-size:.74rem;color:#647361}.eo-ratings{display:grid;gap:7px}.eo-ratings div{border-bottom:1px solid #d7dfd1;padding:8px 0}.eo-ratings dt{font-size:.7rem;text-transform:uppercase}.eo-ratings dd{margin:4px 0;font-size:.84rem}.eo-row{display:block;min-height:48px;width:100%;text-align:left;font:inherit;color:#174d3f;border:1px solid #ced9c9;border-radius:12px;padding:12px;background:#f5f3e7;cursor:pointer}.eo-inspector ul{list-style:none;padding:0}.eo-inspector{align-self:start;position:sticky;top:16px}.eo-fallback{margin-top:12px;font-size:.83rem}
.eo-fallback summary{cursor:pointer;min-height:44px}
@media(max-width:900px){.eo-grid{grid-template-columns:1fr}.eo-inspector{position:static}}
@media(max-width:520px){.eo-landmark{grid-column:1/-1;grid-row:auto;height:130px}.eo-node-grid{grid-template-columns:1fr 1fr}.eo-node{padding:11px}.eo-module-grid{grid-template-columns:repeat(2,1fr)}.eo-hero{padding:20px}}
@media(prefers-reduced-motion:reduce){.eo *{transition:none!important}}
@media print{.eo-inspector [hidden],.eo-panel[hidden]{display:block!important}.eo-module-grid{display:none}.eo-grid{grid-template-columns:1fr}}
"""
SCRIPT = """
(function(){
 document.querySelectorAll('[data-eo-root]:not([data-eo-ready])').forEach(function(root){
   root.dataset.eoReady='true';
   var choices=Array.from(root.querySelectorAll('[data-eo-choice]'));
   var panels=Array.from(root.querySelectorAll('[data-eo-panel]'));
   function select(id){
     choices.forEach(function(c){c.setAttribute('aria-pressed',String(c.dataset.eoChoice===id));});
     panels.forEach(function(p){p.hidden=p.dataset.eoPanel!==id;});
   }
   choices.forEach(function(c){c.addEventListener('click',function(){select(c.dataset.eoChoice);});});
   if(choices.length)select(choices[0].dataset.eoChoice);
 });
})();
"""

def _shell(content):
    return "<style>"+STYLE+"</style><section class='eo' data-eo-root>"+content+"<script>"+SCRIPT+"</script></section>"

def enterprise_overlay(data,projection,comparison_visual='',page_heading=False):
    """Inspect canonical capability and programme associations, never implied org ownership."""
    groups=defaultdict(list)
    cap_labels={c['id']:c.get('title') or c['id'] for c in data.get('capabilities',[])}
    programme_labels={p['id']:p.get('title') or p['id'] for p in data.get('programmes',[])}
    all_rows=projection['candidates']
    unmapped=[]
    for row in all_rows:
        capabilities=list(dict.fromkeys(cid for cid in row.get('capability_ids',[]) if cid in cap_labels))
        programmes=list(dict.fromkeys(pid for pid in row.get('programme_ids',[]) if pid in programme_labels))
        for cid in capabilities:
            groups[('capability',cid)].append(row)
        if not capabilities:
            for pid in programmes:
                groups[('programme',pid)].append(row)
        if not capabilities:
            unmapped.append(row)
    if unmapped:
        groups[('unmapped','unknown')]=unmapped
    if not groups:
        return _shell("<div class='eo-hero'><h2>Enterprise opportunity overlay</h2><p>No mapped hypothesis associations in this research snapshot. No organisational reporting lines should be inferred.</p></div>")
    nodes=[];panels=[]
    from .visual_intelligence import _art, _icon
    for ix,((kind,identifier),rows) in enumerate(groups.items()):
        key='anchor-'+str(ix)
        label=(cap_labels.get(identifier,identifier) if kind=='capability' else
               programme_labels.get(identifier,identifier) if kind=='programme' else
               'Capability not yet mapped')
        kind_label={'capability':'Research capability','programme':'Programme signal','unmapped':'Unmapped research'}[kind]
        nodes.append("<button type='button' class='eo-node' data-eo-choice='"+key+"' aria-controls='eo-panel-"+key+"' aria-pressed='false'><svg class='eo-symbol' viewBox='0 0 48 48' aria-hidden='true'>"+_icon('network',8,8,1)+"</svg><small>"+e(kind_label)+"</small><strong>"+e(label)+"</strong><small>"+str(len(rows))+" linked research hypotheses</small><span class='eo-dots' aria-hidden='true'>"+' '.join('●' for row in rows)+"</span></button>")
        links="".join("<li><button class='eo-row' type='button' data-eo-choice='candidate-"+e(row['id'])+"' aria-controls='eo-candidate-"+e(row['id'])+"' aria-pressed='false'>"+e(row['title'])+" <span aria-hidden='true'>→</span></button></li>" for row in rows)
        panels.append("<div data-eo-panel='"+key+"' id='eo-panel-"+key+"'><span class='eo-label'>"+e(kind_label)+" · not organisation ownership</span><h3>"+e(label)+"</h3><p class='eo-unknown'>Business owner: Unknown</p><p>Research links to "+str(len(rows))+" hypothesis/hypotheses. This association does not establish business-unit accountability, procurement, funding, or a verified technology delivery dependency.</p><ul>"+links+"</ul><p class='eo-warning'>Validate the customer business owner and accountable outcome before advancing any opportunity.</p></div>")
    for row in all_rows:
        ratings=''.join("<div><dt>"+e(d['label'])+"</dt><dd>"+str(d['score'])+" / 3 · "+e(d['anchor'])+"</dd></div>" for d in row['dimensions'])
        proof=next((proof for proof in row['support'] if proof['supported']),None)
        evidence=("<p><a href='"+e(proof['url'],quote=True)+"'>Inspect exact passage · "+e(proof['period'])+"</a></p>" if proof else "<p>Current source support missing. Historical hypothesis retained.</p>")
        panels.append("<article data-eo-panel='candidate-"+e(row['id'])+"' id='eo-candidate-"+e(row['id'])+"'><span class='eo-label'>Unqualified research hypothesis · "+e(row['id'])+"</span><h3>"+e(row['title'])+"</h3><p>"+e(row['commercial']['business_problem'])+"</p><dl class='eo-ratings'>"+ratings+"</dl><small>Authored "+e(row['assessment_date'])+"; separate assessments, not win probability.</small>"+evidence+"<p class='eo-warning'>Existing internal delivery or an incumbent may remove the service gap. Buyer, budget and external demand remain unverified.</p><p><strong>Next:</strong> "+e(row['commercial']['next_commercial_action'])+"</p><a class='eo-action' href='"+e(row['url'],quote=True)+"'>Develop hypothesis & inspect dossier →</a></article>")
    fallback="<details class='eo-fallback'><summary>Compare all "+str(len(all_rows))+" hypotheses · accessible text alternative</summary><div class='eo-comparison'><table><caption>Authored assessments; source context is not customer demand. Counts are not additive.</caption><thead><tr><th scope='col'>Hypothesis</th><th scope='col'>Research capability association</th><th scope='col'>Separate assessments</th></tr></thead><tbody>"+''.join("<tr><th scope='row'><a href='"+e(row['url'],quote=True)+"'>"+e(row['title'])+"</a></th><td>"+e('; '.join(cap_labels[cid] for cid in row.get('capability_ids',[]) if cid in cap_labels) or 'Capability not yet mapped')+"</td><td>"+'<br>'.join(e(d['label'])+': '+str(d['score'])+' / 3' for d in row['dimensions'])+"</td></tr>" for row in all_rows)+"</tbody></table></div>"+comparison_visual+"</details>"

    heading="h1" if page_heading else "h2"
    return _shell("<div class='eo-hero'><span class='eo-kicker'>Enterprise opportunity overlay</span><"+heading+">Locate the possibility in the business.</"+heading+"><p>Select a capability, then a hypothesis in the inspector. These associations are not verified organisation ownership or delivery dependencies.</p></div><div class='eo-grid'><div class='eo-map'><h3>Enterprise capability landscape</h3><p class='eo-map-key'>● Hypotheses associated with this capability · counts overlap</p><div class='eo-node-grid'><svg class='eo-landmark' viewBox='360 120 560 220' role='img' aria-label='Conceptual banking illustration; not an organisational map'>"+_art('banking','eo-bank',True)+"</svg>"+"".join(nodes)+"</div></div><aside class='eo-inspector' aria-live='polite'>"+"".join(panels)+"</aside></div>"+fallback)


MODULES=[
 ('financials','Financial opportunity','Estimated TCV, ACV, funded spend, net benefit, pricing and margin','Opportunity deal value and allocated budget are Unknown. Public corporate investment is not supplier spend.','Request customer-owned outcome baseline, addressable spending scope and funding decision.'),
 ('owner','Business ownership','Where the problem lives, accountable business leader and delivery owner','Actual organisational unit, outcome owner and named economic buyer are unverified. Procurement is not the business owner.','Identify business sponsor and the accountable executive who owns the outcome.'),
 ('stakeholders','Stakeholder network','Sponsor, economic buyer, technical influencers, blockers and access','Roles are hypotheses; no verified named buyer, sponsor or relationship status.','Build a role-based stakeholder map and validate it through customer contact.'),
 ('hotbuttons','Hot buttons & outcomes','Customer priorities, measurable outcomes and individual motivations','Published business outcomes are context, not validated personal hot buttons.','Test the desired outcomes with the accountable stakeholders.'),
 ('competition','Competitors & alternatives','Incumbents, internal delivery, platform partners and competitor positioning','Internal delivery, a platform partner or no purchase may be alternatives. No active competitive procurement is established.','Determine make/buy decision, partners, incumbency and competitive evaluation.'),
 ('solution','Proposed solution','Service scope, differentiation, capabilities, delivery options and proof','A potential service concept is not a confirmed requirement.','Define the smallest customer-validated work package and evidence of differentiation.'),
 ('strategy','Capture & win strategy','Preference creation, positioning, pursuit decisions and win themes','No customer-confirmed buying process or approved win strategy yet.','Form a capture hypothesis after validating access and buying triggers.'),
 ('actions','Pursuit execution','Actions, owners, decision gates, milestones and next review','Research next actions exist; no authorised customer pursuit milestones are established.','Agree the next evidence-gathering action before capture or promotion.')
]

def pursuit_preview(row):
    """Read-only contextual pursuit modules; private inputs remain in the existing authorised Pipeline."""
    nodes=[];panels=[]
    for i,(key,label,sub,known,next_step) in enumerate(MODULES):
        nodes.append("<button class='eo-module' type='button' data-eo-choice='"+e(key)+"' aria-controls='eo-module-"+e(key)+"' aria-pressed='false'>"+e(label)+"</button>")
        value=known
        if key=='solution':value="Potential service: "+row['commercial'].get('proposed_service','Unknown')+" This is a hypothesis, not an approved requirement."
        if key=='actions':next_step=row['commercial'].get('next_commercial_action',next_step)
        if key=='competition':value=row['commercial'].get('supplier_position',known)+" "+known
        if key=='stakeholders':value='Inferred decision functions: '+', '.join(row['commercial'].get('buyer_functions',[]))+'. '+known
        if key=='hotbuttons':value='Potential business outcome: '+row['commercial']['business_problem']+' '+known
        panels.append("<article class='eo-panel' data-eo-panel='"+e(key)+"' id='eo-module-"+e(key)+"'><span class='eo-label'>"+e(sub)+"</span><h3>"+e(label)+"</h3><p>"+e(value)+"</p><p class='eo-label'>Next qualification action</p><p>"+e(next_step)+"</p></article>")
    return _shell("<div class='eo-hero'><span class='eo-kicker'>Opportunity development / read-only preview</span><h2>Develop the opportunity.</h2><p>Eight read-only decision lenses. Customer facts require an authorised workspace.</p></div><div class='eo-module-grid'>"+"".join(nodes)+"</div>"+"".join(panels)+"<p><a class='eo-action' href='#commercial-capture'>Review controlled Pipeline capture →</a></p><p class='eo-warning'>Business owner, stakeholder motivations, funding, procurement and customer demand remain unverified. No standalone CRM record is created here.</p>")

# A structured story with interpreted rather than asserted causal connections.
STORY_STYLE = """
.eo-story{border:1px solid #c6d6c9;border-radius:22px;background:radial-gradient(circle at 55% 30%,#e8f0e5,#f7f5eb 75%);padding:22px;margin:18px 0}
.eo-story h2{font:600 clamp(1.5rem,3vw,2.3rem)/1.15 Georgia,serif;margin:6px 0}
.eo-story-art{display:block;width:100%;height:135px}.eo-story-intro{max-width:700px;font-size:.9rem}
.eo-story-path{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:24px 0}
.eo-story-node{font:inherit;text-align:left;cursor:pointer;color:#174d3f;min-height:120px;min-width:0;border:1px solid #b8cbb9;border-radius:16px;background:#fffefa;padding:17px 12px;position:relative}
.eo-story-node:not(:last-child):after{content:"→";position:absolute;right:-13px;top:40%;color:#a78650;font-size:18px;z-index:2;background:#eef1e7;border-radius:50%}
.eo-story-node[aria-pressed=true]{border:2px solid #174d3f;background:#e2ecde}.eo-story-node small{display:block;margin-top:12px;font-size:.75rem}.eo-story-node strong{display:block;font-size:.95rem;line-height:1.2}
.eo-story-node p{font-size:.78rem;color:#50695b;overflow-wrap:anywhere;margin:8px 0}
.eo-story-status{display:inline-block;font-size:.67rem;color:#856438;font-weight:750;margin-bottom:9px}
.eo-story-actions{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:20px}
.eo-story-actions a{border-radius:22px;border:1px solid #bdd0be;padding:11px 16px;text-decoration:none;font-size:.9rem;color:#174d3f}
.eo-story-actions a:first-child{background:#174d3f;color:white}
.eo-story-foot{font-size:.75rem;color:#66796a}
.cv-full-research{background:#fffdf7;border:1px solid #bfcfbf;border-radius:18px;padding:18px 22px;margin:22px 0}
.cv-full-research>summary{font-weight:750;font-size:1.05rem;cursor:pointer;min-height:44px}
@media(max-width:680px){.eo-story-path{grid-template-columns:repeat(2,minmax(0,1fr))}.eo-story-node:nth-child(2):after{display:none}}
@media print{.eo-story-path{grid-template-columns:repeat(2,1fr)}}
"""

def opportunity_story(data,row):
    """First-screen narrative. Evidence links and decisions remain in the canonical dossier."""
    capabilities={c['id']:c.get('title',c['id']) for c in data.get('capabilities',[])}
    names=[capabilities[i] for i in row.get('capability_ids',[]) if i in capabilities]
    context='; '.join(names) if names else 'Capability association not established'
    commercial=row['commercial']
    story=[
      ('01 / Enterprise anchor','Research association',context),
      ('02 / Business challenge','Analyst interpretation',commercial.get('business_problem') or 'Business outcome to validate'),
      ('03 / Possible service','Unqualified proposition',commercial.get('proposed_service') or 'No service defined'),
      ('04 / Buying gap','Customer validation required','Business owner, addressable spend, budget, demand and procurement: Unknown')
    ]
    from .visual_intelligence import _art
    proof=next((proof for proof in row['support'] if proof['supported']),None)
    source=("<p class='eo-warning'>Source-supported context · "+e(proof['period'])+". <a href='"+e(proof['url'],quote=True)+"'>Exact passage & provenance →</a></p>" if proof else "<p class='eo-warning'>Current source support missing; inspect the retained historical dossier.</p>")
    titles=['Capability context','Business outcome','Potential service','Customer decision']
    nodes=''.join("<button type='button' class='eo-story-node' data-eo-choice='story-"+str(i)+"' aria-controls='eo-story-"+str(i)+"' aria-pressed='false'><span class='eo-story-status'>"+e(state)+"</span><strong>"+e(titles[i])+"</strong><small>Inspect "+str(i+1)+" / 4 →</small></button>" for i,(title,state,value) in enumerate(story))
    panels=''.join("<article class='eo-panel' data-eo-panel='story-"+str(i)+"' id='eo-story-"+str(i)+"'><span class='eo-label'>"+e(state)+"</span><h3>"+e(title)+"</h3><p>"+e(value)+"</p>"+(source if i==0 else '')+("<p>Existing delivery may already satisfy this outcome. Inspect counterevidence before proposing an external service.</p>" if i in (1,2) else '')+"</article>" for i,(title,state,value) in enumerate(story))
    return _shell("<style>"+STORY_STYLE+"</style><section class='eo-story' aria-label='Visual commercial opportunity story'><span class='eo-kicker'>Enterprise → Opportunity → Pursuit</span><h2>Understand where this opportunity could sit.</h2><p class='eo-story-intro'>Select a stage to inspect its context. Research association and analyst interpretation are distinct from verified customer demand.</p><svg class='eo-story-art' viewBox='360 120 560 220' role='img' aria-label='Conceptual enterprise banking illustration'>"+_art('banking','eo-story',True)+"</svg><div class='eo-story-path'>"+nodes+"</div><div aria-live='polite'>"+panels+"</div><p class='eo-story-foot'>Arrows show the analyst's investigation sequence, not established dependencies, contract relationships or buyer authority.</p><div class='eo-story-actions'><a href='#commercial-capture'>Develop in authorised Pipeline →</a><a href='/enterprises/lloyds?lens=opportunities'>Back to Enterprise opportunity overlay →</a><a href='#full-research-evidence'>Full research and evidence ↓</a></div><p class='eo-label'>Next customer validation</p><p>"+e(commercial.get('next_commercial_action') or 'Verify business owner and requirement')+"</p><p><button class='eo-row' type='button' data-depth-print='executive'>Print executive brief</button> <button class='eo-row' type='button' data-depth-print='appendix'>Print full evidence appendix</button></p></section>")
