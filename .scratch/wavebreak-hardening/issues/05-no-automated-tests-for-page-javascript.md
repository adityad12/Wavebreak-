# The page's JavaScript has no automated tests

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
Typing, stop controls, history, memory compaction and the dots all live in inline JavaScript in `app/static/index.html`. The Python tests only check that the page is served. I verified behaviour with a one-off headless-Edge harness (a fake streaming `fetch`, simulated key presses).

## Why it matters
That harness found a real bug (a whitespace-only final chunk left the page stuck "generating" forever). The project rule is that behaviour needs tests, and this part has none in the repo.

## Done when
- Browser tests (for example Playwright) run in the repo against a fake LLM.
- They cover: stop by Ctrl+C, Escape and the button; Ctrl+C with selection still copies; Enter ignored mid-reply; a whitespace-only final chunk; crisis styling; memory compaction after 16 messages.
- Consider moving the script out of the HTML into its own file so it can also be unit-tested with Node.
