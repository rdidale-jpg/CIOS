#!/usr/bin/env python3
"""VP-1 static design export. No application route, model, service or domain write.

Only public merged view owners are read. This is a dated design snapshot, not a
production renderer, intelligence store, permission implementation or source import.
"""
from dataclasses import replace
from datetime import date
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
from html import escape as e
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cios.applications.flora import visual_v2, leadership_agenda as agenda
from cios.applications.flora import intelligence_presentation as policy
from cios.applications.flora.research_intelligence import model

HERE = Path(__file__).resolve().parent
OUT = HERE / 'prototype'
BASE = '8a53777d1dec359f56b66e533d512c0a86881939'
AS_OF = '2026-11-15'
SOURCE_PATHS = ['cios/applications/flora/visual_v2_assets/economy.json',
    'enterprise-knowledge/banking/research-model/Assessment-Overlay.json',
    'enterprise-knowledge/macro/research-model/Macro-Context-v1.json',
    'enterprise-knowledge/banking/research-model/source-snapshots/INT1-FCA-Candidate.json']
SCOPES = {
    'uk': ('United Kingdom', ('landscape', 'forces'), ('overview', 'economics', 'agenda')),
    'banking': ('UK Banking', ('landscape', 'forces'), ('overview', 'regulation', 'agenda')),
    'lloyds': ('Lloyds Banking Group', ('inside', 'landscape', 'forces'), ('overview', 'economics', 'technology', 'agenda')),
}
LABELS = {'overview':'Overview', 'economics':'Financial scale', 'technology':'Technology & AI',
          'regulation':'Regulation', 'agenda':'Leadership Agenda'}


class SnapshotDate(date):
    @classmethod
    def today(cls): return cls.fromisoformat(AS_OF)


def filename(scope, stream, focus='overview'):
    return f'{scope}-{stream}' + ('' if focus == 'overview' else '-' + focus) + '.html'


def accepted_view(row):
    if not policy.eligible(row): raise ValueError('Ineligible design content')
    return row


def statements():
    data = model.load_assessment()
    rows = {c['id']:policy.claim_view(data,c) for c in data['claims']}
    return data, rows


def type_text(row, text=None):
    accepted_view(row)
    state = {'target':'Management target', 'expectation':'Management expectation', 'commitment':'Stated priority'}.get(row.measurement_state,'')
    return f'<p class="statement" data-semantic-type="{row.semantic_type}"><span class="kind">{policy.LABELS[row.semantic_type]}</span> ' + (f'<span class="state">{state}</span> ' if state else '') + e(text or row.text) + '</p>'


def evidence(rows):
    rows = list(dict.fromkeys(accepted_view(r) for r in rows))
    body = '<details class="sources"><summary>Sources &amp; basis</summary>'
    for row in rows:
        body += '<section class="source-entry"><p><strong>' + policy.LABELS[row.semantic_type] + '</strong> · ' + e(row.scope) + ' · ' + e(row.period) + '</p><p>' + e(row.text) + '</p>'
        for t in (row.method,row.reasoning,*row.caveats,*row.counter_evidence):
            if t: body += '<p>' + e(t) + '</p>'
        if row.falsifier: body += '<p>Counter-test: ' + e(row.falsifier) + '</p>'
        if row.assumption_owner: body += '<p>Assumption: ' + e(row.assumption_owner) + ' · ' + e(row.assumption_version) + '</p>'
        if any(t in {'estimated','assumed'} for t in row.dependency_types):
            body += '<p>Depends on estimated or assumed inputs; their limitations remain.</p>'
        for source in row.sources:
            body += '<p><a href="' + e(source.url,quote=True) + '" rel="noreferrer">' + e(source.title) + '</a>' + (' · ' + e(source.published) if source.published else '') + '</p><p>' + e(source.locator) + '</p>'
        body += '</section>'
    urls={s.url for r in rows for s in r.sources}
    if any('ons.gov.uk' in u for u in urls):
        body+='<p class="licence">ONS data: Crown copyright, licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    if any('fca.org.uk/data/firm-level-complaints' in u for u in urls):
        body+='<p class="licence">Contains Financial Conduct Authority information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    if any('gov.uk/government/' in u for u in urls):
        body+='<p class="licence">Contains public sector information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noreferrer">Open Government Licence v3.0</a>.</p>'
    return body + '</details>'


def uk_values():
    b = visual_v2.basis()
    sources = tuple(policy.Source(s['title'],s['url'],'Office for National Statistics',s.get('publication_date') or '',locator=s['locator']) for s in b['sources'][:2])
    reported = policy.Statement('UK gross value added was £2,623bn in 2024, at current basic prices.', 'reported','United Kingdom','2024',sources,'reported_source','existing_public_extract')
    d = next(d for d in b['districts'] if d['sic']=='K')
    share = policy.Statement('Finance & insurance represented 8.1% of UK GVA; this includes more than Banking.','calculated','UK SIC 2007 section K','2024',sources,'derived_from_inputs','derived_view_not_canonical',method='Published weight 81 per thousand ÷ 10 = 8.1%. Rounded weights are not normalised.',dependencies=(reported.text,),dependency_types=('reported',))
    assumption = policy.Statement('The range assumes nearest-unit rounding of the published total and section weight.','assumed','UK SIC 2007 section K','2024',sources,'repository_interpretation','design_assumption_not_canonical',method='Total ± £0.5bn; weight ± 0.5 per thousand. This is a design sensitivity convention, not a published confidence interval.',caveats=('Conditional design sensitivity convention; a different rounding rule changes the range.',),assumption_owner='VP-1 design sensitivity convention',assumption_version='1 / 15 November 2026')
    lo=(Decimal('2622.5')*Decimal('80.5')/1000).to_integral_value(rounding=ROUND_FLOOR)
    hi=(Decimal('2623.5')*Decimal('81.5')/1000).to_integral_value(rounding=ROUND_CEILING)
    estimate=policy.Statement(f'Finance & insurance GVA is approximately £212bn, with an illustrative rounding range of £{lo}–{hi}bn.','estimated','UK SIC 2007 section K; not Banking alone','2024',sources,'derived_from_inputs','design_estimate_not_canonical',method='£2,623bn × 81 / 1,000 = £212.463bn, displayed approximately. Range multiplies nearest-unit input bounds and rounds outward to whole billions.',caveats=('Illustrative rounding sensitivity, not a statistical confidence interval, company revenue or Banking sales-market value. The range depends on the stated rounding assumption.',),dependencies=(reported.text,share.text,assumption.text),dependency_types=('reported','calculated','assumed'))
    for row in (reported,share,assumption,estimate): accepted_view(row)
    return b,reported,share,assumption,estimate


def metrics(values):
    return '<div class="metrics">' + ''.join('<div><span class="metric-label">'+e(label)+'</span><strong>'+e(value)+'</strong><span class="metric-period">'+e(period)+'</span></div>' for label,value,period in values) + '</div>'


def bars(title, rows, ceiling=100, unit='%', note=''):
    # Actual values, linear zero-based scale, visible values and an equivalent table.
    body = '<figure class="chart"><figcaption>'+e(title)+'</figcaption>'
    if title.startswith('Customer-deposit'):
        body += '<input class="reference-control" id="deposit-reference" type="checkbox" checked><label class="reference-label" for="deposit-reference">2025 reference</label>'
    body += '<div class="bars" role="group" aria-label="'+e(title,quote=True)+'">'
    for label,value in rows:
        body += '<div class="bar-row"><span>'+e(label)+'</span><div class="track"><i style="--value:'+str(float(value)/ceiling*100)+'%"></i></div><strong>'+e(str(value)+unit)+'</strong></div>'
    body += '</div><p class="chart-note">'+e(note)+'</p><details class="chart-data"><summary>Chart data</summary><table><caption>'+e(title)+'</caption><tbody>'
    body += ''.join('<tr><th scope="row">'+e(label)+'</th><td>'+e(str(value)+unit)+'</td></tr>' for label,value in rows)
    return body + '</tbody></table></details></figure>'


def leadership(scope):
    with patch.object(agenda,'date',SnapshotDate): rows = agenda.agenda(scope)
    if len(rows)!=2: raise ValueError('Merged INT-1 agenda changed; do not incorporate pending branches')
    body='<p class="eyebrow">Leadership Agenda</p><h1 id="main-title" tabindex="-1">'+{'uk':'Growth and public value','banking':'Funding and resilience','lloyds':'Value within existing capabilities'}[scope]+'</h1>'
    all_rows=[]
    for r in rows:
        body+='<section class="editorial-issue"><h3>'+e(r.title)+'</h3>'+type_text(r.conclusion)
        body+='<p class="perspective">'+e(r.conclusion.counter_evidence[0])+'</p></section>'
        all_rows.extend([r.conclusion,*r.facts])
    if scope=='lloyds':
        body+='<div class="response"><h3>Existing management response</h3><p>Envoy is an announced platform with described controls. Google Cloud is a disclosed collaborator; an announced collaboration does not establish contract value or available external scope.</p></div>'
    return body+evidence(all_rows)


def uk_main(stream,focus):
    if focus=='agenda': return leadership('uk')
    b,total,share,assumption,estimate=uk_values()
    with patch.object(agenda,'date',SnapshotDate): growth=agenda.agenda('uk')[0]
    title='The shape of the UK economy' if stream=='landscape' else 'Services lead the latest expansion'
    if focus=='economics': title='Economic scale, precisely scoped'
    body='<p class="eyebrow">'+('Economic landscape' if stream=='landscape' else 'National forces')+'</p><h1 id="main-title" tabindex="-1">'+title+'</h1><p class="lead">'+('A varied economy, connected by services, industry and infrastructure.' if stream=='landscape' else 'Real output growth and the national output mix describe different dimensions of the economy.')+'</p>'
    body+=metrics([('Reported · UK GVA','£2.62tn','2024 · current basic prices'),('Reported · real GDP growth','+0.7%','3 months to September 2026 · versus prior 3 months')])
    chosen=[d for d in b['districts'] if d['sic'] in {'C','J','K','Q'}]
    body+=bars('Four comparable sector shares',[(d['label'],Decimal(d['weight_per_thousand'])/10)for d in chosen],ceiling=15,note='Calculated · published 2024 SIC 2007 weights ÷ 10. Axis 0–15%; finance & insurance is broader than Banking.')
    body+='<div class="analysis-grid"><section><h3>Financial services in context</h3>'+type_text(share)+type_text(estimate)+'<p class="material">Estimated range £211–214bn under a nearest-unit rounding assumption; not a Banking market size.</p></section><section><h3>Growth has a different basis</h3>'+type_text(growth.conclusion)+'<p class="perspective">UK aggregate volume growth is not an industry or enterprise growth rate. The preliminary estimate is subject to revision.</p></section></div>'
    body+='<details class="sector-directory"><summary>All 20 industry labels</summary><ul>'+''.join('<li>'+e(d['label'])+'</li>'for d in b['districts'])+'</ul></details>'
    return body+evidence([total,share,estimate,assumption,growth.conclusion,*growth.facts])


def banking_main(stream,focus,rows):
    if focus=='agenda': return leadership('banking')
    title='The UK Banking ecosystem' if stream=='landscape' else 'Funding conditions meet resilience policy'
    if focus=='regulation':title='Distinct regulatory responsibilities'
    body='<p class="eyebrow">'+('Industry landscape'if stream=='landscape'else'Industry forces')+'</p><h1 id="main-title" tabindex="-1">'+title+'</h1><p class="lead">Banks connect deposits, credit and payments with the wider economy.</p>'
    body+=metrics([('Reported · Bank Rate','4%','Decision ending 4 November 2026'),('Reported · incident-reporting policy','March 2027','Sector policy · entity scope remains specific')])
    body+='<div class="value-chain" aria-label="Conceptual banking value chain"><span>Deposits</span><b aria-hidden="true">→</b><span>Credit &amp; payments</span><b aria-hidden="true">→</b><span>Households &amp; businesses</span></div><p class="chart-note">FLORA Insight · sector functions, not bilateral contracts or quantified value flows.</p>'
    with patch.object(agenda,'date',SnapshotDate):issues=agenda.agenda('banking')
    body+='<div class="analysis-grid"><section><h3>Funding economics</h3>'+type_text(issues[0].conclusion)+'<p class="perspective">No individual bank margin loss or customer demand follows from a rate decision alone.</p></section><section><h3>Supervision and reporting</h3><dl class="roles"><dt>Bank of England</dt><dd>Central-bank and monetary-policy context.</dd><dt>PRA</dt><dd>Prudential supervision; part of the Bank of England.</dd><dt>FCA</dt><dd>Conduct-supervision context, distinct from prudential supervision.</dd></dl><p class="perspective">Policy does not establish a particular entity’s readiness, supplier shortfall or open procurement.</p></section></div>'
    body+='<details><summary>Industry economics and boundaries</summary>'+type_text(uk_values()[2])+'<p>Capital, liquidity, deposit pricing and operating resilience shape banking economics. No current regulatory threshold, enterprise ranking or Porter score is inferred.</p></details>'
    facts=[rows[k]for k in ['UK-RATE-NOV26','UK-PRA-REPORT27','UK-FCA-REPORT27']]
    return body+evidence([*facts,rows['UK-VALUE'],*[r.conclusion for r in issues],uk_values()[2]])


def financial(rows,stream):
    title={'inside':'Customer funding and earnings','landscape':'Customer deposits anchor the funding picture','forces':'Efficiency ambition sits beside current financial scale'}[stream]
    body='<p class="eyebrow">Financial analysis · consolidated Group</p><h1 id="main-title" tabindex="-1">'+title+'</h1><p class="lead">Current balances and reported earnings, alongside the Group’s 2030 efficiency ambition.</p>'
    body+=metrics([('Reported · customer deposits','£502.8bn','30 September 2026 · stock'),('Reported · statutory pretax profit','£6.6bn','9 months to 30 September 2026 · flow')])
    body+=bars('Customer-deposit stocks · Group', [('31 December 2025',Decimal('496.5')),('30 September 2026',Decimal('502.8'))],ceiling=600,unit='bn',note='Reported · GBP billion, linear 0–600bn scale. Two published stocks; composition and transfer effects are not reconciled. No organic-flow claim.')
    body+='<div class="analysis-grid"><section><h3>Efficiency ambition</h3>'+type_text(rows['LBG-A2030-CIR'])+'<p class="material">A 2030 management target, not achieved performance.</p></section><section><h3>Investment discipline</h3>'+type_text(rows['LBG-A2030-INVESTMENT'])+'<p class="perspective">A management plan does not disclose an allocation to an external supplier.</p></section></div><p class="material">Deposits are a stock; statutory pretax profit is a nine-month flow, not an investment allocation. Neither establishes supplier spending capacity.</p>'
    return body+evidence([rows[k]for k in ['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-AR25-DEPOSITS','LBG-A2030-CIR','LBG-A2030-INVESTMENT']])


def technology(rows,stream):
    facts=[rows[k]for k in ['LBG-AR25-COPILOT','LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS','LBG-AI26-REPORTED','LBG-AI26-EXPECTED']]
    hypothesis=policy.Statement('Broader AI adoption could add value within existing platform capabilities.','hypothesis',facts[0].scope,'FY2025 and stated 2026 ambitions',tuple(dict.fromkeys(s for f in facts for s in f.sources)),'repository_interpretation','design_hypothesis_not_canonical',reasoning='Reported licence distribution and an existing platform establish capability, not full adoption or incremental net value. This is a design example of a falsifiable proposition, not a diagnosed customer requirement.',counter_evidence=('Management already reports AI value and describes controls. Existing teams or incumbents may already deliver further adoption; no adoption deficit or external work is established.',),falsifier='Demonstrated full relevant adoption with no additional net benefit, or evidence that an absent platform capability is the dominant constraint, would weaken this proposition.',dependencies=tuple(f.text for f in facts))
    accepted_view(hypothesis)
    title={'inside':'AI capability is already in place','landscape':'An existing technology collaboration','forces':'AI ambitions sit on existing capabilities'}[stream]
    body='<p class="eyebrow">Technology &amp; operations</p><h1 id="main-title" tabindex="-1">'+title+'</h1><p class="lead">Platform availability, licence distribution and realised net benefit are different measures.</p>'
    body+=metrics([('Reported · licence deployment','30,000+','Copilot licences · FY2025'),('Reported · AI contribution','~£50m','Management-reported · FY2025')])
    body+='<section class="editorial-issue"><h3>Existing platform and controls</h3>'+type_text(rows['LBG-ENVOY-GOOGLE'])+type_text(rows['LBG-ENVOY-CONTROLS'])+'</section><section class="editorial-issue"><h3>Benefit realisation</h3>'+type_text(rows['LBG-AI26-EXPECTED'])+'<p class="material">Expected 2026 value is not achieved net benefit, supplier revenue or an external budget.</p>'+type_text(hypothesis)+'<p class="perspective">Existing management responses weaken a generic missing-platform proposition; no additional seller scope is established.</p></section>'
    return body+evidence([*facts,hypothesis])


def lloyds_main(stream,focus,rows):
    if focus=='economics':return financial(rows,stream)
    if focus=='technology':return technology(rows,stream)
    if focus=='agenda':return leadership('lloyds')
    if stream=='inside':return financial(rows,stream)
    if stream=='forces':return leadership('lloyds')
    body='<p class="eyebrow">Enterprise landscape</p><h1 id="main-title" tabindex="-1">An enterprise within a wider ecosystem</h1><p class="lead">Customers, disclosed collaborators and regulators have different roles.</p>'
    body+='<div class="analysis-grid"><section><h3>Technology collaboration</h3>'+type_text(rows['LBG-ENVOY-GOOGLE'])+'<p class="material">An announced collaboration does not disclose contract value, exclusivity, renewal or workshare.</p></section><section><h3>Customer activity</h3>'+type_text(rows['LBG-Q326-DEPOSITS'])+'<p>Household and business scenes are conceptual customer groups, not named customer relationships.</p></section></div><section class="editorial-issue"><h3>Strategic direction</h3>'+type_text(rows['LBG-A2030-PLATFORMS'])+'<p class="perspective">A stated priority does not establish open procurement or an unallocated external scope.</p></section>'
    return body+evidence([rows[k]for k in ['LBG-ENVOY-GOOGLE','LBG-Q326-DEPOSITS','LBG-A2030-PLATFORMS']])


def scene(scope,stream,focus,mode):
    key=scope+'-'+stream
    links=[]
    def add(label,href,x,y,current=False):links.append((label,href+'#main-title',x,y,current))
    if scope=='uk':
        add('Banking',filename('banking','landscape'),30,65)
        add('Economy',filename(scope,stream,'economics'),56,32,focus=='economics')
        add('Leadership Agenda',filename(scope,stream,'agenda'),52,86,focus=='agenda')
    elif scope=='banking':
        add('Lloyds',filename('lloyds','inside'),38,56)
        add('Regulation',filename(scope,stream,'regulation'),49,20,focus=='regulation')
        add('Leadership Agenda',filename(scope,stream,'agenda'),52,85,focus=='agenda')
    else:
        add('Financial scale',filename(scope,stream,'economics'),48,29,focus=='economics')
        add('Technology & AI',filename(scope,stream,'technology'),53,57,focus=='technology')
        add('Leadership Agenda',filename(scope,stream,'agenda'),51,85,focus=='agenda')
    # Same native links in the active responsive subtree. Hidden alternative is
    # display:none, not focusable, and has no duplicate IDs.
    return '<figure class="portrait"><img src="assets/'+key+'-384.webp" srcset="assets/'+key+'-384.webp 384w, assets/'+key+'-768.webp 768w" sizes="(min-width:1000px) 320px, (min-width:700px) 350px, 100vw" width="1024" height="1536" alt="" loading="lazy" decoding="async"><figcaption class="sr-only">Purpose-composed '+e(key.replace('-',' '))+' illustration. Conceptual environments, not actual premises or a quantitative map.</figcaption>'+''.join('<a class="subject" data-subject="'+e(label,quote=True)+'" href="'+href+'" style="--x:'+str(x)+'%;--y:'+str(y)+'%"'+(' aria-current="true"'if current else'')+'>'+e(label)+'</a>'for label,href,x,y,current in links)+'</figure>'


def watermark(kind):
    return '<img class="watermark" src="assets/watermark-'+kind+'.svg" alt="" aria-hidden="true">'


def shell(scope,stream,focus,body,concept=''):
    title,streams,_=SCOPES[scope]
    context = '<a href="uk-landscape.html">UK</a>' if scope!='uk' else '<span>UK</span>'
    if scope in {'banking','lloyds'}:context+='<span aria-hidden="true">/</span>'+('<a href="banking-landscape.html">Banking</a>'if scope=='lloyds'else'<span>Banking</span>')
    if scope=='lloyds':context+='<span aria-hidden="true">/</span><span>Lloyds Banking Group</span>'
    streamnav='<nav class="streams" aria-label="Insight streams">'+''.join('<a id="stream-'+s+'" href="'+filename(scope,s,focus)+'#stream-'+s+'"'+(' aria-current="page"'if s==stream else'')+'>'+s.title()+'</a>'for s in streams)+'</nav>'
    if concept:context='<span>'+e(concept)+' · layout concept</span>';streamnav='<span class="concept-label">Future concept · not available</span>'
    top='<header id="top" data-region="top"><a class="skip" href="#main-title">Skip to intelligence</a><div class="global"><a class="brand" href="uk-landscape.html" aria-label="FLORA UK home">FLORA</a><nav aria-label="Global FLORA"><a href="uk-landscape.html" aria-current="true">Explore</a><span>Offers</span><span>Pipeline</span></nav><span class="identity">Owner <span>· Design preview</span></span></div><div class="context"><nav aria-label="Current scope">'+context+'</nav>'+streamnav+'</div></header>'
    left='<aside id="left" data-region="left" aria-label="Visual exploration"><div class="wide-scene">'+scene(scope,stream,focus,'wide')+'</div><details class="compact-scene"><summary>Explore the scene <span>'+e(LABELS[focus])+'</span></summary>'+scene(scope,stream,focus,'compact')+'</details></aside>'
    kind=concept.lower()if concept else scope+'-'+stream
    return '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>FLORA · '+e(title)+' · '+e(concept or stream.title())+' · VP-1 design</title><link rel="stylesheet" href="assets/design.css"></head><body data-scope="'+scope+'" data-stream="'+stream+'" data-focus="'+focus+'">'+top+left+'<main id="main" data-region="main" aria-labelledby="main-title">'+watermark(kind)+'<article class="workspace">'+body+'</article></main></body></html>\n'


def concepts(rows):
    news='<p class="eyebrow">News · layout concept only</p><h1 id="main-title" tabindex="-1">The story around the enterprise</h1><p class="lead">Selected historical disclosures, not a current news edition.</p><div class="newspaper"><section><time datetime="2026-10-29">Source published 29 October 2026</time><h3>Lloyds reports nine-month performance</h3>'+type_text(rows['LBG-Q326-PROFIT'])+'<p>Statutory pretax profit is a period flow, not a budget allocation.</p></section><section><time datetime="2026-05-01">Source published 1 May 2026</time><h3>Lloyds describes Envoy with Google Cloud</h3>'+type_text(rows['LBG-ENVOY-GOOGLE'])+'<p>Announcement status does not establish deployed effectiveness or new supplier scope.</p></section></div>'+evidence([rows['LBG-Q326-PROFIT'],rows['LBG-ENVOY-GOOGLE']])
    tools='<p class="eyebrow">Tools · layout concept only</p><h1 id="main-title" tabindex="-1">Enterprise Builder</h1><p class="lead">An optional future workspace, with the enterprise context already in place.</p><section class="tool-studio"><h3>Operating-model composition</h3><fieldset disabled><legend>Design-only controls · no model has been run</legend><label>Enterprise<input value="Lloyds Banking Group" readonly></label><label>Perspective<select><option>Operating model</option></select></label><label>Basis<input value="Published reference intelligence" readonly></label></fieldset><div class="tool-output"><span>Organisation</span><span>Operations</span><span>Technology</span></div><p>Illustrative arrangement only. No scenario, financial output, executable action or saved change.</p></section>'
    return {'concept-news.html':shell('lloyds','landscape','overview',news,'News'),'concept-tools.html':shell('lloyds','inside','overview',tools,'Tools')}


def main():
    for name in SOURCE_PATHS:
        if (ROOT/name).read_bytes()!=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT):
            raise ValueError('Dated design source changed; explicit review required')
    data,rows=statements();outputs={};states=[]
    for scope,(_,streams,focuses)in SCOPES.items():
        for stream in streams:
            for focus in focuses:
                body=uk_main(stream,focus)if scope=='uk'else banking_main(stream,focus,rows)if scope=='banking'else lloyds_main(stream,focus,rows)
                name=filename(scope,stream,focus);outputs[name]=shell(scope,stream,focus,body)
                states.append({'file':name,'scope':scope,'stream':stream,'focus':focus})
    outputs.update(concepts(rows));outputs['index.html']=outputs['uk-landscape.html']
    for name,text in outputs.items():(OUT/name).write_text(text)
    (HERE/'Prototype-States.json').write_text(json.dumps({'baseline':BASE,'as_of':AS_OF,'states':states,'concepts':['concept-news.html','concept-tools.html'],'entry':'index.html'},indent=2)+'\n')
    ledger={'baseline':BASE,'as_of':AS_OF,'kind':'Static design export, not a source registry or new intelligence owner','source_owners':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}for p in SOURCE_PATHS],'new_measurements':False,'canonical_mutation':False,'pending_branch_content_incorporated':False,'design_derivatives':{'rounding_estimate':'Existing frozen public ONS extract only; estimated £212bn, conditional £211–214bn rounding range. Assumption is not a published confidence interval. No new ONS import.','hypothesis':'Static illustrative, falsifiable AI-adoption hypothesis over existing merged disclosures, not proven demand or an accepted finding.'}}
    (HERE/'Content-Lineage.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print(str(len(outputs))+' static HTML compositions generated from merged public owners; no domain writes.')


if __name__=='__main__':main()
