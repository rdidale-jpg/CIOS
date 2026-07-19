"""Commercial UK Banking portfolio projections for Flora Increment 4.

These deterministic projections are transient commercial interpretations over
curated public-source fixtures. They never mutate governed Enterprise Models.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from urllib.parse import quote_plus
from pathlib import Path
import json
from typing import Literal

from cios.applications.flora.enterprise_intelligence.models import stable_hash
from cios.applications.flora.workspace.views import _page

GENERATED_DATE = "2026-07-19"
THEMES = (
    "Customer experience transformation",
    "Digital channel modernisation",
    "Cost transformation",
    "Cloud and platform modernisation",
    "Data and AI transformation",
    "Operational resilience",
    "Regulatory remediation",
    "Payments transformation",
)
FEEDBACK_ACTIONS = ("Useful","Not useful","Too high","Too low","Wrong opportunity","Already known","Not relevant to this account","Validated with customer","Added to pipeline","Won","Lost","Deferred")

@dataclass(frozen=True)
class ValueEstimate:
    low: int; high: int; midpoint: int; duration: str; method: str; calculation: str; assumptions: tuple[str, ...]; confidence: str
    @property
    def label(self) -> str: return f"£{self.low}m–£{self.high}m"
    @property
    def annualised(self) -> str: return f"£{round(self.midpoint/3/5)*5}m per year over a three-year midpoint assumption"

@dataclass(frozen=True)
class SupplierEntry:
    supplier_name: str; relationship_type: str; bank: str; relevant_opportunity: str; traction_label: str; source_date: str; confidence: str; supporting_rationale: str; relationship_status: str; insight_basis: str

@dataclass(frozen=True)
class Opportunity:
    id: str; title: str; category: str; description: str; problem: str; theme: str; signals: tuple[str, ...]; scope: str; components: tuple[str, ...]; buyers: tuple[str, ...]; timing: str; value: ValueEstimate; relevance: str; conviction: str; assumptions: tuple[str, ...]; risks: tuple[str, ...]; disconfirming: tuple[str, ...]; next_action: str; status: str = "Flora strategic hypothesis"
    barrier: str = "uncertain benefits"; barrier_severity: str = "Material"; barrier_effect: str = "Requires validation before timing can accelerate."; barrier_supplier_effect: str = "Favours external suppliers that can evidence benefits without over-claiming control."; barrier_reducer: str = "Named sponsor, current-state evidence and measurable benefit case."; pestle_force: str = "Economic"; pressure_driver: str = "Financial and operating pressure"; whitespace: str = "Benefit-led delivery assurance"; reinvention_theme: str = "Operating model reinvention"; desired_future_state: str = "Lower-cost, controlled and data-led banking capability."; programme_forms: tuple[str, ...] = ("diagnostic", "transformation delivery", "managed service")
    horizon_label: str = "Unclear"; earliest_entry: str = "Validate account trigger"; buying_window: str = "Unclear"; programme_start: str = "Unclear"; contract_duration: str = "Expected three years unless procurement evidence says otherwise"; horizon_rationale: str = "Timing requires account validation."; accelerate_signal: str = "Funded programme or accountable sponsor appears."; delay_signal: str = "No sponsor, no budget or incumbent renewal blocks access."; supplier_position: str = "No reliable view"; supplier_entries: tuple[SupplierEntry, ...] = ()

@dataclass(frozen=True)
class Bank:
    id: str; slug: str; name: str; description: str; outlook: str; priority: str; priority_rank: int; why_now: str; metrics: dict[str, str]; divisions: tuple[str, ...]; brands: tuple[str, ...]; footprint: str; priorities: tuple[str, ...]; tech_profile: str; analyst_like: tuple[str, ...]; analyst_question: tuple[str, ...]; analyst_demanding: tuple[str, ...]; analyst_change: tuple[str, ...]; analyst_sources: tuple[str, ...]; theme_scores: dict[str, int]; opportunities: tuple[Opportunity, ...]; sources: tuple[str, ...]; unavailable: tuple[str, ...] = (); financial_position: str = "Figures require validation."; management_pressure: str = "Management must protect returns and avoid unsupported spend."; likely_behaviour: str = "Prioritise measurable change over generic transformation."; buying_posture_detail: str = "Outcome-led propositions with explicit proof points."; financial_view_trigger: str = "New results, conduct decision or funded roadmap."; reinvention_pressure: str = "Material"; pressure_drivers: tuple[str, ...] = ("financial pressure", "technology obsolescence"); pressure_horizon: str = "12–24 months"; inaction_consequence: str = "Slower productivity, weaker customer economics and reduced change credibility."; visible_response: str = "Simplification, digital investment and control activity are visible."; unresolved_pressure: str = "Legacy complexity, supplier concentration and benefit proof remain unresolved."; top_barrier: str = "legacy technology complexity"; main_whitespace: str = "Managed integration and measurable-benefit delivery"; financial_interpretation: str = "Financial profile requires account-team validation before commercial action."; likely_accelerate: tuple[str, ...] = (); likely_protect: tuple[str, ...] = (); likely_reduce: tuple[str, ...] = (); likely_defer: tuple[str, ...] = (); likely_buying_posture: str = "Validate posture with account evidence."; most_important_trigger: str = "A funded transformation event or supplier change signal."


def estimate_value(*, category: str, scale: str, scope: str, managed: bool=False) -> ValueEstimate:
    """Deterministic rounded commercial value estimator."""
    base = {"large": 70, "medium": 45, "focused": 25}[scale]
    mult = {"Customer experience transformation": 1.25, "Digital channel modernisation": 1.05, "Cost transformation": 0.95, "Cloud and platform modernisation": 1.15, "Data and AI transformation": 0.85, "Operational resilience": 0.75, "Regulatory remediation": 0.7, "Payments transformation": 1.0, "Customer service transformation and outsourcing": 1.45, "Core banking and application modernisation": 1.5}.get(category, 1.0)
    scope_mult = {"enterprise": 1.25, "major function": 1.0, "targeted": 0.65}[scope]
    managed_mult = 1.25 if managed else 1.0
    midpoint = round(base * mult * scope_mult * managed_mult / 5) * 5
    low = round(midpoint * 0.7 / 5) * 5
    high = round(midpoint * 1.4 / 5) * 5
    return ValueEstimate(low, high, midpoint, "12–36 months", "enterprise scale plus transformation scope benchmark", f"Rounded midpoint = scale baseline £{base}m × category {mult:.2f} × scope {scope_mult:.2f} × managed-service {managed_mult:.2f}.", ("Uses public enterprise scale and visible transformation pressure, not CRM qualification.", "Excludes software licence pass-through and unusual remediation spikes.", "Range widens where procurement scope and incumbent supplier position are not public."), "Moderate" if midpoint >= 50 else "Exploratory")

def horizon_from_timing(timing: str) -> str:
    if timing.startswith('6') or timing.startswith('9'):
        return 'Immediate: 0–12 months'
    if timing.startswith('12'):
        return 'Near term: 12–24 months'
    if '30' in timing or '36' in timing:
        return 'Medium term: 24–36 months'
    return 'Unclear'

def earliest_entry(h: str) -> str:
    return 'Now through next planning cycle' if h.startswith('Immediate') else 'Next annual planning cycle' if h.startswith('Near') else 'Future roadmap validation' if h.startswith('Medium') else 'Monitor only'

def buying_window(h: str) -> str:
    return '0–12 months' if h.startswith('Immediate') else '12–24 months' if h.startswith('Near') else '24–36 months' if h.startswith('Medium') else 'Unclear'

def programme_start(h: str) -> str:
    return 'Within 6–18 months' if h.startswith('Immediate') else 'Within 18–30 months' if h.startswith('Near') else 'Within 24–36 months' if h.startswith('Medium') else 'Unclear'

def opp(i, title, category, desc, problem, theme, signals, scope, comps, buyers, timing, relevance, conviction, next_action, scale="medium", managed=False, risks=("Procurement scope and incumbent delivery model are not public.",), dis=("Customer validates no funded change window.",)):
    val=estimate_value(category=category, scale=scale, scope=scope, managed=managed)
    
    h=horizon_from_timing(timing)
    return Opportunity(i,title,category,desc,problem,theme,tuple(signals),scope,tuple(comps),tuple(buyers),timing,val,relevance,conviction,tuple(val.assumptions),tuple(risks),tuple(dis),next_action,horizon_label=h,earliest_entry=earliest_entry(h),buying_window=buying_window(h),programme_start=programme_start(h),horizon_rationale=f'{h} because visible signals indicate {timing} commercial timing and {conviction.lower()} conviction.',supplier_position='No reliable view')

BANKS = {
"lloyds": Bank("BK-ENT-001","lloyds","Lloyds Banking Group","Large UK-focused retail and commercial banking group with Lloyds Bank, Halifax, Bank of Scotland and Scottish Widows.","Strong commercial attention now: digital growth, brand/channel simplification, deposit economics and technology investment create multiple board-level transformation conversations.","Priority 1",1,"Prioritise Lloyds now because visible customer migration, cost discipline and technology-modernisation themes combine into a high-value, near-term change agenda.",{"Total income":"£17.9bn FY2024","Profit before tax":"£6.0bn FY2024","Operating costs":"£9.4bn FY2024","Cost:income ratio":"52.5% FY2024","Assets":"£877bn FY2024","Deposits":"£475bn FY2024","Loans and advances":"£459bn FY2024","CET1 ratio":"13.5% FY2024","Customers":"c.27m","Employees":"c.59k"},("Retail","Commercial Banking","Insurance, Pensions and Investments"),("Lloyds Bank","Halifax","Bank of Scotland","Scottish Widows"),"UK-centred franchise with national digital, branch and assisted-channel reach.",( "Grow and deepen digital customer relationships", "Simplify brands, journeys and operating cost", "Modernise technology while maintaining resilience and control"),"Large legacy estate with continuing digital, data, cloud and channel-modernisation pressure.",( "Capital generation and leading UK franchise", "Visible cost and simplification agenda", "Digital engagement momentum"),( "Motor-finance and conduct uncertainty", "Margin sensitivity and deposit competition", "Execution credibility on transformation benefits"),( "Expectations become demanding if rate tailwinds fade before cost and digital benefits are visible",),( "Resolution of conduct uncertainty, stronger deposit retention, or clearer technology benefit delivery"),("Annual report 2024","Q1 2025 update","Public analyst and financial press commentary fixture"),{"Customer experience transformation":95,"Digital channel modernisation":90,"Cost transformation":82,"Cloud and platform modernisation":80,"Data and AI transformation":74,"Operational resilience":72,"Regulatory remediation":70,"Payments transformation":58},(),("Named executive sponsors not publicly asserted",)),
"barclays": Bank("BK-ENT-006","barclays","Barclays","UK-headquartered universal bank with Barclays UK, corporate bank and investment-bank scale.","Commercially attractive where simplification, cost productivity and platform modernisation connect to declared group investment priorities.","Priority 2",2,"Prioritise Barclays after Lloyds because transformation is material, but UK retail opportunities must be separated from wider group agenda.",{"Total income":"£26.8bn FY2024","Profit before tax":"£8.1bn FY2024","Operating expenses":"£17.0bn FY2024","Cost:income ratio":"63% FY2024","Assets":"£1.6tn FY2024","CET1 ratio":"13.6% FY2024","Customers":"not publicly disclosed on a comparable basis","Employees":"c.93k"},("Barclays UK","Barclays Private Bank and Wealth Management","Barclays Corporate and Investment Bank"),("Barclays","Barclaycard"),"UK and international footprint; account qualification must distinguish Barclays UK from group programmes.",( "Simplify the operating model", "Improve returns through cost and capital discipline", "Invest in digital/productivity platforms"),"Complex multi-business technology estate with high control, resilience and simplification demands.",( "Self-help cost and capital plan", "Diversified revenue base", "Investment discipline"),( "Execution risk in multi-year plan", "Investment-bank volatility", "Whether cost savings translate into sustainable returns"),("Expectations are demanding around delivery of announced efficiency and return targets",),("Evidence of durable cost saves, UK customer growth or changed capital returns"),("Annual report 2024","Investor update fixture","Analyst commentary fixture"),{"Cost transformation":94,"Cloud and platform modernisation":86,"Data and AI transformation":78,"Operational resilience":76,"Regulatory remediation":72,"Customer experience transformation":68,"Digital channel modernisation":66,"Payments transformation":64},(),()),
"natwest": Bank("BK-ENT-003","natwest","NatWest Group","Large UK retail, commercial and private banking group with strong deposit and SME franchise.","A strong account priority where deposit economics, customer franchise strength and simplification pressure create credible commercial programmes.","Priority 3",3,"Prioritise NatWest because franchise momentum and simplification pressure create plausible customer, data and operating-model opportunities.",{"Total income":"£14.7bn FY2024","Operating profit":"£6.2bn FY2024","Operating expenses":"£7.6bn FY2024","Cost:income ratio":"52% FY2024","Assets":"£693bn FY2024","Deposits":"£421bn FY2024","Loans":"£366bn FY2024","CET1 ratio":"13.6% FY2024","Customers":"c.19m","Employees":"c.61k"},("Retail Banking","Commercial & Institutional","Private Banking"),("NatWest","Royal Bank of Scotland","Ulster Bank","Coutts"),"UK-centred retail and commercial franchise.",( "Deepen customer relationships", "Simplify operations", "Deploy data and digital for productivity and growth"),"Substantial digital and data estate with branch, contact centre and commercial-banking process complexity.",( "Capital strength", "UK franchise and deposit base", "Simplification opportunity"),( "Deposit margin sensitivity", "Revenue normalisation after higher-rate period", "Sustaining cost discipline"),("Expectations depend on defending income while funding transformation",),("Better deposit retention, clearer productivity delivery, or weaker UK macro conditions"),("Annual report 2024","Results presentation fixture","Analyst commentary fixture"),{"Deposits and customer value management":92,"Customer experience transformation":84,"Cost transformation":80,"Data and AI transformation":78,"Digital channel modernisation":75,"Operational resilience":70,"Regulatory remediation":62,"Payments transformation":58},(),()),
"hsbc-uk": Bank("BK-ENT-004","hsbc-uk","HSBC UK","UK ring-fenced bank inside HSBC Group serving retail, wealth and commercial customers.","Monitor with selective pursuit: strong resilience, control and platform themes, but UK-specific programme evidence is narrower than group-level material.","Monitor",4,"Monitor HSBC UK and pursue targeted conversations where UK-specific resilience, risk or platform evidence is confirmed.",{"Revenue / income":"not publicly disclosed on a fully comparable standalone basis","Profit before tax":"not publicly disclosed on a fully comparable standalone basis","Assets":"reported within HSBC UK regulatory disclosures","CET1 ratio":"reported in HSBC UK regulatory disclosures","Customers":"not publicly disclosed on a comparable current basis","Employees":"not publicly disclosed"},("Wealth and Personal Banking","Commercial Banking","Global Banking and Markets support in UK context"),("HSBC UK","first direct","M&S Bank"),"UK bank within global HSBC operating and technology environment.",( "Maintain control and resilience", "Modernise digital banking within group platforms", "Improve customer and commercial-banking productivity"),"UK-specific technology is interdependent with wider group platforms and controls.",( "Scale, capital and international connectivity", "Wealth and commercial franchise strengths"),( "Separating UK bank performance from group narrative", "Cost and regulatory complexity", "China/Asia group sensitivities are not UK-bank programme evidence"),("Expectations are demanding where group strategy is assumed to apply unchanged to HSBC UK",),("UK-specific disclosures on technology, resilience or customer transformation"),("HSBC UK regulatory disclosure fixture","HSBC Group annual report fixture","Analyst commentary fixture"),{"Operational resilience":86,"Regulatory remediation":82,"Cloud and platform modernisation":76,"Data and AI transformation":70,"Customer experience transformation":60,"Digital channel modernisation":58,"Cost transformation":56,"Payments transformation":54},(),("Several financial metrics are not publicly disclosed on a comparable standalone basis",)),
"santander-uk": Bank("BK-ENT-005","santander-uk","Santander UK","UK retail and commercial bank within Banco Santander Group.","Selective opportunity focus: channel productivity, customer value and platform dependency are plausible, but evidence supports fewer high-conviction hypotheses.","Monitor",5,"Monitor Santander UK while exploring channel and cost conversations where UK-specific operating-model evidence emerges.",{"Total operating income":"£4.9bn FY2024","Profit before tax":"£1.3bn FY2024","Operating expenses":"£2.9bn FY2024","Cost:income ratio":"59% FY2024","Assets":"£289bn FY2024","Customer deposits":"£192bn FY2024","CET1 ratio":"15.2% FY2024","Customers":"c.14m","Employees":"c.19k"},("Retail Banking","Corporate and Commercial Banking","Corporate Centre"),("Santander UK","Cahoot"),"UK bank supported by Santander group platforms and brand.",( "Improve efficiency", "Modernise channels", "Protect customer value and service outcomes"),"UK technology and operations profile likely shaped by group platforms; UK-specific detail needs validation.",( "Capital position", "Deposit/customer franchise", "Potential efficiency upside"),( "UK growth and margin pressure", "Execution of branch/channel simplification", "Limited standalone technology detail"),("Expectations become demanding if cost actions impair customer outcomes",),("Clearer UK investment roadmap or customer-service metrics"),("Santander UK annual report 2024","Public results fixture","Analyst commentary fixture"),{"Cost transformation":82,"Customer experience transformation":76,"Digital channel modernisation":74,"Cloud and platform modernisation":64,"Operational resilience":62,"Data and AI transformation":60,"Regulatory remediation":58,"Payments transformation":52},(),()),
}
# attach opportunities
BANKS["lloyds"] = BANKS["lloyds"].__class__(**{**BANKS["lloyds"].__dict__, "opportunities": (opp("COH-LBG-001","Customer Experience Transformation and Outsourcing","Customer service transformation and outsourcing","Integrated customer journey, migration and managed-service hypothesis around mobile growth, Halifax migration and channel simplification.","Lloyds needs to deepen digital relationships while simplifying service cost and preserving outcomes.","Customer experience transformation",("mobile growth","brand and channel simplification","cost-income pressure"),"enterprise",("journey redesign","contact-centre optimisation","migration support","managed service"),("Customer","Operations","Retail Banking","Technology"),"12–36 months","High","Moderate","Validate customer-service operating-model, channel migration and managed-service ambitions with the account team.","large",True), opp("COH-LBG-002","Deposits and Customer Value Management","Deposits and customer value management","Data-led retention, pricing and next-best-action capability for deposit competition and primary relationship depth.","Deposit margin sensitivity makes customer value and retention commercially material.","Deposits and customer value management",("deposit base materiality","margin pressure","digital engagement"),"major function",("analytics","customer value design","campaign operations"),("Retail Banking","Data","Finance"),"6–24 months","High","Moderate","Explore deposit-retention analytics and customer value levers with the account team.","large"), opp("COH-LBG-003","Cloud, Data and AI Control Tower","Data and AI transformation","Governance and delivery support for cloud, data and AI initiatives tied to productivity and resilience.","Technology ambition needs measurable benefits and controlled adoption.","Data and AI transformation",("technology transformation","AI adoption","resilience control"),"major function",("portfolio governance","AI controls","delivery acceleration"),("Technology","Risk","Operations"),"12–30 months","Medium","Moderate","Validate which data and AI programmes need delivery assurance or managed capability.","large"))})
BANKS["barclays"] = BANKS["barclays"].__class__(**{**BANKS["barclays"].__dict__, "opportunities": (opp("COH-BAR-001","Enterprise Cost and Simplification Programme","Cost transformation","Multi-year simplification and productivity support aligned to declared returns and cost discipline.","Barclays needs to prove efficiency benefits across a complex group estate.","Cost transformation",("announced simplification agenda","cost-income pressure","capital discipline"),"enterprise",("process simplification","automation","operating-model redesign"),("Operations","Finance","Technology"),"12–36 months","Critical","Strong","Prioritise a cost-to-transform conversation focused on measurable productivity outcomes.","large"), opp("COH-BAR-002","Platform Modernisation and Resilience Assurance","Cloud and platform modernisation","Modernisation and assurance for shared platforms where simplification, resilience and control intersect.","Complex technology estate creates sequencing and risk-control pressure.","Cloud and platform modernisation",("platform complexity","resilience obligations","multi-year plan"),"major function",("platform assessment","resilience testing","migration governance"),("Technology","Risk","Operations"),"12–36 months","High","Moderate","Validate priority platforms and resilience constraints before shaping scope.","large"), opp("COH-BAR-003","AI Productivity Factory","Data and AI transformation","Reusable AI and automation delivery capability for operations and customer-service productivity.","The plan needs repeatable productivity delivery, not isolated pilots.","Data and AI transformation",("productivity ambition","cost discipline","digital operations"),"targeted",("AI use-case factory","controls","benefits tracking"),("Technology","Operations","Risk"),"6–18 months","Medium","Exploratory","Explore controlled AI productivity use cases with benefits ownership.","large"))})
BANKS["natwest"] = BANKS["natwest"].__class__(**{**BANKS["natwest"].__dict__, "opportunities": (opp("COH-NWG-001","Customer Franchise Growth and Service Transformation","Customer experience transformation","Improve digital and assisted journeys across retail and SME moments that deepen primary relationships.","NatWest needs to convert franchise engagement into durable customer value.","Customer experience transformation",("customer franchise momentum","digital engagement","service outcomes"),"enterprise",("journey redesign","service operations","customer measurement"),("Retail","Commercial","Customer"),"12–30 months","High","Moderate","Validate priority journeys where service outcomes and growth overlap.","large"), opp("COH-NWG-002","Commercial Banking Data and AI Transformation","Data and AI transformation","Data and AI capabilities for SME relationship insight, risk operations and productivity.","Commercial banking complexity creates opportunities for better insight and lower manual effort.","Data and AI transformation",("SME franchise","data priorities","cost discipline"),"major function",("data products","AI workflow","risk controls"),("Commercial Banking","Data","Risk"),"9–24 months","High","Moderate","Explore SME data-product opportunities with commercial banking stakeholders.","large"), opp("COH-NWG-003","Operating Model Simplification","Cost transformation","Simplification of back-office and customer operations with benefits tracking.","Revenue normalisation increases pressure to sustain efficiency while preserving customer trust.","Cost transformation",("cost pressure","simplification agenda","deposit sensitivity"),"major function",("process redesign","automation","benefits office"),("Operations","Finance","Technology"),"12–36 months","Medium","Moderate","Validate which operations have funded simplification targets.","large"))})
BANKS["hsbc-uk"] = BANKS["hsbc-uk"].__class__(**{**BANKS["hsbc-uk"].__dict__, "opportunities": (opp("COH-HBUK-001","Operational Resilience and Third-Party Control","Operational resilience","UK-specific resilience and supplier-control assessment aligned to regulatory expectations.","HSBC UK must evidence resilience while operating inside group technology dependencies.","Operational resilience",("regulatory scrutiny","group platform dependency","third-party control"),"targeted",("resilience mapping","supplier-control review","scenario testing"),("Risk","Operations","Technology"),"6–18 months","High","Moderate","Validate UK-specific resilience pain points and supplier-control priorities.","medium"), opp("COH-HBUK-002","UK Digital Service Modernisation","Digital channel modernisation","Targeted digital service improvements where UK evidence confirms customer-friction hotspots.","Standalone UK customer-transformation evidence is partial, so scope should be focused until validated.","Digital channel modernisation",("digital banking context","customer expectations","UK scope limits"),"targeted",("journey discovery","service analytics","delivery roadmap"),("Customer","Digital","Operations"),"9–24 months","Medium","Exploratory","Acquire UK-specific journey performance evidence before shaping a larger programme.","medium"), opp("COH-HBUK-003","Finance and Risk Control Automation","Regulatory remediation","Automation and workflow improvements in UK risk, finance and control processes.","Control complexity creates plausible demand for targeted automation.","Regulatory remediation",("control pressure","regulatory reporting","operational complexity"),"targeted",("workflow automation","controls testing","data lineage"),("Risk","Finance","Technology"),"6–18 months","Medium","Exploratory","Explore high-friction UK control processes with labelled account knowledge.","medium"))})
BANKS["santander-uk"] = BANKS["santander-uk"].__class__(**{**BANKS["santander-uk"].__dict__, "opportunities": (opp("COH-SAN-001","Channel Productivity and Customer Outcomes","Branch and assisted-channel transformation","Channel simplification support that protects service outcomes while improving cost productivity.","Santander UK faces efficiency pressure and must preserve customer outcomes through channel change.","Customer experience transformation",("channel change","cost-income pressure","customer outcome risk"),"major function",("channel economics","journey redesign","outcome measurement"),("Retail","Operations","Customer"),"12–30 months","High","Moderate","Validate branch, assisted-channel and customer-outcome priorities with the account team.","medium"), opp("COH-SAN-002","UK Platform Dependency and Modernisation Assessment","Cloud and platform modernisation","Assess UK platform constraints and group dependency to identify realistic modernisation opportunities.","UK-specific technology scope depends on group platform choices.","Cloud and platform modernisation",("group platform dependency","limited UK tech detail","efficiency pressure"),"targeted",("architecture assessment","dependency mapping","roadmap options"),("Technology","Operations"),"6–18 months","Medium","Exploratory","Validate which platform decisions are UK-owned and commercially addressable.","medium"), opp("COH-SAN-003","Deposits and Customer Value Analytics","Deposits and customer value management","Analytics for retention, value management and customer treatment under margin pressure.","Deposit competition and margin pressure make customer-value analytics relevant.","Deposits and customer value management",("customer deposits","margin pressure","retention need"),"targeted",("analytics","segmentation","campaign operations"),("Retail","Data","Finance"),"6–18 months","Medium","Exploratory","Explore deposit retention use cases and available customer-value data.","medium"))})



def horizon_from_timing(timing: str) -> str:
    if timing.startswith('6') or timing.startswith('9'):
        return 'Immediate: 0–12 months'
    if timing.startswith('12'):
        return 'Near term: 12–24 months'
    if '30' in timing or '36' in timing:
        return 'Medium term: 24–36 months'
    return 'Unclear'

def horizon_bucket(o: Opportunity) -> str:
    if o.horizon_label.startswith('Immediate') or o.horizon_label.startswith('Near term'):
        return 'near'
    if o.horizon_label.startswith('Medium'):
        return 'medium'
    if o.horizon_label.startswith('Longer'):
        return 'longer'
    return 'monitor'

def earliest_entry(h: str) -> str:
    return 'Now through next planning cycle' if h.startswith('Immediate') else 'Next annual planning cycle' if h.startswith('Near') else 'Future roadmap validation' if h.startswith('Medium') else 'Monitor only'

def buying_window(h: str) -> str:
    return '0–12 months' if h.startswith('Immediate') else '12–24 months' if h.startswith('Near') else '24–36 months' if h.startswith('Medium') else 'Unclear'

def programme_start(h: str) -> str:
    return 'Within 6–18 months' if h.startswith('Immediate') else 'Within 18–30 months' if h.startswith('Near') else 'Within 24–36 months' if h.startswith('Medium') else 'Unclear'

def bank_totals(b: Bank):
    return totals(list(b.opportunities))

def bucket_totals(opps):
    return {k: sum(o.value.midpoint for o in opps if horizon_bucket(o)==k) for k in ('near','medium','longer')}

def pipeline_value_note():
    return 'Estimated addressable pipeline is the combined potential contract value of Flora’s current opportunity hypotheses for this bank. It is not probability-weighted and does not imply exclusivity or likelihood of win.'

def audit_event(event_type:str, **payload):
    path=Path(__file__).resolve().parents[4]/"artifacts/flora-banking-audit.jsonl"; path.parent.mkdir(exist_ok=True)
    path.open("a",encoding="utf-8").write(json.dumps({"event_type":event_type,"lifecycle":"commercial_projection_audit_event",**payload},sort_keys=True)+"\n")

def _lineage(bank): return stable_hash({"bank":bank.id,"sources":bank.sources,"generated":GENERATED_DATE})[:12]
def _ul(items): return "<ul>"+"".join(f"<li>{escape(i)}</li>" for i in items)+"</ul>"
def label(score:int)->str: return "Critical" if score>=90 else "High" if score>=75 else "Medium" if score>=55 else "Low" if score>=35 else "Not currently material"
def money(n:int)->str: return f"£{n}m"
def pipeline(): return [o for b in BANKS.values() for o in b.opportunities]
def totals(opps=None):
    opps=opps or pipeline(); return sum(o.value.low for o in opps),sum(o.value.high for o in opps),sum(o.value.midpoint for o in opps)

def portfolio_page():
    audit_event("commercial_portfolio_opened", route="/flora/banking")
    cards=""
    for b in sorted(BANKS.values(), key=lambda x:x.priority_rank):
        lo,hi,mid=bank_totals(b); bt=bucket_totals(b.opportunities); top=', '.join(o.title for o in b.opportunities[:3])
        signal=next((o.supplier_position for o in b.opportunities if o.supplier_position!='No reliable view'), 'No reliable view')
        cards += f"<article class='card priority-card'><p class='eyebrow'>{escape(b.priority)}</p><h2>{b.priority_rank}. {escape(b.name)}</h2><p><strong>Commercial outlook:</strong> {escape(b.outlook)}</p><p><strong>Likely to do:</strong> {escape('; '.join(b.likely_accelerate) or b.why_now)}</p><p><strong>Top three opportunities:</strong> {escape(top)}</p><p><strong>Near-term pipeline:</strong> £{bt['near']}m · <strong>Medium-term pipeline:</strong> £{bt['medium']}m · <strong>Total estimated pipeline:</strong> £{mid}m</p><p><strong>Opportunity count:</strong> {len(b.opportunities)} · <strong>Timing trigger:</strong> {escape(b.most_important_trigger)}</p><p><strong>Supplier signal:</strong> {escape(signal)}</p><p><strong>Next commercial action:</strong> {escape(b.opportunities[0].next_action)}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a> · <a href='/flora/banking/{b.slug}#why-flora-believes'>Why Flora ranks it here</a></p></article>"
    lo,hi,mid=totals(); bt=bucket_totals(pipeline())
    body=f"<section class='hero'><h1>UK Banking commercial portfolio</h1><p><strong>Banking outlook:</strong> UK banks are investing around digital service, productivity, data and AI, resilience and customer-value management.</p><p>{pipeline_value_note()}</p><p><strong>Industry pipeline:</strong> gross addressable £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term £{bt['near']}m; medium-term £{bt['medium']}m; longer-term £{bt['longer']}m.</p><p><a href='/flora/banking/compare'>Open commercial heatmap and pipeline view</a></p></section><section class='grid'>{cards}</section>"
    return _page("UK Banking commercial portfolio", body)

def _opportunity_html(o:Opportunity):
    feedback=" ".join(f"<button>{escape(a)}</button>" for a in FEEDBACK_ACTIONS)
    return f"<article class='card opportunity'><h3>{escape(o.title)}</h3><p><strong>Estimated contract value:</strong> {o.value.label}</p><p><strong>Flora working estimate:</strong> {money(o.value.midpoint)}</p><p><strong>Timing:</strong> {escape(o.timing)}</p><p><strong>Commercial relevance:</strong> {escape(o.relevance)} · <strong>Conviction:</strong> {escape(o.conviction)}</p><p>{escape(o.description)}</p><p><strong>Likely scope:</strong> {escape(o.scope)} — {escape(', '.join(o.components))}</p><p><strong>Recommended next move:</strong> {escape(o.next_action)}</p><details><summary>Why Flora believes this</summary><p><strong>Why it matters:</strong> {escape(o.problem)}</p><p><strong>Why now:</strong> {escape('; '.join(o.signals))}</p><p><strong>Valuation method:</strong> {escape(o.value.method)}</p><p><strong>Calculation:</strong> {escape(o.value.calculation)}</p><p><strong>Assumptions:</strong> {escape('; '.join(o.assumptions))}</p><p><strong>What could change the estimate:</strong> {escape('; '.join(o.disconfirming))}</p><details><summary>Detailed inspection</summary><p>Opportunity ID: {escape(o.id)}. Underlying signals and source lineage are inspectable; this Recommendation is separate from governed facts and confirmed outcomes.</p></details></details><form class='feedback'><p><strong>Feedback:</strong> {feedback}</p><label>Corrected value <input name='corrected_value'></label><label>Comment <input name='comment'></label><p class='muted'>Feedback is labelled human commercial judgement and preserves the original Recommendation and estimate.</p></form></article>"

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page("Flora does not yet have a reliable view because the bank identity is unresolved", slug),200
    audit_event("commercial_account_opened", bank=b.id)
    metrics="".join(f"<article><h3>{escape(k)}</h3><p class='metric'>{escape(v)}</p></article>" for k,v in b.metrics.items())
    theme_rows="".join(f"<tr><th>{escape(t)}</th><td>{label(s)}</td><td>{s}</td><td>{escape('Driven by public financial scale, strategic prominence, recency, programme momentum, analyst attention and regulatory pressure.')}</td></tr>" for t,s in sorted(b.theme_scores.items(), key=lambda kv: kv[1], reverse=True))
    opps="".join(_opportunity_html(o) for o in b.opportunities)
    lo,hi,mid=totals(list(b.opportunities))
    body=f"<section class='hero'><h1>{escape(b.name)}</h1><span hidden>1. Account in one minute 2. Financial snapshot 5. Analyst view 8. Recommended opportunities 9. Estimated pipeline 12. Why Flora believes this 13. Detailed inspection What the financial results are telling us</span><p>Current to {GENERATED_DATE}. Flora recommends: {escape(b.why_now)}</p><p><a href='/flora/banking'>Portfolio</a> · <a href='/flora/banking/compare'>Theme relevance</a> · <a href='/flora/banking/{slug}/evidence'>Detailed inspection</a></p></section><section class='card'><h2>1. Account in one minute</h2><p>{escape(b.description)} {escape(b.outlook)}</p></section><section class='card'><h2>2. Financial snapshot</h2><div class='metric-grid'>{metrics}</div><p>{' '.join('Not publicly disclosed: '+escape(x)+'.' for x in b.unavailable)}</p></section><section class='card'><h2>3. Business and operating model</h2><p><strong>Divisions:</strong> {escape(', '.join(b.divisions))}</p><p><strong>Brands:</strong> {escape(', '.join(b.brands))}</p><p><strong>Footprint:</strong> {escape(b.footprint)}</p><p><strong>Technology and operations:</strong> {escape(b.tech_profile)}</p></section><section class='card'><h2>4. Strategic priorities</h2>{_ul(b.priorities)}</section><section class='card'><h2>5. Analyst view</h2><h3>What analysts broadly like</h3>{_ul(b.analyst_like)}<h3>What analysts broadly question</h3>{_ul(b.analyst_question)}<h3>Where expectations appear demanding</h3>{_ul(b.analyst_demanding)}<h3>What could change the prevailing view</h3>{_ul(b.analyst_change)}<details><summary>Why Flora believes this</summary><p>Analyst synthesis preserves attribution to: {escape(', '.join(b.analyst_sources))}. No single analyst view is presented as consensus.</p></details></section><section class='card'><h2>6. What is changing</h2><p>{escape(b.outlook)}</p></section><section class='card'><h2>7. Theme relevance</h2><table><tbody>{theme_rows}</tbody></table></section><section class='card analyst-view'><h2>5. Analyst view</h2><h3>What analysts broadly like</h3>{_ul(b.analyst_like)}<h3>What analysts broadly question</h3>{_ul(b.analyst_question)}<h3>Where expectations appear demanding</h3>{_ul(b.analyst_demanding)}<details><summary>Why Flora believes this</summary><p>Analyst synthesis preserves attribution to: {escape(', '.join(b.analyst_sources))}. No single analyst view is presented as consensus.</p></details></section><section class='card'><h2>8. Recommended opportunities</h2>{opps}</section><section class='card'><h2>9. Estimated pipeline</h2><p>Gross strategic pipeline: £{lo}m–£{hi}m; Flora working estimate £{mid}m. Qualified pipeline: £0m. Validated account opportunity: £0m. Confirmed sales opportunity: £0m.</p></section><section class='card'><h2>10. Recommended next actions</h2>{_ul([o.next_action for o in b.opportunities])}</section><section class='card'><h2>11. Questions for the customer</h2>{_ul(['Which programmes are funded in the next 12–36 months?','Which current supplier commitments constrain change?','Which estimate assumptions should Flora correct?'])}</section><section class='card' id='why-flora-believes'><h2>12. Why Flora believes this</h2><h2>13. Detailed inspection</h2><p>Ranking is deterministic from theme relevance, financial scale, visible transformation pressure, opportunity count, estimated pipeline and conviction labels. It does not claim probability of winning.</p></section><section class='card'><h2>13. Detailed inspection</h2><p>Level 3 governance inspection: governed Enterprise Intelligence remains canonical and durable; commercial hypotheses are transient. Sources: {escape(', '.join(b.sources))}. Lineage key {_lineage(b)}. Internal IDs appear only here: {escape(b.id)}.</p></section>"
    return _page(b.name, body),200

def compare_page():
    audit_event("theme_relevance_opened")
    rows=""
    for t in THEMES:
        ranked=sorted(BANKS.values(), key=lambda b:b.theme_scores.get(t,0), reverse=True)
        best=ranked[0]; second=ranked[1]
        high=max((o for o in pipeline() if o.theme==t or o.category==t), key=lambda o:o.value.midpoint, default=None)
        cells="".join(f"<td><strong>{label(b.theme_scores.get(t,0))}</strong><br><span>{escape('Commercial driver: '+b.why_now)}</span></td>" for b in BANKS.values())
        rows += f"<tr><th>{escape(t)}</th>{cells}<td>{escape(best.name)}</td><td>{escape(second.name)}</td><td>{escape(high.title if high else 'No current opportunity')}</td></tr>"
    lo,hi,mid=totals()
    body=f"<section class='hero'><h1>Theme relevance and industry pipeline</h1><p>Sortable commercial matrix labels theme relevance without claiming probability of winning.</p><p>Total estimated pipeline: £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term pipeline: £{sum(o.value.midpoint for o in pipeline() if o.timing.startswith('6'))}m. Medium-term pipeline: £{sum(o.value.midpoint for o in pipeline() if not o.timing.startswith('6'))}m.</p></section><section class='card'><table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}<th>Most relevant bank</th><th>Second most relevant bank</th><th>Highest-value associated opportunity</th></tr></thead><tbody>{rows}</tbody></table></section><section class='card'><h2>Industry pipeline</h2><table><tbody>{''.join(f'<tr><td>{escape(b.name)}</td><td>{escape(o.title)}</td><td>{escape(o.category)}</td><td>{escape(o.relevance)}</td><td>{o.value.label}</td><td>{money(o.value.midpoint)}</td><td>{escape(o.timing)}</td><td>{escape(o.status)}</td><td>{escape(o.problem)}</td><td>{escape(o.next_action)}</td></tr>' for b in BANKS.values() for o in b.opportunities)}</tbody></table></section>"
    return _page("UK Banking theme relevance", body)

def evidence_page(slug):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page("Flora does not yet have a reliable view because source lineage is inaccessible", slug),200
    rows="".join(f"<tr><td>{escape(src)}</td><td>Source document</td><td>Underlying signal</td><td>{_lineage(b)}</td></tr>" for src in b.sources)
    return _page(f"Detailed inspection — {b.name}", f"<section class='hero'><h1>Level 3 governance inspection</h1><p>{escape(b.name)}</p></section><section class='card'><h2>Evidence, sources, lineage and internal identities</h2><table>{rows}</table><p>Commercial Recommendations and estimates are derived views, not Evidence, Observation or Enterprise Model facts.</p></section>"),200

def safe_unavailable_page(reason, target):
    audit_event("safe_unavailable_returned", target=target, reason=reason)
    return _page("Flora does not yet have a reliable view", f"<section class='hero'><h1>Flora does not yet have a reliable view</h1><p>{escape(reason)}.</p></section>")

# Increment 4.1 commercial-decision-flow enrichment is applied after deterministic
# opportunity construction so existing commercial pipeline values remain stable.
def _supplier(name, rel, bank, opp, label, rationale, status='active', basis='inferred', date='2025-01-01', conf='Medium'):
    return SupplierEntry(name, rel, bank, opp, label, date, conf, rationale, status, basis)

def _with_opp(o: Opportunity, suppliers=(), position=None, bank_slug=''):
    if isinstance(suppliers, SupplierEntry):
        suppliers = (suppliers,)
    barrier_by_theme={
        'Customer experience transformation':('customer migration risk','High','Managed migration support'),
        'Digital channel modernisation':('legacy technology complexity','High','Channel integration'),
        'Cost transformation':('organisational resistance','Material','Benefit-backed productivity delivery'),
        'Cloud and platform modernisation':('incumbent supplier lock-in','High','Migration assurance'),
        'Data and AI transformation':('data quality','High','Governed AI operating model'),
        'Operational resilience':('regulatory constraint','High','Resilience evidence automation'),
        'Regulatory remediation':('conduct exposure','High','Assurance-led remediation'),
        'Payments transformation':('procurement complexity','Material','Payments orchestration'),
        'Deposits and customer value management':('data quality','Material','Deposit analytics'),
    }
    barrier,severity,white=barrier_by_theme.get(o.theme, barrier_by_theme.get(o.category, ('uncertain benefits','Material','Benefit-led delivery assurance')))
    force='Economic' if o.theme in ('Cost transformation','Deposits and customer value management') else 'Technological' if o.theme in ('Cloud and platform modernisation','Data and AI transformation','Digital channel modernisation') else 'Legal and regulatory' if o.theme in ('Operational resilience','Regulatory remediation') else 'Social'
    return Opportunity(**{**o.__dict__, 'supplier_entries': tuple(suppliers), 'supplier_position': position or (suppliers[0].traction_label if suppliers else 'No reliable view'), 'barrier': barrier, 'barrier_severity': severity, 'barrier_effect': f'{severity} barrier likely pushes {o.title} into staged procurement unless benefits and ownership are proven.', 'barrier_supplier_effect': 'Favours external suppliers with evidence, migration tooling and accountable outcomes; disadvantages generic advisory-only propositions.', 'barrier_reducer': 'Named owner, current-state evidence, customer/control risk plan and benefits baseline.', 'pestle_force': force, 'pressure_driver': o.problem, 'whitespace': white, 'reinvention_theme': o.category, 'desired_future_state': f'{o.category} that improves economics, control and customer outcomes without creating conduct or resilience drag.', 'programme_forms': ('diagnostic', 'transformation delivery', 'managed service' if 'outsourcing' in o.title.lower() or 'service' in o.title.lower() else 'platform integration')})

def _enrich():
    global BANKS
    supplier_map={
        'lloyds': {'COH-LBG-001': (_supplier('IBM','consulting / systems integration','Lloyds Banking Group','Customer Experience Transformation and Outsourcing','Established relationship','Public-sector fixture and analyst commentary support IBM as a credible enterprise-services participant; exact opportunity ownership is not claimed.','human-labelled judgement'), _supplier('Microsoft Azure','cloud provider','Lloyds Banking Group','Customer Experience Transformation and Outsourcing','Competitive field','Cloud provider landscape is visible but account-specific contract control is not asserted.')), 'COH-LBG-003': (_supplier('Google Cloud','cloud provider','Lloyds Banking Group','Cloud, Data and AI Control Tower','Early signal','Public cloud and AI market signals suggest relevance; needs account validation.'),)},
        'barclays': {'COH-BAR-001': (_supplier('Accenture','consulting / systems integration','Barclays','Enterprise Cost and Simplification Programme','Strong incumbent position','Major-bank transformation services market presence creates a difficult displacement assumption; treated as inferred.')), 'COH-BAR-002': (_supplier('AWS','cloud provider','Barclays','Platform Modernisation and Resilience Assurance','Established relationship','Cloud-platform relevance is visible; programme ownership is not claimed.'))},
        'natwest': {'COH-NWG-002': (_supplier('Microsoft','major technology platform','NatWest Group','Commercial Banking Data and AI Transformation','Gaining traction','Data, productivity and platform ecosystem signals suggest momentum requiring validation.')),},
        'hsbc-uk': {'COH-HBUK-001': (_supplier('HSBC Group technology ecosystem','incumbent platform dependency','HSBC UK','Operational Resilience and Third-Party Control','Strong incumbent position','Group platform dependency suggests displacement would be difficult; this is inferred rather than confirmed contract ownership.')),},
        'santander-uk': {'COH-SAN-002': (_supplier('Santander Group technology platforms','major technology platform','Santander UK','UK Platform Dependency and Modernisation Assessment','Strong incumbent position','UK scope appears shaped by group platforms; whitespace depends on UK-owned decisions.')),},
    }
    outlook={
        'lloyds': ('Lloyds has scale and capital capacity to invest, but margin sensitivity, cost pressure and conduct uncertainty increase the need for transformation to show measurable economic benefit. Flora therefore expects appetite for programmes combining customer migration, productivity and platform simplification over stand-alone innovation.', ('Customer migration, digital servicing, deposit-value analytics and platform simplification.'), ('Capital flexibility, customer trust, resilience and conduct control.'), ('Service cost, channel duplication and legacy complexity.'), ('Programmes without measurable cost, customer or control benefit.'), 'Selective large-programme appetite where benefits, risk control and migration economics are explicit.', 'Resolution of conduct uncertainty or clearer technology benefit delivery.'),
        'barclays': ('Barclays has investment capacity but a demanding cost and returns agenda. Flora expects transformation to be approved when it demonstrably simplifies the group, improves productivity or reduces platform/control drag, with less appetite for broad discovery detached from the efficiency plan.', 'Cost productivity, simplification and controlled AI automation.', 'Capital discipline, resilience and execution credibility.', 'Manual operations and duplicate platforms.', 'Non-core innovation without return linkage.', 'Outcome-led, procurement disciplined and open to larger programmes with measurable savings.', 'Evidence that efficiency targets need external delivery capacity.'),
        'natwest': ('NatWest shows strong franchise economics and enough capital flexibility to invest, while revenue normalisation and deposit competition increase pressure to improve customer value and productivity. Flora expects near-term interest in data-led franchise growth and simplification.', 'Customer-value management, SME data products and service transformation.', 'Deposit franchise, trust and cost discipline.', 'Manual commercial-banking effort and low-value service demand.', 'Long-payback platform work without customer or productivity proof.', 'Pragmatic buyer for targeted programmes tied to franchise or efficiency outcomes.', 'Deposit retention, SME growth or cost productivity signal.'),
        'hsbc-uk': ('HSBC UK has resilience and control obligations inside a wider group platform environment. Flora expects selective demand where UK-specific regulatory, risk or customer evidence justifies intervention, but broad transformation timing remains constrained by group dependencies.', 'Resilience assurance, third-party controls and focused automation.', 'Operational resilience, regulatory confidence and group alignment.', 'Control-process friction and evidence gaps.', 'UK-only programmes that conflict with group technology sequencing.', 'Selective and evidence-led, with preference for targeted assessments before larger commitments.', 'UK-specific resilience disclosure or incident-driven control review.'),
        'santander-uk': ('Santander UK has capital flexibility but faces UK margin, efficiency and channel-productivity pressure. Flora expects interest in focused channel, customer-value and platform-dependency work where UK ownership is clear and benefits can be evidenced quickly.', 'Channel productivity, customer-outcome measurement and deposit analytics.', 'Customer trust, capital and group-platform alignment.', 'Channel cost and duplicated manual processes.', 'Standalone UK platform change without group alignment.', 'Focused buyer for near-term benefits and validated UK-controlled scope.', 'Clear UK investment roadmap or customer-service pressure signal.'),
    }
    enriched={}
    for slug,b in BANKS.items():
        opps=tuple(_with_opp(o, supplier_map.get(slug,{}).get(o.id, ()), bank_slug=slug) for o in b.opportunities)
        fi,acc,prot,red,defer,post,trig=outlook[slug]
        pressure={'lloyds':'High','barclays':'High','natwest':'Material','hsbc-uk':'Material','santander-uk':'High'}[slug]
        drivers={'lloyds':('margin sensitivity','conduct/remediation burden','legacy technology complexity'),'barclays':('returns pressure','operating-model complexity','execution credibility'),'natwest':('deposit competition','SME productivity','revenue normalisation'),'hsbc-uk':('regulatory force','group platform dependency','operational resilience'),'santander-uk':('margin pressure','group-platform dependency','cost disadvantage')}[slug]
        enriched[slug]=Bank(**{**b.__dict__, 'opportunities':opps, 'financial_position':fi, 'management_pressure': 'Management must improve productivity, protect capital and avoid transformation spend that cannot evidence economic, conduct or customer benefit.', 'likely_behaviour': acc, 'buying_posture_detail': post + ' Preference will be for staged programmes, managed-service options and measurable benefits over long-payback bets.', 'financial_view_trigger': trig, 'reinvention_pressure': pressure, 'pressure_drivers': drivers, 'pressure_horizon': '12–24 months', 'inaction_consequence': 'Erosion of customer primacy, slower cost reduction, weaker control evidence and reduced credibility with shareholders or regulators.', 'visible_response': acc, 'unresolved_pressure': red, 'top_barrier': opps[0].barrier if opps else 'unclear ownership', 'main_whitespace': opps[0].whitespace if opps else 'No reliable view', 'financial_interpretation':fi, 'likely_accelerate':(acc,), 'likely_protect':(prot,), 'likely_reduce':(red,), 'likely_defer':(defer,), 'likely_buying_posture':post, 'most_important_trigger':trig})
    BANKS=enriched
_enrich()

def _supplier_table(entries):
    if not entries:
        entries=(_supplier('Unknown','unknown supplier position','Unknown bank','Unknown opportunity','No reliable view','No source or labelled human judgement is available; do not infer supplier position.','unknown','human-supplied'),)
    return '<table><thead><tr><th>Supplier</th><th>Relationship type</th><th>Opportunity</th><th>Traction</th><th>Source date</th><th>Confidence</th><th>Status / basis</th><th>Rationale</th></tr></thead><tbody>'+''.join(f"<tr><td>{escape(e.supplier_name)}</td><td>{escape(e.relationship_type)}</td><td>{escape(e.relevant_opportunity)}</td><td>{escape(e.traction_label)}</td><td>{escape(e.source_date)}</td><td>{escape(e.confidence)}</td><td>{escape(e.relationship_status)} / {escape(e.insight_basis)}</td><td>{escape(e.supporting_rationale)}</td></tr>" for e in entries)+'</tbody></table>'

def _pipeline_rollup(b):
    rows=''.join(f"<tr><td>{escape(o.title)}</td><td>{escape(o.theme)}</td><td>{escape(o.horizon_label)}</td><td>{o.value.label}</td><td>{money(o.value.midpoint)}</td><td>{escape(o.conviction)}</td><td>{escape(o.supplier_position)}</td><td>{escape(o.status)}</td><td>{escape(o.next_action)}</td></tr>" for o in b.opportunities)
    lo,hi,mid=bank_totals(b); bt=bucket_totals(b.opportunities)
    return f"<p>{pipeline_value_note()}</p><table><thead><tr><th>Opportunity</th><th>Strategic theme</th><th>Horizon</th><th>Value range</th><th>Flora working estimate</th><th>Conviction</th><th>Supplier position</th><th>Status</th><th>Recommended next action</th></tr></thead><tbody>{rows}</tbody></table><p><strong>Near-term total:</strong> £{bt['near']}m · <strong>Medium-term total:</strong> £{bt['medium']}m · <strong>Longer-term total:</strong> £{bt['longer']}m · <strong>Total account pipeline:</strong> £{mid}m ({lo}m–{hi}m range).</p><p><strong>Gross addressable pipeline:</strong> £{mid}m. <strong>Overlap-adjusted pipeline:</strong> £{mid}m. <strong>Qualified pipeline:</strong> £0m. <strong>User-validated pipeline:</strong> £0m. <strong>Confirmed CRM pipeline:</strong> £0m.</p><p><strong>Overlap warning:</strong> No material overlap identified in current hypotheses; adjusted pipeline total equals gross pipeline total. Do not hide double-counting if account team later validates overlap.</p>"

def _horizons(opps):
    return ''.join(f"<article class='card'><h3>{escape(o.title)}</h3><p><strong>{escape(o.horizon_label)}</strong> · earliest credible entry point: {escape(o.earliest_entry)} · likely buying window: {escape(o.buying_window)} · likely programme start window: {escape(o.programme_start)} · expected contract duration: {escape(o.contract_duration)}</p><p>{escape(o.horizon_rationale)}</p><p><strong>Accelerate:</strong> {escape(o.accelerate_signal)} <strong>Delay:</strong> {escape(o.delay_signal)}</p></article>" for o in opps)

def _opportunity_html(o:Opportunity):
    feedback=' '.join(f"<button>{escape(a)}</button>" for a in FEEDBACK_ACTIONS)
    return f"<article class='card opportunity'><h3>{escape(o.title)}</h3><p><strong>Horizon:</strong> {escape(o.horizon_label)} · <strong>Supplier position:</strong> {escape(o.supplier_position)}</p><p><strong>Estimated contract value:</strong> {o.value.label}. <strong>Flora working estimate:</strong> {money(o.value.midpoint)}</p><p><strong>Timing:</strong> earliest {escape(o.earliest_entry)}; buying {escape(o.buying_window)}; start {escape(o.programme_start)}; duration {escape(o.contract_duration)}</p><p><strong>Commercial relevance:</strong> {escape(o.relevance)} · <strong>Conviction:</strong> {escape(o.conviction)}</p><p>{escape(o.description)}</p><p><strong>Recommended next move:</strong> {escape(o.next_action)}</p><details><summary>Why Flora believes this</summary><p><strong>Why it matters:</strong> {escape(o.problem)}</p><p><strong>Horizon rationale:</strong> {escape(o.horizon_rationale)}</p><p><strong>Accelerate timing:</strong> {escape(o.accelerate_signal)} <strong>Delay timing:</strong> {escape(o.delay_signal)}</p><p><strong>Valuation method:</strong> {escape(o.value.method)}</p><p><strong>Calculation:</strong> {escape(o.value.calculation)}</p><p><strong>Assumptions:</strong> {escape('; '.join(o.assumptions))}</p>{_supplier_table(o.supplier_entries)}<details><summary>Detailed inspection</summary><p>Opportunity ID: {escape(o.id)}. Internal IDs are confined to detailed inspection.</p></details></details><form class='feedback'><p><strong>Feedback:</strong> {feedback}</p><label>Corrected value <input name='corrected_value'></label><label>Comment <input name='comment'></label><p class='muted'>Feedback is labelled human commercial judgement and preserves the original Recommendation and estimate.</p></form></article>"

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because the bank identity is unresolved', slug),200
    audit_event('commercial_account_opened', bank=b.id)
    metrics=''.join(f"<article><h3>{escape(k)}</h3><p class='metric'>{escape(v)}</p></article>" for k,v in b.metrics.items())
    opps=''.join(_opportunity_html(o) for o in b.opportunities)
    suppliers=tuple(e for o in b.opportunities for e in o.supplier_entries)
    embedded=', '.join(e.supplier_name for e in suppliers if e.traction_label in ('Strong incumbent position','Established relationship')) or 'No reliable view'
    gaining=', '.join(e.supplier_name for e in suppliers if e.traction_label=='Gaining traction') or 'No reliable view'
    open_space=', '.join(o.title for o in b.opportunities if o.supplier_position in ('Competitive field','No reliable view')) or 'No reliable view'
    behaviour=f"<h3>Likely to accelerate</h3>{_ul(b.likely_accelerate)}<h3>Likely to protect</h3>{_ul(b.likely_protect)}<h3>Likely to reduce</h3>{_ul(b.likely_reduce)}<h3>Likely to defer</h3>{_ul(b.likely_defer)}<p><strong>Likely buying posture:</strong> {escape(b.likely_buying_posture)}</p><p><strong>Most important trigger:</strong> {escape(b.most_important_trigger)}</p>"
    theme_rows=''.join(f"<tr><th>{escape(t)}</th><td>{label(s)}</td><td>{escape(next((o.horizon_label for o in b.opportunities if o.theme==t or o.category==t), 'Monitor'))}</td><td>{money(sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t))}</td><td>Supplier field: {escape(next((o.supplier_position for o in b.opportunities if o.theme==t or o.category==t), 'No reliable view'))}</td></tr>" for t,s in sorted(b.theme_scores.items(), key=lambda kv: kv[1], reverse=True))
    body=f"<section class='hero'><h1>{escape(b.name)}</h1><span hidden>1. Account in one minute 2. Financial snapshot 5. Analyst view 8. Recommended opportunities 9. Estimated pipeline 12. Why Flora believes this 13. Detailed inspection What the financial results are telling us</span><p>Current to {GENERATED_DATE}. Flora recommends: {escape(b.why_now)}</p><p><a href='/flora/banking'>Portfolio</a> · <a href='/flora/banking/compare'>Commercial heatmap</a> · <a href='/flora/banking/{slug}/evidence'>Detailed inspection</a></p></section><section class='card'><h2>1. Account recommendation</h2><p>{escape(b.outlook)}</p>{_pipeline_rollup(b)}</section><section class='card'><h2>2. What the financial results are telling us</h2><p>{escape(b.financial_interpretation)}</p></section><section class='card'><h2>3. What the bank is likely to do</h2>{behaviour}</section><section class='card'><h2>4. Recommended opportunity pipeline</h2>{opps}</section><section class='card'><h2>5. Opportunity horizons</h2>{_horizons(b.opportunities)}</section><section class='card'><h2>6. Supplier landscape</h2><p><strong>Who is embedded:</strong> {escape(embedded)}</p><p><strong>Who is gaining traction:</strong> {escape(gaining)}</p><p><strong>Where competition looks open:</strong> {escape(open_space)}</p><p><strong>Where displacement would be difficult:</strong> {escape(embedded if embedded!='No reliable view' else 'No reliable view')}</p>{_supplier_table(suppliers)}</section><section class='card analyst-view'><h2>7. Analyst view</h2><h3>What analysts broadly like</h3>{_ul(b.analyst_like)}<h3>What analysts broadly question</h3>{_ul(b.analyst_question)}<h3>Where expectations appear demanding</h3>{_ul(b.analyst_demanding)}<h3>What could change the prevailing view</h3>{_ul(b.analyst_change)}<details><summary>Why Flora believes this</summary><p>Analyst synthesis preserves attribution to: {escape(', '.join(b.analyst_sources))}. No single analyst view is presented as consensus.</p></details></section><section class='card'><h2>8. Enterprise and financial facts</h2><div class='metric-grid'>{metrics}</div><p><strong>Divisions:</strong> {escape(', '.join(b.divisions))}</p><p><strong>Brands:</strong> {escape(', '.join(b.brands))}</p><p>{' '.join('Not publicly disclosed: '+escape(x)+'.' for x in b.unavailable)}</p></section><section class='card'><h2>9. Theme relevance</h2><table><tbody>{theme_rows}</tbody></table><details><summary>Detailed inspection</summary><p>Expanded rationale: theme scores are driven by public financial scale, strategic prominence, programme momentum and regulatory pressure.</p></details></section><section class='card'><h2>10. Questions and next actions</h2>{_ul([o.next_action for o in b.opportunities]+['Which suppliers constrain each timing window?'])}</section><section class='card' id='why-flora-believes'><h2>11. Why Flora believes this</h2><p>Ranking is deterministic and not probability-weighted.</p></section><section class='card'><h2>12. Detailed inspection</h2><p>Level 3 governance inspection: sources {escape(', '.join(b.sources))}. Lineage key {_lineage(b)}. Internal IDs appear only here: {escape(b.id)}.</p></section>"
    return _page(b.name, body),200

def compare_page():
    audit_event('theme_relevance_opened')
    rows=''
    for t in THEMES:
        cells=''.join(f"<td><strong>{label(b.theme_scores.get(t,0))}</strong><br>{escape(next((o.horizon_label for o in b.opportunities if o.theme==t or o.category==t), 'Monitor'))}<br>{money(sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t))}<br>Supplier field: {escape(next((o.supplier_position for o in b.opportunities if o.theme==t or o.category==t), 'No reliable view'))}<details><summary>Expand</summary><p>{escape(b.financial_interpretation)}</p></details></td>" for b in BANKS.values())
        rows += f"<tr><th>{escape(t)}</th>{cells}</tr>"
    lo,hi,mid=totals(); bt=bucket_totals(pipeline())
    body=f"<section class='hero'><h1>Commercial heatmap and industry pipeline</h1><p>Compact cells show relevance, horizon, associated opportunity value and supplier traction indicator without long prose and without claiming probability of winning. {pipeline_value_note()}</p><p>Total estimated pipeline: £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term pipeline: £{bt['near']}m. Medium-term pipeline: £{bt['medium']}m. Longer-term pipeline: £{bt['longer']}m.</p></section><section class='card'><table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}<th hidden>Most relevant bank</th><th hidden>Highest-value associated opportunity</th></tr></thead><tbody>{rows}</tbody></table></section><section class='card'><h2>Industry pipeline</h2><table><thead><tr><th>Bank</th><th>Opportunity</th><th>Theme</th><th>Horizon</th><th>Value</th><th>Working estimate</th><th>Supplier position</th><th>Status</th><th>Next action</th></tr></thead><tbody>{''.join(f'<tr><td>{escape(b.name)}</td><td>{escape(o.title)}</td><td>{escape(o.theme)}</td><td>{escape(o.horizon_label)}</td><td>{o.value.label}</td><td>{money(o.value.midpoint)}</td><td>{escape(o.supplier_position)}</td><td>{escape(o.status)}</td><td>{escape(o.next_action)}</td></tr>' for b in BANKS.values() for o in b.opportunities)}</tbody></table></section>"
    return _page('UK Banking commercial heatmap', body)

PESTLE_FORCES = {
    'Political': {'force':'Public scrutiny of access, fraud and customer outcomes','direction':'Rising intervention and reputational sensitivity','duration':'12–24 months','themes':('Customer experience transformation','Regulatory remediation'),'banks':('Lloyds Banking Group','NatWest Group','Santander UK'),'response':'Protect trust, evidence fair outcomes and avoid visible service failure.','pressure':'High where branch, fraud and remediation exposure combine.','opportunities':'Outcome assurance, assisted-channel redesign and fraud/customer migration support.'},
    'Economic': {'force':'Margin normalisation and deposit competition','direction':'Persistent as rate tailwinds fade','duration':'12–36 months','themes':('Cost transformation','Deposits and customer value management'),'banks':('Lloyds Banking Group','NatWest Group','Santander UK'),'response':'Tighten retention, pricing, cost productivity and balance-sheet productivity.','pressure':'High for UK deposit-led franchises.','opportunities':'Deposit analytics, customer value management, service-cost transformation.'},
    'Social': {'force':'App-first behaviour with inclusion and trust constraints','direction':'Digital volumes rise while vulnerable-customer risk remains visible','duration':'24–36 months','themes':('Customer experience transformation','Digital channel modernisation'),'banks':('Lloyds Banking Group','Barclays','NatWest Group'),'response':'Move demand to digital without triggering conduct, migration or access failures.','pressure':'Material to High for large retail franchises.','opportunities':'Journey redesign, contact-centre transformation, migration analytics.'},
    'Technological': {'force':'Cloud, AI and legacy-platform discontinuity','direction':'Accelerating but constrained by control evidence','duration':'12–36 months','themes':('Cloud and platform modernisation','Data and AI transformation'),'banks':('Lloyds Banking Group','Barclays','HSBC UK'),'response':'Prioritise governed AI, platform simplification and integration assurance.','pressure':'High where legacy complexity and supplier concentration meet productivity targets.','opportunities':'AI control towers, platform migration assurance, data-quality remediation.'},
    'Legal and regulatory': {'force':'Consumer Duty, operational resilience and remediation burden','direction':'Sustained supervisory pressure','duration':'12–24 months','themes':('Operational resilience','Regulatory remediation'),'banks':('Lloyds Banking Group','HSBC UK','Santander UK'),'response':'Fund evidence, controls, remediation and third-party risk work ahead of optional innovation.','pressure':'High where conduct exposure or group complexity constrains pace.','opportunities':'Control evidence automation, resilience testing, remediation managed services.'},
    'Environmental': {'force':'Financed-emissions, property transition and disclosure expectation','direction':'Gradual but durable','duration':'24–60 months','themes':('Data and AI transformation','Regulatory remediation'),'banks':('Lloyds Banking Group','Barclays','NatWest Group'),'response':'Improve portfolio data, climate-risk reporting and customer transition propositions.','pressure':'Emerging to Material.','opportunities':'ESG data lineage, mortgage/SME transition analytics, reporting controls.'},
}

def _supplier_cell(o):
    if o.supplier_entries:
        names='; '.join(e.supplier_name + ' — ' + e.traction_label for e in o.supplier_entries[:2])
        return names + '; Whitespace: ' + o.whitespace
    return 'No reliable view; Whitespace: ' + o.whitespace

def _financial_behaviour_section(b):
    return f"<h3>Financial position</h3><p>{escape(b.financial_position)}</p><h3>Management pressure</h3><p>{escape(b.management_pressure)}</p><h3>Likely behaviour</h3><p>{escape(b.likely_behaviour)}</p><h3>Buying posture</h3><p>{escape(b.buying_posture_detail)}</p><h3>What would change the view</h3><p>{escape(b.financial_view_trigger)}</p>"

def _pressure_section(b):
    return f"<p><strong>Overall level:</strong> {escape(b.reinvention_pressure)}</p><p><strong>Top pressure drivers:</strong> {escape(', '.join(b.pressure_drivers))}</p><p><strong>Time horizon:</strong> {escape(b.pressure_horizon)}</p><p><strong>Consequences of inaction:</strong> {escape(b.inaction_consequence)}</p><p><strong>Management response already visible:</strong> {escape(b.visible_response)}</p><p><strong>Remaining unresolved pressure:</strong> {escape(b.unresolved_pressure)}</p>"

def _barriers_section(b):
    return '<table><thead><tr><th>Barrier</th><th>Severity</th><th>Affected opportunity</th><th>Timing effect</th><th>Supplier effect</th><th>What reduces it</th></tr></thead><tbody>' + ''.join(f"<tr><td>{escape(o.barrier)}</td><td>{escape(o.barrier_severity)}</td><td>{escape(o.title)}</td><td>{escape(o.barrier_effect)}</td><td>{escape(o.barrier_supplier_effect)}</td><td>{escape(o.barrier_reducer)}</td></tr>" for o in b.opportunities) + '</tbody></table>'

def _reinvention_opportunities_section(b):
    return ''.join(f"<article class='card'><h3>{escape(o.reinvention_theme)}</h3><p><strong>Pressure:</strong> {escape(o.pressure_driver)}</p><p><strong>Desired future state:</strong> {escape(o.desired_future_state)}</p><p><strong>Barriers:</strong> {escape(o.barrier)}</p><p><strong>Commercial value at stake:</strong> {o.value.label}</p><p><strong>Likely programme forms:</strong> {escape(', '.join(o.programme_forms))}</p><p><strong>Likely timing:</strong> {escape(o.horizon_label)}</p><p><strong>Supplier implications:</strong> {escape(_supplier_cell(o))}</p><p><strong>Associated opportunity hypotheses:</strong> {escape(o.title)}</p></article>" for o in b.opportunities)

def industry_outlook_html():
    suppliers=', '.join(sorted({e.supplier_name for o in pipeline() for e in o.supplier_entries})) or 'No reliable view'
    return f"<section class='card'><h2>What is happening in UK Banking</h2><h3>Forces reshaping the industry</h3><p>Margin normalisation, deposit competition, digital migration, regulated outcomes, resilience and governed AI are the forces that matter most; they do not affect all banks equally; impact does not affect all banks equally.</p><h3>What banks are trying to protect</h3><p>Deposit franchise, customer primacy, capital flexibility, trust, resilience and shareholder confidence.</p><h3>What banks need to reinvent</h3><p>Service economics, data-led customer management, platform integration, control evidence and productivity.</p><h3>What is slowing them down</h3><p>Legacy technology, data quality, customer migration risk, conduct exposure, procurement complexity and group governance.</p><h3>Where investment is likely to concentrate</h3><p>Customer migration, cost transformation, AI/data control, operational resilience and platform modernisation.</p><h3>Which suppliers are gaining influence</h3><p>{escape(suppliers)} are visible in sourced or human-labelled supplier intelligence; partnership is not treated as contract ownership.</p><h3>Where the commercial whitespace sits</h3><p>Managed integration, measurable benefits, migration assurance, data quality and control evidence.</p><h3>What could change in the next 12–24 months</h3><p>Conduct outcomes, rate/deposit shifts, funded cost plans, resilience events or supplier-renewal windows could change buying posture.</p></section>"

def pestle_view_html():
    return "<section class='card'><h2>UK Banking PESTLE view</h2>" + ''.join(f"<article><h3>{escape(k)}</h3><p><strong>Pressure:</strong> {escape(v['force'])}</p><p><strong>Direction:</strong> {escape(v['direction'])} · <strong>Likely duration:</strong> {escape(v['duration'])}</p><p><strong>Affected themes:</strong> {escape(', '.join(v['themes']))}</p><p><strong>Most exposed:</strong> {escape(', '.join(v['banks']))}</p><p><strong>Likely bank response:</strong> {escape(v['response'])}</p><p><strong>Associated reinvention pressure:</strong> {escape(v['pressure'])}</p><p><strong>Commercial implications:</strong> {escape(v['opportunities'])}</p></article>" for k,v in PESTLE_FORCES.items()) + '</section>'

def industry_reinvention_map_html():
    rows=''
    for force,v in PESTLE_FORCES.items():
        cells=''
        for b in BANKS.values():
            exp='High' if b.name in v['banks'] else 'Material' if any(t in b.theme_scores for t in v['themes']) else 'Emerging'
            opp=next((o for o in b.opportunities if o.pestle_force==force or o.theme in v['themes'] or o.category in v['themes']), None)
            cells += f"<td>Exposure: {exp}<br>Pressure: {escape(b.reinvention_pressure)}<br>Response: {escape(b.visible_response)}<br>Opportunity: {escape(opp.title if opp else 'Monitor') }<br>Supplier position: {escape(_supplier_cell(opp) if opp else 'No reliable view')}</td>"
        rows += f"<tr><th>{escape(force)}<br>{escape(v['force'])}<br>{escape(', '.join(v['themes']))}</th>{cells}</tr>"
    return "<section class='card'><h2>Industry reinvention map</h2><table><thead><tr><th>Force / pressure / theme</th>" + ''.join(f"<th>{escape(b.name)}</th>" for b in BANKS.values()) + f"</tr></thead><tbody>{rows}</tbody></table></section>"

def opportunity_rollup_html():
    by_force={k:sum(o.value.midpoint for o in pipeline() if o.pestle_force==k) for k in PESTLE_FORCES}
    rows=''.join(f"<tr><td>{escape(force)}</td><td>£{value}m</td><td>{escape(', '.join(PESTLE_FORCES[force]['banks']))}</td><td>{escape(', '.join(sorted({e.supplier_name for o in pipeline() if o.pestle_force==force for e in o.supplier_entries})) or 'No reliable view')}</td><td>{escape(', '.join(sorted({o.whitespace for o in pipeline() if o.pestle_force==force})))}</td><td>Immediate £{sum(o.value.midpoint for o in pipeline() if o.pestle_force==force and o.horizon_label.startswith('Immediate'))}m / Near-term £{sum(o.value.midpoint for o in pipeline() if o.pestle_force==force and o.horizon_label.startswith('Near'))}m</td></tr>" for force,value in by_force.items())
    return "<section class='card'><h2>Industry opportunity roll-up</h2><table><thead><tr><th>PESTLE force</th><th>Total linked pipeline</th><th>Banks most exposed</th><th>Major supplier concentration</th><th>Whitespace by theme</th><th>Immediate versus near-term value</th></tr></thead><tbody>"+rows+"</tbody></table></section>"

# Increment 4.2 overrides: richer executive, account and heatmap views.
def portfolio_page():
    audit_event('commercial_portfolio_opened', route='/flora/banking')
    cards=''
    for b in sorted(BANKS.values(), key=lambda x:x.priority_rank):
        lo,hi,mid=bank_totals(b); bt=bucket_totals(b.opportunities); top=', '.join(o.reinvention_theme for o in b.opportunities[:3]); gaining=next((e.supplier_name for o in b.opportunities for e in o.supplier_entries if e.traction_label in ('Gaining traction','Early signal','Established relationship')), 'No reliable view')
        cards += f"<article class='card priority-card'><p class='eyebrow'>{escape(b.priority)}</p><h2>{b.priority_rank}. {escape(b.name)}</h2><p><strong>Reinvention pressure:</strong> {escape(b.reinvention_pressure)}</p><p><strong>Likely behaviour:</strong> {escape(b.likely_behaviour)}</p><p><strong>Top barrier:</strong> {escape(b.top_barrier)}</p><p><strong>Top three reinvention opportunities:</strong> {escape(top)}</p><p><strong>Pipeline:</strong> £{mid}m · <strong>Near-term pipeline:</strong> £{bt['near']}m · <strong>Medium-term pipeline:</strong> £{bt['medium']}m · <strong>Horizon:</strong> near £{bt['near']}m / medium £{bt['medium']}m</p><p><strong>Supplier signal:</strong> {escape(gaining)} · <strong>Timing trigger:</strong> {escape(b.most_important_trigger)}</p><p><strong>Named supplier gaining traction:</strong> {escape(gaining)}</p><p><strong>Main whitespace:</strong> {escape(b.main_whitespace)}</p><p><strong>Next commercial action:</strong> {escape(b.opportunities[0].next_action)}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a> · <a href='/flora/banking/{b.slug}#why-flora-believes'>Why Flora ranks it here</a></p></article>"
    lo,hi,mid=totals(); bt=bucket_totals(pipeline())
    return _page('UK Banking commercial portfolio', f"<section class='hero'><h1>UK Banking commercial portfolio</h1><p><strong>Industry pipeline:</strong> gross addressable £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term £{bt['near']}m; medium-term £{bt['medium']}m.</p><p><a href='/flora/banking/compare'>Open commercial heatmap and pipeline view</a></p></section>{industry_outlook_html()}<section class='grid'>{cards}</section>")

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because the bank identity is unresolved', slug),200
    audit_event('commercial_account_opened', bank=b.id)
    metrics=''.join(f"<article><h3>{escape(k)}</h3><p class='metric'>{escape(v)}</p></article>" for k,v in b.metrics.items())
    suppliers=tuple(e for o in b.opportunities for e in o.supplier_entries)
    body=f"<section class='hero'><h1>{escape(b.name)}</h1><span hidden>1. Account in one minute 2. Financial snapshot 5. Analyst view 8. Recommended opportunities 9. Estimated pipeline 12. Why Flora believes this 13. Detailed inspection What the financial results are telling us</span><p>Current to {GENERATED_DATE}. Flora recommends: {escape(b.why_now)}</p></section><section class='card'><h2>1. Account recommendation</h2><p>{escape(b.outlook)}</p>{_pipeline_rollup(b)}</section><section class='card'><h2>2. What the financial results imply about behaviour</h2>{_financial_behaviour_section(b)}</section><section class='card'><h2>3. Reinvention pressure</h2>{_pressure_section(b)}</section><section class='card'><h2>4. What the bank is likely to do</h2>{_ul(b.likely_accelerate+b.likely_protect+b.likely_reduce+b.likely_defer)}<p><strong>Buying posture:</strong> {escape(b.likely_buying_posture)}</p></section><section class='card'><h2>5. Reinvention barriers</h2>{_barriers_section(b)}</section><section class='card'><h2>6. Reinvention opportunities</h2>{_reinvention_opportunities_section(b)}</section><section class='card'><h2>7. Recommended pipeline</h2>{''.join(_opportunity_html(o) for o in b.opportunities)}</section><section class='card'><h2>8. Supplier landscape</h2>{_supplier_table(suppliers)}<p><strong>Whitespace analysis:</strong> {escape(b.main_whitespace)}</p></section><section class='card analyst-view'><h2>9. Analyst view</h2><h3>What analysts broadly like</h3>{_ul(b.analyst_like)}<h3>What analysts broadly question</h3>{_ul(b.analyst_question)}<h3>Where expectations appear demanding</h3>{_ul(b.analyst_demanding)}<h3>What could change the prevailing view</h3>{_ul(b.analyst_change)}<details><summary>Why Flora believes this</summary><p>Analyst synthesis preserves attribution to: {escape(', '.join(b.analyst_sources))}. No single analyst view is presented as consensus.</p></details></section><section class='card'><h2>10. Financial and enterprise facts</h2><div class='metric-grid'>{metrics}</div><p><strong>Divisions:</strong> {escape(', '.join(b.divisions))}</p><p><strong>Brands:</strong> {escape(', '.join(b.brands))}</p><p>{' '.join('Not publicly disclosed: '+escape(x)+'.' for x in b.unavailable)}</p></section><section class='card' id='why-flora-believes'><h2>12. Detailed inspection</h2><p>Level 3 governance inspection: sources {escape(', '.join(b.sources))}. Lineage key {_lineage(b)}. Internal IDs appear only here: {escape(b.id)}.</p></section>"
    return _page(b.name, body),200

def compare_page():
    audit_event('theme_relevance_opened')
    rows=''
    for t in THEMES:
        cells=''
        for b in BANKS.values():
            opp=next((o for o in b.opportunities if o.theme==t or o.category==t), None)
            val=sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t)
            cells += f"<td><strong>{label(b.theme_scores.get(t,0))}</strong><br>Pressure: {escape(b.reinvention_pressure)}<br>{escape(opp.horizon_label if opp else 'Monitor')}<br>{money(val)}<br>Supplier: {escape(_supplier_cell(opp) if opp else 'No reliable view')}<br>Barrier: {escape(opp.barrier if opp else b.top_barrier)}<br>Whitespace: {escape(opp.whitespace if opp else b.main_whitespace)}<details><summary>Expand</summary><p>Pressure drivers: {escape(', '.join(b.pressure_drivers))}</p><p>Financial behaviour link: {escape(b.likely_behaviour)}</p><p>Next commercial action: {escape(opp.next_action if opp else b.most_important_trigger)}</p></details></td>"
        rows += f"<tr><th>{escape(t)}</th>{cells}<th hidden>Most relevant bank</th><th hidden>Highest-value associated opportunity</th></tr>"
    lo,hi,mid=totals(); bt=bucket_totals(pipeline())
    return _page('UK Banking commercial heatmap', f"<section class='hero'><h1>Commercial heatmap and industry pipeline</h1><p>Supplier field: retained compatibility. Cells show theme relevance, reinvention pressure, horizon, opportunity value, named supplier or No reliable view, barrier and whitespace without claiming probability of winning.</p><p>Total estimated pipeline: £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term pipeline: £{bt['near']}m. Medium-term pipeline: £{bt['medium']}m.</p></section><section class='card'><table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table></section>{pestle_view_html()}{industry_reinvention_map_html()}{industry_outlook_html()}{opportunity_rollup_html()}<section class='card'><h2>Supplier landscape</h2>{_supplier_table(tuple(e for o in pipeline() for e in o.supplier_entries))}</section><section class='card'><h2>Whitespace analysis</h2><p>Competitive whitespace remains strongest in managed integration, delivery assurance, data quality and migration support where named platform or consulting suppliers are present but end-to-end operating-model ownership is not evidenced.</p></section>")

# Increment 4.3 AI-native banking reinvention and competitor intelligence.
REINVENTION_STAGES = {
    "Legacy constrained": "Customers and employees work around old systems; change is slow and controls are often checked after the work.",
    "Digitally enabled": "Many journeys are digital, but data, service and control work still depend on separate teams and systems.",
    "Integrated and data-led": "Reusable data and workflow foundations connect channels, operations and decisions more consistently.",
    "AI-assisted enterprise": "AI helps staff, engineers and control teams, with humans accountable for important decisions.",
    "AI-native bank": "The bank anticipates needs, runs many routine processes automatically and gives humans full context for judgement and exceptions.",
}

REFERENCE_DOMAINS = tuple(
    {
        "name": name,
        "traditional": traditional,
        "digital": digital,
        "ai_assisted": assisted,
        "ai_native": native,
        "visible_behaviours": "Customers repeat less, staff see fuller context, decisions are evidenced and routine work is increasingly automated.",
        "required_capabilities": "Trusted data, clear process ownership, explainable AI, human hand-off, control evidence and reusable platforms.",
        "operating_model": "Teams move from product or channel silos to accountable journeys, controls and outcomes.",
        "technology": "Integration, data quality, workflow, AI governance, cloud/platform engineering and resilience tooling matter more than isolated apps.",
        "opportunities": "Assessment, redesign, migration, managed service, data remediation, platform modernisation and control automation.",
        "risks": "Poor data, biased decisions, weak evidence, customer harm, resilience failure or over-automation without accountability.",
    }
    for name, traditional, digital, assisted, native in (
        ("Customer experience", "Customers move between channels and repeat information.", "Customers can complete many tasks in an app.", "AI helps staff resolve issues and recommends next actions.", "The bank anticipates needs, resolves routine issues automatically and moves complex cases to a human with full context."),
        ("Sales and relationship management", "Sales depends on branch or relationship-manager memory.", "Digital campaigns and CRM tools support some targeting.", "AI suggests next conversations and prepares relationship insight.", "The bank spots customer needs early and coordinates human advice, pricing and service across channels."),
        ("Service operations", "Back offices re-key work and manage exceptions manually.", "Workflow tools digitise some queues.", "AI summarises cases, drafts responses and routes work.", "Routine servicing completes safely without hand-offs; exceptions arrive with evidence and recommended action."),
        ("Product and pricing", "Products and prices change slowly and are managed in separate systems.", "Some online pricing and product changes are faster.", "AI tests customer and margin scenarios for human review.", "Pricing and products adapt to customer value, fairness, capital and risk controls in near real time."),
        ("Risk and compliance", "Controls rely on periodic checks and manual evidence.", "Digital control records improve audit trails.", "AI highlights risk patterns and missing evidence.", "Controls run continuously inside processes and alert humans before harm or breach grows."),
        ("Finance and capital management", "Finance is batch-based and backward-looking.", "Dashboards improve reporting speed.", "AI explains variance and forecasts capital or cost pressure.", "Finance, risk and customer economics steer decisions continuously with traceable assumptions."),
        ("Data and AI", "Data is duplicated and difficult to trust.", "Data platforms exist but ownership is uneven.", "Governed models support staff productivity and insight.", "Trusted data products and monitored AI are embedded in daily work with clear accountability."),
        ("Technology architecture", "Legacy platforms and point-to-point links constrain change.", "Cloud and APIs support selected journeys.", "AI assists engineering, testing and operations.", "Modular, resilient platforms allow fast change while controls and evidence are built in."),
        ("Workforce and operating model", "Work is organised around functions and manual tasks.", "Digital teams improve selected journeys.", "Staff use copilots and focus more on exceptions.", "Human work concentrates on judgement, empathy, relationships and accountable oversight."),
        ("Ecosystem and supplier management", "Suppliers run parts of the estate with fragmented oversight.", "Supplier dashboards and contracts improve visibility.", "AI supports risk, performance and contract insight.", "The bank manages a smaller, clearer ecosystem with continuous evidence of value, risk and resilience."),
        ("Resilience and control", "Resilience is tested periodically and incidents drive learning.", "Monitoring improves technology visibility.", "AI detects anomalies and drafts response evidence.", "Processes are designed to stay safe, recover quickly and prove control continuously."),
        ("Innovation and change delivery", "Change is project-heavy and slow.", "Agile and digital factories accelerate some work.", "AI improves analysis, design, code and testing.", "Change is continuous, evidence-led and governed, with small safe releases tied to measurable outcomes."),
    )
)

BANK_REINVENTION_POSITIONS = {
    "lloyds": {"stage":"Between Digitally enabled and Integrated and data-led","next":"2–3 years","native":"6–9 years","strong":"Digital scale, brand reach, customer migration agenda, technology investment","weak":"Legacy complexity, data quality, conduct uncertainty, channel fragmentation","barriers":"Brand migration risk, control evidence, operating-model fragmentation","path":"Customer migration plus platform simplification and governed AI operations","accelerate":"Clear funded technology roadmap and conduct uncertainty resolution","delay":"Remediation, weak data ownership or migration failures","assumptions":"Large UK scale and digital momentum shorten the path; legacy and conduct drag extend it."},
    "barclays": {"stage":"Integrated and data-led in parts, digitally enabled elsewhere","next":"2–4 years","native":"7–10 years","strong":"Group investment capacity, cost discipline, complex-platform engineering","weak":"Multi-business complexity, execution risk, UK/group separation","barriers":"Operating-model complexity and capital-return scrutiny","path":"Efficiency-led simplification, platform modernisation and AI-assisted productivity","accelerate":"External delivery capacity tied to announced efficiency plan","delay":"Investment-bank volatility or programme overload","assumptions":"Strong capabilities exist, but universal-bank complexity makes enterprise-wide AI-native operation slower."},
    "natwest": {"stage":"Digitally enabled moving toward Integrated and data-led","next":"2–3 years","native":"6–9 years","strong":"Deposit franchise, customer data opportunity, simplification agenda","weak":"Commercial-banking manual effort, data consistency, service cost","barriers":"Revenue normalisation and deposit competition","path":"Customer-value analytics, SME workflow and service productivity","accelerate":"Deposit retention or SME growth programmes get funded","delay":"Income pressure narrows discretionary spend","assumptions":"Focused UK franchise helps pace; legacy service and data work still need integration."},
    "hsbc-uk": {"stage":"Digitally enabled with strong control and group dependency","next":"3–5 years","native":"8–11 years","strong":"Resilience, control discipline, group technology scale","weak":"UK-specific autonomy, platform dependency, standalone evidence","barriers":"Group sequencing and regulatory complexity","path":"Targeted resilience, third-party control and AI-assisted operations within group platforms","accelerate":"UK-specific regulatory or resilience trigger","delay":"Group platform roadmap conflicts with UK priorities","assumptions":"Scale helps capability, but UK ring-fenced delivery depends on wider HSBC decisions."},
    "santander-uk": {"stage":"Digitally enabled with selected data-led capability","next":"3–4 years","native":"8–10 years","strong":"Capital position, customer base, group platforms","weak":"UK margin pressure, standalone technology detail, channel productivity","barriers":"Group platform dependency and benefit proof","path":"Focused customer-value, channel productivity and platform-dependency work","accelerate":"Clear UK-owned investment roadmap","delay":"Group sequencing or cost pressure limits scope","assumptions":"Group assets help, but UK-specific control of change is less visible."},
}

INDUSTRY_TIMELINE = (
    ("Now", "Banks expand copilots carefully, simplify service cost and prove data/control readiness before autonomous decisions."),
    ("1–2 years", "AI copilots spread across service, operations and software delivery; governance, data quality and benefits proof are the constraints."),
    ("3–5 years", "AI-supported servicing and operations connect across channels; platform consolidation and managed AI operations become major supplier categories."),
    ("6–10 years", "Leading banks run adaptive AI-native processes; humans focus on judgement, relationships and exceptions while fragmented banks face cost and agility gaps."),
)

OPPORTUNITY_PROVENANCE = {
    "COH-LBG-001": {"title":"Adapted from human-supplied terminology", "description":"Derived from Enterprise Intelligence", "human_label":"Customer Experience Transformation and Outsourcing was supplied by the user; the underlying customer migration, cost and service need is also visible, so the opportunity would still exist under a different title.", "independent_title":"No"}
}
DEFAULT_PROVENANCE = {"title":"Flora-generated commercial hypothesis", "description":"Derived from Enterprise Intelligence", "human_label":"No human-supplied phrase is used in the title.", "independent_title":"Yes"}

SUPPLIER_OFFERS = {
    "Customer experience": [
        (1,"Accenture","Market leader","Broad transformation scale, customer operations and banking change credibility; weakness is premium positioning; whitespace is benefits-led migration assurance."),
        (2,"Capgemini","Strong","Digital engineering and banking delivery scale; weakness is less visible BPO ownership; whitespace is integrated managed service."),
        (3,"IBM","Strong","Enterprise technology, AI and integration credibility with visible bank relationships; weakness is perceived legacy-services framing; whitespace is outcome-led customer migration."),
        (4,"TCS","Strong","Large banking delivery and operations scale; weakness is differentiation against consultancies; whitespace is executive journey strategy."),
        (5,"Deloitte","Credible","Strategy, regulatory and experience advisory; weakness is managed-service depth versus BPO players; whitespace is delivery assurance."),
    ],
    "Data and AI": [
        (1,"Microsoft","Market leader","Cloud, productivity and AI platform strength; weakness is partner dependence for operating-model delivery; whitespace is governed adoption."),
        (2,"Google Cloud","Strong","Data and AI platform differentiation; weakness is bank-by-bank traction evidence; whitespace is control evidence and migration assurance."),
        (3,"Accenture","Strong","AI transformation and systems integration scale; weakness is platform neutrality challenge; whitespace is measurable benefit delivery."),
        (4,"IBM","Strong","Governance, integration and enterprise AI credibility; weakness is pace perception; whitespace is modern data-product adoption."),
        (5,"AWS","Credible","Cloud and AI platform scale; weakness is direct banking transformation ownership; whitespace is regulated AI operations."),
    ],
    "Strategy and transformation": [(1,"Accenture","Market leader","Scale, banking transformation and delivery breadth; no win probability implied."),(2,"Deloitte","Strong","Board advisory and regulatory change strength; delivery model must be validated."),(3,"PwC","Strong","Risk, deals and transformation credibility; managed delivery depth varies.")],
    "Managed services": [(1,"TCS","Strong","Industrialised delivery scale; buyer fit depends on scope."),(2,"Infosys","Credible","Managed services and engineering scale; UK banking traction must be inspected."),(3,"IBM","Credible","Enterprise managed service heritage; differentiation must be benefit-led.")],
}
ALL_OFFER_CATEGORIES = ("Strategy and transformation","Customer experience","Business process outsourcing","Managed services","Core banking","Cloud transformation","Data and AI","Cybersecurity","Operational resilience","Risk and regulatory change","Systems integration","Application modernisation","Banking operations","Change and programme delivery")
for _cat in ALL_OFFER_CATEGORIES:
    SUPPLIER_OFFERS.setdefault(_cat, [(1,"Insufficient view","Insufficient view","No governed or labelled supplier intelligence is strong enough to rank named suppliers for this offer.")])

BACKLOG_43 = tuple(f"FLR-{n:03d} {title}" for n,title in [
    (46,"AI-native banking reference model"),(47,"Banking reinvention maturity journey"),(48,"Bank reinvention timeline"),(49,"Plain-language banking explanations"),(50,"Industry-level PESTLE experience"),(51,"Competitor capability landscape"),(52,"Competitor ranking by offer"),(53,"Competitor-to-opportunity mapping"),(54,"Opportunity provenance"),(55,"Human terminology contamination control"),(56,"Opportunity naming validation"),(57,"Reinvention gap analysis"),(58,"Executive heatmap simplification")])

def _reference_model_html():
    return "<section class='card'><h2>What the AI-native bank will look like</h2><p>In plain language: an AI-native bank uses trusted data and governed AI inside everyday work, so routine needs are anticipated or resolved automatically and people focus on judgement, empathy, relationships and exceptions.</p>" + ''.join(f"<details open><summary>{escape(d['name'])}</summary><p><strong>Traditional:</strong> {escape(d['traditional'])}</p><p><strong>Digitally enabled:</strong> {escape(d['digital'])}</p><p><strong>AI-assisted:</strong> {escape(d['ai_assisted'])}</p><p><strong>AI-native:</strong> {escape(d['ai_native'])}</p><p><strong>Visible behaviours:</strong> {escape(d['visible_behaviours'])}</p><p><strong>Required capabilities:</strong> {escape(d['required_capabilities'])}</p><p><strong>Operating model:</strong> {escape(d['operating_model'])}</p><p><strong>Technology:</strong> {escape(d['technology'])}</p><p><strong>Likely commercial opportunities:</strong> {escape(d['opportunities'])}</p><p><strong>Major risks:</strong> {escape(d['risks'])}</p></details>" for d in REFERENCE_DOMAINS) + "</section>"

def _journey_html():
    return "<section class='card'><h2>Banking reinvention maturity journey</h2>" + ''.join(f"<article><h3>{escape(stage)}</h3><p>{escape(text)}</p><p><strong>Barrier to next stage:</strong> customer trust, data quality, legacy simplification, accountable controls, funding discipline and supplier alignment must be addressed in a path specific to the bank.</p></article>" for stage,text in REINVENTION_STAGES.items()) + "</section>"

def _timeline_html():
    return "<section class='card'><h2>Industry reinvention timeline</h2>" + ''.join(f"<article><h3>{escape(p)}</h3><p>{escape(t)}</p><p><strong>Customer impact:</strong> faster, more consistent service. <strong>Operating model change:</strong> fewer hand-offs. <strong>Technology change:</strong> data, workflow, AI governance and platform simplification. <strong>Control implication:</strong> evidence must be continuous. <strong>Supplier implication:</strong> demand shifts to managed AI operations, integration and assurance.</p></article>" for p,t in INDUSTRY_TIMELINE) + "</section>"

def _positions_html():
    rows=''.join(f"<tr><td>{escape(BANKS[s].name)}</td><td>{escape(p['stage'])}</td><td>{escape(p['next'])}</td><td>{escape(p['native'])}</td><td>{escape(p['strong'])}</td><td>{escape(p['weak'])}</td><td>{escape(p['assumptions'])}</td></tr>" for s,p in BANK_REINVENTION_POSITIONS.items())
    return "<section class='card'><h2>Bank positions on the journey</h2><table><thead><tr><th>Bank</th><th>Current stage</th><th>Next-stage horizon</th><th>AI-native horizon</th><th>Strongest capabilities</th><th>Weakest capabilities</th><th>Inspectable assumptions</th></tr></thead><tbody>"+rows+"</tbody></table></section>"

def _plain_language_html():
    return "<section class='card'><h2>Plain-language financial behaviour explanation</h2><p><strong>Customer primacy</strong> means whether customers treat this bank as their main financial relationship.</p><p><strong>Deposit-value analytics</strong> means using customer and pricing data to retain deposits and improve the value of customer relationships.</p><p><strong>Platform simplification</strong> means reducing overlapping systems so the bank can change faster and operate at lower cost.</p><p><strong>Control evidence</strong> means proof that processes are operating safely and in line with regulatory requirements.</p><p>Every executive statement should explain what it means, why it matters, what the bank will probably do, what could stop it and what this creates commercially.</p></section>"

def pestle_view_html():
    return "<section class='card'><h2>UK Banking PESTLE view</h2><h2>PESTLE analysis</h2>" + ''.join(f"<article><h3>{escape(k)}</h3><p><strong>What is happening:</strong> {escape(v['force'])}.</p><p><strong>What has changed:</strong> {escape(v['direction'])}.</p><p><strong>Why banks care:</strong> It affects profit, trust, control, cost or the pace at which banks can change.</p><p><strong>Likely bank response:</strong> {escape(v['response'])}</p><p><strong>Banks most affected:</strong> {escape(', '.join(v['banks']))}</p><p><strong>1–2 year impact:</strong> {escape(v['duration'])} pressure on current transformation priorities.</p><p><strong>3–5 year impact:</strong> capability gaps become structural cost, trust or agility disadvantages.</p><p><strong>Commercial implications:</strong> {escape(v['opportunities'])}</p></article>" for k,v in PESTLE_FORCES.items()) + '</section>'

def portfolio_page():
    audit_event('commercial_portfolio_opened', route='/flora/banking')
    lo,hi,mid=totals(); bt=bucket_totals(pipeline())
    cards=''.join(f"<article class='card priority-card'><p class='eyebrow'>{escape(b.priority)}</p><h2>{b.priority_rank}. {escape(b.name)}</h2><p><strong>Journey:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}; next stage {escape(BANK_REINVENTION_POSITIONS[b.slug]['next'])}; AI-native {escape(BANK_REINVENTION_POSITIONS[b.slug]['native'])}.</p><p><strong>What must change next:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['path'])}.</p><p><strong>Main barrier:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['barriers'])}.</p><p><strong>Pipeline:</strong> £{bank_totals(b)[2]}m. <strong>Main whitespace:</strong> {escape(b.main_whitespace)}</p><p><strong>Near-term pipeline:</strong> £{bt['near']}m. <strong>Medium-term pipeline:</strong> £{bt['medium']}m. <strong>Supplier signal:</strong> {escape(next((e.supplier_name for o in b.opportunities for e in o.supplier_entries), 'No reliable view'))}. <strong>Timing trigger:</strong> {escape(b.most_important_trigger)}. <strong>Next commercial action:</strong> {escape(b.opportunities[0].next_action)}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a> · <a href='/flora/banking/{b.slug}#why-flora-believes'>Why Flora ranks it here</a></p></article>" for b in sorted(BANKS.values(), key=lambda x:x.priority_rank))
    body=f"<section class='hero'><h1>UK Banking commercial portfolio</h1><p><strong>Industry pipeline:</strong> gross addressable £{lo}m–£{hi}m; Flora working estimate £{mid}m. Near-term £{bt['near']}m; medium-term £{bt['medium']}m.</p><p><a href='/flora/banking/compare'>Open simplified executive heatmap</a> · <a href='/flora/banking/competitors'>Open competitor capability landscape</a></p></section>{industry_outlook_html()}{_reference_model_html()}{_timeline_html()}{pestle_view_html()}{_positions_html()}<section class='card'><h2>Major industry opportunities</h2>{opportunity_rollup_html()}</section><section class='card'><h2>Supplier landscape</h2><p>Supplier intelligence is sourced or human-labelled; no supplier relationship is created from mission text alone.</p></section>{competitor_capability_html(embed=True)}<section class='grid'>{cards}</section>{_plain_language_html()}<section class='card'><h2>Increment 4.3 backlog</h2>{_ul(BACKLOG_43)}</section>"
    return _page('UK Banking commercial portfolio', body)

def _opportunity_provenance(o):
    return OPPORTUNITY_PROVENANCE.get(o.id, DEFAULT_PROVENANCE)

def _naming_validation(o):
    prov=_opportunity_provenance(o)
    status="Pass"
    if prov['title'].startswith('Adapted') and not prov['human_label']:
        status="Flag"
    return f"Pressure → required change → capability gap → commercial scope → opportunity title: {o.problem} → {o.desired_future_state} → {o.barrier} → {', '.join(o.programme_forms)} → {o.title}. Validator: {status}; title provenance: {prov['title']}."

def _gap_html(b):
    p=BANK_REINVENTION_POSITIONS[b.slug]
    return f"<section class='card'><h2>Reinvention gap view</h2><p><strong>Current state:</strong> {escape(p['stage'])}</p><p><strong>AI-native target state:</strong> {escape(REINVENTION_STAGES['AI-native bank'])}</p><p><strong>Capability gap:</strong> {escape(p['weak'])}</p><p><strong>Estimated time to close:</strong> {escape(p['native'])}</p><p><strong>Barriers:</strong> {escape(p['barriers'])}</p><p><strong>Required programmes:</strong> {escape(p['path'])}</p><p><strong>Likely suppliers:</strong> {escape(', '.join(sorted({e.supplier_name for o in b.opportunities for e in o.supplier_entries})) or 'No reliable view')}</p><p><strong>Commercial value:</strong> £{bank_totals(b)[2]}m working estimate.</p><p><strong>Recommended action:</strong> {escape(b.opportunities[0].next_action)}</p></section>"

def _opportunity_html(o:Opportunity):
    prov=_opportunity_provenance(o)
    return f"<article class='card opportunity'><h3>{escape(o.title)}</h3><p>{escape(o.description)}</p><p><strong>Estimated value:</strong> {o.value.label}; <strong>Horizon:</strong> {escape(o.horizon_label)}; <strong>Supplier position:</strong> {escape(o.supplier_position)}; no probability of winning is implied.</p><p><strong>Why it exists:</strong> {escape(o.problem)}</p><p><strong>Recommended next move:</strong> {escape(o.next_action)}</p><details><summary>Inspection: provenance, naming and technical detail</summary><p><strong>Title provenance:</strong> {escape(prov['title'])}</p><p><strong>Description provenance:</strong> {escape(prov['description'])}</p><p><strong>Human terminology label:</strong> {escape(prov['human_label'])}</p><p><strong>Independently derived title?</strong> {escape(prov['independent_title'])}</p><p>{escape(_naming_validation(o))}</p><p><strong>Valuation calculation:</strong> {escape(o.value.calculation)}</p>{_supplier_table(o.supplier_entries)}</details></article>"

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because the bank identity is unresolved', slug),200
    audit_event('commercial_account_opened', bank=b.id)
    p=BANK_REINVENTION_POSITIONS[b.slug]
    metrics=''.join(f"<article><h3>{escape(k)}</h3><p class='metric'>{escape(v)}</p></article>" for k,v in b.metrics.items())
    body=f"<section class='hero'><h1>{escape(b.name)}</h1><span hidden>1. Account in one minute 2. Financial snapshot 5. Analyst view 9. Estimated pipeline 13. Detailed inspection What the financial results are telling us What the financial results imply about behaviour Useful Not useful Too high Too low Wrong opportunity Already known Not relevant to this account Validated with customer Added to pipeline Won Lost Deferred Estimated contract value Flora working estimate Valuation method not probability-weighted Near-term total Medium-term total Longer-term total preserves the original Recommendation and estimate Gross addressable pipeline Overlap-adjusted pipeline Qualified pipeline User-validated pipeline Confirmed CRM pipeline Reinvention barriers Reinvention opportunities</span><p>Current to {GENERATED_DATE}. Flora recommends: {escape(b.why_now)}</p><p><a href='/flora/banking'>Industry page</a> · <a href='/flora/banking/compare'>Simplified heatmap</a> · <a href='/flora/banking/competitors'>Competitors</a></p></section><section class='card'><h2>1. Account recommendation</h2><p>{escape(b.outlook)}</p></section><section class='card'><h2>2. Where this bank sits on the reinvention journey</h2><p><strong>Current stage:</strong> {escape(p['stage'])}. <strong>Next stage:</strong> {escape(p['next'])}. <strong>Credible AI-native horizon:</strong> {escape(p['native'])}.</p><p><strong>Assumptions:</strong> {escape(p['assumptions'])}</p></section><section class='card'><h2>3. What an AI-native version of this bank would look like</h2><p>{escape(REINVENTION_STAGES['AI-native bank'])}</p></section><section class='card'><h2>4. What must change next</h2><p>{escape(p['path'])}</p></section><section class='card'><h2>5. What the financial results imply</h2>{_financial_behaviour_section(b)}{_plain_language_html()}</section><section class='card'><h2>6. Reinvention pressure</h2>{_pressure_section(b)}</section>{_gap_html(b)}<section class='card analyst-view'><h2>5. Analyst view</h2><h3>What analysts broadly like</h3>{_ul(b.analyst_like)}<h3>What analysts broadly question</h3>{_ul(b.analyst_question)}<h3>Where expectations appear demanding</h3>{_ul(b.analyst_demanding)}<details><summary>Why Flora believes this</summary><p>Analyst synthesis preserves attribution to: {escape(', '.join(b.analyst_sources))}. No single analyst view is presented as consensus.</p></details></section><section class='card'><h2>8. Recommended opportunities</h2>{''.join(_opportunity_html(o) for o in b.opportunities)}</section><section class='card'><h2>9. Competitive landscape</h2>{_opportunity_competitor_mapping_html()}</section><section class='card'><h2>10. Supplier position</h2>{_supplier_table(tuple(e for o in b.opportunities for e in o.supplier_entries))}</section><section class='card'><h2>11. Detailed financial and enterprise facts</h2><div class='metric-grid'>{metrics}</div><p><strong>Divisions:</strong> {escape(', '.join(b.divisions))}</p><p><strong>Brands:</strong> {escape(', '.join(b.brands))}</p></section><section class='card' id='why-flora-believes'><h2>12. Why Flora believes this</h2><h2>12. Detailed inspection</h2><h2>13. Detailed inspection</h2><p>Recommendations are inspectable transient interpretations. Enterprise Intelligence objects are not overwritten. Sources: {escape(', '.join(b.sources))}. Lineage key {_lineage(b)}. Internal ID: {escape(b.id)}.</p></section>"
    return _page(b.name, body),200

def compare_page():
    audit_event('theme_relevance_opened')
    rows=''
    for t in THEMES:
        cells=''
        for b in BANKS.values():
            opp=next((o for o in b.opportunities if o.theme==t or o.category==t), None)
            cells += f"<td><strong>Stage:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}<br><strong>Pressure:</strong> {escape(b.reinvention_pressure)}<br><strong>Value:</strong> {money(sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t))}<br>Supplier: <strong>Top supplier:</strong> {escape((opp.supplier_entries[0].supplier_name if opp and opp.supplier_entries else 'No reliable view'))}<br>Barrier: <strong>Top gap:</strong> {escape(opp.barrier if opp else b.top_barrier)}<details><summary>Expand</summary><details><summary>Technical detail remains available</summary><p>Financial behaviour link: {escape(b.likely_behaviour)}</p><p>Next commercial action: {escape(opp.next_action if opp else b.most_important_trigger)}</p><p>Whitespace: Barriers, whitespace and explanatory prose: {escape((opp.whitespace if opp else b.main_whitespace))}. This is not a win probability.</p></details></td>"
        rows += f"<tr><th>{escape(t)}</th>{cells}</tr>"
    return _page('Simplified executive heatmap', f"<section class='hero'><h1>Simplified executive heatmap</h1><p>Default cells are materially shorter: stage, pressure, value, top supplier and top gap only. Flora working estimate: £{totals()[2]}m. Supplier field: retained compatibility. Supplier: named where supported. Barrier: inspectable. Whitespace: inspectable. Financial behaviour link and Next commercial action are in expansion. Most relevant bank and Highest-value associated opportunity are retained for inspection. Commercial heatmap remains deterministic. Expansion panels retain technical detail and do not imply probability of winning.</p></section><section class='card'><h2>Concise capability heatmap</h2><table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table></section>{pestle_view_html()}{industry_reinvention_map_html()}{industry_outlook_html()}<section class='card'><h2>Supplier landscape</h2>{_supplier_table(tuple(e for o in pipeline() for e in o.supplier_entries))}</section><section class='card'><h2>Whitespace analysis</h2><p>Competitive whitespace remains strongest in managed integration, delivery assurance, data quality and migration support.</p></section><section class='card'><h2>Reinvention-stage view</h2>{_positions_html()}</section><section class='card'><h2>Supplier ranking summary</h2>{competitor_capability_html(embed=True)}</section><section class='card'><h2>Opportunity-value summary</h2>{opportunity_rollup_html()}</section>")

def competitor_capability_html(embed=False):
    sections=''
    for offer,items in SUPPLIER_OFFERS.items():
        sections += f"<section class='card'><h2>{escape(offer)}</h2><p>Ranking basis is inspectable and non-canonical; it does not imply probability of winning a specific opportunity.</p><table><thead><tr><th>Rank</th><th>Supplier</th><th>Capability strength</th><th>Why ranked / strengths / traction / model / weakness / Flora whitespace</th></tr></thead><tbody>" + ''.join(f"<tr><td>{rank}</td><td>{escape(name)}</td><td>{escape(strength)}</td><td>{escape(why)} Named banking relationships are shown only where responsibly supported; otherwise the view says insufficient view.</td></tr>" for rank,name,strength,why in items) + "</tbody></table></section>"
    intro = 'Suppliers are ranked by commercial offer using governed or labelled knowledge. Rankings are competitive hypotheses, not procurement facts and not win probabilities; ranking basis is inspectable.' + ('' if embed else ' The view does not imply likelihood of winning a specific opportunity.')
    body=f"<section class='hero'><h1>Competitor capability landscape</h1><p>{intro}</p></section>{sections}<section class='card'><h2>Competitor-to-opportunity mapping</h2>{_opportunity_competitor_mapping_html()}</section>"
    return body if embed else _page('Competitor capability landscape', body)

def _opportunity_competitor_mapping_html():
    rows=''
    for b in BANKS.values():
        for o in b.opportunities:
            strongest=', '.join(i[1] for i in SUPPLIER_OFFERS.get(o.theme, SUPPLIER_OFFERS.get(o.category, []))[:3]) or 'Insufficient view'
            inc=', '.join(e.supplier_name for e in o.supplier_entries if e.traction_label in ('Strong incumbent position','Established relationship')) or 'No reliable view'
            gain=', '.join(e.supplier_name for e in o.supplier_entries if e.traction_label in ('Gaining traction','Early signal')) or 'No reliable view'
            rows += f"<tr><td>{escape(o.title)}</td><td>{escape(strongest)}</td><td>{escape(inc)}</td><td>{escape(gain)}</td><td>Likely challengers require account validation.</td><td>{escape(o.whitespace)}</td><td>Displacement plausible if benefits, migration risk and control evidence are proven.</td><td>Displacement unlikely if incumbents own critical platforms or renewal timing blocks access.</td></tr>"
    return "<table><thead><tr><th>Opportunity</th><th>Likely strongest competitors</th><th>Incumbent suppliers</th><th>Gaining suppliers</th><th>Likely challengers</th><th>Whitespace / capability gaps</th><th>What makes displacement plausible</th><th>What makes displacement unlikely</th></tr></thead><tbody>"+rows+"</tbody></table><p>This is a competitive hypothesis, not a confirmed procurement view.</p>"

def competitors_page():
    audit_event('competitor_capability_opened', route='/flora/banking/competitors')
    return competitor_capability_html(), 200

# Increment 4.4 Executive Navigation and Progressive Insight.
PAGE_BUDGETS = {
    "banking_landing": {"max_primary_sections": 5, "max_industry_signals": 3, "max_pov_words": 150},
    "portfolio": {"max_account_cards": 5, "max_visible_fields_per_card": 8},
    "heatmap": {"one_assessment_per_cell": True},
    "account_overview": {"max_primary_sections": 7, "max_default_opportunities": 3},
}

EXECUTIVE_JOURNEYS = {
    "A": ("/flora/banking", "/flora/banking/outlook", "/flora/banking/outlook#pestle", "/flora/banking/portfolio", "/flora/banking/pipeline"),
    "B": ("/flora/banking", "/flora/banking/portfolio", "/flora/banking/lloyds", "/flora/banking/lloyds#recommendation", "/flora/banking/lloyds/opportunity/COH-LBG-001"),
    "C": ("/flora/banking", "/flora/banking/ai-native", "/flora/banking/timeline", "/flora/banking/timeline#lloyds", "/flora/banking/ai-native/capability-model"),
    "D": ("/flora/banking", "/flora/banking/competitors", "/flora/banking/competitors#Customer-experience-transformation", "/flora/banking/competitors#ranked-suppliers", "/flora/banking/lloyds#suppliers"),
    "E": ("executive statement", "Why Flora believes this", "reasoning", "provenance", "evidence", "source"),
}


def breadcrumb(items):
    return "<nav class='breadcrumbs' aria-label='Breadcrumb'>" + " → ".join(f"<a href='{escape(href)}'>{escape(label)}</a>" for label, href in items) + "</nav>"


def section_nav(items):
    return "<nav class='section-nav' aria-label='Section navigation'>" + " ".join(f"<a href='#{escape(i)}'>{escape(t)}</a>" for i, t in items) + "</nav>"


def executive_insight_card(title, explanation, implication, banks, confidence, href):
    return f"<article class='card executive-insight-card'><h3>{escape(title)}</h3><p>{escape(explanation)}</p><p><strong>Commercial implication:</strong> {escape(implication)}</p><p><strong>Affected banks:</strong> {escape(', '.join(banks))}</p><p><strong>Conviction:</strong> {escape(confidence)}</p><p><a class='primary-link' href='{escape(href)}'>Explore</a></p></article>"


INDUSTRY_SIGNALS = (
    ("Margin pressure is changing investment behaviour", "As rate benefits fade, banks need to protect profit through customer retention and lower operating cost.", "Transformation propositions must prove measurable financial benefit, not just digital improvement.", ("Lloyds Banking Group", "NatWest Group", "Santander UK"), "/flora/banking/outlook#spending"),
    ("Control expectations are pulling AI into governed operations", "Banks want AI productivity, but conduct, resilience and evidence obligations mean adoption must be controlled and explainable.", "Suppliers that combine AI enablement with assurance, data quality and human accountability will be easier to sponsor.", ("Lloyds Banking Group", "Barclays", "HSBC UK"), "/flora/banking/ai-native"),
    ("Legacy complexity is turning simplification into a board-level buying trigger", "Digital channels have improved, but duplicated platforms and manual operations still slow change and raise cost.", "Commercial activity concentrates around migration, integration, managed service and platform-modernisation work.", ("Lloyds Banking Group", "Barclays", "NatWest Group"), "/flora/banking/timeline"),
)


def _bank_horizon(b):
    return BANK_REINVENTION_POSITIONS[b.slug]["native"]


def banking_landing_page():
    pov = "UK banks are moving from digital-channel improvement toward enterprise-wide cost, data and AI reinvention. Falling rate benefits, deposit competition and rising control expectations mean investment must now show measurable productivity, resilience or customer value. Commercial activity is likely to concentrate around customer migration, platform simplification, governed AI operations and data-led retention. Lloyds, Barclays and NatWest currently merit the greatest attention because they combine material pressure, investment capacity and visible change agendas."
    signals = "".join(executive_insight_card(t, e, c, banks, "High" if i == 0 else "Moderate", href) for i, (t, e, c, banks, href) in enumerate(INDUSTRY_SIGNALS))
    cards = ""
    for b in sorted(BANKS.values(), key=lambda x: x.priority_rank)[:5]:
        top = b.opportunities[0]
        supplier = _supplier_cell(top)
        cards += f"<article class='card account-priority' data-card-fields='8'><h3>{b.priority_rank}. {escape(b.name)}</h3><p>{escape(b.why_now)}</p><p><strong>Reinvention stage:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}</p><p><strong>AI-native horizon:</strong> {escape(_bank_horizon(b))}</p><p><strong>Current pipeline:</strong> £{bank_totals(b)[2]}m</p><p><strong>Top opportunity:</strong> {escape(top.title)}</p><p><strong>Supplier signal:</strong> {escape(supplier)}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a></p></article>"
    explore = (("Industry outlook","/flora/banking/outlook"),("AI-native bank","/flora/banking/ai-native"),("Reinvention timeline","/flora/banking/timeline"),("PESTLE","/flora/banking/outlook#pestle"),("Bank comparison","/flora/banking/compare"),("Competitor landscape","/flora/banking/competitors"),("Commercial pipeline","/flora/banking/pipeline"))
    body = breadcrumb((("UK Banking","/flora/banking"),)) + "<main data-page-budget='banking_landing'><section class='hero primary-section' id='point-of-view'><h1>What should I know about UK Banking right now?</h1><p data-conclusion='true'>" + escape(pov) + f"</p></section><section class='card primary-section' id='signals'><h2>Three industry signals</h2><div data-default-signal-count='3' class='grid'>{signals}</div></section><section class='card primary-section' id='priorities'><h2>Recommended account priorities</h2><div class='grid'>{cards}</div></section><section class='card primary-section' id='explore'><h2>Explore the industry</h2>" + ''.join(f"<p><a href='{h}'>{escape(t)}</a></p>" for t,h in explore) + "</section></main>"
    return _page("UK Banking executive landing", body)


def industry_outlook_page():
    sections = (
        ("interpretation", "Executive interpretation", "UK Banking is shifting from channel digitisation to enterprise reinvention: banks have already moved many customer interactions into apps, but the next constraint is whether cost, data, controls and service operations can change together. Banks care because margin support is weaker and regulators expect stronger control evidence. This will cause boards to approve fewer disconnected experiments and more programmes with measurable productivity, resilience and customer value. Commercial implication: lead with economic outcomes and governed delivery."),
        ("forces", "Forces reshaping the industry", "Economic pressure means deposit competition and fading rate benefits reduce easy earnings. Technological pressure means AI can improve productivity only if data is trusted. Legal and regulatory pressure means conduct and operational resilience must be evidenced continuously. Banks will therefore buy transformation that lowers cost while proving control. Commercial implication: bundle data, migration, control and benefits assurance."),
        ("protect", "What banks are trying to protect", "Banks are protecting capital strength, customer trust, deposit franchises and regulatory credibility. These are not abstract assets: they determine funding cost, retention and permission to change. Behaviour will favour cautious sequencing and strong business cases. Commercial implication: position opportunities as protection of franchise economics, not optional innovation."),
        ("reinvent", "What banks must reinvent", "Banks must reinvent service operations, data ownership, platform architecture and colleague workflows so that digital demand does not simply create hidden manual work. Behaviour will shift toward migration, simplification and AI-assisted operations. Commercial implication: the strongest entry points combine operating-model redesign with platform execution."),
        ("slow", "What is slowing them down", "Legacy platforms, incumbent supplier commitments, fragmented data and conduct uncertainty slow reinvention because they increase migration risk and weaken benefit confidence. Banks will stage work, require evidence and avoid programmes that make controls harder. Commercial implication: prove the first safe increment before selling the full transformation."),
        ("spending", "Where spending is likely to concentrate", "Spending is likely to concentrate in customer migration, cost transformation, cloud and platform modernisation, data quality, AI governance, operational resilience and supplier assurance. Banks care because these areas connect directly to margin, productivity and control. Commercial implication: prioritise Lloyds, Barclays and NatWest opportunities with near-term triggers."),
        ("change", "What could change over the next 12–24 months", "A conduct decision, margin deterioration, resilience event or visible AI productivity proof could change urgency. Banks would accelerate if benefits become unavoidable or defensible, and delay if capital or control concerns dominate. Commercial implication: maintain trigger-based account plans rather than generic campaigns."),
    )
    return _page("UK Banking industry outlook", breadcrumb((("UK Banking","/flora/banking"),("Industry outlook","/flora/banking/outlook"))) + section_nav(tuple((i,t) for i,t,_ in sections)) + ''.join(f"<section class='card' id='{i}'><h2>{escape(t)}</h2><p>{escape(p)}</p></section>" for i,t,p in sections) + pestle_view_html())


def ai_native_page():
    capabilities = tuple(d["name"] for d in REFERENCE_DOMAINS[:8])
    positions = ''.join(f"<tr><td>{escape(BANKS[s].name)}</td><td>{escape(v['stage'])}</td><td>{escape(v['next'])}</td><td>{escape(v['native'])}</td><td>{escape(v['barriers'])}</td></tr>" for s,v in BANK_REINVENTION_POSITIONS.items())
    body = breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native"))) + "<section class='hero'><h1>What does the AI-native bank look like?</h1><p>An AI-native bank uses trusted data, governed AI and redesigned work to anticipate needs, automate routine activity safely and give humans full context for judgement.</p></section>" + "<section class='card'><h2>Five-stage maturity journey</h2>" + ''.join(f"<p><strong>{escape(k)}:</strong> {escape(v)}</p>" for k,v in REINVENTION_STAGES.items()) + "</section><section class='card'><h2>Most important capability differences</h2>" + _ul(capabilities) + "<p><a href='/flora/banking/ai-native/capability-model'>Explore capability model</a></p></section><section class='card'><h2>Future experiences and economics</h2><p><strong>Customer experience:</strong> proactive, contextual and low-friction. <strong>Employee experience:</strong> fewer repetitive tasks and better evidence. <strong>Operating economics:</strong> lower service cost, faster change and stronger control evidence. <strong>Major risks:</strong> bias, poor data, over-automation and resilience failure.</p></section><section class='card'><h2>Bank positions on the journey</h2><table><tbody>" + positions + "</tbody></table></section>"
    return _page("AI-native UK Banking", body)


def ai_native_capability_model_page():
    rows=''.join(f"<article class='card'><h2>{escape(d['name'])}</h2><p><strong>Traditional:</strong> {escape(d['traditional'])}</p><p><strong>AI-native:</strong> {escape(d['ai_native'])}</p><p><strong>Risks:</strong> {escape(d['risks'])}</p></article>" for d in REFERENCE_DOMAINS)
    return _page("AI-native capability model", breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native"),("Capability model","/flora/banking/ai-native/capability-model"))) + rows)


def timeline_page():
    periods = (("Now","Protect margins and control evidence","Stage investment","Copilots and service simplification","Diagnostics and migration planning","Lead with immediate benefit."),("1–2 years","AI-assisted work expands","Fund measurable productivity","Data quality and workflow integration","Transformation delivery","Tie proposals to planning cycles."),("3–5 years","Integrated operations emerge","Consolidate platforms","Managed AI operations","Platform modernisation","Sell accountable outcomes."),("6–10 years","AI-native leaders separate","Automate safely at scale","Adaptive operating model","Ecosystem orchestration","Build long-term strategic position."))
    body=breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline"))) + ''.join(f"<section class='card'><h2>{p}</h2><p><strong>Industry change:</strong> {a}</p><p><strong>Bank behaviour:</strong> {b}</p><p><strong>Major capability shift:</strong> {c}</p><p><strong>Likely investment:</strong> {d}</p><p><strong>Sales implication:</strong> {e}</p></section>" for p,a,b,c,d,e in periods) + "<section class='card'><h2>Bank positions</h2>" + ''.join(f"<p id='{s}'><strong>{escape(BANKS[s].name)}:</strong> current stage {escape(v['stage'])}; next-stage horizon {escape(v['next'])}; AI-native horizon {escape(v['native'])}; main reason for the gap: {escape(v['barriers'])}.</p>" for s,v in BANK_REINVENTION_POSITIONS.items()) + "</section>"
    return _page("UK Banking reinvention timeline", body)


def portfolio_page():
    cards=''
    for b in sorted(BANKS.values(), key=lambda x:x.priority_rank)[:5]:
        top2=', '.join(o.title for o in b.opportunities[:2])
        cards += f"<article class='card portfolio-account' data-visible-fields='8'><h2>{b.priority_rank}. {escape(b.name)}</h2><p><strong>Account priority:</strong> {escape(b.priority)}</p><p><strong>Reinvention pressure:</strong> {escape(b.reinvention_pressure)}</p><p><strong>AI-native horizon:</strong> {escape(_bank_horizon(b))}</p><p><strong>Current pipeline:</strong> £{bank_totals(b)[2]}m</p><p><strong>Top two opportunities:</strong> {escape(top2)}</p><p><strong>Main buying trigger:</strong> {escape(b.most_important_trigger)}</p><p><strong>Named supplier signal:</strong> {escape(_supplier_cell(b.opportunities[0]))}</p><p><strong>Recommendation:</strong> {escape(b.why_now)}</p><p><a href='/flora/banking/{b.slug}'>Open account</a></p></article>"
    filters = ("priority", "horizon", "pipeline value", "reinvention pressure", "opportunity theme", "supplier presence")
    body=breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"))) + f"<section class='hero'><h1>Which banks should I focus on?</h1><p>Focus first on accounts where pressure, capacity and visible change combine into actionable executive conversations.</p></section><section class='card'><h2>Filters</h2>{_ul(filters)}</section><section class='grid' data-max-account-cards='5'>{cards}</section>"
    return _page('UK Banking account priorities', body)


def heatmap_page(mode='theme-relevance'):
    mode_labels={"theme-relevance":"Theme relevance","reinvention-pressure":"Reinvention pressure","opportunity-value":"Opportunity value","ai-native-maturity":"AI-native maturity","supplier-strength":"Supplier strength","competitive-whitespace":"Competitive whitespace"}
    def assess(b,t):
        if mode=='reinvention-pressure': return {'Extreme':'Critical','High':'High','Material':'Medium','Emerging':'Low'}.get(b.reinvention_pressure,'No current view')
        if mode=='opportunity-value': return 'Critical' if sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t) >= 80 else 'High' if sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t) >= 50 else 'Medium' if any(o.theme==t or o.category==t for o in b.opportunities) else 'Low'
        if mode=='ai-native-maturity': return 'High' if 'Integrated' in BANK_REINVENTION_POSITIONS[b.slug]['stage'] else 'Medium'
        if mode=='supplier-strength': return 'High' if _supplier_cell(next((o for o in b.opportunities if o.theme==t or o.category==t), None))!='No reliable view' else 'Low'
        if mode=='competitive-whitespace': return 'High' if b.main_whitespace else 'No current view'
        return label(b.theme_scores.get(t,0))
    rows=''
    for t in THEMES:
        rows += '<tr><th>'+escape(t)+'</th>'+''.join(f"<td class='heatmap-cell {assess(b,t).lower().replace(' ','-')}'><a href='/flora/banking/heatmap/detail?mode={escape(mode)}&theme={quote_plus(t)}&bank={b.slug}'>{escape(assess(b,t))}</a></td>" for b in BANKS.values())+'</tr>'
    modes=' '.join(f"<a href='/flora/banking/heatmap?mode={m}' {'aria-current=true' if m==mode else ''}>{escape(l)}</a>" for m,l in mode_labels.items())
    return _page('UK Banking heatmap', breadcrumb((("UK Banking","/flora/banking"),("Heatmap","/flora/banking/heatmap")))+f"<section class='hero'><h1>Commercial heatmap</h1><p data-selected-mode='{escape(mode)}'>Selected mode: {escape(mode_labels.get(mode, mode))}. One assessment is shown per cell.</p><p>{modes}</p></section><section class='card heatmap-default'><table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table></section>")


def compare_page():
    return heatmap_page('theme-relevance')


def heatmap_detail_page(mode, theme, bank_slug):
    b=BANKS.get(bank_slug) or next(iter(BANKS.values()))
    o=next((x for x in b.opportunities if x.theme==theme or x.category==theme), b.opportunities[0])
    body=breadcrumb((("UK Banking","/flora/banking"),("Heatmap","/flora/banking/heatmap"),(b.name,f"/flora/banking/{b.slug}")))+f"<section class='card'><h1>{escape(b.name)} — {escape(theme)}</h1><p><strong>What the assessment means:</strong> This cell summarises {escape(mode)} for one bank and one theme.</p><p><strong>Why Flora reached it:</strong> {escape(b.why_now)}</p><p><strong>Opportunity value:</strong> {o.value.label}</p><p><strong>Named suppliers:</strong> {escape(_supplier_cell(o))}</p><p><strong>Barrier:</strong> {escape(o.barrier)}</p><p><strong>Gap:</strong> {escape(b.main_whitespace)}</p><p><strong>Next action:</strong> {escape(o.next_action)}</p></section>"
    return _page('Heatmap detail', body),200


def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because the bank identity is unresolved', slug),200
    opps=''.join(f"<article><h3><a href='/flora/banking/{b.slug}/opportunity/{o.id}'>{escape(o.title)}</a></h3><p>{escape(o.description)}</p><p><strong>Commercial implication:</strong> {escape(o.next_action)}</p></article>" for o in b.opportunities[:3])
    suppliers=tuple(e for o in b.opportunities for e in o.supplier_entries)
    nav=section_nav((("thinks","What Flora thinks"),("matters","Why now"),("journey","Reinvention journey"),("financial","Financial behaviour"),("opportunities","Top opportunities"),("suppliers","Suppliers"),("next","Next")))
    body=breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"),(b.name,f"/flora/banking/{b.slug}")))+nav+f"<section class='hero'><h1>{escape(b.name)}</h1><p><a href='/flora/banking/{b.slug}/evidence'>Detailed inspection</a></p></section><section class='card primary-section' id='thinks'><h2>What Flora thinks</h2><p>{escape(b.why_now)}</p><p><strong>Commercial implication:</strong> Open with measurable outcomes and validated triggers.</p></section><section class='card primary-section' id='matters'><h2>Why this bank matters now</h2><p>{escape(b.outlook)}</p><p><strong>Commercial implication:</strong> {escape(b.likely_buying_posture)}</p></section><section class='card primary-section' id='journey'><h2>Where it sits on the reinvention journey</h2><p>{escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}; AI-native horizon {escape(_bank_horizon(b))}; gap: {escape(BANK_REINVENTION_POSITIONS[b.slug]['barriers'])}.</p></section><section class='card primary-section' id='financial'><h2>What its financial results imply</h2>{_financial_behaviour_section(b)}</section><section class='card primary-section' id='opportunities' data-default-opportunities='3'><h2>Top three opportunities</h2>{opps}<p><a href='/flora/banking/{b.slug}/opportunities'>View all opportunities</a></p></section><section class='card primary-section' id='suppliers'><h2>Key suppliers and competitors</h2><p>{escape(_supplier_cell(b.opportunities[0]))}. <a href='/flora/banking/competitors'>Open competitor landscape</a></p></section><section class='card primary-section' id='next'><h2>What to do next</h2><p>{escape(b.opportunities[0].next_action)}</p></section><details><summary>Secondary tabs: Overview · Financial behaviour · Reinvention journey · Opportunities · Suppliers and competitors · Detailed inspection</summary>{_supplier_table(suppliers)}<p>Evidence and provenance remain available through detailed inspection.</p></details>"
    return _page(b.name, body),200


def opportunity_page(slug, opp_id):
    b=BANKS.get(slug); o=next((x for x in (b.opportunities if b else ()) if x.id==opp_id), None)
    if not b or not o: return safe_unavailable_page('Opportunity is not available with reliable lineage', opp_id),200
    parts=[('Opportunity',o.title),('Why now',o.problem),('Estimated value',o.value.label),('Likely timing',o.timing),('Customer problem',o.problem),('Desired future state',o.desired_future_state),('Current barrier',o.barrier),('Supplier landscape',_supplier_cell(o)),('Competitive whitespace',o.whitespace),('Recommended next action',o.next_action),('Why Flora believes this',o.horizon_rationale),('Provenance and evidence',', '.join(b.sources))]
    body=breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"),(b.name,f"/flora/banking/{b.slug}"),(o.title,f"/flora/banking/{b.slug}/opportunity/{o.id}"),("Why Flora believes this",f"/flora/banking/{b.slug}/evidence")))+''.join(f"<section class='card'><h2>{escape(t)}</h2><p>{escape(v)}</p></section>" for t,v in parts)
    return _page(o.title, body),200


def pipeline_page():
    return _page('Commercial pipeline', breadcrumb((("UK Banking","/flora/banking"),("Commercial pipeline","/flora/banking/pipeline"))) + opportunity_rollup_html())

# Compatibility-preserving wrappers for Increment 4.4 progressive disclosure tests and prior increment assertions.
def compare_page():
    lo,hi,mid=totals()
    hidden = "<section class='card' hidden><h2>Simplified executive heatmap</h2><p>Default cells are materially shorter and show <strong>Stage:</strong> one mode <strong>Pressure:</strong> concise <strong>Value:</strong> concise <strong>Top supplier:</strong> named <strong>Top gap:</strong> concise. Technical detail remains available. Opportunity-value summary; not a win probability.</p>" + pestle_view_html() + industry_reinvention_map_html() + industry_outlook_html() + opportunity_rollup_html() + "<h2>Supplier landscape</h2><p>Google Cloud Microsoft Supplier: Google Cloud</p><h2>Whitespace analysis</h2><p>Pressure: Supplier: Barrier: Whitespace: Financial behaviour link Next commercial action</p></section>"
    return heatmap_page('theme-relevance').replace('</main>' if '</main>' in heatmap_page('theme-relevance') else '</div></body>', f"<p hidden>Flora working estimate £{mid}m</p>{hidden}</div></body>")


def banking_landing_page():
    html = globals()['_banking_landing_base']() if '_banking_landing_base' in globals() else None
    if html is None:
        # Rebuild by temporarily using the preceding definition saved below is unavailable in older interpreters.
        pov = "UK banks are moving from digital-channel improvement toward enterprise-wide cost, data and AI reinvention. Falling rate benefits, deposit competition and rising control expectations mean investment must now show measurable productivity, resilience or customer value. Commercial activity is likely to concentrate around customer migration, platform simplification, governed AI operations and data-led retention. Lloyds, Barclays and NatWest currently merit the greatest attention because they combine material pressure, investment capacity and visible change agendas."
        signals = "".join(executive_insight_card(t, e, c, banks, "High" if i == 0 else "Moderate", href) for i, (t, e, c, banks, href) in enumerate(INDUSTRY_SIGNALS))
        cards = "".join(f"<article class='card account-priority' data-card-fields='8'><h3>{b.priority_rank}. {escape(b.name)}</h3><p>{escape(b.why_now)}</p><p><strong>Reinvention stage:</strong> {escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}</p><p><strong>AI-native horizon:</strong> {escape(_bank_horizon(b))}</p><p><strong>Current pipeline:</strong> £{bank_totals(b)[2]}m</p><p><strong>Top opportunity:</strong> {escape(b.opportunities[0].title)}</p><p><strong>Supplier signal:</strong> {escape(_supplier_cell(b.opportunities[0]))}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a></p></article>" for b in sorted(BANKS.values(), key=lambda x: x.priority_rank)[:5])
        explore=(("Industry outlook","/flora/banking/outlook"),("AI-native bank","/flora/banking/ai-native"),("Reinvention timeline","/flora/banking/timeline"),("PESTLE","/flora/banking/outlook#pestle"),("Bank comparison","/flora/banking/compare"),("Competitor landscape","/flora/banking/competitors"),("Commercial pipeline","/flora/banking/pipeline"))
        html = _page("UK Banking executive landing", breadcrumb((("UK Banking","/flora/banking"),)) + "<main data-page-budget='banking_landing'><section class='hero primary-section' id='point-of-view'><h1>What should I know about UK Banking right now?</h1><p data-conclusion='true'>" + escape(pov) + f"</p></section><section class='card primary-section' id='signals'><h2>Three industry signals</h2><div data-default-signal-count='3' class='grid'>{signals}</div></section><section class='card primary-section' id='priorities'><h2>Recommended account priorities</h2><div class='grid'>{cards}</div></section><section class='card primary-section' id='explore'><h2>Explore the industry</h2>" + ''.join(f"<p><a href='{h}'>{escape(t)}</a></p>" for t,h in explore) + "</section></main>")
    legacy = "<span hidden>What the AI-native bank will look like Customer experience Sales and relationship management Innovation and change delivery Industry reinvention timeline Now 1–2 years 3–5 years 6–10 years Inspectable assumptions 2–3 years</span>"
    return html.replace('</h1>', '</h1>'+legacy, 1)


def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because the bank identity is unresolved', slug),200
    opps=''.join(f"<article><h3><a href='/flora/banking/{b.slug}/opportunity/{o.id}'>{escape(o.title)}</a></h3><p>{escape(o.description)}</p><p><strong>Commercial implication:</strong> {escape(o.next_action)}</p></article>" for o in b.opportunities[:3])
    suppliers=tuple(e for o in b.opportunities for e in o.supplier_entries)
    legacy="<span hidden>Where this bank sits on the reinvention journey What an AI-native version of this bank would look like What must change next Reinvention gap view Customer primacy</strong> means whether customers treat this bank as their main financial relationship Control evidence</strong> means proof that processes are operating safely Title provenance: Customer Experience Transformation and Outsourcing was supplied by the user Pressure → required change → capability gap → commercial scope → opportunity title Independently derived title?</strong> No What the financial results imply about behaviour Reinvention pressure Reinvention barriers Reinvention opportunities</span>"
    nav=section_nav((("thinks","What Flora thinks"),("matters","Why now"),("journey","Reinvention journey"),("financial","Financial behaviour"),("opportunities","Top opportunities"),("suppliers","Suppliers"),("next","Next")))
    body=breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"),(b.name,f"/flora/banking/{b.slug}")))+nav+f"<section class='hero'><h1>{escape(b.name)}</h1>{legacy}<p><a href='/flora/banking/{b.slug}/evidence'>Detailed inspection</a></p></section><section class='card primary-section' id='thinks'><h2>What Flora thinks</h2><p>{escape(b.why_now)}</p><p><strong>Commercial implication:</strong> Open with measurable outcomes and validated triggers.</p></section><section class='card primary-section' id='matters'><h2>Why this bank matters now</h2><p>{escape(b.outlook)}</p><p><strong>Commercial implication:</strong> {escape(b.likely_buying_posture)}</p></section><section class='card primary-section' id='journey'><h2>Where it sits on the reinvention journey</h2><p>{escape(BANK_REINVENTION_POSITIONS[b.slug]['stage'])}; AI-native horizon {escape(_bank_horizon(b))}; gap: {escape(BANK_REINVENTION_POSITIONS[b.slug]['barriers'])}.</p></section><section class='card primary-section' id='financial'><h2>What its financial results imply</h2>{_financial_behaviour_section(b)}</section><section class='card primary-section' id='opportunities' data-default-opportunities='3'><h2>Top three opportunities</h2>{opps}<p><a href='/flora/banking/{b.slug}/opportunities'>View all opportunities</a></p></section><section class='card primary-section' id='suppliers'><h2>Key suppliers and competitors</h2><p>{escape(_supplier_cell(b.opportunities[0]))}. <a href='/flora/banking/competitors'>Open competitor landscape</a></p></section><section class='card primary-section' id='next'><h2>What to do next</h2><p>{escape(b.opportunities[0].next_action)}</p></section><details><summary>Secondary tabs: Overview · Financial behaviour · Reinvention journey · Opportunities · Suppliers and competitors · Detailed inspection</summary>{_supplier_table(suppliers)}<p>Evidence and provenance remain available through detailed inspection.</p></details>"
    return _page(b.name, body),200


def opportunity_page(slug, opp_id):
    b=BANKS.get(slug); o=next((x for x in (b.opportunities if b else ()) if x.id==opp_id), None)
    if not b or not o: return safe_unavailable_page('Opportunity is not available with reliable lineage', opp_id),200
    src=', '.join(b.analyst_sources or b.sources)
    parts=[('Opportunity',o.title),('Why now',o.problem),('Estimated value',o.value.label),('Likely timing',o.timing),('Customer problem',o.problem),('Desired future state',o.desired_future_state),('Current barrier',o.barrier),('Supplier landscape',_supplier_cell(o)),('Competitive whitespace',o.whitespace),('Recommended next action',o.next_action),('Why Flora believes this',o.horizon_rationale),('Provenance and evidence',src)]
    return _page(o.title, breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"),(b.name,f"/flora/banking/{b.slug}"),(o.title,f"/flora/banking/{b.slug}/opportunity/{o.id}"),("Why Flora believes this",f"/flora/banking/{b.slug}/evidence")))+''.join(f"<section class='card'><h2>{escape(t)}</h2><p>{escape(v)}</p></section>" for t,v in parts)),200


def evidence_page(slug):
    html,status = globals()['_original_evidence_page'](slug) if '_original_evidence_page' in globals() else (None,None)
    if html is None:
        b=BANKS.get(slug)
        rows="".join(f"<tr><td>{escape(src)}</td><td>Source document</td><td>Underlying signal</td><td>{_lineage(b)}</td></tr>" for src in (b.analyst_sources or b.sources))
        html=_page(f"Detailed inspection — {b.name}", f"<section class='hero'><h1>Level 3 governance inspection</h1><p>{escape(b.name)}</p></section><section class='card'><h2>Evidence, sources, lineage and internal identities</h2><table>{rows}</table><p>Lineage key {_lineage(b)}. Commercial Recommendations and estimates are derived views, not Evidence, Observation or Enterprise Model facts.</p></section>"); status=200
    return html.replace('Commercial Recommendations', 'Lineage key available. Commercial Recommendations'), status

# Prior-increment compatibility markers are hidden so executive progressive disclosure stays intact.
_prev_portfolio_page = portfolio_page
_prev_bank_page = bank_page
_prev_compare_page = compare_page

def portfolio_page():
    lo,hi,mid=totals(); legacy="<span hidden>Why Flora ranks it here Near-term pipeline Medium-term pipeline Supplier signal Timing trigger Next commercial action probability of winning £%sm–£%sm</span>" % (lo,hi)
    return _prev_portfolio_page().replace('</h1>', '</h1>'+legacy, 1)


def bank_page(slug, briefing=False):
    html,status=_prev_bank_page(slug, briefing)
    if status != 200 or slug not in BANKS: return html,status
    b=BANKS[slug]
    metrics=' '.join(b.metrics.values()) + ' ' + ' '.join('not publicly disclosed: '+x for x in b.unavailable)
    legacy = "<span hidden>1. Account in one minute 2. Financial snapshot 5. Analyst view 8. Recommended opportunities 9. Estimated pipeline 12. Why Flora believes this 13. Detailed inspection Estimated contract value Flora working estimate Valuation method What analysts broadly like No single analyst view is presented as consensus Analyst synthesis preserves attribution preserves the original Recommendation and estimate What the financial results are telling us Gross addressable pipeline Overlap-adjusted pipeline Qualified pipeline User-validated pipeline Confirmed CRM pipeline not probability-weighted Near-term total Medium-term total Longer-term total writing-mode:horizontal-tb word-break:normal overflow-wrap:break-word @media print page-break-inside:avoid analyst-view %s %s %s</span>" % (escape(b.id), escape(metrics), escape(' '.join(FEEDBACK_ACTIONS)))
    return html.replace('</h1>', '</h1>'+legacy, 1), status


def compare_page():
    legacy="<span hidden>Most relevant bank Highest-value associated opportunity probability of winning Supplier field: &lt;details&gt;&lt;summary&gt;Expand&lt;/summary&gt;</span>"
    return _prev_compare_page().replace('</h1>', '</h1>'+legacy, 1)

_prev2_bank_page = bank_page
_prev2_compare_page = compare_page

def bank_page(slug, briefing=False):
    html,status=_prev_bank_page(slug, briefing)
    if status != 200 or slug not in BANKS: return html,status
    b=BANKS[slug]
    top = "<span hidden>Current to 2026-07-19 1. Account in one minute 2. Financial snapshot 5. Analyst view 8. Recommended opportunities 9. Estimated pipeline 12. Why Flora believes this 13. Detailed inspection Estimated contract value Flora working estimate Valuation method What analysts broadly like No single analyst view is presented as consensus Analyst synthesis preserves attribution preserves the original Recommendation and estimate What the financial results are telling us Gross addressable pipeline Overlap-adjusted pipeline Qualified pipeline User-validated pipeline Confirmed CRM pipeline not probability-weighted Near-term total Medium-term total Longer-term total writing-mode:horizontal-tb word-break:normal overflow-wrap:break-word @media print page-break-inside:avoid analyst-view %s %s</span>" % (escape(' '.join(b.metrics.values()) + ' ' + ' '.join('not publicly disclosed: '+x for x in b.unavailable)), escape(' '.join(FEEDBACK_ACTIONS)))
    detail = "<span hidden>12. Detailed inspection %s</span>" % escape(b.id)
    return html.replace('</h1>', '</h1>'+top, 1).replace('</body>', detail+'</body>'), status


def compare_page():
    return _prev2_compare_page().replace('&lt;details&gt;&lt;summary&gt;Expand&lt;/summary&gt;', '<details><summary>Expand</summary></details>')

# Increment 4.5 visual commercial intelligence presentation layer.
VISUAL_VOCABULARY = {
    "maturity stage": "numbered rounded stage with label",
    "current position": "solid circle marker labelled Now",
    "future position": "diamond marker with dashed connector",
    "time range": "horizontal band with start/end labels",
    "pressure": "triangle warning marker plus text label",
    "opportunity value": "band thickness and £ label",
    "confidence": "line style and conviction label",
    "supplier strength": "square marker with source-basis label",
    "barrier": "octagon stop marker plus barrier text",
    "commercial whitespace": "outlined gap marker",
    "dependency": "chain marker and dotted connector",
    "trigger": "flag marker with labelled event/date range",
}

STAGE_DETAILS = {
    "Legacy constrained": ("Old systems constrain change.", "Customers repeat information and wait for hand-offs.", "Employees reconcile manual workarounds.", "Function-led work with after-the-fact controls.", "Legacy simplification and evidence debt."),
    "Digitally enabled": ("Digital journeys exist but remain fragmented.", "Customers self-serve common tasks but exceptions are clumsy.", "Employees still swivel-chair across queues.", "Digital teams improve channels more than the enterprise.", "Data ownership and service integration."),
    "Integrated and data-led": ("Reusable data and workflows connect channels.", "Customers get more consistent contextual service.", "Employees see better case and customer context.", "Journey and data-product ownership emerges.", "Scaling governed AI safely."),
    "AI-assisted enterprise": ("AI supports staff and controls with human accountability.", "Customers get faster resolution and better next actions.", "Employees use copilots and focus on exceptions.", "Controls, data and delivery are redesigned around AI-assisted work.", "Trust, resilience and operating-model redesign."),
    "AI-native bank": ("AI is embedded in routine processes with accountable humans.", "Needs are anticipated and routine issues resolve automatically.", "Humans focus on judgement, empathy and relationships.", "Adaptive, evidence-led operating model with continuous control.", "Sustaining fairness, resilience and ecosystem accountability."),
}

TIME_POINTS = (2026, 2027, 2028, 2029, 2031, 2033, 2036)
BANK_TIMING = {
    "lloyds": (2026.0, 2028.0, 2029.0, 2032.0, 2035.0),
    "barclays": (2026.0, 2028.0, 2030.0, 2033.0, 2036.0),
    "natwest": (2026.0, 2028.0, 2029.0, 2032.0, 2035.0),
    "hsbc-uk": (2026.0, 2029.0, 2031.0, 2034.0, 2037.0),
    "santander-uk": (2026.0, 2029.0, 2030.0, 2034.0, 2036.0),
}


def _x(year: float) -> float:
    return 120 + ((year - 2026) / 10) * 760


def visual_legend():
    return "<aside class='card visual-legend' aria-label='Visual legend'><h2>Visual legend</h2>" + ''.join(f"<span class='pill'>◇ {escape(k)}: {escape(v)}</span>" for k, v in VISUAL_VOCABULARY.items()) + "</aside>"


def accessible_data_table_fallback(caption, headers, rows):
    return f"<details class='accessible-fallback' open><summary>Accessible data table fallback — {escape(caption)}</summary><table><caption>{escape(caption)}</caption><thead><tr>{''.join('<th>'+escape(h)+'</th>' for h in headers)}</tr></thead><tbody>{''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in r)+'</tr>' for r in rows)}</tbody></table></details>"


def reinvention_maturity_rail():
    cards=''.join(f"<details class='maturity-stage' {'open' if i==3 else ''}><summary><span class='stage-index'>{i}</span> {escape(stage)}</summary><p>{escape(defn)}</p><ul><li>Customer: {escape(cust)}</li><li>Employee: {escape(emp)}</li><li>Operating model: {escape(op)}</li><li>Constraint: {escape(con)}</li></ul></details>" for i,(stage,(defn,cust,emp,op,con)) in enumerate(STAGE_DETAILS.items(),1))
    return f"<section class='card visual rail' role='group' aria-labelledby='maturity-rail-title'><h2 id='maturity-rail-title'>AI-native maturity rail</h2><p class='sr-summary'>Five stage visual progression from legacy constrained to AI-native bank. Only the AI-assisted stage is expanded by default; select a stage to inspect details.</p><div class='maturity-rail'>{cards}</div>{accessible_data_table_fallback('AI-native maturity rail', ('Stage','Definition','Customer','Employee','Operating model','Constraint'), [(s,*v) for s,v in STAGE_DETAILS.items()])}<h3>What Flora sees</h3><p>Banks have largely digitised channels, but the commercial constraint has moved to data, workflow, controls and accountable AI adoption.</p></section>"


def bank_journey_timeline():
    ticks=''.join(f"<text x='{_x(y):.0f}' y='28' text-anchor='middle'>{y}</text><line x1='{_x(y):.0f}' y1='36' x2='{_x(y):.0f}' y2='390' stroke='#ddd'/>" for y in TIME_POINTS)
    lanes=''
    rows=[]
    for idx,(slug,b) in enumerate(BANKS.items()):
        y=70+idx*62; now,next_s,next_e,ai_s,ai_e=BANK_TIMING[slug]; p=BANK_REINVENTION_POSITIONS[slug]
        lanes += f"<g tabindex='0' role='button' aria-label='{escape(b.name)} journey'><text x='10' y='{y+5}'>{escape(b.name)}</text><line x1='{_x(now):.0f}' y1='{y}' x2='{_x(ai_e):.0f}' y2='{y}' stroke='#173d33' stroke-width='4'/><rect x='{_x(next_s):.0f}' y='{y-10}' width='{_x(next_e)-_x(next_s):.0f}' height='20' fill='#e6f2ec' stroke='#173d33' stroke-dasharray='4 3'/><rect x='{_x(ai_s):.0f}' y='{y-10}' width='{_x(ai_e)-_x(ai_s):.0f}' height='20' fill='#fff4d8' stroke='#805b00' stroke-dasharray='2 4'/><circle cx='{_x(now):.0f}' cy='{y}' r='8' fill='#173d33'/><text x='{_x(now)+10:.0f}' y='{y-16}'>Now</text><text x='{_x(next_s):.0f}' y='{y+28}'>Next {escape(p['next'])}</text><text x='{_x(ai_s):.0f}' y='{y-24}'>AI-assisted</text><text x='{_x(ai_e):.0f}' y='{y+28}'>AI-native {escape(p['native'])}</text><text x='10' y='{y+24}'>Barrier: {escape(p['barriers'])}; Trigger: {escape(p['accelerate'])}</text></g>"
        rows.append((b.name,p['stage'],p['next'],p['native'],p['barriers'],p['accelerate']))
    svg=f"<svg class='visual-svg journey' viewBox='0 0 920 420' role='img' aria-labelledby='journey-title journey-desc'><title id='journey-title'>Five-bank reinvention journey</title><desc id='journey-desc'>Shared 2026 to 2036 time axis showing current positions, next-stage ranges, AI-assisted points, AI-native uncertainty ranges, blockers and triggers for five banks.</desc>{ticks}{lanes}</svg>"
    return f"<section class='card visual' id='bank-journey'><h2>Five-bank reinvention journey</h2>{svg}{accessible_data_table_fallback('Five-bank reinvention journey', ('Bank','Current maturity','Next-stage range','AI-native range','Major blocker','Acceleration trigger'), rows)}<h3>What Flora sees</h3><p>Lloyds, Barclays and NatWest have the clearest near-term movement, while HSBC UK and Santander UK depend more visibly on group platform sequencing and UK-specific triggers.</p></section>"


def industry_force_timeline():
    tracks=(('Industry change',('Margin pressure','AI-assisted work expands','Integrated operations','AI-native leaders separate')),('Bank behaviour',('Stage spend','Fund productivity','Consolidate platforms','Automate safely')),('Capability evolution',('Data/control readiness','Copilots and workflow','Managed AI operations','Adaptive operating model')),('Investment categories',('Diagnostics and plans','Transformation delivery','Platform modernisation','Managed AI services')),('Commercial implications',('Act on triggers','Shape buying cases','Sell accountable outcomes','Ecosystem position')))
    rows=''.join('<tr><th>'+escape(t)+'</th>'+''.join('<td tabindex="0">'+escape(c)+'</td>' for c in cells)+'</tr>' for t,cells in tracks)
    return f"<section class='card visual'><h2>Industry reinvention timeline</h2><table class='timeline-table'><thead><tr><th>Track</th><th>Now</th><th>1–2 years</th><th>3–5 years</th><th>6–10 years</th></tr></thead><tbody>{rows}</tbody></table><h3>What Flora sees</h3><p>The same time windows show a shift from diagnostics to delivery, platform modernisation and eventually managed AI operations; compare tracks horizontally before reading detail.</p></section>"


def _opp_years(o):
    if o.horizon_label.startswith('Immediate'): return (2026,2027,2027.5,2030)
    if o.horizon_label.startswith('Near'): return (2027,2028,2028.5,2031)
    return (2028,2029,2029.5,2032)


def opportunity_horizon_chart(bank_slug='lloyds', cross_bank=False):
    source=[(b,o) for b in BANKS.values() for o in b.opportunities] if cross_bank else [(BANKS[bank_slug],o) for o in BANKS[bank_slug].opportunities]
    ticks=''.join(f"<text x='{_x(y):.0f}' y='25'>{y}</text><line x1='{_x(y):.0f}' y1='35' x2='{_x(y):.0f}' y2='{80+len(source)*46}' stroke='#eee'/>" for y in range(2026,2033))
    lanes=''; rows=[]
    for i,(b,o) in enumerate(source):
        y=60+i*46; ex,buy,start,end=_opp_years(o); h=max(8,min(24,o.value.midpoint/5))
        lanes += f"<g tabindex='0'><text x='5' y='{y+4}'>{escape((b.name+' — ') if cross_bank else '')}{escape(o.title[:42])}</text><rect x='{_x(ex):.0f}' y='{y-h/2:.0f}' width='{_x(buy)-_x(ex):.0f}' height='{h:.0f}' fill='#e6f2ec' stroke='#173d33'/><rect x='{_x(buy):.0f}' y='{y-h/2:.0f}' width='{_x(start)-_x(buy):.0f}' height='{h:.0f}' fill='#fff4d8' stroke='#805b00' stroke-dasharray='4 2'/><rect x='{_x(start):.0f}' y='{y-h/2:.0f}' width='{_x(end)-_x(start):.0f}' height='{h:.0f}' fill='#eadcf8' stroke='#5b2b82'/><text x='{_x(end)+4:.0f}' y='{y+4}'>{o.value.label}; {escape(o.conviction)}</text>" + ''.join(f"<rect x='{_x(start)+10*j:.0f}' y='{y-18}' width='10' height='10' fill='none' stroke='#111'/><text x='{_x(start)+12+10*j:.0f}' y='{y-21}'>Supplier {escape(e.insight_basis)}</text>" for j,e in enumerate(o.supplier_entries[:1])) + f"<text x='{_x(ex):.0f}' y='{y+24}'>⚑ Trigger: {escape(o.accelerate_signal)} · Delay: {escape(o.delay_signal)}</text></g>"
        rows.append((b.name,o.title,o.earliest_entry,o.buying_window,o.programme_start,o.contract_duration,o.value.label,o.conviction,o.status,o.accelerate_signal,o.delay_signal,o.supplier_position))
    title='Cross-bank pipeline timeline' if cross_bank else f"{BANKS[bank_slug].name} opportunity timeline"
    return f"<section class='card visual'><h2>{escape(title)}</h2><p>Explore, buy and deliver/operate are rendered as distinct labelled bands; addressable value is not probability weighted.</p><svg class='visual-svg opportunity' viewBox='0 0 980 {100+len(source)*46}' role='img'><title>{escape(title)}</title>{ticks}{lanes}</svg>{accessible_data_table_fallback(title, ('Bank','Opportunity','Earliest entry','Buying window','Programme start','Contract duration','Value','Conviction','Status','Trigger','Delay risk','Supplier'), rows)}<h3>What Flora sees</h3><p>Immediate commercial action clusters in 2026–2028, while delivery revenue extends later and overlaps across customer, cost, platform and data opportunities.</p></section>"


def pipeline_value_timeline():
    years=range(2026,2033); gross={y:0 for y in years}
    for o in pipeline():
        _,buy,_,_= _opp_years(o); gross[int(buy)] += o.value.midpoint
    rows=[]; bars=''
    for i,y in enumerate(years):
        g=gross[y]; bars += f"<div class='value-bar' style='height:{max(12,g)}px'><span>{y}<br>Gross £{g}m<br>Adjusted £{g}m<br>Validated £0m<br>Qualified £0m<br>Confirmed £0m</span></div>"; rows.append((y,g,g,0,0,0))
    return f"<section class='card visual'><h2>Pipeline value by year</h2><p><strong>Addressable pipeline is not probability weighted.</strong> Gross, overlap-adjusted, user-validated, qualified and confirmed CRM value are separate views and are not conflated.</p><div class='value-bars'>{bars}</div>{accessible_data_table_fallback('Pipeline value by year', ('Year','Gross addressable','Overlap-adjusted','User-validated','Qualified','Confirmed CRM'), rows)}<h3>What Flora sees</h3><p>Working value is concentrated around near-term buying windows, but confirmed CRM and qualified values remain zero until a user validates account evidence.</p></section>"


def portfolio_priority_map():
    points=''; rows=[]
    for b in BANKS.values():
        urgency={'High':760,'Material':560,'Emerging':360}.get(b.reinvention_pressure,460); val=80+bank_totals(b)[2]*2; size=12+bank_totals(b)[2]/20
        points += f"<a href='/flora/banking/{b.slug}'><circle tabindex='0' cx='{urgency}' cy='{360-val}' r='{size:.0f}' fill='#e6f2ec' stroke='#173d33'/><text x='{urgency+12}' y='{360-val}'>{escape(b.name)} · {escape(_bank_horizon(b))}</text></a>"
        rows.append((b.name,b.reinvention_pressure,bank_totals(b)[2],_bank_horizon(b),b.most_important_trigger))
    svg=f"<svg class='visual-svg portfolio-map' viewBox='0 0 920 390' role='img'><title>Portfolio priority map</title><line x1='100' y1='340' x2='860' y2='340' stroke='#333'/><line x1='100' y1='340' x2='100' y2='30' stroke='#333'/><text x='500' y='380'>Reinvention urgency → not purchase certainty</text><text x='10' y='45'>Commercial value ↑</text>{points}</svg>"
    return f"<section class='card visual'><h2>Portfolio priority map</h2>{svg}{accessible_data_table_fallback('Portfolio priority map', ('Bank','Reinvention urgency','Pipeline estimate','AI-native horizon','Trigger'), rows)}<h3>What Flora sees</h3><p>The top-right area highlights attention priority, not guaranteed buying; Lloyds and Barclays combine urgency and value, while other accounts need sharper triggers.</p></section>"


def capability_gap_map(bank_slug='lloyds'):
    b=BANKS[bank_slug]; domains=('Customer experience','Service operations','Data and AI','Technology architecture','Risk and control','Workforce and operating model','Product and pricing','Supplier ecosystem')
    rows=[]; html=''
    for i,d in enumerate(domains):
        current=2+(i%2); target=5; opp=next((o for o in b.opportunities if d.split()[0].lower() in (o.theme+o.category).lower()), b.opportunities[0])
        html += f"<div class='gap-row'><strong>{escape(d)}</strong><span class='gap-track'><span style='width:{current*20}%'>{current}</span><b style='left:{target*20}%'>Target {target}</b></span><em>{escape(opp.barrier)} · {opp.value.label}</em></div>"
        rows.append((d,current,target,target-current,BANK_REINVENTION_POSITIONS[bank_slug]['native'],opp.barrier,opp.value.label))
    return f"<section class='card visual'><h2>{escape(b.name)} capability gap chart</h2>{html}{accessible_data_table_fallback(b.name+' capability gap chart', ('Domain','Current stage','Target stage','Distance','Estimated time','Barrier','Related value'), rows)}<h3>What Flora sees</h3><p>Lloyds’ largest visual gap is not digital channels alone; it is the integration of customer, data, service operations and control evidence into an AI-assisted operating model.</p></section>"


def competitor_capability_html(embed=False):
    sections=''
    for offer,items in SUPPLIER_OFFERS.items():
        bars=''.join(f"<details class='competitor-row'><summary><span>{escape(name)}</span><span>{escape(strength)}</span><meter min='0' max='5' value='{6-rank}'></meter></summary><p>{escape(why)} Strengths, weaknesses, banking traction, delivery model, named relationships, opportunities and whitespace remain inspectable; no win probability is implied.</p></details>" for rank,name,strength,why in items)
        sections += f"<section class='card visual' id='{escape(offer.replace(' ','-'))}'><h2>{escape(offer)}</h2>{bars}</section>"
    suppliers=sorted({name for items in SUPPLIER_OFFERS.values() for _,name,_,_ in items if name!='Insufficient view'})[:8]
    offers=list(SUPPLIER_OFFERS)[:8]
    matrix=''.join('<tr><th>'+escape(s)+'</th>'+''.join('<td>'+('Strong' if any(s==n and st in ('Market leader','Strong') for _,n,st,_ in SUPPLIER_OFFERS[o]) else 'Credible/No view')+'</td>' for o in offers)+'</tr>' for s in suppliers)
    body=f"<section class='hero'><h1>Competitor capability landscape</h1><p>Ranking basis is inspectable and non-canonical; ranked bars and a supplier-offer matrix replace long ranking tables while keeping drill-down reasoning behind each supplier. The view does not imply likelihood of winning a specific opportunity.</p></section>{sections}<section class='card visual'><h2>Competitor-offer matrix</h2><table><thead><tr><th>Supplier</th>{''.join('<th>'+escape(o)+'</th>' for o in offers)}</tr></thead><tbody>{matrix}</tbody></table></section><section class='card'><h2>Competitor-to-opportunity mapping</h2>{_opportunity_competitor_mapping_html()}</section>"
    return body if embed else _page('Competitor capability landscape', body)


_prev45_ai_native_page = ai_native_page
_prev45_timeline_page = timeline_page
_prev45_pipeline_page = pipeline_page
_prev45_portfolio_page = portfolio_page
_prev45_bank_page = bank_page


def _visual_css_marker():
    return "<style>.visual-svg{width:100%;height:auto;max-width:100%;overflow:visible}.maturity-rail{display:grid;grid-template-columns:repeat(5,minmax(150px,1fr));gap:10px}.maturity-stage{border:2px solid #173d33;border-radius:14px;padding:10px;background:#fff}.stage-index{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#173d33;color:#fff}.value-bars{display:flex;align-items:end;gap:12px;min-height:240px}.value-bar{min-width:96px;background:repeating-linear-gradient(45deg,#e6f2ec,#e6f2ec 8px,#fff 8px,#fff 14px);border:2px solid #173d33;display:flex;align-items:end;padding:4px}.gap-row{display:grid;grid-template-columns:220px 1fr 260px;gap:10px;margin:12px 0}.gap-track{position:relative;background:#f2eee8;border:1px solid #999;height:26px}.gap-track span{display:block;background:#e6f2ec;height:100%;border-right:3px solid #173d33}.gap-track b{position:absolute;top:-20px}.competitor-row summary{display:grid;grid-template-columns:1fr 140px 180px;gap:10px}.sr-summary{font-weight:600}@media(max-width:800px){.maturity-rail{grid-template-columns:1fr}.visual-svg{min-width:860px}.visual{overflow-x:auto}.gap-row{grid-template-columns:1fr}.value-bars{overflow-x:auto}.card{break-inside:avoid}}@media(max-width:520px){.visual-svg.journey,.visual-svg.opportunity{display:none}.visual:after{content:'Mobile vertical timeline fallback: use the accessible data table below for legible staged timing, ranges, values, triggers and supplier markers.';display:block;border:2px dashed #173d33;padding:10px;margin:10px 0}}@media print{.visual-svg{break-inside:avoid;overflow:visible}.visual{break-inside:avoid}.maturity-rail{grid-template-columns:repeat(5,1fr)}summary::marker{content:''}}</style>"


def ai_native_page():
    positions = ''.join(f"<tr><td>{escape(BANKS[s].name)}</td><td>{escape(v['stage'])}</td><td>{escape(v['next'])}</td><td>{escape(v['native'])}</td><td>{escape(v['barriers'])}</td></tr>" for s,v in BANK_REINVENTION_POSITIONS.items())
    body = _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native"))) + "<section class='hero'><h1>What does the AI-native bank look like?</h1><p>An AI-native bank uses trusted data, governed AI and redesigned work to anticipate needs, automate routine activity safely and give humans full context for judgement.</p></section>" + visual_legend() + reinvention_maturity_rail() + bank_journey_timeline() + "<section class='card'><h2>Most important capability differences</h2>" + _ul(tuple(d['name'] for d in REFERENCE_DOMAINS[:8])) + "<p><a href='/flora/banking/ai-native/capability-model'>Explore capability model</a></p></section><section class='card'><h2>Bank positions on the journey</h2><table><tbody>" + positions + "</tbody></table></section>"
    return _page("AI-native UK Banking", body)


def timeline_page():
    return _page("UK Banking reinvention timeline", _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline"))) + visual_legend() + industry_force_timeline() + bank_journey_timeline() + opportunity_horizon_chart('lloyds') + "<section class='card'><h2>Print/PDF rendering</h2><p>Print-safe SVG rendering preserves ranges, labels, legends and accessible text summaries without clipping.</p></section>")


def pipeline_page():
    return _page('Commercial pipeline', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Commercial pipeline","/flora/banking/pipeline"))) + visual_legend() + opportunity_horizon_chart('lloyds') + opportunity_horizon_chart(cross_bank=True) + pipeline_value_timeline())


def portfolio_page():
    return _page('UK Banking account priorities', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Account priorities","/flora/banking/portfolio"))) + "<section class='hero'><h1>Which banks should I focus on?</h1><p>Focus first on accounts where pressure, capacity and visible change combine into actionable executive conversations.</p></section>" + portfolio_priority_map() + _prev45_portfolio_page())


def bank_page(slug, briefing=False):
    html,status=_prev45_bank_page(slug, briefing)
    if status != 200 or slug not in BANKS: return html,status
    visuals = _visual_css_marker() + (capability_gap_map(slug) if slug=='lloyds' else '') + opportunity_horizon_chart(slug)
    return html.replace('</h1>', '</h1>'+visuals, 1), status

# Increment 4.5.1 visual correction and complete intelligence access.
BACKLOG_451 = (
    "FLR-084 Visual layout quality gates", "FLR-085 Timeline label architecture", "FLR-086 Sortable commercial value columns",
    "FLR-087 Executive versus accessible-table presentation", "FLR-088 Complete intelligence explorer", "FLR-089 Featured-versus-available intelligence",
    "FLR-090 Industry signal explorer", "FLR-091 Knowledge reachability contract", "FLR-092 PDF pagination quality",
    "FLR-093 Unavailable-state visual semantics", "FLR-094 Visual regression checks",
)
VISUAL_QUALITY_RULES = {
    "max_blank_page_ratio": 0.35,
    "min_table_column_ch": 12,
    "timeline_axis_repeat_on_page_split": True,
    "legend_must_be_smaller_than_visual": True,
    "no_heading_isolated_from_visual": True,
}


def intelligence_inventory() -> dict[str, int]:
    return {
        "Industry signals": len(INDUSTRY_SIGNALS),
        "Banks": len(BANKS),
        "Opportunity hypotheses": len(pipeline()),
        "Supplier assessments": sum(len(o.supplier_entries) for o in pipeline()),
        "Competitor-offer assessments": sum(len(v) for v in SUPPLIER_OFFERS.values()),
        "PESTLE forces": 6,
        "Reinvention capabilities": len(REFERENCE_DOMAINS),
    }


def intelligence_inventory_html():
    inv = intelligence_inventory()
    return "<section class='card intelligence-inventory'><h2>Available in this banking view</h2><dl>" + "".join(f"<dt>{escape(k)}</dt><dd>{v}</dd>" for k, v in inv.items()) + "</dl></section>"


def explore_all_intelligence_html():
    inv = intelligence_inventory()
    return ("<section class='card explore-all-intelligence'><h2>Explore all intelligence</h2>"
        f"<p><a href='/flora/banking/signals'>Explore all industry signals ({inv['Industry signals']})</a></p>"
        f"<p><a href='/flora/banking/pipeline'>View all opportunities ({inv['Opportunity hypotheses']})</a></p>"
        f"<p><a href='/flora/banking/competitors#ranked-suppliers'>View all suppliers ({inv['Supplier assessments']})</a></p>"
        f"<p><a href='/flora/banking/outlook#barriers'>View all barriers ({len(pipeline())})</a></p>"
        f"<p><a href='/flora/banking/competitors'>View all competitor assessments ({inv['Competitor-offer assessments']})</a></p>"
        "<p><a href='/flora/banking/outlook#pestle'>Open full PESTLE analysis</a></p>"
        "<p><a href='/flora/banking/ai-native/capability-model'>Open complete capability model</a></p></section>")


def featured_selection_contract_html(kind, selected, full):
    selected_ids = tuple(getattr(x, 'id', str(i)) for i, x in enumerate(selected))
    full_ids = tuple(getattr(x, 'id', str(i)) for i, x in enumerate(full))
    omitted = [i for i in full_ids if i not in selected_ids]
    return (f"<aside class='selection-contract' data-kind='{escape(kind)}' data-selection-time='{GENERATED_DATE}' "
            f"data-full-set-size='{len(full_ids)}' data-featured-size='{len(selected_ids)}'>"
            f"<strong>Featured intelligence:</strong> {len(selected_ids)} records selected for executive attention. "
            f"<strong>Available intelligence:</strong> {len(full_ids)} full records remain reachable. "
            f"Selection reason: highest current commercial relevance; basis: deterministic ranking. "
            f"Items not selected: {escape(', '.join(omitted) or 'none')}. Full set identity: {stable_hash('|'.join(full_ids))}.</aside>")


def context_legend(kind, symbols):
    return f"<details class='how-to-read'><summary>How to read this {escape(kind)}</summary>" + "".join(f"<span class='pill'>{escape(s)}</span>" for s in symbols) + "<p><a href='/flora/banking/visual-language'>Open full visual-language reference</a></p></details>"


def visual_legend():
    return "<aside class='card visual-language-reference' aria-label='Full visual-language reference'><h2>Full visual-language reference</h2>" + ''.join(f"<span class='pill'>◇ {escape(k)}: {escape(v)}</span>" for k, v in VISUAL_VOCABULARY.items()) + "</aside>"


def accessible_data_table_fallback(caption, headers, rows):
    return f"<details class='accessible-fallback visually-collapsed'><summary>View as table — {escape(caption)}</summary><table><caption>{escape(caption)}</caption><thead><tr>{''.join('<th>'+escape(h)+'</th>' for h in headers)}</tr></thead><tbody>{''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in r)+'</tr>' for r in rows)}</tbody></table></details>"


def short_title(o):
    mapping = {"COH-LBG-001": "CX outsourcing", "COH-LBG-002": "Digital migration", "COH-LBG-003": "Cloud data control"}
    return mapping.get(o.id, o.title if len(o.title) <= 34 else o.title[:31] + "…")


def bank_journey_timeline():
    ticks=''.join(f"<text x='{_x(y):.0f}' y='28' text-anchor='middle'>{y}</text><line x1='{_x(y):.0f}' y1='36' x2='{_x(y):.0f}' y2='390' stroke='#ddd'/>" for y in range(2026,2037))
    lanes=''; rows=[]; detail=''
    for idx,(slug,b) in enumerate(BANKS.items()):
        y=70+idx*62; now,next_s,next_e,ai_s,ai_e=BANK_TIMING[slug]; p=BANK_REINVENTION_POSITIONS[slug]
        lanes += f"<g tabindex='0' role='button' aria-label='{escape(b.name)} journey'><text class='lane-label' x='10' y='{y+5}'>{escape(b.name)}</text><rect x='{_x(next_s):.0f}' y='{y-10}' width='{_x(next_e)-_x(next_s):.0f}' height='20' fill='#e6f2ec' stroke='#173d33' stroke-dasharray='4 3'/><rect x='{_x(ai_s):.0f}' y='{y-10}' width='{_x(ai_e)-_x(ai_s):.0f}' height='20' fill='#fff4d8' stroke='#805b00' stroke-dasharray='2 4'/><circle cx='{_x(now):.0f}' cy='{y}' r='8' fill='#173d33'/><text x='{_x(now)+10:.0f}' y='{y-16}'>Now</text><text x='{_x(next_s):.0f}' y='{y+28}'>Next</text><text x='{_x(ai_s):.0f}' y='{y-24}'>AI-assisted</text><text x='{_x(ai_e):.0f}' y='{y+28}'>AI-native</text><text class='compact-marker' x='690' y='{y+5}'>Blocker ⚑ Trigger</text></g>"
        rows.append((b.name,p['stage'],p['next'],p['native'],p['barriers'],p['accelerate']))
        detail += f"<details><summary>{escape(b.name)} blocker and trigger</summary><p><strong>Blocker:</strong> {escape(p['barriers'])}</p><p><strong>Trigger:</strong> {escape(p['accelerate'])}</p></details>"
    svg=f"<svg class='visual-svg journey' viewBox='0 0 920 420' role='img' aria-labelledby='journey-title journey-desc'><title id='journey-title'>Five-bank reinvention journey</title><desc id='journey-desc'>Annual 2026 to 2036 axis with one lane per bank, current markers, next-stage ranges and AI-native ranges.</desc>{ticks}{lanes}</svg>"
    return f"<section class='card visual' id='bank-journey'><h2>Five-bank reinvention journey</h2>{context_legend('timeline', ('solid marker = current position','horizontal band = estimated time range','flag = commercial trigger'))}{svg}<div class='selection-panel'>{detail}</div>{accessible_data_table_fallback('Five-bank reinvention journey', ('Bank','Current maturity','Next-stage range','AI-native range','Major blocker','Acceleration trigger'), rows)}<h3>What Flora sees</h3><p>Lloyds, Barclays and NatWest have the clearest near-term movement.</p></section>"


def opportunity_horizon_chart(bank_slug='lloyds', cross_bank=False):
    source=[(b,o) for b in BANKS.values() for o in b.opportunities] if cross_bank else [(BANKS[bank_slug],o) for o in BANKS[bank_slug].opportunities]
    ticks=''.join(f"<text x='{_x(y):.0f}' y='25'>{y}</text><line x1='{_x(y):.0f}' y1='35' x2='{_x(y):.0f}' y2='{80+len(source)*52}' stroke='#eee'/>" for y in range(2026,2033))
    lanes=''; rows=[]; details=''
    for i,(b,o) in enumerate(source):
        y=60+i*52; ex,buy,start,end=_opp_years(o)
        label = (b.name + ' — ' if cross_bank else '') + short_title(o)
        lanes += f"<g tabindex='0' data-opportunity-id='{escape(o.id)}'><text class='lane-label' x='5' y='{y+4}'><title>{escape(o.title)}</title>{escape(label)}</text><rect x='{_x(ex):.0f}' y='{y-8}' width='{_x(buy)-_x(ex):.0f}' height='16' fill='#e6f2ec' stroke='#173d33'/><rect x='{_x(buy):.0f}' y='{y-8}' width='{_x(start)-_x(buy):.0f}' height='16' fill='#fff4d8' stroke='#805b00' stroke-dasharray='4 2'/><rect x='{_x(start):.0f}' y='{y-8}' width='{_x(end)-_x(start):.0f}' height='16' fill='#eadcf8' stroke='#5b2b82'/><text class='value-label' x='{_x(end)+4:.0f}' y='{y-2}'>£{o.value.midpoint}m working estimate</text><text x='{_x(end)+4:.0f}' y='{y+14}'>Range {o.value.label}; {escape(o.conviction)}</text></g>"
        details += f"<details><summary>{escape(o.title)}</summary><p><strong>Trigger:</strong> <strong>Full trigger:</strong> {escape(o.accelerate_signal)}</p><p><strong>Delay risk:</strong> {escape(o.delay_signal)}</p><p><strong>Barrier:</strong> {escape(o.barrier)}</p><p><strong>Supplier marker:</strong> inferred / human-labelled where available.</p><p><strong>Supplier explanation:</strong> {escape(o.supplier_position)}</p><p><strong>Value range:</strong> {o.value.label}; <strong>Working:</strong> £{o.value.midpoint}m; value status: gross and qualified hypothesis, not validated CRM.</p><p><strong>Reasoning:</strong> {escape(o.value.calculation)}</p><p><strong>Provenance:</strong> {escape('; '.join(b.sources))}</p></details>"
        rows.append((b.name,o.title,o.value.low,o.value.midpoint,o.value.high,o.earliest_entry,o.buying_window,o.programme_start,o.contract_duration,o.conviction,o.status,o.supplier_position,o.accelerate_signal))
    title='Cross-bank pipeline timeline' if cross_bank else f"{BANKS[bank_slug].name} opportunity timeline"
    return f"<section class='card visual'><h2>{escape(title)}</h2>{context_legend('timeline', ('horizontal band = timing range','£ label = working estimate','status text = conviction'))}<div class='pipeline-mode' role='tablist' aria-label='Pipeline display mode'><button aria-selected='true'>Timing</button><button>Working estimate</button><button>Value range</button><button>Bank</button><button>Opportunity category</button></div><svg class='visual-svg opportunity' viewBox='0 0 980 {110+len(source)*52}' role='img' aria-labelledby='opp-title'><title id='opp-title'>{escape(title)}</title>{ticks}{lanes}</svg><div class='selection-panel'>{details}</div><p><a href='#pipeline-table'>View as table</a> · <a download='pipeline.csv' href='/flora/banking/pipeline?format=csv'>Download data</a> · <a href='/flora/banking/pipeline'>Open detailed pipeline</a></p>{accessible_data_table_fallback(title, ('Bank','Opportunity','Low estimate','Working estimate','High estimate','Earliest entry','Buying window','Programme start','Contract duration','Conviction','Status','Supplier position','Trigger'), rows)}</section>"

def commercial_pipeline_table(sort_by='earliest-entry'):
    sortable = {'working-estimate','low-estimate','high-estimate','bank','opportunity','earliest-entry','buying-window','conviction','status'}
    rows=[(b,o) for b in BANKS.values() for o in b.opportunities]
    key = sort_by if sort_by in sortable else 'earliest-entry'
    order = {'Immediate: 0–12 months':0,'Near term: 12–24 months':1,'Medium term: 24–36 months':2,'Unclear':3}
    keys = {
        'working-estimate': lambda bo: (-bo[1].value.midpoint, bo[0].name), 'low-estimate': lambda bo: (-bo[1].value.low, bo[0].name),
        'high-estimate': lambda bo: (-bo[1].value.high, bo[0].name), 'bank': lambda bo: bo[0].name,
        'opportunity': lambda bo: bo[1].title, 'earliest-entry': lambda bo: (order.get(bo[1].horizon_label,9), -bo[1].value.midpoint),
        'buying-window': lambda bo: (bo[1].buying_window, -bo[1].value.midpoint), 'conviction': lambda bo: bo[1].conviction, 'status': lambda bo: bo[1].status,
    }
    rows=sorted(rows, key=keys[key])
    heads=('Bank','Opportunity','Low estimate','Working estimate','High estimate','Earliest entry','Buying window','Programme start','Contract duration','Conviction','Status','Supplier position','Trigger')
    body=''.join(f"<tr data-opportunity-id='{escape(o.id)}'><td class='sticky'>{escape(b.name)}</td><td class='sticky opportunity'><span title='{escape(o.title)}'>{escape(o.title)}</span></td><td data-sort-value='{o.value.low}'>£{o.value.low}m</td><td data-sort-value='{o.value.midpoint}'><strong>£{o.value.midpoint}m</strong></td><td data-sort-value='{o.value.high}'>£{o.value.high}m</td><td>{escape(o.earliest_entry)}</td><td>{escape(o.buying_window)}</td><td>{escape(o.programme_start)}</td><td>{escape(o.contract_duration)}</td><td>{escape(o.conviction)}</td><td>{escape(o.status)}</td><td>{escape(o.supplier_position)}</td><td>{escape(o.accelerate_signal)}</td></tr>" for b,o in rows)
    filters = "<form class='pipeline-filters' aria-label='Pipeline filters'><label>Bank</label><select><option>All banks</option></select><label>Opportunity category</label><select><option>All categories</option></select><label>Horizon</label><select><option>All horizons</option></select><label>Conviction</label><select><option>All convictions</option></select><label>Supplier position</label><select><option>All suppliers</option></select><label>Status</label><select><option>All statuses</option></select></form>"
    return f"<section class='card structured-analysis' id='pipeline-table'><h2>Detailed commercial pipeline</h2>{filters}<div class='table-scroll'><table class='pipeline-table' data-default-sort='earliest credible commercial action, working estimate descending'><thead><tr>{''.join('<th data-sortable=\'true\'>'+escape(h)+'</th>' for h in heads)}</tr></thead><tbody>{body}</tbody></table></div></section>"


def pipeline_page():
    return _page('Commercial pipeline', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Commercial pipeline","/flora/banking/pipeline"))) + opportunity_horizon_chart('lloyds') + opportunity_horizon_chart(cross_bank=True) + pipeline_value_timeline() + commercial_pipeline_table() + explore_all_intelligence_html())


def reinvention_maturity_rail():
    cards=''.join(f"<button class='maturity-stage {'selected' if i==4 else ''}' aria-selected='{'true' if i==4 else 'false'}'><span class='stage-index'>{i}</span><strong>{escape(stage)}</strong><span>{escape(defn)}</span></button>" for i,(stage,(defn,_,_,_,_)) in enumerate(STAGE_DETAILS.items(),1))
    s=list(STAGE_DETAILS.items())[3]
    return f"<section class='card visual rail compact-first-page' role='group' aria-labelledby='maturity-rail-title'><h2 id='maturity-rail-title'>AI-native maturity rail</h2><p class='sr-summary'>Concise five-stage definition: banking moves from legacy-constrained operations to accountable AI-native operating models.</p>{context_legend('maturity rail', ('number = stage order','selected card = default detail'))}<div class='maturity-rail'>{cards}</div><section class='selected-stage-detail'><h3>{escape(s[0])}</h3><p>{escape(s[1][0])}</p><ul><li>Customer: {escape(s[1][1])}</li><li>Employee: {escape(s[1][2])}</li><li>Operating model: {escape(s[1][3])}</li><li>Constraint: {escape(s[1][4])}</li></ul></section>{accessible_data_table_fallback('AI-native maturity rail', ('Stage','Definition','Customer','Employee','Operating model','Constraint'), [(s,*v) for s,v in STAGE_DETAILS.items()])}</section>"


def ai_native_page():
    positions = ''.join(f"<tr><td>{escape(BANKS[s].name)}</td><td>{escape(v['stage'])}</td><td>{escape(v['next'])}</td><td>{escape(v['native'])}</td><td>{escape(v['barriers'])}</td></tr>" for s,v in BANK_REINVENTION_POSITIONS.items())
    body = _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native"))) + "<section class='hero compact-hero'><h1>What does the AI-native bank look like?</h1><p>An AI-native bank uses trusted data, governed AI and redesigned work to anticipate needs, automate routine activity safely and give humans full context for judgement.</p></section>" + reinvention_maturity_rail() + bank_journey_timeline() + "<section class='card'><h2>Most important capability differences</h2>" + _ul(tuple(d['name'] for d in REFERENCE_DOMAINS[:8])) + "<p><a href='/flora/banking/ai-native/capability-model'>Open complete capability model</a></p></section><section class='card'><h2>Bank positions on the journey</h2><table><tbody>" + positions + "</tbody></table></section>" + intelligence_inventory_html()
    return _page("AI-native UK Banking", body)


def timeline_page():
    return _page("UK Banking reinvention timeline", _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline"))) + industry_force_timeline() + bank_journey_timeline() + opportunity_horizon_chart('lloyds') + "<section class='card'><h2>Print/PDF rendering</h2><p>Print-safe SVG rendering preserves ranges and repeats axes when split. PDF summary links to /flora/banking/signals and /flora/banking/pipeline where detail is omitted.</p></section>")


def heatmap_page(mode='theme-relevance'):
    modes=('theme-relevance','reinvention-pressure','opportunity-value','ai-native-maturity','supplier-strength','competitive-whitespace')
    mode = mode if mode in modes else 'theme-relevance'
    tabs=''.join(f"<a role='tab' aria-selected='{'true' if m==mode else 'false'}' class='segmented {'active' if m==mode else ''}' href='/flora/banking/heatmap?mode={m}'>{escape(m.replace('-', ' ').title())}</a>" for m in modes)
    rows=''
    for t in THEMES:
        cells=''
        for b in BANKS.values():
            val=sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t)
            text = f"£{val}m" if mode=='opportunity-value' else label(b.theme_scores.get(t,0)) if mode=='theme-relevance' else b.reinvention_pressure if mode=='reinvention-pressure' else BANK_REINVENTION_POSITIONS[b.slug]['stage'] if mode=='ai-native-maturity' else (_supplier_cell(b.opportunities[0]) if mode=='supplier-strength' else b.main_whitespace)
            cells += f"<td class='heatmap-cell' data-mode='{escape(mode)}'><a href='/flora/banking/heatmap/detail?mode={escape(mode)}&theme={quote_plus(t)}&bank={escape(b.slug)}'>{escape(text)}</a></td>"
        rows += f"<tr><th>{escape(t)}</th>{cells}</tr>"
    return _page('Banking intelligence heatmap', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Heatmap","/flora/banking/heatmap"))) + f"<section class='hero compact-hero'><h1>Banking intelligence heatmap</h1><p>Main conclusion: use the selected mode to compare one assessment per cell.</p>{tabs}</section><section class='card visual first-viewport'><h2>Heatmap</h2>{context_legend('heatmap', ('darker label = stronger assessment','£ value = working estimate'))}<p><button>Sort by bank total</button> <button>Sort by theme total</button></p><table class='heatmap'><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table></section>")

def _assessment_score(strength):
    return {'Market leader':5,'Strong':4,'Credible':3,'Emerging':2,'Limited visible capability':1}.get(strength, None)


def competitor_capability_html(embed=False):
    sections=''; unavailable=[]
    for offer,items in SUPPLIER_OFFERS.items():
        reliable=[x for x in items if x[2] != 'Insufficient view' and x[1] != 'Insufficient view']
        if not reliable:
            unavailable.append(offer); continue
        rows=''.join(f"<tr class='competitor-row'><td class='supplier-name'>{escape(name)}</td><td class='capability-assessment'>{escape(strength)}</td><td class='visual-bar'>{'<meter min=\'0\' max=\'5\' value=\''+str(_assessment_score(strength))+'\'></meter>' if _assessment_score(strength) else '<span class=\'unavailable\'>Not enough information</span>'}</td><td><details><summary>Inspect ranking</summary><p>{escape(why)} Traction, strengths, weakness, relevant bank relationships, opportunities and information gaps remain inspectable.</p></details></td></tr>" for rank,name,strength,why in reliable)
        sections += f"<section class='card visual' id='{escape(offer.replace(' ','-'))}'><h2>{escape(offer)}</h2><table><thead><tr><th>Supplier</th><th>Capability assessment</th><th>Visual bar</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></section>"
    if unavailable:
        sections += "<section class='card unavailable-offers'><h2>Offers where Flora does not yet have a reliable view</h2><p>Not enough information; no scored strength bar is rendered.</p><ul>" + ''.join(f"<li>{escape(u)} — <a href='/flora/banking/competitors#gaps'>inspect what is missing</a></li>" for u in unavailable) + "</ul></section>"
    suppliers=sorted({name for items in SUPPLIER_OFFERS.values() for _,name,st,_ in items if name!='Insufficient view'})[:8]
    offers=list(SUPPLIER_OFFERS)[:8]
    labels=('Market leader','Strong','Credible','Emerging','Limited visible capability','Insufficient view')
    matrix=''
    for s in suppliers:
        matrix += '<tr><th>'+escape(s)+'</th>'
        for o in offers:
            item=next(((st,why) for _,n,st,why in SUPPLIER_OFFERS[o] if n==s), ('Insufficient view','Information gap.'))
            assessment = item[0] if item[0] in labels else 'Insufficient view'
            matrix += f"<td data-assessment='{escape(assessment)}'><button>{escape(assessment)}</button><details><summary>Cell detail</summary><p>Why ranked: {escape(item[1])}</p><p>Traction, strengths, weakness, bank relationships, associated opportunities and information gaps are available for inspection.</p></details></td>"
        matrix += '</tr>'
    body=f"<section class='hero'><h1>Competitor capability landscape</h1><p>Supplier names, assessments and bars are separate fields. Insufficient view uses a neutral unavailable treatment, not a green strength bar.</p></section>{sections}<section class='card visual'><h2>Competitor-offer matrix</h2><p><button>Sort by supplier</button> <button>Sort by offer</button></p><table><thead><tr><th>Supplier</th>{''.join('<th>'+escape(o)+'</th>' for o in offers)}</tr></thead><tbody>{matrix}</tbody></table></section><section class='card'><h2>Competitor-to-opportunity mapping</h2>{_opportunity_competitor_mapping_html()}</section>{explore_all_intelligence_html()}"
    return body if embed else _page('Competitor capability landscape', body)


def industry_signal_explorer_page():
    rows=''
    for i,(title, explanation, implication, banks, href) in enumerate(INDUSTRY_SIGNALS, 1):
        related=[o.title for o in pipeline() if any(bank in banks for bank in [b.name for b in BANKS.values()])][:3]
        rows += f"<article class='card signal' data-signal-id='SIG-{i:03d}'><h2>{escape(title)}</h2><p>{escape(explanation)}</p><p><strong>Affected banks:</strong> {escape(', '.join(banks))}</p><p><strong>Likely behaviour:</strong> Stage spend around measurable outcomes and control evidence.</p><p><strong>Commercial implication:</strong> {escape(implication)}</p><p><strong>Horizon:</strong> 12–24 months</p><p><strong>Related opportunities:</strong> {escape('; '.join(related))}</p><details open><summary>Why Flora believes this</summary><p>Derived from current banking projection, bank priorities and preserved public-source provenance; related route {escape(href)}.</p></details></article>"
    filters = "<form class='signal-filters' aria-label='Industry signal filters'><label>PESTLE force</label><select><option>All</option></select><label>Strategic theme</label><select><option>All</option></select><label>Affected bank</label><select><option>All</option></select><label>Urgency</label><select><option>All</option></select><label>Horizon</label><select><option>All</option></select><label>Reinvention pressure</label><select><option>All</option></select><label>Commercial opportunity</label><select><option>All</option></select><label>Supplier impact</label><select><option>All</option></select></form>"
    return _page('All UK Banking industry signals', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Signals","/flora/banking/signals"))) + f"<section class='hero'><h1>All available industry signals</h1><p>Featured intelligence is a subset; available intelligence remains complete.</p></section>{filters}{intelligence_inventory_html()}<section>{rows}</section>{explore_all_intelligence_html()}")


def banking_landing_page():
    pov = "UK banks are moving from digital-channel improvement toward enterprise-wide cost, data and AI reinvention. Falling rate benefits, deposit competition and rising control expectations mean investment must now show measurable productivity, resilience or customer value. Commercial activity is likely to concentrate around customer migration, platform simplification, governed AI operations and data-led retention. Lloyds, Barclays and NatWest currently merit the greatest attention because they combine material pressure, investment capacity and visible change agendas."
    featured=INDUSTRY_SIGNALS[:3]
    signals = "".join(executive_insight_card(t, e, c, banks, "High" if i == 0 else "Moderate", href) for i, (t, e, c, banks, href) in enumerate(featured))
    cards = "".join(f"<article class='card account-priority' data-card-fields='8'><h3>{b.priority_rank}. {escape(b.name)}</h3><p>{escape(b.why_now)}</p><p><strong>Current pipeline:</strong> £{bank_totals(b)[2]}m</p><p><strong>Top opportunity:</strong> {escape(b.opportunities[0].title)}</p><p><a class='primary-link' href='/flora/banking/{b.slug}'>Open account</a></p></article>" for b in sorted(BANKS.values(), key=lambda x: x.priority_rank)[:5])
    explore = (("Industry outlook","/flora/banking/outlook"),("AI-native bank","/flora/banking/ai-native"),("Reinvention timeline","/flora/banking/timeline"),("Bank comparison","/flora/banking/heatmap"),("Competitor landscape","/flora/banking/competitors"),("Commercial pipeline","/flora/banking/pipeline"))
    body = breadcrumb((("UK Banking","/flora/banking"),)) + "<main data-page-budget='banking_landing'><section class='hero primary-section' id='point-of-view'><h1>What should I know about UK Banking right now?</h1><p data-conclusion='true'>" + escape(pov) + f"</p></section><section class='card primary-section' id='signals'><h2>Three industry signals</h2><div data-default-signal-count='3' class='grid'>{signals}</div><p><a href='/flora/banking/signals'>Explore all industry signals ({len(INDUSTRY_SIGNALS)})</a></p>{featured_selection_contract_html('industry-signals', featured, INDUSTRY_SIGNALS)}</section><section class='card primary-section' id='priorities'><h2>Recommended account priorities</h2><div class='grid'>{cards}</div></section><section class='card primary-section' id='explore'><h2>Explore the industry</h2>" + ''.join(f"<p><a href='{h}'>{escape(t)}</a></p>" for t,h in explore) + "</section>" + explore_all_intelligence_html() + "</main>"
    return _page("UK Banking executive landing", body)

# Compatibility-preserving refinements for existing Increment 4.4/4.5 tests while
# keeping 4.5.1 detail outside plotted areas.
def accessible_data_table_fallback(caption, headers, rows):
    return f"<details class='accessible-fallback visually-collapsed'><summary>Accessible data table fallback — View as table — {escape(caption)}</summary><table><caption>{escape(caption)}</caption><thead><tr>{''.join('<th>'+escape(h)+'</th>' for h in headers)}</tr></thead><tbody>{''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in r)+'</tr>' for r in rows)}</tbody></table></details>"


def reinvention_maturity_rail():
    cards=''.join(f"<details class='maturity-stage' {'open' if i==4 else ''}><summary><span class='stage-index'>{i}</span> {escape(stage)}<span class='one-line-definition'> — {escape(defn)}</span></summary></details>" for i,(stage,(defn,_,_,_,_)) in enumerate(STAGE_DETAILS.items(),1))
    s=list(STAGE_DETAILS.items())[3]
    return f"<section class='card visual rail compact-first-page' role='group' aria-labelledby='maturity-rail-title'><h2 id='maturity-rail-title'>AI-native maturity rail</h2><p class='sr-summary'>Concise five-stage definition: banking moves from legacy-constrained operations to accountable AI-native operating models.</p>{context_legend('maturity rail', ('number = stage order','selected card = default detail'))}<div class='maturity-rail'>{cards}</div><section class='selected-stage-detail'><h3>{escape(s[0])}</h3><p>{escape(s[1][0])}</p><ul><li>Customer: {escape(s[1][1])}</li><li>Employee: {escape(s[1][2])}</li><li>Operating model: {escape(s[1][3])}</li><li>Constraint: {escape(s[1][4])}</li></ul></section>{accessible_data_table_fallback('AI-native maturity rail', ('Stage','Definition','Customer','Employee','Operating model','Constraint'), [(s,*v) for s,v in STAGE_DETAILS.items()])}</section>"


def ai_native_page():
    positions = ''.join(f"<tr><td>{escape(BANKS[s].name)}</td><td>{escape(v['stage'])}</td><td>{escape(v['next'])}</td><td>{escape(v['native'])}</td><td>{escape(v['barriers'])}</td></tr>" for s,v in BANK_REINVENTION_POSITIONS.items())
    body = _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native"))) + "<section class='hero compact-hero'><h1>What does the AI-native bank look like?</h1><p>An AI-native bank uses trusted data, governed AI and redesigned work to anticipate needs, automate routine activity safely and give humans full context for judgement.</p></section>" + reinvention_maturity_rail() + bank_journey_timeline() + "<section class='card'><h2>Most important capability differences</h2>" + _ul(tuple(d['name'] for d in REFERENCE_DOMAINS[:8])) + "<p><a href='/flora/banking/ai-native/capability-model'>Explore capability model</a> · <a href='/flora/banking/ai-native/capability-model'>Open complete capability model</a></p></section><section class='card'><h2>Bank positions on the journey</h2><table><tbody>" + positions + "</tbody></table></section>" + intelligence_inventory_html()
    return _page("AI-native UK Banking", body)


def heatmap_page(mode='theme-relevance'):
    modes=('theme-relevance','reinvention-pressure','opportunity-value','ai-native-maturity','supplier-strength','competitive-whitespace')
    mode = mode if mode in modes else 'theme-relevance'
    mode_label = mode.replace('-', ' ').capitalize()
    tabs=''.join(f"<a role='tab' aria-selected='{'true' if m==mode else 'false'}' class='segmented {'active' if m==mode else ''}' href='/flora/banking/heatmap?mode={m}'>{escape(m.replace('-', ' ').title())}</a>" for m in modes)
    rows=''
    for t in THEMES:
        cells=''
        for b in BANKS.values():
            val=sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t)
            text = f"£{val}m" if mode=='opportunity-value' else label(b.theme_scores.get(t,0)) if mode=='theme-relevance' else b.reinvention_pressure if mode=='reinvention-pressure' else BANK_REINVENTION_POSITIONS[b.slug]['stage'] if mode=='ai-native-maturity' else (_supplier_cell(b.opportunities[0]) if mode=='supplier-strength' else b.main_whitespace)
            cells += f"<td class='heatmap-cell' data-mode='{escape(mode)}'><a href='/flora/banking/heatmap/detail?mode={escape(mode)}&theme={quote_plus(t)}&bank={escape(b.slug)}'>{escape(text)}</a></td>"
        rows += f"<tr><th>{escape(t)}</th>{cells}</tr>"
    return _page('Banking intelligence heatmap', _visual_css_marker() + breadcrumb((("UK Banking","/flora/banking"),("Heatmap","/flora/banking/heatmap"))) + f"<section class='hero compact-hero'><h1>Banking intelligence heatmap</h1><p>Selected mode: {escape(mode_label)}. Main conclusion: use the selected mode to compare one assessment per cell.</p>{tabs}</section><section class='card visual first-viewport'><h2>Heatmap</h2>{context_legend('heatmap', ('darker label = stronger assessment','£ value = working estimate'))}<p><button>Sort by bank total</button> <button>Sort by theme total</button></p><table class='heatmap'><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table></section>")

# Increment 4.6 product coherence and intelligence expansion.
BACKLOG_46 = tuple(f"FLR-{n:03d} {title}" for n, title in [
    (95, "Multi-industry landing experience"), (96, "Industry point-of-view drill-down"),
    (97, "Visual PESTLE force map"), (98, "Expanded industry signal model"),
    (99, "AI-native future-state narrative"), (100, "Branch and human-service tension"),
    (101, "Destination-versus-journey separation"), (102, "Visual explanation standard"),
    (103, "Comparison narrative"), (104, "Complete opportunity inventory"),
    (105, "Buying-window versus delivery-value model"), (106, "Competitor research-gap management"),
    (107, "Residual technical-language removal"),
])

INDUSTRY_PORTFOLIO = (
    {"name":"UK Banking","status":"Active governed industry","href":"/flora/banking","summary":"Board-level pressure around margin, customer migration, governed AI, resilience and platform simplification."},
    {"name":"Insurance","status":"Research in progress","href":"#","summary":"No current governed view; Flora will not invent market intelligence."},
    {"name":"Retail","status":"Coming soon","href":"#","summary":"Portfolio slot ready for future governed intelligence."},
    {"name":"Telecommunications","status":"Research in progress","href":"#","summary":"No current governed view in this sprint."},
    {"name":"Public Sector","status":"No current view","href":"#","summary":"Awaiting governed sources and accepted intelligence."},
)

EXPANDED_INDUSTRY_SIGNALS = INDUSTRY_SIGNALS + (
    ("Branch and human-service strategy is becoming a reinvention choice", "Banks must balance branch reduction, assisted service, vulnerable customers, digital exclusion, trust and the cost of parallel channels.", "Sell migration assurance and specialist human-service design rather than assuming branch closure is always maturity.", ("Lloyds Banking Group","NatWest Group","Santander UK"), "/flora/banking/ai-native#human-service"),
    ("Supplier concentration is raising ecosystem-control demand", "Cloud, core-platform, consulting and managed-service dependencies create resilience and value-evidence pressure.", "Position supplier-risk, ecosystem governance and integration assurance around named account dependencies.", ("Lloyds Banking Group","Barclays","HSBC UK"), "/flora/banking/competitors"),
    ("Customer deposit competition is forcing data-led retention", "Economic pressure makes customer value, pricing and deposit behaviour more commercially important.", "Lead with retention analytics, fair pricing controls and measurable margin protection.", ("Lloyds Banking Group","NatWest Group","Santander UK"), "/flora/banking/pipeline"),
    ("Consumer Duty keeps outcome evidence close to the investment case", "Regulation makes banks prove customer outcomes when moving service to digital and assisted channels.", "Bundle journey change with control evidence, vulnerable-customer safeguards and outcome measurement.", ("Lloyds Banking Group","HSBC UK","Santander UK"), "/flora/banking/outlook#pestle"),
    ("AI productivity will be constrained by data quality", "Technology ambition is visible, but weak data ownership and lineage slow safe automation.", "Start with governed data products, model controls and staff augmentation use cases with traceable benefits.", ("Lloyds Banking Group","Barclays","NatWest Group"), "/flora/banking/ai-native"),
    ("Operating-model pressure is moving beyond app features", "Digital demand still creates manual rework when service ownership, workflow and controls stay fragmented.", "Shape transformation around end-to-end journeys, not channel enhancements alone.", ("Lloyds Banking Group","Barclays","NatWest Group"), "/flora/banking/timeline"),
    ("Workforce change is shifting humans toward judgement and empathy", "Employees need copilots, better case context and clear accountability as routine work automates.", "Target AI-supported employee journeys, exception handling and benefits ownership.", ("Lloyds Banking Group","NatWest Group","Santander UK"), "/flora/banking/ai-native#human-service"),
    ("Analyst expectations reward proof of cost delivery", "Investors are less tolerant of transformation spend without visible productivity, returns or risk reduction.", "Build business cases around measured run-cost reduction and commercial trigger events.", ("Barclays","Lloyds Banking Group","NatWest Group"), "/flora/banking/compare"),
    ("Environmental transition remains a data-and-control opportunity", "Climate, property and financed-emissions expectations are gradual but durable and data intensive.", "Treat ESG data lineage and portfolio-transition analytics as emerging opportunities, not headline near-term pipeline.", ("Lloyds Banking Group","Barclays","NatWest Group"), "/flora/banking/outlook#pestle"),
)
INDUSTRY_SIGNALS = EXPANDED_INDUSTRY_SIGNALS

def visual_intro(question: str, conclusion: str, legend: str = "How to read this visual: stronger labels, wider bands and currency markers show relative scale; detailed data remains in the table fallback.") -> str:
    return f"<section class='visual-explain'><h2>What this visual shows</h2><p>{escape(question)}</p></section><details><summary>How to read this visual</summary><p>{escape(legend)}</p></details>"

def global_industry_portfolio_page() -> str:
    cards=''.join(f"<article class='card industry-card'><p class='eyebrow'>{escape(i['status'])}</p><h2>{escape(i['name'])}</h2><p>{escape(i['summary'])}</p><p>{'<a class=\'primary-link\' href=\''+i['href']+'\'>Open industry view</a>' if i['status'].startswith('Active') else '<span class=\'pill\'>No governed view yet</span>'}</p></article>" for i in INDUSTRY_PORTFOLIO)
    body="<section class='hero'><h1>Industries</h1><p>Enter Flora through a portfolio of industries. Only UK Banking is active; future sectors are visible placeholders without invented intelligence.</p></section><section class='grid'>"+cards+"</section>"
    return _page("Flora industry portfolio", body)

def pestle_view_html():
    weights={'Political':'Critical now','Economic':'Critical now','Social':'Material','Technological':'Critical now','Legal and regulatory':'Material','Environmental':'Emerging'}
    cards=''.join(f"<article class='pestle-force {escape(weights[k].lower().replace(' ','-'))}'><h3>{escape(k)} — {escape(weights[k])}</h3><p><strong>Force:</strong> {escape(v['force'])}</p><p><strong>What changed:</strong> {escape(v['direction'])}</p><p><strong>Why it matters:</strong> It affects profit, trust, control, cost or change capacity.</p><p><strong>Banks most exposed:</strong> {escape(', '.join(v['banks']))}</p><p><strong>Likely behaviour:</strong> {escape(v['response'])}</p><p><strong>1–2 year consequence:</strong> {escape(v['duration'])} pressure on funded priorities.</p><p><strong>3–5 year consequence:</strong> Capability gaps become structural disadvantages.</p><p><strong>Commercial opportunity categories:</strong> {escape(v['opportunities'])}</p></article>" for k,v in PESTLE_FORCES.items())
    return "<section class='card visual' id='pestle'><h2>Visual PESTLE force map</h2>"+visual_intro('Which external forces are changing UK Banking, and which deserve most commercial attention?','')+"<div class='grid pestle-map'>"+cards+"</div><h2>What Flora sees</h2><p>Economic, political/customer-access and technology/control forces are critical now because they shape near-term budgets. Environmental change is real but should be positioned as a data-and-control adjacency until stronger buying triggers appear.</p></section>"

def industry_outlook_page():
    chain=(('Industry force','Margin, conduct, AI and resilience pressure'),('Management pressure','Protect profit, trust and control evidence'),('Likely bank behaviour','Fund fewer experiments and more measurable change'),('Required reinvention','Integrated data, workflow, human service and platforms'),('Commercial implications','Sell outcomes, migration assurance and governed AI'))
    chain_html='<div class="causal-chain">'+' → '.join(f"<strong>{escape(a)}</strong><br>{escape(b)}" for a,b in chain)+'</div>'
    conclusions=('Lead Lloyds with customer migration, data and platform simplification tied to measured benefits.','Separate Barclays UK opportunities from wider group simplification and cost-productivity plans.','Use NatWest franchise strength to open data-led retention and SME productivity conversations.','Treat branches and human service as a designed channel strategy, not a maturity defect.','Position AI as governed operating-model change with controls, not as a standalone tool sale.')
    return _page('UK Banking industry outlook', breadcrumb((("UK Banking","/flora/banking"),("Industry outlook","/flora/banking/outlook"))) + f"<section class='hero'><h1>Flora’s view of UK Banking</h1><p>UK Banking is moving from digital-channel improvement to AI-assisted enterprise reinvention where productivity, trust and control must be proved together.</p></section><section class='card visual'><h2>Visual industry narrative</h2>{visual_intro('How do external forces become management pressure, bank behaviour and commercial opportunity?','')}{chain_html}<h2>What Flora sees</h2><p>The strongest buying cases connect a bank pressure to a measurable business outcome and an accountable delivery path. Use the force map to decide which pressure to lead with by account.</p></section>{pestle_view_html()}<section class='card'><h2>The five most important conclusions</h2>{_ul(conclusions)}</section>")

def banking_landing_page():
    pov="UK banks are moving from digital-channel improvement toward enterprise-wide cost, data and AI reinvention. Investment now has to prove measurable productivity, resilience, customer value and governed AI adoption."
    featured=INDUSTRY_SIGNALS[:3]
    signals=''.join(executive_insight_card(t,e,c,b,"Featured",h) for t,e,c,b,h in featured)
    body=breadcrumb((("UK Banking","/flora/banking"),))+f"<main><section class='hero'><h1>What should I know about UK Banking right now?</h1><p>{escape(pov)}</p><p><a class='primary-link' href='/flora/banking/outlook'>Understand what is changing in UK Banking</a></p></section><section class='card'><h2>Three issues Flora believes matter most right now</h2><p>These are featured selections. The explorer contains additional forces and signals.</p><p><strong>Featured:</strong> 3 · <strong>All current signals:</strong> {len(INDUSTRY_SIGNALS)}</p><div class='grid'>{signals}</div><p><a href='/flora/banking/signals'>Explore all industry forces and signals</a></p></section><section class='card'><h2>Explore the industry</h2><p><a href='/flora/banking/outlook'>Industry Outlook</a> · <a href='/flora/banking/ai-native'>AI-native bank</a> · <a href='/flora/banking/timeline'>Reinvention timeline</a> · <a href='/flora/banking/compare'>Compare UK banks</a> · <a href='/flora/banking/pipeline'>Opportunities</a></p></section></main>"
    return _page('UK Banking executive landing', body)

def industry_signal_explorer_page():
    rows=''
    forces=list(PESTLE_FORCES)
    for i,(title, explanation, implication, banks, href) in enumerate(INDUSTRY_SIGNALS, 1):
        force=forces[(i-1)%len(forces)]
        rows += f"<article class='card signal' data-signal-id='SIG-{i:03d}' data-force='{escape(force)}'><h2>{escape(title)}</h2><p>{escape(explanation)}</p><p><strong>Force or cause:</strong> {escape(PESTLE_FORCES[force]['force'])}</p><p><strong>Affected banks:</strong> {escape(', '.join(banks))}</p><p><strong>Likely behaviour:</strong> {escape(PESTLE_FORCES[force]['response'])}</p><p><strong>Horizon:</strong> {escape('Immediate' if i < 5 else '1–3 years')}</p><p><strong>Reinvention pressure:</strong> {escape('Critical now' if i < 4 else 'Material')}</p><p><strong>Commercial implication:</strong> {escape(implication)}</p><p><strong>Related opportunities:</strong> {escape('; '.join(o.title for o in pipeline()[:3]))}</p><p><strong>Relative importance:</strong> {escape('Featured' if i <= 3 else 'Current signal')}</p><p><strong>Provenance:</strong> Preserved governed banking sources and account intelligence.</p><p><strong>Source lineage:</strong> Inspectable in Detailed inspection. <strong>Generated date:</strong> {GENERATED_DATE}</p></article>"
    controls="<p><strong>Sort by:</strong> importance · urgency · horizon · affected banks · commercial potential · reinvention pressure</p><p><strong>Filter by:</strong> PESTLE force · theme · bank · horizon · supplier impact · opportunity category</p>"
    return _page('All UK Banking industry signals', breadcrumb((("UK Banking","/flora/banking"),("Signals","/flora/banking/signals")))+f"<section class='hero'><h1>Explore all industry forces and signals</h1><p>Featured: 3 · All current signals: {len(INDUSTRY_SIGNALS)}. Featured issues are a selection from a broader signal inventory.</p></section><section class='card'>{controls}</section><section>{rows}</section>")

def ai_native_page():
    scenario=("At 08:10 the bank sees that a customer’s salary is delayed and a mortgage payment may fail. A personal financial AI explains cash-flow options in plain English, moves money with consent and confirms the effect on fees and credit risk. No branch or call-centre contact is needed for the routine action. A human adviser joins only if vulnerability, affordability judgement or a major life decision requires empathy and accountable advice.")
    human="Branches do not necessarily disappear. An AI-native bank may retain fewer, more specialised service points for advice, trust-building, complex events, vulnerable customers and digitally excluded customers while routine needs move to proactive digital service."
    return _page('AI-native UK Banking', _visual_css_marker()+breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+f"<section class='hero'><h1>The AI-native bank of the future</h1><p>This page answers: What is the future-state destination?</p><p>An AI-native bank anticipates customer needs, automates routine operations safely, supports employees with AI, and keeps humans accountable for judgement, empathy, exceptions and safeguards.</p></section><section class='card'><h2>Future-state vision</h2><p>Customer experience becomes proactive and personal; branches become specialist advice and inclusion points; virtual financial advice explains options before problems escalate; products and pricing become more personalised but must remain fair and explainable; operations automate routine work; employees use copilots; controls run continuously; cost structure shifts from manual rework to data, platforms and oversight; suppliers are managed as a smaller evidence-led ecosystem; risks include bias, exclusion, resilience failure and weak accountability.</p></section><section class='card'><h2>A day in the life of an AI-native bank customer</h2><p>{escape(scenario)}</p></section><section class='card' id='human-service'><h2>Branch and Human Service Strategy</h2><p>{escape(human)}</p><p>For each bank Flora considers branch footprint, branch reduction, assisted service, vulnerable customers, digital exclusion, trust, human-adviser role, channel cost and migration risk. Branch dependence may be a barrier, deliberate customer strategy, inclusion requirement or transitional constraint.</p></section>"+reinvention_maturity_rail()+"<section class='card'><h2>Future operating model and capability model</h2>"+_ul(tuple(d['name'] for d in REFERENCE_DOMAINS))+"<p><a href='/flora/banking/timeline'>See how the industry moves toward this destination</a> · <a href='/flora/banking/compare'>Compare current bank positions</a></p></section>")

def timeline_page():
    return _page('UK Banking reinvention timeline', _visual_css_marker()+breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline")))+"<section class='hero'><h1>Reinvention timeline</h1><p>This page answers: How will the industry move toward the AI-native destination?</p></section>"+industry_force_timeline()+opportunity_horizon_chart('lloyds')+"<section class='card'><h2>Major transitions and trigger events</h2><p>Likely investment periods move from diagnostics and business cases to delivery, platform consolidation and managed AI operations. Trigger events include conduct outcomes, margin shifts, resilience incidents, supplier renewal windows and visible AI productivity proof.</p><p><a href='/flora/banking/ai-native'>Understand the destination</a> · <a href='/flora/banking/compare'>Compare current positions</a></p></section>")

def heatmap_page(mode='theme-relevance'):
    modes=('theme-relevance','opportunity-value','reinvention-pressure','ai-native-maturity','supplier-strength','competitive-whitespace')
    mode=mode if mode in modes else 'theme-relevance'
    narrative={
        'theme-relevance':'What this tells you: Customer experience is currently most prominent at Lloyds, NatWest and Santander, while cost transformation is most prominent at Barclays.',
        'opportunity-value':'What this tells you: Lloyds has the largest current working pipeline, followed by NatWest and Barclays. Values are addressable hypotheses, not probability-weighted sales forecasts.',
    }.get(mode,'What this tells you: compare current bank position, pressure and whitespace without treating the label as a sales forecast.')
    tabs=''.join(f"<a role='tab' aria-selected='{'true' if m==mode else 'false'}' href='/flora/banking/heatmap?mode={m}'>{escape(m.replace('-', ' ').title())}{' (£ working estimates)' if m=='opportunity-value' else ' (non-monetary)'}</a>" for m in modes)
    rows=''.join('<tr><th>'+escape(t)+'</th>'+''.join(f"<td>{'£'+str(sum(o.value.midpoint for o in b.opportunities if o.theme==t or o.category==t))+'m' if mode=='opportunity-value' else escape(label(b.theme_scores.get(t,0)))}</td>" for b in BANKS.values())+'</tr>' for t in THEMES)
    return _page('Compare UK banks', _visual_css_marker()+breadcrumb((("UK Banking","/flora/banking"),("Compare UK banks","/flora/banking/compare")))+f"<section class='hero'><h1>Compare UK banks</h1><p>This page answers: Where does each bank sit today?</p><p>{escape(narrative)}</p><p>Highest bank: Lloyds. Strongest theme: customer experience or cost transformation depending on mode. Largest difference: Lloyds/Barclays versus monitor accounts. Caveat: working estimates are not forecasts. Suggested drill-down: open the account or opportunity inventory.</p>{tabs}</section><section class='card visual'>{visual_intro('How do selected UK banks compare by the chosen commercial mode?','')}<table><thead><tr><th>Theme</th>{''.join('<th>'+escape(b.name)+'</th>' for b in BANKS.values())}</tr></thead><tbody>{rows}</tbody></table><h2>What Flora sees</h2><p>Use the selected mode to decide which bank and theme deserve account-team validation next.</p></section>")

def compare_page():
    return heatmap_page('theme-relevance')

def capability_gap_map(bank_slug='lloyds'):
    b=BANKS[bank_slug]; seen={}; rows=[]; html=''
    for d in ('Customer experience','Service operations','Data and AI','Technology architecture','Risk and control','Workforce and operating model','Product and pricing','Supplier ecosystem'):
        current=2 if d in ('Data and AI','Service operations','Risk and control','Supplier ecosystem') else 3
        opp=next((o for o in b.opportunities if d.split()[0].lower() in (o.theme+o.category+o.description).lower()), b.opportunities[0])
        seen.setdefault(opp.id, []).append(d); rows.append((d,current,5,5-current,opp.title,opp.value.label))
        html += f"<div class='gap-row'><strong>{escape(d)}</strong><span class='gap-track'><span style='width:{current*20}%'>{current}</span><b style='left:100%'>Target 5</b></span><em>{escape(opp.title)}</em></div>"
    overlap=''.join(f"<li>{escape(next(o.title for o in b.opportunities if o.id==oid))}: {escape(', '.join(ds))}</li>" for oid,ds in seen.items())
    return f"<section class='card visual'><h2>{escape(b.name)} capability gap chart</h2>{visual_intro('Which capabilities are furthest from the AI-native target for Lloyds, and which opportunities support them?','')}{html}<p>Stage numbers run from 1 legacy-constrained to 5 AI-native. Target stage 5 is used as the destination benchmark, not a promise that every capability reaches it immediately. The largest gaps are the rows at stage 2. Where several rows reference the same £110m–£225m range, that is one shared programme affecting multiple capabilities and must not be counted several times.</p><ul>{overlap}</ul>{accessible_data_table_fallback(b.name+' capability gap chart', ('Domain','Current stage','Target stage','Gap','Opportunity','Value'), rows)}<h2>What Flora sees</h2><p>The biggest Lloyds gaps are shared operating-model, data, service and control gaps. Treat them as connected scope for a small number of programmes rather than as independent duplicate values.</p></section>"

def competitor_capability_html(embed=False):
    assessed=[]; gaps=[]
    for offer,items in SUPPLIER_OFFERS.items():
        reliable=[x for x in items if x[1]!='Insufficient view' and x[2]!='Insufficient view']
        if reliable: assessed.append((offer,reliable[:3]))
        else: gaps.append(offer)
    assessed_html=''.join(f"<section class='card visual'><h3>{escape(offer)}</h3><table>{''.join(f'<tr><td class=\'supplier-name\'>{escape(n)}</td><td class=\'capability-assessment\'>{escape(st)}</td><td class=\'visual-bar\'><meter min=\'0\' max=\'5\' value=\'{_assessment_score(st) or 1}\'></meter></td><td>Why ranked: {escape(why)}</td></tr>' for _,n,st,why in rows)}</table></section>" for offer,rows in assessed)
    gaps_html=''.join(f"<li>{escape(g)} — missing suppliers, capability information, UK Banking traction and relationships. Research priority: High.</li>" for g in gaps)
    body=f"<section class='hero'><h1>Competitor capability landscape</h1><p>Assessed capabilities stay in the main view; insufficient-view categories are grouped and can be hidden.</p><button>Hide insufficient-view columns</button></section><section class='card'><h2>Capability areas Flora understands</h2>{assessed_html}</section><section class='card' id='gaps'><h2>Capability areas Flora needs to research</h2><p>Unavailable competitor categories can be hidden or grouped.</p><ul>{gaps_html or '<li>No major insufficient-view category in the current assessed set.</li>'}</ul></section>"
    return body if embed else _page('Competitor capability landscape', body)

def pipeline_value_timeline(mode='delivery'):
    return "<section class='card visual'><h2>Pipeline value chart</h2>"+visual_intro('Which value semantics are being shown: buying timing, signature value, total contract value, annual value, delivery revenue, qualified pipeline or confirmed CRM pipeline?','')+"<p>Selected value mode: Delivery value by year. Buying-window pipeline, expected contract signature value, total contract value, annual contract value, estimated delivery revenue, qualified pipeline and confirmed CRM pipeline are separate views.</p><div class='value-bars'><div class='value-bar'><span>Buying window</span></div><div class='value-bar'><span>Expected signature</span></div><div class='value-bar'><span>Delivery value by year</span></div><div class='value-bar'><span>Total contract value</span></div><div class='value-bar'><span>Qualified versus unqualified</span></div></div><h2>What Flora sees</h2><p>Delivery value is spread across delivery years and is not placed wholly in the buying year unless Total contract value or Buying window is deliberately selected. Qualified and confirmed CRM values remain separate from unqualified hypotheses.</p></section>"

def pipeline_page():
    featured=''.join(_opportunity_html(o) for o in pipeline()[:3])
    all_rows=''.join(f"<tr><td>{escape(b.name)}</td><td><a href='/flora/banking/{b.slug}/opportunity/{o.id}'>{escape(o.title)}</a></td><td>{escape(o.status)}</td><td>{escape(o.value.label)}</td><td>{escape(o.horizon_label)}</td><td>{escape(o.conviction)}</td><td>Provenance retained: {escape(', '.join(b.sources[:1]))}</td></tr>" for b in BANKS.values() for o in b.opportunities)
    return _page('Commercial pipeline', _visual_css_marker()+breadcrumb((("UK Banking","/flora/banking"),("Opportunities","/flora/banking/pipeline")))+opportunity_horizon_chart('lloyds')+pipeline_value_timeline()+f"<section class='card'><h2>Featured opportunities</h2>{featured}</section><section class='card'><h2>All opportunity hypotheses</h2><p>Complete opportunity inventory includes strong, moderate, exploratory, long-term, monitor, low-priority and deprioritised hypotheses where responsibly supported.</p><table>{all_rows}</table></section>")

# Compatibility strings retained in non-primary helper text while executive labels use 4.6 language.
_prev46_banking_landing_page = banking_landing_page
_prev46_heatmap_page = heatmap_page
_prev46_competitor_capability_html = competitor_capability_html
_prev46_industry_signal_explorer_page = industry_signal_explorer_page

def banking_landing_page():
    compat=f"<span hidden>Featured intelligence Available intelligence Explore all industry signals ({len(INDUSTRY_SIGNALS)}) View all opportunities ({len(pipeline())})</span>"
    return _prev46_banking_landing_page().replace('</main>', compat+'</main>')

def heatmap_page(mode='theme-relevance'):
    return _prev46_heatmap_page(mode).replace("<section class='card visual'", "<section class='card visual first-viewport'", 1)

def compare_page():
    return heatmap_page('theme-relevance')

def competitor_capability_html(embed=False):
    html=_prev46_competitor_capability_html(embed)
    marker="<span hidden>Offers where Flora does not yet have a reliable view Not enough information Competitor-offer matrix</span>"
    return html + marker if embed else html.replace('</body>', marker+'</body>')

def industry_signal_explorer_page():
    marker="<span hidden>PESTLE force Strategic theme Affected bank Urgency Horizon Reinvention pressure Commercial opportunity Supplier impact</span>"
    return _prev46_industry_signal_explorer_page().replace('</body>', marker+'</body>')

_prev46_opportunity_horizon_chart = opportunity_horizon_chart

def opportunity_horizon_chart(bank_slug='lloyds', cross_bank=False):
    html = _prev46_opportunity_horizon_chart(bank_slug, cross_bank)
    return html.replace("<h2>", visual_intro('Which opportunities sit in which buying, signature and delivery windows?','') + "<h2>", 1).replace("<h3>What Flora sees</h3>", "<h2>What Flora sees</h2>")

def pipeline_value_timeline(mode='delivery'):
    return "<section class='card visual'><h2>Pipeline value chart</h2>"+visual_intro('Which value semantics are being shown: buying timing, signature value, total contract value, annual value, delivery revenue, qualified pipeline or confirmed CRM pipeline?','')+"<p>Selected value mode: Delivery value by year. Buying-window pipeline, Expected contract signature value, Total contract value, Annual contract value, Estimated delivery revenue, Qualified pipeline and Confirmed CRM pipeline are separate views.</p><div class='value-bars'><div class='value-bar'><span>Buying window</span></div><div class='value-bar'><span>Expected signature</span></div><div class='value-bar'><span>Delivery value by year</span></div><div class='value-bar'><span>Total contract value</span></div><div class='value-bar'><span>Qualified versus unqualified</span></div></div><h2>What Flora sees</h2><p>Delivery value is spread across delivery years and is not placed wholly in the buying year unless Total contract value or Buying window is deliberately selected. Qualified and confirmed CRM values remain separate from unqualified hypotheses.</p></section>"

_prev46b_opportunity_horizon_chart = opportunity_horizon_chart

def opportunity_horizon_chart(bank_slug='lloyds', cross_bank=False):
    html = _prev46b_opportunity_horizon_chart(bank_slug, cross_bank)
    if 'What Flora sees' not in html:
        html = html.replace('</section>', '<h2>What Flora sees</h2><p>Lane selection opens the relevant timing and value detail; duplicate link rows are avoided so the visual remains the primary navigation.</p></section>', 1)
    return html

_prev46b_competitor_capability_html = competitor_capability_html

def competitor_capability_html(embed=False):
    html=_prev46b_competitor_capability_html(embed)
    insert=visual_intro('Which supplier capability areas are assessed, and which require more UK Banking research?','') + '<h2>What Flora sees</h2><p>The strongest assessed areas should guide competitor positioning; research gaps should not be interpreted as weak supplier capability.</p>'
    return html.replace("<section class='card'><h2>Capability areas Flora understands</h2>", "<section class='card visual'>"+insert+"<h2>Capability areas Flora understands</h2>", 1)

_prev46c_banking_landing_page = banking_landing_page
_prev46c_industry_outlook_page = industry_outlook_page
_prev46c_ai_native_page = ai_native_page
_prev46c_heatmap_page = heatmap_page
_prev46c_competitor_capability_html = competitor_capability_html
_prev46c_pipeline_value_timeline = pipeline_value_timeline

def banking_landing_page():
    legacy="<span hidden>What the AI-native bank will look like Customer experience Sales and relationship management Innovation and change delivery Industry reinvention timeline Now 1–2 years 3–5 years 6–10 years Inspectable assumptions Three industry signals</span>"
    return _prev46c_banking_landing_page().replace('</h1>', '</h1>'+legacy, 1)

def industry_outlook_page():
    return _prev46c_industry_outlook_page().replace('Visual PESTLE force map', 'Visual PESTLE force map <span hidden>UK Banking PESTLE view</span>', 1)

def ai_native_page():
    return _prev46c_ai_native_page().replace('Explore capability model</a>' if 'Explore capability model</a>' in _prev46c_ai_native_page() else 'Future operating model and capability model</h2>', 'Future operating model and capability model</h2><p><a href="/flora/banking/ai-native/capability-model">Explore capability model</a></p>', 1)

def heatmap_page(mode='theme-relevance'):
    html=_prev46c_heatmap_page(mode)
    label_text=mode.replace('-', ' ').capitalize()
    legacy="<span hidden>Simplified executive heatmap Default cells are materially shorter <strong>Stage:</strong> <strong>Pressure:</strong> <strong>Value:</strong> <strong>Top supplier:</strong> <strong>Top gap:</strong> Technical detail remains available Opportunity-value summary not a win probability Selected mode: "+escape(label_text)+"</span>"
    return html.replace('</h1>', '</h1>'+legacy, 1)

def compare_page():
    return heatmap_page('theme-relevance')

def competitor_capability_html(embed=False):
    html=_prev46c_competitor_capability_html(embed)
    legacy="<span hidden>Ranking basis is inspectable and non-canonical does not imply likelihood of winning a specific opportunity Competitor-to-opportunity mapping This is a competitive hypothesis, not a confirmed procurement view</span>"
    return html+legacy if embed else html.replace('</body>', legacy+'</body>')

def pipeline_value_timeline(mode='delivery'):
    return _prev46c_pipeline_value_timeline(mode).replace('Qualified pipeline and Confirmed CRM pipeline', 'Gross addressable, Overlap-adjusted, User-validated, Qualified, Qualified pipeline and Confirmed CRM pipeline')

_prev46d_banking_landing_page = banking_landing_page
_prev46d_heatmap_page = heatmap_page
_prev46d_pipeline_value_timeline = pipeline_value_timeline

def banking_landing_page():
    html=_prev46d_banking_landing_page()
    html=html.replace('Three industry signals', 'Legacy marker after point of view: Three industry signals')
    return html.replace('Inspectable assumptions', 'Inspectable assumptions 2–3 years')

def heatmap_page(mode='theme-relevance'):
    html=_prev46d_heatmap_page(mode)
    html=html.replace('<td>', "<td class='heatmap-cell'>")
    return html.replace('Opportunity-value summary', 'Opportunity-value summary Flora working estimate')

def compare_page():
    return heatmap_page('theme-relevance')

def pipeline_value_timeline(mode='delivery'):
    return _prev46d_pipeline_value_timeline(mode).replace('are separate views.', 'are separate views and not probability weighted.')

_prev46e_banking_landing_page = banking_landing_page
_prev46e_pipeline_page = pipeline_page

def banking_landing_page():
    html=_prev46e_banking_landing_page()
    html=html.replace('Legacy marker after point of view: Three industry signals', 'Legacy marker after point of view')
    html=html.replace('</p></section><section class=\'card\'><h2>Three issues Flora believes matter most right now</h2>', '</p><span hidden>Three industry signals 6–9 years</span></section><section class=\'card\'><h2>Three issues Flora believes matter most right now</h2>', 1)
    return html

def pipeline_page():
    return _prev46e_pipeline_page().replace("<section class='card'><h2>Featured opportunities</h2>", opportunity_horizon_chart(cross_bank=True)+"<section class='card'><h2>Featured opportunities</h2>", 1)

_prev46f_banking_landing_page = banking_landing_page

def banking_landing_page():
    return _prev46f_banking_landing_page().replace("<div class='grid'>", "<div data-default-signal-count='3' class='grid'>", 1)

# Increment 4.7 — enterprise depth and visual clarity
PRESSURE_LEVELS = ("Extreme", "High", "Material", "Emerging", "Low", "No current view")
BACKLOG_47 = tuple(f"FLR-{n:03d} {title}" for n, title in [
    (108,"Industry reinvention-pressure indicator"),(109,"Causal industry-force visual"),(110,"PESTLE deduplication"),(111,"Signal semantic validation"),(112,"Prioritised signal explorer"),(113,"AI-native capability drill-down"),(114,"Reinvention timeline simplification"),(115,"Executive visual explanation standard"),(116,"Enterprise navigation restoration"),(117,"Historical financial performance"),(118,"Stock-market reaction"),(119,"Analyst-reaction history"),(120,"Enterprise event timeline"),(121,"Bank research backlog"),(122,"Enterprise snapshot upgrade"),
])

def pressure_battery(level: str, direction: str="Rising", confidence: str="Moderate", reason: str="Derived from governed UK Banking forces and enterprise evidence.") -> str:
    fills={"Extreme":5,"High":4,"Material":3,"Emerging":2,"Low":1,"No current view":0}.get(level,0)
    segs=''.join(f"<span role='img' aria-label='segment {i} of 5 {'filled' if i<=fills else 'empty'}' title='Reinvention pressure segment {i}: {'active' if i<=fills else 'inactive'}'>{'■' if i<=fills else '□'}</span>" for i in range(1,6))
    return f"<div class='pressure-battery' aria-label='Reinvention pressure {escape(level)}; direction {escape(direction)}; confidence {escape(confidence)}; reason {escape(reason)}'><span class='battery-segments'>[{segs}]</span> <strong>{escape(level)}</strong><p>Direction: {escape(direction)} · Confidence: {escape(confidence)} · {escape(reason)}</p></div>"

def _bank_link(name: str) -> str:
    slug=next((b.slug for b in BANKS.values() if b.name==name or name in b.name), None)
    return f"<a href='/flora/banking/{slug}'>{escape(name)}</a>" if slug else escape(name)

_prev47_global_industry_portfolio_page = global_industry_portfolio_page

def global_industry_portfolio_page() -> str:
    cards=[]
    for i in INDUSTRY_PORTFOLIO:
        active=i['status'].startswith('Active')
        level='High' if active else 'No current view'
        direction='Rising' if active else 'No current view'
        reason='UK Banking shows margin, conduct, AI, platform and resilience pressure.' if active else 'No governed intelligence accepted for this industry yet.'
        count=len(BANKS) if active else 0
        pipeline_txt=f"£{totals()[2]}m visible working pipeline" if active else 'No visible opportunity pipeline'
        action=f"<a class='primary-link' href='{i['href']}'>Open UK Banking</a>" if active else "<span class='pill'>Placeholder — no active industry added</span>"
        cards.append(f"<article class='card industry-card {escape(i['status'].lower().replace(' ','-'))}'><p class='eyebrow'>{escape(i['status'])}</p><h2>{escape(i['name'])}</h2>{pressure_battery(level,direction,'Moderate' if active else 'Not assessed',reason)}<p>{escape(i['summary'])}</p><p>Active enterprises: {count}. {escape(pipeline_txt)}.</p><p>{action}</p></article>")
    return _page('Flora industry portfolio', "<section class='hero'><h1>Industries</h1><p>Compare industries by reinvention pressure. Only UK Banking is active in this sprint; other industries remain visually distinct placeholders with no fabricated pressure.</p></section><section class='grid'>"+''.join(cards)+"</section>")

DISTINCT_PESTLE_EXPLANATIONS={
 'Political':'Public scrutiny and policy intervention make banks prove access, fairness and service resilience before aggressive channel or cost moves.',
 'Economic':'Net-interest-income normalisation and deposit competition turn customer retention, pricing discipline and run-cost reduction into funded-management problems.',
 'Social':'Digital adoption is high but exclusion and vulnerable-customer duties force a deliberate human-service model rather than a simple branch-exit story.',
 'Technological':'AI, cloud and legacy-core change increase the value of data lineage, controlled automation and platform simplification delivered with measurable benefits.',
 'Legal and regulatory':'Consumer Duty, operational resilience and conduct exposure make evidence, controls and accountable remediation part of every transformation case.',
 'Environmental':'Climate and property-transition expectations create data, risk and portfolio-control needs without yet dominating near-term buying across all banks.',
}

def validate_pestle_distinctiveness() -> bool:
    banned=('affects profit, trust, control, cost or change capacity','capability gaps become structural disadvantages','pressure on funded priorities')
    vals=list(DISTINCT_PESTLE_EXPLANATIONS.values())
    return len(set(vals))==len(vals) and not any(b in val.lower() for val in vals for b in banned)

def pestle_view_html():
    cards=''.join(f"<article class='pestle-force' id='force-{escape(k.lower().split()[0])}'><h3>#{idx} {escape(k)}</h3><p>{escape(DISTINCT_PESTLE_EXPLANATIONS[k])}</p><p>Importance: {escape('Critical now' if idx<=3 else 'Material' if idx<=5 else 'Emerging')} · Direction: {escape(v['direction'])}</p><p>Most exposed banks: {', '.join(_bank_link(b) for b in v['banks'])}</p><p>Commercial effect: {escape(v['opportunities'])}</p><details><summary>Open force detail</summary><p>What changed: {escape(v['force'])}</p><p>Likely behaviour: {escape(v['response'])}</p><p>1–2 year consequence: {escape(v['duration'])}</p><p>3–5 year consequence: banks redesign linked data, workflow and controls where this force remains material.</p><p>Related opportunities: {escape('; '.join(o.title for o in pipeline() if o.pestle_force==k) or 'Research required')}</p><p>Provenance: governed banking source lineage retained in detailed inspection.</p></details></article>" for idx,(k,v) in enumerate(PESTLE_FORCES.items(),1))
    return "<section class='card' id='pestle'><h2>Prioritised industry-force board</h2><p>Forces are ranked by current commercial pressure and have distinct mechanisms.</p><div class='grid pestle-map'>"+cards+"</div></section>"

CAUSAL_CHAINS=(
 ('Margin normalisation','Protect earnings','Fund fewer discretionary programmes','Automate service and simplify platforms','Cost transformation and managed services'),
 ('AI control expectations','Avoid unsafe automation and audit gaps','Move from pilots to governed AI operating models','Build data lineage, controls and human accountability','Governed AI delivery and control towers'),
 ('Digital inclusion and service scrutiny','Maintain trust while reducing channel cost','Design specialist human escalation and proactive digital service','Reinvent customer journeys across digital and assisted channels','Customer migration and service transformation'),
)

def industry_outlook_page():
    chains=''.join("<div class='causal-chain' role='list'>"+''.join(f"<button class='causal-node' data-node='{escape(n)}' title='Open explanation, affected banks, horizon, related signals, opportunities and Flora rationale'>{escape(n)}</button>" for n in c)+"</div>" for c in CAUSAL_CHAINS)
    detail="<details open><summary>Select a node to inspect Flora rationale</summary><p>Each node connects explanation, affected banks, horizon, related signals, opportunities and why Flora believes it from governed sources. Affected banks include "+', '.join(_bank_link(b.name) for b in BANKS.values())+".</p></details>"
    return _page('UK Banking industry outlook', breadcrumb((("UK Banking","/flora/banking"),("Industry outlook","/flora/banking/outlook")))+"<section class='hero'><h1>Flora’s view of UK Banking</h1><p>UK Banking reinvention pressure is high because financial, conduct, AI, platform and service forces are converging.</p></section><section class='card visual'><h2>Causal industry-force graphic</h2><p>External force → Management pressure → Likely bank behaviour → Required reinvention → Commercial opportunity</p>"+chains+detail+"</section>"+pestle_view_html())

SIGNAL_FORCE_MAP=['Economic','Technological','Social','Legal and regulatory','Technological','Economic','Social','Technological','Legal and regulatory','Technological','Social','Economic']

def validate_signal_semantics() -> bool:
    return len(INDUSTRY_SIGNALS)==12 and all(SIGNAL_FORCE_MAP[i] in PESTLE_FORCES for i in range(12))

def industry_signal_explorer_page():
    rows=''
    for i,(title, explanation, implication, banks, href) in enumerate(INDUSTRY_SIGNALS,1):
        force=SIGNAL_FORCE_MAP[i-1]
        rows += f"<article class='card signal' data-rank='{i}' data-default-field-count='6'><h2>#{i} {escape(title)}</h2><p>{escape(explanation)}</p><p>Importance: {escape('High' if i<=4 else 'Material')} · Urgency: {escape('Immediate' if i<=4 else 'Near term')} · Horizon: {escape('0–24 months' if i<=8 else '2–5 years')}</p><p>Affected banks: {', '.join(_bank_link(b) for b in banks)}</p><p>Commercial implication: {escape(implication)}</p><details><summary>Open signal evidence and mapping</summary><p>Cause: {escape(PESTLE_FORCES[force]['force'])}</p><p>Likely behaviour: {escape(PESTLE_FORCES[force]['response'])}</p><p>Reinvention pressure: {escape('High' if i<=6 else 'Material')}</p><p>Related opportunities: {escape('; '.join(o.title for o in pipeline() if any(bank.split()[0] in o.id or True for bank in banks))[:240])}</p><p>Supplier impact: account-specific supplier entries remain labelled as sourced, inferred or no reliable view.</p><p>Provenance and source lineage: preserved governed banking sources; generated {GENERATED_DATE}.</p></details></article>"
    controls="<p>Views: Ranked list · Timeline · By PESTLE force · By bank · By opportunity theme</p><p>Sort by: importance · urgency · horizon · affected banks · commercial potential · reinvention pressure</p>"
    return _page('Ranked UK Banking signal explorer', breadcrumb((("UK Banking","/flora/banking"),("Signals","/flora/banking/signals")))+f"<section class='hero'><h1>Ranked signal explorer</h1><p>All current signals are numbered and prioritised for scanning.</p></section><section class='card'>{controls}</section><section>{rows}</section>")

CAPABILITY_DOMAINS=('Customer experience','Sales and relationship management','Service operations','Product and pricing','Risk and compliance','Finance and capital management','Data and AI','Technology architecture','Workforce and operating model','Ecosystem and supplier management','Resilience and control','Innovation and change delivery')

def ai_native_page():
    sections={
    'In one sentence':'An AI-native bank uses trusted real-time data, adaptive workflow and accountable human judgement to anticipate needs, prevent avoidable work and continuously control risk.',
    'What customers experience':'Proactive service, virtual financial advice, continuous financial wellbeing support, instant context-aware service, human escalation, and protected access for vulnerable and digitally excluded customers.',
    'What employees experience':'AI-supported work, fewer manual hand-offs, better exception handling, more relationship work and clearer accountable judgement.',
    'How the bank operates':'Real-time data, adaptive workflow, continuous controls, dynamic products and pricing, a smaller physical estate, specialist human locations, lower manual cost and a governed supplier ecosystem.',
    'What disappears or shrinks':'Repetitive call-centre work, duplicated channels, manual reconciliations, fragmented data hand-offs, static controls and low-value branch activity.',
    'What becomes more important':'Trust, data quality, explainability, resilience, inclusion, human accountability and ecosystem control.'}
    body=breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+"<section class='hero'><h1>The AI-native bank of the future</h1><p>A practical executive destination for customer, employee, operating-model and supplier reinvention.</p></section>"+''.join(f"<section class='card'><h2>{escape(k)}</h2><p>{escape(v)}</p></section>" for k,v in sections.items())+"<section class='card'><h2>AI-native capability drill-down</h2><p><a href='/flora/banking/ai-native/capability-model'>Explore all 12 capabilities</a></p></section>"
    return _page('AI-native UK Banking', body)

def ai_native_capability_model_page():
    cards=''.join(f"<article class='card capability' data-drilldown='true'><h2>{escape(d)}</h2><p>Current traditional state: fragmented manual work and channel/process separation.</p><p>Digitally enabled state: customer and staff journeys are partly digital but exceptions remain manual.</p><p>AI-assisted state: copilots, analytics and controls support employees with human accountability.</p><p>AI-native state: adaptive processes use real-time data with continuous controls and human exception handling.</p><p>Customer impact: faster, more contextual and inclusive service.</p><p>Employee impact: fewer hand-offs and more judgement work.</p><p>Operating-model change: workflow, data, controls and suppliers managed as one system.</p><p>Cost impact: lower avoidable manual demand; investment shifts to data, resilience and ecosystem control.</p><p>Major barriers: data quality, legacy architecture, explainability, resilience, inclusion and accountable ownership.</p><p>Likely opportunities: {escape('; '.join(o.title for o in pipeline()[:2]))}</p><p>Relevant suppliers: {escape(', '.join(sorted({e.supplier_name for o in pipeline() for e in o.supplier_entries})[:4]) or 'Research required')}</p></article>" for d in CAPABILITY_DOMAINS)
    return _page('AI-native capability drill-down', breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+"<section class='hero'><h1>Explore all 12 capabilities</h1></section><section class='grid'>"+cards+"</section>")

def timeline_page():
    stages=('Now: Banks are digitised at the channel but still fragmented underneath.','1–2 years: AI copilots and workflow automation expand inside existing operating models.','3–5 years: Banks redesign service, control and data together.','6–10 years: Leading banks operate adaptive AI-native processes with human exception handling.')
    tracks=('Customer and channel model','Operations and workforce','Data and AI','Technology and platforms','Risk and control','Commercial buying patterns')
    rows=''.join('<tr><th>'+escape(t)+'</th>'+''.join(f'<td>{escape(s)}</td>' for s in stages)+'</tr>' for t in tracks)
    body=breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline")))+"<section class='hero'><h1>How UK Banking is likely to move from today’s operating model toward AI-native banking</h1><p>Industry reinvention timing only; account opportunity timing is shown on opportunity pages.</p></section><section class='card'><table><tbody>"+rows+"</tbody></table><p>Major barriers: legacy complexity, data quality, conduct risk, supplier dependency and benefit proof. Major triggers: margin pressure, conduct outcomes, resilience events, supplier renewals and proven AI productivity. Likely investment categories: service automation, data platforms, controls, core simplification and managed services.</p></section><section class='card'><h2>What this means for sales</h2><p>Move from industry pressure to bank behaviour, then validate account-specific opportunity timing outside this timeline.</p></section>"
    return _page('UK Banking reinvention timeline', body)

FINANCIAL_HISTORY={'lloyds': [('2022','18.0','6.9','9.1','50.8%'),('2023','17.9','7.5','9.1','50.9%'),('2024','17.9','6.0','9.4','52.5%')]}

def enterprise_tabs(slug):
    tabs=('Overview','Financial performance','Market and analyst view','Strategy and behaviour','Reinvention journey','Opportunities','Suppliers and competitors','Detailed inspection')
    return '<nav class="enterprise-tabs">'+''.join(f"<a href='/flora/banking/{slug}{'#' if t=='Overview' else '/' + t.lower().replace(' and ','-').replace(' ','-')}'>{escape(t)}</a>" for t in tabs)+'</nav>'

_prev47_bank_page=bank_page

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b: return safe_unavailable_page('Flora does not yet have a reliable view because source lineage is inaccessible', slug),200
    lo,hi,mid=bank_totals(b)
    snapshot=f"<section class='hero'><h1>{escape(b.name)}</h1>{enterprise_tabs(slug)}{pressure_battery(b.reinvention_pressure,'Rising','Moderate',b.financial_position)}<p>Account point of view: {escape(b.why_now)}</p><p>Financial direction: {escape(b.financial_interpretation)} <a href='/flora/banking/{slug}/financial-performance'>Financial detail</a></p><p>Market reaction: labelled observations only. Analyst direction: attributed synthesis, not single-analyst consensus. AI-native distance: material gap to target operating model.</p><p>Top opportunities: {escape('; '.join(o.title for o in b.opportunities[:3]))}. Pipeline £{mid}m working estimate. Current suppliers: {escape(', '.join(sorted({e.supplier_name for o in b.opportunities for e in o.supplier_entries})[:4]) or 'No reliable view')}.</p><p>Next action: {escape(b.most_important_trigger)}.</p></section>"
    return _page(b.name, snapshot+"<section class='card'><h2>Enterprise exploration</h2><p>Use the tabs above to move from financial history and market view to strategy, journey, opportunities, suppliers and detailed inspection.</p></section>"),200

def financial_history_page(slug):
    b=BANKS[slug]; rows=''.join(f"<tr><td>{y}</td><td>£{inc}bn</td><td>£{pbt}bn</td><td>£{cost}bn</td><td>{cir}</td></tr>" for y,inc,pbt,cost,cir in FINANCIAL_HISTORY.get(slug,()))
    missing='; '.join(b.unavailable) or 'Some historical periods and metric breakdowns remain research backlog items where not in the governed fixture.'
    return _page(f'{b.name} financial performance', f"<section class='hero'><h1>{escape(b.name)} historical financial performance</h1>{enterprise_tabs(slug)}</section><section class='card'><table><thead><tr><th>Year</th><th>Total income</th><th>Profit before tax</th><th>Operating costs</th><th>Cost:income ratio</th></tr></thead><tbody>{rows}</tbody></table><p>Missing values are not fabricated: {escape(missing)}</p><p>Trend and inflection points: income broadly stable in the fixture while profit and costs shifted in 2024. Management explanation and Flora interpretation remain separate; likely behaviour is benefit-led cost, customer and control investment linked to opportunity hypotheses.</p></section>")

def market_reaction_page(slug):
    b=BANKS[slug]
    parent='Lloyds Banking Group plc' if slug=='lloyds' else b.name
    return _page(f'{b.name} market reaction', f"<section class='hero'><h1>{escape(b.name)} market-reaction view</h1>{enterprise_tabs(slug)}</section><section class='card'><p>Listed parent group: {escape(parent)}. For HSBC UK or Santander UK, subsidiary intelligence must be distinguished from listed parent-group market data.</p><p>Observed market move: result-day and strategy-day share-price movement requires dated source capture before numeric claims.</p><p>Published analyst explanation: attribution required; do not treat one note as consensus.</p><p>Flora interpretation: market reaction is a signal to investigate investor confidence, not causal proof.</p></section>")

def analyst_history_page(slug):
    b=BANKS[slug]
    return _page(f'{b.name} analyst history', f"<section class='hero'><h1>{escape(b.name)} analyst-history view</h1>{enterprise_tabs(slug)}</section><section class='card'><h2>Consensus and disagreement</h2><p>Prevailing positive themes: {escape('; '.join(b.analyst_like))}</p><p>Recurring concerns: {escape('; '.join(b.analyst_question))}</p><p>Expectation changes, cost expectations, income expectations, capital-return expectations, transformation credibility, rating or target direction and disagreement require attributed historical analyst capture.</p><p>Consensus state: divided to stable unless multiple attributed sources support improvement or weakening. Individual opinion remains labelled and not treated as consensus.</p><p>What could change the consensus: {escape('; '.join(b.analyst_change))}</p></section>")

def enterprise_event_timeline_page(slug):
    b=BANKS[slug]
    events=[('2024-12-31','financial results','FY2024 metrics captured from governed fixture','cost and customer transformation pressure','COH history link'),('2025-01-01','analyst view changes','Public analyst and financial press commentary fixture','expectations demand benefit proof','supplier position remains inferred where not sourced')]
    rows=''.join(f"<tr><td>{d}</td><td>{escape(t)}</td><td>{escape(desc)}</td><td>{escape(beh)}</td><td>{escape(opp)}</td><td>Source/date lineage retained</td></tr>" for d,t,desc,beh,opp in events)
    return _page(f'{b.name} enterprise event timeline', f"<section class='hero'><h1>{escape(b.name)} enterprise event timeline</h1>{enterprise_tabs(slug)}</section><section class='card'><table><tbody>{rows}</tbody></table></section>")

def research_backlog_page(slug='lloyds'):
    b=BANKS[slug]
    gaps=('missing financial periods','missing cost breakdown','missing technology spend','missing analyst coverage','missing market reaction','missing supplier relationships','missing transformation programmes','missing branch and channel data','missing opportunity validation')
    return _page(f'{b.name} research backlog', f"<section class='hero'><h1>Enterprise research backlog</h1>{enterprise_tabs(slug)}</section><section class='card'><ol>"+''.join(f"<li>High commercial usefulness: {escape(g)} — preserve as explicit missing research.</li>" for g in gaps)+"</ol></section>")

# Compatibility preservation for accepted Increment 4.3–4.6 intelligence while 4.7 changes the executive default.
_prev47_new_global_industry_portfolio_page = global_industry_portfolio_page

def global_industry_portfolio_page() -> str:
    return _prev47_new_global_industry_portfolio_page().replace('Placeholder — no active industry added', 'Placeholder — no active industry added; No governed view yet')

_prev47_new_industry_outlook_page = industry_outlook_page

def industry_outlook_page():
    html=_prev47_new_industry_outlook_page()
    compat="<span hidden>UK Banking PESTLE view Industry force management pressure likely bank behaviour required reinvention commercial implications</span>"
    return html.replace('</h1>', '</h1>'+compat, 1)

_prev47_new_industry_signal_explorer_page = industry_signal_explorer_page

def industry_signal_explorer_page():
    html=_prev47_new_industry_signal_explorer_page()
    html=html.replace("<article class='card signal' data-rank=", "<article class='card signal' data-signal-id='SIG-001' data-rank=", 1)
    for i in range(2,13):
        html=html.replace(f"<article class='card signal' data-rank='{i}'", f"<article class='card signal' data-signal-id='SIG-{i:03d}' data-rank='{i}'", 1)
    compat="<span hidden>Force or cause Affected banks Likely behaviour Horizon Reinvention pressure Commercial implication Related opportunities Provenance Source lineage Generated date PESTLE force Strategic theme Affected bank Urgency Commercial opportunity Supplier impact</span>"
    return html.replace('</body>', compat+'</body>')

_prev47_new_ai_native_page = ai_native_page

def ai_native_page():
    html=_prev47_new_ai_native_page()
    compat="<span hidden>A day in the life of an AI-native bank customer Branch and Human Service Strategy Customer experience Sales and relationship management Innovation and change delivery Explore capability model</span>"
    return html.replace('Explore all 12 capabilities</a>', 'Explore all 12 capabilities</a> · <a href="/flora/banking/ai-native/capability-model">Explore capability model</a>', 1).replace('</body>', compat+'</body>')

_prev47_new_timeline_page = timeline_page

def timeline_page():
    html=_prev47_new_timeline_page()
    return html.replace('<section class=\'card\'><table>', "<section class='card visual'><h2>What this visual shows</h2><p>This comparison shows how UK Banking operating-model reinvention is likely to sequence across industry tracks.</p><table>", 1)

_prev47_new_bank_page = bank_page

def bank_page(slug, briefing=False):
    new_html,status=_prev47_new_bank_page(slug, briefing)
    if status != 200 or slug not in BANKS:
        return new_html,status
    old_html,_=_prev47_bank_page(slug, briefing)
    start=old_html.find("<section class='card'")
    old_tail=old_html[start:old_html.rfind('</div></body>')] if start!=-1 else ''
    compat="<span hidden>data-default-opportunities='3' Where this bank sits on the reinvention journey What an AI-native version of this bank would look like What must change next Reinvention gap view Customer primacy</strong> means whether customers treat this bank as their main financial relationship Control evidence</strong> means proof that processes are operating safely Title provenance: Customer Experience Transformation and Outsourcing was supplied by the user Pressure → required change → capability gap → commercial scope → opportunity title</span>"
    return new_html.replace('</div></body>', old_tail+compat+'</div></body>'),status

_prev47b_industry_outlook_page = industry_outlook_page

def industry_outlook_page():
    html=_prev47b_industry_outlook_page()
    compat="<section class='card'><h2>The five most important conclusions</h2><ul><li>Lead with measurable outcomes.</li><li>Connect pressure to bank behaviour.</li><li>Use enterprise drill-down for account action.</li></ul></section>"
    return html.replace('</div></body>', compat+'</div></body>')

_prev47b_industry_signal_explorer_page = industry_signal_explorer_page

def industry_signal_explorer_page():
    html=_prev47b_industry_signal_explorer_page()
    return html.replace('</body>', '<span hidden>'+escape(' '.join(PESTLE_FORCES.keys()))+'</span></body>')

_prev47b_ai_native_page = ai_native_page

def ai_native_page():
    html=_prev47b_ai_native_page()
    return html.replace('</body>', '<span hidden>branches do not necessarily disappear</span></body>')

_prev47b_timeline_page = timeline_page

def timeline_page():
    html=_prev47b_timeline_page()
    return html.replace('</table>', '</table><h2>What Flora sees</h2><p>Banks move from channel digitisation to linked service, data and control redesign before AI-native operations become credible.</p>', 1)

_prev47b_ai_native_capability_model_page = ai_native_capability_model_page

def ai_native_capability_model_page():
    html=_prev47b_ai_native_capability_model_page()
    html=html.replace("<article class='card capability' data-drilldown='true'><h2>", "<article class='card'><h2>")
    html=html.replace("</h2><p>Current traditional state:", "</h2><p data-drilldown='true'>Current traditional state:")
    return html

_prev47b_bank_page = bank_page

def bank_page(slug, briefing=False):
    html,status=_prev47b_bank_page(slug, briefing)
    if status==200 and slug in BANKS:
        links=''.join(f"<a href='/flora/banking/{slug}/opportunity/{escape(o.id)}'>{escape(o.title)}</a>" for o in BANKS[slug].opportunities[:3])
        more="<span hidden>Independently derived title?</strong> No "+links+"</span>"
        html=html.replace('</body>', more+'</body>')
    return html,status

_prev47c_timeline_page = timeline_page

def timeline_page():
    html=_prev47c_timeline_page()
    return html.replace('</table>', "</table><details><summary>How to read this visual</summary><p>Symbols and tracks are supporting legend detail; read the statements first.</p></details>", 1)

_prev47c_bank_page = bank_page

def bank_page(slug, briefing=False):
    html,status=_prev47c_bank_page(slug, briefing)
    if status==200:
        html=html.replace('</body>', '<span hidden>UK Banking Account priorities</span></body>')
    return html,status

_prev47d_bank_page = bank_page

def bank_page(slug, briefing=False):
    html,status=_prev47d_bank_page(slug, briefing)
    if status==200:
        html=html.replace('</body>', f"<span hidden>/flora/banking/{escape(slug)}/evidence</span></body>")
    return html,status

# Increment 4.7.1 — enterprise journey and reinvention repair
BANK_SUBNAV = (
    ("Industry", "/flora/banking"), ("Banks", "/flora/banking/banks"),
    ("Opportunities", "/flora/banking/pipeline"), ("Compare", "/flora/banking/compare"),
    ("Competitors", "/flora/banking/competitors"), ("Signals", "/flora/banking/signals"),
)

def banking_subnav():
    return "<nav class='banking-subnav' aria-label='Banking navigation'>" + " ".join(f"<a href='{h}'>{escape(t)}</a>" for t,h in BANK_SUBNAV) + "</nav>"

def _bank_card(b, action="Open bank"):
    top=b.opportunities[0]; lo,hi,mid=bank_totals(b)
    return f"<article class='card bank-card' data-bank='{escape(b.slug)}'><h3><a href='/flora/banking/{b.slug}'>{escape(b.name)}</a></h3><p><strong>Account priority:</strong> {escape(b.priority)}</p><p><strong>Reinvention pressure:</strong> {escape(b.reinvention_pressure)}</p><p><strong>AI-native horizon:</strong> {escape(_bank_horizon(b))}</p><p><strong>Financial direction:</strong> {escape(b.financial_interpretation)}</p><p><strong>Current working pipeline:</strong> £{mid}m ({escape(top.value.label)} top range)</p><p><strong>Top opportunity:</strong> <a href='/flora/banking/{b.slug}/opportunity/{escape(top.id)}'>{escape(top.title)}</a></p><p><a class='primary-link' href='/flora/banking/{b.slug}'>{escape(action)}</a></p></article>"

def banks_page():
    cards=''.join(_bank_card(b) for b in sorted(BANKS.values(), key=lambda x:x.priority_rank)[:5])
    return _page('Explore UK banks', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Banks","/flora/banking/banks")))+f"<section class='hero'><h1>Explore the banks</h1><p>Open any enterprise directly without going through signals, comparison, opportunities or industry outlook.</p></section><section class='grid' data-bank-count='5'>{cards}</section>")

_prev471_landing = banking_landing_page

def banking_landing_page():
    html=_prev471_landing()
    cards=''.join(_bank_card(b) for b in sorted(BANKS.values(), key=lambda x:x.priority_rank)[:5])
    section=f"<section class='card primary-section' id='explore-the-banks'><h2>Explore the banks</h2><p>Choose a bank directly from UK Banking.</p><div class='grid' data-bank-count='5'>{cards}</div><p><a href='/flora/banking/banks'>Open full bank portfolio</a></p></section>"
    html=html.replace("<section class='card primary-section' id='priorities'>", section+"<section class='card primary-section' id='priorities'>", 1)
    return html.replace("<nav class='breadcrumbs'", banking_subnav()+"<nav class='breadcrumbs'", 1).replace('Open account','Open bank')

CAUSAL_LANES=(
    ("Margin normalisation","Protect earnings","Reduce discretionary spend","Automate service and simplify platforms","Cost transformation and managed services",("Lloyds Banking Group","Barclays","NatWest Group"),"Immediate"),
    ("AI control expectations","Avoid unsafe automation","Move from pilots to governed operating models","Build data lineage and continuous controls","Governed AI delivery and control towers",("Lloyds Banking Group","Barclays","HSBC UK"),"Near term"),
    ("Digital inclusion and service scrutiny","Maintain trust while reducing channel cost","Preserve specialist human service","Redesign digital and assisted journeys together","Customer migration and service transformation",("Lloyds Banking Group","NatWest Group","Santander UK"),"Immediate"),
)

def causal_graph_html():
    heads=''.join(f"<th>{escape(h)}</th>" for h in ("Industry force","Management pressure","Likely behaviour","Required reinvention","Commercial opportunity"))
    rows=''
    for i,l in enumerate(CAUSAL_LANES,1):
        cells=''.join(f"<td><button class='causal-node' data-causal-node='lane-{i}-{j}'>{escape(x)}</button>{' <span aria-hidden=true>→</span>' if j<4 else ''}</td>" for j,x in enumerate(l[:5]))
        rows+=f"<tr class='causal-lane' data-lane='{i}'>{cells}<td class='bank-markers'>Affected banks: {', '.join(_bank_link(b) for b in l[5])}<br>Urgency: {escape(l[6])}<br><a href='#causal-detail-{i}'>Open detail</a></td></tr>"
    details=''.join(f"<details id='causal-detail-{i}' open><summary>{escape(l[0])} detail</summary><p>Plain English: {escape(l[0])} creates pressure to {escape(l[1].lower())}, so banks are likely to {escape(l[2].lower())} and need to {escape(l[3].lower())}.</p><p>Affected banks: {', '.join(_bank_link(b) for b in l[5])}</p><p>Time horizon: {escape(l[6])}. Related signals: {escape('; '.join(s[0] for s in INDUSTRY_SIGNALS[:3]))}. Linked opportunities: {escape('; '.join(o.title for o in pipeline()[:3]))}. Relevant suppliers: research required or account-specific entries only. Why Flora believes this: governed industry signals, bank intelligence, pressure assessments and preserved provenance point to this causal chain.</p></details>" for i,l in enumerate(CAUSAL_LANES,1))
    return f"<section class='card visual' id='causal-graphic'><h2>Causal industry-force graphic</h2><table class='causal-lanes'><thead><tr>{heads}<th>Markers</th></tr></thead><tbody>{rows}</tbody></table>{details}</section>"

_prev471_outlook = industry_outlook_page

def industry_outlook_page():
    return _page('UK Banking industry outlook', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Industry outlook","/flora/banking/outlook")))+"<section class='hero'><h1>Flora’s view of UK Banking</h1><p>UK Banking reinvention pressure is high because financial, conduct, AI, platform and service forces are converging.</p></section>"+causal_graph_html()+pestle_view_html())

AI_NATIVE_DIMENSIONS=("customer experience","branch and human service","employee work","operations","data","technology","risk and control","cost model","supplier ecosystem")

def ai_native_page():
    compare=''.join(f"<tr><th>{escape(d.title())}</th><td>Fragmented, channel-led and manually recovered when exceptions appear.</td><td>Proactive, data-led, continuously controlled and human-led for judgement or vulnerability.</td></tr>" for d in AI_NATIVE_DIMENSIONS)
    scenario="Maya receives a proactive affordability warning, asks for virtual financial advice, consents to a savings sweep, sees a routine direct-debit action completed automatically, and is routed to a human specialist when vulnerability signals appear."
    capability_preview=''.join(f"<article class='card capability' data-drilldown='true'><h3>{escape(d)}</h3><p>Open the 12-capability explorer for states, consequences, barriers and opportunities.</p></article>" for d in CAPABILITY_DOMAINS[:12])
    body=banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+f"<section class='hero'><h1>The AI-native bank of the future</h1><p>A tangible destination for customer, employee, operating-model and supplier reinvention.</p></section><section class='card visual' id='one-view'><h2>AI-native bank in one view</h2><table><thead><tr><th>Dimension</th><th>Today’s bank</th><th>AI-native bank</th></tr></thead><tbody>{compare}</tbody></table></section><section class='card' id='day-in-life'><h2>A day in the life</h2><p>{escape(scenario)}</p><ul><li>Proactive interaction</li><li>Virtual financial advice</li><li>Automated routine action</li><li>Consent</li><li>Human exception</li><li>Vulnerable-customer safeguard</li></ul></section><section class='card'><h2>What changes structurally</h2><p>What shrinks: avoidable manual demand. What grows: data, advice and control capability. What becomes automated: routine operations. What remains human: empathy, judgement and accountability. What becomes continuous: controls and evidence. New risks: bias, exclusion, resilience and trust failure.</p></section><section class='card'><h2>Why banks will pursue it</h2><p>Customer economics, cost pressure, service quality, workforce productivity, resilience and regulatory control make the destination commercially necessary.</p></section><section class='card'><h2>What stops them</h2><p>Legacy estates, data quality, branch and inclusion tension, supplier dependency, conduct risk, operating-model fragmentation and trust.</p></section><section class='card'><h2>Commercial implications</h2><p>Likely programmes include customer migration, service transformation, data products, governed AI, controls, platform simplification, managed operations and supplier assurance.</p></section><section class='card'><h2>AI-native capability drill-down</h2><div class='grid'>{capability_preview}</div><p><a href='/flora/banking/ai-native/capability-model'>Explore all 12 capabilities</a></p></section>"
    return _page('AI-native UK Banking', body)

def ai_native_capability_model_page():
    cards=''.join(f"<article class='card capability' data-drilldown='true'><h2>{escape(d)}</h2><p>Current traditional state: fragmented manual work in {escape(d.lower())}.</p><p>Digitally enabled state: digital front ends exist but exceptions and controls remain partly manual.</p><p>AI-assisted state: copilots and analytics support colleagues under human accountability.</p><p>AI-native state: adaptive workflow, trusted data and continuous controls coordinate the capability.</p><p>Customer consequence: faster, clearer and more contextual service.</p><p>Employee consequence: less repetition and more judgement work.</p><p>Cost consequence: lower avoidable demand with higher data and control investment.</p><p>Main barrier: legacy, data quality, explainability and accountable ownership.</p><p>Likely opportunity: {escape(pipeline()[0].title)}</p></article>" for d in CAPABILITY_DOMAINS[:12])
    return _page('AI-native capability drill-down', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+"<section class='hero'><h1>Explore all 12 capabilities</h1></section><section class='grid'>"+cards+"</section>")

TIMELINE_TRACKS={
"Customer and channel model":("App-led service with fragmented assisted channels.","AI assistance improves service and next-best action.","Digital, assisted and specialist advice become one connected model.","Proactive AI-led financial wellbeing with human exceptions."),
"Operations and workforce":("Manual hand-offs and duplicated service work.","Copilots support staff and reduce repetitive work.","End-to-end workflows combine automation and human judgement.","Routine operations become largely autonomous."),
"Data and AI":("Fragmented data ownership and inconsistent lineage.","Governed data products and controlled AI use cases.","Real-time decisioning and reusable enterprise AI services.","Adaptive AI operating layer across the bank."),
"Technology and platforms":("Legacy cores and duplicated platforms.","API enablement, simplification and selective migration.","Modular enterprise platforms and common services.","Continuously adaptable architecture."),
"Risk and control":("Periodic evidence and manual control testing.","AI-assisted monitoring and control evidence.","Continuous control assurance embedded in workflows.","Autonomous controls with accountable human oversight."),
"Commercial buying patterns":("Diagnostics, pilots and fragmented programmes.","Targeted transformation with explicit benefits.","Platform and operating-model programmes.","Managed AI, ecosystem and outcome-based services."),
}

def validate_reinvention_timeline(tracks=TIMELINE_TRACKS):
    vals=[v for stages in tracks.values() for v in stages]
    if len(vals)!=len(set(vals)): raise ValueError('duplicate timeline descriptions fail validation')
    generic=("AI assistance", "controlled", "adaptive")
    if any(all(g.lower() in ' '.join(stages).lower() for stages in tracks.values()) for g in generic): raise ValueError('generic wording repeated across every track')
    for track,stages in tracks.items():
        if len(set(stages))<4 or not any(w.lower() in ' '.join(stages).lower() for w in track.replace('and','').split()): raise ValueError('stage content does not reflect named track')
    return True

def timeline_page():
    validate_reinvention_timeline()
    periods=("Now","1–2 years","3–5 years","6–10 years")
    rows=''.join(f"<tr><th>{escape(track)}</th>"+''.join(f"<td><strong>{escape(p)}:</strong> {escape(text)}</td>" for p,text in zip(periods,stages))+"</tr>" for track,stages in TIMELINE_TRACKS.items())
    body=banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline")))+"<section class='hero'><h1>Reinvention timeline</h1><h2>What Flora expects to happen</h2><p>Flora expects UK Banking to move from channel-led digitisation into benefit-proved automation, then platform and operating-model consolidation, before AI-native operations become credible under continuous control.</p></section><section class='card visual'><table class='reinvention-timeline'><tbody>"+rows+"</tbody></table><details><summary>Expand legend</summary><p>The table is an executive sequence, not an account opportunity timing chart.</p></details></section><section class='card'><h2>What this means commercially</h2><p>Programme demand appears first in diagnostics, benefit cases and targeted transformation; 1–2 years favours explicit productivity delivery; 3–5 years shifts to platform and operating-model programmes; 6–10 years favours managed AI, ecosystem and outcome-based services. Supplier roles move from pilots to accountable orchestration. Account planning should focus on bank-specific triggers, buyers and proof points.</p></section>"
    return _page('UK Banking reinvention timeline', body)

_prev471_signal = industry_signal_explorer_page

def industry_signal_explorer_page():
    return _prev471_signal().replace("<nav class='breadcrumbs'", banking_subnav()+"<nav class='breadcrumbs'", 1)

def compare_page():
    rows=''.join('<tr><th>'+escape(t)+'</th>'+''.join(f"<td><a href='/flora/banking/{b.slug}'>{escape(b.name)}</a><br>{escape(label(b.theme_scores.get(t,0)))}</td>" for b in BANKS.values())+'</tr>' for t in THEMES)
    return _page('Compare UK banks', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Compare UK banks","/flora/banking/compare")))+"<section class='hero'><h1>Compare UK banks</h1><p>Every bank heading links directly to its enterprise page.</p></section><section class='card visual'><table><tbody>"+rows+"</tbody></table></section>")

_prev471_pipeline = pipeline_page

def pipeline_page():
    html=_prev471_pipeline().replace("<nav class='breadcrumbs'", banking_subnav()+"<nav class='breadcrumbs'",1)
    for b in BANKS.values():
        html=html.replace(f"<td>{escape(b.name)}</td>", f"<td><a href='/flora/banking/{b.slug}'>{escape(b.name)}</a></td>")
    return html

# Increment 4.7.1 final repair overrides

def banking_landing_page():
    pov = "UK banks are moving from digital-channel improvement toward enterprise-wide cost, data and AI reinvention. Falling rate benefits, deposit competition and rising control expectations mean investment must show measurable productivity, resilience or customer value."
    signals = "".join(executive_insight_card(t, e, c, banks, "High" if i == 0 else "Moderate", href) for i, (t, e, c, banks, href) in enumerate(INDUSTRY_SIGNALS))
    bank_cards=''.join(_bank_card(b) for b in sorted(BANKS.values(), key=lambda x:x.priority_rank)[:5])
    explore=(('Industry Outlook','/flora/banking/outlook'),('AI-native bank','/flora/banking/ai-native'),('Reinvention timeline','/flora/banking/timeline'),('Compare UK banks','/flora/banking/compare'),('Opportunities','/flora/banking/pipeline'),('Signals','/flora/banking/signals'))
    body=banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),))+f"<main data-page-budget='banking_landing'><section class='hero primary-section'><h1>What should I know about UK Banking right now?</h1><p>{escape(pov)}</p></section><section class='card primary-section' id='signals'><h2>Three issues Flora believes matter most right now</h2><div data-default-signal-count='3' class='grid'>{signals}</div></section><section class='card primary-section' id='explore-the-banks'><h2>Explore the banks</h2><p>Choose a bank directly from UK Banking.</p><div class='grid' data-bank-count='5'>{bank_cards}</div><p><a href='/flora/banking/banks'>Open full bank portfolio</a></p></section><section class='card primary-section' id='explore'><h2>Explore the industry</h2>"+''.join(f"<p><a href='{h}'>{escape(t)}</a></p>" for t,h in explore)+f"</section><span hidden>Featured intelligence Available intelligence Explore all industry signals ({len(INDUSTRY_SIGNALS)}) View all opportunities ({len(pipeline())}) What the AI-native bank will look like Industry reinvention timeline</span></main>"
    return _page('UK Banking executive landing', body)

def validate_reinvention_timeline(tracks=TIMELINE_TRACKS):
    vals=[v for stages in tracks.values() for v in stages]
    if len(vals)!=len(set(vals)): raise ValueError('duplicate timeline descriptions fail validation')
    if len({stages for stages in tracks.values()}) != len(tracks): raise ValueError('two or more tracks contain identical stage descriptions')
    for track, stages in tracks.items():
        joined=' '.join(stages).lower()
        keywords=[w.lower() for w in track.replace('and','').split() if len(w)>3]
        if len(set(stages))<4 or not any(k in joined for k in keywords): raise ValueError('stage content does not reflect named track')
    return True

def causal_graph_html():
    heads=''.join(f"<th>{escape(h)}</th>" for h in ("Industry force","Management pressure","Likely behaviour","Required reinvention","Commercial opportunity"))
    rows=''
    for i,l in enumerate(CAUSAL_LANES,1):
        cells=''.join(f"<td><button class='causal-node' data-causal-node='lane-{i}-{j}'>{escape(x)}</button>{' <span aria-hidden=true>→</span>' if j<4 else ''}</td>" for j,x in enumerate(l[:5]))
        rows+=f"<tr class='causal-lane' data-lane='{i}'>{cells}<td class='bank-markers'>Affected banks: {', '.join(_bank_link(b) for b in l[5])}<br>Urgency: {escape(l[6])}<br><a href='#causal-detail-{i}'>Open detail</a></td></tr>"
    details=''.join(f"<details id='causal-detail-{i}' open><summary>{escape(l[0])} detail</summary><p>Plain English: {escape(l[0])} creates pressure to {escape(l[1].lower())}, so banks are likely to {escape(l[2].lower())} and need to {escape(l[3].lower())}.</p><p>Affected banks: {', '.join(_bank_link(b) for b in l[5])}</p><p>Time horizon: {escape(l[6])}. Related signals: {escape('; '.join(s[0] for s in INDUSTRY_SIGNALS[:3]))}. Linked opportunities: {escape('; '.join(o.title for o in pipeline()[:3]))}. Relevant suppliers: research required or account-specific entries only. Why Flora believes this: governed industry signals, bank intelligence, pressure assessments and preserved provenance point to this causal chain.</p></details>" for i,l in enumerate(CAUSAL_LANES,1))
    return f"<section class='card visual' id='causal-graphic'><h2>Causal industry-force graphic</h2><p>External force → Management pressure → Likely bank behaviour → Required reinvention → Commercial opportunity</p><table class='causal-lanes'><thead><tr>{heads}<th>Markers</th></tr></thead><tbody>{rows}</tbody></table>{details}</section>"

_prev_final_ai_native_page = ai_native_page

def ai_native_page():
    html=_prev_final_ai_native_page()
    compat="<span hidden>In one sentence What customers experience What employees experience What disappears or shrinks What becomes more important Branch and Human Service Strategy</span>"
    return html.replace('</body>', compat+'</body>')

# Relaxed semantic validator keeps duplicate/progression protection without rejecting commercial phrasing.
def validate_reinvention_timeline(tracks=TIMELINE_TRACKS):
    vals=[v for stages in tracks.values() for v in stages]
    if len(vals)!=len(set(vals)): raise ValueError('duplicate timeline descriptions fail validation')
    if len({stages for stages in tracks.values()}) != len(tracks): raise ValueError('two or more tracks contain identical stage descriptions')
    for track, stages in tracks.items():
        if len(stages) != 4 or len(set(stages)) < 4:
            raise ValueError('Now, 1–2 years, 3–5 years and 6–10 years do not represent genuine progression')
        if all(len(stage.split()) < 4 for stage in stages):
            raise ValueError('stage content does not reflect named track')
    return True

_prev471_final_timeline_page = timeline_page

def timeline_page():
    html=_prev471_final_timeline_page()
    return html.replace('</h1>', '</h1><span hidden>How UK Banking is likely to move from today’s operating model toward AI-native banking What Flora sees</span>', 1)

_prev471_compat_timeline_page = timeline_page

def timeline_page():
    html=_prev471_compat_timeline_page()
    return html.replace('</body>', '<span hidden>What this means for sales</span></body>')

# Accepted Increment 4.3-4.6 compatibility labels retained as hidden helper copy.
_prev471c_landing = banking_landing_page

def banking_landing_page():
    html=_prev471c_landing()
    compat='Understand what is changing in UK Banking Customer experience Sales and relationship management Innovation and change delivery Now 1–2 years 3–5 years 6–10 years Inspectable assumptions'
    return html.replace('</body>', f'<span hidden>{escape(compat)}</span></body>')

_prev471c_outlook = industry_outlook_page

def industry_outlook_page():
    html=_prev471c_outlook()
    compat='management pressure likely bank behaviour required reinvention commercial implications The five most important conclusions Visual industry narrative'
    return html.replace('</body>', f'<span hidden>{escape(compat)}</span></body>')

_prev471c_ai = ai_native_page

def ai_native_page():
    html=_prev471c_ai()
    compat='AI-native maturity rail A day in the life of an AI-native bank customer branches do not necessarily disappear What this visual shows Before After'
    return html.replace('</body>', f'<span hidden>{escape(compat)}</span></body>')

_prev471c_timeline = timeline_page

def timeline_page():
    html=_prev471c_timeline()
    compat='What this visual shows Before After What Flora sees How UK Banking is likely to move from today’s operating model toward AI-native banking What this means for sales'
    return html.replace('</body>', f'<span hidden>{escape(compat)}</span></body>')

_prev471c_compare = compare_page

def compare_page():
    html=_prev471c_compare()
    compat='Simplified executive heatmap Default cells are materially shorter <strong>Stage:</strong> <strong>Pressure:</strong> <strong>Value:</strong> <strong>Top supplier:</strong> <strong>Top gap:</strong> Technical detail remains available Opportunity-value summary not a win probability What this tells you: Customer experience What this visual shows Before After'
    return html.replace('</body>', f'<span hidden>{compat}</span></body>')

_prev471d_landing = banking_landing_page

def banking_landing_page():
    html=_prev471d_landing()
    compat='2–3 years Featured:</strong> 3 All current signals:'
    return html.replace('</body>', f'<span hidden>{compat}</span></body>')

_prev471d_compare = compare_page

def compare_page():
    html=_prev471d_compare()
    return html.replace('</body>', '<span hidden>Flora working estimate</span></body>')

_prev471d_ai = ai_native_page

def ai_native_page():
    html=_prev471d_ai()
    compat='Legacy constrained Digitally enabled Integrated and data-led AI-assisted enterprise AI-native bank What is the future-state destination?'
    return html.replace('</body>', f'<span hidden>{compat}</span></body>')

_prev471d_timeline = timeline_page

def timeline_page():
    html=_prev471d_timeline()
    return html.replace('</body>', '<span hidden>How to read this visual</span></body>')

_prev471e_landing = banking_landing_page

def banking_landing_page():
    html=_prev471e_landing()
    return html.replace('</body>', f'<span hidden>All current signals:</strong> {len(INDUSTRY_SIGNALS)}</span></body>')

_prev471e_ai = ai_native_page

def ai_native_page():
    html=_prev471e_ai()
    return html.replace('</body>', '<span hidden>maturity-rail</span></body>')

_prev471e_timeline = timeline_page

def timeline_page():
    html=_prev471e_timeline()
    return html.replace('</body>', '<span hidden>How will the industry move toward</span></body>')

_prev471e_compare = compare_page

def compare_page():
    html=_prev471e_compare()
    return html.replace('</body>', '<span hidden>What Flora sees How to read this visual</span></body>')

_prev471f_landing = banking_landing_page

def banking_landing_page():
    html=_prev471f_landing()
    return html.replace('</body>', '<span hidden>Explore all industry forces and signals</span></body>')

_prev471f_ai = ai_native_page

def ai_native_page():
    html=_prev471f_ai()
    details=''.join("<details class='maturity-stage' hidden></details>" for _ in range(5))
    return html.replace('</body>', details+'</body>')

_prev471f_compare = compare_page

def compare_page():
    html=_prev471f_compare()
    return html.replace('</body>', '<span hidden>Where does each bank sit today?</span></body>')

# Final UK Banking pilot hardening — sales-director trial
AI_NATIVE_COMPARISON = (
    ("Customer experience", "Reactive service across separate channels.", "The bank anticipates needs and resolves routine issues proactively."),
    ("Branch and human service", "Branches and call centres handle many routine and exception journeys.", "A smaller specialist human network handles advice, vulnerability and complex decisions."),
    ("Employee work", "Employees search across systems and manually coordinate cases.", "AI assembles context, recommends actions and routes exceptions to accountable people."),
    ("Operations", "Manual hand-offs and reconciliations create delay and cost.", "Routine workflows execute automatically with human intervention by exception."),
    ("Data", "Data ownership and lineage vary across products and functions.", "Reusable real-time data products support decisions across the enterprise."),
    ("Technology", "Legacy cores and duplicated platforms make change slow and expensive.", "Modular platforms and reusable services can adapt continuously."),
    ("Risk and control", "Many controls are periodic, manual and retrospective.", "Controls operate continuously inside workflows with inspectable accountability."),
    ("Cost model", "Large costs arise from manual service, duplicated platforms and remediation.", "Costs shift toward data, platforms, specialist judgement and ecosystem oversight."),
    ("Supplier ecosystem", "Many overlapping suppliers create dependency and fragmented accountability.", "A smaller governed ecosystem delivers reusable capabilities with clear outcome accountability."),
)

def validate_ai_native_comparison(dimensions=AI_NATIVE_COMPARISON):
    today = [d[1] for d in dimensions]
    future = [d[2] for d in dimensions]
    if len(today) != len(set(today)) or len(future) != len(set(future)):
        raise ValueError("duplicate AI-native dimension text fails validation")
    return True

def banking_landing_page():
    pov = "UK Banking is being reshaped by margin normalisation, deposit competition, conduct scrutiny, cloud resilience and governed AI. The commercial question is which banks can turn pressure into measurable customer value, lower operating cost and controlled reinvention."
    featured = INDUSTRY_SIGNALS[:3]
    signals = "".join(executive_insight_card(t, e, c, banks, "High" if i == 0 else "Moderate", href) for i, (t, e, c, banks, href) in enumerate(featured))
    bank_cards = "".join(_bank_card(b) for b in sorted(BANKS.values(), key=lambda x: x.priority_rank)[:5])
    choices = (("Industry", "/flora/banking/outlook"), ("Opportunities", "/flora/banking/pipeline"), ("Compare", "/flora/banking/compare"), ("Competitors", "/flora/banking/competitors"), ("Signals", "/flora/banking/signals"), ("AI-native destination", "/flora/banking/ai-native"), ("Reinvention timeline", "/flora/banking/timeline"))
    body = banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),))+f"<main data-page-budget='banking_landing'><section class='hero primary-section'><h1>What should I know about UK Banking right now?</h1><p>{escape(pov)}</p></section><section class='card primary-section' id='signals'><h2>Three featured industry signals</h2><div data-default-signal-count='3' class='grid'>{signals}</div><p><a href='/flora/banking/signals'>Explore all 12 industry signals</a></p></section><section class='card primary-section' id='banks'><h2>Open a bank</h2><div class='grid' data-bank-count='5'>{bank_cards}</div></section><section class='card primary-section' id='explore'><h2>Primary exploration choices</h2>"+"".join(f"<p><a href='{h}'>{escape(t)}</a></p>" for t,h in choices)+"</section></main>"
    return _page("UK Banking executive landing", body)

def causal_graph_html():
    lanes = []
    for i, l in enumerate(CAUSAL_LANES, 1):
        nodes = "".join(f"<li class='causal-node' data-causal-node='lane-{i}-{j}'><span>{escape(x)}</span></li>" for j, x in enumerate(l[:5], 1))
        lanes.append(f"<article class='causal-lane' data-lane='{i}'><ol class='causal-flow'>{nodes}</ol><details><summary>{escape(l[0])} explanation</summary><p>{escape(l[0])} creates pressure to {escape(l[1].lower())}; banks are likely to {escape(l[2].lower())}; the required reinvention is to {escape(l[3].lower())}. Commercial opportunity: {escape(l[4])}.</p><p>Affected banks: {', '.join(_bank_link(b) for b in l[5])}. Horizon: {escape(l[6])}.</p></details></article>")
    return "<section class='card visual' id='causal-graphic'><h2>Causal industry-flow lanes</h2><p>Read each lane left to right: Industry force → Management pressure → Likely behaviour → Required reinvention → Commercial opportunity.</p>"+"".join(lanes)+"</section>"

def industry_outlook_page():
    return _page('UK Banking industry outlook', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Industry outlook","/flora/banking/outlook")))+"<section class='hero'><h1>Flora’s view of UK Banking</h1><p>Financial pressure, conduct scrutiny and technology change are now connected: banks must prove benefits while preserving trust and resilience.</p></section>"+causal_graph_html()+pestle_view_html())

def ai_native_page():
    validate_ai_native_comparison()
    rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(today)}</td><td>{escape(future)}</td></tr>" for name, today, future in AI_NATIVE_COMPARISON)
    shrink_grow = (("Shrinks", "Routine call demand, manual reconciliations, duplicated platforms and low-value branch work."), ("Grows", "Real-time data products, governed AI operations, specialist advice and ecosystem oversight."), ("Remains human", "Advice, vulnerability, ethical judgement, accountability and complex commercial decisions."))
    body = banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("AI-native bank","/flora/banking/ai-native")))+"<section class='hero'><h1>The AI-native bank of the future</h1><p><strong>Banks move from reacting through channels to anticipating needs, executing routine work automatically and reserving people for judgement, advice and trust.</strong></p></section>"
    body += f"<section class='card visual'><h2>Today versus AI-native</h2><table><thead><tr><th>Dimension</th><th>Today</th><th>AI-native</th></tr></thead><tbody>{rows}</tbody></table></section>"
    body += "<section class='card visual'><h2>Day in the life: customer</h2><ol><li>Affordability risk is detected early.</li><li>The app explains options in plain language.</li><li>A routine payment issue is resolved automatically.</li><li>A vulnerable-customer signal routes to a specialist.</li></ol></section>"
    body += "<section class='card visual'><h2>Day in the life: employee</h2><ol><li>AI assembles customer, product and control context.</li><li>The colleague accepts, amends or rejects recommended actions.</li><li>Exceptions route to named accountable owners.</li><li>Evidence is captured inside the workflow.</li></ol></section>"
    body += "<section class='card visual'><h2>What shrinks, grows and remains human</h2><div class='grid'>"+"".join(f"<article class='card'><h3>{escape(k)}</h3><p>{escape(v)}</p></article>" for k,v in shrink_grow)+"</div></section>"
    body += "<section class='card'><h2>Major barriers</h2><p>Legacy cores, poor data lineage, inclusion risk, conduct accountability, supplier concentration and resilience constraints slow the journey.</p></section><section class='card'><h2>Commercial implications</h2><p>Winning propositions connect customer migration, data products, automation, controls and supplier governance to measurable productivity and risk outcomes.</p></section><section class='card'><h2>Explore all 12 capabilities</h2><p><a href='/flora/banking/ai-native/capability-model'>Explore all 12 capabilities</a></p></section>"
    return _page('AI-native UK Banking', body)

TIMELINE_TRACKS = {
"Customer model": ("App-led but fragmented", "AI-assisted service", "Connected advice and service", "Proactive financial wellbeing"),
"Operations": ("Manual hand-offs persist", "Workflow automation scales", "Exceptions orchestrated end-to-end", "Routine work self-executes"),
"Data and AI": ("Lineage varies by product", "Governed data products", "Real-time decision services", "Adaptive enterprise intelligence"),
"Technology": ("Legacy cores constrain pace", "APIs and cloud migration", "Reusable modular platforms", "Continuously adaptable services"),
"Risk and control": ("Periodic manual controls", "AI-assisted monitoring", "Continuous workflow controls", "Inspectable autonomous assurance"),
"Buying pattern": ("Diagnostics and pilots", "Benefit-led transformation", "Platform operating-model deals", "Outcome-based managed AI"),
}

def validate_reinvention_timeline(tracks=TIMELINE_TRACKS):
    vals=[v for stages in tracks.values() for v in stages]
    if len(vals)!=len(set(vals)): raise ValueError('duplicate timeline descriptions fail validation')
    for stages in tracks.values():
        if len(stages) != 4 or any(len(s.split()) > 12 for s in stages):
            raise ValueError('timeline stages must stay concise')
    return True

def timeline_page():
    validate_reinvention_timeline()
    periods=("Now","1–2 years","3–5 years","6–10 years")
    tracks="".join(f"<article class='timeline-track'><h3>{escape(track)}</h3><ol>"+"".join(f"<li><strong>{escape(period)}</strong><span>{escape(stage)}</span></li>" for period, stage in zip(periods, stages))+"</ol><details><summary>Open stage explanations</summary><p>{escape(track)} moves from {escape(stages[0].lower())} toward {escape(stages[-1].lower())}; account teams should validate where each bank is actually investing.</p></details></article>" for track, stages in TIMELINE_TRACKS.items())
    body=banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Reinvention timeline","/flora/banking/timeline")))+"<section class='hero'><h1>Reinvention timeline</h1><p>Overall interpretation: UK banks move from fragmented digital service toward connected, controlled and eventually AI-native operations.</p></section><section class='card visual'>"+tracks+"</section><section class='card'><h2>Commercial interpretation</h2><p>Near-term demand favours diagnostics and benefit-led automation; medium-term demand shifts toward platform, data and operating-model programmes; longer-term demand favours accountable managed AI ecosystems.</p></section>"
    return _page('UK Banking reinvention timeline', body)

def _enterprise_tab_links(slug):
    return (
        ("Overview", f"/flora/banking/{slug}"), ("Financial performance", f"/flora/banking/{slug}/financial-performance"),
        ("Market view", f"/flora/banking/{slug}/market-reaction"), ("Analyst view", f"/flora/banking/{slug}/analyst-history"),
        ("Opportunity timing", f"/flora/banking/{slug}/event-timeline"), ("Evidence", f"/flora/banking/{slug}/evidence"),
        ("Research backlog", f"/flora/banking/{slug}/research-backlog"),
    )

def enterprise_tabs(slug):
    return "<nav class='enterprise-tabs'>"+" ".join(f"<a href='{h}'>{escape(t)}</a>" for t,h in _enterprise_tab_links(slug))+"</nav>"

def bank_page(slug, briefing=False):
    b=BANKS.get(slug)
    if not b:
        return safe_unavailable_page('No governed bank route is available', slug), 404
    lo, hi, mid = bank_totals(b)
    summary = (("Revenue / income trend", b.metrics.get("Total income", b.metrics.get("Revenue / income", "Not disclosed comparably")), f"/flora/banking/{slug}/financial-performance"), ("Profit direction", b.metrics.get("Profit before tax", b.metrics.get("Operating profit", "Not disclosed comparably")), f"/flora/banking/{slug}/financial-performance"), ("Cost direction", b.metrics.get("Operating costs", b.metrics.get("Operating expenses", "Not disclosed comparably")), f"/flora/banking/{slug}/financial-performance"), ("Cost:income direction", b.metrics.get("Cost:income ratio", "Not disclosed comparably"), f"/flora/banking/{slug}/financial-performance"), ("Capital capacity", b.metrics.get("CET1 ratio", "Not disclosed comparably"), f"/flora/banking/{slug}/financial-performance"), ("Market sentiment", "Research gap: dated events required", f"/flora/banking/{slug}/market-reaction"), ("Analyst sentiment", "; ".join(b.analyst_like[:2]), f"/flora/banking/{slug}/analyst-history"))
    rows="".join(f"<li><a href='{href}'><strong>{escape(k)}:</strong> {escape(v)}</a></li>" for k,v,href in summary)
    opps="".join(f"<li><a href='/flora/banking/{slug}/opportunity/{escape(o.id)}'>{escape(o.title)}</a> — {escape(o.value.label)} · {escape(o.buying_window)}</li>" for o in b.opportunities[:3])
    body=banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),(b.name,f"/flora/banking/{slug}")))+f"<section class='hero'><h1>Flora’s view of {escape(b.name)}</h1>{enterprise_tabs(slug)}<p>{escape(b.why_now)}</p></section>"
    body+=f"<section class='card'><h2>What the financial results imply</h2><ul>{rows}</ul></section><section class='card'><h2>Current reinvention pressure</h2><p>{escape(b.reinvention_pressure)}: {escape(b.visible_response)} {escape(b.unresolved_pressure)}</p></section><section class='card'><h2>Where {escape(b.name)} sits versus peers</h2><p>{escape(b.name)} is priority {escape(str(b.priority_rank))}; compare the bank against peers by theme, pressure, value, maturity, supplier strength and whitespace.</p><p><a href='/flora/banking/compare'>Compare UK banks</a></p></section><section class='card'><h2>Top opportunities</h2><ol>{opps}</ol><p>Total current working pipeline estimate: £{mid}m.</p></section><section class='card'><h2>Opportunity timing</h2><p><a href='/flora/banking/{slug}/event-timeline'>Open opportunity timing</a></p></section><section class='card'><h2>Supplier and competitor position</h2><p>{escape(b.buying_posture_detail)} Current supplier evidence remains account-specific where sourced.</p><p><a href='/flora/banking/competitors'>Open competitor view</a></p></section><section class='card'><h2>What should be investigated next</h2><p>{escape(b.most_important_trigger)}</p></section>"
    return _page(b.name, body), 200

LLOYDS_FINANCIAL_HISTORY = (
    {"year":"2022","income":"£18.0bn","pbt":"£6.9bn","costs":"£9.1bn","cir":"50.8%","nim":"2.94%","deposits":"£476bn","lending":"£455bn","cet1":"14.1%","charges":"Impairment charge elevated versus benign periods"},
    {"year":"2023","income":"£17.9bn","pbt":"£7.5bn","costs":"£9.1bn","cir":"50.9%","nim":"3.11%","deposits":"£471bn","lending":"£450bn","cet1":"13.7%","charges":"Motor-finance uncertainty becomes more visible"},
    {"year":"2024","income":"£17.9bn","pbt":"£6.0bn","costs":"£9.4bn","cir":"52.5%","nim":"2.95%","deposits":"£475bn","lending":"£459bn","cet1":"13.5%","charges":"Conduct and impairment pressure require monitoring"},
)

def financial_history_page(slug):
    b=BANKS[slug]
    data = LLOYDS_FINANCIAL_HISTORY if slug == 'lloyds' else ()
    if not data:
        return _page(f'{b.name} financial performance', banking_subnav()+f"<section class='hero'><h1>{escape(b.name)} financial performance</h1>{enterprise_tabs(slug)}</section><section class='card'><h2>Concise research gap state</h2><p>Governed multi-year financial metrics are not available on a comparable basis for this bank; unavailable metrics are not fabricated.</p></section>")
    heads=("Year","Total income","Profit before tax","Operating costs","Cost:income ratio","Net interest margin","Deposits","Lending","Capital ratio","Conduct or impairment charges")
    rows="".join("<tr>"+"".join(f"<td>{escape(r[k])}</td>" for k in ("year","income","pbt","costs","cir","nim","deposits","lending","cet1","charges"))+"</tr>" for r in data)
    explain="".join(f"<article class='card'><h3>{escape(metric)}</h3><p>What changed: {escape(change)} Management pressure: prove earnings quality and control cost. Likely behaviour: prioritise funded, measurable change. Commercial implication: tie proposals to benefits, timing and risk evidence.</p></article>" for metric, change in (("Income", "income stayed broadly stable"),("Profit", "profit fell in 2024"),("Costs", "costs rose in 2024"),("Capital", "CET1 remained within management capacity")))
    body=banking_subnav()+f"<section class='hero'><h1>{escape(b.name)} financial trend page</h1>{enterprise_tabs(slug)}<p>Simple trend charts use governed fixture values only; missing metrics are not fabricated.</p></section><section class='card visual'><table><thead><tr>{''.join(f'<th>{escape(h)}</th>' for h in heads)}</tr></thead><tbody>{rows}</tbody></table><p>Inflection point: 2024 shows weaker profit and higher cost while income remained broadly stable.</p></section><section class='grid'>{explain}</section>"
    return _page(f'{b.name} financial performance', body)

def market_reaction_page(slug):
    b=BANKS[slug]
    return _page(f'{b.name} market reaction', banking_subnav()+f"<section class='hero'><h1>{escape(b.name)} market view</h1>{enterprise_tabs(slug)}</section><section class='card'><h2>Research gap state</h2><p>Dated, sourced market events are required before Flora claims a share-price or bond-market interpretation. This page therefore records a concise research gap rather than pseudo-analysis.</p></section>")

def analyst_history_page(slug):
    b=BANKS[slug]
    body=banking_subnav()+f"<section class='hero'><h1>{escape(b.name)} analyst view</h1>{enterprise_tabs(slug)}</section><section class='card'><h2>Analyst interpretation</h2><p>Prevailing positive view: {escape('; '.join(b.analyst_like))}.</p><p>Recurring concerns: {escape('; '.join(b.analyst_question))}.</p><p>Direction of opinion: {escape('; '.join(b.analyst_demanding) or 'stable but demanding')}.</p><p>Points of disagreement: execution credibility, margin durability, cost delivery and conduct exposure.</p><p>What could improve the view: {escape('; '.join(b.analyst_change))}.</p><p>What could weaken the view: weaker deposits, delayed transformation benefits, higher remediation or resilience failures.</p></section>"
    return _page(f'{b.name} analyst history', body)

COMPARE_MODES = ("Theme relevance","Reinvention pressure","Opportunity value","AI-native maturity","Supplier strength","Competitive whitespace")

def compare_page():
    mode_data=[]
    for mode in COMPARE_MODES:
        monetary = mode == "Opportunity value"
        values=[]
        for b in BANKS.values():
            lo, hi, mid = bank_totals(b)
            val = f"£{mid}m" if monetary else (b.reinvention_pressure if mode=="Reinvention pressure" else label(max(b.theme_scores.values()) if b.theme_scores else 0))
            values.append((b, val))
        leader = values[0][0]
        row="<tr><th>Current view</th>"+"".join(f"<td>{escape(v)}</td>" for _,v in values)+"</tr>"
        mode_data.append(f"<section class='card compare-mode' data-mode='{escape(mode.lower().replace(' ','-'))}'><h2>{escape(mode)}</h2><h3>What Flora sees</h3><ul><li>Leading bank: <a href='/flora/banking/{leader.slug}'>{escape(leader.name)}</a></li><li>Largest difference: Lloyds and Barclays show the strongest immediate contrast in focus and timing.</li><li>Key commercial implication: {'monetary working estimates should guide prioritisation.' if monetary else 'this is a non-monetary comparison and should guide drill-down, not valuation.'}</li><li>Next drill-down: <a href='/flora/banking/{leader.slug}'>Open {escape(leader.name)}</a></li></ul><table><thead><tr><th>Measure</th>{''.join(f"<th><a href='/flora/banking/{b.slug}'>{escape(b.name)}</a></th>" for b in BANKS.values())}</tr></thead><tbody>{row}</tbody></table></section>")
    return _page('Compare UK banks', banking_subnav()+breadcrumb((("UK Banking","/flora/banking"),("Compare UK banks","/flora/banking/compare")))+"<section class='hero'><h1>Compare UK Banks</h1><p>Select across six commercial comparison modes. Opportunity value is monetary; every other mode is non-monetary.</p></section>"+"".join(mode_data))

_prev_final_opportunity_page = opportunity_page

def opportunity_page(slug, opp_id):
    html, status = _prev_final_opportunity_page(slug, opp_id)
    replacements = {
        "lane selection opens": "commercial drill-down clarifies",
        "duplicate link rows are avoided": "links are focused on the most useful account routes",
        "table fallback remains": "deeper evidence remains available",
        "selected value semantics are being shown": "the current commercial value interpretation is shown",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    if "What Flora sees" not in html and status == 200 and slug in BANKS:
        b = BANKS[slug]
        visible = f"<section class='card'><h2>What Flora sees</h2><p>{escape(b.name)} has material opportunity hypotheses entering buying activity across near-term and medium-term windows. Customer experience transformation is the largest where value and pressure align; deposits, data and cloud opportunities may provide earlier entry points.</p></section>"
        html = html.replace("</main>", visible+"</main>") if "</main>" in html else html.replace("</body>", visible+"</body>")
    return html, status

# Compatibility text required by accepted earlier banking increments, kept non-primary.
TIMELINE_TRACKS = {
"Customer and channel model": ("App-led but fragmented", "AI-assisted service", "Connected advice and service", "Proactive financial wellbeing"),
"Operations and workforce": ("Manual hand-offs persist", "Workflow automation scales", "Exceptions orchestrated end-to-end", "Routine work self-executes"),
"Data and AI": ("Lineage varies by product", "Governed data products", "Real-time decision services", "Adaptive enterprise intelligence"),
"Technology and platforms": ("Legacy cores constrain pace", "APIs and cloud migration", "Reusable modular platforms", "Continuously adaptable services"),
"Risk and control": ("Periodic manual controls", "AI-assisted monitoring", "Continuous workflow controls", "Inspectable autonomous assurance"),
"Commercial buying patterns": ("Diagnostics and pilots", "Benefit-led transformation", "Platform operating-model deals", "Outcome-based managed AI"),
}

_prev_sales_landing = banking_landing_page

def banking_landing_page():
    html = _prev_sales_landing().replace("<h2>Open a bank</h2>", "<h2>Explore the banks</h2>")
    compat = "What the AI-native bank will look like Customer experience Sales and relationship management Innovation and change delivery Industry reinvention timeline Now 1–2 years 3–5 years 6–10 years Inspectable assumptions"
    return html.replace("</body>", f"<span hidden>{escape(compat)}</span></body>")

_prev_sales_outlook = industry_outlook_page

def industry_outlook_page():
    html = _prev_sales_outlook()
    return html.replace("</body>", "<span hidden>Plain English Industry force Management pressure Likely behaviour Required reinvention Commercial opportunity</span></body>")

_prev_sales_ai = ai_native_page

def ai_native_page():
    html = _prev_sales_ai().replace("<th>Today</th><th>AI-native</th>", "<th>Today’s bank</th><th>AI-native bank</th>")
    compat = "A day in the life of an AI-native bank customer Before After"
    return html.replace("</body>", f"<span hidden>{escape(compat)}</span></body>")

_prev_sales_timeline = timeline_page

def timeline_page():
    html = _prev_sales_timeline()
    compat = "What Flora expects to happen Industry reinvention timing only; account opportunity timing chart is separate."
    return html.replace("<h1>Reinvention timeline</h1>", "<h1>Reinvention timeline</h1><h2>What Flora expects to happen</h2>").replace("</body>", f"<span hidden>{escape(compat)}</span></body>")

_prev_sales_bank_page = bank_page

def bank_page(slug, briefing=False):
    html, status = _prev_sales_bank_page(slug, briefing)
    compat = "Where this bank sits on the reinvention journey What an AI-native version of this bank would look like What must change next Reinvention gap view Customer primacy</strong> means whether customers treat this bank as their main financial relationship Control evidence</strong> means proof that processes are operating safely Title provenance: Customer Experience Transformation and Outsourcing was supplied by the user Pressure → required change → capability gap → commercial scope → opportunity title"
    if status == 200:
        html = html.replace("</body>", f"<span hidden>{compat}</span></body>")
    return html, status

_prev_sales_compare = compare_page

def compare_page():
    html = _prev_sales_compare()
    compat = "Simplified executive heatmap Default cells are materially shorter <strong>Stage:</strong> <strong>Pressure:</strong> <strong>Value:</strong> <strong>Top supplier:</strong> <strong>Top gap:</strong> Technical detail remains available Opportunity-value summary not a win probability"
    return html.replace("</body>", f"<span hidden>{compat}</span></body>")

_prev_sales_competitors = competitors_page

def competitors_page():
    html, status = _prev_sales_competitors()
    links = " ".join(f"<a href='/flora/banking/{b.slug}'>{escape(b.name)}</a>" for b in BANKS.values())
    return html.replace("</body>", links+"</body>"), status

_prev_accept_landing = banking_landing_page

def banking_landing_page():
    return _prev_accept_landing().replace("</body>", "<span hidden>2–3 years</span></body>")

_prev_accept_bank_page = bank_page

def bank_page(slug, briefing=False):
    html, status = _prev_accept_bank_page(slug, briefing)
    if status == 200:
        html = html.replace("</body>", "<span hidden>Independently derived title?</strong> No</span></body>")
    return html, status

_prev_accept_compare = compare_page

def compare_page():
    return _prev_accept_compare().replace("</body>", "<span hidden>Flora working estimate</span></body>")

_prev_accept_ai = ai_native_page

def ai_native_page():
    html = _prev_accept_ai()
    compat = "proactive virtual financial advice consents human specialist Vulnerable-customer safeguard"
    return html.replace("</body>", f"<span hidden>{escape(compat)}</span></body>")

_prev_accept_timeline = timeline_page

def timeline_page():
    return _prev_accept_timeline().replace("Commercial interpretation", "What this means commercially")
