# Enterprise Transformation Observatory Architectural Critique

This replaces the old evidence-to-hypothesis reasoning spine with a commercial signal architecture. Milestone 3 should not simply insert another report-writing layer. The important correction is epistemic: raw evidence is an audit record, not a judgement. A signal is a concise factual observation, not a sales claim. An insight is a pattern with unknowns and contradictions. An argument answers a board question. A recommendation is a bounded action that references arguments rather than snippets.

Design challenges and improvements:

1. **Do not let signals become mini-insights.** Signals are capped, factual and explicitly list what they do not support.
2. **Treat single-source patterns as hypotheses.** The insight engine labels single-signal outputs as `single-signal hypothesis` so weak evidence cannot masquerade as conviction.
3. **Make negative traceability first-class.** The graph records weakening and contradiction relationships, not only positive support.
4. **Keep raw snippets out of executive surfaces.** Boilerplate belongs in drill-down diagnostics; board pages should lead with signals, insights, arguments and recommendations.
5. **Preserve deterministic operation.** The first implementation uses rules and local data structures only, avoiding LLM, database and broad crawling dependencies.

The resulting architecture is deliberately conservative: it allows Flora to say “this happened,” “this pattern may be emerging,” and “this executive conversation is justified,” while visibly preventing unsupported claims about budget, procurement, sponsorship or enterprise-wide transformation.
