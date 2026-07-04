EXTRACTION_INSTRUCTIONS = """Extract only facts explicitly supported by the supplied authoritative enterprise document. Return one fact per schema object. Do not infer missing values. Do not combine multiple metrics in one fact. Distinguish group and business-unit scope. Distinguish actual, target, guidance and announced state. Retain the exact source page. Include a bounded supporting excerpt. Return no fact when the source does not explicitly support it. Do not produce Signals, Insights, Hypotheses or Recommendations.
Positive example: BT Group plc reported revenue of GBP X billion for FY26.
Negative example: BT is facing financial pressure and should transform its operating model.
"""
