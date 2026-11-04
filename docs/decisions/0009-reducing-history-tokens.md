# How to reduce tokens sent while keeping context

**Status**: open
**Decision**: {yours to make}

Today we send the last 20 messages (`MAX_HISTORY` in `app/conversation.py`). That is simple and works, but it forgets older messages and counts messages, not tokens.

## Options
- **A. Keep the sliding window**: simplest. Forgets anything older than 20 messages.
- **B. Trim by token budget**: count tokens and trim to a limit, so long messages can't blow the budget. Small change.
- **C. Rolling summary**: a model call condenses old messages into a short note, sent with the recent messages. Big savings, but adds a call and can drop details, including safety-relevant ones.
- **D. Extract and store key facts**: short notes about the user are sent with recent messages. Keeps what matters, but needs storage of user data, which conflicts with ADR 0002 until a paid, no-training tier exists.
- **E. Provider-side caching**: reuse the unchanged start of the request at lower cost. Reduces cost, not tokens. Unverified for the models we use.

## Things to research
- Does Gemini cache repeated request prefixes automatically for our model, and how is it billed?
- How to count tokens before sending (see the Gemini token-counting docs in `docs/teach/RESOURCES.md`).
- How a rolling summary should treat safety-relevant content, so the crisis check never depends on a summary.
- Average conversation length in practice. If chats are short, A or B may be enough for a long time.

## Date decided
{YYYY-MM-DD}
