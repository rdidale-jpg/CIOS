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
      if (panel) select('#' + panel.id);
    };
    for (const link of links) link.addEventListener('click', () => select(link.hash));
    select(links[0].hash);
    sync();
    window.addEventListener('hashchange', sync);
  }

  const sources = flagship.querySelector('#llf-sources');
  const packets = [...sources.querySelectorAll(':scope > section')];
  const showSource = () => {
    if (!packets.some(packet => '#' + packet.id === location.hash)) return;
    sources.open = true;
    for (const packet of packets) packet.hidden = '#' + packet.id !== location.hash;
    packets.find(packet => !packet.hidden).focus();
  };
  sources.querySelector('summary').addEventListener('click', () => {
    if (!sources.open) for (const packet of packets) packet.hidden = false;
  });
  for (const link of flagship.querySelectorAll('[data-llf-source]')) {
    link.addEventListener('click', () => {
      sources.open = true;
      for (const packet of packets) packet.hidden = '#' + packet.id !== link.hash;
    });
  }
  window.addEventListener('hashchange', showSource);
  showSource();
}
})();
