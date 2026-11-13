// Progressive keyboard convenience only. Every route/control works without JS.
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const opened = document.querySelector('header details[open]');
  if (opened) {
    opened.open = false;
    opened.querySelector('summary').focus();
  } else {
    const close = document.querySelector('.close-insight');
    if (close) close.click();
  }
});
if (location.hash === '#insight') document.getElementById('insight')?.focus({preventScroll: true});
document.querySelectorAll('header nav>details').forEach(item => item.addEventListener('toggle', () => {
  if (item.open) document.querySelectorAll('header nav>details').forEach(other => {
    if (other !== item) other.open = false;
  });
}));
