// Fixed-scope prototype navigation only; no storage, network, or permission logic.
const validBankSelections = new Set([
  '#bank-barclays', '#bank-hsbc-uk', '#bank-natwest',
  '#bank-santander-uk', '#selected-lloyds'
]);
function retainBankSelection() {
  document.querySelectorAll('.stream-switcher a[data-scope="banking"], main[data-scope="banking"] .layer-options a').forEach(a => {
    a.hash = validBankSelections.has(location.hash) ? location.hash : '';
  });
}
retainBankSelection();
addEventListener('hashchange', retainBankSelection);
