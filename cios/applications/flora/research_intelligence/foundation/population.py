"""Rebuildable discovery projection; no automatic key-enterprise assertions."""
SOURCE_SEGMENTS={'TECH-SOFTWARE':'software','TECH-CLOUD':'infrastructure','TECH-CYBER':'cyber','TECH-SERVICES':'services'}


def population(release):
    records={}
    for row in release['content']['claims']:
        if row['source_id'] not in SOURCE_SEGMENTS:continue
        name=row['candidate']['statement']
        record=records.setdefault(name,{'name':name,'kind':'consortium_label' if 'Consortium' in name else 'catalogue_entity_label',
          'legal_entity_id':None,'primary_cohorts':[],'claim_ids':[],
          'criteria':{'UK_relevance':'UK government procurement catalogue participation evidenced; significant UK operations/headquarters unverified',
            'scale':'Unknown; no comparable revenue/employment evidence retained',
            'strategic_importance':'Unknown; procurement eligibility is not market importance',
            'ecosystem_role':'Catalogue participant; manufacturer/reseller/implementation role unverified'},
          'selection_state':'research_candidate_not_confirmed_key_enterprise'})
        record['primary_cohorts'].append(SOURCE_SEGMENTS[row['source_id']]);record['claim_ids'].append(row['candidate']['claim_id'])
    return {'schema_version':1,'method':'First four displayed headings per approved cohort; exact-name deduplication only; no fuzzy legal-entity merging',
      'market_scope':'UK-headquartered or significant evidenced UK operations; inclusion still requires legal identity and UK operating evidence',
      'records':sorted(records.values(),key=lambda r:r['name'].casefold()),
      'excluded':[{'label':'Annodata (part of the Kyocera Group)','reason':'Brand/group label; separate legal entity and parent relationship unresolved'}],
      'limitations':['Alphabetical first-page truncation creates severe selection bias; no exhaustive coverage or key-enterprise ranking.',
        'Public procurement catalogues miss private-market, emerging and non-framework providers.',
        'Data/AI, channel roles and emerging technology require distinct sources and comparable significance research.',
        'Source-family count is one even though multiple catalogue pages were separately reacquired.'],
      'next_population_increment':['Resolve exact legal entities and UK operating scope without retaining personal data.',
        'Add independently licensed statistics/register/enterprise-publication families for scale and role evidence.',
        'Expand each segment with documented pagination and stopping rules, including non-procurement providers.',
        'Rank key-enterprise candidates only after comparable UK relevance, scale, importance and role evidence.']}
