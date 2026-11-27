"""Reproduce finite review annotations over #735, not a runtime research store.

Original notes, source identities and crosswalk records remain immutable. These
annotations record human source inspection; this script cannot perform or grant
source verification, publisher permission, admission, canonical acceptance or
publication. No original-document bytes or fabricated byte digests are stored.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = 'c7122f89f56871685772767eab207fd93b7550ce'
MAIN = '0a6423fe3a32d0a0d5d11fe9d7027859e94c6df7'
PACK = 'docs/research/lloyds-intelligence-recovery/'
DAY = '2026-11-26'


def original(name):
    return json.loads(subprocess.check_output(['git', 'show', BASE + ':' + PACK + name], cwd=ROOT))


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


# A source ID here is an annotation reference, NOT a CIOS Source registry ID.
SOURCES = {
 'CH-BANK': ('https://find-and-update.company-information.service.gov.uk/company/00002065/persons-with-significant-control', None, 'Registry page returned via web connector; corporate fields only', 'turn160view0', 'Corporate number and active corporate PSC; filed information not independently guaranteed'),
 'CH-HBOS': ('https://find-and-update.company-information.service.gov.uk/company/SC218813/persons-with-significant-control', None, 'Registry page returned via web connector; corporate fields only', 'turn160view1', 'Corporate PSC; not a complete legal ownership tree'),
 'CH-WIDOWS': ('https://find-and-update.company-information.service.gov.uk/company/03196171', None, 'Registry page returned via web connector', 'turn159view2', 'Number and previous registered name, not brand or trading-history equivalence'),
 'CH-GROUP': ('https://find-and-update.company-information.service.gov.uk/company/SC095000', None, 'Registry page returned via web connector', 'turn165view0', 'Group corporate identity, not a production canonical/workspace binding'),
 'TPR-LIST': ('https://www.thepensionsregulator.gov.uk/en/master-trust-pension-schemes/list-of-authorised-master-trusts', None, 'Regulator list returned via web connector', 'turn177view3', 'List observation is not authorisation date, scheme asset measure or company identity'),
 'TPR-GUIDE': ('https://www.thepensionsregulator.gov.uk/en/document-library/scheme-management-detailed-guidance/winding-up-or-transferring-a-scheme-detailed-guidance/transferring-to-a-master-trust-smaller-defined-contribution-schemes', '2026-03-31', 'Original guidance and dated update history', 'turn175view1', '6 May inclusion is the smaller-scheme enquiries list; latest displayed update 6 July 2026'),
 'GEC': ('https://www.lloydsbankinggroup.com/who-we-are/group-overview/group-executive-committee.html', None, 'Issuer current roster and biographies', 'turn158view2 / turn168view0', 'Undated live page; does not prove its historical 14/22 November contents or delegated buying powers'),
 'BRANDS': ('https://www.lloydsbankinggroup.com/who-we-are/our-brands.html', None, 'Issuer brand page and dated transition statement', 'turn180view0 L615-L640', 'Halifax change starts 1 July 2026; no completed migration, legal rename or changed segment allocation inferred'),
 'INVESTORS': ('https://www.lloydsbankinggroup.com/investors.html', None, 'Issuer governance summary', 'turn173view0 L796-L800', 'Alternative locator supports committee reporting; ignore unrelated financial headlines for this claim'),
 'CONDON': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds/lloyds-appoints-natasha-condon-global-head-transaction-banking.html', '2026-11-18', 'Issuer dated announcement', 'turn158view0 L598-L623', 'Reporting line/remit are disclosed; delegation, sourcing decisions and budget are not'),
 'MORTON': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds/fiamma-morton-appointment.html', '2026-08-12', 'Issuer dated announcement', 'turn162view0 L598-L617', 'Appointment disclosure is not effective authority or a procurement invitation'),
 'FITZGERALD': ('https://www.lloydsbankinggroup.com/media/press-releases/2025/lloyds-banking-group-2025/peter-fitzgerald-appointed.html', '2025-12-10', 'Issuer historical announcement', 'turn162view1 L598-L615', 'Historic appointment/remit; do not assume November delegation or unchanged organisation'),
 'AI-ROLES': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/1000-new-ai-roles.html', '2026-06-22', 'Issuer workforce plan', 'turn162view2 L598-L623', 'Planned roles and an apprenticeship are not incremental realised FTE or measured benefits'),
 'MS-ISSUER': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/microsoft-365-frontier-suite.html', '2026-06-04', 'Issuer dated announcement', 'turn162view3 L604-L614', 'Issuer itself also reports engineering deployment; licences, active licensed users and engineers remain different populations'),
 'MS-SUPPLIER': ('https://ukstories.microsoft.com/features/lloyds-banking-group-rolls-out-microsoft-365-frontier-suite-to-power-its-agentic-future/', '2026-06-04', 'Interested supplier original announcement', 'turn162view4 / turn163view0', 'Supplier corroboration is not independent proof of realised productivity, price or contract scope'),
 'ARIBA': ('https://www.lloydsbankinggroup.com/who-we-are/working-with-suppliers/faqs.html', None, 'Issuer supplier process', 'turn167view0 L636-L640', 'Registration follows sourcing contact; it is not an unsolicited invitation or a known tender'),
 'SOURCING': ('https://www.lloydsbankinggroup.com/who-we-are/working-with-suppliers/responsible-sourcing-supplier-management.html', None, 'Issuer supplier expectations', 'turn167view1 L607-L615', 'Applicable policies and FSQS expectations do not establish a particular contract or performance'),
 'SPROUT': ('https://www.lloydsbankinggroup.com/media/press-releases/2025/scottish-widows-2025/scottish-widows-turns-to-ai-to-speed-up-protection-insurance-cla.html', '2025-06-05', 'Issuer historical trial announcement', 'turn167view2 L598-L623', 'Trial/expected outcomes do not demonstrate production effectiveness or current supplier terms'),
 'FCA-LIVE': ('https://www.fca.org.uk/news/press-releases/fca-announces-second-cohort-ai-live-testing', '2026-04-21', 'Regulator original announcement', 'turn159view0 L262-L286', 'First cohort is retrospective in note 8; second-cohort selection/testing is distinct; no company-specific outcomes'),
 'FCA-SANDBOX': ('https://www.fca.org.uk/news/press-releases/anthropic-supercharged-sandbox', '2026-07-22', 'Regulator original announcement', 'turn159view1 L263-L288', 'Sandbox experimentation is not live-market adoption or a Lloyds contract with every programme supplier'),
 'GCA': ('https://redirect-b.webprod.crowncommercial.gov.uk/suppliers/1183/lloyds-bank-plc', None, 'Official page found in search index; direct open returned 502', 'turn170search0 / turn169view2', 'Cached official listing supports historical supplier direction; current listing not freshly retrieved'),
 'COUNCIL': ('https://glostext.gloucestershire.gov.uk/ieDecisionDetails.aspx?ID=1741', '2021-09-28', 'Official decision indexed in search; direct open returned 403', 'turn170search3 / turn169view3', 'Decision 14 September; publication 28 September; five-year service from October 2021; no renewal inference'),
 'IPSOS': ('https://www.ipsos.com/en-uk/business-banking-service-quality-great-britain', '2026-08-17', 'Original survey methodology and linked PDF', 'turn169view0 / turn175view0', 'GB SME recommendation, July 2025-June 2026; extracted PDF loses named chart row alignment'),
 'STARLING': ('https://www.starlingbank.com/business-account/business-service-quality-survey-results/', '2026-08', 'Bank publication of independently commissioned survey', 'turn169view1 L17-L43', 'Text alternatives support Monzo/Starling results; do not independently verify the Lloyds chart row'),
 'FCA-MOTOR': ('https://www.fca.org.uk/firms/information-firms-motor-finance-complaints', '2024-01-24', 'Regulator page with dated updates', 'turn168view3', 'Latest update 26 November 2026; 26 October hearing extension is not a firm payment deadline'),
 'FCA-AI': ('https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services', '2026-10-19', 'Regulator original guidance', 'turn170view0 L260-L295', 'Updated 20 October; general obligations are not a demonstrated Lloyds control failure'),
 'BOE-SEP': ('https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026', '2026-09-17', 'Central-bank original decision/minutes', 'turn166view0 L4-L7', 'Meeting ended 16 September; publication 17 September; external context, not firm-specific economics'),
 'BOE-NOV': ('https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/november-2026', '2026-11-05', 'Central-bank original decision/minutes', 'turn166view1 L8-L11', 'Meeting ended 4 November; publication 5 November; do not use one as the other'),
 'PRA-CLIMATE': ('https://www.bankofengland.co.uk/prudential-regulation/publication/2025/december/enhancing-banks-and-insurers-approaches-to-managing-climate-related-risks-ss', '2025-12-03', 'PRA original supervisory summary', 'turn166view2', 'Proportionate expectations; exact entity applicability and material failure not inferred'),
 'SKILLS': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/lloyds-banking-group-to-invest-100-million-in-future-skills.html', '2026-08-20', 'Issuer programme announcement', 'turn167view3', 'Plan, not realised spending, results or an external delivery allocation; amount excluded from presentation candidate'),
 'H126': ('https://www.sec.gov/Archives/edgar/data/1160106/000116010626000022/lyg-20260630.htm', '2026-07-30', 'Original issuer-filed SEC text', 'turn163view3 / turn164view2 / turn177view2', 'H1 segment/APM scope; SEC hosting is not endorsement or Source admission; no numerical output activated'),
 'FY25': ('https://www.sec.gov/Archives/edgar/data/1160106/000116010626000010/lyg-20251231_d2.htm', '2026-02-13', 'Original issuer-filed SEC text', 'turn168view1 / turn178view2', 'As-filed date; principal interests at 31 December 2025; indirect does not specify intermediate parent'),
 'Q326': ('https://www.lloydsbankinggroup.com/assets/pdfs/investors/financial-performance/lloyds-banking-group-plc/2026/q3/2026-lbg-q3-ims.pdf', '2026-10-29', 'Original issuer PDF text inspected through web connector', 'turn168view4 P7', 'Nine months, operating costs versus total costs and quarter/year movements remain separate; held output unchanged'),
 'ENVOY-PDF': ('https://www.lloydsbankinggroup.com/assets/pdfs/media/press-releases/2026-press-releases/lloyds-banking-group/260428-lbg-unveils-envoy.pdf', '2026-04-28', 'Original dated issuer PDF text', 'turn164view4 P0', 'PDF date differs from HTML publication, not proof of a second launch'),
 'ENVOY-HTML': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/lloyds-banking-group-unveils-envoy.html', '2026-05-01', 'Original issuer HTML text', 'turn158view1 L604-L634', 'Platform/controls/collaboration are issuer assertions, not independently measured effectiveness or executed contract scope'),
 'AI-VALUE': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/ai-driven-benefits-2026.html', '2026-01-29', 'Original issuer announcement', 'turn164view0', 'Reported prior-year value versus current-year expectation, not independently verified net benefit or supplier budget'),
 'FRAUD': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/lloyds-banking-group-deploys-agentic-ai-to-strengthen-real-time-.html', '2026-06-08', 'Original issuer operating-use announcement', 'turn172view0 L608-L628', 'Issuer links Envoy to fraud colleague support; Scam Check was prospective in this announcement'),
 'EXPORT': ('https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds/ai-tool-to-recover-trading-days-uk-exporters.html', '2026-11-11', 'Original issuer product announcement', 'turn178view0 L604-L623', 'Export Assist is attributed to TradeSpeed/Complidata; SME sponsor is not proof of CIB ownership, a full contract or supplier scope'),
 'GOOGLE': ('https://cloud.google.com/blog/products/ai-machine-learning/welcome-to-gemini-at-work-2026', '2026-10-08', 'Original interested supplier publication', 'turn174view2 L217 / turn172view2', 'Supplier-described Envoy use/population; no general Gemini features or namesake Envoy proxy dependencies inherited by Lloyds'),
 'LBG-TERMS': ('https://www.lloydsbankinggroup.com/site-terms-and-conditions.html', '2010-06-01', 'Current displayed terms, last-change date as stated', 'turn160view4 L598-L652', 'Material applicability of section 2 remains an existing-owner decision; section 5 homepage condition retained'),
}

# One disposition per recovered note; no wholesale copy of earlier claim tables.
# States describe support of the proposition, not canonical or publication status.
REVIEWS = {
 'F01': ('registry_supported_as_returned', ['CH-BANK'], 'Registration and corporate PSC supported; no historical-page snapshot for 22 November.'),
 'F02': ('registry_supported_as_returned', ['CH-HBOS'], 'Corporate PSC supported; no complete ownership chain inferred.'),
 'F03A': ('registry_supported_as_returned', ['CH-WIDOWS'], 'Corrected corporate number supported.'),
 'F03B': ('historical_registry_supported', ['CH-WIDOWS'], 'Previous registered name period supported; not business continuity.'),
 'F04': ('regulator_supported_date_qualified', ['TPR-LIST', 'TPR-GUIDE'], 'Authorised listing and 6 May enquiries-list update are distinct events.'),
 'F05A': ('issuer_attributed_dated_role', ['GEC'], 'Biography supports February 2026 start; present role observed on retrieval.'),
 'F05B': ('issuer_attributed_announcement', ['MORTON'], 'Dated appointment announcement supported; delegation unknown.'),
 'F06A': ('issuer_attributed_dated_role', ['GEC'], 'Biography supports March 2026 CIB start.'),
 'F06B': ('issuer_attributed_announcement', ['CONDON'], 'Remit and stated reporting line supported; open external scope not established.'),
 'F07': ('issuer_attributed_dated_role', ['GEC'], 'October grouping supported; no retrospective segment restatement.'),
 'F08A': ('historical_label_not_current_confirmed', ['GEC', 'FITZGERALD'], 'IP&I title appears in December 2025 announcement; current roster says Wealth & Insurance. Exact 22 November page unavailable.'),
 'F08B': ('historical_issuer_announcement', ['FITZGERALD'], 'Historical appointment/remit supported, not current delegation.'),
 'F08C': ('issuer_attributed_current_role', ['GEC'], 'Current Scottish Widows role supported; legal company/brand/trust remain separate.'),
 'F09': ('issuer_attributed_dated_role', ['GEC'], 'Biography supports September 2026 start; no programme decision powers inferred.'),
 'F10A': ('issuer_attributed_plan', ['AI-ROLES'], 'Planned roles are not completed hiring or incremental external delivery demand.'),
 'F10B': ('issuer_attributed_plan', ['AI-ROLES'], 'Apprenticeship announcement supported; not qualification/outcome completion.'),
 'F11A': ('issuer_and_supplier_attributed', ['MS-ISSUER', 'MS-SUPPLIER'], 'Company-wide announced scope supported; not measured deployment completeness.'),
 'F11B': ('supplier_attributed_corroborated_by_issuer', ['MS-SUPPLIER', 'MS-ISSUER'], 'Engineering agreement/deployment is also reported in issuer body, not only supplier evidence.'),
 'F12': ('issuer_attributed_process', ['ARIBA'], 'Ariba process supported; supplier participation is not a tender invitation.'),
 'F13': ('historical_issuer_trial', ['SPROUT'], 'Claims/underwriting trial supported; live effectiveness and terms remain unverified.'),
 'F14A': ('regulator_retrospective_cohort', ['FCA-LIVE'], 'First-cohort participant appears in retrospective note 8; April date is the release date, not that cohort start.'),
 'F14B': ('regulator_announcement_supported', ['FCA-LIVE'], 'Second-cohort selection supported with distinct participant wording.'),
 'F15': ('regulator_announcement_supported', ['FCA-SANDBOX'], 'Separate experimentation programme supported, not live-market rollout.'),
 'F16': ('official_search_support_current_unverified', ['GCA'], 'Official indexed listing corroborates bank-as-supplier direction; direct retrieval failed 502.'),
 'F17': ('historical_official_search_support', ['COUNCIL'], 'Historical award supported by official index; direct open 403. No renewal/current term conclusion.'),
 'F18': ('partial_chart_identity_unverified', ['IPSOS', 'STARLING'], 'Survey wave/definition and Monzo/Starling values supported; extracted PDF does not map named Lloyds row. Do not release its 60% without row verification.'),
 'F19': ('regulator_update_supported', ['FCA-MOTOR'], '26 October hearing extension supported; not firm-specific liability or deadline.'),
 'F20': ('regulator_guidance_date_qualified', ['FCA-AI'], 'First publication 19 October, update 20 October; not proof of Lloyds deficiency.'),
 'F21A': ('regulator_external_actor_supported', ['FCA-LIVE'], 'Go-Cardless programme participant, not a Lloyds supplier/customer relationship.'),
 'F21B': ('regulator_external_actor_supported', ['FCA-SANDBOX'], 'TrueLayer programme participant, not a Lloyds relationship.'),
 'F22': ('issuer_and_supplier_attributed', ['MS-SUPPLIER', 'MS-ISSUER'], 'Issuer also includes engineering deployment; denominator is not M365 licence population or value.'),
 'F23A': ('official_decision_publication_separated', ['BOE-SEP'], 'Meeting ended 16 September, published 17 September; decision substance supported.'),
 'F23B': ('official_decision_publication_separated', ['BOE-NOV'], 'Meeting ended 4 November, published 5 November; do not call 4 November publication.'),
 'F24': ('regulator_expectations_supported', ['PRA-CLIMATE'], 'Scope and themes supported; no bank-specific materiality or non-compliance finding.'),
 'F25': ('issuer_attributed_plan', ['SKILLS'], 'Programme supported as a plan; amount omitted from presentation candidate.'),
 'F26A': ('issuer_attributed_current_role', ['GEC'], 'Roster role supported; exact historic observation snapshot not re-created.'),
 'F26B': ('issuer_attributed_current_role', ['GEC'], 'Roster role supported; not a verified buyer mandate.'),
 'F26C': ('issuer_attributed_current_role', ['GEC'], 'Roster role supported; no private authority inferred.'),
 'F26D': ('issuer_statement_locator_corrected', ['INVESTORS'], 'Committee reporting is supported in investor summary, not found in cited roster intro; locator corrected.'),
 'F27': ('issuer_attributed_policy', ['SOURCING'], 'Supplier standards supported; no particular contract or actual compliance finding.'),
 'R2-OBS-RETAIL-PRICE': ('historical_issuer_financial_source_held', ['H126'], 'Matched H1 Retail narrative supported; no organic Group flow inference.'),
 'R2-OBS-RETAIL-LEASE': ('historical_issuer_financial_source_held', ['H126'], 'Fleet/mix/used-car mechanism and mitigation supported; not leasing profit or margin.'),
 'R2-OBS-CREDIT-EXPLAIN': ('historical_issuer_financial_source_held', ['H126'], 'Model/normalisation/growth and prior comparator supported; stable credit is counter-evidence.'),
 'R2-OBS-IP-DIVIDEND': ('historical_issuer_financial_source_held', ['H126'], 'Distribution, deferred-profit stock and release are different measures; no new output.'),
 'R2-OBS-PRIMARY-SUBS': ('historical_issuer_legal_interests', ['FY25'], 'Direct/indirect principal interests supported at year-end; not current full hierarchy.'),
 'R2-OBS-MS-ADOPTION': ('issuer_attributed_denominators_separated', ['MS-ISSUER', 'MS-SUPPLIER'], 'All retained populations also appear in issuer announcement; correct any supplier-only implication in prior recovery annotation.'),
 'R2-OBS-ENVOY-DATE': ('issuer_publication_versions_supported', ['ENVOY-PDF', 'ENVOY-HTML'], '28 April PDF and 1 May HTML supported; one announcement, not two platform deployments.'),
 'R2-OBS-AI-VALUE': ('issuer_actual_claim_and_expectation_separated', ['AI-VALUE'], 'Company-reported prior contribution versus expectation supported; net method/costs not verified.'),
 'R2-OBS-INVESTMENT': ('historical_issuer_financial_source_held', ['Q326'], 'Narrative includes growth/inflation/Lloyds Wealth and offsets; not unallocated external budget.'),
}


def build():
    notes = original('Recovery.json')['records']
    dispositions = []
    for row in notes:
        key = row['original_refs'][0].split(':', 1)[1]
        state, refs, delta = REVIEWS[key]
        dispositions.append({'recovery_id': row['id'], 'original_record_sha256': fingerprint(row),
            'disposition': state, 'reviewed_source_refs': refs, 'review_delta': delta,
            'original_period': row['period'], 'entity_scope': row['entity'],
            'information_type': 'reported_candidate',
            'assurance_limit': 'Support review is not independent issuer-performance verification or canonical acceptance',
            'source_bytes_verified': False, 'new_source_permission': False,
            'canonical_acceptance': False, 'production_admission': False})
    entries = original('Entity-Crosswalk.json')['entries']
    crosswalk = []
    for i, row in enumerate(entries, 1):
        kind = row['kind']
        if kind == 'group_legal_identity': state, refs = 'registry_identity_supported', ['CH-GROUP']
        elif kind == 'legal_entity': state, refs = 'historical_principal_interest_supported', ['FY25']
        elif kind == 'reporting_segment': state, refs = 'historical_segment_supported', ['H126']
        elif kind == 'professional_role': state, refs = 'current_role_supported_historic_snapshot_unverified', ['GEC']
        elif kind == 'dated_management_or_brand_context':
            note = next(r for r in dispositions if r['recovery_id'] == row['record_ref'])
            state, refs = note['disposition'], note['reviewed_source_refs']
        elif row['name'] == 'Halifax': state, refs = 'issuer_rebrand_in_progress_no_legal_rename_inferred', ['BRANDS']
        else: state, refs = 'brand_role_not_corporate_identity', ['BRANDS', 'GEC', 'CH-WIDOWS']
        crosswalk.append({'crosswalk_entry': i, 'original_record_sha256': fingerprint(row),
            'kind': kind, 'disposition': state, 'reviewed_source_refs': refs,
            'canonical_id_resolved': False, 'workspace_id_resolved': False,
            'caveat': 'Dated reporting/management/brand/legal axes remain separate; no delegated buying authority or retrospective page reconstruction.'})
    sources = [{'review_ref': key, 'original_url': u, 'publication_date': None if key == 'LBG-TERMS' else d,
                'stated_terms_last_changed_on': d if key == 'LBG-TERMS' else None,
                'last_updated_on': {'FCA-MOTOR': '2026-11-26', 'FCA-AI': '2026-10-20',
                    'TPR-GUIDE': '2026-07-06'}.get(key),
                'date_basis': 'SEC as-filed date' if key == 'FY25' else 'Displayed publisher date where supplied; null if not established',
                'currency_qualification': 'Inspected on review day through connector; exact current HTTP byte revision and historic page versions unverified',
                'inspection_method': method, 'inspection_locator': locator,
                'material_limit': limit, 'retrieved_on': DAY,
                'original_bytes_sha256': None, 'publisher_byte_archive_created': False,
                'source_use_authority_changed': False,
                'rights_disposition': ('Existing Lloyds material section 2 applicability and section 5 limits retained'
                    if 'lloydsbankinggroup.com' in u else 'Factual inspection only; no new publisher permission, expression reuse or CIOS admission inferred')}
               for key, (u, d, method, locator, limit) in SOURCES.items()]
    return {'Note-Disposition.json': {'input_sha': BASE, 'review_day': DAY,
                'scope': 'Finite source-support review annotations, not a new intelligence store',
                'notes': dispositions, 'counts': dict(Counter(r['disposition'] for r in dispositions))},
            'Crosswalk-Review.json': {'input_sha': BASE, 'entries': crosswalk},
            'Source-Inspection.json': {'input_sha': BASE, 'sources': sources,
                'retrieval_limit': 'Web connector returns publisher text, sometimes cached. No direct original-byte capture; no invented original digest or rights grant.'}}


if __name__ == '__main__':
    for name, value in build().items():
        (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print('49 note and 34 crosswalk dispositions reconstructed; no runtime or owner services written.')
