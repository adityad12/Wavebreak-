# Tell users in the page that this is a demo on a free LLM tier

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
ADR 0002 says no real user data until a paid, no-training tier is in place. The page doesn't say so. Anyone who opens it would reasonably type real feelings, and unpaid Gemini use may be used for training.

## Why it matters
This is a privacy promise the product can break by default. It matters the moment anyone besides you can reach the server.

## Done when
- The page shows a clear, closable demo notice ("use made-up messages only") whenever the app runs on the free tier.
- The notice can be switched off by configuration once a paid tier is in use.
- Tests cover both modes.
