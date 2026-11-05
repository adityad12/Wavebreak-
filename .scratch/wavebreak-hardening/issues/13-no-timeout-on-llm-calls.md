# No timeout on Gemini calls, so a slow reply leaves the typing dots running

Status: needs-triage

Raised by Claude, 2026-11-05.

## Problem
`GeminiLLM` in `app/gemini.py` sets no timeout. While testing with gibberish messages the first word took 9 s once and 22.7 s once, and the page showed the animated typing dots the whole time. If Gemini hangs, the dots can run indefinitely. About half of the test requests also failed with a 429 (free-tier quota), and there is no retry.

## Why it matters
Endless dots look like a frozen app, and someone mid-urge has no sign that anything is wrong. The timeout also touches the crisis check, so what happens when the classifier times out is decision 0005 in `docs/decisions.md`, still open.

## Done when
- Every Gemini call (reply, crisis classifier, memory summary) has a timeout, and a timeout ends in the existing "Companion unavailable" path.
- One retry on a transient 429 or 503 is considered and either added or ruled out, and recorded in `docs/decisions.md`.
- Unit tests cover a timeout for the stream and for the classifier.

## Already done
- The page shows a "Still thinking…" line after 8 s without a first word.

## Related
- `01-classifier-failure-fallback.md`, `02-no-rate-limit-or-spend-cap.md`, `11-model-retirement-and-legacy-api.md`
