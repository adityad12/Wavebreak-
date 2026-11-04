# Helpline numbers and links in the crisis message are plain text

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
The fixed crisis message (`app/messages.py`) is rendered with `textContent`, so `findahelpline.com` and the phone numbers are not tappable. On a phone, someone in crisis has to copy a number by hand.

## Why it matters
This is the one message where friction costs the most.

## Done when
- Numbers use `tel:` links, text uses `sms:`, and URLs open normally.
- Rendering stays safe: build the links in code from a fixed structure, never by inserting model text as HTML.
- A browser-level test confirms the links exist.
