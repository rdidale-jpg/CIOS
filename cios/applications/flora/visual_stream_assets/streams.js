// Focus and missing-art feedback only. All navigation is native, server-first.
const insight = document.getElementById('insight');
if (insight) insight.focus({preventScroll: false});
const agendaInsight = document.getElementById('agenda-insight');
if (agendaInsight) agendaInsight.focus({preventScroll: false});
for (const img of document.querySelectorAll('.world img, .portrait img')) {
  const failed = () => document.body.classList.add('art-missing');
  img.addEventListener('error', failed);
  if (img.complete && !img.naturalWidth) failed();
}
// Escape handling uses the existing design-system close-insight/menu owner.

// Native stream/subject URLs own history. Focus restoration never reads records.
if (location.hash.startsWith('#stream-')) document.getElementById(location.hash.slice(1))?.focus({preventScroll:true});
