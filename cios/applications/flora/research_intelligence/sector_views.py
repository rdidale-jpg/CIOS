"""Compatibility entry points into the common visual and research presentation.

No independent sector templates, menus or ranking logic live here.
"""
from . import unified_views as shared
from . import views as research
from .model import load_assessment
from .visual_templates import render_visual


def catalogue(headers=None):return shared.catalogue(headers=headers)
def operating_model(data):return render_visual(shared.specs(data)['value-chain'])
def industry(data,lens='pestle',headers=None):return shared.industry_page(lens,headers,data.get('research_domain','banking'))
def enterprise(data,headers=None):return shared.enterprise_page(data.get('enterprise_slug','lloyds'),headers=headers)
def opportunities(data,headers=None):
    return shared.page(data['enterprise_name']+' opportunity landscape',shared.opportunities_body(data.get('research_domain','banking')),headers,'opportunities','/opportunities')
def sources(data,headers=None):return research.sources_page(headers,data)
def gaps(data,headers=None):return research.gaps_page(headers,data)
def detail(data,category,identifier,headers=None):
    handlers={'nodes':research.node_page,'evidence':research.evidence_page,'candidates':research.candidate_page}
    if category not in handlers:raise ValueError('Unknown research view')
    return handlers[category](identifier,headers,data)


def render(domain,suffix='',lens='pestle',headers=None):
    data=load_assessment(domain)
    if suffix=='':return industry(data,lens,headers)
    if suffix=='/'+data['enterprise_slug']:return enterprise(data,headers)
    if suffix=='/opportunities':return opportunities(data,headers)
    if suffix=='/sources':return sources(data,headers)
    if suffix=='/gaps':return gaps(data,headers)
    parts=suffix.strip('/').split('/')
    if len(parts)==2:return detail(data,parts[0],parts[1],headers)
    raise ValueError('Unknown research route')
