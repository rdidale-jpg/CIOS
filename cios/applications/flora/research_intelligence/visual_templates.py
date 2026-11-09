"""Responsive, accessible SVG templates for the shared visual specification."""
from html import escape as e
import re
from math import sin, cos, radians
from textwrap import wrap, shorten
from .visual_specs import local_link

STYLE="""
.vt-figure{margin:24px 0;border:1px solid #cbd9d0;border-radius:22px;background:#fffefa;overflow:hidden}.vt-caption{padding:22px 26px 0}.vt-caption h3{font-size:1.45rem;margin:0}.vt-caption p{color:#5b6d63;max-width:850px;margin:8px 0}.vt-scroll{overflow-x:auto;padding:6px 16px}.vt-scroll svg{display:block;width:100%;height:auto;min-width:660px}.vt-figure[data-diagram-type=value-chain] svg{min-width:1000px}.vt-scroll a:hover .vt-box,.vt-scroll a:focus .vt-box{stroke:#926329;stroke-width:3;filter:brightness(.97)}.vt-scroll a:focus{outline:0}.vt-scroll text{font-family:inherit;pointer-events:none}.vt-links{display:flex;flex-wrap:wrap;gap:8px;margin:12px 24px}.vt-links a{border:1px solid #cbd9d0;background:#f0f4ed;padding:7px 12px;border-radius:22px;text-decoration:none;font-size:.85rem;min-height:40px;display:flex;align-items:center}.vt-meta{margin:14px 26px 22px;font-size:.82rem;color:#586b60}.vt-score-key{font-size:.82rem;color:#586b60}.vt-empty{padding:24px}.vt-figure a:focus-visible{outline:3px solid #9b5cff;outline-offset:3px}@media(max-width:640px){.vt-scroll{display:none}.vt-links{display:grid;grid-template-columns:1fr 1fr;margin:16px}.vt-links a{border-radius:12px;align-items:start;padding:12px}.vt-caption{padding:18px 18px 0}.vt-meta{margin:16px}}@media(prefers-reduced-motion:reduce){.vt-figure *{transition:none!important}}
"""
INK='#174d3f'; MUTED='#536b5b'; LINE='#aec4b3'


def text(x,y,value,width=25,size=16,color=INK,anchor='start',bold=True):
    lines=wrap(str(value),width=width,break_long_words=False,break_on_hyphens=False) or ['']
    return ''.join(f"<text x='{x}' y='{y+i*(size+5)}' font-size='{size}' fill='{color}' text-anchor='{anchor}' font-weight='{700 if bold else 400}'>{e(line)}</text>" for i,line in enumerate(lines))


def linked(n,body):
    url=local_link(n['url'])
    return f"<a href='{e(url,quote=True)}' aria-label='{e(n['label'],quote=True)}'><title>{e(n['label'])} · {e(n['verification'])} · {len(n['evidence_refs'])} evidence references</title>{body}</a>"


def box(n,x,y,w=250,h=100,fill='#edf3e9',subtitle=None):
    caption=subtitle or n['verification'].split(';')[0]
    caption_width=max(18,int((w-32)/6))
    lines=wrap(caption,width=caption_width,break_long_words=False)
    caption_y=y+h-16-(max(1,len(lines))-1)*16
    return linked(n,f"<rect class='vt-box' x='{x}' y='{y}' width='{w}' height='{h}' rx='16' fill='{fill}' stroke='{LINE}'/>"+text(x+16,y+30,n['label'],width=max(16,int(w/9)),size=15)+text(x+16,caption_y,caption,width=caption_width,size=11,color=MUTED,bold=False))


def pestle(nodes):
    shapes=[];cx,cy=450,240
    for i,n in enumerate(nodes):
        a,b=-90+i*60,-90+(i+1)*60
        def point(radius,angle):return (cx+radius*cos(radians(angle)),cy+radius*sin(radians(angle)))
        p1=point(185,a+1);p2=point(185,b-1);p3=point(82,b-1);p4=point(82,a+1)
        d=f'M {p1[0]} {p1[1]} A 185 185 0 0 1 {p2[0]} {p2[1]} L {p3[0]} {p3[1]} A 82 82 0 0 0 {p4[0]} {p4[1]} Z'
        x,y=point(136,(a+b)/2)
        shapes.append(linked(n,f"<path class='vt-box' d='{d}' fill='{['#dcebdd','#f3e8d5','#e5eee8'][i%3]}' stroke='white' stroke-width='3'/>"+text(round(x),round(y),n['label'],width=15,size=14,anchor='middle')))
    return (900,480,"".join(shapes)+f"<circle cx='{cx}' cy='{cy}' r='75' fill='{INK}'/>"+text(cx,cy-6,'External forces',width=20,size=16,color='white',anchor='middle')+text(cx,cy+24,'PESTLE',size=11,color='#cfe2d4',anchor='middle'))


def forces(nodes):
    # Position by the established framework category, not array order.
    positions={'rival':(325,190),'entry':(325,28),'entrants':(325,28),'supplier':(30,190),'buyer':(620,190),'substitut':(325,352)}
    shapes=["<path d='M450 130 V185 M285 240 H320 M580 240 H615 M450 295 V347' fill='none' stroke='#a2b9a9' stroke-width='3'/>"]
    for n in nodes:
        key=next((k for k in positions if k in n['label'].lower()),None)
        if key is None:raise ValueError('Five Forces requires its standard categories')
        x,y=positions[key];shapes.append(box(n,x,y,h=115,fill='#dcebdd' if key=='rival' else '#f5efe3',subtitle=shorten(n['summary'],width=85,placeholder='…')))
    return 900,490,''.join(shapes)


def chain(nodes):
    width=max(800,len(nodes)*152+20);shapes=[]
    for i,n in enumerate(nodes):
        x=12+i*152
        points=f'{x},34 {x+128},34 {x+146},105 {x+128},176 {x},176 {x+15},105'
        shapes.append(linked(n,f"<polygon class='vt-box' points='{points}' fill='{['#dcebdd','#e9eee3','#f3e8d5'][i%3]}' stroke='white' stroke-width='3'/>"+text(x+30,60,f'{i+1:02}',size=11,color=MUTED)+text(x+27,88,n['label'],width=14,size=15)))
    return width,212,''.join(shapes)


def operating(nodes):
    cols=4;shapes=[text(20,30,'BUSINESS CAPABILITIES / CONCEPTUAL MAP',width=80,size=12,color=MUTED)]
    for i,n in enumerate(nodes):
        x=20+(i%cols)*235;y=55+(i//cols)*125
        shapes.append(box(n,x,y,215,108,fill=['#e8efe4','#f5ecdc','#edf1ec'][i//cols%3],subtitle=f"{len(n['opportunity_links'])} linked research hypotheses"))
    return 960,75+((len(nodes)+cols-1)//cols)*125,''.join(shapes)


def ecosystem(spec):
    nodes=spec['nodes'];height=max(350,45+len(nodes)*100);center=height/2
    shapes=[f"<rect x='20' y='{center-55}' width='255' height='110' rx='20' fill='{INK}'/>"+text(148,center-12,spec['enterprise']['label'],width=20,color='white',anchor='middle')+text(148,center+34,'Public relationship evidence',size=11,color='#d7e5db',anchor='middle')]
    for i,n in enumerate(nodes):
        y=22+i*100;relations=[r for r in spec['relationships'] if r['object']==n['id'] and r['subject']==spec['enterprise']['id']]
        verified=any(r['verified'] for r in relations);status='Announced plan / not yet live' if any('planned' in r['predicate'] for r in relations) else 'Source-supported / scope unverified' if verified else 'Reported / verify primary' if 'reported relationship' in n['verification'] else 'Relationship unknown'
        shapes.append(f"<path d='M275 {center} C360 {center} 350 {y+42} 430 {y+42}' fill='none' stroke='{INK if verified else LINE}' stroke-width='{2 if verified else 1.5}'"+('' if verified else " stroke-dasharray='5 5'")+"/>")
        shapes.append(box(n,430,y,420,84,fill='#e1eddf' if verified else '#f4efe4',subtitle=status))
    return 900,height,''.join(shapes)


def opportunities(nodes):
    keys=list(nodes[0].get('ratings',{})) if nodes else [];shapes=[]
    for j,k in enumerate(keys):shapes.append(text(500+j*105,28,{'strategic_relevance':'Relevance','commercial_accessibility':'Access','evidence_maturity':'Evidence','seller_fit':'Seller fit'}[k],size=12,anchor='middle'))
    for i,n in enumerate(nodes):
        y=45+i*86
        body=f"<rect class='vt-box' x='15' y='{y}' width='930' height='76' rx='12' fill='{['#e6eee1','#f7f1e6'][i%2]}' stroke='#d4dfd1'/>"+text(32,y+28,f"{n['priority']:02}",size=14,color=MUTED)+text(78,y+27,n['label'],width=43,size=13)
        for j,k in enumerate(keys):
            score=n['ratings'][k]['score'];x=500+j*105
            for step in range(3):body+=f"<circle cx='{x-20+step*20}' cy='{y+28}' r='5' fill='{INK if step<score else '#c5d2c1'}'/>"
            body+=text(x,y+56,f'{score}/3',size=11,anchor='middle',color=MUTED)
        shapes.append(linked(n,body))
    return 960,55+len(nodes)*86,''.join(shapes)


def render_visual(spec):
    kind=spec['diagram_type'];nodes=spec['nodes']
    if not nodes:return "<div class='vt-empty'>No supported visual nodes. Research gaps remain open.</div>"
    if kind=='pestle':w,h,body=pestle(nodes)
    elif kind=='five-forces':w,h,body=forces(nodes)
    elif kind=='value-chain':w,h,body=chain(nodes)
    elif kind=='operating-model':w,h,body=operating(nodes)
    elif kind=='ecosystem':w,h,body=ecosystem(spec)
    elif kind=='opportunities':w,h,body=opportunities(nodes)
    else:raise ValueError('Unknown visual template')
    identifier='vt-'+kind+'-'+re.sub(r'[^A-Za-z0-9_-]','-',spec['research_assessment_id'])
    nav="<nav class='vt-links' aria-label='"+e(spec['title'],quote=True)+" destinations'>"+''.join(f"<a href='{e(local_link(n['url']),quote=True)}'>{e(n['label'])}</a>" for n in nodes)+"</nav>"
    return f"<figure class='vt-figure' data-diagram-type='{kind}'><figcaption class='vt-caption'><h3>{e(spec['title'])}</h3><p>{e(spec['summary'])}</p></figcaption><div class='vt-scroll' tabindex='0' aria-label='Scrollable {e(spec['title'],quote=True)}'><svg viewBox='0 0 {w} {h}' role='group' aria-labelledby='{identifier}-title {identifier}-desc'><title id='{identifier}-title'>{e(spec['title'])}</title><desc id='{identifier}-desc'>Linked research nodes. Equivalent text navigation follows. All analytical claims retain their evidence status.</desc>{body}</svg></div>{nav}<p class='vt-meta'>Research assessment updated {e(spec['last_research_update'])}. Source periods differ. {e(spec['verification'])}. <a href='{e(local_link(spec['opportunities_url']),quote=True)}'>Explore commercial hypotheses →</a></p></figure>"
