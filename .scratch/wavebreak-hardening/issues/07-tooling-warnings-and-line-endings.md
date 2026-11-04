# Test warnings and CRLF line-ending noise

Status: needs-triage

Raised by Claude, 2026-11-04.

## Problem
- pytest-asyncio warns that `asyncio_default_fixture_loop_scope` is unset (`pytest.ini`).
- Starlette's test client warns that using `httpx` is deprecated.
- Git prints "LF will be replaced by CRLF" for nearly every file on every commit, because there is no `.gitattributes`.

## Why it matters
Noise hides real warnings, and the config warning says behaviour will change in a future pytest-asyncio release.

## Done when
- `asyncio_default_fixture_loop_scope` is set explicitly.
- The httpx deprecation is resolved (check what Starlette now recommends).
- A `.gitattributes` fixes line endings, and the warnings stop.
