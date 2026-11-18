/* Progressive enhancement only: ordinary GET links work without JavaScript.
   No intelligence, credentials, private cache or record mutation in the browser. */
(() => {
  const route = '/enterprises/easyjet/preview';
  if (matchMedia('(max-width:700px)').matches) document.querySelector('.scene-control').open = false;
  let pending;
  async function navigate(href, push, focus = true, closeScene = false) {
    if (pending) pending.abort();
    const controller = new AbortController(); pending = controller;
    try {
      const response = await fetch(href, {signal: controller.signal, cache: 'no-store'});
      if (!response.ok) throw new Error('Unavailable');
      const next = new DOMParser().parseFromString(await response.text(), 'text/html');
      const main = next.querySelector('#preview-main');
      if (!main || !next.body.classList.contains('et-preview')) throw new Error('Unavailable');
      if (controller.signal.aborted) return;
      document.querySelector('#preview-main').replaceChildren(...main.childNodes);
      for (const selector of ['.stream-switcher', '.airline-scene nav']) {
        const incoming = next.querySelectorAll(selector + ' a');
        document.querySelectorAll(selector + ' a').forEach((node, i) => {
          node.href = incoming[i].getAttribute('href');
          if (incoming[i].hasAttribute('aria-current')) node.setAttribute('aria-current', incoming[i].getAttribute('aria-current'));
          else node.removeAttribute('aria-current');
        });
      }
      document.body.dataset.stream = next.body.dataset.stream;
      document.body.dataset.capability = next.body.dataset.capability;
      document.title = next.title;
      if (push) history.pushState(null, '', href);
      document.querySelector('#preview-status').textContent = `${document.querySelector('h1').textContent} · ${document.querySelector('.stream-switcher [aria-current]').textContent}`;
      if (closeScene && matchMedia('(max-width:700px)').matches) document.querySelector('.scene-control').open = false;
      if (focus) {
        const heading = document.querySelector('h1');
        heading.focus({preventScroll: true});
        heading.scrollIntoView({block: 'nearest'});
      }
    } catch (error) {
      if (error.name !== 'AbortError') location.assign(href);
    }
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-preview-nav]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.origin !== location.origin || url.pathname !== route) return;
    event.preventDefault(); navigate(url.pathname + url.search, true, true, link.classList.contains('capability'));
  });
  window.addEventListener('popstate', () => { if (location.pathname === route) navigate(location.pathname + location.search, false); });
})();
