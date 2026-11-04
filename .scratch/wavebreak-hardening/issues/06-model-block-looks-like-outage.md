# A model-side block looks like "Companion unavailable"

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
If Gemini returns no text (for example its own safety filters block a reply to a distressing message), `GeminiLLM` raises `LLMUnavailable`. The user sees "The Companion is unavailable right now. Please try again in a moment."

## Why it matters
For someone in distress, a generic outage message is the wrong response, and retrying won't help. Distinguishing a block from an outage would let the app show the helplines instead.

## Done when
- The adapter tells a blocked response apart from a failed request.
- A blocked response on a safe-looking message triggers a caring fixed reply with helplines.
- Unit and integration tests cover both cases.
