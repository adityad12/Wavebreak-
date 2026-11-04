# No rate limiting or spend cap on the chat endpoints

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
`/chat`, `/chat/stream` and `/chat/memory` are open to anyone who can reach the server. Each chat request makes up to two model calls (the crisis classifier, then the reply), and `/chat/memory` makes one. Nothing limits how often one client can call them.

## Why it matters
Anyone could use up the Gemini quota in minutes. If a paid key is added later, it would be a direct cost risk. It also affects the plan to run a free tier with limits (see the earlier discussion of cost and ADR 0002).

## Done when
- A per-client rate limit is in place (decide where: app, reverse proxy, or both).
- A hard monthly cap exists before any paid key is used.
- Tests cover the limit being hit.
