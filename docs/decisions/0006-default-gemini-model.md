# Default Gemini model

**Status**: decided
**Decision**: Pin `gemini-3.5-flash-lite` as the default, overridable with the `GEMINI_MODEL` environment variable.

## Options
- **`gemini-2.5-flash`**: Google has retired it for new users (404).
- **`gemini-3.8-flash`** and the **`gemini-flash-latest` alias**: returned 503 "high demand" when tested. The alias can also change the model silently, which is risky for a safety classifier.
- **`gemini-3.5-flash`**: worked once, then returned 503 and 429 (quota) on the free tier.
- **`gemini-3.1-flash-lite`**: returned 503 on every request.
- **`gemini-3.5-flash-lite`**: answered every request in testing and gave the right crisis and non-crisis verdicts.

## Date decided
2026-11-03
