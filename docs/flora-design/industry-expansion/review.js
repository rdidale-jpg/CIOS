const repo = 'https://github.com/rdidale-jpg/CIOS/blob/03719d7573f087c65d9622719273aa4b89caf7d3/';
const tel = 'docs/operations/flora/';
const tech = 'docs/flora-runtime/technology-visual-foundation/Foundation.json';
const utilities = 'docs/CBOK/Playbooks/SECTOR_PLAYBOOK_UTILITIES.md';
const energy = 'docs/CBOK/Playbooks/SECTOR_PLAYBOOK_ENERGY.md';

const concepts = {
  telecom: {
    title: 'UK Telecommunications', headline: 'From signal to service', label: 'FIXED + MOBILE',
    steps: ['Build the network', 'Provide access', 'Serve customers'],
    operating: ['Fibre and radio sites connect premises and devices.', 'Network owners can provide access to other service providers.', 'Retail and business teams package connectivity and support.'],
    economics: ['Build & maintain', 'Sell access', 'Bill for service'],
    economicsTitle: 'Two routes to revenue',
    economicsNote: 'Access can be sold wholesale. Retail providers can bill homes and businesses for service.',
    ecosystem: ['BT Group', 'Kyndryl', 'Dynatrace'],
    timeline: ['FY26 · Annual report', '23 Jul 2026 · Trading update', 'Next · Copper migration'],
    enterprises: ['BT Group', 'Openreach', 'CityFibre'],
    status: 'Candidate record · TEL-001',
    fact: 'The BT Group profile describes consumer broadband and mobile, business connectivity and Openreach fixed-access infrastructure.',
    insight: 'Ask which part of the group owns the decision. Network investment and retail service may sit with different teams.',
    relationship: 'TEL-001 records Kyndryl in mainframe-to-cloud context and Dynatrace in operations automation context.',
    changes: 'The TEL-001 trace identifies BT’s FY26 report and Q1 FY27 update and records copper migration as an execution challenge.',
    evidence: tel + 'TEL-001-BT-Factual-Synthesis-Runtime-Closure.md',
    relationshipEvidence: tel + 'rendered-tel001-relationship-acceptance/enterprise-ent-bt.html',
    scope: 'ENT-BT · FACT-ENT-BT-PROFILE / OPERATING-MODEL / STRATEGY · EV-BT-FY26 / EV-BT-Q1FY27. Supplier context cites EV-BT-KYNDRYL and EV-BT-DYNATRACE.',
    gap: 'Candidate scope. Current supplier terms, allocation of revenue and costs, and the migration end date require separate checks. The source retains UN-002, UN-004, UN-005 and UN-011 and CR-003/004.',
    enterpriseLinks: ['bt', 'openreach', 'cityfibre'].map(id => repo + tel + 'rendered-tel001-relationship-acceptance/enterprise-ent-' + id + '.html')
  },
  energy: {
    title: 'UK Energy & Utilities', headline: 'Power has to keep moving', label: 'ELECTRICITY VIEW',
    steps: ['Generate power', 'Move it across the grid', 'Deliver to customers'],
    operating: ['Generators supply electricity.', 'Transmission and distribution move electricity across networks.', 'Retail suppliers serve customers. The physical flow and the customer bill are different paths.'],
    economics: ['Invest in assets', 'Regulatory settlement', 'Run & renew networks'],
    economicsTitle: 'The regulated investment cycle',
    economicsNote: 'Network investment, allowances and delivery performance belong in one view. Generation and retail require different economics.',
    ecosystem: ['Grid operator', 'Equipment makers', 'Field contractors'],
    timeline: ['Set priorities', 'Deliver investment', 'Review performance'],
    enterprises: ['National Grid'],
    status: 'Draft sector guidance',
    fact: 'The Utilities playbook identifies affordability, resilience and capital investment cycles as sector pressures.',
    insight: 'Ask which obligation and investment cycle apply to the network business before discussing delivery priorities.',
    relationship: 'An illustrative grid operator coordinates the system. Equipment makers supply assets and field contractors can deliver works.',
    changes: 'This sequence illustrates a regulatory cycle. The playbook identifies regulatory determinations and service incidents as potential triggers.',
    evidence: utilities, relationshipEvidence: energy,
    scope: 'CIOS-CBOK-PLAYBOOK-SECTOR-UTILITIES-001 · v0.1.0 · draft · reviewed 29 June 2026. Electricity is the worked example.',
    gap: 'National Grid is a proposed research destination. Local entity identity, price control, allowance, dates and contract evidence were unavailable in the reviewed material.',
    enterpriseLinks: []
  },
  technology: {
    title: 'UK Technology', headline: 'One workflow, many providers', label: 'PLATFORMS + DELIVERY',
    steps: ['Provide capacity', 'Build tools', 'Integrate & run'],
    operating: ['Cloud and infrastructure providers supply computing capacity.', 'Software providers offer products and platforms.', 'Delivery teams integrate tools and run services. One provider can occupy multiple roles.'],
    economics: ['Usage', 'Subscriptions', 'Delivery & support'],
    economicsTitle: 'Three ways to charge',
    economicsNote: 'Consumption, subscriptions and service fees can coexist. Each offering has its own basis.',
    ecosystem: ['BT Group', 'ServiceNow', 'Delivery partner unknown'],
    timeline: ['Before announcement · Consolidation', '20 Jun 2024 · Rollout reported', 'At announcement · Pilot'],
    enterprises: ['ServiceNow', 'BT Group'],
    status: 'Attributed research · date-bound',
    fact: 'BT’s June 2024 disclosure describes wider ServiceNow rollout and an initial Now Assist pilot.',
    insight: 'Ask which capabilities were rolled out and which were being tested. The two stages call for different follow-up questions.',
    relationship: 'BT Group is the reporting customer and ServiceNow the named provider for service management, Service Bridge and the Now Assist pilot.',
    changes: 'The disclosure distinguishes prior Digital-unit consolidation, a wider rollout and an initial pilot.',
    evidence: tech, relationshipEvidence: tech,
    original: 'https://newsroom.bt.com/bt-group-expands-strategic-relationship-with-servicenow-to-improve-customer-and-employee-experiences/',
    scope: 'Foundation programme-67-1 · customer-authored report, published 20 June 2024 · retained research draft · canonical identity unbound.',
    gap: 'Current contract, deployment geography, group-wide scope, fees and implementation responsibilities remain unconfirmed.',
    enterpriseLinks: [repo + tech, repo + tel + 'rendered-tel001-relationship-acceptance/enterprise-ent-bt.html']
  }
};

const views = {landscape:'Landscape', economics:'Enterprise Economics', ecosystem:'Ecosystem', change:'Change over time'};
const byId = id => document.getElementById(id);
const evidence = byId('evidence');
const route = (id, view='landscape', mode='facts', item='') => '#' + [id,view,mode,item].filter(Boolean).join('/');
const link = (title, href, current=false) => `<a href="${href}"${current ? ' aria-current="page"' : ''}>${title}</a>`;
let inspect;
let focusEvidence;

function render() {
  if (evidence.open) evidence.close();
  const [requested, selected, reading, selection] = location.hash.slice(1).split('/');
  const id = Object.hasOwn(concepts, requested) ? requested : 'telecom';
  const enterprise = selected === 'enterprise';
  const view = enterprise || Object.hasOwn(views, selected) ? selected : 'landscape';
  const mode = reading === 'insight' ? reading : 'facts';
  const item = /^[0-2]$/.test(selection || '') ? Number(selection) : null;
  const c = concepts[id];
  const enterpriseIndex = enterprise && c.enterprises[item] ? item : 0;
  const path = (v, i) => route(id, v, mode, i === undefined ? '' : String(i));
  document.body.className = id;
  byId('scene').style.setProperty('--art', `url("${id}.webp")`);
  byId('industry').textContent = c.title;
  byId('headline').textContent = c.headline;
  byId('scene-label').textContent = c.label;
  document.querySelectorAll('.top nav a').forEach(a => {
    if (a.hash === '#' + id) a.setAttribute('aria-current','page');
    else a.removeAttribute('aria-current');
  });
  byId('sections').innerHTML = Object.entries(views).map(([key,title]) => link(title,path(key),view===key)).join('');
  byId('enterprises').innerHTML = c.enterprises.map((name,i) => link(name,path('enterprise',i),enterprise&&enterpriseIndex===i)).join('');
  byId('modes').innerHTML = ['facts','insight'].map(m => link(m==='facts'?'Facts':'Insight',route(id,view,m,item===null?'':String(item)),m===mode)).join('');
  byId('stations').innerHTML = c.steps.map((step,i) => link(step,path('landscape',i),view==='landscape'&&i===item)).join('');

  const panels = {
    landscape: [item===null?'How it works':c.steps[item], item===null?c.operating[0]+' '+c.operating[1]+' '+c.operating[2]:c.operating[item], []],
    economics: [c.economicsTitle, c.economicsNote, c.economics],
    ecosystem: ['Who works with whom', c.relationship, c.ecosystem],
    change: ['Change over time', c.changes, c.timeline],
    enterprise: [c.enterprises[enterpriseIndex], id==='energy'?'Research needed before opening a governed enterprise view.':'Open the existing research or candidate record to check scope and identity.', []]
  };
  const [heading, description, labels] = panels[view];
  const status = ['economics','landscape'].includes(view) || (id==='energy' && view==='ecosystem') ? 'Conceptual mechanism' : view==='change' && id==='energy' ? 'Illustrative sequence' : enterprise ? 'Enterprise context' : c.status;
  const enterpriseLink = enterprise && c.enterpriseLinks[enterpriseIndex];
  const note = mode==='insight' ? c.insight : c.fact;
  const mechanism = view==='economics' && id==='telecom'
    ? '<div class="split"><span>Network investment</span><div><span>Wholesale access</span><span>Retail bills</span></div></div>'
    : view==='economics' && id==='energy'
    ? '<div class="cycle"><span>Invest in assets</span><span>Run &amp; renew</span><span>Regulatory settlement</span><span>↻ Next cycle</span></div>'
    : labels.length ? '<div class="tokens '+view+'">'+labels.map(t=>`<span>${t}</span>`).join('')+'</div>' : '';
  byId('diagram').innerHTML = `<span class="type">${status}</span><h3>${heading}</h3>${mechanism}<p>${description}</p>${enterpriseLink?link('Open existing record ↗',enterpriseLink):''}`;
  byId('reading').innerHTML = `<span class="type">${mode==='facts'?c.status:'Insight · question to explore'}</span><h3>${mode==='facts'?'What the record says':'What to ask next'}</h3><p>${note}</p><button class="source" type="button">Evidence &amp; uncertainty ↗</button>`;
  inspect = () => {
    focusEvidence = document.activeElement;
    const reference = view==='ecosystem' ? c.relationshipEvidence : c.evidence;
    const selectedClaim = view==='ecosystem' || view==='change' ? description : c.fact;
    byId('e-body').innerHTML = `<span class="type">${c.status}</span><h2 id="e-title">Evidence &amp; uncertainty</h2><p>${selectedClaim}</p><p>${c.scope}</p><h3>What’s unresolved</h3><p>${c.gap}</p><p>${link('Inspect retained record ↗',repo+reference)}${c.original?' · '+link('Read original disclosure ↗',c.original):''}</p>`;
    evidence.showModal();
  };
  byId('reading').querySelector('button').addEventListener('click',inspect);
}

evidence.addEventListener('close', () => { if(focusEvidence?.isConnected) focusEvidence.focus(); });
const compact = window.matchMedia('(max-width:900px) and (orientation:portrait),(max-width:650px)');
const setRail = () => { byId('rail').open = !compact.matches; };
compact.addEventListener('change',setRail);
setRail();
window.addEventListener('hashchange',render);
render();
