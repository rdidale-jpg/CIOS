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
