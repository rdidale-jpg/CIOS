// Optional URL-only enhancement; native selected-bank panel links work without JS.
document.querySelectorAll('a[data-lens]').forEach(a=>a.addEventListener('click',()=>{
 if(/^#bank-/.test(location.hash))a.hash=location.hash;
}));
