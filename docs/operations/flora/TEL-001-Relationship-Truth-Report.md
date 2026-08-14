# TEL-001 Relationship Truth Report

## Audit decision

**SAFE TO MERGE.** This is a source-truth audit and presentation-only change. The governed ZIP was read in place and was not modified. No importer, validator, resolver, semantic construction, association, governance, promotion, Programme, or Opportunity runtime behaviour was changed.

## Fixture verification and record-set filenames

- Repository fixture: `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`
- SHA-256: `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07` (matches expected: **YES**)
- Relationship record set: `record_sets/relationship_register_wave5.ndjson` (308 records)
- Membership record set: `record_sets/membership_register_wave5.ndjson` (50 records)
- Enterprise record set: `record_sets/enterprise_dossiers_wave5.ndjson` (6 records)
- Programme record set: `record_sets/programme_objects_wave5.ndjson` (13 records)
- Opportunity record set: `record_sets/opportunity_objects_wave5.ndjson` (17 records)

“Exists” below means an exact endpoint identity resolves to an accepted governed object record from the unchanged ZIP; labels and pseudo-identities are not treated as objects. Enterprise relevance is direct only: the Enterprise ID must be a source or target endpoint.

## Relationship-family summary

| Source family | Relationship type | Target family | Count |
|---|---|---|---:|
| Enterprise | Enterprise owns Programme | Programme | 11 |
| Evidence | Evidence supports Industry Economics | Not an object record in governed ZIP record sets | 1 |
| Evidence | Evidence supports Industry Infrastructure | Not an object record in governed ZIP record sets | 1 |
| Evidence | Evidence supports Opportunity | Opportunity | 48 |
| Market Participant | Enterprise owns Programme | Programme | 1 |
| Market Participant | Participant enables Opportunity | Opportunity | 1 |
| Market Participant | Participant partners Enterprise | Enterprise | 2 |
| Market Participant | Participant partners Participant | Market Participant | 1 |
| Market Participant | Participant supplies Enterprise | Enterprise | 5 |
| Market Participant | Participant supplies/partners Enterprise | Enterprise | 9 |
| Market Participant | Regulation impacts Enterprise | Enterprise | 8 |
| Market Participant | Regulation impacts Programme | Programme | 1 |
| Monitoring Trigger | Monitoring Trigger watches Opportunity | Opportunity | 51 |
| Not an object record in governed ZIP record sets | Enterprise owns Programme | Programme | 1 |
| Not an object record in governed ZIP record sets | Estimate addresses Unknown | Not an object record in governed ZIP record sets | 17 |
| Not an object record in governed ZIP record sets | Estimate addresses Unknown | Unknown | 76 |
| Not an object record in governed ZIP record sets | Programme creates Opportunity | Opportunity | 1 |
| Not an object record in governed ZIP record sets | Technology enables Programme | Programme | 2 |
| Opportunity | Opportunity classified into pipeline bucket | Not an object record in governed ZIP record sets | 17 |
| Opportunity | Opportunity targets Business Unit | Not an object record in governed ZIP record sets | 16 |
| Opportunity | Opportunity targets Enterprise | Enterprise | 16 |
| Opportunity | Opportunity targets Enterprise | Market Participant | 1 |
| Programme | Programme creates Opportunity | Opportunity | 16 |
| Programme | Programme creates or enables Opportunity | Opportunity | 5 |

**Reconciled total: 308 Relationship records.**

## Enterprise truth matrix

| Enterprise | Related Programmes | Related Opportunities | Related Market Participants | Other relationships |
|---|---|---|---|---|
| BT Group (`ENT-BT`) | `PROG-BT-TRANSFORMATION` — Enterprise owns Programme (`REL-W2-001`) | `OPP-BT-AI-ENGINEERING` — Opportunity targets Enterprise (`REL-W2-014`)<br>`OPP-BT-AIOPS` — Opportunity targets Enterprise (`REL-W2-017`)<br>`OPP-BT-VERIZON-JV-INTEGRATION` — Opportunity targets Enterprise (`REL-W4-183`) | `MP-KYNDRYL` — Participant supplies/partners Enterprise (`REL-W2-043`)<br>`MP-DYNATRACE` — Participant supplies/partners Enterprise (`REL-W2-044`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-052`) | None explicitly supplied in TEL-001 Relationship objects. |
| Openreach (`ENT-OPENREACH`) | `PROG-OPENREACH-FTTP` — Enterprise owns Programme (`REL-W2-002`) | `OPP-OPENREACH-FIBRE-AUTOMATION` — Opportunity targets Enterprise (`REL-W2-020`)<br>`OPP-OPENREACH-CP-ENABLEMENT` — Opportunity targets Enterprise (`REL-W2-023`)<br>`OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-128`) | `MP-NOKIA` — Participant supplies/partners Enterprise (`REL-W2-045`)<br>`MP-GOOGLE` — Participant supplies/partners Enterprise (`REL-W2-046`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-053`)<br>`MP-DSIT-BDUK` — Participant supplies Enterprise (`REL-W3-018`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W3-020`) | None explicitly supplied in TEL-001 Relationship objects. |
| Virgin Media O2 (`ENT-VMO2`) | `PROG-VMO2-LUMI-AI` — Enterprise owns Programme (`REL-W2-004`)<br>`PROG-VMO2-MOBILE-TRANSFORMATION` — Enterprise owns Programme (`REL-W3-001`)<br>`PROG-VMO2-LUMI-AI` — Enterprise owns Programme (`REL-W3-006`) | `OPP-VMO2-AI-CX` — Opportunity targets Enterprise (`REL-W2-011`)<br>`OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-140`)<br>`OPP-VMO2-NEXFIBRE-MIGRATION` — Opportunity targets Enterprise (`REL-W4-151`) | `MP-AWS` — Participant supplies/partners Enterprise (`REL-W2-047`)<br>`MP-HIYA` — Participant supplies/partners Enterprise (`REL-W2-048`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-054`)<br>`MP-ERICSSON` — Participant supplies Enterprise (`REL-W3-003`)<br>`MP-NOKIA` — Participant supplies Enterprise (`REL-W3-004`)<br>`MP-AWS` — Participant supplies Enterprise (`REL-W3-005`)<br>`MP-NEXFIBRE` — Participant partners Enterprise (`REL-W3-008`)<br>`MP-LIBERTY-TELEFONICA-INFRAVIA` — Participant partners Enterprise (`REL-W3-024`) | None explicitly supplied in TEL-001 Relationship objects. |
| VodafoneThree (`ENT-VODAFONETHREE`) | `PROG-VT-5G-SA` — Enterprise owns Programme (`REL-W2-005`)<br>`PROG-VT-INTEGRATION` — Enterprise owns Programme (`REL-W2-006`)<br>`PROG-VT-INTEGRATION` — Enterprise owns Programme (`REL-W3-012`)<br>`PROG-VT-5G-SA` — Enterprise owns Programme (`REL-W3-013`) | `OPP-VT-NETWORK-AI-OPS` — Opportunity targets Enterprise (`REL-W2-026`)<br>`OPP-VT-ENTERPRISE-5G` — Opportunity targets Enterprise (`REL-W2-029`)<br>`OPP-VT-WHOLESALE-REMEDY-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-162`) | `MP-ERICSSON` — Participant supplies/partners Enterprise (`REL-W2-049`)<br>`MP-NOKIA` — Participant supplies/partners Enterprise (`REL-W2-050`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-055`)<br>`MP-CMA` — Regulation impacts Enterprise (`REL-W3-014`) | None explicitly supplied in TEL-001 Relationship objects. |
| CityFibre (`ENT-CITYFIBRE`) | `PROG-CITYFIBRE-WHOLESALE` — Enterprise owns Programme (`REL-W2-008`) | `OPP-CITYFIBRE-PROJECT-GIGABIT` — Opportunity targets Enterprise (`REL-W2-032`)<br>`OPP-CITYFIBRE-WHOLESALE` — Opportunity targets Enterprise (`REL-W2-035`) | `MP-DSIT-BDUK` — Participant supplies/partners Enterprise (`REL-W2-051`)<br>`MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-056`)<br>`MP-DSIT-BDUK` — Participant supplies Enterprise (`REL-W3-019`) | None explicitly supplied in TEL-001 Relationship objects. |
| TalkTalk (`ENT-TALKTALK`) | `PROG-TALKTALK-PXC-DEMERGER` — Enterprise owns Programme (`REL-W2-009`) | `OPP-TALKTALK-COST` — Opportunity targets Enterprise (`REL-W2-038`)<br>`OPP-PXC-PLATFORM-EFFICIENCY` — Opportunity targets Enterprise (`REL-W2-041`) | `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-057`) | None explicitly supplied in TEL-001 Relationship objects. |

### BT Group

**Programmes:**
- `PROG-BT-TRANSFORMATION` — Enterprise owns Programme (`REL-W2-001`; endpoints `ENT-BT` → `PROG-BT-TRANSFORMATION`)

**Opportunities:**
- `OPP-BT-AI-ENGINEERING` — Opportunity targets Enterprise (`REL-W2-014`; endpoints `OPP-BT-AI-ENGINEERING` → `ENT-BT`)
- `OPP-BT-AIOPS` — Opportunity targets Enterprise (`REL-W2-017`; endpoints `OPP-BT-AIOPS` → `ENT-BT`)
- `OPP-BT-VERIZON-JV-INTEGRATION` — Opportunity targets Enterprise (`REL-W4-183`; endpoints `OPP-BT-VERIZON-JV-INTEGRATION` → `ENT-BT`)

**Market Participants:**
- `MP-KYNDRYL` — Participant supplies/partners Enterprise (`REL-W2-043`; endpoints `MP-KYNDRYL` → `ENT-BT`)
- `MP-DYNATRACE` — Participant supplies/partners Enterprise (`REL-W2-044`; endpoints `MP-DYNATRACE` → `ENT-BT`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-052`; endpoints `MP-OFCOM` → `ENT-BT`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

### Openreach

**Programmes:**
- `PROG-OPENREACH-FTTP` — Enterprise owns Programme (`REL-W2-002`; endpoints `ENT-OPENREACH` → `PROG-OPENREACH-FTTP`)

**Opportunities:**
- `OPP-OPENREACH-FIBRE-AUTOMATION` — Opportunity targets Enterprise (`REL-W2-020`; endpoints `OPP-OPENREACH-FIBRE-AUTOMATION` → `ENT-OPENREACH`)
- `OPP-OPENREACH-CP-ENABLEMENT` — Opportunity targets Enterprise (`REL-W2-023`; endpoints `OPP-OPENREACH-CP-ENABLEMENT` → `ENT-OPENREACH`)
- `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-128`; endpoints `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` → `ENT-OPENREACH`)

**Market Participants:**
- `MP-NOKIA` — Participant supplies/partners Enterprise (`REL-W2-045`; endpoints `MP-NOKIA` → `ENT-OPENREACH`)
- `MP-GOOGLE` — Participant supplies/partners Enterprise (`REL-W2-046`; endpoints `MP-GOOGLE` → `ENT-OPENREACH`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-053`; endpoints `MP-OFCOM` → `ENT-OPENREACH`)
- `MP-DSIT-BDUK` — Participant supplies Enterprise (`REL-W3-018`; endpoints `MP-DSIT-BDUK` → `ENT-OPENREACH`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W3-020`; endpoints `MP-OFCOM` → `ENT-OPENREACH`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

### Virgin Media O2

**Programmes:**
- `PROG-VMO2-LUMI-AI` — Enterprise owns Programme (`REL-W2-004`; endpoints `ENT-VMO2` → `PROG-VMO2-LUMI-AI`)
- `PROG-VMO2-MOBILE-TRANSFORMATION` — Enterprise owns Programme (`REL-W3-001`; endpoints `ENT-VMO2` → `PROG-VMO2-MOBILE-TRANSFORMATION`)
- `PROG-VMO2-LUMI-AI` — Enterprise owns Programme (`REL-W3-006`; endpoints `ENT-VMO2` → `PROG-VMO2-LUMI-AI`)

**Opportunities:**
- `OPP-VMO2-AI-CX` — Opportunity targets Enterprise (`REL-W2-011`; endpoints `OPP-VMO2-AI-CX` → `ENT-VMO2`)
- `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-140`; endpoints `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` → `ENT-VMO2`)
- `OPP-VMO2-NEXFIBRE-MIGRATION` — Opportunity targets Enterprise (`REL-W4-151`; endpoints `OPP-VMO2-NEXFIBRE-MIGRATION` → `ENT-VMO2`)

**Market Participants:**
- `MP-AWS` — Participant supplies/partners Enterprise (`REL-W2-047`; endpoints `MP-AWS` → `ENT-VMO2`)
- `MP-HIYA` — Participant supplies/partners Enterprise (`REL-W2-048`; endpoints `MP-HIYA` → `ENT-VMO2`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-054`; endpoints `MP-OFCOM` → `ENT-VMO2`)
- `MP-ERICSSON` — Participant supplies Enterprise (`REL-W3-003`; endpoints `MP-ERICSSON` → `ENT-VMO2`)
- `MP-NOKIA` — Participant supplies Enterprise (`REL-W3-004`; endpoints `MP-NOKIA` → `ENT-VMO2`)
- `MP-AWS` — Participant supplies Enterprise (`REL-W3-005`; endpoints `MP-AWS` → `ENT-VMO2`)
- `MP-NEXFIBRE` — Participant partners Enterprise (`REL-W3-008`; endpoints `MP-NEXFIBRE` → `ENT-VMO2`)
- `MP-LIBERTY-TELEFONICA-INFRAVIA` — Participant partners Enterprise (`REL-W3-024`; endpoints `MP-LIBERTY-TELEFONICA-INFRAVIA` → `ENT-VMO2`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

### VodafoneThree

**Programmes:**
- `PROG-VT-5G-SA` — Enterprise owns Programme (`REL-W2-005`; endpoints `ENT-VODAFONETHREE` → `PROG-VT-5G-SA`)
- `PROG-VT-INTEGRATION` — Enterprise owns Programme (`REL-W2-006`; endpoints `ENT-VODAFONETHREE` → `PROG-VT-INTEGRATION`)
- `PROG-VT-INTEGRATION` — Enterprise owns Programme (`REL-W3-012`; endpoints `ENT-VODAFONETHREE` → `PROG-VT-INTEGRATION`)
- `PROG-VT-5G-SA` — Enterprise owns Programme (`REL-W3-013`; endpoints `ENT-VODAFONETHREE` → `PROG-VT-5G-SA`)

**Opportunities:**
- `OPP-VT-NETWORK-AI-OPS` — Opportunity targets Enterprise (`REL-W2-026`; endpoints `OPP-VT-NETWORK-AI-OPS` → `ENT-VODAFONETHREE`)
- `OPP-VT-ENTERPRISE-5G` — Opportunity targets Enterprise (`REL-W2-029`; endpoints `OPP-VT-ENTERPRISE-5G` → `ENT-VODAFONETHREE`)
- `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` — Opportunity targets Enterprise (`REL-W4-162`; endpoints `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` → `ENT-VODAFONETHREE`)

**Market Participants:**
- `MP-ERICSSON` — Participant supplies/partners Enterprise (`REL-W2-049`; endpoints `MP-ERICSSON` → `ENT-VODAFONETHREE`)
- `MP-NOKIA` — Participant supplies/partners Enterprise (`REL-W2-050`; endpoints `MP-NOKIA` → `ENT-VODAFONETHREE`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-055`; endpoints `MP-OFCOM` → `ENT-VODAFONETHREE`)
- `MP-CMA` — Regulation impacts Enterprise (`REL-W3-014`; endpoints `MP-CMA` → `ENT-VODAFONETHREE`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

### CityFibre

**Programmes:**
- `PROG-CITYFIBRE-WHOLESALE` — Enterprise owns Programme (`REL-W2-008`; endpoints `ENT-CITYFIBRE` → `PROG-CITYFIBRE-WHOLESALE`)

**Opportunities:**
- `OPP-CITYFIBRE-PROJECT-GIGABIT` — Opportunity targets Enterprise (`REL-W2-032`; endpoints `OPP-CITYFIBRE-PROJECT-GIGABIT` → `ENT-CITYFIBRE`)
- `OPP-CITYFIBRE-WHOLESALE` — Opportunity targets Enterprise (`REL-W2-035`; endpoints `OPP-CITYFIBRE-WHOLESALE` → `ENT-CITYFIBRE`)

**Market Participants:**
- `MP-DSIT-BDUK` — Participant supplies/partners Enterprise (`REL-W2-051`; endpoints `MP-DSIT-BDUK` → `ENT-CITYFIBRE`)
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-056`; endpoints `MP-OFCOM` → `ENT-CITYFIBRE`)
- `MP-DSIT-BDUK` — Participant supplies Enterprise (`REL-W3-019`; endpoints `MP-DSIT-BDUK` → `ENT-CITYFIBRE`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

### TalkTalk

**Programmes:**
- `PROG-TALKTALK-PXC-DEMERGER` — Enterprise owns Programme (`REL-W2-009`; endpoints `ENT-TALKTALK` → `PROG-TALKTALK-PXC-DEMERGER`)

**Opportunities:**
- `OPP-TALKTALK-COST` — Opportunity targets Enterprise (`REL-W2-038`; endpoints `OPP-TALKTALK-COST` → `ENT-TALKTALK`)
- `OPP-PXC-PLATFORM-EFFICIENCY` — Opportunity targets Enterprise (`REL-W2-041`; endpoints `OPP-PXC-PLATFORM-EFFICIENCY` → `ENT-TALKTALK`)

**Market Participants:**
- `MP-OFCOM` — Regulation impacts Enterprise (`REL-W2-057`; endpoints `MP-OFCOM` → `ENT-TALKTALK`)

**Other:**
None explicitly supplied in TEL-001 Relationship objects.

## Programme trace: BT/Verizon JV

- Programme ID: `PROG-BT-VERIZON-JV`
- Programme source file: `record_sets/programme_objects_wave5.ndjson`
- ENT-BT explicitly linked: **NO**
- Link form: **neither direct nor mediated through another explicit Relationship object**. No Relationship record has the Programme as an endpoint, so its narrative and embedded fields cannot establish canonical linkage.

## Opportunity trace: BT/Verizon JV integration

- Opportunity ID: `OPP-BT-VERIZON-JV-INTEGRATION`
- Opportunity source file: `record_sets/opportunity_objects_wave5.ndjson`
- `REL-W4-183` — `OPP-BT-VERIZON-JV-INTEGRATION` → `ENT-BT` — Opportunity targets Enterprise
- `REL-W4-184` — `EV-BT-VERIZON-JV-W4` → `OPP-BT-VERIZON-JV-INTEGRATION` — Evidence supports Opportunity
- `REL-W4-189` — `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-01` → `OPP-BT-VERIZON-JV-INTEGRATION` — Monitoring Trigger watches Opportunity
- `REL-W4-190` — `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-02` → `OPP-BT-VERIZON-JV-INTEGRATION` — Monitoring Trigger watches Opportunity
- `REL-W4-191` — `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-03` → `OPP-BT-VERIZON-JV-INTEGRATION` — Monitoring Trigger watches Opportunity
- `REL-W5-OPP-PIPELINE-OPP-BT-VERIZON-JV-INTEGRATION` — `OPP-BT-VERIZON-JV-INTEGRATION` → `Named open opportunity pipeline` — Opportunity classified into pipeline bucket
- Direct BT relationship: **YES**

## Membership audit (50 records)

| Membership ID | Member object | Member family | Container/parent object | Parent family | Contributes to Enterprise association semantics? |
|---|---|---|---|---|---|
| `MEM-ENT-BT` | `ENT-BT` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-ENT-OPENREACH` | `ENT-OPENREACH` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-ENT-VMO2` | `ENT-VMO2` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-ENT-VODAFONETHREE` | `ENT-VODAFONETHREE` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-ENT-CITYFIBRE` | `ENT-CITYFIBRE` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-ENT-TALKTALK` | `ENT-TALKTALK` | Enterprise | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-OFCOM` | `MP-OFCOM` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-DSIT-BDUK` | `MP-DSIT-BDUK` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-CMA` | `MP-CMA` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-ERICSSON` | `MP-ERICSSON` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-NOKIA` | `MP-NOKIA` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-AWS` | `MP-AWS` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-KYNDRYL` | `MP-KYNDRYL` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-DYNATRACE` | `MP-DYNATRACE` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-SERVICENOW` | `MP-SERVICENOW` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-GOOGLE` | `MP-GOOGLE` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-HIYA` | `MP-HIYA` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-NEXFIBRE` | `MP-NEXFIBRE` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-BT-TRANSFORMATION` | `PROG-BT-TRANSFORMATION` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-OPENREACH-FTTP` | `PROG-OPENREACH-FTTP` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-COPPER-PSTN-MIGRATION` | `PROG-COPPER-PSTN-MIGRATION` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-VMO2-LUMI-AI` | `PROG-VMO2-LUMI-AI` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-VT-5G-SA` | `PROG-VT-5G-SA` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-VT-INTEGRATION` | `PROG-VT-INTEGRATION` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-PROJECT-GIGABIT` | `PROG-PROJECT-GIGABIT` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-CITYFIBRE-WHOLESALE` | `PROG-CITYFIBRE-WHOLESALE` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-TALKTALK-PXC-DEMERGER` | `PROG-TALKTALK-PXC-DEMERGER` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VMO2-AI-CX` | `OPP-VMO2-AI-CX` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-BT-AI-ENGINEERING` | `OPP-BT-AI-ENGINEERING` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-BT-AIOPS` | `OPP-BT-AIOPS` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-OPENREACH-FIBRE-AUTOMATION` | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-OPENREACH-CP-ENABLEMENT` | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VT-NETWORK-AI-OPS` | `OPP-VT-NETWORK-AI-OPS` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VT-ENTERPRISE-5G` | `OPP-VT-ENTERPRISE-5G` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-CITYFIBRE-PROJECT-GIGABIT` | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-CITYFIBRE-WHOLESALE` | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-TALKTALK-COST` | `OPP-TALKTALK-COST` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-PXC-PLATFORM-EFFICIENCY` | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-VMO2-MOBILE-TRANSFORMATION` | `PROG-VMO2-MOBILE-TRANSFORMATION` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-PROG-NEXFIBRE-NETOMNIA-CONSOLIDATION` | `PROG-NEXFIBRE-NETOMNIA-CONSOLIDATION` | Programme | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VMO2-NEXFIBRE-MIGRATION` | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-NETOMNIA-SUBSTANTIAL` | `MP-NETOMNIA-SUBSTANTIAL` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-CCS-GCA` | `MP-CCS-GCA` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-MP-LIBERTY-TELEFONICA-INFRAVIA` | `MP-LIBERTY-TELEFONICA-INFRAVIA` | Market Participant | `IND-UK-TELECOMS` | Industry Twin | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-W4-MP-VERIZON` | `MP-VERIZON` | Market Participant | `TEL-001` | Release Manifest | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |
| `MEM-W4-MP-SKY` | `MP-SKY` | Market Participant | `TEL-001` | Release Manifest | NO — industry inclusion only; not an Enterprise → Programme/Opportunity edge |

All 50 Membership objects place a child record in the parent Industry Twin. They do not connect a Programme or Opportunity to an Enterprise. Therefore Membership is **not needed** to understand Enterprise → Programme/Opportunity association; the explicit Relationship objects are sufficient. The six Enterprise memberships establish Industry Twin inclusion only.

## Runtime comparison

The supplied current Flora evidence is 0 associated Programmes and 0 associated Opportunities on every Enterprise page. Source counts below use only direct, explicit Relationship endpoints.

| Enterprise | Source Programmes | Flora Programmes | Source Opportunities | Flora Opportunities | Conclusion |
|---|---:|---:|---:|---:|---|
| BT Group (`ENT-BT`) | 1 | 0 | 3 | 0 | **FLORA DEFECT** |
| Openreach (`ENT-OPENREACH`) | 1 | 0 | 3 | 0 | **FLORA DEFECT** |
| Virgin Media O2 (`ENT-VMO2`) | 2 | 0 | 3 | 0 | **FLORA DEFECT** |
| VodafoneThree (`ENT-VODAFONETHREE`) | 2 | 0 | 3 | 0 | **FLORA DEFECT** |
| CityFibre (`ENT-CITYFIBRE`) | 1 | 0 | 2 | 0 | **FLORA DEFECT** |
| TalkTalk (`ENT-TALKTALK`) | 1 | 0 | 2 | 0 | **FLORA DEFECT** |

## Relationship resolution comparison (all source Relationship records)

“First divergence” is “None” when candidate inventory and resolution preserve source truth. For unresolved rows it identifies the first resolver boundary evidenced by the current candidate resolver.

| Source Relationship ID | Present in Flora candidate inventory | Endpoint IDs preserved | Relationship type preserved | Candidate resolver result | First divergence |
|---|---|---|---|---|---|
| `REL-W2-001` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-002` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-003` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-004` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-005` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-006` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-007` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-008` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-009` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-010` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-011` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-012` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-013` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-014` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-015` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-016` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-017` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-018` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-019` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-020` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-021` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-022` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-023` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-024` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-025` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-026` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-027` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-028` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-029` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-030` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-031` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-032` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-033` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-034` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-035` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-036` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-037` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-038` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-039` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-040` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-041` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-042` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W2-043` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-044` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-045` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-046` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-047` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-048` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-049` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-050` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-051` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-052` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-053` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-054` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-055` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-056` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W2-057` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-001` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-002` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-003` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-004` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-005` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-006` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-007` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-008` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-009` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-010` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-011` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-012` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-013` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-014` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-015` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-016` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-017` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-018` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-019` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-020` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-021` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W3-022` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W3-023` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W3-024` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-001` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-002` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-003` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-004` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-005` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-006` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-007` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-008` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-009` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-010` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-011` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-012` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-013` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-014` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-015` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-016` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-017` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-018` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-019` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-020` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-021` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-022` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-023` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-024` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-025` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-026` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-027` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-028` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-029` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-030` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-031` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-032` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-033` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-034` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-035` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-036` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-037` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-038` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-039` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-040` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-041` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-042` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-043` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-044` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-045` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-046` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-047` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-048` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-049` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-050` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-051` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-052` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-053` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-054` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-055` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-056` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-057` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-058` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-059` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-060` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-061` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-062` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-063` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-064` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-065` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-066` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-067` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-068` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-069` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-070` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-071` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-072` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-073` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-074` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-075` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-076` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-077` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-078` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-079` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-080` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-081` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-082` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-083` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-084` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-085` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-086` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-087` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-088` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-089` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-090` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-091` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-092` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-093` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-094` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-095` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-096` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-097` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-098` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-099` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-100` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-101` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-102` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-103` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-104` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-105` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-106` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-107` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-108` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-109` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-110` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-111` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-112` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-113` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-114` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-115` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-116` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-117` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-118` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-119` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-120` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-121` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-122` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-123` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-124` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-125` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-126` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-127` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-128` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-129` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-130` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-131` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-132` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-133` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-134` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-135` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-136` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-137` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-138` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-139` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-140` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-141` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-142` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-143` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-144` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-145` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-146` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-147` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-148` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-149` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-150` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-151` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-152` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-153` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-154` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-155` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-156` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-157` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-158` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-159` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-160` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-161` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-162` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-163` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-164` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-165` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-166` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-167` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-168` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-169` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-170` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-171` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-172` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-173` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-174` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-175` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-176` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-177` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-178` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-179` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-180` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-181` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-182` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-183` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-184` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-185` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-186` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-187` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-188` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-189` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-190` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-191` | YES | YES | YES | candidate relationship resolved — candidate endpoints resolved in import scope | None |
| `REL-W4-192` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W4-193` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-AI-CX` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-AI-CX` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-BT-AI-ENGINEERING` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-BT-AI-ENGINEERING` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-BT-AIOPS` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-BT-AIOPS` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-FIBRE-AUTOMATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-FIBRE-AUTOMATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-CP-ENABLEMENT` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-CP-ENABLEMENT` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VT-NETWORK-AI-OPS` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VT-NETWORK-AI-OPS` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VT-ENTERPRISE-5G` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VT-ENTERPRISE-5G` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-CITYFIBRE-PROJECT-GIGABIT` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-CITYFIBRE-PROJECT-GIGABIT` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-CITYFIBRE-WHOLESALE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-CITYFIBRE-WHOLESALE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-TALKTALK-COST` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-TALKTALK-COST` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-PXC-PLATFORM-EFFICIENCY` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-PXC-PLATFORM-EFFICIENCY` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-NEXFIBRE-MIGRATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-NEXFIBRE-MIGRATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-EST-UNKNOWN-OPP-BT-VERIZON-JV-INTEGRATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |
| `REL-W5-OPP-PIPELINE-OPP-BT-VERIZON-JV-INTEGRATION` | YES | YES | YES | candidate relationship unresolved — endpoint missing | endpoint missing |

## Complete Relationship register (308 records)

| Relationship ID | Relationship type | Source object ID | Source family | Target object ID | Target family | Source endpoint exists in ZIP | Target endpoint exists in ZIP | Enterprise relevance |
|---|---|---|---|---|---|---|---|---|
| `REL-W2-001` | Enterprise owns Programme | `ENT-BT` | Enterprise | `PROG-BT-TRANSFORMATION` | Programme | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-002` | Enterprise owns Programme | `ENT-OPENREACH` | Enterprise | `PROG-OPENREACH-FTTP` | Programme | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-003` | Enterprise owns Programme | `ENT-OPENREACH/Industry` | Not an object record in governed ZIP record sets | `PROG-COPPER-PSTN-MIGRATION` | Programme | NO | YES | None |
| `REL-W2-004` | Enterprise owns Programme | `ENT-VMO2` | Enterprise | `PROG-VMO2-LUMI-AI` | Programme | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W2-005` | Enterprise owns Programme | `ENT-VODAFONETHREE` | Enterprise | `PROG-VT-5G-SA` | Programme | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-006` | Enterprise owns Programme | `ENT-VODAFONETHREE` | Enterprise | `PROG-VT-INTEGRATION` | Programme | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-007` | Enterprise owns Programme | `MP-DSIT-BDUK` | Market Participant | `PROG-PROJECT-GIGABIT` | Programme | YES | YES | None |
| `REL-W2-008` | Enterprise owns Programme | `ENT-CITYFIBRE` | Enterprise | `PROG-CITYFIBRE-WHOLESALE` | Programme | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W2-009` | Enterprise owns Programme | `ENT-TALKTALK` | Enterprise | `PROG-TALKTALK-PXC-DEMERGER` | Programme | YES | YES | TalkTalk (`ENT-TALKTALK`) |
| `REL-W2-010` | Programme creates Opportunity | `PROG-VMO2-LUMI-AI` | Programme | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W2-011` | Opportunity targets Enterprise | `OPP-VMO2-AI-CX` | Opportunity | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W2-012` | Opportunity targets Business Unit | `OPP-VMO2-AI-CX` | Opportunity | `ENT-VMO2:Customer operations` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-013` | Programme creates Opportunity | `PROG-BT-TRANSFORMATION` | Programme | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W2-014` | Opportunity targets Enterprise | `OPP-BT-AI-ENGINEERING` | Opportunity | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-015` | Opportunity targets Business Unit | `OPP-BT-AI-ENGINEERING` | Opportunity | `ENT-BT:BT Digital / Technology` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-016` | Programme creates Opportunity | `PROG-BT-AIOPS` | Not an object record in governed ZIP record sets | `OPP-BT-AIOPS` | Opportunity | NO | YES | None |
| `REL-W2-017` | Opportunity targets Enterprise | `OPP-BT-AIOPS` | Opportunity | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-018` | Opportunity targets Business Unit | `OPP-BT-AIOPS` | Opportunity | `ENT-BT:Service operations / Digital` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-019` | Programme creates Opportunity | `PROG-OPENREACH-FTTP` | Programme | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W2-020` | Opportunity targets Enterprise | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-021` | Opportunity targets Business Unit | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | `ENT-OPENREACH:Network build/planning` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-022` | Programme creates Opportunity | `PROG-COPPER-PSTN-MIGRATION` | Programme | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W2-023` | Opportunity targets Enterprise | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-024` | Opportunity targets Business Unit | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | `ENT-OPENREACH:Wholesale access` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-025` | Programme creates Opportunity | `PROG-VT-5G-SA` | Programme | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W2-026` | Opportunity targets Enterprise | `OPP-VT-NETWORK-AI-OPS` | Opportunity | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-027` | Opportunity targets Business Unit | `OPP-VT-NETWORK-AI-OPS` | Opportunity | `ENT-VODAFONETHREE:Network/integration` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-028` | Programme creates Opportunity | `PROG-VT-5G-SA` | Programme | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W2-029` | Opportunity targets Enterprise | `OPP-VT-ENTERPRISE-5G` | Opportunity | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-030` | Opportunity targets Business Unit | `OPP-VT-ENTERPRISE-5G` | Opportunity | `ENT-VODAFONETHREE:Business/enterprise 5G` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-031` | Programme creates Opportunity | `PROG-PROJECT-GIGABIT` | Programme | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W2-032` | Opportunity targets Enterprise | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | `ENT-CITYFIBRE` | Enterprise | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W2-033` | Opportunity targets Business Unit | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | `ENT-CITYFIBRE:Project Gigabit delivery` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-034` | Programme creates Opportunity | `PROG-CITYFIBRE-WHOLESALE` | Programme | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W2-035` | Opportunity targets Enterprise | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | `ENT-CITYFIBRE` | Enterprise | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W2-036` | Opportunity targets Business Unit | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | `ENT-CITYFIBRE:Wholesale network/commercial` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-037` | Programme creates Opportunity | `PROG-TALKTALK-PXC-DEMERGER` | Programme | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W2-038` | Opportunity targets Enterprise | `OPP-TALKTALK-COST` | Opportunity | `ENT-TALKTALK` | Enterprise | YES | YES | TalkTalk (`ENT-TALKTALK`) |
| `REL-W2-039` | Opportunity targets Business Unit | `OPP-TALKTALK-COST` | Opportunity | `ENT-TALKTALK:TalkTalk Consumer / group operations` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-040` | Programme creates Opportunity | `PROG-TALKTALK-PXC-DEMERGER` | Programme | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W2-041` | Opportunity targets Enterprise | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | `ENT-TALKTALK` | Enterprise | YES | YES | TalkTalk (`ENT-TALKTALK`) |
| `REL-W2-042` | Opportunity targets Business Unit | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | `ENT-TALKTALK:PXC` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W2-043` | Participant supplies/partners Enterprise | `MP-KYNDRYL` | Market Participant | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-044` | Participant supplies/partners Enterprise | `MP-DYNATRACE` | Market Participant | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-045` | Participant supplies/partners Enterprise | `MP-NOKIA` | Market Participant | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-046` | Participant supplies/partners Enterprise | `MP-GOOGLE` | Market Participant | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-047` | Participant supplies/partners Enterprise | `MP-AWS` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W2-048` | Participant supplies/partners Enterprise | `MP-HIYA` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W2-049` | Participant supplies/partners Enterprise | `MP-ERICSSON` | Market Participant | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-050` | Participant supplies/partners Enterprise | `MP-NOKIA` | Market Participant | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-051` | Participant supplies/partners Enterprise | `MP-DSIT-BDUK` | Market Participant | `ENT-CITYFIBRE` | Enterprise | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W2-052` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W2-053` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W2-054` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W2-055` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W2-056` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-CITYFIBRE` | Enterprise | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W2-057` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-TALKTALK` | Enterprise | YES | YES | TalkTalk (`ENT-TALKTALK`) |
| `REL-W3-001` | Enterprise owns Programme | `ENT-VMO2` | Enterprise | `PROG-VMO2-MOBILE-TRANSFORMATION` | Programme | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-002` | Programme creates Opportunity | `PROG-VMO2-MOBILE-TRANSFORMATION` | Programme | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W3-003` | Participant supplies Enterprise | `MP-ERICSSON` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-004` | Participant supplies Enterprise | `MP-NOKIA` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-005` | Participant supplies Enterprise | `MP-AWS` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-006` | Enterprise owns Programme | `ENT-VMO2` | Enterprise | `PROG-VMO2-LUMI-AI` | Programme | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-007` | Programme creates Opportunity | `PROG-VMO2-LUMI-AI` | Programme | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W3-008` | Participant partners Enterprise | `MP-NEXFIBRE` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W3-009` | Participant partners Participant | `MP-NEXFIBRE` | Market Participant | `MP-NETOMNIA-SUBSTANTIAL` | Market Participant | YES | YES | None |
| `REL-W3-010` | Regulation impacts Programme | `MP-CMA` | Market Participant | `PROG-NEXFIBRE-NETOMNIA-CONSOLIDATION` | Programme | YES | YES | None |
| `REL-W3-011` | Programme creates Opportunity | `PROG-NEXFIBRE-NETOMNIA-CONSOLIDATION` | Programme | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W3-012` | Enterprise owns Programme | `ENT-VODAFONETHREE` | Enterprise | `PROG-VT-INTEGRATION` | Programme | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W3-013` | Enterprise owns Programme | `ENT-VODAFONETHREE` | Enterprise | `PROG-VT-5G-SA` | Programme | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W3-014` | Regulation impacts Enterprise | `MP-CMA` | Market Participant | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W3-015` | Programme creates Opportunity | `PROG-VT-5G-SA` | Programme | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W3-016` | Programme creates Opportunity | `PROG-PROJECT-GIGABIT` | Programme | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W3-017` | Programme creates Opportunity | `PROG-PROJECT-GIGABIT` | Programme | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W3-018` | Participant supplies Enterprise | `MP-DSIT-BDUK` | Market Participant | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W3-019` | Participant supplies Enterprise | `MP-DSIT-BDUK` | Market Participant | `ENT-CITYFIBRE` | Enterprise | YES | YES | CityFibre (`ENT-CITYFIBRE`) |
| `REL-W3-020` | Regulation impacts Enterprise | `MP-OFCOM` | Market Participant | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W3-021` | Participant enables Opportunity | `MP-CCS-GCA` | Market Participant | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W3-022` | Technology enables Programme | `AI` | Not an object record in governed ZIP record sets | `PROG-VMO2-LUMI-AI` | Programme | NO | YES | None |
| `REL-W3-023` | Technology enables Programme | `AI` | Not an object record in governed ZIP record sets | `PROG-VMO2-MOBILE-TRANSFORMATION` | Programme | NO | YES | None |
| `REL-W3-024` | Participant partners Enterprise | `MP-LIBERTY-TELEFONICA-INFRAVIA` | Market Participant | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W4-001` | Programme creates or enables Opportunity | `PROG-VMO2-LUMI-AI` | Programme | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-002` | Opportunity targets Business Unit | `OPP-VMO2-AI-CX` | Opportunity | `Customer operations / Consumer` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-003` | Evidence supports Opportunity | `EV-VMO2-Q2FY26-W4` | Evidence | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-004` | Evidence supports Opportunity | `EV-VMO2-LUMI-2025` | Evidence | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-005` | Evidence supports Opportunity | `EV-VMO2-LUMI` | Evidence | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-006` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-AI-CX-VALUE` | Not an object record in governed ZIP record sets | `UN-009` | Unknown | NO | YES | None |
| `REL-W4-007` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-AI-CX-TIMING` | Not an object record in governed ZIP record sets | `UN-009` | Unknown | NO | YES | None |
| `REL-W4-008` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-AI-CX-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-009` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-AI-CX-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-010` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-AI-CX-01` | Monitoring Trigger | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-011` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-AI-CX-02` | Monitoring Trigger | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-012` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-AI-CX-03` | Monitoring Trigger | `OPP-VMO2-AI-CX` | Opportunity | YES | YES | None |
| `REL-W4-013` | Programme creates or enables Opportunity | `PROG-BT-TRANSFORMATION` | Programme | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-014` | Opportunity targets Business Unit | `OPP-BT-AI-ENGINEERING` | Opportunity | `BT Group transformation / Networks / Field engineering` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-015` | Evidence supports Opportunity | `EV-BT-AR26` | Evidence | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-016` | Evidence supports Opportunity | `EV-BT-Q1FY27-W4` | Evidence | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-017` | Evidence supports Opportunity | `EV-BT-KYNDRYL` | Evidence | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-018` | Evidence supports Opportunity | `EV-BT-DYNATRACE` | Evidence | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-019` | Estimate addresses Unknown | `EST-W4-OPP-BT-AI-ENGINEERING-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-020` | Estimate addresses Unknown | `EST-W4-OPP-BT-AI-ENGINEERING-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-021` | Estimate addresses Unknown | `EST-W4-OPP-BT-AI-ENGINEERING-VALUE` | Not an object record in governed ZIP record sets | `UN-004` | Unknown | NO | YES | None |
| `REL-W4-022` | Estimate addresses Unknown | `EST-W4-OPP-BT-AI-ENGINEERING-TIMING` | Not an object record in governed ZIP record sets | `UN-004` | Unknown | NO | YES | None |
| `REL-W4-023` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AI-ENGINEERING-01` | Monitoring Trigger | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-024` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AI-ENGINEERING-02` | Monitoring Trigger | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-025` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AI-ENGINEERING-03` | Monitoring Trigger | `OPP-BT-AI-ENGINEERING` | Opportunity | YES | YES | None |
| `REL-W4-026` | Programme creates or enables Opportunity | `PROG-BT-TRANSFORMATION` | Programme | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-027` | Opportunity targets Business Unit | `OPP-BT-AIOPS` | Opportunity | `Technology / Networks / Service operations` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-028` | Evidence supports Opportunity | `EV-BT-DYNATRACE` | Evidence | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-029` | Evidence supports Opportunity | `EV-BT-Q1FY27-W4` | Evidence | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-030` | Estimate addresses Unknown | `EST-W4-OPP-BT-AIOPS-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-031` | Estimate addresses Unknown | `EST-W4-OPP-BT-AIOPS-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-032` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AIOPS-01` | Monitoring Trigger | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-033` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AIOPS-02` | Monitoring Trigger | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-034` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-AIOPS-03` | Monitoring Trigger | `OPP-BT-AIOPS` | Opportunity | YES | YES | None |
| `REL-W4-035` | Programme creates or enables Opportunity | `PROG-OPENREACH-FTTP` | Programme | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-036` | Opportunity targets Business Unit | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | `Network build, planning and field operations` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-037` | Evidence supports Opportunity | `EV-OR-GOOGLE-AI-W4` | Evidence | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-038` | Evidence supports Opportunity | `EV-BT-Q1FY27-W4` | Evidence | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-039` | Evidence supports Opportunity | `EV-OF-CNS-SPRING26` | Evidence | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-040` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-FIBRE-AUTOMATION-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-OPENREACH-GOOGLE-SCOPE` | Unknown | NO | YES | None |
| `REL-W4-041` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-FIBRE-AUTOMATION-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-OPENREACH-GOOGLE-SCOPE` | Unknown | NO | YES | None |
| `REL-W4-042` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-FIBRE-AUTOMATION-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-043` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-FIBRE-AUTOMATION-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-044` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-FIBRE-AUTOMATION-01` | Monitoring Trigger | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-045` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-FIBRE-AUTOMATION-02` | Monitoring Trigger | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-046` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-FIBRE-AUTOMATION-03` | Monitoring Trigger | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | YES | YES | None |
| `REL-W4-047` | Programme creates or enables Opportunity | `PROG-COPPER-PSTN-MIGRATION` | Programme | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-048` | Opportunity targets Business Unit | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | `Wholesale access / CP enablement` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-049` | Evidence supports Opportunity | `EV-OF-CMR26-W4` | Evidence | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-050` | Evidence supports Opportunity | `EV-OF-CNS-SPRING26` | Evidence | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-051` | Evidence supports Opportunity | `EV-OF-TAR26` | Evidence | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-052` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-CP-ENABLEMENT-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-053` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-CP-ENABLEMENT-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-054` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-CP-ENABLEMENT-01` | Monitoring Trigger | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-055` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-CP-ENABLEMENT-02` | Monitoring Trigger | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-056` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-CP-ENABLEMENT-03` | Monitoring Trigger | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | YES | YES | None |
| `REL-W4-057` | Evidence supports Opportunity | `EV-VT-OWNERSHIP-W4` | Evidence | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-058` | Evidence supports Opportunity | `EV-ERICSSON-VT-MOCN-W4` | Evidence | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-059` | Evidence supports Opportunity | `EV-VT-5GSA26` | Evidence | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-060` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-VALUE` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-061` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-TIMING` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-062` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-VT-STANDALONE-REPORTING` | Unknown | NO | YES | None |
| `REL-W4-063` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-VT-STANDALONE-REPORTING` | Unknown | NO | YES | None |
| `REL-W4-064` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-065` | Estimate addresses Unknown | `EST-W4-OPP-VT-NETWORK-AI-OPS-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-066` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-NETWORK-AI-OPS-01` | Monitoring Trigger | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-067` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-NETWORK-AI-OPS-02` | Monitoring Trigger | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-068` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-NETWORK-AI-OPS-03` | Monitoring Trigger | `OPP-VT-NETWORK-AI-OPS` | Opportunity | YES | YES | None |
| `REL-W4-069` | Evidence supports Opportunity | `EV-DSIT-MMR26` | Evidence | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-070` | Evidence supports Opportunity | `EV-VT-5GSA26` | Evidence | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-071` | Evidence supports Opportunity | `EV-ERICSSON-VT-MOCN-W4` | Evidence | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-072` | Estimate addresses Unknown | `EST-W4-OPP-VT-ENTERPRISE-5G-VALUE` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-073` | Estimate addresses Unknown | `EST-W4-OPP-VT-ENTERPRISE-5G-TIMING` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-074` | Estimate addresses Unknown | `EST-W4-OPP-VT-ENTERPRISE-5G-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-075` | Estimate addresses Unknown | `EST-W4-OPP-VT-ENTERPRISE-5G-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-076` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-ENTERPRISE-5G-01` | Monitoring Trigger | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-077` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-ENTERPRISE-5G-02` | Monitoring Trigger | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-078` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-ENTERPRISE-5G-03` | Monitoring Trigger | `OPP-VT-ENTERPRISE-5G` | Opportunity | YES | YES | None |
| `REL-W4-079` | Evidence supports Opportunity | `EV-BDUK-SUFFOLK-REDESIGN-W4` | Evidence | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-080` | Evidence supports Opportunity | `EV-BDUK-KENT-REDESIGN-W4` | Evidence | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-081` | Evidence supports Opportunity | `EV-BDUK-PG-JUL2026-W4` | Evidence | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-082` | Evidence supports Opportunity | `EV-CITYFIBRE-FY25-W4` | Evidence | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-083` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-BDUK-SUBCONTRACTORS` | Unknown | NO | YES | None |
| `REL-W4-084` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-BDUK-SUBCONTRACTORS` | Unknown | NO | YES | None |
| `REL-W4-085` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-VALUE` | Not an object record in governed ZIP record sets | `UN-014` | Unknown | NO | YES | None |
| `REL-W4-086` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-TIMING` | Not an object record in governed ZIP record sets | `UN-014` | Unknown | NO | YES | None |
| `REL-W4-087` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-088` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-089` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-01` | Monitoring Trigger | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-090` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-02` | Monitoring Trigger | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-091` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-PROJECT-GIGABIT-03` | Monitoring Trigger | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | YES | YES | None |
| `REL-W4-092` | Evidence supports Opportunity | `EV-CITYFIBRE-FY25-W4` | Evidence | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-093` | Evidence supports Opportunity | `EV-CITYFIBRE-1M-W4` | Evidence | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-094` | Evidence supports Opportunity | `EV-REUTERS-CITYFIBRE-900M-W4` | Evidence | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-095` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-SKY-WHOLESALE-TERMS` | Unknown | NO | YES | None |
| `REL-W4-096` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-SKY-WHOLESALE-TERMS` | Unknown | NO | YES | None |
| `REL-W4-097` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-VALUE` | Not an object record in governed ZIP record sets | `UN-005` | Unknown | NO | YES | None |
| `REL-W4-098` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-TIMING` | Not an object record in governed ZIP record sets | `UN-005` | Unknown | NO | YES | None |
| `REL-W4-099` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-100` | Estimate addresses Unknown | `EST-W4-OPP-CITYFIBRE-WHOLESALE-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-101` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-WHOLESALE-01` | Monitoring Trigger | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-102` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-WHOLESALE-02` | Monitoring Trigger | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-103` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-CITYFIBRE-WHOLESALE-03` | Monitoring Trigger | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | YES | YES | None |
| `REL-W4-104` | Evidence supports Opportunity | `EV-TALKTALK-REFINANCE-W4` | Evidence | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-105` | Evidence supports Opportunity | `EV-TALKTALK-FT-RESULTS25-W4` | Evidence | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-106` | Evidence supports Opportunity | `EV-SPGLOBAL-TALKTALK25-W4` | Evidence | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-107` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Unknown | NO | YES | None |
| `REL-W4-108` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Unknown | NO | YES | None |
| `REL-W4-109` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-VALUE` | Not an object record in governed ZIP record sets | `UN-003` | Unknown | NO | YES | None |
| `REL-W4-110` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-TIMING` | Not an object record in governed ZIP record sets | `UN-003` | Unknown | NO | YES | None |
| `REL-W4-111` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-VALUE` | Not an object record in governed ZIP record sets | `UN-007` | Unknown | NO | YES | None |
| `REL-W4-112` | Estimate addresses Unknown | `EST-W4-OPP-TALKTALK-COST-TIMING` | Not an object record in governed ZIP record sets | `UN-007` | Unknown | NO | YES | None |
| `REL-W4-113` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-TALKTALK-COST-01` | Monitoring Trigger | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-114` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-TALKTALK-COST-02` | Monitoring Trigger | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-115` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-TALKTALK-COST-03` | Monitoring Trigger | `OPP-TALKTALK-COST` | Opportunity | YES | YES | None |
| `REL-W4-116` | Evidence supports Opportunity | `EV-PXC-REBRAND24` | Evidence | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-117` | Evidence supports Opportunity | `EV-TALKTALK-REFINANCE-W4` | Evidence | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-118` | Evidence supports Opportunity | `EV-TALKTALK-FT-RESULTS25-W4` | Evidence | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-119` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Unknown | NO | YES | None |
| `REL-W4-120` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Unknown | NO | YES | None |
| `REL-W4-121` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-VALUE` | Not an object record in governed ZIP record sets | `UN-007` | Unknown | NO | YES | None |
| `REL-W4-122` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-TIMING` | Not an object record in governed ZIP record sets | `UN-007` | Unknown | NO | YES | None |
| `REL-W4-123` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-124` | Estimate addresses Unknown | `EST-W4-OPP-PXC-PLATFORM-EFFICIENCY-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-125` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-PXC-PLATFORM-EFFICIENCY-01` | Monitoring Trigger | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-126` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-PXC-PLATFORM-EFFICIENCY-02` | Monitoring Trigger | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-127` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-PXC-PLATFORM-EFFICIENCY-03` | Monitoring Trigger | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | YES | YES | None |
| `REL-W4-128` | Opportunity targets Enterprise | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | `ENT-OPENREACH` | Enterprise | YES | YES | Openreach (`ENT-OPENREACH`) |
| `REL-W4-129` | Evidence supports Opportunity | `EV-BDUK-OR-FRAMEWORK-W4` | Evidence | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-130` | Evidence supports Opportunity | `EV-BDUK-PG-JUL2026-W4` | Evidence | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-131` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-BDUK-SUBCONTRACTORS` | Unknown | NO | YES | None |
| `REL-W4-132` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-BDUK-SUBCONTRACTORS` | Unknown | NO | YES | None |
| `REL-W4-133` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-014` | Unknown | NO | YES | None |
| `REL-W4-134` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-014` | Unknown | NO | YES | None |
| `REL-W4-135` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-136` | Estimate addresses Unknown | `EST-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-137` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-01` | Monitoring Trigger | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-138` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-02` | Monitoring Trigger | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-139` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE-03` | Monitoring Trigger | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-140` | Opportunity targets Enterprise | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W4-141` | Evidence supports Opportunity | `EV-VMO2-RAN-2026` | Evidence | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-142` | Evidence supports Opportunity | `EV-VMO2-RAN-ERICSSON-W4` | Evidence | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-143` | Evidence supports Opportunity | `EV-VMO2-Q2FY26-W4` | Evidence | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-144` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-VMO2-RAN-ADJACENT` | Unknown | NO | YES | None |
| `REL-W4-145` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-VMO2-RAN-ADJACENT` | Unknown | NO | YES | None |
| `REL-W4-146` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-147` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-148` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-01` | Monitoring Trigger | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-149` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-02` | Monitoring Trigger | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-150` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE-03` | Monitoring Trigger | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-151` | Opportunity targets Enterprise | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | `ENT-VMO2` | Enterprise | YES | YES | Virgin Media O2 (`ENT-VMO2`) |
| `REL-W4-152` | Evidence supports Opportunity | `EV-NEXFIBRE-SUBSTANTIAL26` | Evidence | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-153` | Evidence supports Opportunity | `EV-CMA-NEXFIBRE-IU-W4` | Evidence | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-154` | Evidence supports Opportunity | `EV-BT-CMA-NEXFIBRE-RESPONSE26` | Evidence | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-155` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-NEXFIBRE-MIGRATION-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-NEXFIBRE-REMEDIES` | Unknown | NO | YES | None |
| `REL-W4-156` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-NEXFIBRE-MIGRATION-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-NEXFIBRE-REMEDIES` | Unknown | NO | YES | None |
| `REL-W4-157` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-NEXFIBRE-MIGRATION-VALUE` | Not an object record in governed ZIP record sets | `UN-012` | Unknown | NO | YES | None |
| `REL-W4-158` | Estimate addresses Unknown | `EST-W4-OPP-VMO2-NEXFIBRE-MIGRATION-TIMING` | Not an object record in governed ZIP record sets | `UN-012` | Unknown | NO | YES | None |
| `REL-W4-159` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-NEXFIBRE-MIGRATION-01` | Monitoring Trigger | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-160` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-NEXFIBRE-MIGRATION-02` | Monitoring Trigger | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-161` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VMO2-NEXFIBRE-MIGRATION-03` | Monitoring Trigger | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | YES | YES | None |
| `REL-W4-162` | Opportunity targets Enterprise | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | `ENT-VODAFONETHREE` | Enterprise | YES | YES | VodafoneThree (`ENT-VODAFONETHREE`) |
| `REL-W4-163` | Evidence supports Opportunity | `EV-CMA-VT-CLOSE25` | Evidence | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-164` | Evidence supports Opportunity | `EV-VT-WRO26` | Evidence | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-165` | Evidence supports Opportunity | `EV-VT-OWNERSHIP-W4` | Evidence | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-166` | Estimate addresses Unknown | `EST-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-167` | Estimate addresses Unknown | `EST-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-008` | Unknown | NO | YES | None |
| `REL-W4-168` | Estimate addresses Unknown | `EST-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-VALUE` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-169` | Estimate addresses Unknown | `EST-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-TIMING` | Not an object record in governed ZIP record sets | `UN-002` | Unknown | NO | YES | None |
| `REL-W4-170` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-01` | Monitoring Trigger | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-171` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-02` | Monitoring Trigger | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-172` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-VT-WHOLESALE-REMEDY-ASSURANCE-03` | Monitoring Trigger | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | YES | YES | None |
| `REL-W4-173` | Opportunity targets Enterprise | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | `MP-CCS-GCA` | Market Participant | YES | YES | None |
| `REL-W4-174` | Evidence supports Opportunity | `EV-GCA-NS4-RM6377-W4` | Evidence | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W4-175` | Evidence supports Opportunity | `EV-FTS-NS4-PME-W4` | Evidence | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W4-176` | Estimate addresses Unknown | `EST-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-NS4-SUPPLIERS` | Unknown | NO | YES | None |
| `REL-W4-177` | Estimate addresses Unknown | `EST-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-NS4-SUPPLIERS` | Unknown | NO | YES | None |
| `REL-W4-178` | Estimate addresses Unknown | `EST-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-NS4-CALLOFFS` | Unknown | NO | YES | None |
| `REL-W4-179` | Estimate addresses Unknown | `EST-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-NS4-CALLOFFS` | Unknown | NO | YES | None |
| `REL-W4-180` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-01` | Monitoring Trigger | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W4-181` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-02` | Monitoring Trigger | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W4-182` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR-03` | Monitoring Trigger | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | YES | YES | None |
| `REL-W4-183` | Opportunity targets Enterprise | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | `ENT-BT` | Enterprise | YES | YES | BT Group (`ENT-BT`) |
| `REL-W4-184` | Evidence supports Opportunity | `EV-BT-VERIZON-JV-W4` | Evidence | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | YES | YES | None |
| `REL-W4-185` | Estimate addresses Unknown | `EST-W4-OPP-BT-VERIZON-JV-INTEGRATION-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-BT-VERIZON-PROCUREMENT` | Unknown | NO | YES | None |
| `REL-W4-186` | Estimate addresses Unknown | `EST-W4-OPP-BT-VERIZON-JV-INTEGRATION-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-BT-VERIZON-PROCUREMENT` | Unknown | NO | YES | None |
| `REL-W4-187` | Estimate addresses Unknown | `EST-W4-OPP-BT-VERIZON-JV-INTEGRATION-VALUE` | Not an object record in governed ZIP record sets | `UN-W4-BT-VERIZON-BUDGET` | Unknown | NO | YES | None |
| `REL-W4-188` | Estimate addresses Unknown | `EST-W4-OPP-BT-VERIZON-JV-INTEGRATION-TIMING` | Not an object record in governed ZIP record sets | `UN-W4-BT-VERIZON-BUDGET` | Unknown | NO | YES | None |
| `REL-W4-189` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-01` | Monitoring Trigger | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | YES | YES | None |
| `REL-W4-190` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-02` | Monitoring Trigger | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | YES | YES | None |
| `REL-W4-191` | Monitoring Trigger watches Opportunity | `TRG-W4-OPP-BT-VERIZON-JV-INTEGRATION-03` | Monitoring Trigger | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | YES | YES | None |
| `REL-W4-192` | Evidence supports Industry Economics | `EV-OF-CMR26-W4` | Evidence | `TEL-001-INDUSTRY-ECONOMICS` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W4-193` | Evidence supports Industry Infrastructure | `EV-OF-CNS-SPRING26` | Evidence | `TEL-001-TECHNOLOGY-LANDSCAPE` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-AI-CX` | Estimate addresses Unknown | `ESTIMATE::OPP-VMO2-AI-CX` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-009` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-AI-CX` | Opportunity classified into pipeline bucket | `OPP-VMO2-AI-CX` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-BT-AI-ENGINEERING` | Estimate addresses Unknown | `ESTIMATE::OPP-BT-AI-ENGINEERING` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-002` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-BT-AI-ENGINEERING` | Opportunity classified into pipeline bucket | `OPP-BT-AI-ENGINEERING` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-BT-AIOPS` | Estimate addresses Unknown | `ESTIMATE::OPP-BT-AIOPS` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-002` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-BT-AIOPS` | Opportunity classified into pipeline bucket | `OPP-BT-AIOPS` | Opportunity | `Existing awards` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-FIBRE-AUTOMATION` | Estimate addresses Unknown | `ESTIMATE::OPP-OPENREACH-FIBRE-AUTOMATION` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-OPENREACH-GOOGLE-SCOPE` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity classified into pipeline bucket | `OPP-OPENREACH-FIBRE-AUTOMATION` | Opportunity | `Existing awards` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-CP-ENABLEMENT` | Estimate addresses Unknown | `ESTIMATE::OPP-OPENREACH-CP-ENABLEMENT` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-002` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-CP-ENABLEMENT` | Opportunity classified into pipeline bucket | `OPP-OPENREACH-CP-ENABLEMENT` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VT-NETWORK-AI-OPS` | Estimate addresses Unknown | `ESTIMATE::OPP-VT-NETWORK-AI-OPS` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-008` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VT-NETWORK-AI-OPS` | Opportunity classified into pipeline bucket | `OPP-VT-NETWORK-AI-OPS` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VT-ENTERPRISE-5G` | Estimate addresses Unknown | `ESTIMATE::OPP-VT-ENTERPRISE-5G` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-008` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VT-ENTERPRISE-5G` | Opportunity classified into pipeline bucket | `OPP-VT-ENTERPRISE-5G` | Opportunity | `Strategic hypothesis range` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-CITYFIBRE-PROJECT-GIGABIT` | Estimate addresses Unknown | `ESTIMATE::OPP-CITYFIBRE-PROJECT-GIGABIT` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-BDUK-SUBCONTRACTORS` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity classified into pipeline bucket | `OPP-CITYFIBRE-PROJECT-GIGABIT` | Opportunity | `Existing awards` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-CITYFIBRE-WHOLESALE` | Estimate addresses Unknown | `ESTIMATE::OPP-CITYFIBRE-WHOLESALE` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-SKY-WHOLESALE-TERMS` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-CITYFIBRE-WHOLESALE` | Opportunity classified into pipeline bucket | `OPP-CITYFIBRE-WHOLESALE` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-TALKTALK-COST` | Estimate addresses Unknown | `ESTIMATE::OPP-TALKTALK-COST` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-TALKTALK-COST` | Opportunity classified into pipeline bucket | `OPP-TALKTALK-COST` | Opportunity | `Strategic hypothesis range` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-PXC-PLATFORM-EFFICIENCY` | Estimate addresses Unknown | `ESTIMATE::OPP-PXC-PLATFORM-EFFICIENCY` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-TALKTALK-ACCOUNTS-EXTRACT` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity classified into pipeline bucket | `OPP-PXC-PLATFORM-EFFICIENCY` | Opportunity | `Strategic hypothesis range` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Estimate addresses Unknown | `ESTIMATE::OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-BDUK-SUBCONTRACTORS` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity classified into pipeline bucket | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | Opportunity | `Existing awards` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Estimate addresses Unknown | `ESTIMATE::OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-VMO2-RAN-ADJACENT` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity classified into pipeline bucket | `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE` | Opportunity | `Existing awards` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VMO2-NEXFIBRE-MIGRATION` | Estimate addresses Unknown | `ESTIMATE::OPP-VMO2-NEXFIBRE-MIGRATION` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-NEXFIBRE-REMEDIES` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity classified into pipeline bucket | `OPP-VMO2-NEXFIBRE-MIGRATION` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Estimate addresses Unknown | `ESTIMATE::OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-008` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity classified into pipeline bucket | `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Estimate addresses Unknown | `ESTIMATE::OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-NS4-SUPPLIERS` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity classified into pipeline bucket | `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR` | Opportunity | `Framework market ceilings` | Not an object record in governed ZIP record sets | YES | NO | None |
| `REL-W5-EST-UNKNOWN-OPP-BT-VERIZON-JV-INTEGRATION` | Estimate addresses Unknown | `ESTIMATE::OPP-BT-VERIZON-JV-INTEGRATION` | Not an object record in governed ZIP record sets | `UNKNOWN::UN-W4-BT-VERIZON-PROCUREMENT` | Not an object record in governed ZIP record sets | NO | NO | None |
| `REL-W5-OPP-PIPELINE-OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity classified into pipeline bucket | `OPP-BT-VERIZON-JV-INTEGRATION` | Opportunity | `Named open opportunity pipeline` | Not an object record in governed ZIP record sets | YES | NO | None |

## Controls and limitations

- No relationships were inferred from dossier, Programme, or Opportunity prose or embedded convenience fields.
- The source truth is conclusive for all 308 Relationship and all 50 Membership objects.
- Candidate resolver diagnostics were reproduced from a fresh staging of the immutable repository fixture in an isolated temporary data directory; this audit made no canonical mutations or runtime changes.
- The user-supplied Enterprise-page observation (all zeros) is treated as current Flora display evidence. Candidate inventory/resolver results are separately reported above, allowing the first divergence to be bounded to presentation/association consumption when a source relationship resolves.

