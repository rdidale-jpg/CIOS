"""Read-only visual bridge from enterprise capabilities to commercial hypotheses.

No independent business-owner inference, opportunity state, or Pipeline write path.
"""
from collections import defaultdict
from html import escape as e

STYLE = """
.eo{--eo:#174d3f;--eo-gold:#b58a4b;margin:18px 0;color:#174d3f}
.eo *{box-sizing:border-box}
.eo-hero{background:linear-gradient(125deg,#153d33,#276252);border-radius:22px;padding:27px;color:white}
.eo-hero h2{font:600 clamp(1.55rem,3vw,2.2rem)/1.15 Georgia,serif;color:white;margin:9px 0}
.eo-hero p{color:#d4e6db;max-width:720px}
.eo-kicker{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
.eo-grid{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(250px,1fr);gap:17px;margin:17px 0}
.eo-map{position:relative;background:radial-gradient(ellipse at center,#eaf0e5,#f7f5e9);border:1px solid #c8d8ca;border-radius:20px;padding:20px;min-width:0}
.eo-map:before{content:"";position:absolute;inset:30px 18%;border:1px dashed #b2cabb;border-radius:50%;pointer-events:none}
.eo-map>*{position:relative}
.eo-map h3{font-size:1.1rem;margin:0 0 8px}
.eo-node-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.eo-node{font:inherit;color:#174d3f;text-align:left;background:#fffef8;border:1px solid #b8cdbb;border-radius:14px;padding:15px;min-height:102px;cursor:pointer}
.eo-node strong,.eo-node small{display:block;overflow-wrap:anywhere}
.eo-node strong{line-height:1.28}
.eo-node small{font-size:.77rem;color:#52695e;margin-top:6px}
.eo-node[aria-pressed=true]{background:#174d3f;border-color:#174d3f;color:white}
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
.eo-fallback{margin-top:12px;font-size:.83rem}
.eo-fallback summary{cursor:pointer;min-height:44px}
@media(max-width:800px){.eo-grid{grid-template-columns:1fr}}
@media(max-width:520px){.eo-node-grid{grid-template-columns:1fr 1fr}.eo-node{padding:11px}.eo-module-grid{grid-template-columns:repeat(2,1fr)}.eo-hero{padding:20px}}
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

def enterprise_overlay(data,projection):
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
        for pid in programmes:
            groups[('programme',pid)].append(row)
        if not capabilities and not programmes:
            unmapped.append(row)
    if unmapped:
        groups[('unmapped','unknown')]=unmapped
    if not groups:
        return _shell("<div class='eo-hero'><h2>Enterprise opportunity overlay</h2><p>No mapped hypothesis associations in this research snapshot. No organisational reporting lines should be inferred.</p></div>")
    nodes=[];panels=[]
    for ix,((kind,identifier),rows) in enumerate(groups.items()):
        key='anchor-'+str(ix)
        label=(cap_labels.get(identifier,identifier) if kind=='capability' else
               programme_labels.get(identifier,identifier) if kind=='programme' else
               'Capability not yet mapped')
        kind_label={'capability':'Research capability','programme':'Programme signal','unmapped':'Unmapped research'}[kind]
        nodes.append("<button type='button' class='eo-node' data-eo-choice='"+key+"' aria-controls='eo-panel-"+key+"' aria-pressed='false'><small>"+e(kind_label)+"</small><strong>"+e(label)+"</strong><small>"+str(len(rows))+" linked research hypotheses</small></button>")
        links="".join("<li><a href='"+e(row['url'],quote=True)+"'>"+e(row['title'])+"</a></li>" for row in rows)
        panels.append("<div data-eo-panel='"+key+"' id='eo-panel-"+key+"'><span class='eo-label'>"+e(kind_label)+" · not organisation ownership</span><h3>"+e(label)+"</h3><p class='eo-unknown'>Business owner: Unknown</p><p>Research links to "+str(len(rows))+" hypothesis/hypotheses. This association does not establish business-unit accountability, procurement, funding, or a verified technology delivery dependency.</p><ul>"+links+"</ul><p class='eo-warning'>Validate the customer business owner and accountable outcome before advancing any opportunity.</p></div>")
    fallback="<details class='eo-fallback'><summary>Accessible enterprise anchors and opportunity links</summary><ul>"+"".join("<li>"+e(cap_labels.get(identifier,identifier) if kind=='capability' else programme_labels.get(identifier,identifier) if kind=='programme' else 'Capability not yet mapped')+": "+", ".join("<a href='"+e(row['url'],quote=True)+"'>"+e(row['title'])+"</a>" for row in rows)+"</li>" for (kind,identifier),rows in groups.items())+"</ul></details>"
    return _shell("<div class='eo-hero'><span class='eo-kicker'>Enterprise opportunity overlay</span><h2>Locate the possibility in the business.</h2><p>Select an existing capability or programme signal to see its research hypotheses. These associations are not verified organisation ownership or delivery dependencies.</p></div><div class='eo-grid'><div class='eo-map'><h3>Enterprise capability landscape</h3><div class='eo-node-grid'>"+"".join(nodes)+"</div></div><aside class='eo-inspector' aria-live='polite'>"+"".join(panels)+"</aside></div>"+fallback)


MODULES=[
 ('financials','Financial opportunity','Estimated TCV, ACV, funded spend, net benefit, pricing and margin','Opportunity deal value and allocated budget are Unknown. Public corporate investment is not supplier spend.','Request customer-owned outcome baseline, addressable spending scope and funding decision.'),
 ('owner','Business ownership','Where the problem lives, accountable business leader and delivery owner','Actual organisational unit, outcome owner and named economic buyer are unverified. Procurement is not the business owner.','Identify business sponsor and the accountable executive who owns the outcome.'),
 ('stakeholders','Stakeholder network','Sponsor, economic buyer, technical influencers, blockers and access','Roles are hypotheses; no verified named buyer, sponsor or relationship status.','Build a role-based stakeholder map and validate it through customer contact.'),
 ('hotbuttons','Hot buttons & outcomes','Customer priorities, measurable outcomes and individual motivations','Potential AI net benefit, adoption and controls are analytical themes, not validated personal hot buttons.','Test the desired outcomes with the accountable stakeholders.'),
 ('competition','Competitors & alternatives','Incumbents, internal delivery, platform partners and competitor positioning','Existing internal teams and published Google Cloud involvement are alternatives, not confirmed competitors for an active procurement.','Determine make/buy decision, partners, incumbency and competitive evaluation.'),
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
        panels.append("<article class='eo-panel' data-eo-panel='"+e(key)+"' id='eo-module-"+e(key)+"'><span class='eo-label'>"+e(sub)+"</span><h3>"+e(label)+"</h3><p>"+e(value)+"</p><p class='eo-label'>Next qualification action</p><p>"+e(next_step)+"</p><p class='eo-warning'>No public-source assessment is a customer-validated or private Pipeline fact.</p></article>")
    return _shell("<div class='eo-hero'><span class='eo-kicker'>Opportunity development / read-only preview</span><h2>Build the commercial case. Then earn the pursuit.</h2><p>"+e(row['title'])+" · Select a development dimension. Actual customer facts belong in an authorised workspace.</p></div><div class='eo-module-grid'>"+"".join(nodes)+"</div>"+"".join(panels)+"<p><a class='eo-action' href='#commercial-capture'>Review controlled Pipeline capture →</a></p><p class='eo-warning'>Business owner, stakeholder motivations, funding, procurement and customer demand remain unverified. No standalone CRM record is created here.</p>")

# A structured story with interpreted rather than asserted causal connections.
STORY_STYLE = """
.eo-story{border:1px solid #c6d6c9;border-radius:22px;background:radial-gradient(circle at 55% 30%,#e8f0e5,#f7f5eb 75%);padding:22px;margin:18px 0}
.eo-story h2{font:600 clamp(1.5rem,3vw,2.3rem)/1.15 Georgia,serif;margin:6px 0}
.eo-story-intro{max-width:700px;font-size:.9rem}
.eo-story-path{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:24px 0}
.eo-story-node{min-width:0;border:1px solid #b8cbb9;border-radius:16px;background:#fffefa;padding:17px 12px;position:relative}
.eo-story-node:not(:last-child):after{content:"→";position:absolute;right:-13px;top:40%;color:#a78650;font-size:18px;z-index:2;background:#eef1e7;border-radius:50%}
.eo-story-node strong{display:block;font-size:.95rem;line-height:1.2}
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
    nodes=''.join("<article class='eo-story-node'><span class='eo-story-status'>"+e(state)+"</span><strong>"+e(title)+"</strong><p>"+e(value)+"</p></article>" for title,state,value in story)
    return "<style>"+STORY_STYLE+"</style><section class='eo-story' aria-label='Visual commercial opportunity story'><span class='eo-kicker'>Enterprise → Opportunity → Pursuit</span><h2>Understand where this opportunity could sit.</h2><p class='eo-story-intro'>A visual research hypothesis, not a proven customer programme or buying decision. Business ownership is separate from procurement.</p><div class='eo-story-path'>"+nodes+"</div><p class='eo-story-foot'>Arrows show the analyst's investigation sequence, not established dependencies, contract relationships or buyer authority.</p><div class='eo-story-actions'><a href='#commercial-capture'>Develop in authorised Pipeline →</a><a href='/enterprises/lloyds?lens=opportunities'>Back to Enterprise opportunity overlay →</a><a href='#full-research-evidence'>Full research and evidence ↓</a></div><p class='eo-label'>Next customer validation</p><p>"+e(commercial.get('next_commercial_action') or 'Verify business owner and requirement')+"</p></section>"
