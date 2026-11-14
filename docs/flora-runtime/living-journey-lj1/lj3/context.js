// URL-only selection enhancement; no storage, network, authority or model state.
document.querySelectorAll('a[data-lens]').forEach(a=>a.addEventListener('click',()=>{
 if(/^#bank-/.test(location.hash)||location.hash==='#selected-lloyds')a.hash=location.hash;
}));
