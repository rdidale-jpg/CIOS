MAX_MATERIAL_FACTS = 15

EXTRACTION_INSTRUCTIONS = """Extract only material financial facts explicitly supported by the supplied authoritative enterprise document. Return one atomic fact per schema object. Do not infer missing values. Do not combine multiple metrics in one fact. Distinguish group and business-unit scope. Distinguish actual, target, guidance and announced state. Retain the exact source page. Include a bounded supporting excerpt.

For this testing extraction, return only the material golden financial facts needed to prove the pipeline:
- revenue;
- adjusted EBITDA or equivalent;
- operating profit;
- capital expenditure;
- cash flow;
- net debt;
- cost-reduction commitment;
- guidance;
- up to seven other material financial changes.

Provider value rules:
- populate exactly one of numeric_value, text_value, date_value, or boolean_value;
- set every unused value field to null;
- set value_kind to match the one populated field;
- produce one atomic financial fact per object.
Valid numeric example: {"value_kind":"numeric","numeric_value":20.8,"text_value":null,"date_value":null,"boolean_value":null,"currency":"GBP","unit":"GBP","scale":"bn"}.
Valid text/guidance example: {"value_kind":"text","numeric_value":null,"text_value":"BT expects revenue growth in FY26.","date_value":null,"boolean_value":null,"currency":null,"unit":null,"scale":null}.

Return no more than 15 facts total. Keep facts factual, atomic and page-grounded. Do not produce narrative summaries, Signals, Insights, Hypotheses or Recommendations. Return no fact when the source does not explicitly support it.
Positive example: BT Group plc reported revenue of GBP X billion for FY26.
Negative example: BT is facing financial pressure and should transform its operating model.
"""
