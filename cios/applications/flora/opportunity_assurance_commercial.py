"""Business-language presentation only; no new influence score or matching policy.

Historical assessment results stay unchanged. A future versioned influence-window
model belongs to #604. These are questions and cautions, not customer demand.
"""
TSB_URL='https://www.tsb.co.uk/news-releases/Santander-UK-and-TSB-apply-to-transfer-the-TSB-business-to-Santander-UK.html'
TSB_NOTE={
 'published':'2026-11-10','reviewed':'2026-11-14','locator':'Announcement paragraphs 1–4; notes to editors',
 'url':TSB_URL,'authority':'Presentation context only; no historical research record changed',
 'context':'The 10 November update follows the acquisition completed on 30 April 2026. It concerns a proposed legal transfer and conditional customer migration in H2 2027; the banks remain separate legal entities.',
 'warning':'A significant integration is under way. The early strategy-setting window may have passed. This announcement does not establish an early strategic sales opportunity, open procurement, unallocated external scope or an opportunity to shape. Remaining needs or future phases may exist, but are unconfirmed.'}


def summary(assessment):
    b=assessment['buying_trigger'];slug=assessment['enterprise_slug'];dimension=b['dimension']
    result={'customer':assessment['enterprise_name'],'outcome':'Investigate customer need',
        'challenge':'A business need still needs to be established with the customer.',
        'influence':'Unknown. A public update does not show which decisions remain open.',
        'next_action':'Find a permitted customer route and test whether a material, unresolved need exists.',
        'uncertainty':'Customer need, access and available work are unconfirmed.',
        'value':'Value is unquantified. Establish the customer outcome, baseline and cost of change first.',
        'context':'Public information informs a conversation; it does not confirm a buying decision.'}
    if b['tier']=='Research only':
        result.update(outcome='Research only',challenge='No current customer need is established for this Offer.',
            influence='Not established. There is no basis here to claim an open opportunity.',
            next_action='Research the customer problem before proposing a programme.',
            uncertainty='Whether there is any relevant unmet need at all.')
    if slug=='santander-uk' and any(f['id']=='BTI-TSB-MIGRATION' for f in b['timeline']):
        result.update(outcome='Programme under way · timing uncertain',context=TSB_NOTE['context'],
            influence='Uncertain and potentially late. '+TSB_NOTE['warning'],
            uncertainty='Which material decisions, residual work or future phases remain open—and whether an external seller could help.')
        if dimension=='business_service':
            result.update(challenge='Could a remaining customer-service or ownership gap affect the integration?',
                next_action='Ask an authorised programme contact which customer-journey decisions remain unresolved beyond the existing integration plan.',
                value='Potential service continuity and fewer customer hand-off failures; residual need and value remain unconfirmed.')
        elif dimension=='estate':
            result.update(challenge='Could an unresolved dependency or reconciliation decision affect migration continuity?',
                next_action='Check which estate-treatment, vendor-rights or rollback decisions remain open; compare retention or a supported upgrade with further change.',
                value='Potential continuity and avoidable transition-cost benefits; no additional work or financial value is established.')
    elif slug=='lloyds' and dimension=='enterprise_ai' and b['tier']!='Research only':
        result.update(challenge='Does AI expansion involve a business-process or role change that still needs help?',
            next_action='Ask whether a customer-owned process is genuinely being redesigned; compare the non-AI alternative before suggesting a diagnostic.',
            uncertainty='Whether this is enterprise change, an existing team’s use-case expansion, or a need for outside help.',
            value='Potential process and adoption improvements; no savings or customer baseline is confirmed.')
    elif slug=='computacenter' and dimension=='security':
        result.update(challenge='Is any assurance question left unanswered by the existing cybersecurity framework?',
            next_action='Check whether internal teams or current suppliers already provide the assurance needed. Establish the relevant business and permission before discussing a review.',
            uncertainty='An assurance gap, external scope and the relevant UK business are unconfirmed.',
            value='Potential assurance of a critical service; existing controls may already be sufficient.')
    elif dimension=='social_value':
        result.update(outcome='Research only',challenge='No specific unmet social-value or ESG need is established.',
            next_action='Look for a customer-owned outcome and missing measure; do not infer demand from broad ESG commitments.',
            uncertainty='Whether there is a real problem beyond existing plans and achieved results.')
    if b['tier']=='Research only':
        result['outcome']='Research only'
        if not b['shortlist_eligible']:
            result['next_action']='Keep this as account context. Respect the current customer and Offer restrictions before considering a sales action.'
    return result
