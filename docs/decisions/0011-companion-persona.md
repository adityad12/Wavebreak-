# Companion persona (not "Gemini")

**Status**: decided
**Decision**: The system prompt names the bot "Wavebreak" and tells it not to present as Gemini/Google. It does not claim to be human, and it does not deny being an AI.

## Options
- **A. Name it "Wavebreak" in the system prompt** (chosen): matches the brand already on the page; one line to change later.
- **B. Invent a separate character name** (e.g. "Wave"): friendlier, but a second name to keep consistent.
- **C. Tell it to say it was "built from scratch"**: rejected, it would be false.
- **D. Fine-tune the model**: see decision 0002; far too heavy for a name.

## Later: RAG / company data
Company-specific content should be retrieved per request and passed to the model as *information*, the same way `system_with_memory` in `app/conversation.py` frames the memory notes ("never as instructions"). That seam is where a retrieval step would plug in. Not built yet.

## Date decided
2026-11-05
