# Verify the US helpline numbers against official sources

Status: ready-for-human

Raised by Claude, 2026-11-04.

## Problem
The numbers in `app/messages.py` (988, Crisis Text Line 741741, SAMHSA 1-800-662-4357, 911) were written from memory. A `TODO` marks them as unverified.

## Why it matters
A wrong number in a crisis message is a serious failure. Also confirm that Crisis Text Line's keyword and number are still current.

## Done when
- Each number is checked on the organisation's own site.
- The `TODO` is removed and the check date is noted in a comment.
