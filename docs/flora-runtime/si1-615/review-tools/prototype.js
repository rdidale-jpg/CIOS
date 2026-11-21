/* Read-only prototype navigation. No fetch, storage, matcher or domain writes. */
(() => {
 const single = document.body.classList.contains('standalone');
 const paneOf = () => single ? document.querySelector('.prototype-pane:not([hidden])') : document;
 function reveal() {
  const hash=decodeURIComponent(location.hash.slice(1));
  if(single){
   const view=(hash.split('--')[0].split('?')[0]||'uk-landscape');
   const pane=document.querySelector('[data-view="'+CSS.escape(view)+'"]')||document.querySelector('[data-view="uk-landscape"]');
   document.querySelectorAll('.prototype-pane').forEach(p=>p.hidden=p!==pane);
   pane.querySelectorAll('[data-art-key]').forEach(img=>{if(!img.src)img.src=embeddedArtwork[img.dataset.artKey];});
   document.title=pane.querySelector('h1').textContent+' · '+pane.querySelector('main').dataset.stream+' · FLORA design';
  }
  const [rawView,anchor]=hash.split('--');
  const viewName=rawView.split('?')[0];
  const params=new URLSearchParams(single ? (rawView.split('?')[1]||'') : location.search);
  const active=paneOf(),main=active.querySelector('main');
  if(main){
   main.dataset.layer=params.get('layer')||'enterprises';
   active.querySelectorAll('.layer-options a').forEach(a=>{const layer=(a.getAttribute('href').match(/layer=([^&#]+)/)||[])[1]||'enterprises';if(layer===main.dataset.layer)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
   active.querySelectorAll('.spot').forEach(a=>{const id=a.dataset.labelId; a.classList.toggle('layer-focus',(main.dataset.layer==='regulators'&&['boe','pra','fca','payments','economics'].includes(id))||(main.dataset.layer==='suppliers'&&['technology','customers','operations','payments'].includes(id)));a.classList.toggle('selected',id===params.get('selected'));});
  }
  const target=document.getElementById(single ? viewName+(anchor?'--'+anchor:'') : hash);
  if(target){
   let el=target;
   while(el){if(el.tagName==='DETAILS')el.open=true;el=el.parentElement;}
   if(target.classList.contains('focus'))target.style.display='block';
   requestAnimationFrame(()=>{target.scrollIntoView({block:'start'});if(target.hasAttribute('tabindex'))target.focus({preventScroll:true});});
  }else if(single){window.scrollTo(0,0);}
  paneOf().querySelectorAll('.focus').forEach(el=>{if(el!==target)el.style.display='';});
  paneOf().querySelectorAll('img').forEach(img=>img.addEventListener('error',()=>document.body.classList.add('art-missing'),{once:true}));
 }
 document.addEventListener('click',event=>{
  const a=event.target.closest('a');if(!a||!single)return;
  const href=a.getAttribute('href');if(!href?.startsWith('#'))return;
  const current=location.hash.slice(1).split('--')[0],next=href.slice(1).split('--')[0];
  const [from,fromQuery]=current.split('?'),[to,toQuery]=next.split('?');
  if(from.split('-')[0]!==to.split('-')[0])return;
  const params=new URLSearchParams(fromQuery||'');new URLSearchParams(toQuery||'').forEach((v,k)=>params.set(k,v));
  const tail=href.slice(1).split('--')[1];
  const query=params.toString();const updated='#'+to+(query?'?'+query:'')+(tail?'--'+tail:'');
  if(updated!==href){event.preventDefault();location.hash=updated;}
 });
 document.addEventListener('keydown',event=>{
  if(event.key!=='Escape')return;
  const pane=paneOf(),menu=pane.querySelector('.product-menu[open]');
  if(menu){menu.open=false;menu.querySelector('summary').focus();return;}
  const focused=document.activeElement.closest?.('details');
  if(focused&&focused.open){focused.open=false;focused.querySelector('summary').focus();return;}
  const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));
  const close=target?.querySelector('.close-insight');if(close)close.click();
 });
 window.addEventListener('hashchange',reveal);reveal();
})();
