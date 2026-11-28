"""Lloyds presentation paths over existing Source-owned projections."""
from dataclasses import dataclass

from . import intelligence_presentation as p


@dataclass(frozen=True)
class Path:
    title: str
    claims: tuple[str, ...]
    destinations: tuple[tuple[str, str, str], ...]
    context: str


def evidence_for(path, facts):
    """Resolve a path on every read, retaining only eligible reported evidence."""
    rows = tuple(facts.get(key) for key in path.claims)
    if all(item and item.semantic_type == 'reported' and p.eligible(item) for item in rows):
        return rows
    return ()


STRATEGY = (
    Path('Distribution productivity', ('LBG-CE-DISTRIBUTION25', 'LBG-CE-DISTRIBUTION26'),
         (('landscape', 'economics', 'distribution'), ('inside', 'people', 'employees'),
          ('forces', 'strategy', 'objective-distribution')),
         'The FY2025 measure and 2026 objective have different horizons. No full-year 2026 achievement is shown.'),
    Path('Cost efficiency and investment', ('LBG-A2030-CIR', 'LBG-A2030-SAVINGS', 'LBG-A2030-INVESTMENT'),
         (('landscape', 'economics', 'costs'), ('inside', 'programmes', 'legacy'),
          ('forces', 'strategy', 'objective-efficiency')),
         'Compare reported costs and separately dated guidance. Expected gross savings precede parallel-running and delivery costs.'),
    Path('Renewal and service continuity', ('LBG-AR25-MIGRATION', 'LBG-A2030-PLATFORMS', 'UK-PRA-REPORT27'),
         (('landscape', 'economics', 'reporting-context'), ('inside', 'operations', 'reporting-context'),
          ('forces', 'strategy', 'objective-reporting')),
         'The reported management plan and regulatory timetable are separate. A service outcome or delivery probability is not established.'),
    Path('Payments growth and customer use', ('LBG-A2030-WALLET', 'LBG-Q326-CURVE'),
         (('landscape', 'commercial', 'transactions'), ('inside', 'operations', 'journey-payments'),
          ('forces', 'strategy', 'objective-payments')),
         'The acquisition was reported complete. Adoption and product economics still determine what the strategy delivers.'),
    Path('Reported AI contribution and expectations', ('LBG-AI26-REPORTED', 'LBG-AI26-EXPECTED'),
         (('landscape', 'economics', 'ai-value'), ('inside', 'operations', 'journey-data'),
          ('forces', 'strategy', 'objective-ai')),
         'Reported value and a later expectation are not like-for-like realised net profit.'),
)

BUSINESS = {
    'retail': Path('Mortgage verification and retail resources',
                   ('LBG-CE-FTERETAIL', 'LBG-CE-MORTGAGESPEED', 'LBG-CE-VERTEX'),
                   (('landscape', 'retail', 'mortgage'), ('inside', 'operations', 'mortgage-ml'),
                    ('forces', 'strategy', 'objective-mortgage')),
                   'Retail employee FTEs cover the reporting business. Faster verification covers one step. No mortgage-team staffing or cost allocation is established.'),
    'commercial': Path('Digital business service and Commercial resources',
                       ('LBG-CE-FTECOMMERCIAL', 'LBG-CE-BCBDIGITAL', 'LBG-CE-BCBSERVICE'),
                       (('landscape', 'commercial', 'digital-business'), ('inside', 'operations', 'digital-business'),
                        ('forces', 'strategy', 'objective-business-digital')),
                       'The workforce count covers Commercial Banking. The operating evidence covers the stated Business Banking service, not the full segment.'),
    'retirement': Path('Investment account openings and business resources',
                       ('LBG-CE-FTEINSURANCE', 'LBG-CE-INVESTMENTACCOUNTS', 'LBG-CE-WEALTHPLAN'),
                       (('landscape', 'retirement', 'wealth-delivery'), ('inside', 'operations', 'journey-insurance'),
                        ('forces', 'strategy', 'investigations')),
                       'The account figure covers openings. It does not measure active accounts, returns or delivery of the advice integration plan.'),
}

PRESSURES = (
    Path('Funding pressure and margin', ('UK-RATE-NOV26', 'LBG-Q326-DEPOSITS'),
         (('landscape', 'economics', 'funding'), ('inside', 'operations', 'journey-credit'),
          ('forces', 'markets', '')),
         'Rates and the Group funding balance shape the margin question. Product-level sensitivity and peer pricing are not quantified.'),
    Path('Payment competition and substitutes', ('treasury-payments', 'LBG-A2030-WALLET', 'LBG-Q326-CURVE'),
         (('landscape', 'commercial', 'transactions'), ('inside', 'operations', 'journey-payments'),
          ('forces', 'competition', 'transaction-direction')),
         'The external pilot is policy context. It does not establish competitor adoption or prove a named supplier opportunity.'),
    Path('Service quality during simplification', ('UK-PRA-REPORT27', 'LBG-AR25-MIGRATION'),
         (('landscape', 'economics', 'reporting-context'), ('inside', 'operations', 'service'),
          ('forces', 'strategy', 'investigations')),
         'Investigate whether service quality and resilience hold as operating costs change. The reporting timetable alone does not establish a Lloyds failure.'),
)

ESTATE = (
    Path('Delivery and infrastructure', ('LBG-CE-CLOUD', 'LBG-CE-DATACENTRES', 'LBG-CE-RELEASES'),
         (('landscape', 'economics', 'costs'), ('inside', 'applications', 'platform-delivery'),
          ('forces', 'strategy', 'objective-renewal')),
         'Reported changes in data centres, cloud and release activity describe a dated delivery footprint. They do not specify workloads, locations or the current installed estate.'),
    Path('Branches and customer access', ('LBG-BRAND26-TIMING', 'LBG-BRAND26-NO-ROLES'),
         (('landscape', 'group', 'brands'), ('inside', 'programmes', 'brand'),
          ('forces', 'strategy', 'objective-access')),
         'The announcement defines the scope of planned access and its workforce qualification. Branch-level utilisation and costs are not established.'),
    Path('Commercial settlement pilot', ('LBG-CE-VISAPILOT', 'LBG-CE-SETTLEMENTSPEED', 'LBG-CE-JERSEY'),
         (('landscape', 'commercial', 'settlement'), ('inside', 'applications', 'settlement'),
          ('forces', 'competition', 'settlement')),
         'The timed pilot was scoped to the named participants and Jersey booking perimeter. There is no inference of a production contract or dependency.'),
)
