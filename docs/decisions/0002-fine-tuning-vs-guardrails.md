# Fine-tuning vs prompted LLM with guardrails

**Status**: decided
**Decision**: Use a hosted base LLM with a system prompt, curated content and a safety layer. No fine-tuning for now.

## Options
- **Fine-tune a model on recovery data**: could sound more specialised, but needs a large, ethically sourced dataset you don't have.
- **Prompted base LLM plus guardrails**: cheap, quick to iterate and swappable. Quality depends on prompt and safety design.

## Date decided
2026-11-03
