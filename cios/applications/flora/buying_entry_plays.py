"""Authored commercial questions over retained candidate facts, never new facts.

The shared matcher chooses whether these bounded plays are admissible. No
ranking, source collection, approvals, customer intent or operational writes.
"""
from copy import deepcopy
from hashlib import sha256
import json

D='tech-strategic-digital-transformation'
A='tech-strategic-ai-first-transformation'
C='tech-strategic-cybersecurity-resilience'
L='tech-strategic-complex-legacy-modernisation'

# required: every retained basis/counter fact must still be admissible at cutoff.
# positive: these facts must also survive the matcher's decay/closure rules.
PLAYS = {
 (D,'santander-uk'): {
  'required':['BTI-TSB-MIGRATION','BTI-TSB-LEGAL'], 'positive':['BTI-TSB-MIGRATION'],
  'conversation':'For Santander UK, use the 10 November transfer announcement to ask which customer-service outcomes would need protecting if the conditional H2 2027 migration proceeds, while Santander UK and TSB remain separate legal entities.',
  'diagnostic':'If the programme owner confirms an unresolved service question, offer a customer-journey continuity diagnostic: choose one owner-identified journey, map pre/post-transfer responsibilities and exception handling, and agree service acceptance measures. Confirm the relevant entity and permission before reviewing any customer information.',
  'question':'Which customer journey has an unresolved outcome or accountable benefits owner beyond the existing integration plan, and could the internal programme close it without external help?',
  'stop':'Stop if the conditional plan changes, the existing integration team already owns and resolves the journey, or no authorised external diagnostic scope is confirmed.'},
 (D,'lloyds'): {
  'required':['BTI-LBG-STRATEGY','LBG-AR25-MIGRATION'], 'positive':['BTI-LBG-STRATEGY'],
  'conversation':'For Lloyds, ask how the service outcomes of the existing migration priorities would be carried into Accelerate 2030 preparation described on 29 October, rather than proposing another technology roadmap.',
  'diagnostic':'If an accountable business owner identifies a remaining gap, propose a benefits-continuity diagnostic for one migration-linked service: trace the intended customer outcome to process hand-offs, adoption measures and post-change ownership; separate existing delivery commitments from decisions still open.',
  'question':'Is there an evidenced service or adoption gap between current migration delivery and the next strategy phase, or do existing benefits owners and delivery plans already cover it?',
  'stop':'Stop if no residual outcome gap is established; a future strategy phase alone is not a new change mandate or supplier invitation.'},
 (D,'computacenter'): {
  'required':['BTI-CC-SERVICE','BTI-CC-CRM'], 'positive':['BTI-CC-SERVICE'],
  'conversation':'For Computacenter, start from the 8 September distinction between the completed CRM rollout and the service-management upgrade under way: ask whether any business-service hand-off remains unresolved, rather than pitching a fresh CRM implementation.',
  'diagnostic':'Only if the owner confirms such a hand-off, propose a service-transition diagnostic for one selected workflow: test CRM-to-service ownership, exception routing and acceptance measures against the upgrade plan. First establish the relevant business unit and UK workshare; the group disclosure does not supply either.',
  'question':'Does the service-management upgrade leave a demonstrable workflow or ownership gap after CRM completion, and is it outside existing internal or incumbent delivery scope?',
  'stop':'Stop if the upgrade already resolves the workflow, or UK/entity scope and permission for outside work cannot be confirmed.'},
 (D,'bt'): {
  'required':['BTI-BT-TRANSFORM'], 'positive':['BTI-BT-TRANSFORM'],
  'conversation':'For BT, use the 5 November report of continuing simplification and modernisation to ask which customer-service outcome, if any, still crosses unresolved organisational or process boundaries within the existing transformation programme.',
  'diagnostic':'If a continuing-operations owner identifies a gap, offer a simplification decision diagnostic: select one service, map process and responsibility boundaries, compare removing steps with adding technology, and define a customer acceptance measure. Establish UK workshare and already committed delivery before any proposal.',
  'question':'Can a confirmed continuing-operations service owner show a residual problem that process simplification and BT\'s current transformation teams cannot already resolve?',
  'stop':'Stop if no distinct residual outcome is evidenced or the work is already owned; reported modernisation is not proof of an external delivery requirement.'},
 (D,'natwest'): {
  'required':['BTI-NWG-SIMPLIFY'], 'positive':['BTI-NWG-SIMPLIFY'],
  'conversation':'For NatWest, ask where the structural simplification and platform investment reported on 30 October still needs a business-service decision: which customer outcome would demonstrate simplification beyond a platform milestone?',
  'diagnostic':'If a benefits owner identifies a service with unresolved cross-functional hand-offs, propose an outcome-to-investment diagnostic: map the service outcome to platform dependencies, process changes and benefits accountability; compare a process-only intervention with further technology change. Treat any candidate workflow as a question, not a discovered defect.',
  'question':'Is there an attributable customer-service or benefits-accountability gap outside the current simplification plan, or would the existing plan deliver the same outcome?',
  'stop':'Stop if current teams already cover the outcome, or no separately authorised diagnostic scope exists.'},
 (A,'lloyds'): {
  'required':['BTI-LBG-AI-SCALE'], 'positive':['BTI-LBG-AI-SCALE'],
  'conversation':'For Lloyds, distinguish the AI-use-case expansion reported on 29 October from an AI-first operating-model mandate: ask whether any named-by-the-owner process is actually being redesigned across roles, controls and adoption, rather than merely gaining another AI tool.',
  'diagnostic':'If process redesign is confirmed, propose a process-and-role diagnostic for one owner-selected use case: compare the non-AI baseline with the proposed workflow, identify human decision and exception responsibilities, and test control, adoption and cost assumptions. No new model build or access to customer data is implied.',
  'question':'Is enterprise process and role redesign genuinely in scope, and what evidence would show that a non-AI change or the existing AI team is sufficient?',
  'stop':'Stop at Research only if this remains point-tool expansion; an unconfirmed external role or available budget cannot be assumed.'},
 (C,'computacenter'): {
  'required':['BTI-CC-CYBER'], 'positive':['BTI-CC-CYBER'],
  'conversation':'For Computacenter, acknowledge the cybersecurity-framework investment reported on 8 September and ask whether its current assurance plan leaves any owner-confirmed critical-service question; do not begin with an assertion that controls are missing.',
  'diagnostic':'Only with the security and service owners\' permission, propose an assurance-coverage diagnostic: choose one critical service, map the existing framework evidence and recovery/response responsibilities, and identify whether any test is actually uncovered. Confirm group versus UK scope and incumbent responsibilities before considering independent assurance.',
  'question':'Is there a specific assurance question that existing internal or incumbent tests do not answer, or does the current framework investment already provide sufficient evidence?',
  'stop':'Stop if existing assurance closes the question, or no authorised independent scope is established; framework investment alone does not show a control failure.'},
 (L,'santander-uk'): {
  'required':['BTI-TSB-MIGRATION','BTI-TSB-LEGAL'], 'positive':['BTI-TSB-MIGRATION'],
  'conversation':'For Santander UK, ask which estate-transition decisions would remain open under the conditional H2 2027 migration described on 10 November; keep the separate Santander UK and TSB entities explicit and avoid treating the transfer as approved.',
  'diagnostic':'If the authorised integration owner identifies an undecided dependency, offer a migration-treatment diagnostic: map one service\'s interfaces, reconciliation, vendor/licence rights and continuity gates; compare retain, upgrade and retire options and ask what rollback evidence each requires. Do not assume a cloud move, rewrite or vacant supplier role.',
  'question':'Which dependency or reconciliation decision is still open beyond the existing integration plan, and could retention or a supported upgrade remove the constraint with less transition risk?',
  'stop':'Stop if the transfer conditions or programme direction change, decisions are already resolved, or entity authority and external scope are not established.'},
 (L,'lloyds'): {
  'required':['LBG-AR25-MIGRATION'], 'positive':['LBG-AR25-MIGRATION'],
  'conversation':'For Lloyds, revisit the annual-report migration priorities as structural context, not a new event: ask which estate-treatment or service-continuity decision, if any, remains unresolved in the current programme.',
  'diagnostic':'If a residual decision is confirmed, propose a legacy-treatment diagnostic for one owner-selected service: map multi-vendor dependencies, support and licence obligations, reconciliation and rollback needs; compare retaining or upgrading with retiring or replacing. Reconfirm current status before discussing delivery.',
  'question':'Does the migration programme still contain an unresolved continuity or treatment decision, or do existing teams and supported upgrade paths already remove the constraint?',
  'stop':'Stop if the historical priority is complete or no residual decision exists; an annual-report priority is neither new procurement nor available supplier scope.'},
 (L,'computacenter'): {
  'required':['BTI-CC-ERP'], 'positive':['BTI-CC-ERP'],
  'conversation':'For Computacenter, start with the existing ERP-to-cloud-version design work reported on 8 September: ask which upgrade, interface or transition decision is still genuinely undecided, rather than pitching wholesale ERP replacement.',
  'diagnostic':'If the ERP owner confirms a remaining design choice, propose an upgrade-design diagnostic: compare the supported upgrade with selective retention or replacement, trace one critical interface and data-reconciliation path, and review vendor rights, dual-run and rollback assumptions. Establish the legal entity, UK workshare and incumbent design responsibilities first.',
  'question':'Is an ERP interface, rights or transition decision still open and outside existing design ownership, or is the supported upgrade already sufficient?',
  'stop':'Stop if the design is settled or existing teams cover it; group ERP design work does not establish a UK external modernisation purchase.'}
}

REVISION=sha256(json.dumps([[list(k),v] for k,v in sorted(PLAYS.items())],sort_keys=True,separators=(',',':')).encode()).hexdigest()


def resolve(offer_id, enterprise_slug, facts, positive_ids):
    """Return authored questions only while every cited basis remains available."""
    play=PLAYS.get((offer_id,enterprise_slug))
    by_id={f['id']:f for f in facts}
    if not play or not set(play['required'])<=by_id.keys() or not set(play['positive'])<=set(positive_ids):
        return None
    result=deepcopy(play)
    result.update(revision=REVISION,classification='Evidence-led conversation hypothesis; not customer demand or agreed scope',
        evidence=[{'fact_id':i,'source_id':by_id[i]['source_id'],'publication_date':by_id[i]['publication_date'],
                   'last_verified':by_id[i]['last_verified'],'source_url':by_id[i]['source_url']} for i in play['required']])
    return result
