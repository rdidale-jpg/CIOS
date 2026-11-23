(() => {
// The flagship already renders eligible public evidence on the server.
const flagship = document.querySelector('.llf');
if (flagship) {
  for (const group of flagship.querySelectorAll('[data-llf-choices]')) {
    const links = [...group.querySelector(':scope > nav').querySelectorAll('[data-llf-choice]')];
    const panels = [...group.querySelectorAll(':scope > [data-llf-panel]')];
    const select = (hash) => {
      for (const link of links) {
        if (link.hash === hash) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      }
      for (const panel of panels) panel.hidden = '#' + panel.id !== hash;
    };
    const sync = () => {
      const target = document.getElementById(location.hash.slice(1));
      const panel = panels.find(panel => target && panel.contains(target));
      select(panel ? '#' + panel.id : links[0].hash);
    };
    for (const link of links) link.addEventListener('click', () => select(link.hash));
    select(links[0].hash);
    sync();
    window.addEventListener('hashchange', sync);
  }

}
})();
