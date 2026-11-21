from pathlib import Path
import re, subprocess
D=Path(__file__).resolve().parents[2]
for p in D.glob('*.html'):
 m=re.fullmatch(r'(uk|banking|lloyds)-(landscape|forces|inside)(-(suppliers|regulators))?\.html',p.name)
 if not m:continue
 scope,stream,suffix,_=m.groups();suffix=suffix or '';html=subprocess.check_output(['git','show','9384071c246ff83acbe134a0864f2ab0520e9b1d:'+str(p.relative_to(Path.cwd()))],text=True)
 # One identity; no default breadcrumb or repeated Home/Explore destinations.
 html=re.sub(r'<nav class="breadcrumb".*?</nav>','',html,flags=re.S)
 header=re.search(r'<header>.*?</header>',html,re.S).group(0)
 source=re.search(r'<div class="menu source-menu">(.*)</div></details></nav></header>',header,re.S).group(1)
 newheader='<header class="global-header"><a class="wordmark" href="uk-landscape.html">FLORA</a><nav aria-label="Global tools"><a href="uk-landscape.html">Explore</a></nav></header>'
 html=html.replace(header,newheader)
 layer=re.search(r'<details class="layers">.*?</details>',html,re.S)
 if layer:
  layer=layer.group(0);html=html.replace(layer,'');layer=layer.replace('class="layers"','class="layer-options"').replace('<summary>Layers</summary>','<summary>Context layers</summary>')
 streams=['inside','landscape','forces']if scope=='lloyds'else ['landscape','forces']
 nav='<nav class="stream-switcher" aria-label="Insight streams">'+''.join(f'<a data-lens="true" data-scope="{scope}" href="{scope}-{s}{suffix}.html"'+(' aria-current="page"'if s==stream else '')+'>'+s.title()+'</a>'for s in streams)+'</nav>'
 html=re.sub(r'<nav class="lens".*?</nav>',nav,html,count=1,flags=re.S)
 proof='<details class="proof"><summary>Sources</summary>'+source+'</details>'
 html=html.replace('</main>',(layer or '')+proof+'</main>')
 html=re.sub(r'<title>.*?</title>',f"<title>{ {'uk':'UK Economy','banking':'UK Banking','lloyds':'Lloyds Banking Group'}[scope]} · {stream.title()} · FLORA design preview</title>",html)
 html=html.replace('Skip to landscape','Skip to main content')
 p.write_text(html)
