"""Shared executive understanding view; static candidate assessments, no stores."""
from html import escape
from . import visual_templates as visual
from .understanding import assess, load_review, before_after, STATES
from .model import load_assessment
from .registry import enterprise_domain
from .unified_views import page, breadcrumb


def relationship_visual(data, report, review, slug):
    stages = ['Strategic objective','Business challenge','Operational capability','Technology dependency','Transformation programme','Supplier / contract','Measured outcome']
    labels = {row['id']: row.get('title', row['id']) for key in ('capabilities','programmes','suppliers','gaps') for row in data[key]}
    labels.update({c['id']: c['title'] for c in report['conclusions']})
    labels.update({'LBG-A2030-PLATFORMS':'Core-platform renewal','AV-STRATEGY':'Reliability and low cost'})
    for o in review['observations']:
        if 'Jetstream' in o['candidate']['statement']: labels[o['candidate']['claim_id']]='Jetstream / planning tools'
    shapes=[];links=[]
    for i,(stage,id) in enumerate(zip(stages,review['stage_ids'])):
        x=15+i*226
        href='#conclusion-'+id if any(c['id']==id for c in report['conclusions']) else '#relationships'
        if any(c['id']==id for c in data['claims']): href=data.get('route_root','/flora/banking/research')+'/evidence/'+id
        elif any(o['candidate']['claim_id']==id for o in review['observations']): href='#claim-'+id
        href=escape(href,quote=True)
        label=labels.get(id,id)
        is_gap=any(g['id']==id for g in data['gaps'])
        # Positions are an enquiry sequence, NOT asserted edges. No solid arrows
        # manufacture a strategy-to-outcome causal chain.
        shapes.append(visual.text(x+12,24,stage,width=25,size=12))
        shapes.append(f"<a href='{href}' aria-label='{escape(stage+': '+label,quote=True)}'><title>{escape(label)}</title><rect class='vt-box' x='{x}' y='45' width='208' height='170' rx='16' fill='{'#f4ecdc' if is_gap else '#e6eee1'}' stroke='#afc3b4'/>"+visual.text(x+12,76,label,width=21,size=14)+visual.text(x+12,184,'Unknown / evidence needed' if is_gap else 'Inspect scope and evidence',width=25,size=11,bold=False)+'</a>')
        if i<6:shapes.append(f"<path d='M{x+208} 125 H{x+225}' stroke='#a2b9a9' stroke-dasharray='3 4'/>")
        links.append(f"<li><a href='{href}'>{escape(stage)}: {escape(label)}</a></li>")
    return ("<style>.understanding-map .vt-scroll svg{min-width:1500px}.understanding-map .vt-links{list-style:none;padding:0}</style><figure class='vt-figure understanding-map'><figcaption class='vt-caption'><h2>Connected enterprise understanding</h2><p>Question map, not a proven causal chain. Inspect factual, interpretive and missing relationships below. Supplier context does not establish a contract.</p></figcaption>"
        + "<div class='vt-scroll'><svg role='img' aria-labelledby='understanding-map-title' viewBox='0 0 1600 245'><title id='understanding-map-title'>Seven research questions connecting strategy, capabilities, dependencies and outcomes</title>"+''.join(shapes)+"</svg></div><ul class='vt-links' aria-label='Text alternative to relationship map'>"+''.join(links)+'</ul></figure>')


def render(data, review, as_of):
    result=assess(data,review,as_of);comparison=before_after(data,review,as_of)
    slug='lloyds' if data['enterprise_twin_id']=='BK-ENT-001' else 'easyjet'
    esc=lambda x:escape(str(x),quote=True)
    claims={c['id']:c for c in result['claims']};sources={s['id']:s for s in result['sources']}
    body=(f"<section class='ux-hero' id='content'><p class='eyebrow'>Research Intelligence / Enterprise Understanding</p><h1>{esc(data['enterprise_name'])}.<br>What the evidence supports.</h1><p>Separate attributable facts, analytical connections and unresolved questions. Research cut-off {esc(as_of)}.</p></section>"
          "<p class='ux-disclosure'>Read-only candidate assessment. No canonical acceptance, causal proof, sales qualification or IT-001 maturity certification. Source support means the recorded assertion is supported within its stated scope and period; company statements are not independent outcome verification.</p>"
          "<nav class='ux-tabs' aria-label='Understanding sections'><a href='#conclusions'>Key conclusions</a><a href='#relationships'>Relationships</a><a href='#evidence'>Evidence quality</a><a href='#changes'>What changed</a><a href='#next'>Research next</a></nav>")
    body+=relationship_visual(data,result,review,slug)+"<section id='conclusions'><h2>What FLORA understands</h2>"
    for c in result['conclusions']:
        refs=''.join(f"<li><a href='#claim-{esc(cid)}'>{esc(cid)} — inspect exact passage and scope</a></li>" for cid in c['claim_ids'])
        missing=''.join(f'<li>{esc(m)}</li>' for m in c['missing_evidence'])
        body+=f"<article class='ux-card' id='conclusion-{esc(c['id'])}'><p class='eyebrow'>{esc(c['kind'])} · candidate reasoning</p><h3>{esc(c['title'])}</h3><p>{esc(c['statement'])}</p><p><strong>What changed:</strong> {esc(c['change_from_v2'])}</p><details><summary>Supporting evidence and missing evidence</summary><ul>{refs}</ul><h4>Still required</h4><ul>{missing}</ul></details></article>"
    body+="</section><section id='relationships'><h2>Factual, interpretive and unknown relationships</h2>"
    body+="<p>Legacy verification flags are preserved in the underlying research. This stricter review requires an exact scoped edge assessment; it does not rewrite historical findings.</p>"
    for e in result['relationships']:
        if not e['id'].startswith('V3-'):continue
        body+=f"<details class='ux-claim'><summary>{esc(e['subject'])} → {esc(e['predicate'])} → {esc(e['object'])} · {esc(e['state'])}</summary><p>{esc(e['reason'])}</p><p>Scope: {esc(e['scope'])}. Period: {esc(e['period'])}. Causation proven: no.</p><ul>"+''.join(f"<li><a href='#claim-{esc(cid)}'>{esc(cid)}</a></li>" for cid in e['claim_ids'])+'</ul><p>Missing: '+esc('; '.join(e['missing_evidence']))+'</p></details>'
    body+="</section><section id='evidence'><h2>Evidence quality and exact assertion support</h2><p>Original primary · reviewed primary excerpt · search-index only · independent-publisher secondary · unverified reference · interpretation/unsupported assertion. Publisher diversity alone does not prove independent corroboration.</p>"
    for row in review['observations']:
        cid=row['candidate']['claim_id'];c=claims[cid];s=sources[row['source_id']]
        body+=f"<details class='ux-claim' id='claim-{esc(cid)}'><summary>{esc(cid)} · {esc(s['kind'])}</summary><blockquote>{esc(c['statement'])}</blockquote><p>{esc(row['segment']['section_heading'])}</p><p>{esc(c['quality_state'])}. Entity: {esc(c['subject'])}. Period: {esc(c['period'])}.</p><p><a href='{esc(s['url'])}' rel='noreferrer'>Inspect attributable source</a> · Published {esc(s['publication_date'] or 'Unknown')} · Retrieved {esc(s['retrieved_at'])} · {esc(s['currentness'])}.</p><p>Original bytes: {'archived and checked' if s['primary_content_sha256'] else 'not archived; excerpt hash only'}. Independent outcome corroboration: {'reviewed' if c['independent_corroboration'] else 'not established'}.</p><p>{esc(s['limitation'])}</p></details>"
    body+='</section><section id="changes"><h2>Before and after — same assessment rules</h2><div class="ux-grid">'
    for key,label in [('exact_support_reviewed','Scoped assertion/passages reviewed'),('independent_corroborated_claims','Independently corroborated claims'),('reviewed_company_outcome_observations','Reviewed company outcome observations'),('evidence_supported_causal_outcomes','Causal business outcomes established'),('unresolved_conflicts','Unresolved scope/time conflicts')]:
        body+=f"<article class='ux-card'><h3>{label}</h3><p>{comparison['before'][key]} → {comparison['after'][key]}</p></article>"
    body+="</div><p>Zero here means no qualifying review under these rules, not that the prior Twin contained no information. Additional records are not a maturity grade. No gap is automatically closed.</p>"
    for c in result['contradictions']:
        body+=f"<article class='ux-claim'><h3>{esc(c['id'])}</h3><p>{esc(c['status'])}</p><p>{esc(c['treatment'])}</p><ul>"+''.join(f"<li><a href='#claim-{esc(cid)}'>{esc(cid)}</a></li>" for cid in c['claim_ids'])+'</ul></article>'
    body+="<details><summary>Fourteen-dimension dossier coverage</summary>"+''.join(f"<p><strong>{esc(d['label'])}</strong>: {len(d['reviewed_candidate_ids'])} new scoped candidate passages. {esc('; '.join(d['deficiencies']))}</p>" for d in result['dossier'])+'</details></section>'
    body+="<section id='next'><h2>Research next, and why</h2>"+''.join(f"<article class='ux-claim'><h3>{esc(t['title'])}</h3><p>{esc(t['question'])}</p><p>{esc(t['rationale'])}</p></article>" for t in result['next_research'][:3])
    body+=f"<p><a href='/enterprises/{slug}/research-diagnostic'>Research diagnostic and bounded cycle →</a> · <a href='/enterprises/{slug}'>Return to Enterprise Twin →</a></p></section>"
    return body


def understanding_page(slug, headers=None):
    domain=enterprise_domain(slug);data=load_assessment(domain)
    from datetime import date
    body=breadcrumb(True,data)+render(data,load_review(domain),date.today().isoformat())
    return page(data['enterprise_name']+' — Enterprise Understanding',body,headers,'enterprises','/enterprises/'+slug+'/understanding')
