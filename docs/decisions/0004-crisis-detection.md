# Crisis detection approach

**Status**: decided
**Decision**: Use both layers: a fixed keyword and phrase list, plus an LLM classifier. If either one flags a message, we declare a crisis.

## Options
- **Keywords only**: fast, free and predictable, but misses indirect phrasing ("I can't see the point anymore") and false-triggers on harmless text.
- **LLM classifier only**: catches indirect language, but costs money, adds latency and can fail or be wrong.
- **Both, either one triggers**: catches the most real crises. Costs an extra LLM call per message and will produce some false alarms, which was judged acceptable.

## Date decided
2026-11-03
