(() => {
 addEventListener('pageshow',event=>{if(event.persisted)location.reload();});
 const button=document.querySelector('.le-compact');
 const scene=document.getElementById('enterprise-scene');
 const compact=matchMedia('(max-width:999px)');
 document.body.classList.add('le-enhanced');
 const set=open=>{scene.hidden=!open;button.setAttribute('aria-expanded',String(open));button.querySelector('span').textContent=open?'−':'+';};
 // Wide always retains the operating system; compact opens on explicit request.
 const restore=()=>set(!compact.matches);
 restore(); compact.addEventListener('change',restore);
 button.addEventListener('click',()=>set(button.getAttribute('aria-expanded')!=='true'));
 scene.addEventListener('click',event=>{if(compact.matches&&event.target.closest('a'))set(false);});
})();
