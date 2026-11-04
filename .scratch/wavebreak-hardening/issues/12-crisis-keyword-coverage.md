# The crisis keyword list is small and English-only

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
`app/crisis/keywords.py` has about 17 English patterns. It misses misspellings ("sucide"), slang, abbreviations, other languages, and many indirect phrasings. The classifier is meant to catch those, but it can fail (ticket 01).

## Why it matters
The keyword layer is the only part that works with no network and no model, so it is the floor under the safety design.

## Done when
- The list is reviewed and extended, ideally with input from published crisis-language guidance.
- Known false positives (quoted text, song titles, "overdose" in a medical sense) are decided on and tested.
- Tests record both what must trigger and what must not.
