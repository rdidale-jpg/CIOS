// Focus and missing-art feedback only. All navigation is native, server-first.
const insight = document.getElementById('insight');
if (insight) insight.focus({preventScroll: false});
for (const img of document.querySelectorAll('.world img')) {
  const failed = () => document.body.classList.add('art-missing');
  img.addEventListener('error', failed);
  if (img.complete && !img.naturalWidth) failed();
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !document.querySelector('.product-menu[open]'))
    document.querySelector('#insight .close')?.click();
});
