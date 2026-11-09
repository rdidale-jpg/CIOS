"""Finite public source-route catalogue; never an intelligence identity store.

Records are presentation routes derived only from repository-owned public data.
No prefix, path normalisation or private-record lookup establishes publicity.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import re
from types import MappingProxyType
from urllib.parse import parse_qsl, urlsplit


@dataclass(frozen=True)
class PublicRoute:
    handler: str
    source_boundary: str
    query_keys: frozenset[str] = frozenset()


@lru_cache(maxsize=1)
def public_route_catalog():
    routes = {}
    def add(paths, handler, source, keys=()):
        for path in paths:
            if path in routes:
                raise ValueError('Ambiguous public route catalogue')
            routes[path] = PublicRoute(handler, source, frozenset(keys))
    add(('/health',), 'health_response', 'Fixed service availability; no owner records')
    add(('/deployment',), 'deployment_payload', 'Allowlisted public code fingerprint only')
    add(('/', '/flora', '/flora/'), '_flora_home_page', 'Repository Banking pipeline; private discovery short-circuits without authority')
    add(('/intelligence',), '_flora_intelligence_page', 'Public source discovery shell; protected owners remain filtered', ('tab',))
    add(('/digital-twins',), 'digital_twins_landing_page', 'Public source discovery shell; protected owners remain filtered')
    add(('/blueprint-import',), 'import_blueprint_entry_page', 'Public closed setup; no protected registry enumeration')
    add(('/pilot-sign-in',), 'sign_in_page', 'Fixed closed-access notice; no credential issuer')
    add(('/opportunities',), '_flora_opportunities_page', 'Repository Banking scenario pipeline', ('tab',))
    add(('/research',), '_flora_research_page', 'Fixed navigation; no research/import records')
    add(('/workspace/reference', '/flora/reference'), 'reference_workspace_page', 'Repository source pipeline and non-authority preference cookie', ('saved',))
    add(('/explore',), '_flora_explore_page', 'Repository Banking pipeline')
    add(('/focus',), '_flora_focus_page', 'Public scenario filtering only', ('opportunity','horizon','enterprise','participant','executive_role','hypothesis','confidence','evidence_strength','recommendation_eligibility','unknown','contradiction'))
    add(('/shape','/shape/banking','/shape/strategic-sales-brief','/shape/banking/strategic-sales-brief'), '_flora_shape_page', 'Repository Banking brief/scenario pipeline', ('opportunity','horizon'))
    add(('/governance',), '_flora_governance_page', 'Repository-source governance summary; fixed protected navigation links')
    add(('/ask',), '_flora_question_page', 'Bounded public Banking question or escaped unavailable response', ('question',))
    add(('/flora/object/BK-ENT-001','/workspace/enterprise/BK-ENT-001','/flora/lloyds'), 'increment1_workspace_page', 'Frozen repository Increment 1 fixture; no Enterprise Model store')
    add(('/flora/object/BK-ENT-001/explain',), '_flora_increment2_explain_page', 'Fixed repository semantic evaluation dataset', ('question_id',))
    add(('/flora/object/BK-ENT-001/context-package',), '_flora_increment2_context_package_page', 'Fixed repository semantic evaluation dataset')
    add(('/industries/uk-banking','/flora/banking/inspect'), 'twin_inspection_page', 'Curated repository industry inspection, not imported package inspection')
    static = {
        '':'banking_landing_page', '/':'banking_landing_page', '/portfolio':'banking_portfolio_page',
        '/banks':'banks_page', '/outlook':'industry_outlook_page', '/ai-native':'ai_native_page',
        '/ai-native/capability-model':'ai_native_capability_model_page', '/timeline':'timeline_page',
        '/pipeline':'pipeline_page', '/signals':'industry_signal_explorer_page',
        '/compare':'banking_compare_page', '/competitors':'banking_competitors_page',
    }
    for suffix, handler in static.items():
        add(('/flora/banking'+suffix,), handler, 'Repository banking_portfolio constants and public source scenarios')
    add(('/flora/banking/heatmap',), 'heatmap_page', 'Public source scenario view labels only', ('mode',))
    add(('/flora/banking/heatmap/detail',), 'heatmap_detail_page', 'Public bank/theme scenario lookup only', ('mode','theme','bank'))
    add(('/flora/banking/explorer',), 'industry_page', 'Repository BANKS public-source fixtures; conceptual ecosystem only')
    from .banking_portfolio import BANKS
    suffixes = {'':'banking_bank_page','/briefing':'banking_bank_page','/evidence':'banking_evidence_page',
                '/financial-performance':'financial_history_page','/market-analyst-view':'market_reaction_page',
                '/market-reaction':'market_reaction_page','/analyst-history':'analyst_history_page',
                '/event-timeline':'enterprise_event_timeline_page','/research-backlog':'research_backlog_page'}
    for slug, bank in BANKS.items():
        add((f'/flora/banking/explorer/{slug}', f'/flora/banking/explorer/{slug}/insights'),
            'enterprise_page', 'Exact public BANKS fixture; no private Canvas or canonical Evidence resolution')
        for suffix, handler in suffixes.items():
            add((f'/flora/banking/{slug}{suffix}',), handler, 'Exact public bank slug in repository BANKS; no private Enterprise lookup')
        for opportunity in bank.opportunities:
            add((f'/flora/banking/{slug}/opportunity/{opportunity.id}',), 'banking_opportunity_page', 'Exact opportunity belonging to this public bank scenario')
    from .enterprise_intelligence.pipeline import OBS, MECH, ASSETS
    for identifier in frozenset((*OBS,*MECH,*ASSETS,'BRH-003')):
        add(('/evidence/'+identifier,), '_flora_evidence_detail_page', 'Exact repository retrieval ID; never canonical Evidence repository')
    from .enterprise_intelligence.explain import explain_lloyds_changes
    for change in explain_lloyds_changes().changes:
        add(('/flora/object/BK-ENT-001/lineage/'+change.change_id,), '_flora_increment2_lineage_page', 'Exact fixed-dataset claim; no arbitrary lineage lookup')
    return MappingProxyType(routes)


def public_read_path(path: str) -> bool:
    if type(path) is not str or not re.fullmatch(r'/[A-Za-z0-9/_-]*',path):
        return False
    if '//' in path:
        return False
    return path in public_route_catalog()


def public_request_target(target: str) -> bool:
    if type(target) is not str or len(target)>4096 or not target.startswith('/') or target.startswith('//'):
        return False
    if any(ord(c)<32 or ord(c)==127 for c in target):
        return False
    try:
        parts=urlsplit(target)
        if parts.scheme or parts.netloc or parts.fragment or not public_read_path(parts.path):
            return False
        if re.search(r'%(?![0-9A-Fa-f]{2})',parts.query):
            return False
        pairs=parse_qsl(parts.query,keep_blank_values=True,strict_parsing=True,encoding='utf-8',errors='strict',max_num_fields=16)
        policy=public_route_catalog()[parts.path]
        keys=[k for k,v in pairs]
        if len(keys)!=len(set(keys)) or any(k not in policy.query_keys or len(v)>1024 or any(ord(c)<32 or ord(c)==127 for c in v) for k,v in pairs):
            return False
        if parts.path.endswith('/explain') and any(k=='question_id' and v!='Q-LBG-CHANGE-EXPLAIN-001' for k,v in pairs):
            return False
        return True
    except (ValueError,UnicodeError):
        return False
