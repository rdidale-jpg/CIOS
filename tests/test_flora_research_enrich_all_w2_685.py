"""Research integrity and deliberate negative cases; no mutation of application owners."""
import copy
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).parents[1]/'docs/flora-runtime/research-enrich-all-w2-685/validate.py'
spec=importlib.util.spec_from_file_location('wave2_research_qa',PATH)
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)


def test_complete_documentary_integrity():
    assert q.validate()['runtime_edits']==0


@pytest.mark.parametrize('sid,dependent,unrelated',[
    ('GDP','GVA-RESIDUAL-A','TECH-CHANNEL'),('LAB','UK-SOCIAL-INSIGHT','IC-C'),
    ('CLOUD','TECH-CLOUD-SIZE','AIR-HUB'),('HUB','AIR-HUB','BNK-RATES'),
    ('CARDS','SECTOR-G-INSIGHT','HOUSEHOLD-BOUNDARY'),
    ('CC','CALC-CC-GROSS-MARGIN','CALC-HUB-EBITDA'),
    ('RR','CALC-RR-UNDERLYING-MARGIN','TECH-CHANNEL')])
def test_withdrawal_removes_exact_dependent_research_not_unrelated(sid,dependent,unrelated):
    alive=q.documentary_survivors(q.read('Claims.json'),[sid])
    assert dependent not in alive and unrelated in alive


def test_cycle_rejected_even_with_withdrawn_source():
    claims=copy.deepcopy(q.read('Claims.json'));claims[0]['input_claim_ids']=[claims[0]['id']]
    with pytest.raises(AssertionError,match='Cyclic'):q.documentary_survivors(claims,['JOBS'])


@pytest.mark.parametrize('field,value', [('public_eligible',True),('canonical_acceptance',True),('source_ids',['UNACQUIRED']),('reporting_period',''),('input_claim_ids',['missing'])])
def test_unsupported_or_promoted_claim_rejected(field,value):
    claims=q.index(q.read('Claims.json'));c=copy.deepcopy(claims['BNK-FLOWS']);c[field]=value
    with pytest.raises(AssertionError):q.claim_check(c,q.index(q.read('Sources.json')),claims)


@pytest.mark.parametrize('field,value',[('original_bytes_acquired',True),('original_bytes_sha256','invented'),('public_use_decision','admitted'),('excerpt_sha256','bad')])
def test_no_fabricated_bytes_or_permission(field,value):
    s=copy.deepcopy(q.read('Sources.json')[0]);s[field]=value
    with pytest.raises(AssertionError):q.source_check(s)


@pytest.mark.parametrize('field,value',[('entity','subsidiary'),('period','FY2025'),('unit','USD million'),('basis','statutory'),('inputs',['2534','11448'])])
def test_financial_perimeter_rejects_near_matches(field,value):
    expected=q.read('Financial-and-Scope-QA.json')[0];row=copy.deepcopy(expected);row[field]=value
    with pytest.raises(AssertionError):q.calculation(row,expected)


@pytest.mark.parametrize('row',q.read('Financial-and-Scope-QA.json'),ids=lambda r:r['id'])
def test_cited_calculation_reproduces(row):
    assert q.calculation(row,row)==row['expected_rounded']


def test_estimate_cannot_become_actual_through_classification():
    claims=q.index(q.read('Claims.json'));row=copy.deepcopy(claims['UK-LABOUR'])
    row['measurements'][0]['semantic_type']='reported'
    with pytest.raises(AssertionError):q.claim_check(row,q.index(q.read('Sources.json')),claims)


def test_self_consistent_wrong_source_denominator_is_rejected():
    row=copy.deepcopy(q.read('Financial-and-Scope-QA.json')[0]);row['inputs'][1]='11448'
    with pytest.raises(AssertionError):q.calculation(row,row)
