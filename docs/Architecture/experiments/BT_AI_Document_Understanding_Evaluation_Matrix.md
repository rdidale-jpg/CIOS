# BT AI Document Understanding Evaluation Matrix

| Route | Precision | Recall | Numeric accuracy | Page accuracy | Unsupported facts | Cost | Latency | Recommendation |
| ----- | --------: | -----: | ---------------: | ------------: | ----------------: | ---: | ------: | -------------- |
| Current Flora baseline | TBD after document run | TBD | TBD | TBD | TBD | local only | local only | Control baseline; deterministic parsing is not native document understanding |
| OpenAI native PDF understanding | not executed | not executed | not executed | not executed | not executed | not measured | not measured | Implemented; execute with `OPENAI_API_KEY` before selection |
| Anthropic native PDF understanding | not executed | not executed | not executed | not executed | not executed | not measured | not measured | Credential blocker documented |
| Layout extraction plus reasoning | not executed | not executed | not executed | not executed | not executed | not measured | not measured | Credential blocker documented |

Recommendation: E. None meet the quality threshold yet because credentialed model execution was not available in this environment.
