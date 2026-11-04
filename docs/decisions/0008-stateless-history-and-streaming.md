# Conversation history and streaming design

**Status**: decided
**Decision**: The browser holds the conversation history for the current tab and sends it with each message. The server stores nothing. Replies stream as newline-delimited JSON events (`delta`, `crisis`, `error`), and the page reveals them one word at a time.

## Options
- **History held by the browser, sent each time**: no server storage, so it fits the anonymous-user design. History is lost on refresh. Each request re-sends the history.
- **History stored on the server per session**: survives a refresh, but means storing sensitive conversations, which ADR 0002 avoids until a paid, no-training tier exists.
- **Server-Sent Events (SSE) for streaming**: a standard browser format, but it only supports GET requests with the built-in client, and we need to POST the history.
- **Newline-delimited JSON over a POST stream**: simple, works with `fetch`, carries typed events. Used here.
- **Word-by-word pacing on the server vs the client**: pacing on the client keeps the server fast and lets the speed be tuned in the page.

## Date decided
2026-11-04
