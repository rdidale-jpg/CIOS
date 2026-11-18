# Banking ecosystem — role and relationship map

Solid connections below are source-reported **research candidates**, not accepted contracts, dependency criticality or canonical graph edges. Exact predicates, parties, dates and limitations are in [Typed-Relationships.json](Typed-Relationships.json). No diagram adjacency creates an additional relationship.

```mermaid
flowchart LR
  LBG["Lloyds Banking Group"] -->|"Envoy built with brand · 28 Apr"| GC["Google Cloud brand"]
  NW["NatWest Group"] -->|"Data collaboration · Group/brand scope"| AWS["AWS brand"]
  NW -->|"Data collaboration · Group/brand scope"| ACC["Accenture brand"]
  STAR["Starling bank brand"] -->|"Model development · 14 Oct"| NV["NVIDIA brand"]
  STAR -->|"Model training infrastructure · 14 Oct"| CIVO["Civo brand"]
  CB["ClearBank Group"] -->|"Issuer names embedded partner · FY25"| PC["PayCaptain brand"]
  BOE["Bank of England · operator role"] -->|operates| RTGS["RTGS infrastructure"]
  BOE -->|operates| CHAPS["CHAPS system"]
  LB["Lloyds Bank plc"] -->|"Listed direct participant · observed 18 Nov"| CHAPS
  NWP["National Westminster Bank plc"] -->|"Listed direct participant · observed 18 Nov"| CHAPS
  HU["HSBC UK Bank plc"] -->|"Listed direct participant · observed 18 Nov"| CHAPS
  CBL["ClearBank Limited"] -->|"Listed direct participant · observed 18 Nov"| CHAPS
```

The commercial value-system reference is **customer choice and servicing → funding and credit → payments and settlement → enabling technology/control**. This ordering is conceptual: a provider can support several stages, and a regulator is not a production supplier. Actual enterprise capabilities are distinct from the ordered stages. Banks, mutuals, operator/provider firms and institutions use different economic measures.

Pay.UK Limited remains separate from Bacs/FPS/ICS systems and CASS switching service. Guarantor governance, direct clearing participation, indirect access, settlement accounts, technology infrastructure and legal service contracts are distinct roles. Its financial/list/tariff evidence remains withheld under the documented acquisition/use exception; there is no inferred participant graph here.

The July CTP legal-person designations and 17 November additional cohort are national oversight context. They do not turn the Google Cloud brand edge into a Lloyds Bank plc–Google Cloud EMEA Limited contract, make a bank workload critical or establish purchasing intent. PRA is part of the Bank; FCA conduct and PSR access functions retain separate powers/status. A proposed transfer is not an already completed merger.

The airline/holidays reporting elimination and provider economic exemplars demonstrate cross-sector reuse of the same exact-scope method. They add no unverified Banking supplier/client edges. All 31 older candidate edges remain preserved separately, including their unresolved legal parties and source-use requirements.
