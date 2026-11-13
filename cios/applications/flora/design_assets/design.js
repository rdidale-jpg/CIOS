// Progressive disclosure/focus only; no fetch, business state or Pipeline writes.
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const opened = document.querySelector('.product-header nav>details[open]');
  if (opened) { opened.open=false; opened.querySelector('summary').focus(); }
  else document.querySelector('.close-insight,.ds-model-close')?.click();
});
function revealTarget() {
  if (!location.hash) return;
  let id;try {id=decodeURIComponent(location.hash.slice(1));}catch {return;}
  const el=document.getElementById(id);if(!el)return;
  for(let parent=el.parentElement;parent;parent=parent.parentElement)
    if(parent.tagName==='DETAILS')parent.open=true;
  if (el.matches('.image-insight,.ds-model-insight')) el.focus({preventScroll:true});
}
revealTarget();document.addEventListener('DOMContentLoaded',revealTarget);window.addEventListener('hashchange',revealTarget);
