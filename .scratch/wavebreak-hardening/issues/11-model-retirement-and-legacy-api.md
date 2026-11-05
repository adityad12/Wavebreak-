# Model retirement and the "legacy" Gemini API path

Status: needs-triage

Raised by Claude, 2026-11-04. Related to decision 0006 in `docs/decisions.md`.

## Problem
- `gemini-2.5-flash` was retired for new users (404), and larger models returned 503 and 429. A retired or unavailable model only shows up to the user as "Companion unavailable".
- The code uses `generateContent`, which Google's docs label "Legacy" next to a newer Interactions API.

## Why it matters
Models get retired without a code change, and the failure is silent for users. Staying on a legacy path may mean a forced migration later.

## Done when
- The server checks the configured model at startup (or on the first call) and logs a clear error naming the model and the status.
- A short research note compares staying on `generateContent` with moving to the Interactions API, and a decision is recorded.
