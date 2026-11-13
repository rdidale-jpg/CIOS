/* Owner-testing interactions only. No network writes, model calls or live CRM access. */
(() => {
  'use strict';
  const config = JSON.parse(document.getElementById('experience-config').textContent);
  const seeds = JSON.parse(document.getElementById('experience-demo').textContent);
  const storageKey = 'flora.technology.owner-preview.v1';
  const status = document.getElementById('preview-status');
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const route = (suffix, params = {}) => config.base + suffix + '?' + new URLSearchParams(params).toString();
  const today = () => new Intl.DateTimeFormat('en-CA', {timeZone: 'Europe/London', year: 'numeric', month: '2-digit', day: '2-digit'}).format(new Date());
  const validDate = value => value === '' || /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(value + 'T12:00:00Z').toISOString().slice(0,10) === value;
  const money = value => value === '' ? '' : new Intl.NumberFormat('en-GB', {style:'currency', currency:'GBP', maximumFractionDigits: Number(value) % 1 ? 2 : 0}).format(Number(value));
  const date = value => value ? new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',day:'2-digit',month:'short',year:'numeric'}).format(new Date(value+'T12:00:00Z')) : '';
  const clean = source => {
    if (!source || typeof source !== 'object' || !/^(cooling|migration|resilience|connectivity|demo-[a-f0-9-]{1,40})$/.test(source.id)) throw Error('Invalid preview entry');
    const row = {};
    for (const [key,limit] of Object.entries({id:45,title:120,enterprise:120,district:40,stage:30,start:10,close:10,tcv:15,unit:100,stakeholder:100,owner:100,need:1000,next:300,decision:100,budgetOwner:100,responsible:100,due:10,procurement:200,competition:200,budget:30,scopeEnterprise:30})) {
      row[key] = typeof source[key] === 'string' ? source[key].slice(0,limit) : '';
    }
    if (!row.title.trim() || !row.enterprise.trim() || !config.stages.includes(row.stage) || !Object.hasOwn(config.districts,row.district)) throw Error('Invalid preview fields');
    if (![row.start,row.close,row.due].every(validDate) || row.start && row.close && row.close < row.start) throw Error('Invalid preview dates');
    if (row.tcv && (!/^\d+(\.\d{1,2})?$/.test(row.tcv) || !Number.isFinite(Number(row.tcv)) || Number(row.tcv)>999999999999)) throw Error('Invalid contract value');
    row.notes = Array.isArray(source.notes) ? source.notes.slice(-50).filter(n => n && typeof n.text==='string' && validDate(n.date) && n.date).map(n => ({text:n.text.slice(0,1000),date:n.date})) : [];
    row.history = Array.isArray(source.history) ? source.history.slice(-30).filter(n=>n && typeof n.text==='string' && validDate(n.date) && n.date).map(n=>({text:n.text.slice(0,200),date:n.date})) : [];
    return row;
  };
  let rows = seeds.map(clean);
  let tabStorage = true;
  try {
    const saved = sessionStorage.getItem(storageKey);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (!Array.isArray(parsed) || parsed.length > 200) throw Error('Invalid preview collection');
      rows = parsed.map(clean);
      if (new Set(rows.map(r=>r.id)).size !== rows.length) throw Error('Duplicate entry');
    }
  } catch (e) {
    rows = seeds.map(clean);
    status.textContent = 'Stored preview changes could not be loaded. Illustrative defaults are shown.';
  }
  const persist = () => {
    try { sessionStorage.setItem(storageKey, JSON.stringify(rows)); }
    catch (e) { tabStorage = false; }
    status.textContent = tabStorage ? 'Preview saved in this tab. No live Pipeline records changed.' : 'Browser storage is unavailable. Changes last only on this page; no live records changed.';
  };
  const inScope = row => config.scope === 'industry' || Object.hasOwn(config.participants,config.scope) && row.scopeEnterprise === config.scope || row.district === config.scope;
  let selected = '';
  let sort = {key:'title',direction:1};
  const tbody = document.getElementById('pipeline-rows');
  const q = document.getElementById('pipeline-search');
  const stageFilter = document.getElementById('pipeline-stage');
  const ownerFilter = document.getElementById('pipeline-owner');
  const selectOptions = () => {
    if (!ownerFilter) return;
    const value = ownerFilter.value;
    ownerFilter.innerHTML = '<option value="">All owners</option><option value="__unassigned">Unassigned</option>' + [...new Set(rows.filter(inScope).map(r=>r.owner).filter(Boolean))].sort().map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('');
    ownerFilter.value = [...ownerFilter.options].some(o=>o.value===value) ? value : '';
  };
  const table = () => {
    if (!tbody) return;
    const term = q.value.trim().toLocaleLowerCase();
    const visible = rows.filter(inScope).filter(r=>!stageFilter.value || r.stage===stageFilter.value).filter(r=>!ownerFilter.value || (ownerFilter.value==='__unassigned' ? !r.owner : r.owner===ownerFilter.value)).filter(r=>[r.title,r.enterprise,r.unit,r.stakeholder,r.owner].join(' ').toLocaleLowerCase().includes(term));
    visible.sort((a,b)=>{
      const av=a[sort.key],bv=b[sort.key];
      if (av==='' || bv==='') return av===bv ? 0 : av==='' ? 1 : -1;
      return (sort.key==='tcv' ? Number(av)-Number(bv) : av.localeCompare(bv,'en-GB',{numeric:true}))*sort.direction;
    });
    if (selected && !visible.some(r=>r.id===selected)) selected='';
    tbody.innerHTML = visible.map(r=>`<tr data-row="${esc(r.id)}"${selected===r.id?' aria-selected="true"':''}>
      <td><a class="exp-row-select" data-select="${esc(r.id)}" href="${esc(route('/opportunity',{record:r.id,scope:config.scope}))}">${esc(r.title)}</a></td>
      <td>${esc(r.enterprise)}</td><td><span class="exp-stage">${esc(r.stage)}</span></td>
      <td>${esc(date(r.start))}<button type="button" class="exp-text-button" data-edit="${esc(r.id)}" data-focus="start" aria-label="Edit start date for ${esc(r.title)}">✎</button></td>
      <td>${esc(date(r.close))}</td><td>${esc(money(r.tcv))}</td><td>${esc(r.unit||'')}<small>${esc(r.stakeholder||'')}</small></td><td>${esc(r.owner||'')}</td></tr>`).join('') || `<tr><td colspan="8"><div class="exp-empty"><h2>Build your preview Pipeline</h2><p>Add an illustrative opportunity, or change the filters.</p></div></td></tr>`;
    document.getElementById('pipeline-count').textContent = visible.length + ' illustrative opportunit' + (visible.length===1?'y':'ies');
    document.querySelectorAll('[data-sort]').forEach(button=>button.parentElement.setAttribute('aria-sort',sort.key===button.dataset.sort?(sort.direction===1?'ascending':'descending'):'none'));
    const quick = document.getElementById('quick-detail');
    const current = rows.find(r=>r.id===selected);
    quick.hidden = !current;
    if (current) quick.innerHTML = `<div class="exp-heading"><h2>${esc(current.title)}</h2><a href="${esc(route('/opportunity',{record:current.id,scope:config.scope}))}">Open full opportunity →</a></div><dl class="exp-summary"><div><dt>Business unit</dt><dd>${esc(current.unit||'')}</dd></div><div><dt>Key stakeholder</dt><dd>${esc(current.stakeholder||'')}</dd></div><div><dt>Next action</dt><dd>${esc(current.next||'')}</dd></div><div><dt>Edit</dt><dd><button type="button" data-edit="${esc(current.id)}">Edit preview</button></dd></div></dl>`;
  };
  const fact = (label,value) => `<div><dt>${esc(label)}</dt><dd>${esc(value||'')}</dd></div>`;
  const detail = () => {
    const target = document.getElementById('opportunity-detail');
    if (!target) return;
    const row = rows.find(r=>r.id===config.record && inScope(r));
    if (!row) {
      target.innerHTML = `<h1>Opportunity unavailable</h1><p>This opportunity is not in this tab’s preview or current scope.</p><a href="${esc(route('/pipeline',{scope:config.scope}))}">Return to Pipeline →</a>`;
      return;
    }
    target.innerHTML = `<div class="exp-heading"><div><h1>${esc(row.title)}</h1><p class="exp-subtitle">${esc(row.enterprise)} · ${esc(row.unit||'')}</p><p class="exp-subtle">Illustrative opportunity · edits stay in this tab</p></div><div class="exp-inline"><label>Stage<select id="opportunity-stage" aria-label="Opportunity stage">${config.stages.map(s=>`<option${row.stage===s?' selected':''}>${esc(s)}</option>`).join('')}</select></label><button type="button" data-edit="${esc(row.id)}">Edit</button></div></div>
      <dl class="exp-summary">${fact('Estimated TCV',money(row.tcv))}${fact('Start date',date(row.start))}${fact('Expected close',date(row.close))}${fact('Owner',row.owner||'')}</dl>
      <div class="exp-op-layout"><div><section><h2>Buying need</h2><p>${esc(row.need||'')}</p></section>
      <section><h2>Next action</h2><p class="exp-action">${esc(row.next||'')}</p><div class="exp-inline"><span>Responsible: ${esc(row.responsible||'')}</span><span>Due: ${esc(date(row.due))}</span><button type="button" data-edit="${esc(row.id)}" data-focus="next">Edit next action</button></div></section>
      <section><h2>Progress</h2><ul class="exp-notes">${(row.history.length?row.history:[{date:'2026-11-12',text:'Illustrative opportunity prepared'}]).map(n=>`<li>${esc(date(n.date))} · ${esc(n.text)}</li>`).join('')}</ul></section></div>
      <div><section><h2>People & ownership</h2><dl class="exp-facts">${fact('Business unit',row.unit)}${fact('Key stakeholder',row.stakeholder)}${fact('Decision maker',row.decision)}${fact('Budget owner',row.budgetOwner)}</dl></section>
      <section><h2>Commercial position</h2><dl class="exp-facts">${fact('Budget',row.budget==='Not confirmed'?'':row.budget||'')}${fact('Procurement route',row.procurement||'')}${fact('Competition',row.competition||'')}</dl></section></div></div>
      <section class="exp-editorial"><h2>Notes</h2>${row.notes.length?`<ul class="exp-notes">${row.notes.map(n=>`<li><small>${esc(date(n.date))}</small><br>${esc(n.text)}</li>`).join('')}</ul>`:'<p class="exp-subtle">No notes yet.</p>'}<form class="exp-notes-form" id="note-form"><label class="visually-hidden" for="opportunity-note">Add a note</label><textarea id="opportunity-note" name="note" rows="2" maxlength="1000" required placeholder="Add a note"></textarea><button type="submit">Add note</button></form></section>
      <div class="exp-inline"><a href="${esc(route('/pipeline',{scope:config.scope}))}">← Pipeline</a>${row.scopeEnterprise?`<a href="${config.base}/enterprise?enterprise=${esc(row.scopeEnterprise)}">Enterprise context →</a>`:'<span class="exp-subtle">Fictitious enterprise · no live enterprise record</span>'}</div><p class="exp-subtle">TCV = estimated full-term value excluding VAT · Dates and amounts are illustrative.</p>`;
    document.getElementById('opportunity-stage').addEventListener('change',event=>{
      const old = row.stage;
      row.stage = event.target.value;
      row.history.push({date:today(),text:`Stage changed from ${old} to ${row.stage} (preview)`});
      persist(); detail(); document.getElementById('opportunity-stage').focus();
    });
    document.getElementById('opportunity-note').addEventListener('input',event=>event.target.setCustomValidity(''));
    document.getElementById('note-form').addEventListener('submit',event=>{
      event.preventDefault();
      const input=document.getElementById('opportunity-note'),value=input.value.trim();
      if (!value) {input.setCustomValidity('Enter a note.');input.reportValidity();return;}
      if (row.notes.length>=50) {status.textContent='Preview limit: 50 notes per opportunity.';return;}
      row.notes.push({date:today(),text:value});persist();detail();document.getElementById('opportunity-note').focus();
    });
  };
  const dialog = document.getElementById('demo-editor');
  const form = document.getElementById('opportunity-form');
  let editing='', opener=null;
  const openEditor = (id='', focus='title') => {
    if (!dialog) return;
    const row = id ? rows.find(r=>r.id===id) : {stage:'Discovery',district:Object.hasOwn(config.districts,config.scope)?config.scope:'cloud',start:today(),enterprise:Object.hasOwn(config.participants,config.scope)?config.participants[config.scope]+' (preview)':''};
    if (!row || rows.length>=200 && !id) {status.textContent='Preview limit reached.';return;}
    editing = id;opener=document.activeElement;form.reset();
    form.elements.enterprise.readOnly = Object.hasOwn(config.participants,config.scope) || Object.hasOwn(config.participants,row.scopeEnterprise||'');
    for (const element of form.elements) if (element.name) element.value = row[element.name] || (element.name==='budget'?'Not confirmed':'');
    document.getElementById('editor-title').textContent=id?'Edit opportunity':'New illustrative opportunity';
    document.getElementById('editor-error').textContent='';dialog.showModal();
    if (form.elements[focus]) form.elements[focus].focus();
  };
  if (form) {
    document.getElementById('close-editor').addEventListener('click',()=>dialog.close());
    dialog.addEventListener('close',()=>{if(opener && opener.isConnected)opener.focus();});
    form.addEventListener('submit',event=>{
      event.preventDefault();
      const previous=rows.find(r=>r.id===editing);
      const incoming={...(previous||{}),...Object.fromEntries(new FormData(form).entries()),id:editing||'demo-'+crypto.randomUUID(),scopeEnterprise:previous?.scopeEnterprise||(Object.hasOwn(config.participants,config.scope)?config.scope:'')};
      for (const key of Object.keys(incoming)) if(typeof incoming[key]==='string')incoming[key]=incoming[key].trim();
      try {
        const row=clean(incoming);
        row.history.push({date:today(),text:editing?'Opportunity updated (preview)':'Opportunity opened (preview)'});
        if (editing) rows=rows.map(r=>r.id===editing?row:r); else rows.push(row);
        persist();dialog.close();selectOptions();table();detail();
        if (tbody) {const focusTarget=[...document.querySelectorAll('[data-select]')].find(a=>a.dataset.select===row.id);if(focusTarget)focusTarget.focus();}
        else {const target=document.querySelector('[data-edit]');if(target)target.focus();}
      } catch(e) {document.getElementById('editor-error').textContent='Check required fields, valid dates (close on or after start), and a non-negative contract value with up to two decimal places.';}
    });
  }
  document.addEventListener('click', event=>{
    const edit=event.target.closest('[data-edit]');
    if(edit){event.preventDefault();openEditor(edit.dataset.edit,edit.dataset.focus||'title');return;}
    const create=event.target.closest('[data-new-opportunity]');
    if(create){openEditor();return;}
    const select=event.target.closest('[data-select]');
    if(select){event.preventDefault();selected=select.dataset.select;table();const quick=document.getElementById('quick-detail');const heading=quick.querySelector('h2');heading.tabIndex=-1;heading.focus();return;}
    const sortButton=event.target.closest('[data-sort]');
    if(sortButton){const key=sortButton.dataset.sort;sort={key,direction:sort.key===key?-sort.direction:1};table();return;}
  });
  if(tbody){
    [q,stageFilter,ownerFilter].forEach(element=>element.addEventListener(element===q?'input':'change',table));
    document.getElementById('reset-demo').addEventListener('click',()=>{if(!confirm('Reset all illustrative Pipeline changes in this tab?'))return;rows=seeds.map(clean);selected='';persist();selectOptions();table();});
    selectOptions();table();
  }
  detail();
  const reveal = () => {const id=location.hash.slice(1),node=document.getElementById(id);if(node?.tagName==='DETAILS')node.open=true;};
  reveal();addEventListener('hashchange',reveal);
})();
