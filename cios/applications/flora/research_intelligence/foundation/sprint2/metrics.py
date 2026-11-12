"""Selective-decision metrics; indeterminate references are not negative truth labels."""
from collections import Counter

REFERENCES=('supported','unsupported_as_cited','indeterminate')
DECISIONS=('accepted','rejected','unresolved','not_executed')


def decision_matrix(records):
    matrix={r:{d:0 for d in DECISIONS} for r in REFERENCES}
    for row in records:
        if row['reference'] not in matrix or row['decision'] not in DECISIONS:raise ValueError('Explicit reference/decision classes required')
        matrix[row['reference']][row['decision']]+=1
    total=len(records);executed=total-sum(r['decision']=='not_executed' for r in records)
    accepted=sum(r['decision']=='accepted' for r in records);rejected=sum(r['decision']=='rejected' for r in records)
    unresolved=sum(r['decision']=='unresolved' for r in records)
    ratio=lambda n,d:None if not d else n/d
    unsupported=sum(matrix['unsupported_as_cited'].values())-matrix['unsupported_as_cited']['not_executed'];supported=sum(matrix['supported'].values())-matrix['supported']['not_executed'];unknown=sum(matrix['indeterminate'].values())-matrix['indeterminate']['not_executed']
    return {'reference_by_decision':matrix,'total':total,'executed':executed,'not_executed':total-executed,
      'false_acceptance':{'count':matrix['unsupported_as_cited']['accepted'],'executed_reference_denominator':unsupported,'rate':ratio(matrix['unsupported_as_cited']['accepted'],unsupported)},
      'false_rejection':{'count':matrix['supported']['rejected'],'executed_reference_denominator':supported,'rate':ratio(matrix['supported']['rejected'],supported)},
      'supported_unresolved':matrix['supported']['unresolved'],
      'indeterminate_release':{'count':matrix['indeterminate']['accepted'],'executed_reference_denominator':unknown,'rate':ratio(matrix['indeterminate']['accepted'],unknown)},
      'abstention':{'count':unresolved,'executed_denominator':executed,'rate':ratio(unresolved,executed)},
      'decision_coverage':{'count':accepted+rejected,'total_denominator':total,'rate':ratio(accepted+rejected,total)},
      'execution_coverage':{'count':executed,'total_denominator':total,'rate':ratio(executed,total)},
      'limitations':'Rates describe reference support decisions, not absolute real-world truth. Not-executed is not a semantic rejection or model abstention.'}


def reconcile_controlled(report):
    refs={'accept_bounded':'supported','reject':'unsupported_as_cited','unresolved':'indeterminate'}
    obs={'accept_bounded':'accepted','reject':'rejected','unresolved':'unresolved'}
    rows=[{'id':r['id'],'claim_type':r['claim_type'],'reference':refs[r['reference']],'decision':obs[r['observed']]} for r in report['cases']]
    by_type={kind:decision_matrix([r for r in rows if r['claim_type']==kind]) for kind in sorted({r['claim_type'] for r in rows})}
    return {'schema_version':2,'legacy_report_preserved':True,'matrix':decision_matrix(rows),'by_claim_type':by_type,
      'legacy_0_over_30_explanation':'30 combines 19 unsupported-as-cited and 11 indeterminate references. It is a conservative non-acceptance-policy pool, not a factual false-positive denominator. The 11 unresolved outcomes overlap that pool.',
      'corrected_false_acceptance':'0/19 unsupported-as-cited references','corrected_false_rejection':'0/5 supported references',
      'unresolved':'11/35 executed cases','decision_coverage':'24/35 (68.57%)','reference_limits':report['calibration_limit'],'records':rows}
