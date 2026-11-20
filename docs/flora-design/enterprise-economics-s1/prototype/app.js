'use strict';
// Local design document only. No runtime imports, fetches, private identifiers,
// storage, authentication, source decisions or mutation endpoints.
const BANK = {
  name:'Lloyds Banking Group', industry:'Banking', identity:'Lloyds Banking Group plc',
  period:'Banking economics · conceptual view',
  capability:'Risk assessment',
  nodes:[
    ['funding','01 / Funding','Customer funding','Deposits and other funding'],
    ['lending','02 / Earning','Lending & services','Assets, interest and fees'],
    ['earnings','03 / Retaining','Earnings','After costs and credit losses']],
  details:{
    funding:['Funding is not income.','Customer deposits are liabilities. A bank uses funding to support lending and other assets.','The price and stability of funding can affect the economics of earning assets. Actual sensitivity needs matched asset and liability evidence.'],
    lending:['Earning assets create income.','Interest and fees are distinct income sources. Funding costs reduce the return from interest-earning assets.','Different repricing timings can change the spread. A banking margin does not describe the profit of the whole Group.'],
    earnings:['Income is only part of the story.','Operating costs and credit losses reduce earnings. Capital supports risk-taking and absorbs losses.','Higher income need not produce higher profit. The size and timing of costs and losses matter; this diagram assigns no amount to Lloyds.']},
  activities:[['Assess','Credit origination','Affordability, information and risk decisions'],['Deliver','Service credit','Account servicing and customer support'],['Retain','Manage losses','Credit outcomes and operational controls']],
  force:['Rates & repricing','Funding costs and asset yields can adjust at different times.','The earnings effect depends on the actual mix, timing and scale of repricing.'],
  roles:[['Finance','Funding, income and capital economics'],['Operations','Delivery, servicing and running costs'],['Risk','Credit outcomes and resilience']],
};
const AIR = {
  name:'easyJet',industry:'Aviation',identity:'easyJet plc · consolidated Group',
  period:'Year ended 30 September 2025 · Group · GBP',capability:'Network Planning',
  nodes:[['income','01 / Earning','Flights & holidays','Group revenue'],['capacity','02 / Delivering','Capacity & service','Aircraft time and operations'],['earnings','03 / Retaining','Headline profit','Before tax · APM']],
  details:{
    income:['Revenue describes the scale of activity.','Group revenue describes the scale of the business. Profit is a separate financial outcome.','Revenue growth describes the top line. It does not identify which route, capability or cost driver created the earnings.'],
    capacity:['Capacity is not an earnings measure.','The operating diagram is conceptual. Aircraft availability, scheduling and delivery are different activities; no capability cost allocation is supplied.','More scheduled capacity creates value only if demand, pricing and delivery economics support it. No route profitability or realised improvement is inferred.'],
    earnings:['Headline profit is a distinct measure.','Headline pretax profit is the issuer’s alternative performance measure. It is distinct from statutory profit and cash generation.','Revenue scale and retained earnings answer different questions. These two Group figures do not establish a cost bridge, operating margin or seller opportunity.']},
  activities:[['Plan','Shape the network','Demand, schedule and aircraft-time decisions'],['Deliver','Operate the flight','Fleet readiness, crew and operational recovery'],['Retain','Earn a return','Pricing, delivery costs and financial outcomes']],
  force:['Cost & delivery conditions','The FY2025 report describes cost inflation and supply constraints.','The effect on a particular capability or future year is not quantified by the Group revenue and profit figures.'],
  roles:[['Finance','Reported performance and financial definitions'],['Network & operations','Capacity, scheduling and delivery choices'],['Commercial','Demand, pricing and customer proposition']],
};
const REVENUE_25=10106, REVENUE_24=9309, HEADLINE_PBT_25=665;
const GROWTH=((REVENUE_25-REVENUE_24)/REVENUE_24*100).toFixed(2);
const OPTIONS={a:['A / Landscape component','The economic story'],b:['B / Operating model','Economics in the work'],c:['C / Contextual lens','The economic overlay']};
let state;
let firstRender=true;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function read(){
 const p=new URLSearchParams(location.search);
 const allowed=['option','enterprise','mode','view','subject','lens'];
 if([...p.keys()].some(k=>!allowed.includes(k)||p.getAll(k).length!==1))throw Error('Unsupported design selection');
 const s={option:p.get('option')||'a',enterprise:p.get('enterprise')||'lloyds',mode:p.get('mode')||'facts',view:p.get('view')||'economics',subject:p.get('subject')||'',lens:p.get('lens')||'on'};
 if(!OPTIONS[s.option]||!['lloyds','easyjet'].includes(s.enterprise)||!['facts','insight'].includes(s.mode)||!['economics','operating','landscape','forces','leadership'].includes(s.view)||!['on','off'].includes(s.lens))throw Error('Unsupported design selection');
 const d=s.enterprise==='lloyds'?BANK:AIR;
 if(!s.subject)s.subject=d.nodes[s.option==='b'?1:0][0];
 if(!d.nodes.some(n=>n[0]===s.subject))throw Error('Unsupported design subject');
 return s;
}
function href(changes={}){const s={...state,...changes};return 'view.html?'+new URLSearchParams(s).toString();}
function link(text,changes,cls='',active=false){return `<a data-nav href="${href(changes)}" class="${cls}"${active?' aria-current="page"':''}>${text}</a>`;}
function scene(d){
 const art=state.enterprise==='easyjet'?'easyjet':state.view==='forces'?'lloyds-forces':(state.option==='b'||state.view==='operating')?'lloyds-inside':'lloyds-landscape';
 const inside=state.option==='b'||state.view==='operating';
 const fig=`<figure class="scene"><img src="assets/${art}.webp" alt="Conceptual ${state.enterprise==='easyjet'?'airport operating scene':'Lloyds architectural scene'}; not actual premises or financial allocations"><a data-nav class="scene-label ${state.view==='economics'?'active':''}" style="top:43%" href="${href({view:'economics'})}">${inside?'Economic context':'Economics'}</a><a data-nav class="scene-label ${state.view==='operating'?'active':''}" style="top:69%" href="${href({view:'operating'})}">${state.enterprise==='easyjet'?'Network Planning':'Credit operations'}</a></figure>`;
 const nav='';
 return `<div class="wide-art">${fig}${nav}</div><details class="compact-art"><summary>Explore the enterprise</summary>${fig}${nav}</details>`;
}
function topHeader(d){
 const active=state.view==='forces'?'Forces':state.view==='operating'||(state.option==='b'&&state.view==='economics')?'Inside':'Landscape';
 return `<a class="skip" href="#main">Skip to intelligence</a><div class="global"><div><a class="brand" href="index.html">FLORA</a><span class="design-label">LOCAL DESIGN PROTOTYPE</span></div><nav class="product-tools" aria-label="Existing product context"><a href="index.html">Explore</a><span title="Outside this design prototype">Offers</span><span title="Outside this design prototype">Pipeline</span></nav></div><div class="scopebar"><div class="trail"><span>UK</span><span>/ ${d.industry}</span><strong>/ ${d.name}</strong></div><nav class="perspectives" aria-label="Enterprise perspective">${link('Landscape',{view:state.option==='a'?'economics':'landscape'},'',active==='Landscape')}${link('Inside',{view:'operating'},'',active==='Inside')}${link('Forces',{view:'forces'},'',active==='Forces')}</nav></div>`;
}
function reading(){return `<div class="reading"><nav aria-label="Reading mode">${link('Facts',{mode:'facts'},'',state.mode==='facts')}${link('FLORA Insight',{mode:'insight'},'',state.mode==='insight')}</nav><span class="option-caption">${OPTIONS[state.option][0]}</span></div>`;}
function heading(d,title,copy,tag=''){return `<p class="eyebrow">${d.identity}</p><p class="period">${d.period}</p>${tag?`<p class="tag">${tag}</p>`:''}<h1>${title}</h1><p class="intro">${copy}</p>`;}
function flow(d){return `<figure class="diagram" aria-label="Illustrative economic mechanism"><div class="flow">${d.nodes.map((n,i)=>`${i?'<span class="arrow" aria-hidden="true">→</span>':''}${link(`<small>${n[1]}</small><strong>${n[2]}</strong><span>${n[3]}</span>`,{subject:n[0]},'flow-node '+(state.subject===n[0]?'active':''),state.subject===n[0])}`).join('')}</div><figcaption class="fine" style="margin-top:13px">Illustrative, unweighted mechanism · not a financial reconciliation</figcaption></figure>`;}
function selected(d){const n=d.details[state.subject];return `<section class="selection-copy" id="selection">${state.mode==='insight'?'<p class="mode-label">FLORA Insight · conditional</p>':''}<h2>${n[0]}</h2><p>${n[state.mode==='facts'?1:2]}</p></section>`;}
function financials(compact=false){
 if(state.enterprise!=='easyjet')return '';
 if(compact)return `<div class="group-context"><div><strong>£10.106bn</strong><span>Reported · FY2025 Group revenue</span></div><div><strong>£665m</strong><span>Reported · Group headline pretax profit</span></div></div><p class="fine">Group context · not allocated to this capability.</p>`;
 return `<div class="measure-pair"><div class="measure"><small>Reported · Group revenue</small><strong>£10.106bn</strong><span>FY2025 · £9.309bn in FY2024</span><em>Calculated +${GROWTH}% revenue growth</em></div><div class="measure"><small>Reported · headline pretax profit</small><strong>£665m</strong><span>FY2025 · alternative performance measure</span></div></div><div class="revenue-chart" role="img" aria-label="Revenue, common zero baseline in GBP billion: FY2024 9.309; FY2025 10.106. Calculated growth ${GROWTH} percent."><div class="bar-pair"><span>FY2024</span><div class="bar-track"><div class="bar-fill" style="width:${REVENUE_24/REVENUE_25*100}%;opacity:.45"></div></div><strong>£9.309bn</strong></div><div class="bar-pair"><span>FY2025</span><div class="bar-track"><div class="bar-fill" style="width:100%"></div></div><strong>£10.106bn</strong></div></div><p class="profit-context">Annual Group revenue · zero baseline. Headline pretax profit is a separate measure.</p>`;
}
function optionA(d){return heading(d,state.enterprise==='lloyds'?'From funding<br>to earnings.':'From seats<br>to earnings.',state.enterprise==='lloyds'?'Funding, income and the costs of earning a return.':'The scale of revenue. The return retained.',state.enterprise==='lloyds'?'Illustrative · not quantified Lloyds economics':'')+flow(d)+(state.enterprise==='easyjet'&&state.mode==='facts'&&state.subject==='income'?'':selected(d))+financials();}
function optionB(d){return heading(d,'Economics in<br>the work.',state.mode==='facts'?'Start with the operating activity. Keep its economic mechanism distinct from the Group financial context.':'Operating choices can influence economics. They are not measured capability returns or evidence of buying demand.','Illustrative operating structure')+`<span class="capability">Focus · ${d.capability}</span><div class="operating-spine">${d.activities.map((r,i)=>`<section class="activity"><span class="step">0${i+1}</span><h3>${r[0]}</h3><div><strong>${r[1]}</strong><p>${r[2]}</p></div></section>`).join('')}</div>`+`<p class="conditional">${state.enterprise==='easyjet'?'Network decisions affect which seats can be offered. Their value depends on demand, pricing and delivery costs.':'Credit decisions can influence income, service effort and losses. This is a mechanism, not an observed Lloyds outcome.'}</p>`+financials(true)+`<p class="fine">Illustrative operating view · no organisation or supplier relationship is inferred.</p>`;}
function optionC(d){
 const air=state.enterprise==='easyjet',on=state.lens==='on',nodes=air?['Customers','Flight capacity','Delivery','Earnings']:['Customers','Earning assets','Funding','Earnings'];
 const notes=air?['Flight & holiday demand','Aircraft time and schedule','Unallocated delivery costs','£665m headline PBT · FY2025']:['Access and service','Interest and fee mechanisms','Price and stability','After costs and losses'];
 return heading(d,'See the economic<br>connections.',state.mode==='facts'?'Keep the business context in view. Add economic drivers to the same illustration.':'The overlay explains possible mechanisms. It does not establish the magnitude, causality or commercial significance of an exposure.','Illustrative relationship layout')+`<div class="lens-toolbar"><p class="eyebrow" style="margin:0">${on?'Economic drivers':'Business context'}</p><a data-nav class="lens-toggle" role="button" href="${href({lens:on?'off':'on'})}" aria-pressed="${on}">${on?'Hide economic drivers':'Show economic drivers'}</a></div><div class="lens-canvas" data-overlay="${state.lens}" aria-label="Conceptual ecosystem with optional economic annotations"><div class="orbit" aria-hidden="true"></div><div class="orbit second" aria-hidden="true"></div><div class="hub">${d.name}<small>${air?'FLIGHTS & HOLIDAYS':'BANKING CONTEXT'}</small></div>${nodes.map((n,i)=>`${link(n,{subject:d.nodes[i===0?0:i===3?2:1][0]},'orbit-node n'+(i+1))}<span class="lens-note l${i+1}">${esc(notes[i])}</span>`).join('')}</div><p class="fine">Illustrative placement and unweighted connections; not an ownership, cash-flow or supplier map.</p>`+selected(d)+(air?financials(true):'');
}
function pressure(d){return heading(d,'Conditions that<br>shape the return.',state.mode==='facts'?d.force[1]:d.force[2],state.enterprise==='lloyds'?'Illustrative mechanism':'Reported historical context / conceptual transmission')+`<div class="force-path"><div><small>Context</small><strong>${d.force[0]}</strong></div><div><small>Illustrative transmission</small><strong>${state.enterprise==='easyjet'?'Delivery economics and available capacity':'Funding and asset repricing'}</strong></div><div><small>Conditional consequence</small><strong>${state.enterprise==='easyjet'?'The retained return can change':'The spread can widen or narrow'}</strong></div></div><p class="conditional">This is a possible economic effect. It does not establish customer demand or a buying programme.</p>`;}
function leadership(d){return heading(d,'Decisions behind<br>the economics.','Economic outcomes connect financial and operating decisions.','Illustrative functional perspectives')+`<div class="role-grid">${d.roles.map(r=>`<section><h2>${r[0]}</h2><p>${r[1]}</p></section>`).join('')}</div><p class="conditional">Functional perspectives, not verified decision rights.</p>`+financials(true);}
function overview(d){return heading(d,'The business<br>in context.','Explore economic outcomes alongside the operating model, without changing the enterprise or reading mode.','Illustrative executive overview')+flow(d)+`<p>${link('Explore the economics →',{view:'economics'},'lens-toggle')}</p>`;}
function evidence(d){
 const body=state.enterprise==='lloyds'?`<p>The banking relationships are an explicitly illustrative reading of the existing Landscape mechanism, not quantified Lloyds assertions.</p><dl><dt>Source of conceptual structure</dt><dd>Existing FLORA Landscape components: Funding, Lending &amp; income, Profit &amp; costs.</dd><dt>Financial claims</dt><dd>No bank-specific financial values are included in this study.</dd><dt>Uncertainty</dt><dd>Links are unweighted. No actual funding mix, allocation, earnings sensitivity or buyer need is established.</dd></dl><p><a href="https://www.lloydsbankinggroup.com/" target="_blank" rel="noreferrer">Lloyds Banking Group homepage</a></p>`:`<dl><dt>Original issuer document</dt><dd>easyJet Annual Report and Accounts 2025, performance summary, printed page 32. Rechecked 19 November 2026.</dd><dt>Reported facts</dt><dd>Group revenue: FY2025 £10,106m; FY2024 £9,309m. FY2025 headline profit before tax: £665m.</dd><dt>Period and perimeter</dt><dd>FY2025: 1 October 2024–30 September 2025. FY2024: 1 October 2023–30 September 2024. Consolidated Group, GBP millions.</dd><dt>Calculation</dt><dd>(10,106 − 9,309) ÷ 9,309 × 100 = ${GROWTH}% revenue growth, rounded to two decimal places. No FX or perimeter adjustment.</dd><dt>Basis and limitations</dt><dd>Revenue is a reported Group measure. Headline pretax profit is an APM, not statutory profit. These are historical periods, not current trading or capability economics. Publication day is not established in the retained Source record.</dd><dt>Authority</dt><dd>Design-only factual illustration, not a canonical update, new source grant or Financial run. Existing Source eligibility and lifecycle remain authoritative for a later runtime.</dd></dl><p><a href="https://s203.q4cdn.com/522538739/files/doc_financials/2025/ar/easyJetARA25_DIGITAL_sm.pdf" target="_blank" rel="noreferrer">Original easyJet annual report</a></p>`;
 return `<dialog id="basis" aria-labelledby="basis-title"><button class="close-dialog" type="button" aria-label="Close source inspection">×</button><p class="eyebrow">Optional inspection</p><h2 id="basis-title">Source &amp; basis</h2>${body}</dialog>`;
}
function render(){
 try{state=read();if(firstRender){history.replaceState(null,'',href());firstRender=false;}}catch(e){document.getElementById('main').innerHTML='<h1>Design selection unavailable</h1><a href="index.html">Return to the design comparison</a>';return;}
 const d=state.enterprise==='lloyds'?BANK:AIR;
 document.body.classList.toggle('aviation',state.enterprise==='easyjet');
 document.title=`FLORA · ${d.name} · Option ${state.option.toUpperCase()} · ${state.mode}`;
 document.getElementById('top').innerHTML=topHeader(d);document.getElementById('left').innerHTML=scene(d);
 const content=state.view==='forces'?pressure(d):state.view==='leadership'?leadership(d):state.view==='landscape'?overview(d):state.view==='operating'?optionB(d):({a:optionA,b:optionB,c:optionC}[state.option])(d);
 document.getElementById('main').innerHTML=reading()+content+`<div class="bottom-line"><button class="basis-button" type="button" id="inspect">Source &amp; basis</button><nav class="related" aria-label="Related intelligence">${link('Related forces →',{view:'forces'})}${link('Leadership context →',{view:'leadership'})}${state.view!=='economics'?link('Back to economics →',{view:'economics'}):''}</nav></div>`+evidence(d);
 const dialog=document.getElementById('basis'),button=document.getElementById('inspect');button.onclick=()=>dialog.showModal();dialog.querySelector('button').onclick=()=>dialog.close();dialog.addEventListener('close',()=>button.focus());
}
document.addEventListener('click',event=>{
 const a=event.target.closest('a[data-nav]');if(!a||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 event.preventDefault();const wasCompact=document.querySelector('.compact-art')?.open;history.pushState(null,'',a.href);render();if(wasCompact)document.querySelector('.compact-art').open=true;document.getElementById('main').focus();
});
document.addEventListener('keydown',event=>{if(event.key===' '&&event.target.matches('a[role=button]')){event.preventDefault();event.target.click();}});
window.addEventListener('popstate',()=>{render();document.getElementById('main').focus();});render();
