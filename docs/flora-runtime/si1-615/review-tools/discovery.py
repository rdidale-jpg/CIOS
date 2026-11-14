"""Index actual public implementation/test paths and symbols, without loading records."""
from pathlib import Path
import ast,json
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1]
paths=['banking_portfolio.py','visual_v2.py','research_intelligence/registry.py','memory/models.py','memory/service.py','blueprint_import/observation_runtime.py','research_intelligence/model.py','research_intelligence/macro_intelligence.py','research_intelligence/macro_trace.py','research_intelligence/visual_specs.py','research_intelligence/unified_views.py','research_intelligence/living_map_specs.py','research_intelligence/visual_intelligence_specs.py','research_intelligence/understanding.py','research_intelligence/understanding_views.py','research_intelligence/intelligence_depth.py','research_intelligence/buying_evidence.py','buying_entry_plays.py','financial_intelligence/schema.py','financial_intelligence/normalisation.py','financial_intelligence/rapid.py','financial_intelligence/candidate_validation.py','financial_intelligence/provider_guard.py','enterprise_canvas/service.py','enterprise_canvas/access.py','enterprise_canvas/models.py','twin_inspection/enterprise.py','blueprint_import/material_pressure.py','enterprise_intelligence/runtime.py','enterprise_intelligence/retrieval.py','enterprise_intelligence/validator.py','offers.py','seller_development.py','sales_pipeline.py','visual_streams.py','design_system.py']
rows=[]
for path in paths:
 p=ROOT/'cios/applications/flora'/path
 assert p.is_file(),path
 tree=ast.parse(p.read_text());names=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
 rows.append({'path':str(p.relative_to(ROOT)),'top_level_symbols':names})
tests=[]
terms=('memory','blueprint','macro','visual_intelligence','visual_stream','enterprise_canvas','enterprise_understanding','financial','buying_trigger','seller_development','offers','material_pressure','enterprise_intelligence','flora_security')
for p in sorted((ROOT/'tests').glob('test_*.py')):
 if not any(t in p.name for t in terms):continue
 tree=ast.parse(p.read_text());tests.append({'path':str(p.relative_to(ROOT)),'tests_or_suites':[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and(n.name.startswith('test')or isinstance(n,ast.ClassDef))]})
authority_paths=[]
for p in sorted((ROOT/'architecture/decisions').glob('ADR-*.md')):
 if p.name.startswith(tuple('ADR-'+x+'-'for x in ['001','002','003','004','005','009','010','011','012','013','014','015','016','023','024','025','026'])):authority_paths.append(str(p.relative_to(ROOT)))
authority_paths+=['architecture/reference-architecture/Architecture-Authority-Registry.md','architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md']
from hashlib import sha256
(D/'Authority-Index.json').write_text(json.dumps({'status':'Read-only source pins; resolved authority and status conflicts described in SI-001, never inferred from filename/header alone','references':[{'path':p,'sha256':sha256((ROOT/p).read_bytes()).hexdigest()}for p in authority_paths]},indent=2)+'\n')
(D/'Discovery-Index.json').write_text(json.dumps({'status':'Static discovery, not a claim these tests were run in SI-1','code':rows,'available_test_modules':tests},indent=2)+'\n')
p=D/'Coverage-and-Ownership.md';s=p.read_text().replace('`tests/test_flora_memory.py`, `tests/test_flora_observation_runtime.py` where present','`tests/test_flora_enterprise_memory.py`, `tests/test_flora_blueprint_import_promotion.py`, `tests/test_memory_models.py`').replace("this table's generic historical names are not declarations that a non-existent test file ran.",'paths abbreviated under `cios/applications/flora/` exist in that index. Available tests are discovery evidence, not a claim they were rerun during SI-1.')
p.write_text(s)
print(f'Indexed {len(rows)} actual code modules and {len(tests)} available test modules.')
