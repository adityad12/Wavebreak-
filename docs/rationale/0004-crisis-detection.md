# Crisis detection approach

## What was considered
Keywords only, an LLM classifier only, or both. See `../decisions/0004-crisis-detection.md`.

## Why this was chosen
- **Asymmetric cost.** Missing a real crisis is far worse than a false alarm or a few extra API calls, so the design leans toward over-detecting.
- **The layers fail differently.** Keywords are exact and work with no network, but miss indirect phrasing. The classifier catches indirect phrasing, but can be down or wrong. Together each covers the other's gap.
- **Either one triggers.** Requiring both to agree would bring back the misses we're trying to avoid.
- **The model never writes the crisis reply.** The fixed message with US helplines is shown, so the response is the same and reviewable every time.
- **Testable.** The keyword layer can be tested exactly, and the classifier is tested through a fake LLM.

## Costs accepted
- Some harmless messages will trigger the crisis message.
- One extra LLM call per message, adding cost and latency.
- Behaviour when the classifier fails is a separate open decision (0005).
