"""Read-only Lloyds decision views over canonical research/source-review owners."""
from datetime import date
from html import escape as e
from . import model,understanding
from .commercial_intelligence import commercial_projection

PRIORITIES={
 'RCO-LBG-002':('AI','CAP-DATA','Which deployed workflow has a customer-owned net-benefit baseline, risk owner and a delivery gap that existing teams/Google Cloud cannot cover?','Internal AI delivery and the disclosed Google Cloud collaboration are alternatives to an external services mandate.'),
 'RCO-LBG-001':('LEGACY','CAP-TECH','Which named remaining application can be retired, who owns dependencies and what independently testable cost/control outcome will be accepted?','Cloud adoption is not application retirement. Internal platform teams or existing partners may already cover the work.'),
 'RCO-LBG-009':('WALLET','CAP-PAYMENTS','Which wallet integration outcome remains unmet, what is Curve versus Group scope, and who can authorise an external delivery tranche?','Wallet launch intent is not verified completion, Curve integration architecture, supplier demand or a procurement process.')}
STYLE='''
.depth{color:#174d3f;margin:20px 0}.depth-box{background:#f5f3e7;border:1px solid #c4d3be;border-radius:20px;padding:24px;margin:16px 0}.depth h2{font-size:1.5rem}.depth p,.depth li,.depth dd{line-height:1.55}.depth-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.depth-grid>*{min-width:0}.depth article{border:1px solid #c6d3c0;border-radius:16px;padding:18px;background:#fffdf7}.depth small{display:block;font-size:.82rem;overflow-wrap:anywhere}.depth a,.depth button,.depth summary{min-height:44px;align-content:center}.depth a{display:inline-block}.depth button{border:1px solid #9eb59d;border-radius:20px;padding:10px 15px;background:#174d3f;color:white;font:inherit;cursor:pointer}.depth a:focus-visible,.depth button:focus-visible,.depth summary:focus-visible{outline:3px solid #885a2f;outline-offset:3px}.depth dt{font-weight:bold;margin-top:10px}.depth dd{margin:4px 0 12px}.depth table{width:100%;border-collapse:collapse}.depth td,.depth th{padding:12px;text-align:left;border-bottom:1px solid #c4d3be;vertical-align:top}.depth-warning{border-left:4px solid #b78548;padding:12px;background:#f5ead8}.depth-flow{font-size:.8rem;color:#695b38}.depth-print-output,.depth-print-citations{display:none}@media(max-width:750px){.depth-grid{grid-template-columns:1fr}.depth table,.depth tbody,.depth tr,.depth td{display:block}.depth thead{display:none}.depth-box{padding:18px}}@media(prefers-reduced-motion:reduce){.depth *{scroll-behavior:auto!important;transition:none!important}}@media print{@page depthExecutive{size:A4 portrait;margin:15mm}.depth-print-output{page:depthExecutive}body:has(>.depth-print-output)>:not(.depth-print-output){display:none!important}.depth-print-output{display:block!important;color:#173f37;font:11pt/1.35 Arial}.depth-print-output .depth-print-citations{display:block}.depth-print-output h2{font-size:18pt}.depth-print-output a{color:#173f37;overflow-wrap:anywhere}.depth-print-output button{display:none}.depth-print-output .depth-grid{display:block}.depth-print-output article{padding:8px;margin:8px 0;break-inside:avoid}.depth-print-output small{display:block;font-size:9pt;overflow-wrap:anywhere}.depth-print-output p{margin:7px 0}.depth-print-output .depth-no-exec{display:none}}
'''
SCRIPT='''
(function(){if(window.floraDepthPrint)return;window.floraDepthPrint=true;
 var states=[];
 function cleanup(){var restore=states;states=[];setTimeout(function(){restore.forEach(function(s){if(s[0].isConnected)s[0].open=s[1]})},0);document.querySelectorAll('body>.depth-print-output').forEach(function(n){n.remove()});delete document.documentElement.dataset.depthPrint}
 window.addEventListener('beforeprint',function(){var source=document.querySelector('.depth-executive');if(!source)return;states=Array.from(document.querySelectorAll('details')).map(function(d){return [d,d.open]});if(document.documentElement.dataset.depthPrint==='appendix'){states.forEach(function(s){s[0].open=true});return;}document.querySelectorAll('body>.depth-print-output').forEach(function(n){n.remove()});var copy=source.cloneNode(true);copy.className='depth-print-output';copy.querySelectorAll('script,button').forEach(function(n){n.remove()});document.body.appendChild(copy)},true);
 window.addEventListener('afterprint',cleanup);
 document.addEventListener('click',function(event){var button=event.target.closest('[data-depth-print]');if(!button)return;document.documentElement.dataset.depthPrint=button.dataset.depthPrint;window.print()});
})();
'''

def available(data):
    from .cycle import digest
    r=understanding.load_review('banking')
    return data['enterprise_twin_id']=='BK-ENT-001' and r['baseline_digest']==digest(data)


def assessment(data):
    return understanding.assess(data,understanding.load_review('banking'),date.today().isoformat())


def source_cards(data,key,reviewed=None):
    x=reviewed if reviewed is not None else assessment(data);sid='DEPTH-LBG-'+key
    source=next(s for s in x['sources'] if s['id']==sid)
    title=next(s['title'] for s in understanding.load_review('banking')['sources'] if s['id']==sid)
    claim=next(c for c in x['claims'] if c['id']=='RC-'+sid)
    return (f"<blockquote>{e(claim['statement'])}</blockquote><small>Candidate company statement · {e(claim['period'])}. Publication: {e(source['publication_date'] or 'Unknown')}; retrieved {e(source['retrieved_at'])}.</small>"
        +f"<small>{e(claim['links'][0]['locator'])}. {e(source['limitation'])}</small><a href='{e(source['url'],quote=True)}'>Primary source: {e(title)}</a><small>{e(source['url'])}</small>")


def hypothesis_depth(data,row):
    if not available(data) or row['id'] not in PRIORITIES:return ''
    key,cap,question,alternative=PRIORITIES[row['id']]
    capabilities={c['id']:c['title'] for c in data['capabilities']}
    return f"<style>{STYLE}</style><script>{SCRIPT}</script><section class='depth depth-box depth-executive' id='depth-{row['id']}'><h2>Qualification gap map · investigate before pursuing</h2><p>Analyst interpretation, not customer validation. Affected research capability: {e(capabilities.get(cap,cap))}.</p>"+source_cards(data,key)+(source_cards(data,'CURVE') if key=='WALLET' else '')+f"<dl><dt>Potential business outcome</dt><dd>{e(row['commercial']['business_problem'])}</dd><dt>Trigger and competing delivery options</dt><dd>{e(alternative)}</dd><dt>Evidence against the commercial inference</dt><dd>Existing internal delivery, retained counterevidence and unclear scope may remove any external service gap. No unfilled mandate is established.</dd><dt>Next customer-validation question</dt><dd>{e(question)}</dd><dt>Authority, access and money</dt><dd>Buyer authority/access: Unknown. Budget/value: Unknown. Procurement: Unknown. External service gap: Unverified.</dd></dl><a href='#commercial-counterevidence'>Inspect full counterevidence and conflicting periods →</a><p><button type='button' data-depth-print='executive'>Print executive brief</button> <button type='button' data-depth-print='appendix'>Print full evidence appendix</button></p></section>"


def executive(data,industry=False):
    if not available(data):return ''
    title='UK Banking — pressures to investigate' if industry else 'Lloyds — three changes worth investigating'
    body=f"<style>{STYLE}</style><section class='depth depth-box depth-executive'><p>Candidate research · as of {date.today().isoformat()} · not accepted enterprise facts</p><h2>{title}</h2>"
    if industry:
        body+="<p>Industry pressures affect operating capabilities; a Lloyds disclosure is an enterprise example, not proof of an industry-wide trend or procurement.</p><ul><li>Political/legal → service access and operational resilience → test entity-specific obligations and accountable controls.</li><li>Economic/competition → deposit value and switching → test customer outcomes before proposing technology.</li><li>Technology/value chain → data, payments and platforms → inspect dependence, delivery alternatives and net benefits.</li></ul><p>Interpretive investigation prompts; no numerical attractiveness or pressure score.</p><a href='/enterprises/lloyds'>Lloyds-specific programmes and evidence →</a>"
    else:
        body+="<p>What changed: four primary documents re-opened and short located passages appended, preserving historical evidence. This deepens specificity, not verified customer demand.</p><div class='depth-grid'>"
        p=commercial_projection(data)
        for cid,(key,cap,question,alternative) in PRIORITIES.items():
            row=next(r for r in p['candidates'] if r['id']==cid)
            body+=f"<article><h3>{e(row['title'])}</h3><p>{e(alternative)}</p><p><strong>Unanswered buying question:</strong> {e(question)}</p><a href='{row['url']}#depth-{cid}'>Inspect hypothesis, evidence & next step →</a></article>"
        body+='</div><p>Evidence strength: short company primary excerpts; no independent outcome corroboration, current supplier contract, buyer authority or external buying intent established.</p>'
    # Short citations survive executive print. Complete quotations live in drill-down.
    reviewed=assessment(data)
    body+="<details class='depth-no-exec'><summary>Fresh primary provenance and acquisition limits</summary>"+''.join(source_cards(data,k,reviewed) for k in ('AI','LEGACY','WALLET','CURVE'))+'</details>'
    body+="<div class='depth-print-citations'>Sources (quotation availability and dates via drill-down): "
    citation_sources=([s for s in data['sources'] if s['id'] in {'PR-FCA-RES26','PR-PRA-PS726','SRC-CMA-OB'}] if industry else [s for s in understanding.load_review('banking')['sources'] if s['id'].startswith('DEPTH-')])
    for s in citation_sources:
        if s:body+=f"<small><a href='{e(s['url'],quote=True)}'>{e(s['title'])}</a> · publication {e(s['publication_date'] or 'Unknown')} · {e(s['url'])}</small>"
    body+="</div><p><button type='button' data-depth-print='executive'>Print executive brief</button> <button type='button' data-depth-print='appendix'>Print full evidence appendix</button></p><p class='depth-no-exec'>Browser print defaults to this executive brief when JavaScript is enabled. Without JavaScript the ordinary detailed page remains printable. No sources are suppressed from the full appendix.</p>"
    return body+f"<script>{SCRIPT}</script></section>"


def operating_depth(data):
    from .visual_intelligence import _icon
    if not available(data):return ''
    return executive(data)+coverage_body(data)+"<section class='depth'><h2>Programme → operating capability → outcome to validate</h2><p class='depth-warning'>Research associations, not a complete application inventory or contractual topology. Group scope; no automatic brand/subsidiary propagation.</p><div class='depth-grid'>"+''.join(f"<article><svg viewBox='0 0 80 65' width='80' height='65' aria-hidden='true' style='color:#47735d'>{_icon('bank' if cid.endswith('009') else 'server',10,5,1.4)}</svg><h3>{e(label)}</h3><p class='depth-flow'>{e(flow)}</p><p>{e(note)}</p><a href='/flora/banking/research/candidates/{cid}#depth-{cid}'>Evidence, options & customer question →</a></article>" for cid,label,flow,note in [
 ('RCO-LBG-002','AI delivery','Group AI platform → data/model delivery → net benefit and control outcomes','Google Cloud Vertex AI is named in an April 2025 disclosure. Present contract breadth, exclusivity and programme ownership remain unknown.'),
 ('RCO-LBG-001','Legacy simplification','Platform change → dependency retirement → cost and resilience outcome','Simplification is a stated direction. Named retirement waves, accountable application owners and verified benefits are missing. Retained 50% / 60% estate claims have different scope/period; never average them.'),
 ('RCO-LBG-009','Wallet proposition','Group wallet outlook → payments/customer experience → adoption and integration outcomes','A product intention does not prove Curve integration design or completion. Current partner roles, operational readiness and an external service gap remain unknown.')])+"</div></section>"


def framework_depth(data,rows):
    if not available(data):return ''
    caps={c['id']:c['title'] for c in data['capabilities']}
    return "<section class='depth'><h2>Pressure → capability → investigation</h2><p>Interpretive direction, not proven causation. Enterprise examples retain their own scope; no sector-wide claim follows.</p><div class='depth-grid'>"+''.join(f"<article><h3>{e(f['title'])}</h3><p>{e(f['assessment'])}</p><p class='depth-flow'>Pressure → affected capabilities: {e(', '.join(caps.get(k,k) for k in f['capability_ids']))}</p><p><strong>Investigate:</strong> {e(framework_question(f))}</p><a href='/flora/banking/research/nodes/{f['id']}'>Scoped examples, sources & gaps →</a></article>" for f in rows)+'</div></section>'


def coverage_inventory(data,reviewed=None):
    x=reviewed if reviewed is not None else assessment(data)
    claims={c['id']:c for c in x['claims']};sources={s['id']:s for s in x['sources']}
    conflicting={cid for c in x['contradictions'] for cid in c.get('claim_ids',[])}
    rows=[]
    for row in x['dossier']:
        ids=set(row['claim_ids'])|set(row.get('reviewed_candidate_ids',[]))
        retained=[claims[c] for c in sorted(ids) if c in claims]
        backed=bool(row['supported_claim_ids']) or any(c['direct_support_reviewed'] for c in retained)
        historical=any(sources[s].get('publication_date') and sources[s]['publication_date']<'2026-01-01' for c in retained for s in c['source_ids'])
        tags=['Source-backed candidate; inspect scope/date' if backed else 'Missing / interpreted; not certified']
        if ids & conflicting:tags.append('Conflicting scope/period retained')
        if historical:tags.append('Includes historical evidence')
        rows.append({**row,'classification':'; '.join(tags),'claims':retained})
    return rows


def decision_register(data):
    rows=commercial_projection(data)['candidates']
    return f"<style>{STYLE}</style><section class='depth'><h3>Hypothesis decision register · {len(rows)} retained identities</h3><p>Source-owned assessments stay separate; no combined score or verified buying demand. Industry shows structure, Enterprise shows change, this register chooses the next commercial question.</p><table><thead><tr><th>Hypothesis</th><th>Separate assessments</th><th>Access and next decision</th></tr></thead><tbody>"+''.join(f"<tr><td><a href='{row['url']}'>{e(row['title'])}</a><small>Research priority {row['commercial_rank']} / Unqualified</small></td><td>"+'<br>'.join(e(d['label'])+' '+str(d['score'])+'/3' for d in row['dimensions'])+f"</td><td>{e(PRIORITIES[row['id']][2] if row['id'] in PRIORITIES else row['commercial']['next_commercial_action'])}<small>Buyer access, budget and procurement: Unknown. External service gap: Unverified.</small></td></tr>" for row in rows)+'</tbody></table></section>'


def coverage_body(data):
    rows=coverage_inventory(data)
    return "<section class='depth'><details><summary>Coverage inventory · source-backed, historical, conflicting and missing</summary><p>Coverage is not certification. Specific source periods and contradictions remain inspectable below; missing mapped claims do not prove absence of a capability.</p><table><thead><tr><th>Knowledge area</th><th>Evidence state</th><th>Material deficiency</th></tr></thead><tbody>"+''.join(f"<tr><td>{e(r['label'])}</td><td>{e(r['classification'])}<small>{e('; '.join(r['period_labels']) or 'Period unknown')}</small></td><td>{e('; '.join(r['deficiencies']))}</td></tr>" for r in rows)+"</tbody></table><a href='/enterprises/lloyds/understanding'>Inspect complete source, contradiction and relationship review →</a></details></section>"


def framework_question(node):
    questions={
      'PESTLE-P':'Which service-access or capital-policy change binds which regulated entity, and who owns its control response?',
      'PESTLE-E':'Which deposit, margin or cost pressure has comparable cross-bank evidence rather than a single-enterprise forecast?',
      'PESTLE-S':'Which customer cohort needs assisted access, and what measured outcome would justify channel change?',
      'PESTLE-T':'Which data/platform dependency limits a specific workflow, and can existing internal teams or partners resolve it?',
      'PESTLE-L':'Which applicable obligation and implementation date require evidence, rather than assuming every policy creates procurement?',
      'PESTLE-ENV':'Which operational versus financed-emissions measure is affected, with what boundary and reporting period?',
      'PORTER-RIVALRY':'Where do banks compete on switching, service and value, and which customer metric distinguishes a proposition?',
      'PORTER-ENTRY':'Which entrant can overcome regulated scale, trust and funding barriers, rather than treating digital adoption as disruption?',
      'PORTER-BUYER':'How do switching friction, open banking and deposit alternatives change customer choice in this segment?',
      'PORTER-SUPPLIER':'Which critical technology concentration is evidenced, what substitution/exit options exist, and which contracts remain unknown?',
      'PORTER-SUBSTITUTE':'Which payments or savings substitutes displace a customer task, and is there evidence of adoption rather than launch intention?',
      'VC-PRODUCT':'Who owns the proposition outcome and business case, and how is investment linked to measurable customer benefit?',
      'VC-ACQUIRE':'Where does onboarding lose customers, and how do digital conversion and assisted-access obligations interact?',
      'VC-DEPOSITS':'Which funding/customer-value trade-off is measurable without inferring a bank-specific commercial budget?',
      'VC-LENDING':'Which credit decision or servicing process can improve speed while preserving affordability and model controls?',
      'VC-PAYMENTS':'Which settlement, wallet or fraud-control dependency is actually established, and what is proposed versus operational?',
      'VC-SERVICE':'Which servicing task has avoidable effort, with evidence of vulnerability, complaints and customer-outcome effects?',
      'VC-CONTROL':'Which critical service, third party and recovery objective require evidenced accountability and resilience testing?',
      'VC-ENABLE':'Which application/data dependency can be retired or reused, and what baseline proves net benefit after change cost?'}
    return questions.get(node['id'],'Which bounded customer outcome, accountable owner and evidence would establish the proposed operating change?')
