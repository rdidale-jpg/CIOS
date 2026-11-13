"""FLORA visual-world v1: pure SVG presentation, never an intelligence owner.

Illustrated districts explain roles, not actual deployments. Programme ribbons
show one retained research record; amber seams remain unqualified hypotheses.
All navigation is ordinary server-rendered links, including without JavaScript.
"""
from html import escape as e
from urllib.parse import urlencode
from . import technology as research

CONTRACT = 'flora-visual-world-v1'
ROLES = {
 'applications':('Applications','Enterprise workflows'),
 'cloud':('Cloud & data','Compute · storage · platforms'),
 'ai':('AI & decisions','Models · knowledge · controls'),
 'cyber':('Cybersecurity','Protect · detect · recover'),
 'services':('Technology services','Design · integrate · operate'),
 'channels':('Channels & distribution','Source · finance · deliver'),
 'infrastructure':('Infrastructure','Data centres · connectivity'),
 'frontier':('Semiconductors & frontier','IP · silicon · quantum')}
# Composition coordinates, not geographic locations or provider rankings.
WIDE={'applications':(240,190),'cloud':(560,405),'ai':(630,150),'cyber':(955,210),'services':(980,440),'channels':(790,660),'infrastructure':(310,630),'frontier':(150,425)}
PORTRAIT={'applications':(200,170),'cloud':(470,420),'ai':(600,155),'cyber':(755,365),'services':(710,620),'channels':(570,880),'infrastructure':(230,755),'frontier':(160,445)}
THEME_POS=[(620,270),(395,315),(860,335),(940,550),(430,535),(170,530)]
THEME_COMPACT=[(525,270),(330,300),(700,445),(700,735),(360,620),(145,565)]
THEME_LABELS=['AI adoption & controls','Data & application change','Cyber recovery & assurance','Provider transformation','Cloud portability','Industrial & frontier adoption']

STYLE='''
.world-page .tech-hero .eyebrow{display:none}.world-page .tech-hero p{max-width:1050px!important}.world-svg.world-wide{max-height:640px}.world-svg.world-wide .world-label{font-size:22px}.world-svg.world-wide .world-caption{font-size:15px}
.world-stage:has(.world-svg a:focus-visible) .world-detail{opacity:.18;pointer-events:none}
.world-detail:target{outline:none}
.tech.world-page{max-width:1400px;color:#243c3c}.world-page .crumb{margin:12px 0 18px}.world-page .tech-hero{display:block;padding:0 0 13px}.world-page .tech-hero h1{font-family:Georgia,'Times New Roman',serif;font-weight:400;font-size:clamp(2.4rem,4.2vw,4rem);line-height:1.08;color:#1e4640;letter-spacing:-.045em;margin:8px 0}.world-page .tech-hero p{margin:6px 0;max-width:850px;font-size:.95rem}.world-page .tech-count{display:none}.world-page .tech-nav{border-top:0;margin:0 0 9px;padding:6px 0;border-bottom:1px solid #c8d0c7;gap:18px}.world-page .tech-nav a{border-radius:0;background:none!important;color:#4c615b!important;font-size:.88rem;font-weight:500;padding:10px 0;border-bottom:2px solid transparent}.world-page .tech-nav a[aria-current]{border-color:#386c60;color:#244f44!important;font-weight:750}.world-mast{display:flex;justify-content:space-between;align-items:center;gap:15px;margin:12px 0 9px;font-size:.73rem;color:#64756b;flex-wrap:wrap}.world-mast strong{font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#426557}.world-status{display:flex;gap:7px;align-items:center}.world-status:before{content:'';width:7px;height:7px;background:#b29355;border-radius:50%}.world-stage{position:relative;isolation:isolate;margin:0 -20px;overflow:hidden;border-radius:35% 6% 28% 5%/3% 4% 3% 5%;background:radial-gradient(ellipse at 48% 44%,#e7eee3 0,#f0f2e8 36%,#f8f6ee 72%)}.world-viewport{overflow:auto;overscroll-behavior:contain}.world-svg{display:block;width:100%;height:auto;max-height:none;font-family:system-ui,sans-serif}.world-compact{display:none}.world-svg a{cursor:pointer}.world-district .world-hit{fill:transparent;stroke:transparent;stroke-width:2;pointer-events:all}.world-district:hover .world-hit,.world-district:focus-visible .world-hit{stroke:#3d7768;stroke-width:2;fill:#ffffff30;stroke-dasharray:4 5}.world-district:focus{outline:none}.world-district:focus-visible .world-label{fill:#143f34;text-decoration:underline}.world-district[aria-current] .world-halo{opacity:.9}.world-halo{opacity:0;fill:#abcdb4;filter:var(--world-blur)}.world-label{font-size:20px;font-weight:650;fill:#264b42;letter-spacing:-.025em;paint-order:stroke;stroke:#f5f5e9;stroke-width:5;stroke-linejoin:round}.world-caption{font-size:13px;fill:#64766a;paint-order:stroke;stroke:#f5f5e9;stroke-width:3}.world-street{fill:none;stroke:#a3b9a5;stroke-width:1.6}.world-flow{fill:none;stroke:#668d83;stroke-width:2;stroke-dasharray:3 8;opacity:.7}.world-flow-label{font-size:12px;letter-spacing:.09em;text-transform:uppercase;fill:#65796d}.world-ground{fill:#dce8d8;stroke:#c3d2bf;stroke-width:1}.world-detail{position:absolute;right:23px;bottom:30px;z-index:4;width:340px;max-height:440px;overflow:auto;padding:23px 25px;background:#fffdf4f5;border:1px solid #c9cfb9;border-radius:4px 24px 4px 18px;box-shadow:0 12px 45px #24483b18;backdrop-filter:blur(8px)}.world-detail h2{font-family:Georgia,serif;font-size:1.65rem;font-weight:400;color:#244c40;margin:10px 0}.world-detail p,.world-detail dl,.world-detail li{font-size:.85rem;line-height:1.55}.world-detail .eyebrow{font-size:.64rem;color:#6a7867}.world-detail .tech-source{padding:5px 0 5px 10px;margin:12px 0}.world-detail .tech-source p{font-size:.75rem}.world-detail .tech-badge{font-size:.65rem;background:#eee9d4;color:#6e5a31}.world-detail .world-close{display:block;min-height:32px;text-align:right;color:#6a7462;font-size:.75rem}.world-detail .tech-provider-links{gap:2px 9px}.world-detail .tech-provider-links a{font-size:.8rem}.world-page .tech-inspector{border-top:0}.world-detail summary{font-size:.85rem}.world-page .world-detail details{padding:8px 0!important;border:0!important;border-radius:0!important;background:transparent!important;margin:6px 0!important}.world-key{display:flex;flex-wrap:wrap;gap:20px;align-items:center;font-size:.72rem;color:#6b786b;margin:11px 0}.world-key span{display:inline-flex;align-items:center;gap:7px}.world-key i{width:20px;height:1px;background:#7e9b86;display:inline-block}.world-key i.report{background:#386f7a;height:3px}.world-key i.hypothesis{height:8px;width:8px;border:1px dashed #a57837;background:#e6c87f55;border-radius:50%}.world-bottom-note{font-size:.75rem!important;color:#68796a!important;margin:5px 0 17px!important;max-width:1000px}.world-page .tech-support{font-size:.8rem;gap:12px;border-top:1px solid #ced5c6;padding-top:13px;margin:19px 0}.world-page .tech-support a{font-weight:500;min-height:30px}.world-page .tech-section{margin:20px 0}.world-textnav{padding:10px 0!important;background:transparent!important;border:0!important;border-top:1px solid #cdd5c5!important;border-radius:0!important}.world-textnav summary{font-size:.85rem}.world-textnav ol{display:flex;flex-wrap:wrap;gap:6px 22px;padding-left:22px;font-size:.84rem}.world-textnav a{min-height:34px;display:inline-block}.world-spark{fill:#f6df9c;stroke:#a47c34;stroke-width:1.7}.world-theme-glow{fill:#d8b361;opacity:.27}.world-theme-link .world-target{fill:transparent;stroke:transparent;stroke-width:2}.world-theme-link:hover .world-target,.world-theme-link:focus-visible .world-target{stroke:#916b2b;stroke-dasharray:4 5}.world-theme-link:focus{outline:none}.world-theme-link text{fill:#75582d;font-size:16px;paint-order:stroke;stroke:#f6f1df;stroke-width:5;stroke-linejoin:round}.world-theme-link .world-theme-number{font-size:13px;fill:#674a25;font-weight:700;stroke:none}.world-theme-link[aria-current] .world-theme-glow{opacity:.7}.world-programme{font-family:system-ui,sans-serif}.world-programme .world-programme-label{fill:#214a4f;font-size:20px;font-weight:600;paint-order:stroke;stroke:#f4f5eb;stroke-width:5}.world-programme .world-programme-note{font-size:13px;fill:#416e73}.world-programme .world-programme-flow{fill:none;stroke:#397f86;stroke-width:4}.world-programme a:focus-visible{outline:3px solid #755c2d}.world-programme-pick{display:flex;align-items:center;gap:10px;font-size:.8rem;flex-wrap:wrap;margin:12px 0}.world-programme-pick label{font-size:.8rem}.world-programme-pick select{font-size:.8rem;max-width:480px;padding:8px;background:transparent;border:0;border-bottom:1px solid #aab8ad;border-radius:0}.world-programme-pick button{font-size:.8rem;padding:5px 14px;background:#e3eadc;border:1px solid #becab9;border-radius:20px;min-height:36px}.world-page:has(.world-stage) .tech-hero h1{font-size:clamp(2.3rem,4vw,3.7rem)}.world-scene-partial{font-size:.73rem;font-style:italic;color:#6f785e}.world-page .tech-source a{overflow-wrap:anywhere}.world-page .tech-footer{font-size:.73rem}.world-focus-provider{fill:#e9f0da;stroke:#90a879;stroke-width:1.5}.world-focus-provider-text{font-size:18px;fill:#315543}.world-page .world-print-title{display:none}
.world-detail-left{left:23px;right:auto}.world-svg[data-scene-mode=uses] .world-district .world-label,.world-svg[data-scene-mode=uses] .world-district .world-caption{display:none}.world-svg[data-scene-mode=work] .world-district .world-caption{display:none}
@media(max-width:1100px){.world-detail{width:300px;max-height:370px;padding:18px}.world-stage{margin:0 -8px}.world-label{font-size:21px}.world-caption{font-size:14px}}
@media(max-width:850px){.world-detail-left{left:auto}.world-wide{display:none}.world-compact{display:block;min-width:680px}.world-stage{border-radius:15px}.world-detail{position:relative;right:auto;bottom:auto;width:auto;max-height:none;margin:0 14px 18px;box-shadow:none;border-left:3px solid #759a80;border-radius:0 15px 15px 0;padding:18px}.world-label{font-size:21px}.world-caption{font-size:14px}.world-page .tech-hero h1{font-size:2.6rem}.world-key{gap:10px}.world-programme-pick select{max-width:100%}}
@media(max-width:540px){.world-page .tech-nav{gap:12px}.world-page .tech-nav a{font-size:.75rem}.world-mast{font-size:.65rem}.world-programme-pick{display:block}.world-programme-pick select{display:block;width:100%;margin:8px 0}.world-page .tech-hero h1{font-size:2.1rem}.world-page .tech-hero p{font-size:.87rem}.world-stage{margin:0 -8px}.world-mobile-hint{display:block!important}.world-detail{margin:0 9px 15px}.world-page .tech-support{gap:10px}}
@media(prefers-reduced-motion:reduce){.world-svg *{animation:none!important;transition:none!important}}
@media print{.world-wide{display:block!important}.world-compact{display:none!important}.world-stage{overflow:visible;background:#f7f8ef}.world-detail{position:static;width:auto;max-height:none;overflow:visible;border:1px solid #bbc8b4;box-shadow:none;margin:15px 0}.world-viewport{overflow:visible}.world-key,.world-bottom-note{display:block}.world-programme-pick,.world-close{display:none!important}.world-svg{break-inside:avoid}.world-detail details{display:block}.world-detail details>*{display:block!important}.world-page .world-print-title{display:block}}
'''


def target(**query):
    return research.BASE + '?' + urlencode(query)


def multiline(text,x,y,width=28,cls='world-label',line=22,anchor='middle'):
    """Bounded SVG wrapping; full original text remains in title/context detail."""
    words=text.split();lines=[];current=''
    for word in words:
        if len(current+' '+word)>width and current:lines.append(current);current=word
        else:current=(current+' '+word).strip()
    if current:lines.append(current)
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else line}">{e(s)}</tspan>' for i,s in enumerate(lines[:4]))+'</text>'


def short_text(text,limit):
    return text if len(text)<=limit else text[:limit].rsplit(' ',1)[0]+'…'


def building(x,y,w=50,h=70,color='#789b8d',roof='#b8d3c2',depth=22):
    """An isometric miniature; never a content panel or provider-importance area."""
    windows=''.join(f'<path d="M{x+8} {y-h+13+i*13}l{w-16} 10" stroke="#dcebdd" stroke-width="2" opacity=".8"/>' for i in range(max(1,(h-12)//13)))
    return f'<path d="M{x} {y-h}l{w} 15v{h}l-{w}-15z" fill="{color}"/><path d="M{x+w} {y-h+15}l{depth}-{depth//2}v{h}l-{depth} {depth//2}z" fill="#456b62"/><path d="M{x} {y-h}l{depth}-{depth//2} {w} 15-{depth} {depth//2}z" fill="{roof}"/>{windows}'


def drawing(kind):
    """Bespoke semantic miniatures, centred around a district's local origin."""
    if kind=='applications':
        return building(-70,5,40,75)+building(-20,-20,43,110,'#7e9b9d','#c5dad5')+building(35,28,40,65)+''.join(f'<path d="M{-56+i*27} -88v-12l16 6v12z" fill="#e7eee0" stroke="#799890"/>' for i in range(4))+'<path d="M-85 25Q-10 75 95 38" fill="none" stroke="#749f8b" stroke-width="3"/>'
    if kind=='cloud':
        return '<ellipse cx="0" cy="24" rx="115" ry="49" fill="#ccdfce"/><ellipse cx="0" cy="14" rx="100" ry="37" fill="#e6eee0" stroke="#a3c0ac"/>'+''.join(f'<path d="M{-75+i*38} 10q0 18 65 18v18q-65 0-65-18z" fill="{c}" stroke="#8daf9d"/><ellipse cx="{-42+i*38}" cy="10" rx="33" ry="12" fill="#dfece0" stroke="#8daf9d"/>' for i,c in enumerate(['#b0cdb7','#9fbdad','#b7d0bf']))+'<path d="M-80-36c-28 0-30-35-7-40 0-32 50-44 65-16 34-22 68 5 57 31 38 0 43 38 12 42" fill="#f9fbf1" stroke="#b0c7b5" stroke-width="2"/><path d="M-32-27v20m32-10v20m30-25v20" stroke="#79a399" stroke-dasharray="3 5"/>'
    if kind=='ai':
        points=[(-70,-8),(-43,-70),(22,-97),(70,-45),(42,15),(0,-35)]
        return '<ellipse cx="0" cy="35" rx="100" ry="30" fill="#d9e5ce"/>'+''.join(f'<path d="M0-35L{x} {y}" stroke="#8ea98b" stroke-width="2"/>' for x,y in points[:-1])+''.join(f'<circle cx="{x}" cy="{y}" r="{12 if i<5 else 26}" fill="{["#cad6a7","#c9dabd","#a9bd8c","#d2e1c4","#b1cda6","#6d9572"][i]}" stroke="#79936b"/><circle cx="{x-3}" cy="{y-3}" r="4" fill="#edf3dc"/>' for i,(x,y) in enumerate(points))+'<path d="M-4-12v40m-35-1h75" stroke="#78936b" stroke-width="2"/><ellipse cx="0" cy="-35" rx="99" ry="40" fill="none" stroke="#b5c79e" transform="rotate(-22 0 -35)"/>'
    if kind=='cyber':
        return '<ellipse cx="0" cy="30" rx="88" ry="25" fill="#dce8dc"/><path d="M-70-57L0-84 70-57v46C55 16 18 34 0 42-18 34-55 16-70-11z" fill="#c8dfd2" fill-opacity=".65" stroke="#6c9f8c" stroke-width="2"/><path d="M-33-18l22 21 49-52" fill="none" stroke="#538b75" stroke-width="5"/><path d="M-90-35Q0-135 90-35" fill="none" stroke="#9ebea9" stroke-dasharray="3 6"/>'
    if kind=='services':
        return '<path d="M-98 30l44-21 108 28 44-21" fill="none" stroke="#90a989" stroke-width="16"/><path d="M-98 26l44-21 108 28 44-21" fill="none" stroke="#e8e9cf" stroke-width="12"/>'+building(-55,0,28,54,'#aaa982','#dfdfbd')+building(25,22,28,68,'#98a68a','#d4dfbd')+'<path d="M-25-15Q0-100 40-35" stroke="#849976" stroke-width="4" fill="none"/><path d="M-25-14v48m65-70v70" stroke="#a7b69b" stroke-width="3"/>'+''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="#5c7d66"/><path d="M{x} {y+7}v17" stroke="#5c7d66" stroke-width="5"/>' for x,y in [(-72,18),(1,26),(74,43)])
    if kind=='channels':
        return '<path d="M-110 6l100-48 120 35M-110 6L0 50 110-7M-10-42V5L0 50" fill="none" stroke="#b1bb9c" stroke-width="11"/><path d="M-110 6l100-48 120 35M-110 6L0 50 110-7M-10-42V5L0 50" fill="none" stroke="#e9e9d2" stroke-width="6"/>'+''.join(f'<path d="M{x} {y}l25-13 30 11-25 14z" fill="#bdbb8a"/><path d="M{x} {y}v19l30 12v-21M{x+30} {y+10}l25-13v18l-25 14" fill="#d2d2a4" stroke="#a5a574"/>' for x,y in [(-75,-9),(-8,-40),(35,15)])
    if kind=='infrastructure':
        return '<ellipse cx="0" cy="35" rx="120" ry="37" fill="#dae2d0"/>'+building(-80,7,48,73,'#80958a','#b8c9b3')+building(-19,30,48,92,'#6b897c','#bdd0bb')+building(43,12,40,65,'#8d9e8a','#cbd5bd')+'<path d="M-100 53Q0 100 120 37M-93 62Q0 111 123 47" fill="none" stroke="#81a69b" stroke-width="2"/><path d="M100-30v68m-17-52q17-30 34 0m-28 6q11-18 22 0" fill="none" stroke="#78988d" stroke-width="2"/>'
    return '<ellipse cx="0" cy="25" rx="90" ry="30" fill="#e0e3d2"/><path d="M-65-10L0-45 65-10 0 28z" fill="#a7b7a0" stroke="#78927d"/><path d="M-42-11L0-32 42-11 0 11z" fill="#d9e6cf" stroke="#92aa8d"/>'+''.join(f'<path d="M{x}-31v-14m{x} 60v13" stroke="#91a18a" stroke-width="3"/>' for x in [-30,-15,0,15,30])+'<ellipse cx="0" cy="-65" rx="58" ry="21" fill="none" stroke="#a5b798" transform="rotate(-35 0 -65)"/><ellipse cx="0" cy="-65" rx="58" ry="21" fill="none" stroke="#829d83" transform="rotate(35 0 -65)"/><circle cx="0" cy="-65" r="10" fill="#afc7a2"/>'


def programme(data,key):
    return next((r for r in data['relationships'] if r['key']==key),data['relationships'][4])


def scene(data,lens='how',selected='',relationship='',theme='',provider=''):
    """One semantic world with mode overlays; no new research or graph records."""
    if lens not in ('how','uses','work'):raise ValueError('Unknown scene mode')
    if selected and selected not in ROLES:raise ValueError('Unknown scene district')
    if theme and theme not in {r['key'] for r in data['themes']}:raise ValueError('Unknown scene theme')
    if provider and provider not in {r['key'] for r in data['providers']}:raise ValueError('Unknown scene provider')
    if relationship and relationship not in {r['key'] for r in data['relationships']}:raise ValueError('Unknown scene programme')
    return '<div class="world-viewport" role="region" aria-label="Illustrated Technology landscape; scroll to explore on small screens" tabindex="0">'+svg(data,lens,selected,relationship,theme,provider,False)+svg(data,lens,selected,relationship,theme,provider,True)+'</div>'


def svg(data,lens,selected,relationship,theme,provider,compact):
    positions=PORTRAIT if compact else WIDE;w,h=(920,1030) if compact else (1200,800);prefix='world-p' if compact else 'world-w'
    definitions=f'''<defs><linearGradient id="{prefix}-earth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ecf0e2"/><stop offset="1" stop-color="#dbe4cd"/></linearGradient><radialGradient id="{prefix}-air"><stop stop-color="#c5dbc5" stop-opacity=".5"/><stop offset="1" stop-color="#e9eedb" stop-opacity="0"/></radialGradient><filter id="{prefix}-mist"><feGaussianBlur stdDeviation="16"/></filter></defs>'''
    # Organic terrain and contours are the shared spatial anchor across every lens.
    terrain=(f'M70 {h*.42}C40 190 {w*.38} 30 {w*.7} 100S{w+50} {h*.57} {w*.81} {h*.83}S210 {h+20} 90 {h*.7}Q10 {h*.6} 70 {h*.42}Z')
    ground=f'<ellipse cx="{w/2}" cy="{h*.57}" rx="{w*.46}" ry="{h*.39}" fill="url(#{prefix}-air)"/><path d="{terrain}" fill="url(#{prefix}-earth)" opacity=".6"/>'
    for scale in ('.91','.82','.72'):
        ground+=f'<path d="{terrain}" transform="translate({w*(1-float(scale))/2} {h*(1-float(scale))/2}) scale({scale})" fill="none" stroke="#c9d6bf" stroke-width="1" opacity=".75"/>'
    # Functional conceptual flows: paths disclose no actual customer/provider join.
    connections=[('infrastructure','cloud'),('cloud','applications'),('cloud','ai'),('ai','cyber'),('cyber','services'),('services','channels'),('channels','applications'),('frontier','infrastructure'),('frontier','cloud')]
    paths=''
    for i,(a,b) in enumerate(connections):
        x,y=positions[a];xx,yy=positions[b];mx=(x+xx)/2+(40 if i%2 else -40);my=(y+yy)/2+45
        paths+=f'<path d="M{x} {y+30}Q{mx} {my} {xx} {yy+25}" class="world-street"/><path d="M{x} {y+38}Q{mx} {my+8} {xx} {yy+33}" class="world-flow"/>'
    regions=''
    for n,(key,(x,y)) in enumerate(positions.items(),1):
        name,sub=ROLES[key];href=target(lens='how',segment=key)+'#landscape';active=' aria-current="true"' if key==selected else ''
        opacity='.38' if lens=='uses' else '.67' if lens=='work' else '1'
        regions+=f'<a href="{e(href,quote=True)}" class="world-district scene-role {key}" data-role="{key}" data-truth-class="conceptual" aria-label="{e(name+": "+sub,quote=True)}"{active}><title>{e(name)} — select to inspect role, providers and research limits</title><g transform="translate({x} {y})" opacity="{opacity}"><ellipse class="world-halo" cx="0" cy="0" rx="122" ry="89" style="--world-blur:url(#{prefix}-mist)"/><path class="world-ground" d="M-111 15Q-125-5-72-18L38-36Q90-24 112 10L93 45Q10 76-90 45Z"/>{drawing(key)}<ellipse class="world-hit" cx="0" cy="-10" rx="116" ry="100"/>{multiline(name,0,91,29,line=23)}{multiline(sub,0,115,36,"world-caption",18)}</g></a>'
    overlays=''
    if lens=='work':
        for i,(r,(x,y)) in enumerate(zip(data['themes'],THEME_COMPACT if compact else THEME_POS),1):
            title=THEME_LABELS[i-1];active=' aria-current="true"' if r['key']==theme else ''
            overlays+=f'<a href="{e(target(lens="work",theme=r["key"]),quote=True)}#{r["key"]}" class="world-theme-link" data-truth-class="hypothesis" data-theme="{r["key"]}" aria-label="Unqualified hypothesis {i}: {e(r["title"],quote=True)}"{active}><title>{e(r["title"])} · unqualified research hypothesis</title><ellipse cx="{x}" cy="{y}" rx="67" ry="27" class="world-theme-glow" filter="url(#{prefix}-mist)"/><path d="M{x-48} {y+3}Q{x} {y-24} {x+53} {y-7}" fill="none" stroke="#bb964d" stroke-width="2" stroke-dasharray="3 4"/><circle class="world-spark" cx="{x}" cy="{y}" r="15"/><circle class="world-target" cx="{x}" cy="{y}" r="34"/><text x="{x}" y="{y+5}" text-anchor="middle" class="world-theme-number">{i:02}</text>{multiline(title,x,y+39,27,"",19)}</a>'
    if lens=='uses':
        r=programme(data,relationship);cx,cy=(275,390) if compact else (300,345) if relationship else (370,345);px,py=(570,575) if compact else (620,490) if relationship else (755,450)
        href=e(target(lens='uses',relationship=r['key'])+'#programme',quote=True)
        overlays+=f'<g class="world-programme" data-truth-class="attributed_report"><path d="M{cx} {cy}C{cx+30} {cy-100} {px-130} {py-100} {px} {py}" stroke="#edf2e7" stroke-width="24" fill="none"/><path d="M{cx} {cy}C{cx+30} {cy-100} {px-130} {py-100} {px} {py}" class="world-programme-flow"/><a href="{href}" aria-label="Inspect programme: {e(r["customer"],quote=True)}" data-programme="{r["key"]}"><title>{e(r["customer"]+": "+r["offering"])}</title><ellipse cx="{cx}" cy="{cy}" rx="96" ry="60" fill="#f1f3e4" stroke="#6e9a8f" stroke-width="2"/><path d="M{cx-31} {cy+9}v-33l31-21 31 21v33M{cx-39} {cy+9}h78m-61-26v26m22-26v26m22-26v26" stroke="#7e9b90" stroke-width="2" fill="none"/>{multiline(r["customer"],cx,cy+92,26,"world-programme-label",24)}<ellipse cx="{px}" cy="{py}" rx="120" ry="68" fill="#e3eee6" stroke="#6e9a8f" stroke-width="2"/>'+''.join(f'<circle cx="{px+x}" cy="{py+y}" r="{s}" fill="{col}" stroke="#71998e"/>' for x,y,s,col in [(-38,-7,18,'#a4c6b9'),(20,-25,24,'#bdd5c0'),(45,25,15,'#d1dbc1'),(-16,32,21,'#d3e4d6')])+f'{multiline(short_text(r["participants"],100),px,py+102,32,"world-programme-label",23)}<circle cx="{cx+125}" cy="{cy-16}" r="5" fill="#44818a"/>{multiline("Product / capability / exact programme",(cx+px)/2,min(cy,py)-155,40,"world-programme-note",18)}{multiline(short_text(r["offering"],130),(cx+px)/2,min(cy,py)-130,39,"world-programme-label",22)}</a></g>'
    if provider:
        r=next(r for r in data['providers'] if r['key']==provider);x,y=positions[selected or r['memberships'][0]]
        overlays+=f'<g><ellipse cx="{x}" cy="{y+45}" rx="90" ry="19" class="world-focus-provider"/>{multiline(r["label"],x,y+51,30,"world-focus-provider-text",20)}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" class="world-svg {"world-compact" if compact else "world-wide"}" role="group" aria-labelledby="{prefix}-title {prefix}-desc" data-scene-contract="{CONTRACT}" data-scene-mode="{lens}"><title id="{prefix}-title">UK Technology — {lens} visual world</title><desc id="{prefix}-desc">Eight navigable illustrated districts. Landscape flows explain conceptual dependencies, never actual deployments. Blue programme ribbons show one attributed research record. Amber seams show unqualified hypotheses. Every link also works without JavaScript.</desc>{definitions}{ground}{paths}{regions}{overlays}</svg>'
