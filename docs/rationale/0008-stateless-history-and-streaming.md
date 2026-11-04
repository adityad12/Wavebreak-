# Conversation history and streaming design

## What was considered
Browser-held or server-held history, SSE or NDJSON for streaming, and where to pace the typing. See `../decisions/0008-stateless-history-and-streaming.md`.

## Why this was chosen
- **Privacy first.** Anonymous users shouldn't have their conversations stored. Keeping history in the tab means the server never holds it, which matches ADR 0002 and the decision to give anonymous users no memory.
- **Context is cheap.** The Companion needs the conversation to be useful, and sending the last 20 messages costs little.
- **Roles are restricted.** The server accepts only `user` and `assistant` roles, so a visitor can't inject a `system` message through the history. History is capped at 100 items in the request and 20 sent to the model.
- **Safety sees context.** A short reply like "yes" means nothing alone. The crisis classifier now gets the last three user messages as context. Keywords still check only the latest message, so an old phrase doesn't trigger a crisis on every later turn.
- **NDJSON over SSE.** We need to POST a body, and typed events (`crisis`, `error`) map cleanly onto lines of JSON.
- **Crisis is decided before streaming.** The crisis check runs first, so a crisis never starts streaming model text. The user gets the fixed message.
- **Typing pace in the page.** Gemini sends text in chunks, not words. The page reveals it a word at a time (about 35 ms each), which feels like typing and is easy to adjust.

## Costs accepted
- A refresh loses the conversation, as designed for anonymous use. Account holders will get stored history later.
- Each request re-sends the history, which costs a little bandwidth and tokens.
- The typing effect adds a short delay after the model finishes if the page falls behind the stream.

## What would change this
Accounts with stored history (a server-side store for account holders only), or a need for resumable streams.
