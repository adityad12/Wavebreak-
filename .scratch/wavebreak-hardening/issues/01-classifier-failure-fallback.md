# Decide what happens when the crisis classifier fails

Status: needs-triage

Raised by Claude while building the Gemini adapter, 2026-11-04. Related to open decision `docs/decisions/0005-classifier-failure-behaviour.md`.

## Problem
When the LLM classifier errors, `CrisisDetector` falls back to the keyword layer only (`app/crisis/detector.py`). A crisis phrased without a keyword is then answered as a normal chat message. This is a placeholder, not a decision.

## Why it matters
The free Gemini tier returned 503 and 429 often during testing, so this path is likely, not rare. It is the main way the safety design can quietly weaken.

## Done when
- Decision 0005 is made and recorded.
- The detector's behaviour matches it, with unit and integration tests for the failure case.
