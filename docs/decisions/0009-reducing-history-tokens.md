# How to reduce tokens sent while keeping context

**Status**: decided
**Decision**: Combine a rolling summary (C) with stored key facts (D). Both are held in the browser and sent with each request, so the server stays stateless. When the history reaches 16 messages, the oldest 8 are folded into the summary and facts by one extra model call and then dropped.

## Options
- **A. Keep the sliding window**: simplest. Forgets anything older than 20 messages.
- **B. Trim by token budget**: count tokens and trim to a limit, so long messages can't blow the budget. Small change.
- **C. Rolling summary**: a model call condenses old messages into a short note, sent with the recent messages. Big savings, but adds a call and can drop details, including safety-relevant ones.
- **D. Extract and store key facts**: short notes about the user are sent with recent messages. Keeps what matters. Held server-side it would conflict with ADR 0002, so it is held in the browser.
- **E. Provider-side caching**: reuse the unchanged start of the request at lower cost. Reduces cost, not tokens. Unverified for the models we use.

## Date decided
2026-11-04

Chosen for learning value, not because it is needed yet: conversations are short, so A would be enough for now. Not researched: provider caching (E) and token counting (B).
